import re

import pytest
from hypothesis import HealthCheck, assume, given, settings

from changelogtxt_parser import app
from tests import strategies as sts

BASE_SETTINGS = settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
DEFAULT_FILE = "CHANGELOG.txt"
ASSUME_LIST = ["v1.0.1", "v1.0.0"]
CHANGELOG_CONTENT = "v1.0.1\n- Fixed bug\n\nv1.0.0\n- Initial release"


class TestCheckTag:
    @BASE_SETTINGS
    @given(version=sts.version_st, message=sts.random_string)
    def test_get_tag_existing(
        self,
        version,
        message,
        tmp_path,
    ):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)
        assume(version not in ASSUME_LIST)

        app.update(version, message, file)
        result = app.get_tag(version, file)

        assert result["version"] == version
        assert result["changes"][0] == message

    @BASE_SETTINGS
    @given(version=sts.version_st)
    def test_get_tag_non_existing(self, version, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)
        assume(version not in ASSUME_LIST)

        with pytest.raises(
            ValueError,
            match=(f"Tag '{version}' not found in changelog"),
        ):
            app.get_tag(version, file)


class TestUpdate:
    @BASE_SETTINGS
    @given(version=sts.version_st, message=sts.random_string)
    def test_update_add_new_version(
        self,
        version,
        message,
        tmp_path,
    ):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)
        assume(version not in ASSUME_LIST)

        app.update(version, message, file)
        updated_file = file.read_text(encoding="utf-8")
        first_line = updated_file.splitlines()[0]

        assert version in first_line
        assert f"- {message}" in updated_file

    @BASE_SETTINGS
    @given(version=sts.version_st, message=sts.random_string)
    def test_update_add_unreleased_points_to_new_version(
        self,
        version,
        message,
        tmp_path,
    ):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)
        assume(version not in ASSUME_LIST)

        app.update("", message, file)
        app.update(version, "", file)
        updated_file = file.read_text(encoding="utf-8")
        first_line = updated_file.splitlines()[0]
        second_line = updated_file.splitlines()[1]

        assert version in first_line
        assert message in second_line

    def test_update_existing_version_raises_error(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)
        with pytest.raises(
            RuntimeError,
            match=re.escape("Cannot overwrite an existing version."),
        ):
            app.update("v1.0.1", "New change", file)

    def test_update_existing_version_with_force_allows_update(
        self,
        tmp_path,
    ):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)
        message = "New change"
        app.update("v1.0.1", message, file, force=True)
        updated_file = file.read_text(encoding="utf-8")
        second_line = updated_file.splitlines()[1]

        assert message in updated_file
        assert message in second_line

    @BASE_SETTINGS
    @given(version=sts.version_st, message=sts.random_string)
    def test_update_unreleased_with_existing_changes(
        self,
        version,
        message,
        tmp_path,
    ):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)
        assume(version not in ASSUME_LIST)

        app.update("", "New feature added", file)
        app.update("", "Performance improvements", file)
        app.update("", message, file)

        updated_file = file.read_text(encoding="utf-8")
        message_index = updated_file.find(f"- {message}")
        new_feature_index = updated_file.find("- New feature added")
        performance_index = updated_file.find("- Performance improvements")

        assert f"- {message}" in updated_file
        assert "Performance improvements" in updated_file
        assert "New feature added" in updated_file
        assert message_index < new_feature_index
        assert message_index < performance_index

    def test_update_invalid_version_format(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)

    def test_update_version_missing_message(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text(CHANGELOG_CONTENT)
        with pytest.raises(
            ValueError,
            match=re.escape("Version already exists: Nothing to do."),
        ):
            app.update("v1.0.1", "", file, force=True)


class TestSummarizeNews:
    def test_summarize_news_target_has_unreleased_changes(self, tmp_path):
        source_file = tmp_path / "source.txt"
        target_file = tmp_path / "target.txt"
        source_file.write_text(CHANGELOG_CONTENT)
        target_file.write_text(CHANGELOG_CONTENT)

        app.update("", "New change", target_file)
        new_versions, _ = app.summarize_news(source_file, target_file)

        assert new_versions == {""}

    def test_summarize_news_no_changes(self, tmp_path):
        source_file = tmp_path / "source.txt"
        target_file = tmp_path / "target.txt"
        source_file.write_text(CHANGELOG_CONTENT)
        target_file.write_text(CHANGELOG_CONTENT)

        new_versions, new_changes = app.summarize_news(source_file, target_file)

        assert new_versions == set()
        assert new_changes == {}

    @BASE_SETTINGS
    @given(version=sts.version_st, message=sts.random_string)
    def test_summarize_news_new_version(
        self,
        version,
        message,
        tmp_path,
    ):
        source_file = tmp_path / "source.txt"
        target_file = tmp_path / "target.txt"
        source_file.write_text(CHANGELOG_CONTENT)
        target_file.write_text(CHANGELOG_CONTENT)
        assume(version not in ASSUME_LIST)

        app.update(version, message, target_file)

        new_versions, new_changes = app.summarize_news(source_file, target_file)

        assert version in new_versions
        assert new_changes == {}
