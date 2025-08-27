import argparse
import sys
from typing import Any

import changelogtxt_parser as changelog


def _get_cli_args() -> tuple[argparse.ArgumentParser, dict[str, Any]]:
    description = """changelogtxt helps you manage your changelog file.

    See changelogtxt COMMAND --help for information about commands.
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

    check_format = subparsers.add_parser(
        "check-format",
        description="Verify that changelog file has the correct format",
        help="Check changelog format.",
    )
    check_format.add_argument(
        "-f",
        "--file",
        help="Optional file path to check format.",
        required=False,
        default="./",
    )

    basic_args = parser.parse_args()
    return parser, vars(basic_args)


def run_cli() -> None:
    parser, cli_args = _get_cli_args()
    tag = cli_args.pop("tag", None)
    file = cli_args.get("file", "")
    command = cli_args.pop("command", None)
    match command:
        case "check-tag":
            res = changelog.check_tag(tag)
            sys.exit(int(not res))
        case "check-format":
            if not (path_file := changelog.find_changelogtxt_file(file)):
                sys.exit(1)
            print(f"File found in: {path_file}")
            res = changelog.load(path_file)
            sys.exit(int(not res))
        case _:
            print("No command supplied.", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
