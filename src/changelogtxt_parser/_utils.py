import logging
import os
import pathlib

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# casos correctos pero dadas las dudas de la function seguiente, tengo que enter
# un poco mejor esto.
# Crea data mock y pasa a resolve_path(tmp) y que retorne el objeto de `Path` de
#   Path() correcta
# Casos de prueba:
# * Pasar arg path existente y retorne una instancia de Path y el str correcto
# * Pasar arg path y touch y verificar que el archivo fue creado.
# * Path que no existe devuelve FileNotFountError
def resolve_path(
    path: str,
    *,
    touch: bool = False,
) -> pathlib.Path:
    file_path = pathlib.Path(path).expanduser()

    if not file_path.is_absolute():
        file_path = file_path.resolve()

    # debemos revisar primero que no es dir?
    if touch:
        file_path.touch()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path


# probablemente este concepto sería incorrecto, "resultados infinitos".
# Similar a `resolve_path` pero debe retornar un str con CHANGELOG.txt
#   o el nombre del archivo que agrego en el arg `path`
def find_file(path: str = "./") -> str:
    if pathlib.Path(path).is_file():
        return path
    if pathlib.Path(path).is_dir():
        filename = "CHANGELOG.txt"
        for root, _, files in os.walk(path):
            if filename in files:
                file_path = str(pathlib.Path(root) / filename)
                logger.info(f"File found in: {file_path}")
                return file_path
    raise FileNotFoundError(f"{filename} file not found in the specified path.")
