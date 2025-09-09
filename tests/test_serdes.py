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
        entries.insert(0, {"version": "", "changes": []})

        serdes.dump(entries, file)
        loaded = serdes.load(file)

        assert loaded == entries


class TestLoad:
    @BASE_SETTINGS
    @given(changes=sts.list_of_strings)
    def test_load_bullets_without_version_unreleased_changes(self, changes, tmp_path):
        file = tmp_path / DEFAULT_FILE

        serdes.dump([{"version": "", "changes": changes}], file)
        result = serdes.load(str(file))

        assert result[0]["version"] == ""
        assert result[0]["changes"] == changes

    @BASE_SETTINGS
    @given(version=sts.version_strings, changes=sts.list_of_strings)
    def test_load_version_with_bullets(self, version, changes, tmp_path):
        file = tmp_path / DEFAULT_FILE

        serdes.dump([{"version": version, "changes": changes}], file)
        result = serdes.load(str(file))

        assert result[0]["version"] == ""
        assert result[0]["changes"] == []
        assert result[1]["version"] == version
        assert result[1]["changes"] == changes

    def test_load_empty_bullet_raises_error(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text("v1.0.0\n-\n- Valid change")

        with pytest.raises(
            ValueError,
            match='Invalid changelog format at line 2: Expected content after "-"',
        ):
            serdes.load(str(file))

    @BASE_SETTINGS
    @given(version=sts.version_strings, message=sts.random_string)
    def test_load_multiline_change_continuation(self, version, message, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text(f"{version}\n- {message}\n line another line", encoding="utf-8")

        result = serdes.load(str(file))
        expected = f"{message} line another line"

        assert result[-1]["changes"][0] == expected
