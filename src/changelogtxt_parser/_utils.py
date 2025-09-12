import logging
import os
import pathlib

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def resolve_path(
    path: str,
    *,
    touch: bool = False,
) -> pathlib.Path:
    file_path = pathlib.Path(path).expanduser()

    if not file_path.is_absolute():
        file_path = file_path.resolve()

    if file_path.is_dir():
        raise IsADirectoryError(f"Expected a file but got a directory: {file_path}")
    # no hay nada en el nombre para sugerir que estamos buscando un file

    if touch:
        file_path.touch()
    elif not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path

# esto es buscando arriba o bajo
# usamos esto?
# normalmente vamos bajando hasta que encontramos un .git y
# buscamos ahí
def find_file(path: str = "./") -> str:
    filename = "CHANGELOG.txt"
    if pathlib.Path(path).is_file():
        return path
    if pathlib.Path(path).is_dir():
        for root, _, files in os.walk(path):
            if filename in files:
                file_path = str(pathlib.Path(root) / filename)
                logger.info(f"File found in: {file_path}")
                return file_path
    raise FileNotFoundError(f"{filename} file not found in the specified path.")
