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
from hsml import kafka_topic_config


class InferenceLoggerConfig:
    """Configuration for an inference logger."""

    def __init__(self, kafka_topic=None, mode="NONE"):
        self._kafka_topic = kafka_topic
        self._mode = mode

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @classmethod
    def from_json(self, json_decamelized):
        topic = kafka_topic_config.from_json(json_decamelized.pop("kafka_topic_dto"))
        return InferenceLoggerConfig(
            kafka_topic=topic, mode=json_decamelized.pop("inference_logging")
        )

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        topic = kafka_topic_config.from_json(json_decamelized.pop("kafka_topic_dto"))
        self.__init__(kafka_topic=topic, mode=json_decamelized.pop("inference_logging"))
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        json = {"inferenceLogging": self._mode}
        if self._kafka_topic is not None:
            return {**json, **self._kafka_topic.to_dict()}
        return json

    @property
    def kafka_topic(self):
        """Kafka topic to send the inference logs."""
        return self._kafka_topic

    @kafka_topic.setter
    def kafka_topic(self, kafka_topic):
        self._kafka_topic = kafka_topic

    @property
    def mode(self):
        """Inference logging mode ("ALL", "PREDICTIONS", or "INPUTS")."""
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode
