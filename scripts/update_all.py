#!/usr/bin/env python3

# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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
#

"""Run all update scripts that are present in the repository in the correct order"""

try:
    from scripts.update_template_files import main as update_template

    print("Pulling in updates from template repository")
    update_template()
except ModuleNotFoundError:
    pass

try:
    from scripts.update_config_docs import main as update_config

    print("Updating config docs")
    update_config()
except ModuleNotFoundError:
    pass

try:
    from scripts.update_openapi_docs import main as update_openapi

    print("Updating OpenAPI docs")
    update_openapi()
except ModuleNotFoundError:
    pass

try:
    from scripts.update_readme import main as update_readme

    print("Updating README")
    update_readme()
except ModuleNotFoundError:
    pass

try:
    from scripts.license_checker import run as check_license_headers

    print("Checking license headers")
    check_license_headers()
except ModuleNotFoundError:
    pass