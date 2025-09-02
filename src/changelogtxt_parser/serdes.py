"""SerDes(Serializer/Deserializer) Module."""

from __future__ import annotations

from changelogtxt_parser import _utils
from changelogtxt_parser import version as version_tools

DEFAULT_VER = "Unreleased"


def load(path: str) -> tuple[list[version_tools.VersionEntry], str]:
    """Parse a changelog file and returns a list of version entries."""
    file_path = _utils.find_file(path)
    file = _utils.resolve_path(file_path)

    with file.open("r", encoding="utf-8") as f:
        changelog: list[version_tools.VersionEntry] = [
            {"version": DEFAULT_VER, "changes": []},
        ]
        current_entry: version_tools.VersionEntry = changelog[-1]

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
                current_entry["changes"].append(change)
            elif changes := current_entry["changes"]:
                changes[-1] += f" {line}"
            else:
                raise ValueError(
                    f"Invalid changelog format at line {line_no}: "
                    'Expected "-" and then text content',
                )
    return changelog, file_path


def dump(entries: list[version_tools.VersionEntry], path: str) -> None:
    """Write a formatted changelog to the specified file path."""
    file = _utils.resolve_path(path, for_write=True)

    changelog = []
    for entry in entries:
        version = entry["version"]
        changes = entry["changes"]

        valid_version = version_tools.parse_version(version)
        ver_label = version if valid_version else DEFAULT_VER

        section = [ver_label] if ver_label != DEFAULT_VER else []
        section += [f"- {change}" for change in changes]
        changelog.append("\n".join(section))

    content: str = "\n\n".join(changelog) + "\n"

    with file.open("w", encoding="utf-8") as f:
        f.write(content.strip())
