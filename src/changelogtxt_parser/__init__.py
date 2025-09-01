# SPDX-License-Identifier: MIT
"""ChangelogTXT Parser Module."""

from __future__ import annotations

import os
import pathlib

from changelogtxt_parser import _logs, version

DEFAULT_VER = "Unreleased"


def _resolve_path(
    path_file: str,
    *,
    for_write: bool = False,
    base_dir: pathlib.Path | None = None,
) -> pathlib.Path:
    path = pathlib.Path(path_file).expanduser()

    if not path.is_absolute():
        base = base_dir if base_dir else pathlib.Path.cwd()
        path = (base / path).resolve()

    if for_write:
        path.parent.mkdir(parents=True, exist_ok=True)
    elif not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path


def load(path_file: str) -> list[version.VersionEntry]:
    """Parse a changelog file and returns a list of version entries."""
    file = _resolve_path(path_file)

    with file.open("r", encoding="utf-8") as f:
        changelog: list[version.VersionEntry] = [
            {"version": DEFAULT_VER, "changes": []},
        ]
        current: version.VersionEntry = changelog[-1]
        need_bullet = False
        last_line_v = None

        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue

            if need_bullet and not line.startswith("-"):
                raise ValueError(
                    f"Invalid changelog format at line {line_no}: "
                    f"Expected a '-' bullet after version at line {last_line_v}",
                )

            if version.parse_version(line):
                current = {"version": line, "changes": []}
                changelog.append(current)
                need_bullet = True
                last_line_v = line_no
                continue

            if line.startswith("-"):
                need_bullet = False
                change = line.lstrip("-").strip()
                if not change:
                    raise ValueError(
                        f"Invalid changelog format at line {line_no}: "
                        f'Expected content after "-"',
                    )
                current["changes"].append(change)
                continue

            current_list = current["changes"]
            if current_list:
                current_list[-1] += f" {line}"
            else:
                current_list.append(line)

    return changelog


def dump(entries: list[version.VersionEntry], path_file: str) -> None:
    """Write a formatted changelog to the specified file path."""
    path = _resolve_path(path_file, for_write=True)

    lines = []
    for e in entries:
        if e["version"] == DEFAULT_VER and not e["changes"]:
            continue
        header = [] if e["version"] == DEFAULT_VER else [e["version"]]
        lines.append("\n".join(header + [f"- {c}" for c in e["changes"]]))

    content: str = "\n\n".join(lines) + "\n"

    with path.open("w", encoding="utf-8") as f:
        f.write(content)

    _logs.logger.info(f"File generated at: {path}")


def find_changelogtxt_file(path: str = "./") -> str | None:
    """Search for a 'CHANGELOG.txt' file starting from the given path."""
    if pathlib.Path(path).is_file():
        return path
    if pathlib.Path(path).is_dir():
        filename = "CHANGELOG.txt"
        for root, _, files in os.walk(path):
            if filename in files:
                return str(pathlib.Path(root) / filename)
    raise FileNotFoundError(f"{filename} file not found in the specified path.")


def update(
    version: str | None,
    message: str,
    base_path: str = "./",
) -> bool:
    """
    Add a new change message to the specified version in the changelog file.

    Creates a new version entry if it doesn't exist.
    """
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
        return True
    return False


def check_tag(tag: str, base_path: str = "./") -> bool:
    """Validate whether a given version tag exists in the changelog file."""
    file_path = find_changelogtxt_file(base_path)
    if file_path:
        logs = load(file_path)
        for log in logs:
            if log["version"] == tag:
                _logs.logger.info(f"Tag validation for '{tag}' was successful.")
                return True
    raise ValueError(f"Tag '{tag}' not found in changelog.")


def _changes_count(logs, version):
    for log in logs:
        if log["version"] == version:
            return len(log["changes"])
    return 0


def compare_files(source_file: str, target_file: str) -> bool:
    """Compare two changelog files to detect version or change differences."""
    src_file = load(source_file)
    trg_file = load(target_file)

    if len(src_file) != len(trg_file):
        _logs.logger.info("New version")
        return True

    src_changes = _changes_count(src_file, DEFAULT_VER)
    trg_changes = _changes_count(trg_file, DEFAULT_VER)

    if src_changes != trg_changes:
        _logs.logger.info("New Unreleased point")
        return True

    _logs.logger.info("No changes")
    return False
