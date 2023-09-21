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
"""Script to ensure the pre-commit hook revs match what is installed."""
import re
import sys
from pathlib import Path

REPO_ROOT_DIR = Path(__file__).parent.parent.resolve()
PRE_COMMIT_CFG_PATH = REPO_ROOT_DIR / ".pre-commit-config.yaml"
LOCK_FILE_PATH = REPO_ROOT_DIR / "requirements-dev.txt"


def main():
    """Compare configured pre-commit hooks with the installed dependencies. For the set
    that overlap (e.g. `black`, `mypy`, `ruff`, etc.), make sure the versions match.
    If running with `--check`, exit with status code 1 if anything is outdated.
    If running without `--check`, update `.pre-commit-config.yaml` as needed.
    Any invalid flags are ignored.
    """
    args = sys.argv[1:]
    running_pre_commit = "--check" in args

    dependency = re.compile(r"([^=\s]+)==([^\s]*?)\s")
    dependencies = {}

    # Get the set of dependencies from the requirements-dev.txt lock file
    with open(LOCK_FILE_PATH, encoding="utf-8") as lock_file:
        lines = lock_file.readlines()

    for line in lines:
        match = re.match(dependency, line)
        if match:
            package, version = match.groups()
            dependencies[package] = version

    outdated_hooks: list[str] = []

    def get_repl_value(match):
        """Look up pre-commit hook id in list of dependencies. If there's a match, update
        return the version stored in the dictionary"""
        ver, name = match.groups()
        if name in dependencies:
            new_ver = dependencies[name].strip()

            # Use the v prefix if it was used before
            if ver.startswith("v"):
                new_ver = ver[0] + new_ver

            # Make a list of what's outdated
            if new_ver != ver:
                msg = f"\t{name} (configured: {ver}, expected: {new_ver})"
                outdated_hooks.append(msg)
            return new_ver
        return ver

    hook_rev = re.compile(r"([^\s\n]+)(?=\s*hooks:\s*- id: ([^\s]+))")
    with open(PRE_COMMIT_CFG_PATH, encoding="utf-8") as pre_commit_config:
        config = pre_commit_config.read()

    new_config = re.sub(hook_rev, repl=get_repl_value, string=config)
    if config != new_config:
        if running_pre_commit:
            print("The following pre-commit hook versions are outdated:")
            for hook in outdated_hooks:
                print(hook)
            print("Run 'scripts/update_hook_revs.py' to update")
            sys.exit(1)
        else:
            # update the pre-commit config
            with open(PRE_COMMIT_CFG_PATH, "w", encoding="utf-8") as pre_commit_config:
                pre_commit_config.write(new_config)
                print(f"Updated '{PRE_COMMIT_CFG_PATH}'")
    else:
        print("Pre-commit hooks are up to date.")


if __name__ == "__main__":
    main()
