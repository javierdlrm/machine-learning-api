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


class KafkaTopicConfig:
    """Configuration for a Kafka topic."""

    def __init__(self, topic_name, topic_num_replicas=None, topic_num_partitions=None):
        self._topic_name = topic_name
        self._topic_num_replicas = topic_num_replicas
        self._topic_num_partitions = topic_num_partitions

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @classmethod
    def from_json(self, json_decamelized):
        return KafkaTopicConfig(
            topic_name=json_decamelized.pop("name"),
            topic_num_replicas=json_decamelized.pop("num_of_replicas"),
            topic_num_partitions=json_decamelized.pop("num_of_partitions"),
        )

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(
            topic_name=json_decamelized.pop("name"),
            topic_num_replicas=json_decamelized.pop("num_of_replicas"),
            topic_num_partitions=json_decamelized.pop("num_of_partitions"),
        )
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        return {
            "kafkaTopicDTO": {
                "name": self._topic_name,
                "numOfReplicas": self._topic_num_replicas,
                "numOfPartitions": self._topic_num_partitions,
            }
        }

    @property
    def topic_name(self):
        """Name of the Kafka topic."""
        return self._topic_name

    @topic_name.setter
    def topic_name(self, topic_name):
        self._topic_name = topic_name

    @property
    def topic_num_replicas(self):
        """Number of replicas of the Kafka topic."""
        return self._topic_num_replicas

    @topic_num_replicas.setter
    def topic_num_replicas(self, topic_num_replicas):
        self._topic_num_replicas = topic_num_replicas

    @property
    def topic_num_partitions(self):
        """Number of partitions of the Kafka topic."""
        return self._topic_num_partitions

    @topic_num_partitions.setter
    def topic_num_partitions(self, topic_num_partitions):
        self._topic_num_partitions = topic_num_partitions
