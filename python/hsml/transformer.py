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
from typing import Optional, Union

from hsml import util

from hsml.deployable_component import DeployableComponent
from hsml.resources import TransformerResources


class Transformer(DeployableComponent):
    """Configuration object attached to a Transformer."""

    def __init__(
        self,
        script_file: str,
        resources: Optional[Union[TransformerResources, dict]] = None,  # base
    ):
        super().__init__(
            script_file,
            util.get_obj_from_json(resources, TransformerResources)
            or TransformerResources(),
        )

    def describe(self):
        util.pretty_print(self)

    @classmethod
    def from_json(cls, json_decamelized):
        sf, rc = cls.extract_fields_from_json(json_decamelized)
        return Transformer(sf, rc) if sf is not None else None

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        sf = util.extract_field_from_json(
            json_decamelized, ["transformer", "script_file"]
        )
        rc = TransformerResources.from_json(json_decamelized)
        return sf, rc

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(*self.extract_fields_from_json(json_decamelized))
        return self

    def to_dict(self):
        return {"transformer": self._script_file, **self._resources.to_dict()}
