"""SerDes(Serializer/Deserializer) Module."""

from __future__ import annotations

from changelogtxt_parser import _utils
from changelogtxt_parser import version as version_tools

# yo veo una lista de ejemplos buenos (tal vez no completo?) pero ya como was a
# estructurar las pruebas (lo de chat gpt)


# Crea data mock de texto plano para llenar un tmp(del fixture)
#   lo paso a load(tmp) y verifico que la salida coincida con
#   una lista de VersionEntry esperada.
# Casos de prueba:
# * Bullets sin version y verificar los 'changes' unreleased.
# * Version con bullets y sin bullets.
# * Bullets sin contenido para verificar el error.
def load(file_path: str) -> list[version_tools.VersionEntry]:
    """
    Parse a changelog file and returns a list of version entries.

    Args:
        file_path: Path to the file where the changelog will be read.

    Returns:
        A list of `VersionEntry` with changelog data

    """
    file = _utils.resolve_path(file_path)

    with file.open("r", encoding="utf-8") as f:
        changelog: list[version_tools.VersionEntry] = [
            {"version": "", "changes": []},
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
    return changelog


# Crea data mock de list[VersionEntry] y pasarla a dump(list) y
#   verifico que el archivo creado contenga parte de los cambios que genere.
# Casos de prueba:
# * Verificar llave "unrelease" y sus "changes" = [].
# * Verificar llave "unrelease" y sus "changes" que coincidan
#   con los de las entradas.
# * Una version con changes que tenga los bullets correctos.
# * Una version mal formateada y verificarla en el archivo
def dump(
    entries: list[version_tools.VersionEntry],
    file_path: str,
) -> None:
    """
    Write a formatted changelog to the specified file path.

    Each entry in the changelog includes a version string and a list of changes.

    Args:
        entries: A list of `VersionEntry` objects, each containing a version
            string and associated changes.
        file_path: Path to the file where the changelog will be written.

    """
    file = _utils.resolve_path(file_path, touch=True)

    changelog = []
    for entry in entries:
        version = entry["version"]
        changes = entry["changes"]

        section = (
            [str(f"v{_s}")] if (_s := version_tools.parse_version(version)) else []
        )
        section.extend([f"- {change}" for change in changes])
        changelog.append("\n".join(section))

    content: str = "\n\n".join(changelog) + "\n"

    with file.open("w", encoding="utf-8") as f:
        f.write(content.strip())
