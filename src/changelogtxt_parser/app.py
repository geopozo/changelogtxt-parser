"""App ChangelogTXT Module."""

from changelogtxt_parser import serdes
from changelogtxt_parser import version as version_tools


def update(
    version: str,
    message: str,
    file_path: str = "./CHANGELOG.txt",
    *,
    force: bool = False,
    strict: bool = False,
) -> None:
    """
    Create a new version entry if it doesn't exist.

    Args:
        version: Version identifier to update or create in the changelog.
        message: Change message to add under the specified version.
        file_path: Path to the changelog file to be updated.
        force: If True, allows adding changes to an existing version.
            Defaults to False.
        strict: If True, attempts to parse the version string for each entry.
            Defaults to False.

    Raises:
        ValueError: If parsing version fails.
        RuntimeError: If attempting to adding changes to an existing version without
            force.

    """
    if not version:
        new_version = ""
    elif strict:
        if not (parsed := version_tools.parse_version(version)):
            raise ValueError(f"Poorly formatted version value {version}")
        new_version = f"v{parsed}"
    else:
        new_version = version

    entries: list[version_tools.VersionEntry] = serdes.load(file_path)

    if not entries:
        entries = [{"version": "", "changes": []}]

    for entry in entries:
        if new_version.removeprefix("v") == entry["version"].removeprefix("v"):
            if not force and new_version:
                raise RuntimeError("Cannot overwrite an existing version.")
            if not message:
                raise ValueError("Version already exists: Nothing to do.")
            current_changes = entry["changes"]
            break
    else:
        should_absorb_unreleased = new_version and entries[0]["version"] == ""
        new_entry: version_tools.VersionEntry = {
            "version": new_version,
            "changes": entries.pop(0)["changes"] if should_absorb_unreleased else [],
        }
        entries.insert(0, new_entry)
        current_changes = new_entry["changes"]
    if message:
        current_changes.insert(0, message)

    serdes.dump(entries, file_path)


def get_tag(tag: str, file_path: str) -> version_tools.VersionEntry:
    """
    Return a VersionEntry from the tag in the changelog file.

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
            return entry
    raise ValueError(f"Tag '{tag}' not found in changelog.")


def summarize_news(
    source_file_path: str,
    target_file_path: str,
) -> tuple[set[str], dict[str, set[str]]]:
    """
    Compare two changelog files to detect version or change differences.

    Args:
        source_file_path: Path to the original changelog file.
        target_file_path: Path to the updated changelog file to compare against.

    Returns:
        A list of tuple[set[str], dict[str, list[str]]] representing the differences
        found, or an empty list if the files are equivalent.

    """
    src = serdes.load(source_file_path)
    trg = serdes.load(target_file_path)

    src_dict = {entry["version"]: entry["changes"] for entry in src}
    trg_dict = {entry["version"]: entry["changes"] for entry in trg}

    new_versions = trg_dict.keys() - src_dict.keys()
    new_changes = {}
    for v in src_dict.keys() & trg_dict.keys():
        if c := set(trg_dict[v]) - set(src_dict[v]):
            new_changes[v] = c

    return new_versions, new_changes
