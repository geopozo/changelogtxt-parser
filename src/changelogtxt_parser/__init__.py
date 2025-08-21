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


def _resolve_path(path_file: str, for_write: bool = False) -> pathlib.Path:
    path = pathlib.Path(path_file)

    if not path.is_absolute():
        path = (pathlib.Path(__file__).parent / path).resolve()

    if for_write:
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    return path


def load(path_file: str) -> list[VersionEntry]:
    file = _resolve_path(path_file)

    with file.open("r", encoding="utf-8") as f:
        changelog: list[VersionEntry] = [{"version": "Unreleased", "changes": []}]
        current = changelog[-1]
        need_bullet = False

        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue

            if _parse_version(line):
                current: VersionEntry = {"version": line, "changes": []}
                changelog.append(current)
                need_bullet = True
                continue

            if need_bullet:
                if not BULLET_RE.match(line):
                    raise ValueError(
                        f"Invalid changelog format at line {line_no}: "
                        f'Expected a "-" bullet after version, got "{line}"'
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
        if e["version"] == "Unreleased" and not e["changes"]:
            continue
        header = [] if e["version"] == "Unreleased" else [e["version"]]
        lines.append("\n".join(header + [f"- {c}" for c in e["changes"]]))

    content = "\n\n".join(lines) + "\n"

    with path.open("w", encoding="utf-8") as f:
        f.write(content)
