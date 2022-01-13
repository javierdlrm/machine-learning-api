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

import humps

from hsml import util

from hsml.resources_config import ResourcesConfig
from hsml.inference_logger_config import InferenceLoggerConfig
from hsml.inference_batcher_config import InferenceBatcherConfig

from hsml.component_config import ComponentConfig


class PredictorConfig(ComponentConfig):
    """Configuration object attached to a Predictor."""

    def __init__(
        self,
        model_server,
        serving_tool="DEFAULT",
        script_file=None,
        resources_config=None,
        inference_logger=None,
        inference_batcher=None,
    ):
        super().__init__(
            script_file, resources_config, inference_logger, inference_batcher
        )

        self._model_server = model_server
        self._serving_tool = serving_tool

    @classmethod
    def for_model(cls, model):
        return util.get_predictor_config_for_model(model)

    @classmethod
    def from_json(cls, json_decamelized):
        return PredictorConfig(
            model_server=json_decamelized.pop("model_server"),
            serving_tool=json_decamelized.pop("serving_tool"),
            script_file=json_decamelized.pop("predictor"),
            resources_config=ResourcesConfig.from_json(
                json_decamelized, "requested_instances"
            ),
            inference_logger=InferenceLoggerConfig.from_json(json_decamelized),
            inference_batcher=InferenceBatcherConfig.from_json(json_decamelized),
        )

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)

        self._resources_config.update_from_response_json(json_decamelized)
        if self._inference_logger is not None:
            self._inference_logger.update_from_response_json(json_decamelized)
        if self._inference_batcher is not None:
            self._inference_batcher.update_from_response_json(json_decamelized)

        self.__init__(
            model_server=json_decamelized.pop("model_server"),
            serving_tool=json_decamelized.pop("serving_tool"),
            script_file=json_decamelized.pop("predictor"),
            resources_config=self._resources_config,
            inference_logger=self._inference_logger,
            inference_batcher=self._inference_batcher,
        )
        return self

    def to_dict(self):
        return {
            "modelServer": self._model_server,
            "servingTool": self._serving_tool,
            "predictor": self._script_file,
            **self._resources_config.to_dict("requestedInstances"),
            **self._inference_logger.to_dict(),
            **self._inference_batcher.to_dict(),
        }

    @property
    def model_server(self):
        """Model server used by the predictor."""
        return self._model_server

    @model_server.setter
    def model_server(self, model_server):
        self._model_server = model_server

    @property
    def serving_tool(self):
        """Serving tool used to run the model server."""
        return self._serving_tool

    @serving_tool.setter
    def serving_tool(self, serving_tool):
        self._serving_tool = serving_tool
