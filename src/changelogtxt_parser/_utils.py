import json
import logging
import os
import pathlib
from typing import Any

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

    if touch:
        file_path.touch()

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path


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


def get_diffs(source: list[Any], target: list[Any]) -> list[Any]:
    set1 = {json.dumps(entry, sort_keys=True) for entry in source}
    set2 = {json.dumps(entry, sort_keys=True) for entry in target}
    diffs = [json.loads(diff) for diff in list(set1.symmetric_difference(set2))]
    return diffs
