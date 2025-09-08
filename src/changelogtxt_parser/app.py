"""App ChangelogTXT Module."""

from changelogtxt_parser import serdes
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
        if str(new_version) == entry["version"].removeprefix("v"):
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


#   summarize_news():
#       1) Si envia args `source_file_path` y `target_file_path` y el target
#           tiene `bullets` en unreleased(cabecera del archivo) debe verificar
#           que retorne algo similar a (set(), {'unreleased': {'new change'}}).
#       2) Si envia args `source_file_path` y `target_file_path` y el target
#           tiene no `bullets` en unreleased(cabecera del archivo) ni version
#           nueva debe verificar que retorne un (set(), {}).
#       3) Si envia args `source_file_path` y `target_file_path` y el target
#           tiene una version nueva debe verificar que retorne algo similar
#           ({'v1.0.2'}, {}).
#       4) Si envia args `source_file_path` y `target_file_path` y el target
#           tiene una version nueva y tiene `bullets` en unreleased debe verificar
#           que retorne algo similar a ({'v1.0.2'}, {'unreleased': {'new change'}})
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
