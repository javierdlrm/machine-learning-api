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

from hsml.core import serving_api


class ModelServing:
    DEFAULT_VERSION = 1

    def __init__(self, project_name, project_id, shared_registry_project=None):
        self._project_name = project_name
        self._project_id = project_id

        self._shared_registry_project = shared_registry_project

        self._serving_api = serving_api.ServingApi()

    def get_deployment(self, id):
        """Get a deployment entity from model serving.
        Getting a deployment from Model Serving means getting its metadata handle
        so you can subsequently operate on it (e.g., start or stop).

        # Arguments
            id: Id of the deployment to get.
        # Returns
            `Deployment`: The deployment metadata object.
        # Raises
            `RestAPIError`: If unable to retrieve deployment from model serving.
        """

        return self._serving_api.get(id)

    @property
    def project_name(self):
        """Name of the project in which model serving is located."""
        return self._project_name

    @property
    def project_id(self):
        """Id of the project in which model serving is located."""
        return self._project_id

    @property
    def shared_registry_project(self):
        """Name of the model registry shared with the project."""
        return self._shared_registry_project
