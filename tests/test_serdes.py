import pytest
from hypothesis import HealthCheck, given, settings

from changelogtxt_parser import serdes
from tests import strategies as sts

BASE_SETTINGS = settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
CHANGELOG_CONTENT = "v1.0.1\n- Fixed bug\n\nv1.0.0\n- Initial release"
DEFAULT_FILE = "CHANGELOG.txt"


class TestRoundtrip:
    @BASE_SETTINGS
    @given(entries=sts.list_of_version_entries)
    def test_roundtrip(
        self,
        entries,
        tmp_path,
    ):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)

        serdes.dump(entries, file)
        loaded = serdes.load(file)

        assert loaded == entries

    def test_empty_bullet_raises_error(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text("v1.0.0\n-\n- Valid change")

        with pytest.raises(
            ValueError,
            match='Invalid changelog format at line 2: Expected content after "-"',
        ):
            serdes.load(file)

    def test_missing_bullet_raises_error(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text("v1.0.0\nValid change")

        with pytest.raises(
            ValueError,
            match=(
                'Invalid changelog format at line 2: Expected "-" and then text content'
            ),
        ):
            serdes.load(file)
