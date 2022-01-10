#!/usr/bin/env python3

# Copyright 2021 Universität Tübingen, DKFZ and EMBL
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate a JSON schema from the service's Config class.
"""

from pathlib import Path

import yaml
from typer import Typer

from my_microservice.config import Config

HERE = Path(__file__).parent.resolve()
DEV_CONFIG_YAML = HERE.parent.resolve() / ".devcontainer" / ".dev_config.yaml"

cli = Typer()


def get_dev_config():
    """Get dev config object."""
    return Config(config_yaml=DEV_CONFIG_YAML)


@cli.command()
def print_schema():
    """Prints a JSON schema generated from a Config class."""
    config = get_dev_config()
    print(config.schema_json(indent=2))


@cli.command()
def print_example():
    """Prints an example config yaml."""
    config = get_dev_config()
    print(yaml.dump(config.dict()))


if __name__ == "__main__":
    cli()
