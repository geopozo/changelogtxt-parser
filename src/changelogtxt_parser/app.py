"""App ChangelogTXT Module."""

from changelogtxt_parser import _utils, serdes
from changelogtxt_parser import version as version_tools

DEFAULT_VER = "unreleased"


def update(
    version: str,
    message: str,
    file_path: str,
    *,
    force=False,
) -> None:
    """
    Create a new version entry if it doesn't exist.

    Args:
        version: Version identifier to update or create in the changelog.
        message: Change message to add under the specified version.
        file_path: Path to the changelog file to be updated.
        force: If True, allows adding changes to an existing version.
            Defaults to False.

    Raises:
        ValueError: If parsing version fails.
        ValueError: If attempting to adding changes to an existing version without
            force.

    """
    version = version.lower()
    if version == DEFAULT_VER:
        new_version = version
        force = True
    elif not (new_version := version_tools.parse_version(version)):
        raise ValueError(f"Poorly formatted version value {version}")

    entries = serdes.load(file_path)
    for entry in entries:
        if str(new_version) == entry["version"]:
            if not force:
                raise ValueError("Cannot overwrite an existing version.")
            current_changes = entry["changes"]
            break
    else:
        entries.insert(
            0,
            {
                "version": f"v{new_version!s}",
                "changes": entries.pop(0)["changes"],
            },
        )
        current_changes = entries[0]["changes"]
    if message:
        current_changes.insert(0, message)
    serdes.dump(entries, file_path)


def check_tag(tag: str, file_path: str) -> None:
    """
    Validate whether a given version tag exists in the changelog file.

    Args:
        tag: The version tag to validate (e.g., "1.2.3" or "v1.2.3").
        file_path: Path to the changelog file to search within.

    Raises:
        ValueError: If the specified tag is not found in the changelog.

    """
    entries = serdes.load(file_path)
    target_ver = version_tools.parse_version(tag)
    for entry in entries:
        current_ver = version_tools.parse_version(entry["version"])
        if current_ver == target_ver:
            return
    raise ValueError(f"Tag '{tag}' not found in changelog.")


def compare_files(
    source_file_path: str,
    target_file_path: str,
) -> list[version_tools.VersionEntry]:
    """
    Compare two changelog files to detect version or change differences.

    Args:
        source_file_path: Path to the original changelog file.
        target_file_path: Path to the updated changelog file to compare against.

    Returns:
        A list of VersionEntry representing the differences found,
            or an empty list if the files are equivalent.

    """
    src_file = serdes.load(source_file_path)
    trg_file = serdes.load(target_file_path)

    return _utils.get_diffs(src_file, trg_file)
