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

import json
import humps

from hsml import util


class InferenceBatcherConfig:
    """Configuration for an inference batcher."""

    def __init__(self, enabled=False):
        self._enabled = enabled

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @classmethod
    def from_json(self, json_decamelized):
        return InferenceBatcherConfig(enabled=json_decamelized.pop("batching_enabled"))

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(enabled=json_decamelized.pop("batching_enabled"))
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        return {"batchingEnabled": self._enabled}

    @property
    def enabled(self):
        """Wheter the inference batcher is enabled or not."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
