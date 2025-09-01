import logging
import os
import pathlib

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def resolve_path(
    path: str,
    *,
    for_write: bool = False,
    base_dir: pathlib.Path | None = None,
) -> pathlib.Path:
    file_path = pathlib.Path(path).expanduser()

    if not file_path.is_absolute():
        base = base_dir if base_dir else pathlib.Path.cwd()
        file_path = (base / file_path).resolve()

    if for_write:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    elif not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path


def find_file(path: str = "./") -> str:
    """Search for a 'CHANGELOG.txt' file starting from the given path."""
    if pathlib.Path(path).is_file():
        return path
    if pathlib.Path(path).is_dir():
        filename = "CHANGELOG.txt"
        for root, _, files in os.walk(path):
            if filename in files:
                path_file = str(pathlib.Path(root) / filename)
                logger.info(f"File found in: {path_file}")
                return path_file
    raise FileNotFoundError(f"{filename} file not found in the specified path.")
