"""App ChangelogTXT Module."""

from changelogtxt_parser import _utils, serdes
from changelogtxt_parser import version as version_tools

DEFAULT_VER = "Unreleased"


def update(
    version: str,
    message: str,
    path: str,
    *,
    force=False,
) -> None:
    """
    Add a new change message to the specified version in the changelog file.

    Creates a new version entry if it doesn't exist.
    """
    if not message:
        raise ValueError("Message must not be empty.")

    new_version = str(version_tools.parse_version(version) or DEFAULT_VER)
    entries = serdes.load(path)

    for entry in entries:
        if new_version == entry["version"]:
            if force or new_version == DEFAULT_VER:
                entry["changes"].append(message)
                break
            else:
                raise ValueError("Cannot overwrite an existing version.")
    else:
        entries.insert(1, {"version": f"v{new_version}", "changes": [message]})

    serdes.dump(entries, path)


def check_tag(tag: str, file_path: str) -> None:
    """
    Validate whether a given version tag exists in the changelog file.

    :param tag: The version tag to validate (e.g., "1.2.3" or "v1.2.3").
    :param file_path: Path to the changelog file to search within.
    :raises ValueError: If the specified tag is not found in the changelog.
    """
    entries = serdes.load(file_path)
    target_ver = version_tools.parse_version(tag)
    for entry in entries:
        current_ver = version_tools.parse_version(entry["version"])
        if current_ver == target_ver:
            return
    raise ValueError(f"Tag '{tag}' not found in changelog.")


def _changes_count(entries: list[version_tools.VersionEntry]) -> int:
    for entry in entries:
        if entry["version"] == DEFAULT_VER:
            return len(entry["changes"])
    return 0


def compare_files(
    source_file_path: str,
    target_file_path: str,
) -> list[version_tools.VersionEntry]:
    """
    Compare two changelog files to detect version or change differences.

    :param source_file_path: Path to the original changelog file.
    :param target_file_path: Path to the updated changelog file to compare against.
    :return: A list of VersionEntry representing the differences found,
             or an empty list if the files are equivalent.
    """
    src_file = serdes.load(source_file_path)
    trg_file = serdes.load(target_file_path)
    src_count_changes = _changes_count(src_file)
    trg_count_changes = _changes_count(trg_file)

    if len(src_file) != len(trg_file) or src_count_changes != trg_count_changes:
        return _utils.get_diffs(src_file, trg_file)

    return []
