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
from hsml import predictor_config
from hsml import transformer_config

from hsml.deployment import Deployment


class Predictor:
    """Metadata object representing a predictor in Model Serving."""

    def __init__(
        self,
        name,
        model_name,
        model_path,
        model_version,
        artifact_version,
        predictor_config,
        transformer_config=None,
        id=None,
        created_at=None,
        creator=None,
    ):
        self._name = name
        self._model_name = model_name
        self._model_path = model_path
        self._model_version = model_version
        self._artifact_version = artifact_version
        self._predictor_config = predictor_config
        self._transformer_config = transformer_config
        self._id = id
        self._created_at = created_at
        self._creator = creator

    def deploy(self):
        """Deploy this predictor of a pre-trained model"""

        deployment = Deployment(self._name, self)
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
    def from_json(cls, json_decamelized):
        return Predictor(
            name=json_decamelized.pop("name"),
            model_name=json_decamelized.pop("model_name"),
            model_path=json_decamelized.pop("model_path"),
            model_version=json_decamelized.pop("model_version"),
            artifact_version=json_decamelized.pop("artifact_version"),
            predictor_config=predictor_config.from_json(json_decamelized),
            transformer_config=transformer_config.from_json(json_decamelized),
            id=json_decamelized.pop("id"),
            created_at=json_decamelized.pop("created_at"),
            creator=json_decamelized.pop("creator"),
        )

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(
            name=json_decamelized.pop("name"),
            model_name=json_decamelized.pop("model_name"),
            model_path=json_decamelized.pop("model_path"),
            model_version=json_decamelized.pop("model_version"),
            artifact_version=json_decamelized.pop("artifact_version"),
            predictor_config=predictor_config.from_json(json_decamelized),
            transformer_config=transformer_config.from_json(json_decamelized),
            id=json_decamelized.pop("id"),
            created_at=json_decamelized.pop("created_at"),
            creator=json_decamelized.pop("creator"),
        )
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        json = {
            "id": self._id,
            "name": self._name,
            "modelName": self._model_name,
            "modelPath": self._model_path,
            "modelVersion": self._model_version,
            "artifactVersion": self._artifact_version,
            "created": self._created_at,
            "creator": self._creator,
            **self._predictor_config.to_dict(),
        }
        if self._transformer_config is not None:
            return {**json, **self._transformer_config.to_dict()}
        return json

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
    def model_name(self):
        """Name of the model deployed by the predictor."""
        return self._model_name

    @model_name.setter
    def model_name(self, model_name):
        self._model_name = model_name

    @property
    def model_path(self):
        """Model path deployed by the predictor."""
        return self._model_path

    @model_path.setter
    def model_path(self, model_path):
        self._model_path = model_path

    @property
    def model_version(self):
        """Model version deployed by the predictor."""
        return self._model_version

    @model_version.setter
    def model_version(self, model_version):
        self._model_version = model_version

    @property
    def artifact_version(self):
        """Artifact version deployed by the predictor."""
        return self._artifact_version

    @artifact_version.setter
    def artifact_version(self, artifact_version):
        self._artifact_version = artifact_version

    @property
    def predictor_config(self):
        """Configuration of the predictor."""
        return self._predictor_config

    @predictor_config.setter
    def predictor_config(self, predictor_config):
        self._predictor_config = predictor_config

    @property
    def transformer_config(self):
        """Transformer configuration attached to the predictor."""
        return self._transformer_config

    @transformer_config.setter
    def transformer_config(self, transformer_config):
        self._transformer_config = transformer_config

    @property
    def created_at(self):
        """Created at date of the predictor."""
        return self._created_at

    @property
    def creator(self):
        """Creator of the predictor."""
        return self._creator
