import semver
from hypothesis import given, settings
from packaging import version as pyversion

from changelogtxt_parser import version as version_tools
from tests import strategies as sts

BASE_SETTINGS = settings(max_examples=30)


class TestParseVersion:
    @BASE_SETTINGS
    @given(version=sts.version_st)
    def test_parse_version_with_v_prefix_returns_parsed_version(self, version):
        result = version_tools.parse_version(version)

        assert result is not None
        assert isinstance(
            result,
            (
                pyversion.Version,
                semver.Version,
                version_tools.BadVersion,
            ),
        )

    def test_parse_version_return_none(self):
        result = version_tools.parse_version("malformed")

        assert result is None
