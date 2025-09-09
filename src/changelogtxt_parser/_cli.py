import argparse
import sys
from typing import Any

from changelogtxt_parser import _utils, app, serdes

# ruff: noqa: T201 allow print in CLI


def _get_cli_args() -> tuple[argparse.ArgumentParser, dict[str, Any]]:
    description = """changelogtxt helps you manage your changelog file.

    changelogtxt COMMAND --help for information about commands.
    """

    parser = argparse.ArgumentParser(
        add_help=True,
        conflict_handler="resolve",
        description=description,
    )

    subparsers = parser.add_subparsers(dest="command")

    check_tag = subparsers.add_parser(
        "check-tag",
        description="Verify that a tag in the changelog matches the provided tag.",
        help="Checks if a tag in the changelog matches the specified tag.",
    )
    check_tag.add_argument(
        "-t",
        "--tag",
        help="Tag name is required.",
        required=True,
    )
    check_tag.add_argument(
        "-f",
        "--file",
        help="Optional file path.",
        required=False,
        default="./",
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
        default="./",
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
        default="./",
    )
    update.add_argument(
        "--force",
        action="store_true",
        help="Force update of an existing version",
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
    command = cli_args.pop("command", None)

    match command:
        case "check-tag":
            file = _utils.find_file(file)
            app.check_tag(tag, file)
            print(f"Tag validation for {tag} was successful.")
        case "check-format":
            file = _utils.find_file(file)
            serdes.load(file)
            print("Changelog format validation was successful.")
        case "summarize-news":
            diff = app.summarize_news(source_file, target_file)
            if any(diff):
                print(diff)
            else:
                print("No changes found", file=sys.stderr)
                sys.exit(1)
        case "update":
            file = _utils.find_file(file)
            app.update(tag, message, file, force=force)
            print(f"File update was successful and generated at: {file}")
        case _:
            print("No command supplied.", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
