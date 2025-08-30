# SPDX-License-Identifier: MIT

# por qué todo en __init__?

# nombres lo hace difícil leer. Cambias durante.

from __future__ import annotations

import logging
import os
import pathlib
import re
import sys
from typing import Optional, TypedDict

from changelogtxt_parser.version import parse_version # -_-

VersionEntry = TypedDict("VersionEntry", {"version": str, "changes": list[str]})

BULLET_RE = re.compile(r"^-") # == str.startswith("-") -_-
DEFAULT_VER = "Unreleased"

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def _resolve_path(
    path_file: str,
    for_write: bool = False,
    base_dir: Optional[pathlib.Path] = None,
) -> pathlib.Path:

    path = pathlib.Path(path_file).expanduser()

    if not path.is_absolute():
        base = base_dir if base_dir else pathlib.Path.cwd()
        path = (base / path).resolve()
    # por qué no solo path.resolve()?, o, si vas a permitir
    # "path/relativo", por que necesitamos "base_dir"?
    # nunca se usa. si el usuario va a dar un "basedir",
    # van a hacerlo en el mismo string de path_file

    if for_write:
        path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    return path


def load(path_file: str) -> list[VersionEntry]:
    file = _resolve_path(path_file)

    with file.open("r", encoding="utf-8") as f:
        changelog: list[VersionEntry] = [{"version": DEFAULT_VER, "changes": []}]
        current: VersionEntry = changelog[-1]
        need_bullet = False # no creo
        last_v_line_no = None

        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue

            # no hay necesidad de -, solo que texto sin - es una version
            if need_bullet and not BULLET_RE.match(line):
                raise ValueError(
                    f"Invalid changelog format at line {line_no}: "
                    f"Expected a '-' bullet after version declared at line {last_v_line_no}",
                )

            # si hay versión
            if parse_version(line):
                current = {"version": line, "changes": []}
                changelog.append(current)
                need_bullet = True # nop
                last_v_line_no = line_no
                continue

            # si hay punto
            if BULLET_RE.match(line): # entonces, sería primero, regex demasiado
                need_bullet = False # nop
                change = line.lstrip("-").strip() # sip
                if not change:
                    raise ValueError(
                        f"Invalid changelog format at line {line_no}: "
                        f'Expected content after "-"',
                    )
                current["changes"].append(change)
                continue

            # cuando puede pasar esto? que es esto?
            # no entiendo
            current_list = current["changes"]
            if current_list:
                current_list[-1] += f" {line}"
            else:
                current_list.append(line)

    return changelog


def dump(entries: list[VersionEntry], path_file: str) -> None:
    path = _resolve_path(path_file, True)

    lines = []
    # probably el usuario no uso "Unreleased" pero algo blanco
    for e in entries:
        if e["version"] == DEFAULT_VER and not e["changes"]:
            continue
        header = [] if e["version"] == DEFAULT_VER else [e["version"]]
        lines.append("\n".join(header + [f"- {c}" for c in e["changes"]]))
    # un poco difícil leer, demasiado condensado creo

    content: str = "\n\n".join(lines) + "\n"

    with path.open("w", encoding="utf-8") as f:
        f.write(content)

    logging.info(f"File generated at: {path}")



def find_changelogtxt_file(base_path: str = "./") -> str | None:
    if pathlib.Path(base_path).is_file():
        return base_path
    if pathlib.Path(base_path).exists(): # is_dir()?
        filename = "CHANGELOG.txt"
        for root, _, files in os.walk(base_path):
            if filename in files:
                return os.path.join(root, filename)
    raise FileNotFoundError(f"{filename} file not found in the specified path.")


def update_version( # solo "update" tal vez?
    version: str | None,
    message: str,
    base_path: str = "./", # base_path es raro el nombre
) -> bool:
    if not version:
        version = DEFAULT_VER

    if not version.startswith("v"):
        version = f"v{version}"

    if not message:
        raise ValueError("Message must not be empty.") # no?

    path_file = find_changelogtxt_file(base_path)
    if path_file: # es posible `not path_file`?
        logs = load(path_file)
        for log in logs:
            if log["version"] == version:
                log["changes"].append(message)
                break
            else:
                logs.insert(1, {"version": version, "changes": [message]})
                # por qué no break?

        dump(logs, path_file)
        return True
    return False # cuando?

# otra función para ver si hay unreleased.

def check_tag(tag: str, base_path: str = "./") -> bool:
    file_path = find_changelogtxt_file(base_path)
    if file_path:
        logs = load(file_path)
        for log in logs:
            if log["version"] == tag:
                logging.info(f"Tag validation for '{tag}' was successful.")
                return True
    print(
        f"Tag '{tag}' not found in changelog.",
        file=sys.stderr,
    )
    return False

# no puede lanzar puntos nuevos en versiones antiguas.
def _changes_count(logs, version):
    for log in logs:
        if log["version"] == version:
            return len(log["changes"])
    return 0


def compare_files(source_file: str, target_file: str) -> bool:
    src_file = load(source_file)
    trg_file = load(target_file)

    if len(src_file) != len(trg_file):
        logging.info("New version")
        return True

    src_changes = _changes_count(src_file, DEFAULT_VER)
    trg_changes = _changes_count(trg_file, DEFAULT_VER)

    if src_changes != trg_changes:
        logging.info("New Unreleased point")
        return True

    logging.info("No changes")
    return False
