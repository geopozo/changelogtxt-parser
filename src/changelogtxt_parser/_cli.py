import argparse
import pprint
import sys
from typing import Any

import logistro

from changelogtxt_parser import app, serdes

# ruff: noqa: T201 allow print in CLI

DEFAULT_FILE = "./CHANGELOG.txt"


def _get_cli_args() -> tuple[argparse.ArgumentParser, dict[str, Any]]:
    description = """changelogtxt helps you manage your changelog file.

    changelogtxt COMMAND --help for information about commands.
    """

    parser = argparse.ArgumentParser(
        add_help=True,
        parents=[logistro.parser],
        conflict_handler="resolve",
        description=description,
    )

    subparsers = parser.add_subparsers(dest="command")

    get_tag = subparsers.add_parser(
        "get-tag",
        description="Verify that a tag in the changelog matches the provided tag.",
        help="Checks if a tag in the changelog matches the specified tag.",
    )
    get_tag.add_argument(
        "tag",
        help="Tag name is required.",
    )
    get_tag.add_argument(
        "-f",
        "--file",
        help="Optional file path.",
        required=False,
        default=DEFAULT_FILE,
    )

    check_format = subparsers.add_parser(
        "check-format",
        description="Verify that changelog file has the correct format",
        help="Check changelog format.",
    )
    check_format.add_argument(
        "-f",
        "--file",
        help="Optional file path.",
        required=False,
        default=DEFAULT_FILE,
    )

    compare_files = subparsers.add_parser(
        "summarize-news",
        description="Compare two changelog files.",
        help="Compare source file with target file.",
    )
    compare_files.add_argument(
        "source",
        help="First changelog file path.",
    )
    compare_files.add_argument(
        "target",
        help="Second changelog file path.",
    )
    update = subparsers.add_parser(
        "update",
        description="Add a new change message to the specified version.",
        help="Creates a new version entry if it doesn't exist.",
    )
    update.add_argument(
        "-t",
        "--tag",
        help="Tag name is required.",
        required=False,
    )
    update.add_argument(
        "-m",
        "--message",
        help="Message to add change from version",
        required=False,
    )
    update.add_argument(
        "-f",
        "--file",
        help="Optional file path.",
        required=False,
        default=DEFAULT_FILE,
    )
    update.add_argument(
        "--force",
        action="store_true",
        help="Force update of an existing version",
    )
    update.add_argument(
        "--strict",
        action="store_true",
        help="Force parse the version",
    )

    basic_args = parser.parse_args()
    return parser, vars(basic_args)


def run_cli() -> None:
    parser, cli_args = _get_cli_args()
    tag = cli_args.pop("tag", "")
    file = cli_args.pop("file", "")
    source_file = cli_args.pop("source", "")
    target_file = cli_args.pop("target", "")
    message = cli_args.pop("message", None)
    force = cli_args.pop("force", "")
    strict = cli_args.pop("strict", "")
    command = cli_args.pop("command", None)

    match command:
        case "get-tag":
            version_entry = app.get_tag(tag, file)
            print(version_entry.get("version"))
            print("\n".join(f"- {c}" for c in version_entry["changes"]))
        case "check-format":
            serdes.load(file)
            print("Changelog format validation was successful.")
        case "summarize-news":
            diff = app.summarize_news(source_file, target_file)
            if any(diff):
                pprint.pp(diff)
            else:
                print("No changes found", file=sys.stderr)
                sys.exit(1)
        case "update":
            app.update(tag, message, file, force=force, strict=strict)
            print(f"File update was successful and generated at: {file}")
        case _:
            print("No command supplied.", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
