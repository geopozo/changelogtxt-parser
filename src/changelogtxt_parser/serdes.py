"""SerDes(Serializer/Deserializer) Module."""

from __future__ import annotations

import textwrap
import warnings

from changelogtxt_parser import _utils
from changelogtxt_parser import version as version_tools


def load(file_path: str) -> list[version_tools.VersionEntry]:
    """
    Parse a changelog file and returns a list of version entries.

    Args:
        file_path: Path to the file where the changelog will be read.

    Returns:
        A list of `VersionEntry` with changelog data

    """
    file = _utils.resolve_file_path(file_path)

    with file.open("r", encoding="utf-8") as f:
        changelog: list[version_tools.VersionEntry] = []
        current_entry: version_tools.VersionEntry | None = None

        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue

            if version_tools.parse_version(line):
                current_entry = {"version": line, "changes": []}
                changelog.append(current_entry)
            elif line.startswith("-"):
                change = line.lstrip("-").strip()
                if not change:
                    raise ValueError(
                        f"Invalid changelog format at line {line_no}: "
                        f'Expected content after "-"',
                    )

                if not current_entry:
                    current_entry = {"version": "", "changes": []}
                    changelog.append(current_entry)

                current_entry["changes"].append(change)

            elif current_entry and current_entry["changes"]:
                current_entry["changes"][-1] += f" {line}"

            else:
                raise ValueError(
                    f"Invalid changelog format at line {line_no}: "
                    'Expected "-" and then text content',
                )
    return changelog


def dump(
    entries: list[version_tools.VersionEntry],
    file_path: str,
    *,
    strict: bool = False,
) -> None:
    """
    Write a formatted changelog to the specified file path.

    Each entry in the changelog includes a version string and a list of changes.

    Args:
        entries: A list of `VersionEntry` objects, each containing a version
            string and associated changes.
        file_path: Path to the file where the changelog will be written.
        strict: If True, attempts to parse the version string for each entry.
            Defaults to False.

    """
    file = _utils.resolve_file_path(file_path, touch=True)

    changelog = []
    for entry in entries:
        version = entry["version"]
        changes = entry["changes"]

        if strict:
            parsed = version_tools.parse_version(version)
            if not parsed:
                raise ValueError(f"Invalid version format: {version!s}")
            elif isinstance(parsed, version_tools.BadVersion):
                warnings.warn(
                    f"Bad version detected: {version!s}.",
                    UserWarning,
                    stacklevel=2,
                )
            section = [f"v{version!s}"]
        else:
            section = [version] if version else []

        for change in changes:
            wrapped = textwrap.fill(
                change,
                width=88,
                initial_indent="- ",
                subsequent_indent="  ",
            )
            section.append(wrapped)

        changelog.append("\n".join(section))

    content: str = "\n\n".join(changelog) + "\n"

    with file.open("w", encoding="utf-8") as f:
        f.write(content.strip())
