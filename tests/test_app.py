import re

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from changelogtxt_parser import app

CHANGELOG_CONTENT = """v1.0.1
- Fixed bug in parser

v1.0.0
- Initial release
"""

BASE_SETTINGS = settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
ASSUME_LIST = ["v1.0.1", "v1.0.0"]


@pytest.fixture
def changelog_tmp(tmp_path):
    path = tmp_path / "CHANGELOG.txt"
    path.write_text(CHANGELOG_CONTENT)
    return path


class TestCheckTag:
    @BASE_SETTINGS
    @given(data=st.data())
    def test_check_tag_existing(
        self,
        data,
        changelog_tmp,
        version_strings,
        random_string,
    ):
        version = data.draw(version_strings).removeprefix("v")
        message = data.draw(random_string)
        app.update(version, message, changelog_tmp)
        assume(version not in ASSUME_LIST)

        result = app.check_tag(version, str(changelog_tmp))

        assert result is None

    @BASE_SETTINGS
    @given(data=st.data())
    def test_check_tag_non_existing(self, data, changelog_tmp, version_strings):
        tag = data.draw(version_strings)
        assume(tag not in ASSUME_LIST)

        with pytest.raises(
            ValueError,
            match=re.escape(f"Tag '{tag}' not found in changelog"),
        ):
            app.check_tag(tag, str(changelog_tmp))


class TestUpdate:
    @BASE_SETTINGS
    @given(data=st.data())
    def test_update_add_new_version(
        self,
        data,
        changelog_tmp,
        version_strings,
        random_string,
    ):
        version = data.draw(version_strings)
        message = data.draw(random_string)
        assume(version not in ASSUME_LIST)

        app.update(version, message, str(changelog_tmp))
        updated_file = changelog_tmp.read_text(encoding="utf-8")
        first_line = updated_file.splitlines()[0]

        assert version in updated_file
        assert version in first_line
        assert f"- {message}" in updated_file

    @BASE_SETTINGS
    @given(data=st.data())
    def test_update_new_version_moves_unreleased_points(
        self,
        data,
        changelog_tmp,
        version_strings,
        random_string,
    ):
        version = data.draw(version_strings)
        message = data.draw(random_string)
        assume(version not in ASSUME_LIST)

        app.update("unreleased", message, str(changelog_tmp))
        app.update(version, "", str(changelog_tmp))
        updated_file = changelog_tmp.read_text(encoding="utf-8")
        first_line = updated_file.splitlines()[0]

        assert version in updated_file
        assert version in first_line
        assert message in updated_file

    @BASE_SETTINGS
    @given(data=st.data())
    def test_update_new_version_with_message_and_unreleased(
        self,
        data,
        changelog_tmp,
        version_strings,
        random_string,
    ):
        version = data.draw(version_strings)
        message = data.draw(random_string)
        assume(version not in ASSUME_LIST)

        app.update("unreleased", message, str(changelog_tmp))
        app.update(version, message, str(changelog_tmp))

        updated_file = changelog_tmp.read_text(encoding="utf-8").splitlines()
        idx = next(i for i, line in enumerate(updated_file) if version in line)
        assert f"- {message}" in updated_file[idx + 1]

    def test_update_existing_version_raises_error(self, changelog_tmp):
        with pytest.raises(ValueError, match="Cannot overwrite an existing version."):
            app.update("v1.0.1", "New change", str(changelog_tmp))

    def test_update_existing_version_with_force_no_message_allows_update(
        self,
        changelog_tmp,
    ):
        message = "New change"
        app.update("v1.0.1", message, str(changelog_tmp), force=True)
        updated_file = changelog_tmp.read_text(encoding="utf-8")
        second_line = updated_file.splitlines()[1]

        assert message in updated_file
        assert message in second_line

    @BASE_SETTINGS
    @given(data=st.data())
    def test_update_unreleased_no_existing_changes(
        self,
        data,
        changelog_tmp,
        version_strings,
        random_string,
    ):
        version = data.draw(version_strings)
        message = data.draw(random_string)
        assume(version not in ASSUME_LIST)

        app.update("unreleased", message, str(changelog_tmp))
        updated_file = changelog_tmp.read_text(encoding="utf-8")
        first_line = updated_file.splitlines()[0]

        assert f"- {message}" in updated_file
        assert message in first_line

    @BASE_SETTINGS
    @given(data=st.data())
    def test_update_unreleased_with_existing_changes(
        self,
        data,
        changelog_tmp,
        version_strings,
        random_string,
    ):
        version = data.draw(version_strings)
        message = data.draw(random_string)
        assume(version not in ASSUME_LIST)

        app.update("unreleased", "New feature added", str(changelog_tmp))
        app.update("unreleased", "Performance improvements", str(changelog_tmp))
        app.update("unreleased", message, str(changelog_tmp))

        updated_file = changelog_tmp.read_text(encoding="utf-8")
        message_index = updated_file.find(f"- {message}")
        new_feature_index = updated_file.find("- New feature added")
        performance_index = updated_file.find("- Performance improvements")

        assert f"- {message}" in updated_file
        assert "Performance improvements" in updated_file
        assert "New feature added" in updated_file
        assert message_index < new_feature_index
        assert message_index < performance_index

    def test_update_invalid_version_format(
        self,
        changelog_tmp,
    ):
        with pytest.raises(ValueError, match="Poorly formatted version value"):
            app.update("rc1.0.1fr", "test message", str(changelog_tmp))
