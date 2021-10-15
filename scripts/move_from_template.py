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

"""This script moves all files considered static from the microservice template
repository over to this repository
"""

import urllib.parse

import requests

STATIC_FILE_LIST = ".static_files"
RAW_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/ghga-de/microservice-repository-template/main/"
)


def run():

    """Moves the files"""

    with open(STATIC_FILE_LIST) as list_file:
        for line in list_file:
            line_stripped = line.rstrip("\n")

            request_file = requests.get(
                urllib.parse.urljoin(RAW_TEMPLATE_URL, line_stripped)
            )

            with open(line_stripped, "w") as static_file:
                static_file.seek(0)
                static_file.write(request_file.text)
                static_file.truncate()


if __name__ == "__main__":
    run()
