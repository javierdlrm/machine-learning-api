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

import json
import humps

from hsml import util

from hsml.deployment import Deployment


class Predictor:
    """Metadata object representing a predictor in Model Serving."""

    def __init__(self, name, predictor_config, artifact_version="CREATE"):
        self._name = name
        self._artifact_version = artifact_version
        self._predictor_config = predictor_config

    def deploy(self):
        """Deploy this predictor of a pre-trained model"""

        deployment = Deployment(self._name, predictors=[self], type="SINGLE_MODEL")
        deployment.save()

        return deployment

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        if "count" in json_decamelized:
            if json_decamelized["count"] == 0:
                return []
            return [cls.from_json(predictor) for predictor in json_decamelized["items"]]
        else:
            return cls.from_json(json_decamelized)

    @classmethod
    def from_json(self, json_decamelized):
        name = json_decamelized.pop("name")
        artifact_version = json_decamelized.pop("artifact_version")
        return Predictor(name, json_decamelized, artifact_version)

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        name = json_decamelized.pop("name")
        artifact_version = json_decamelized.pop("artifact_version")
        self.__init__(name, json_decamelized, artifact_version)
        return self

    def json(self):
        predictor_json = json.dumps(self._predictor_config, cls=util.MLEncode)
        predictor_json["name"] = self._name
        predictor_json["artifact_version"] = self._artifact_version
        return predictor_json

    def to_dict(self):
        return {
            "name": self._name,
            "artifact_version": self._artifact_version,
            "predict_config": self._predictor_config,
        }

    @property
    def name(self):
        """Name of the predictor."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def predictor_config(self):
        """Configuration of the predictor."""
        return self._predictor_config

    @predictor_config.setter
    def predictor_config(self, predictor_config):
        self._predictor_config = predictor_config

    @property
    def artifact_version(self):
        """Artifact version used by predictor."""
        return self._artifact_version

    @artifact_version.setter
    def artifact_version(self, artifact_version):
        self._artifact_version = artifact_version
