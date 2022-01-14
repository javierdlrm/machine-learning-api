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

import time

from tqdm.auto import tqdm

from hsml.core import serving_api
from hsml.constants import PREDICTOR_STATE, DEPLOYMENT


class ServingEngine:
    def __init__(self):
        self._serving_api = serving_api.ServingApi()

    def _poll_deployment_status(self, deployment_instance, status, await_status):
        if await_status > 0:
            sleep_seconds = 5
            for i in range(int(await_status / sleep_seconds)):
                time.sleep(sleep_seconds)
                state = deployment_instance.get_state()
                if state.status == status:
                    return state
            print(
                "Deployment has not reach the desired status within the expected awaiting time, set a higher value for await_"
                + status
                + " to wait longer."
            )
            return state

    def start(self, deployment_instance, await_status):
        pbar = tqdm(
            [
                {
                    "status": PREDICTOR_STATE.STATUS_STOPPED,
                    "desc": "Deployment is stopped",
                },
                {
                    "status": PREDICTOR_STATE.STATUS_STARTING,
                    "desc": "Starting deployment",
                },
                {
                    "status": PREDICTOR_STATE.STATUS_RUNNING,
                    "desc": "Deployment is running",
                },
            ]
        )

        for step in pbar:
            try:
                pbar.set_description("%s" % step["desc"])
                if step["status"] == PREDICTOR_STATE.STATUS_STOPPED:
                    self._serving_api.post(deployment_instance, DEPLOYMENT.ACTION_START)
                if step["status"] == PREDICTOR_STATE.STATUS_STARTING:
                    status = self._poll_deployment_status(
                        deployment_instance,
                        PREDICTOR_STATE.STATUS_RUNNING,
                        await_status,
                    )
                    if status != PREDICTOR_STATE.STATUS_RUNNING:
                        return
                if step["status"] == PREDICTOR_STATE.STATUS_RUNNING:
                    pass
            except BaseException as be:
                self.stop(self, deployment_instance, await_status=0)
                raise be

    def stop(self, deployment_instance, await_status):
        pbar = tqdm(
            [
                {
                    "status": PREDICTOR_STATE.STATUS_RUNNING,
                    "desc": "Deployment is running",
                },
                {
                    "status": PREDICTOR_STATE.STATUS_STOPPING,
                    "desc": "Stopping deployment",
                },
                {
                    "status": PREDICTOR_STATE.STATUS_STOPPED,
                    "desc": "Deployment is stopped",
                },
            ]
        )

        for step in pbar:
            pbar.set_description("%s" % step["desc"])
            if step["status"] == PREDICTOR_STATE.STATUS_RUNNING:
                self._serving_api.post(deployment_instance, DEPLOYMENT.ACTION_STOP)
            if step["status"] == PREDICTOR_STATE.STATUS_STOPPING:
                self._poll_deployment_status(
                    deployment_instance, PREDICTOR_STATE.STATUS_STOPPED, await_status
                )
            if step["status"] == PREDICTOR_STATE.STATUS_STOPPED:
                pass
