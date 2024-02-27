#
#   Copyright 2022 Logical Clocks AB
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from typing import Union, Dict, List

import os
import time
import uuid

from tqdm.auto import tqdm

from hsml import util

from hsml.constants import (
    DEPLOYMENT,
    PREDICTOR,
    PREDICTOR_STATE,
    INFERENCE_ENDPOINTS as IE,
)

from hsml.core import serving_api, dataset_api

from hsml.client.exceptions import ModelServingException, RestAPIError
from hsml.client.istio.grpc.infer_type import InferInput


class ServingEngine:
    START_STEPS = [
        PREDICTOR_STATE.CONDITION_TYPE_STOPPED,
        PREDICTOR_STATE.CONDITION_TYPE_SCHEDULED,
        PREDICTOR_STATE.CONDITION_TYPE_INITIALIZED,
        PREDICTOR_STATE.CONDITION_TYPE_STARTED,
        PREDICTOR_STATE.CONDITION_TYPE_READY,
    ]
    STOP_STEPS = [
        PREDICTOR_STATE.CONDITION_TYPE_SCHEDULED,
        PREDICTOR_STATE.CONDITION_TYPE_STOPPED,
    ]

    def __init__(self):
        self._serving_api = serving_api.ServingApi()
        self._dataset_api = dataset_api.DatasetApi()

    def _poll_deployment_status(
        self, deployment_instance, status: str, await_status: int, update_progress=None
    ):
        if await_status > 0:
            sleep_seconds = 5
            for _ in range(int(await_status / sleep_seconds)):
                time.sleep(sleep_seconds)
                state = deployment_instance.get_state()
                num_instances = self._get_available_instances(state)
                if update_progress is not None:
                    update_progress(state, num_instances)
                if state.status == status:
                    return state  # deployment reached desired status
                elif (
                    status == PREDICTOR_STATE.STATUS_RUNNING
                    and state.status == PREDICTOR_STATE.STATUS_FAILED
                ):
                    error_msg = state.condition.reason
                    if (
                        state.condition.type
                        == PREDICTOR_STATE.CONDITION_TYPE_INITIALIZED
                        or state.condition.type
                        == PREDICTOR_STATE.CONDITION_TYPE_STARTED
                    ):
                        component = (
                            "transformer"
                            if "transformer" in state.condition.reason
                            else "predictor"
                        )
                        error_msg += (
                            ". Please, check the server logs using `.get_logs(component='"
                            + component
                            + "')`"
                        )
                    raise ModelServingException(error_msg)
            raise ModelServingException(
                "Deployment has not reached the desired status within the expected awaiting time. Check the current status by using `.get_state()`, "
                + "explore the server logs using `.get_logs()` or set a higher value for await_"
                + status.lower()
            )

    def start(self, deployment_instance, await_status: int) -> bool:
        (done, state) = self._check_status(
            deployment_instance, PREDICTOR_STATE.STATUS_RUNNING
        )

        if not done:
            min_instances = self._get_min_starting_instances(deployment_instance)
            num_steps = (len(self.START_STEPS) - 1) + min_instances
            if deployment_instance._predictor._state.condition is None:
                num_steps = min_instances  # backward compatibility
            pbar = tqdm(total=num_steps)
            pbar.set_description("Creating deployment")

            # set progress function
            def update_progress(state, num_instances):
                (progress, desc) = self._get_starting_progress(
                    pbar.n, state, num_instances
                )
                pbar.update(progress)
                if desc is not None:
                    pbar.set_description(desc)

            try:
                update_progress(state, num_instances=0)

                if state.status == PREDICTOR_STATE.STATUS_CREATING:
                    state = self._poll_deployment_status(  # wait for preparation
                        deployment_instance,
                        PREDICTOR_STATE.STATUS_CREATED,
                        await_status,
                        update_progress,
                    )

                self._serving_api.post(
                    deployment_instance, DEPLOYMENT.ACTION_START
                )  # start deployment

                state = self._poll_deployment_status(  # wait for status
                    deployment_instance,
                    PREDICTOR_STATE.STATUS_RUNNING,
                    await_status,
                    update_progress,
                )
            except RestAPIError as re:
                self.stop(deployment_instance, await_status=0)
                raise re

        if state.status == PREDICTOR_STATE.STATUS_RUNNING:
            if (
                deployment_instance.grpc_channel is None
                and deployment_instance.serving_tool == PREDICTOR.SERVING_TOOL_KSERVE
                and deployment_instance.protocol == IE.PROTOCOL_GRPC
            ):
                # create a grpc channel
                print("Creating a gRPC channel...")
                deployment_instance._grpc_channel = (
                    self._serving_api._create_grpc_channel(deployment_instance.name)
                )
            print("Start making predictions by using `.predict()`")

    def stop(self, deployment_instance, await_status: int) -> bool:
        (done, state) = self._check_status(
            deployment_instance, PREDICTOR_STATE.STATUS_STOPPED
        )
        if not done:
            num_instances = self._get_available_instances(state)
            num_steps = len(self.STOP_STEPS) + (
                deployment_instance.requested_instances
                if deployment_instance.requested_instances >= num_instances
                else num_instances
            )
            if deployment_instance._predictor._state.condition is None:
                # backward compatibility
                num_steps = self._get_min_starting_instances(deployment_instance)
            pbar = tqdm(total=num_steps)
            pbar.set_description("Preparing to stop deployment")

            # set progress function
            def update_progress(state, num_instances):
                (progress, desc) = self._get_stopping_progress(
                    pbar.total, pbar.n, state, num_instances
                )
                pbar.update(progress)
                if desc is not None:
                    pbar.set_description(desc)

            update_progress(state, num_instances)
            self._serving_api.post(
                deployment_instance, DEPLOYMENT.ACTION_STOP
            )  # stop deployment

            _ = self._poll_deployment_status(  # wait for status
                deployment_instance,
                PREDICTOR_STATE.STATUS_STOPPED,
                await_status,
                update_progress,
            )

        # free grpc channel
        deployment_instance._grpc_channel = None

    def _check_status(self, deployment_instance, desired_status):
        state = deployment_instance.get_state()
        if state is None:
            return (True, None)

        # desired status: running
        if desired_status == PREDICTOR_STATE.STATUS_RUNNING:
            if (
                state.status == PREDICTOR_STATE.STATUS_RUNNING
                or state.status == PREDICTOR_STATE.STATUS_IDLE
            ):
                print("Deployment is already running")
                return (True, state)
            if state.status == PREDICTOR_STATE.STATUS_STARTING:
                print("Deployment is already starting")
                return (True, state)
            if state.status == PREDICTOR_STATE.STATUS_UPDATING:
                print("Deployments is already running and updating")
                return (True, state)
            if state.status == PREDICTOR_STATE.STATUS_FAILED:
                print("Deployment is in failed state. " + state.condition.reason)
                return (True, state)
            if state.status == PREDICTOR_STATE.STATUS_STOPPING:
                raise ModelServingException(
                    "Deployment is stopping, please wait until it completely stops"
                )

        # desired status: stopped
        if desired_status == PREDICTOR_STATE.STATUS_STOPPED:
            if (
                state.status == PREDICTOR_STATE.STATUS_CREATING
                or state.status == PREDICTOR_STATE.STATUS_CREATED
                or state.status == PREDICTOR_STATE.STATUS_STOPPED
            ):
                print("Deployment is already stopped")
                return (True, state)
            if state.status == PREDICTOR_STATE.STATUS_STOPPING:
                print("Deployment is already stopping")
                return (True, state)
            if state.status == PREDICTOR_STATE.STATUS_STARTING:
                if state.condition is not None:
                    raise ModelServingException(
                        "Deployment is starting, please wait until it completely starts"
                    )
            if state.status == PREDICTOR_STATE.STATUS_UPDATING:
                if state.condition is not None:
                    raise ModelServingException(
                        "Deployment is updating, please wait until the update completes"
                    )

        return (False, state)

    def _get_starting_progress(self, current_step, state, num_instances):
        if state.condition is None:  # backward compatibility
            progress = num_instances - current_step
            if state.status == PREDICTOR_STATE.STATUS_RUNNING:
                return (progress, "Deployment is ready")
            return (progress, None if current_step == 0 else "Deployment is starting")

        step = self.START_STEPS.index(state.condition.type)
        if (
            state.condition.type == PREDICTOR_STATE.CONDITION_TYPE_STARTED
            or state.condition.type == PREDICTOR_STATE.CONDITION_TYPE_READY
        ):
            step += num_instances
        progress = step - current_step
        desc = None
        if state.condition.type != PREDICTOR_STATE.CONDITION_TYPE_STOPPED:
            desc = (
                state.condition.reason
                if state.status != PREDICTOR_STATE.STATUS_FAILED
                else "Deployment failed to start"
            )
        return (progress, desc)

    def _get_stopping_progress(self, total_steps, current_step, state, num_instances):
        if state.condition is None:  # backward compatibility
            progress = (total_steps - num_instances) - current_step
            if state.status == PREDICTOR_STATE.STATUS_STOPPED:
                return (progress, "Deployment is stopped")
            return (
                progress,
                None if total_steps == current_step else "Deployment is stopping",
            )

        step = 0
        if state.condition.type == PREDICTOR_STATE.CONDITION_TYPE_SCHEDULED:
            step = 1 if state.condition.status is None else 0
        elif state.condition.type == PREDICTOR_STATE.CONDITION_TYPE_STOPPED:
            num_instances = (total_steps - 2) - num_instances  # num stopped instances
            step = (
                (2 + num_instances)
                if (state.condition.status is None or state.condition.status)
                else 0
            )
        progress = step - current_step
        desc = None
        if (
            state.condition.type != PREDICTOR_STATE.CONDITION_TYPE_READY
            and state.status != PREDICTOR_STATE.STATUS_FAILED
        ):
            desc = (
                "Deployment is stopped"
                if state.status == PREDICTOR_STATE.STATUS_STOPPED
                else state.condition.reason
            )

        return (progress, desc)

    def _get_min_starting_instances(self, deployment_instance):
        min_start_instances = 1  # predictor
        if deployment_instance.transformer is not None:
            min_start_instances += 1  # transformer
        return (
            deployment_instance.requested_instances
            if deployment_instance.requested_instances >= min_start_instances
            else min_start_instances
        )

    def _get_available_instances(self, state):
        if state.status == PREDICTOR_STATE.STATUS_CREATING:
            return 0
        num_instances = state.available_predictor_instances
        if state.available_transformer_instances is not None:
            num_instances += state.available_transformer_instances
        return num_instances

    def _get_stopped_instances(self, available_instances, requested_instances):
        num_instances = requested_instances - available_instances
        return num_instances if num_instances >= 0 else 0

    def download_artifact(self, deployment_instance):
        if deployment_instance.id is None:
            raise ModelServingException(
                "Deployment is not created yet. To create the deployment use `.save()`"
            )
        if deployment_instance.artifact_version is None:
            # model artifacts are not created in non-k8s installations
            raise ModelServingException(
                "Model artifacts not supported in non-k8s installations. \
                 Download the model files by using `model.download()`"
            )

        from_artifact_zip_path = deployment_instance.artifact_path
        to_artifacts_path = os.path.join(
            os.getcwd(),
            str(uuid.uuid4()),
            deployment_instance.model_name,
            str(deployment_instance.model_version),
            "Artifacts",
        )
        to_artifact_version_path = (
            to_artifacts_path + "/" + str(deployment_instance.artifact_version)
        )
        to_artifact_zip_path = to_artifact_version_path + ".zip"

        os.makedirs(to_artifacts_path)

        try:
            self._dataset_api.download(from_artifact_zip_path, to_artifact_zip_path)
            util.decompress(to_artifact_zip_path, extract_dir=to_artifacts_path)
            os.remove(to_artifact_zip_path)
        except BaseException as be:
            raise be
        finally:
            if os.path.exists(to_artifact_zip_path):
                os.remove(to_artifact_zip_path)

        return to_artifact_version_path

    def create(self, deployment_instance):
        try:
            self._serving_api.put(deployment_instance)
            print("Deployment created, explore it at " + deployment_instance.get_url())
        except RestAPIError as re:
            raise_err = True
            if re.error_code == ModelServingException.ERROR_CODE_DUPLICATED_ENTRY:
                msg = "Deployment with the same name already exists"
                existing_deployment = self._serving_api.get(deployment_instance.name)
                if (
                    existing_deployment.model_name == deployment_instance.model_name
                    and existing_deployment.model_version
                    == deployment_instance.model_version
                ):  # if same name and model version, retrieve existing deployment
                    print(msg + ". Getting existing deployment...")
                    print("To create a new deployment choose a different name.")
                    deployment_instance.update_from_response_json(
                        existing_deployment.to_dict()
                    )
                    raise_err = False
                else:  # otherwise, raise an exception
                    print(", but it is serving a different model version.")
                    print("Please, choose a different name.")

            if raise_err:
                raise re

        if deployment_instance.is_stopped():
            print("Before making predictions, start the deployment by using `.start()`")

    def update(self, deployment_instance, await_update):
        state = deployment_instance.get_state()
        if state is None:
            return

        if state.status == PREDICTOR_STATE.STATUS_STARTING:
            # if starting, it cannot be updated yet
            raise ModelServingException(
                "Deployment is starting, please wait until it is running before applying changes. \n"
                + "Check the current status by using `.get_state()` or explore the server logs using `.get_logs()`"
            )
        if (
            state.status == PREDICTOR_STATE.STATUS_RUNNING
            or state.status == PREDICTOR_STATE.STATUS_IDLE
            or state.status == PREDICTOR_STATE.STATUS_FAILED
        ):
            # if running, it's fine
            self._serving_api.put(deployment_instance)
            print("Deployment updated, applying changes to running instances...")
            state = self._poll_deployment_status(  # wait for status
                deployment_instance, PREDICTOR_STATE.STATUS_RUNNING, await_update
            )
            if state is not None:
                if state.status == PREDICTOR_STATE.STATUS_RUNNING:
                    print("Running instances updated successfully")
            return
        if state.status == PREDICTOR_STATE.STATUS_UPDATING:
            # if updating, it cannot be updated yet
            raise ModelServingException(
                "Deployment is updating, please wait until it is running before applying changes. \n"
                + "Check the current status by using `.get_state()` or explore the server logs using `.get_logs()`"
            )
        if state.status == PREDICTOR_STATE.STATUS_STOPPING:
            # if stopping, it cannot be updated yet
            raise ModelServingException(
                "Deployment is stopping, please wait until it is stopped before applying changes"
            )
        if (
            state.status == PREDICTOR_STATE.STATUS_CREATING
            or state.status == PREDICTOR_STATE.STATUS_CREATED
            or state.status == PREDICTOR_STATE.STATUS_STOPPED
        ):
            # if stopped, it's fine
            self._serving_api.put(deployment_instance)
            print("Deployment updated, explore it at " + deployment_instance.get_url())
            return

        raise ValueError("Unknown deployment status: " + state.status)

    def save(self, deployment_instance, await_update: int):
        if deployment_instance.id is None:
            # if new deployment
            self.create(deployment_instance)
            return

        # if existing deployment
        self.update(deployment_instance, await_update)

    def delete(self, deployment_instance, force=False):
        state = deployment_instance.get_state()
        if state is None:
            return

        if not force and state.status != PREDICTOR_STATE.STATUS_STOPPED:
            raise ModelServingException(
                "Deployment not stopped, please stop it first by using `.stop()` or check its status with .get_state()"
            )

        self._serving_api.delete(deployment_instance)
        print("Deployment deleted successfully")

    def get_state(self, deployment_instance):
        try:
            state = self._serving_api.get_state(deployment_instance)
        except RestAPIError as re:
            if re.error_code == ModelServingException.ERROR_CODE_SERVING_NOT_FOUND:
                raise ModelServingException("Deployment not found")
            raise re
        deployment_instance._predictor._set_state(state)
        return state

    def get_logs(self, deployment_instance, component, tail):
        state = self.get_state(deployment_instance)
        if state is None:
            return

        if state.status == PREDICTOR_STATE.STATUS_STOPPING:
            print(
                "Deployment is stopping, explore historical logs at "
                + deployment_instance.get_url()
            )
            return
        if state.status == PREDICTOR_STATE.STATUS_STOPPED:
            print(
                "Deployment not running, explore historical logs at "
                + deployment_instance.get_url()
            )
            return
        if state.status == PREDICTOR_STATE.STATUS_STARTING:
            print("Deployment is starting, server logs might not be ready yet")

        print(
            "Explore all the logs and filters in the Kibana logs at "
            + deployment_instance.get_url(),
            end="\n\n",
        )

        return self._serving_api.get_logs(deployment_instance, component, tail)

    # Model inference

    def predict(
        self,
        deployment_instance,
        data: Union[Dict, InferInput, List[InferInput]],
        inputs: Union[List, Dict],
    ):
        # validate user-provided payload
        self._validate_inference_payload(deployment_instance.api_protocol, data, inputs)

        # build inference payload based on API protocol
        payload = self._build_inference_payload(
            deployment_instance.api_protocol, data, inputs
        )

        # if not KServe, send request through Hopsworks
        serving_tool = deployment_instance.predictor.serving_tool
        through_hopsworks = serving_tool != PREDICTOR.SERVING_TOOL_KSERVE
        try:
            return self._serving_api.send_inference_request(
                deployment_instance, payload, through_hopsworks
            )
        except RestAPIError as re:
            if (
                re.response.status_code == RestAPIError.STATUS_CODE_NOT_FOUND
                or re.error_code
                == ModelServingException.ERROR_CODE_DEPLOYMENT_NOT_RUNNING
            ):
                raise ModelServingException(
                    "Deployment not created or running. If it is already created, start it by using `.start()` or check its status with .get_state()"
                )

            re.args = (
                re.args[0] + "\n\n Check the model server logs by using `.get_logs()`",
            )
            raise re

    def _validate_inference_payload(
        self,
        api_protocol,
        data: Union[Dict, InferInput, List[InferInput]],
        inputs: Union[List, Dict],
    ):
        """Validates the user-provided inference payload. Either data or inputs parameter is expected, but both cannot be provided together."""
        # check null inputs
        if data is not None and inputs is not None:
            raise ModelServingException(
                "Inference data and inputs parameters cannot be provided together."
            )
        # check empty inputs
        if isinstance(data or inputs, List) and len(data or inputs) == 0:
            raise ModelServingException("Inference inputs cannot be empty.")
        # check data or inputs
        if data is not None:
            self._validate_inference_data(api_protocol, data)
        else:
            self._validate_inference_inputs(inputs)

    def _validate_inference_data(
        self, api_protocol, data: Union[Dict, InferInput, List[InferInput]]
    ):
        """Validates the inference payload when provided through the `data` parameter. The data parameter contains the raw payload to be sent
        in the inference request and should be passed with the corresponding type and format depending on the API protocol.
        More specifically, a dictionary for the REST protocol or an InferInput object for the GRPC protocol.
        """
        if api_protocol == IE.API_PROTOCOL_REST:  # REST protocol
            if isinstance(data, InferInput) or (
                isinstance(data, List) and isinstance(data[0], InferInput)
            ):
                raise ModelServingException(
                    "Inference data cannot be of type InferInput for deployments with gRPC protocol disabled. Use a dictionary instead."
                )
        if api_protocol == IE.API_PROTOCOL_GRPC:  # gRPC protocol
            if isinstance(data, Dict):
                raise ModelServingException(
                    "Inference data cannot be a dictionary for deployments with gRPC protocol enabled. "
                    "Convert it to `InferInput` type or use the `inputs` parameter instead."
                )
        if isinstance(data, Dict):
            payload_list = None
            if "instances" in data:
                if not isinstance(data["instances"], List):
                    raise ModelServingException(
                        "Instances fields should contain a list."
                    )
                payload_list = data["instances"]
            if "inputs" in data:
                if not isinstance(data["inputs"], List):
                    raise ModelServingException("Inputs field should contain a list.")
                payload_list = data["inputs"]
            if payload_list is None:
                raise ModelServingException(
                    "Inference data is missing 'instances' key."
                )
        elif not isinstance(data, InferInput):  # neither Dict nor InferInput
            expected_type = "a dictionary"
            if IE.API_PROTOCOL_GRPC:
                expected_type = "an InferInput object"
            raise ModelServingException(
                f"Inference data must be {expected_type}. Otherwise, use the `inputs` parameter."
            )

    def _validate_inference_inputs(self, inputs: Union[List, Dict]):
        """Validates the inference payload when provided through the `inputs` parameter. The inputs parameter contains only the payload values,
        which will be parsed when building the request payload. It can be either a dictionary or a list.
        """
        if isinstance(inputs, InferInput):
            raise ModelServingException(
                "Inference inputs cannot be of type `InferInput`. Use the `data` parameter instead."
            )
        if not isinstance(inputs, (Dict, List)):
            raise ModelServingException(
                "Inference inputs type is not valid. Supported types are dictionary or list."
            )
        if isinstance(inputs, List):
            if len(inputs) == 0:
                raise ModelServingException("Inference inputs cannot be empty.")
            if isinstance(inputs[0], InferInput):
                raise ModelServingException(
                    "Inference inputs cannot be of type `InferInput`. Use the `data` parameter instead."
                )

    def _build_inference_payload(
        self,
        api_protocol,
        data: Union[Dict, InferInput, List[InferInput]],
        inputs: Union[Dict, List],
    ):
        """Build the inference payload for an inference request. If the 'data' parameter is provided, this method ensures
        it has the correct format depending on the API protocol. Otherwise, if the 'inputs' parameter is provided, this method
        builds the correct request payload depending on the API protocol.
        """
        if data is not None:
            # data contains the raw payload (dict or InferInput), nothing needs to be changed
            pass
        else:  # parse inputs
            if api_protocol == IE.API_PROTOCOL_REST:
                if not isinstance(inputs, List):
                    data = {"instances": [inputs]}  # wrap inputs in a list
                else:
                    data = {"instances": inputs}  # use given inputs list by default
                    # check depth of the list: at least two levels are required for batch inference
                    # if the content is neither a list or dict, wrap it in an additional list
                    for i in inputs:
                        if not isinstance(i, List) and not isinstance(i, Dict):
                            # if there are no two levels, wrap inputs in a list
                            data = {"instances": [inputs]}
                            break
            else:  # gRPC
                data = self._build_infer_inputs(inputs)
        return data

    def _build_infer_inputs(
        self, infer_inputs: Union[Dict, List[Dict]]
    ) -> Union[InferInput, List[InferInput]]:
        if isinstance(infer_inputs, Dict):  # Dict
            infer_inputs = InferInput(
                self._get_value_from_dict("name", infer_inputs),
                self._get_value_from_dict("shape", infer_inputs),
                self._get_value_from_dict("datatype", infer_inputs),
                data=self._get_value_from_dict("data", infer_inputs),
                parameters=self._get_value_from_dict("parameters", infer_inputs),
            )
        else:  # List[Dict]
            for index, infer_input in enumerate(infer_inputs):
                if isinstance(infer_input, Dict):
                    infer_inputs[index] = InferInput(
                        self._get_value_from_dict("name", infer_input),
                        self._get_value_from_dict("shape", infer_input),
                        self._get_value_from_dict("datatype", infer_input),
                        data=self._get_value_from_dict("data", infer_input),
                        parameters=self._get_value_from_dict("parameters", infer_input),
                    )
        return infer_inputs

    def _get_value_from_dict(self, key, data: Dict):
        try:
            return data[key]
        except KeyError:
            return None
