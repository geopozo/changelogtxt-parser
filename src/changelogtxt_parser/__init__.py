# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import pathlib
import re
import sys
from typing import Optional, TypedDict

from changelogtxt_parser.version import parse_version

VersionEntry = TypedDict("VersionEntry", {"version": str, "changes": list[str]})

BULLET_RE = re.compile(r"^-")
DEFAULT_VER = "Unreleased"


def _resolve_path(
    path_file: str,
    for_write: bool = False,
    base_dir: Optional[pathlib.Path] = None,
) -> pathlib.Path:
    path = pathlib.Path(path_file).expanduser()

    if not path.is_absolute():
        base = base_dir if base_dir else pathlib.Path.cwd()
        path = (base / path).resolve()

    if for_write:
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    return path


def load(path_file: str) -> list[VersionEntry]:
    file = _resolve_path(path_file)

    with file.open("r", encoding="utf-8") as f:
        changelog: list[VersionEntry] = [{"version": DEFAULT_VER, "changes": []}]
        current: VersionEntry = changelog[-1]
        need_bullet = False

        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue

            if parse_version(line):
                current = {"version": line, "changes": []}
                changelog.append(current)
                need_bullet = True
                continue

            if need_bullet:
                if not BULLET_RE.match(line):
                    raise ValueError(
                        f"Invalid changelog format at line {line_no}: "
                        f'Expected a "-" bullet after version, got "{line}"',
                    )
                need_bullet = False

            if BULLET_RE.match(line):
                current["changes"].append(line.lstrip("-").strip())
                continue

            current_list = current["changes"]
            if current_list:
                current_list[-1] += f" {line}"
            else:
                current_list.append(line)

    return changelog


def dump(entries: list[VersionEntry], path_file: str) -> None:
    path = _resolve_path(path_file, True)

    lines = []
    for e in entries:
        if e["version"] == DEFAULT_VER and not e["changes"]:
            continue
        header = [] if e["version"] == DEFAULT_VER else [e["version"]]
        lines.append("\n".join(header + [f"- {c}" for c in e["changes"]]))

    content: str = "\n\n".join(lines) + "\n"

    with path.open("w", encoding="utf-8") as f:
        f.write(content)

    print(f"File generated at: {path}")


def find_changelogtxt_file(base_path: str = "./") -> str | None:
    if pathlib.Path(base_path).is_file():
        return base_path
    if pathlib.Path(base_path).exists():
        filename = "CHANGELOG.txt"
        for root, _, files in os.walk(base_path):
            if filename in files:
                return os.path.join(root, filename)
    raise FileNotFoundError(f"{filename} file not found in the specified path.")


def update_version(
    version: str | None,
    message: str,
    base_path: str = "./",
) -> bool:
    if not version:
        version = DEFAULT_VER

    if not version.startswith("v"):
        version = f"v{version}"

    if not message:
        raise ValueError("Message must not be empty.")

    path_file = find_changelogtxt_file(base_path)
    if path_file:
        logs = load(path_file)
        for log in logs:
            if log["version"] == version:
                log["changes"].append(message)
                break
            else:
                logs.insert(1, {"version": version, "changes": [message]})

        dump(logs, path_file)
        # If you want to know if the changelog was successful.
        return True
    return False


def check_tag(tag: str, base_path: str = "./") -> bool:
    file_path = find_changelogtxt_file(base_path)
    if file_path:
        logs = load(file_path)
        for log in logs:
            if log["version"] == tag:
                print(f"Tag validation for '{tag}' was successful.")
                return True
    print(
        f"""Tag '{tag}' not found in changelog.
            Please update the changelog file before pushing the tag.""",
        file=sys.stderr,
    )
    return False
