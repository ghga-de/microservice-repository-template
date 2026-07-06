#!/usr/bin/env python3

# Copyright 2021 - 2026 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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
"""Script to keep ABC classes and their implementations in sync"""

import inspect

# from my_microservice.core.handler import HandlerClass
# from my_microservice.ports.inbound.handler import HandlerClassPort
from rich import box
from rich.console import Console
from rich.style import Style
from rich.table import Table

# Import the abstract base classes and their implementations like in the comments above
PORTS: list[type] = [
    # Then list the imported port classes here as well and run the script
]

TABLE_COLOR = "cornsilk1"
HEADER_STYLE = Style(bold=False, color=TABLE_COLOR)
BORDER_STYLE = Style(dim=True, color=TABLE_COLOR)


def get_issues(abc_class: type, imp_class: type) -> list[str]:
    """Return issue strings for mismatches between the ABC and implementation."""
    methods = [m for m in abc_class.__abstractmethods__ if not m.startswith("_")]  # type: ignore
    issues = []
    for method in methods:
        abc_method = getattr(abc_class, method)
        imp_method = getattr(imp_class, method)

        if imp_method.__doc__ != abc_method.__doc__:
            abc_file = inspect.getfile(abc_method)
            abc_line = inspect.getsourcelines(abc_method)[1]
            imp_file = inspect.getfile(imp_method)
            imp_line = inspect.getsourcelines(imp_method)[1]
            issues.append(
                f"[yellow]`{method}` doc string mismatch[/yellow]\n"
                f"  [dim]port:[/dim] {abc_file}:{abc_line}\n"
                f"  [dim]impl:[/dim] {imp_file}:{imp_line}"
            )

        if inspect.signature(imp_method) != inspect.signature(abc_method):
            abc_file = inspect.getfile(abc_method)
            abc_line = inspect.getsourcelines(abc_method)[1]
            imp_file = inspect.getfile(imp_method)
            imp_line = inspect.getsourcelines(imp_method)[1]
            issues.append(
                f"[red]`{method}` signature mismatch[/red]\n"
                f"  [dim]port:[/dim] {abc_file}:{abc_line}\n"
                f"  [dim]impl:[/dim] {imp_file}:{imp_line}"
            )
    return issues


def main():
    """Build and print a 2-column comparison table for each port/implementation pair."""

    console = Console()

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style=HEADER_STYLE,
        expand=False,
        border_style=BORDER_STYLE,
    )
    table.add_column("Port (ABC)", style="cyan", no_wrap=True)
    table.add_column("Implementation", style="green", no_wrap=True)
    table.add_column("Status", no_wrap=False)

    for port in PORTS:
        imp_class = port.__subclasses__()[0]
        issues = get_issues(port, imp_class)

        if issues:
            status = "\n".join(issues)
        else:
            status = "[bold green]✓ OK[/bold green]"

        table.add_row(port.__name__, imp_class.__name__, status)

    console.print(table)


if __name__ == "__main__":
    main()
