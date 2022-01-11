#!/usr/bin/env python3

# Copyright 2021 - 2022 Universität Tübingen, DKFZ and EMBL
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

# pylint: skip-file

"""This script checks that the license and license headers
exists and that they are up to date.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import List, Tuple, Union

# root directory of the package:
ROOT_DIR = Path(__file__).parent.parent.resolve()

# exlude files and dirs from license header check:
EXCLUDE = [
    ".devcontainer",
    "eggs",
    ".eggs",
    "dist",
    "build",
    "develop-eggs",
    "lib",
    "lib62",
    "parts",
    "sdist",
    "wheels",
    "pip-wheel-metadata",
    ".git",
    ".github",
    ".flake8",
    ".gitignore",
    ".pylintrc",
    "example-config.yaml",
    "LICENSE",  # is checked but not for the license header
    ".pre-commit-config.yaml",
    "docs",
    "requirements.txt",
    ".vscode",
    ".mypy_cache",
    "db_migration",
    ".pytest_cache",
    ".editorconfig",
    ".static_files",
    ".mandatory_files",
]

# exclude file by file ending from license header check:
EXCLUDE_ENDINGS = ["json", "pyc", "yaml", "yml", "md", "html", "xml"]

# exclude any files with names that match any of the following regex:
EXCLUDE_PATTERN = [r".*\.egg-info.*", r".*__cache__.*", r".*\.git.*"]

# The License header, "{year}" will be replaced by current year:
LICENSE_HEADER = """Copyright {year} {author}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

# A list of all chars that may be used to introduce a comment:
COMMENT_CHARS = ["#"]

AUTHOR = """Universität Tübingen, DKFZ and EMBL
for the German Human Genome-Phenome Archive (GHGA)"""

# The path to the License file relative to target dir
LICENCE_FILE = "LICENSE"


class UnexpectedBinaryFileError(RuntimeError):
    """Thrown when trying to read a binary file."""

    def __init__(self, file_path: Union[str, Path]):
        message = f"The file could not be read because it is binary: {str(file_path)}"
        super().__init__(message)


def get_target_files(  # pylint: disable=dangerous-default-value
    target_dir: Path,
    exclude: List[str] = EXCLUDE,
    exclude_endings: List[str] = EXCLUDE_ENDINGS,
    exclude_pattern: List[str] = EXCLUDE_PATTERN,
) -> List[Path]:
    """Get target files that are not match the exclude conditions.
    Args:
        target_dir (pathlib.Path): The target dir to search.
        exclude (List[str], optional):
            Overwrite default list of file/dir paths relative to
            the target dir that shall be excluded.
        exclude_endings (List[str], optional):
            Overwrite default list of file endings that shall
            be excluded.
        exclude_pattern (List[str], optional):
            Overwrite default list of regex patterns match file path
            for exclusion.
    """
    abs_target_dir = Path(target_dir).absolute()
    exclude_normalized = [(abs_target_dir / excl).absolute() for excl in exclude]

    # get all files:
    all_files = [
        file_.absolute() for file_ in Path(abs_target_dir).rglob("*") if file_.is_file()
    ]

    target_files = [
        file_
        for file_ in all_files
        if not (
            any([file_.is_relative_to(excl) for excl in exclude_normalized])
            or any([str(file_).endswith(ending) for ending in exclude_endings])
            or any([re.match(pattern, str(file_)) for pattern in exclude_pattern])
        )
    ]
    return target_files


def normalized_line(line: str, chars_to_trim: List[str] = COMMENT_CHARS) -> str:
    norm_line = line.strip()

    for char in chars_to_trim:
        norm_line = norm_line.strip(char)

    return norm_line.strip("\n").strip("\t").strip()


def normalized_text(text: str, chars_to_trim: List[str] = COMMENT_CHARS) -> str:
    "Normalize a license header text."
    lines = text.split("\n")

    norm_lines: List[str] = []

    for line in lines:
        stripped_line = line.strip()
        # exclude shebang:
        if stripped_line.startswith("#!"):
            continue

        norm_line = normalized_line(stripped_line)

        # exclude empty lines:
        if norm_line == "":
            continue

        norm_lines.append(norm_line)

    return "\n".join(norm_lines).strip("\n")


def format_license_header_template(license_header_template: str, author: str) -> str:
    """Formats license header by inserting the specified author for every occurence of
    "{author}" in the header template.
    """
    return normalized_text(license_header_template.replace("{author}", author))


def is_commented_line(line: str, comment_chars: List[str] = COMMENT_CHARS) -> bool:
    """Checks whether a line is a comment."""
    line_stripped = line.strip()
    for commment_char in comment_chars:
        if line_stripped.startswith(commment_char):
            return True

    return False


def is_empty_line(line: str) -> bool:
    """Checks whether a line is empty."""
    return line.strip("\n").strip("\t").strip() == ""


def get_header_lines(file_path: Path, comment_chars: List[str] = COMMENT_CHARS):
    """Extracts the header from a file and normalizes it."""
    header_lines: List[str] = []

    try:
        with open(file_path, "r") as file:
            for line in file:
                if is_commented_line(
                    line, comment_chars=comment_chars
                ) or is_empty_line(line):
                    header_lines.append(line)
                else:
                    break
    except UnicodeDecodeError as error:
        raise UnexpectedBinaryFileError(file_path=file_path) from error

    # normalize the lines:
    header = "".join(header_lines)
    norm_header = normalized_text(header, chars_to_trim=comment_chars)
    norm_header_lines = norm_header.split("\n")

    return norm_header_lines


def validate_year_string(year_string: str) -> bool:
    """Check if the specified year string is valid.
    Returns `True` if valid or `False` otherwise."""
    current_year = str(date.today().year)

    # If the year_string is a single number, it must be the current year:
    if year_string.isnumeric():
        return year_string == current_year

    # Otherwise, a range (e.g. 2021 - 2022) is expected:
    match = re.match("(\d+) - (\d+)", year_string)

    if not match:
        return False

    year_1 = match.group(1)
    year_2 = match.group(2)

    # year_2 must be larger that year_1
    if int(year_2) <= int(year_1):
        return False

    # year_2 must be equal to the current year:
    return year_2 == current_year


def check_file_header(  # pylint: disable=dangerous-default-value
    file_path: Path,
    license_header_template: str = LICENSE_HEADER,
    author: str = AUTHOR,
    exclude: List[str] = EXCLUDE,
    exclude_endings: List[str] = EXCLUDE_ENDINGS,
    exclude_pattern: List[str] = EXCLUDE_PATTERN,
    comment_chars: List[str] = COMMENT_CHARS,
) -> bool:
    """Check files for presence of a license header and verify that
    the copyright notice is up to date (correct year).

    Args:
        file_path (pathlib.Path): The path to the target file.
        license_header_template (str, optional):
            A string containing a template for the expected license header.
            You may include "{year}" which will be replace by the current year.
            This defaults to the Apache 2.0 Copyright notice.
        author (str, optional):
            The author that shall be included in the license header.
            It will replace any appearance of "{author}" in the license
            header. This defaults to an auther info for GHGA.
        exclude (List[str], optional):
            Overwrite default list of file/dir paths relative to
            the target dir that shall be excluded.
        exclude_endings (List[str], optional):
            Overwrite default list of file endings that shall
            be excluded.
        exclude_pattern (List[str], optional):
            Overwrite default list of regex patterns match file path
            for exclusion.

    Returns:
        `True` - If file header valid.
        `False` - If file header invalid
    """
    formatted_template = format_license_header_template(
        license_header_template, author=author
    )
    template_lines = formatted_template.split("\n")

    header_lines = get_header_lines(file_path, comment_chars=comment_chars)

    # The header should be at least as long as the template:
    if len(header_lines) < len(template_lines):
        return False

    for idx, template_line in enumerate(template_lines):
        header_line = header_lines[idx]

        if "{year}" in template_line:
            pattern = template_line.replace("{year}", r"(.+?)")
            match = re.match(pattern, header_line)

            if not match:
                return False

            year_string = match.group(1)
            if not validate_year_string(year_string):
                return False

        elif template_line != header_line:
            return False

    return True


def check_file_headers(  # pylint: disable=dangerous-default-value
    target_dir: Path,
    license_header_template: str = LICENSE_HEADER,
    author: str = AUTHOR,
    exclude: List[str] = EXCLUDE,
    exclude_endings: List[str] = EXCLUDE_ENDINGS,
    exclude_pattern: List[str] = EXCLUDE_PATTERN,
    comment_chars: List[str] = COMMENT_CHARS,
) -> Tuple[List[Path], List[Path]]:
    """Check files for presence of a license header and verify that
    the copyright notice is up to date (correct year).

    Args:
        target_dir (pathlib.Path): The target dir to search.
        license_header_template (str, optional):
            A string containing a template for the expected license header.
            You may include "{year}" which will be replace by the current year.
            This defaults to the Apache 2.0 Copyright notice.
        author (str, optional):
            The author that shall be included in the license header.
            It will replace any appearance of "{author}" in the license
            header. This defaults to an auther info for GHGA.
        exclude (List[str], optional):
            Overwrite default list of file/dir paths relative to
            the target dir that shall be excluded.
        exclude_endings (List[str], optional):
            Overwrite default list of file endings that shall
            be excluded.
        exclude_pattern (List[str], optional):
            Overwrite default list of regex patterns match file path
            for exclusion.
    """
    target_files = get_target_files(
        target_dir,
        exclude=exclude,
        exclude_endings=exclude_endings,
        exclude_pattern=exclude_pattern,
    )

    # check if license header present in file:
    passed_files: List[Path] = []
    failed_files: List[Path] = []

    for target_file in target_files:
        try:
            if check_file_header(
                target_file,
                license_header_template=license_header_template,
                author=author,
                comment_chars=comment_chars,
            ):
                passed_files.append(target_file)
            else:
                failed_files.append(target_file)
        except UnexpectedBinaryFileError:
            # This file is a binary and is therefor skipped.
            pass

    return (passed_files, failed_files)


def check_license_file(
    license_file: Path,
    copyright_notice: str = LICENSE_HEADER,
    author: str = AUTHOR,
) -> bool:
    """Currently only checks if the copyright notice in the
    License file is up to data.

    Args:
        license_file (pathlib.Path, optional): Overwrite the default license file.
        copyright_notice (str, optional):
            A string of the copyright notice (usually same as license header).
            You may include "{year}" which will be replace by the current year.
            This defaults to the Apache 2.0 Copyright notice.
        author (str, optional):
            The author that shall be included in the copyright notice.
            It will replace any appearance of "{author}" in the copyright
            notice. This defaults to an auther info for GHGA.
    """

    if not license_file.is_file():
        print(f'Could not find license file "{str(license_file)}".')
        return False

    with open(license_file, "r") as file_:
        license_text = normalized_text(file_.read())

    expected_copyright = format_license_header_template(copyright_notice, author)

    return expected_copyright in license_text


def run():
    """Run checks from CLI."""
    parser = argparse.ArgumentParser(
        prog="license-checker",
        description=(
            "This script checks that the license and license headers "
            + "exists and that they are up to date."
        ),
    )

    parser.add_argument(
        "-L",
        "--no-license-file-check",
        help="Disables the check of the license file",
        action="store_true",
    )

    parser.add_argument(
        "-t",
        "--target-dir",
        help="Specify a custom target dir. Overwrites the default package root.",
    )

    args = parser.parse_args()

    target_dir = Path(args.target_dir).absolute() if args.target_dir else ROOT_DIR

    print(f'Working in "{target_dir}"\n')

    print("Checking license headers in files:")
    passed_files, failed_files = check_file_headers(target_dir)
    print(f"{len(passed_files)} files passed.")
    print(f"{len(failed_files)} files failed" + (":" if failed_files else "."))
    for failed_file in failed_files:
        print(f'  - "{failed_file.relative_to(target_dir)}"')

    print("")

    if args.no_license_file_check:
        license_file_valid = True
    else:
        license_file = Path(target_dir / LICENCE_FILE)
        print(f'Checking if LICENSE file is up to date: "{license_file}"')
        license_file_valid = check_license_file(license_file)
        print(
            "Copyright notice in license file is "
            + ("" if license_file_valid else "not ")
            + "up to date.\n"
        )

    if failed_files or not license_file_valid:
        print("Some checks failed.")
        sys.exit(1)

    print("All checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    run()
