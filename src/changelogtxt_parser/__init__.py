# SPDX-License-Identifier: MIT
"""ChangelogTXT Parser Module."""

from __future__ import annotations

from changelogtxt_parser import _utils, version

DEFAULT_VER = "Unreleased"


def load(path: str) -> list[version.VersionEntry]:
    """Parse a changelog file and returns a list of version entries."""
    file_path = _utils.resolve_path(path)

    with file_path.open("r", encoding="utf-8") as f:
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


def dump(entries: list[version.VersionEntry], path: str) -> None:
    """Write a formatted changelog to the specified file path."""
    file_path = _utils.resolve_path(path, for_write=True)

    lines = []
    for entry in entries:
        if entry["version"] == DEFAULT_VER and not entry["changes"]:
            continue
        header = [] if entry["version"] == DEFAULT_VER else [entry["version"]]
        lines.append("\n".join(header + [f"- {c}" for c in entry["changes"]]))

    content: str = "\n\n".join(lines) + "\n"

    with file_path.open("w", encoding="utf-8") as f:
        f.write(content)

    _utils.logger.info(f"File generated at: {file_path}")


def update(
    version: str | None,
    message: str,
    path: str = "./",
) -> str:
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

    file_path = _utils.find_file(path)
    entries = load(file_path)
    for entry in entries:
        if entry["version"] == version:
            entry["changes"].append(message)
            break
        else:
            entries.insert(1, {"version": version, "changes": [message]})
            break

    dump(entries, file_path)
    return f"File update for {file_path} was successful"


def check_tag(tag: str, path: str = "./") -> str:
    """
    Validate whether a given version tag exists in the changelog file.

    Prefixes the tag with 'v' if missing.
    """
    file_path = _utils.find_file(path)
    if not tag.startswith("v"):
        tag = f"v{tag}"

    if file_path:
        logs = load(file_path)
        for log in logs:
            if log["version"] == tag:
                return f"Tag validation for '{tag}' was successful."
    raise ValueError(f"Tag '{tag}' not found in changelog.")


def _changes_count(logs, version):
    for log in logs:
        if log["version"] == version:
            return len(log["changes"])
    return 0


def compare_files(source_file: str, target_file: str) -> str | None:
    """Compare two changelog files to detect version or change differences."""
    src_file = load(source_file)
    trg_file = load(target_file)

    if len(src_file) != len(trg_file):
        return "New version"

    src_changes = _changes_count(src_file, DEFAULT_VER)
    trg_changes = _changes_count(trg_file, DEFAULT_VER)

    if src_changes != trg_changes:
        return "New Unreleased point"

    return None
