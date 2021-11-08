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


class PredictorConfig:
    """Configuration object attached to a Predictor."""

    def __init__(
        self,
        serving_tool="DEFAULT",
        # predictor
        min_instances=1,
        max_instances=None,
        cores=1,
        memory=1024,
        gpus=0,
        # transformer
        min_transformer_instances=1,
        max_transformer_instances=None,
        # kafka
        inference_logging=None,
        topic_name=None,
        topic_replication_factor=None,
        topic_num_partitions=None,
        # framework-specific
        request_batching=False,
    ):
        self._serving_tool = serving_tool
        self._min_instances = min_instances
        self._max_instances = max_instances
        self._cores = cores
        self._memory = memory
        self._gpus = gpus
        self._min_transformer_instances = min_transformer_instances
        self._max_transformer_instances = max_transformer_instances
        self._inference_logging = inference_logging
        self._topic_name = topic_name
        self._topic_replication_factor = topic_replication_factor
        self._topic_num_partitions = topic_num_partitions
        self._request_batching = request_batching

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(**json_decamelized)
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        return {
            "serving_tool": self._serving_tool,
            "min_instances": self._min_instances,
            "max_instances": self._max_instances,
            "cores": self._cores,
            "memory": self._memory,
            "gpus": self._gpus,
            "min_transformer_instances": self._min_transformer_instances,
            "max_transformer_instances": self._max_transformer_instances,
            "inference_logging": self._inference_logging,
            "topic_name": self._topic_name,
            "topic_replication_factor": self._topic_replication_factor,
            "topic_num_partitions": self._topic_num_partitions,
            "request_batching": self._request_batching,
        }

    @property
    def serving_tool(self):
        """Serving tool of the predictor."""
        return self._serving_tool

    @serving_tool.setter
    def serving_tool(self, serving_tool):
        self._serving_tool = serving_tool

    # TODO: Complete with other fields
