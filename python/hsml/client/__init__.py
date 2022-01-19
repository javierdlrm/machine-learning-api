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
#

from hsml.client.hopsworks import internal as hw_internal
from hsml.client.hopsworks import external as hw_external
from hsml.client.istio import internal as is_internal

_hopsworks_client = None
_istio_client = None


def init(
    client_type,
    host=None,
    port=None,
    project=None,
    region_name=None,
    secrets_store=None,
    hostname_verification=None,
    trust_store_path=None,
    api_key_file=None,
    api_key_value=None,
):
    global _hopsworks_client
    if not _hopsworks_client:
        if client_type == "internal":
            _hopsworks_client = hw_internal.Client()
        elif client_type == "external":
            _hopsworks_client = hw_external.external.Client(
                host,
                port,
                project,
                region_name,
                secrets_store,
                hostname_verification,
                trust_store_path,
                api_key_file,
                api_key_value,
            )

    global _istio_client
    if not _istio_client and client_type == "internal":
        _istio_client = (
            is_internal.Client()
        )  # TODO: Add external Istio client after adding support for AKS, EKS


def get_instance():
    global _hopsworks_client
    if _hopsworks_client:
        return _hopsworks_client
    raise Exception("Couldn't find client. Try reconnecting to Hopsworks.")


def get_istio_instance():
    global _istio_client
    if _istio_client:
        return _istio_client
    raise Exception("Couldn't find the istio client. Try reconnecting to Hopsworks.")


def stop():
    global _hopsworks_client, _istio_client
    _hopsworks_client._close()
    _istio_client.close()
    _hopsworks_client = _istio_client = None
