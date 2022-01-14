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


class PredictorStatus:
    """Status of a Predictor."""

    def __init__(
        self,
        available_instances,
        available_transformer_instances,
        internal_ips,
        internal_path,
        internal_port,
        external_ip,
        external_port,
        revision,
        deployed,
        conditions,
        status,
    ):
        self._available_instances = available_instances
        self._available_transformer_instances = available_transformer_instances
        self._internal_ips = internal_ips
        self._internal_path = internal_path
        self._internal_port = internal_port
        self._external_ip = external_ip
        self._external_port = external_port
        self._revision = revision
        self._deployed = deployed if deployed is not None else False
        self._conditions = conditions
        self._status = status

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return PredictorStatus(*cls.extract_fields_from_json(json_decamelized))

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        ai = json_decamelized.pop("available_instances")
        ati = (
            json_decamelized.pop("available_transformer_instances")
            if "available_transformer_instances" in json_decamelized
            else None
        )
        ii = json_decamelized.pop("internal_ips")
        iph = json_decamelized.pop("internal_path")
        ipt = json_decamelized.pop("internal_port")
        ei = (
            json_decamelized.pop("external_ip")
            if "external_ip" in json_decamelized
            else None
        )
        ep = (
            json_decamelized.pop("external_port")
            if "external_port" in json_decamelized
            else None
        )
        r = json_decamelized.pop("revision") if "revision" in json_decamelized else None
        d = json_decamelized.pop("deployed") if "deployed" in json_decamelized else None
        c = (
            json_decamelized.pop("conditions")
            if "conditions" in json_decamelized
            else None
        )
        s = json_decamelized.pop("status")

        return ai, ati, ii, iph, ipt, ei, ep, r, d, c, s

    @property
    def available_instances(self):
        """Available instances of the predictor."""
        return self._available_instances

    @property
    def available_transformer_instances(self):
        """Available instances of the transformer."""
        return self._available_transformer_instances

    @property
    def internal_ips(self):
        """Internal IPs of the predictor."""
        return self._internal_ips

    @property
    def internal_path(self):
        """Internal path to the predictor."""
        return self._internal_path

    @property
    def internal_port(self):
        """Internal port of the predictor."""
        return self._internal_port

    @property
    def external_ip(self):
        """External IP of the predictor."""
        return self._external_ip

    @property
    def external_port(self):
        """External port of the predictor."""
        return self._external_port

    @property
    def revision(self):
        """Revision of the predictor."""
        return self._revision

    @property
    def deployed(self):
        """Whether the predictor is deployed."""
        return self._deployed

    @property
    def conditions(self):
        """Conditions of the predictor."""
        return self._conditions

    @property
    def status(self):
        """Status of the predictor."""
        return self._status
