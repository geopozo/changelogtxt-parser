from __future__ import annotations

import pathlib
import re
from typing import TypedDict

import semver
from packaging import version

VersionEntry = TypedDict("VersionEntry", {"version": str, "changes": list[str]})

BULLET_RE = re.compile(r"^-")


def _parse_version(content: str) -> semver.Version | version.Version | None:
    content = content.removeprefix("v")
    v = None
    try:
        v = version.Version(content)
    except version.InvalidVersion:
        pass
    try:
        v = semver.Version.parse(content)
    except ValueError:
        pass
    if not v:
        return None
    return v


def _validate_path_file(path_file: str) -> pathlib.Path:
    path = pathlib.Path(path_file)

    if not path.is_absolute():
        path = pathlib.Path(__file__).parent / path

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path


def load(path_file: str) -> list[VersionEntry]:
    file = _validate_path_file(path_file)

    with file.open("r", encoding="utf-8") as f:
        changelog: list[VersionEntry] = [{"version": "Unreleased", "changes": []}]
        current = changelog[-1]

        for raw in f:
            line = raw.strip()
            if not line:
                continue

            if _parse_version(line):
                current: VersionEntry = {"version": line, "changes": []}
                changelog.append(current)
                continue

            if BULLET_RE.match(line):
                current["changes"].append(line.lstrip("-").strip())
                continue

            current_list = current["changes"]
            if current_list:
                current_list[-1] += f" {line}"
            else:
                current_list.append(line)

    return changelog
