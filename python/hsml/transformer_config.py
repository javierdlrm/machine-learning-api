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

import humps

from hsml import resources_config
from hsml import inference_logger_config
from hsml import inference_batcher_config

from hsml.component_config import ComponentConfig


class TransformerConfig(ComponentConfig):
    """Configuration object attached to a Transformer."""

    def __init__(
        self,
        script_file,
        resources_config=None,
        inference_logger=None,
        inference_batcher=None,
    ):
        super().__init__(
            script_file, resources_config, inference_logger, inference_batcher
        )

    @classmethod
    def from_json(cls, json_decamelized):
        return TransformerConfig(
            script_file=json_decamelized.pop("transformer"),
            resources_config=resources_config.from_json(
                json_decamelized, "requested_transformer_instances"
            ),
            inference_logger=inference_logger_config.from_json(json_decamelized),
            inference_batcher=inference_batcher_config.from_json(json_decamelized),
        )

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(
            script_file=json_decamelized.pop("transformer"),
            resources_config=resources_config.from_json(
                json_decamelized, "requested_transformer_instances"
            ),
            inference_logger=inference_logger_config.from_json(json_decamelized),
            inference_batcher=inference_batcher_config.from_json(json_decamelized),
        )
        return self

    def to_dict(self):
        numInstancesKey = "requestedTransformerInstances"
        resources = self._resources_config.to_dict(numInstancesKey)
        return {
            "transformer": self._script_file,
            numInstancesKey: resources[numInstancesKey],
        }
