# SPDX-License-Identifier: MIT
"""ChangelogTXT Parser Module."""

from changelogtxt_parser.app import get_tag, summarize_news, update
from changelogtxt_parser.serdes import dump, load

__all__ = [
    "dump",
    "get_tag",
    "load",
    "summarize_news",
    "update",
]
