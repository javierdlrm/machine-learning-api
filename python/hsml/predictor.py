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

    def __init__(
        self,
        name,
        model_path,
        model_version,
        predictor_config,
        id=None,
        artifact_version="CREATE",
        transformer=None,
        created_at=None,
        creator=None,
    ):
        self._id = id
        self._name = name
        self._model_path = model_path
        self._model_version = model_version
        self._artifact_version = artifact_version
        self._transformer = transformer
        self._created_at = created_at
        self._creator = creator
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
        id = json_decamelized.pop("id")
        name = json_decamelized.pop("name")
        model_path = json_decamelized.pop("model_path")
        model_version = json_decamelized.pop("model_version")
        artifact_version = json_decamelized.pop("artifact_version")
        transformer = json_decamelized.pop("transformer")
        created_at = json_decamelized.pop("created_at")
        creator = json_decamelized.pop("creator")
        return Predictor(
            name,
            model_path,
            model_version,
            json_decamelized,
            id,
            artifact_version,
            transformer,
            created_at,
            creator,
        )

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        id = json_decamelized.pop("id")
        name = json_decamelized.pop("name")
        model_path = json_decamelized.pop("model_path")
        model_version = json_decamelized.pop("model_version")
        artifact_version = json_decamelized.pop("artifact_version")
        transformer = json_decamelized.pop("transformer")
        created_at = json_decamelized.pop("created_at")
        creator = json_decamelized.pop("creator")
        self.__init__(
            name,
            model_path,
            model_version,
            json_decamelized,
            id,
            artifact_version,
            transformer,
            created_at,
            creator,
        )
        return self

    def json(self):
        predictor_json = json.dumps(self._predictor_config, cls=util.MLEncode)
        predictor_json["id"] = self._id
        predictor_json["name"] = self._name
        predictor_json["model_path"] = self._model_path
        predictor_json["model_version"] = self._model_version
        predictor_json["artifact_version"] = self._artifact_version
        predictor_json["transformer"] = self._transformer
        return predictor_json

    def to_dict(self):
        return {
            "id": self._id,
            "name": self._name,
            "model_path": self._model_path,
            "model_version": self._model_version,
            "artifact_version": self._artifact_version,
            "transformer": self._transformer,
            "predictor_config": self._predictor_config,
            "predictor_status": self._predictor_status,
            "created_at": self._created_at,
            "creator": self._creator,
        }

    @property
    def id(self):
        """Id of the predictor."""
        return self._id

    @property
    def name(self):
        """Name of the predictor."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def model_path(self):
        """Model path deployed by predictor."""
        return self._model_path

    @model_path.setter
    def model_path(self, model_path):
        self._model_path = model_path

    @property
    def model_version(self):
        """Model version deployed by predictor."""
        return self._model_version

    @model_version.setter
    def model_version(self, model_version):
        self._model_version = model_version

    @property
    def created_at(self):
        """Created at date of the predictor."""
        return self._created_at

    @property
    def creator(self):
        """Creator of the predictor."""
        return self._creator

    @property
    def predictor_config(self):
        """Configuration of the predictor."""
        return self._predictor_config

    @predictor_config.setter
    def predictor_config(self, predictor_config):
        self._predictor_config = predictor_config

    @property
    def artifact_version(self):
        """Artifact version deployed by predictor."""
        return self._artifact_version

    @artifact_version.setter
    def artifact_version(self, artifact_version):
        self._artifact_version = artifact_version

    @property
    def transformer(self):
        """Transformer deployed by predictor."""
        return self._transformer

    @transformer.setter
    def transformer(self, transformer):
        self._transformer = transformer
