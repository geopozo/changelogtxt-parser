import argparse
import sys
from typing import Any

from changelogtxt_parser import _utils, app, serdes


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
        "compare",
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

    basic_args = parser.parse_args()
    return parser, vars(basic_args)


def run_cli() -> None:
    parser, cli_args = _get_cli_args()
    tag = cli_args.pop("tag", None)
    file = cli_args.pop("file", "")
    source_file = cli_args.pop("source", "")
    target_file = cli_args.pop("target", "")
    command = cli_args.pop("command", None)

    match command:
        case "check-tag":
            res = app.check_tag(tag, file)
        case "check-format":
            res, _ = serdes.load(file)
        case "compare":
            res = app.compare_files(source_file, target_file)
            res = res or "No changes"
        case _:
            res = "No command supplied."
            parser.print_help()
            sys.exit(1)

    _utils.logger.info(res)
    sys.exit(int(not res))
