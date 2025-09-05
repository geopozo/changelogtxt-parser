"""App ChangelogTXT Module."""

from changelogtxt_parser import _utils, serdes
from changelogtxt_parser import version as version_tools

DEFAULT_VER = "unreleased"


# Claude,
# * Crea una strategia de hypothesis para la generación de string alreatorio `changes`,
#       unica y exlusivamente para las pruebas que usen message.
# * Usar el fixture de tmp file de pytest para las pruebas que usen file_path.
# * Arreglar la data del tmp fixture para que coincida con las pruebas.


#   update():
#      1) Si envia arg `version` y es nueva debe agregarla y verificar que
#          esta en el archivo.
#      2) Si envia arg `version` y es nueva y envia arg `message` debe agregar
#          la versiòn y la `bullet` con el texto del mensaje.
#      3) Si envia arg `version` y es nueva y hay `changes` en `unreleased` debe
#          agregar la version nueva y sumarle los `changes` de `unreleased` a esa
#          version.
#      4) Si envia arg `version` y es nueva y envia arg `message` y hay `changes`
#          en `unreleased` debe agregar la vesion nueva, sumarle los `changes` de
#          `unreleased` a esa version y el `message` verificar que esa en primera
#          posición.
#      5) Si envia arg `version` y ya existe en el archivo debe validar que salga
#          el ValueError.
#      6) Si envia arg `version` y ya existe en el archivo y envia el arg `force`
#          debe validar que salga un ValueError porque no agregara nada nuevo.
#      7) Si envia arg `version` y ya existe en el archivo y envia el arg `force`
#          y envia el arg `message`, y no hay `changes` en esa version debe agregar
#          el `message` a esa version como un nuevo `changes`.
#      8) Si envia arg `version` y ya existe en el archivo y envia el arg `force`
#          y envia el arg `message`, y hay `changes` en esa version debe agregar
#          el `message` a esa version en la primera posición.
#      9) Si envia arg `version`y es igual a `unreleased` y no hay mas `changes`
#          debe agregar esa `bullet` a `unreleased` en el archivo.
#      10) Si envia arg `version`y es igual a `unreleased` y hay mas `changes` debe
#          debe agregar esa `bullet` a `unreleased` en la primera posición del archivo.
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


#   check_tag():
#       1) Si envia arg `tag` y existe verificar el retorno `None`
#       2) Si envia arg `tag` que no existe debe verificar el ValueError
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


# Crea data mock de dos tmp(fixture) para source y target file path:
# Casos de prueba:
# * Pasar las dos changelog iguales y verificar que retorne `[]`
# * Pasar dos changelog diferentes y verificar que retorne len(list) > 0
# Está descripción no es completa. Cuales son los ingresos y cuales son las
# salidas posibles. Es decir, en que sentido puede ser iguales. Y para dos
# changelog iguales, des comparar changelogs de extremos. Otra vez, tabla.
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
