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

from hsml import predictor

from hsml.core import serving_api

from hsml.client.exceptions import ModelServingException


class Deployment:
    """Metadata object representing a deployment in Model Serving."""

    def __init__(self, name, predictors, type=None):
        self._name = name
        self._predictors = predictors
        self._type = type

        if len(predictors) == 0:
            raise ModelServingException("One or more predictors are required")

        if type is None:
            self._type = "SINGLE_MODEL" if len(predictors) == 1 else "MULTI_MODEL"

        if type != "SINGLE_MODEL" or len(self._predictor) > 1:
            raise ModelServingException(
                "Only single model deployments are supported at the moment"
            )

        self._serving_api = serving_api.ServingApi()

    def save(self):
        """Persist this deployment including predictors and metadata to model serving."""

        if len(self._predictors) == 0:
            raise ModelServingException("At least one predictor is required")

        self._serving_api.put(self, query_params={})

    def start(self):
        """Start this deployment"""

        self._serving_api.post(self, "START")

    def stop(self):
        """Stop this deployment"""

        self._serving_api.post(self, "STOP")

    def delete(self):
        """Delete this deployment"""

        self._serving_api.delete(self)

    @classmethod
    def from_response_json(cls, json_dict):
        predictors = predictor.from_response_json(json_dict)
        if isinstance(predictors, list):
            return [
                cls.from_predictor(predictor_instance)
                for predictor_instance in predictors
            ]
        else:
            return cls.from_predictor(predictors)

    @staticmethod
    def from_predictor(cls, predictor_instance):
        return Deployment(
            predictor_instance._name, [predictor_instance], "SINGLE_MODEL"
        )

    def update_from_response_json(self, json_dict):
        predictor_instance = predictor.from_response_json(json_dict)
        self.__init__(predictor_instance._name, [predictor_instance], "SINGLE_MODEL")
        return self

    def json(self):
        if len(self._predictors) == 0:
            return self.json()
        return self._predictors[0].json()

    @property
    def name(self):
        """Name of the deployment."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def predictor(self):
        """Predictor contained in the deployment."""
        return self._predictors[0] if len(self._predictors) > 0 else None

    @predictor.setter
    def predictor(self, predictor):
        self._predictors = [predictor]

    @property
    def type(self):
        """Type of deployment."""
        return self._type

    @type.setter
    def type(self, type):
        self._type = type
