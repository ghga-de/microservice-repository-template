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

"""This script moves all files considered static (as defined in `../.static_files`)
from the microservice template repository over to this repository
"""

import urllib.parse
from pathlib import Path

import requests

REPO_ROOT_DIR = Path(__file__).parent.parent.resolve()

STATIC_FILE_LIST = ".static_files"
RAW_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/ghga-de/microservice-repository-template/main/"
)


def run():
    """Moves the files"""

    print("Updating static file from template repo:")

    with open(STATIC_FILE_LIST, "r", encoding="utf8") as list_file:
        for line in list_file:
            relative_file_path = line.rstrip("\n")

            if relative_file_path == "" or relative_file_path.startswith("#"):
                continue

            print(relative_file_path)

            remote_file = requests.get(
                urllib.parse.urljoin(RAW_TEMPLATE_URL, relative_file_path)
            )

            local_file_path = REPO_ROOT_DIR / Path(relative_file_path)

            with open(local_file_path, "w", encoding="utf8") as local_file:
                local_file.seek(0)
                local_file.write(remote_file.text)
                local_file.truncate()


if __name__ == "__main__":
    run()
