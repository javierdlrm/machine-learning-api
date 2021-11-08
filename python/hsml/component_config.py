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

from abc import abstractclassmethod, abstractmethod

from hsml import util
from hsml import resources_config as resources_conf
from hsml import inference_logger_config
from hsml import inference_batcher_config


class ComponentConfig:
    """Configuration of a serving component (predictor or transformer)."""

    def __init__(
        self,
        script_file=None,
        resources_config=None,
        inference_logger=None,
        inference_batcher=None,
    ):
        self._script_file = script_file
        self._resources_config = resources_config
        self._inference_logger = inference_logger
        self._inference_batcher = inference_batcher

        # defaults
        if self._resources_config is None:
            self._resources_config = resources_conf.ResourcesConfig()
        if self._inference_logger is None:
            self._inference_logger = inference_logger_config.InferenceLoggerConfig()
        if self._inference_batcher is None:
            self._inference_batcher = inference_batcher_config.InferenceBatcherConfig()

    @abstractclassmethod
    def from_json(cls, json_decamelized):
        "To be implemented by the component type"
        pass

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    @abstractmethod
    def update_from_response_json(self, json_dict):
        "To be implemented by the component type"
        pass

    @abstractmethod
    def to_dict(self):
        "To be implemented by the component type"
        pass

    @property
    def script_file(self):
        """Script file ran by the serving component."""
        return self._script_file

    @script_file.setter
    def script_file(self, script_file):
        self._script_file = script_file

    @property
    def resources_config(self):
        """Resources configuration for the predictor."""
        return self._resources_config

    @resources_config.setter
    def resources_config(self, resources_config):
        self._resources_config = resources_config

    @property
    def inference_logger(self):
        """Configuration of the inference logger attached to this predictor."""
        return self._inference_logger

    @inference_logger.setter
    def inference_logger(self, inference_logger):
        self._inference_logger = inference_logger

    @property
    def inference_batcher(self):
        """Configuration of the inference batcher attached to this predictor."""
        return self._inference_batcher

    @inference_batcher.setter
    def inference_batcher(self, inference_batcher):
        self._inference_batcher = inference_batcher
