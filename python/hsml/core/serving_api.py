#
#   Copyright 2021 Logical Clocks AB
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

from hsml import client, deployment, predictor_state


class ServingApi:
    def __init__(self):
        pass

    def get(self, id):
        """Get the metadata of a deployment with a certain id.

        :param id: id of the deployment
        :type id: int
        :return: deployment metadata object
        :rtype: Deployment
        """
        _client = client.get_instance()
        path_params = [
            "project",
            _client._project_id,
            "serving",
            str(id),
        ]
        deployment_json = _client._send_request("GET", path_params)
        return deployment.Deployment.from_response_json(deployment_json)

    def get_all(self):
        """Get the metadata of all deployments.

        :return: model metadata objects
        :rtype: List[Deployment]
        """

        _client = client.get_instance()
        path_params = ["project", _client._project_id, "serving"]
        deployments_json = _client._send_request("GET", path_params)
        return deployment.Deployment.from_response_json(deployments_json)

    def put(self, deployment_instance, query_params):
        """Save deployment metadata to model serving.

        :param deployment_instance: metadata object of deployment to be saved
        :type deployment_instance: Deployment
        :return: updated metadata object of the deployment
        :rtype: Deployment
        """
        _client = client.get_instance()
        path_params = ["project", _client._project_id, "serving"]
        headers = {"content-type": "application/json"}
        return deployment_instance.update_from_response_json(
            _client._send_request(
                "PUT",
                path_params,
                headers=headers,
                query_params=query_params,
                data=deployment_instance.json(),
            )
        )

    def post(self, deployment_instance, action):
        """Perform an action on the deployment

        :param action: action to perform on the deployment (i.e., START or STOP)
        :type action: str
        """

        _client = client.get_instance()
        path_params = [
            "project",
            _client._project_id,
            "serving",
            deployment_instance.id,
        ]
        query_params = {"action": action}
        _client._send_request("POST", path_params, query_params=query_params)

    def delete(self, deployment_instance):
        """Delete the deployment and metadata.

        :param deployment_instance: metadata object of the deployment to delete
        :type deployment_instance: Deployment
        """
        _client = client.get_instance()
        path_params = [
            "project",
            _client._project_id,
            "serving",
            deployment_instance.id,
        ]
        _client._send_request("DELETE", path_params)

    def get_state(self, deployment_instance):
        """Get the state of a deployment with a certain id

        :param deployment_instance: metadata object of the deployment to get state of
        :type deployment_instance: Deployment
        :return: predictor state
        :rtype: PredictorState
        """

        _client = client.get_instance()
        path_params = [
            "project",
            _client._project_id,
            "serving",
            str(deployment_instance.id),
        ]
        deployment_json = _client._send_request("GET", path_params)
        return predictor_state.PredictorState.from_response_json(deployment_json)

    def predict(self, deployment_instance, data):
        """Send inference requests to a deployment with a certain id

        :param deployment_instance: metadata object of the deployment to be used for the prediction
        :type deployment_instance: Deployment
        :param data: payload of the inference requests
        :type data: dict
        :return: inference response
        :rtype: dict
        """

        _client = client.get_instance()
        path_params = [
            "project",
            _client._project_id,
            "inference",
            "models",
            deployment_instance.name + ":predict",
        ]
        headers = {"content-type": "application/json"}
        return _client._send_request("POST", path_params, headers=headers, data=data)
