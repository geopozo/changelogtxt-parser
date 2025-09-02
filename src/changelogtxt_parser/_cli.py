import argparse
import logging
import sys
from typing import Any

from changelogtxt_parser import app, serdes

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


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
    update = subparsers.add_parser(
        "update",
        description="Add a new change message to the specified version.",
        help="Creates a new version entry if it doesn't exist.",
    )
    update.add_argument(
        "-t",
        "--tag",
        help="Tag name is required.",
        required=True,
    )
    update.add_argument(
        "-m",
        "--message",
        help="Message is required.",
        required=True,
    )
    update.add_argument(
        "-f",
        "--file",
        help="Optional file path.",
        required=False,
        default="./",
    )

    basic_args = parser.parse_args()
    return parser, vars(basic_args)


def run_cli() -> None:
    parser, cli_args = _get_cli_args()
    tag = cli_args.pop("tag", None)
    file = cli_args.pop("file", "")
    source_file = cli_args.pop("source", "")
    target_file = cli_args.pop("target", "")
    message = cli_args.pop("message", "")
    command = cli_args.pop("command", None)

    match command:
        case "check-tag":
            try:
                app.check_tag(tag, file)
                logger.info(f"Tag validation for {tag} was successful.")
                reteval = 0
            except (ValueError, TypeError):
                logger.exception("Invalid tag")
                reteval = 1
        case "check-format":
            try:
                serdes.load(file)
                logger.info("Changelog format validation was successful.")
                reteval = 0
            except ValueError:
                logger.exception("Invalid changelog format")
                reteval = 1
        case "compare":
            try:
                res = app.compare_files(source_file, target_file)
                logger.info(res)
                reteval = 0
            except ValueError:
                logger.exception("No changes founded")
                reteval = 1
        case "update":
            try:
                app.update(tag, message, file)
                logger.info("File update was successful and generated at: {file}")
                reteval = 0
            except ValueError:
                logger.exception("File update failed")
                reteval = 1
        case _:
            logger.error("No command supplied.")
            parser.print_help()
            sys.exit(1)

    sys.exit(reteval)
