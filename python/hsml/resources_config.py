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


class ResourcesConfig:
    """Resources configuration for predictors and transformers."""

    def __init__(self, num_instances=1, cores=1, memory=1024, gpus=0):
        self._num_instances = num_instances
        self._cores = cores
        self._memory = memory
        self._gpus = gpus

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @classmethod
    def from_json(cls, json_decamelized, num_instances_key):
        resources = json_decamelized.pop("predictor_resource_config")
        return ResourcesConfig(
            num_instances=json_decamelized.pop(num_instances_key),
            cores=resources["cores"],
            memory=resources["memory"],
            gpus=resources["gpus"],
        )

    def update_from_response_json(self, json_dict, num_instances_key):
        json_decamelized = humps.decamelize(json_dict)
        resources = json_decamelized.pop("predictor_resource_config")
        self.__init__(
            num_instances=json_decamelized.pop(num_instances_key),
            cores=resources["cores"],
            memory=resources["memory"],
            gpus=resources["gpus"],
        )
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self, num_instances_key):
        return {
            num_instances_key: self._num_instances,
            "predictorResourceConfig": {
                "cores": self._cores,
                "memory": self._memory,
                "gpus": self._gpus,
            },
        }

    @property
    def num_instances(self):
        """Number of instances."""
        return self._num_instances

    @num_instances.setter
    def num_instances(self, num_instances):
        self._num_instances = num_instances

    @property
    def cores(self):
        """Number of cores."""
        return self._cores

    @cores.setter
    def cores(self, cores):
        self._cores = cores

    @property
    def memory(self):
        """Memory resources."""
        return self._memory

    @memory.setter
    def memory(self, memory):
        self._memory = memory

    @property
    def gpus(self):
        """Number of GPUs."""
        return self._gpus

    @gpus.setter
    def gpus(self, gpus):
        self._gpus = gpus
