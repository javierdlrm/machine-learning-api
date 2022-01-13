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

import json

from hsml import util, predictor

from hsml.core import serving_api

from hsml.client.exceptions import ModelServingException


class Deployment:
    """Metadata object representing a deployment in Model Serving."""

    def __init__(self, name, predictor):
        self._name = name
        self._predictor = predictor

        if predictor is None:
            raise ModelServingException("A predictor is required")

        self._serving_api = serving_api.ServingApi()

    def save(self):
        """Persist this deployment including the predictor and metadata to model serving."""

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

    def get_status(self):
        """Get status of the deployment"""

        return self._serving_api.get_status(self._id)

    def predict(self, data):
        """Send inference requests to this deployment"""

        return self._serving_api.predict(self._id, data)

    @classmethod
    def from_response_json(cls, json_dict):
        predictors = predictor.Predictor.from_response_json(json_dict)
        if isinstance(predictors, list):
            return [
                cls.from_predictor(predictor_instance)
                for predictor_instance in predictors
            ]
        else:
            return cls.from_predictor(predictors)

    @classmethod
    def from_predictor(cls, predictor_instance):
        return Deployment(name=predictor_instance._name, predictor=predictor_instance)

    def update_from_response_json(self, json_dict):
        self._predictor.update_from_response_json(json_dict)
        self.__init__(name=self._predictor._name, predictor=self._predictor)
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        return self._predictor.to_dict()

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
        return self._predictor

    @predictor.setter
    def predictor(self, predictor):
        self._predictor = predictor
