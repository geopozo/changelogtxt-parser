"""Version Parsing Utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TypedDict

import semver
from packaging import version as pyversion


class VersionEntry(TypedDict):
    """
    Represents a single changelog entry.

    Attributes:
        version (str): The version number or tag associated with the changes.
        changes (list[str]): A list of change descriptions for the specified version.

    """

    version: str
    changes: list[str]


# Class taken from:
# https://github.com/geopozo/github-helper/blob/andrew/more_versions/src/github_helper/api/versions.py
@dataclass(frozen=True, slots=True)
class BadVersion:
    """A weak parser that looks for instances where someone tried to tag."""

    _tag_part_re = re.compile(r"^(\d*)(?:\.?(.*))?$")
    tag: str
    major: int
    minor: int
    micro: int
    pre: None = None
    local: str | None = None
    is_prerelease: bool = False

    def __init__(self, tag: str) -> None:
        """Look for tag-like structures that parsers won't return."""
        object.__setattr__(self, "tag", tag)
        object.__setattr__(self, "major", 0)
        object.__setattr__(self, "minor", 0)
        object.__setattr__(self, "micro", 0)
        object.__setattr__(self, "pre", None)
        object.__setattr__(self, "local", None)
        object.__setattr__(self, "is_prerelease", False)

        tag = tag.removeprefix("v")

        major_match = self._tag_part_re.search(tag)
        if not major_match or not major_match.group(1):
            raise ValueError

        object.__setattr__(self, "major", int(major_match.group(1)))
        if not major_match.group(2):
            return

        minor_match = self._tag_part_re.search(major_match.group(2))
        if not minor_match or not minor_match.group(1):
            object.__setattr__(self, "local", major_match.group(2))
            return

        object.__setattr__(self, "minor", int(minor_match.group(1)))
        if not minor_match.group(2):
            return

        micro_match = self._tag_part_re.search(minor_match.group(2))
        if not micro_match or not micro_match.group(1):
            object.__setattr__(self, "local", minor_match.group(2))
            return

        object.__setattr__(self, "micro", int(micro_match.group(1)))
        object.__setattr__(self, "local", micro_match.group(2) or None)

    def __str__(self) -> str:
        """Print Version as string."""
        return self.__repr__()

    def __repr__(self) -> str:
        """Print Version as python-compatible string if possible."""
        pre = f"{self.pre[0]}{self.pre[1]}" if self.pre is not None else ""
        local = f"+{self.local}" if self.local is not None else ""
        return f"{self.major}.{self.minor}.{self.micro}{pre}{local}"


_VersionTypes = semver.Version | pyversion.Version | BadVersion | None


def parse_version(content: str) -> _VersionTypes:
    """
    Parse a version string using multiple versioning libraries.

    :return: a parsed version object from one of the supported libraries, or
    `None` if parsing fails.

    """
    content = content.removeprefix("v")
    v: _VersionTypes = None
    try:
        v = pyversion.Version(content)
    except pyversion.InvalidVersion:
        pass
    try:
        v = semver.Version.parse(content)
    except ValueError:
        pass
    try:
        v = BadVersion(content)
    except ValueError:
        pass
    if not v:
        return None
    return v
