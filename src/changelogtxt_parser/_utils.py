import logging
import pathlib

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def resolve_file_path(
    path: str,
    *,
    touch: bool = False,
) -> pathlib.Path:
    file_path = pathlib.Path(path).expanduser()

    if not file_path.is_absolute():
        file_path = file_path.resolve()

    if file_path.is_dir():
        raise IsADirectoryError(f"Expected a file but got a directory: {file_path}")

    if touch:
        file_path.touch()
    elif not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"File found in: {file_path}")
    return file_path
