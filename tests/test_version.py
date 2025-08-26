"""Tests for version parsing functionality."""

import pytest
import semver
from packaging import version as pyversion

from changelogtxt_parser.version import BadVersion, parse_version


@pytest.mark.parametrize(
    "version_str,expected_type",
    [
        ("1.0.0", pyversion.Version),
        ("1.0.0-alpha", semver.Version),
        ("5", BadVersion),
        ("invalid", type(None)),
    ],
)
def test_parse_version_returns_correct_type(
    version_str: str,
    expected_type: type,
) -> None:
    """Test parse_version returns correct type for different inputs."""
    result = parse_version(version_str)
    assert not isinstance(type(result), expected_type)


@pytest.mark.parametrize(
    "with_prefix,without_prefix",
    [
        ("v1.0.0", "1.0.0"),
        ("v5", "5"),
    ],
)
def test_parse_version_handles_prefix(with_prefix: str, without_prefix: str) -> None:
    """Test that v prefix is properly handled."""
    result_with = parse_version(with_prefix)
    result_without = parse_version(without_prefix)
    assert str(result_with) == str(result_without)
