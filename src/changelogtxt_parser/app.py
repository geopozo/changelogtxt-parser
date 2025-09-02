"""App ChangelogTXT Module."""

from changelogtxt_parser import _utils, serdes
from changelogtxt_parser import version as version_tools

DEFAULT_VER = "Unreleased"


def update(
    version: str | None,
    message: str,
    path: str = "./",
) -> None:
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

    entries, file_path = serdes.load(path)

    for entry in entries:
        if entry["version"] == version:
            entry["changes"].append(message)
            break
    else:
        entries.insert(1, {"version": version, "changes": [message]})

    serdes.dump(entries, file_path)


def check_tag(tag: str, path: str = "./") -> None:
    """
    Validate whether a given version tag exists in the changelog file.

    Prefixes the tag with 'v' if missing.
    """
    if not tag.startswith("v"):
        tag = f"v{tag}"

    entries, _ = serdes.load(path)
    for entry in entries:
        if entry["version"] == tag:
            return
    raise ValueError(f"Tag '{tag}' not found in changelog.")


def _changes_count(entries: list[version_tools.VersionEntry]) -> int:
    for entry in entries:
        if entry["version"] == DEFAULT_VER:
            return len(entry["changes"])
    return 0


def compare_files(source_file: str, target_file: str) -> list[str]:
    """Compare two changelog files to detect version or change differences."""
    src_file, _ = serdes.load(source_file)
    trg_file, _ = serdes.load(target_file)
    src_changes = _changes_count(src_file)
    trg_changes = _changes_count(trg_file)

    if len(src_file) != len(trg_file) or src_changes != trg_changes:
        return _utils.get_diffs(src_file, trg_file)

    raise ValueError("Comparison failed: no differences found between the files.")
