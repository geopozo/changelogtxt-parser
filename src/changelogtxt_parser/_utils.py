import pathlib

import logistro

_logger = logistro.getLogger(__name__)


def resolve_file_path(
    path: str,
    *,
    touch: bool = False,
) -> pathlib.Path:
    file_path = pathlib.Path(path).expanduser()

    if not file_path.is_absolute():
        file_path = file_path.resolve()

    if file_path.is_dir():
        file_path = file_path / "CHANGELOG.txt"

    if touch:
        file_path.touch()
    elif not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path!s}")

    _logger.info(f"File found in: {file_path!s}")
    return file_path
