import pytest

import changelogtxt_parser as changelog

DEFAULT_FILE = "CHANGELOG.txt"
CHANGELOG_CONTENT = (
    "v1.0.0\n- First release\n- Bug fixes\n\nv0.1.0\n- Initial version\n"
)
PARSED_CHANGELOG: list[changelog.VersionEntry] = [
    {"version": "Unreleased", "changes": []},
    {"version": "v1.0.0", "changes": ["First release", "Bug fixes"]},
    {"version": "v0.1.0", "changes": ["Initial version"]},
]
DUMP_OUTPUT = "v1.0.0\n- First release\n- Bug fixes\n\nv0.1.0\n- Initial version\n"
TEST_PATHS = ["/nonexistent/changelog.txt", "subdir", "nested/deep"]
VERSION_CASES = [
    ("1.0.0", "New feature", "v1.0.0"),
    (None, "Unreleased feature", "Unreleased"),
]


class TestLoad:
    def test_load_valid_path(self, tmp_path):
        changelog_file = tmp_path / DEFAULT_FILE
        changelog_file.write_text(CHANGELOG_CONTENT)

        result = changelog.load(str(changelog_file))
        assert result == PARSED_CHANGELOG

    def test_load_file_not_found_error(self):
        with pytest.raises(FileNotFoundError, match="File not found"):
            changelog.load(TEST_PATHS[0])

    def test_load_return_right_path(self, tmp_path, monkeypatch):
        changelog_file = tmp_path / DEFAULT_FILE
        changelog_file.write_text(CHANGELOG_CONTENT)

        monkeypatch.chdir(tmp_path)
        result = changelog.load(DEFAULT_FILE)
        assert len(result) == 3
        assert result[1]["version"] == "v1.0.0"


class TestDump:
    def test_dump_valid_entries_and_path_file(self, tmp_path):
        changelog_file = tmp_path / DEFAULT_FILE

        changelog.dump(PARSED_CHANGELOG, str(changelog_file))

        content = changelog_file.read_text()
        assert content == DUMP_OUTPUT

    def test_dump_verify_modified_file(self, tmp_path):
        nested_path = tmp_path / "nested" / DEFAULT_FILE

        changelog.dump(PARSED_CHANGELOG, str(nested_path))

        assert nested_path.exists()
        content = nested_path.read_text()
        assert content == DUMP_OUTPUT


class TestFindChangelogTxtFile:
    def test_find_valid_base_path(self, tmp_path):
        changelog_file = tmp_path / "test.txt"
        changelog_file.write_text("test")

        result = changelog.find_changelogtxt_file(str(changelog_file))
        assert result == str(changelog_file)

    def test_find_trigger_error(self, tmp_path):
        with pytest.raises(FileNotFoundError, match=f"{DEFAULT_FILE} file not found"):
            changelog.find_changelogtxt_file(str(tmp_path))

    def test_find_valid_path_file_return_right_path(self, tmp_path):
        nested_dir = tmp_path / TEST_PATHS[1]
        nested_dir.mkdir(parents=True)
        changelog_file = nested_dir / DEFAULT_FILE
        changelog_file.write_text("test")

        result = changelog.find_changelogtxt_file(str(tmp_path))
        assert result == str(changelog_file)


class TestUpdateVersion:
    @pytest.fixture
    def setup_changelog(self, tmp_path):
        def _setup(content="Unreleased\n- Some change\n"):
            changelog_file = tmp_path / DEFAULT_FILE
            changelog_file.write_text(content)
            return str(tmp_path), str(changelog_file)

        return _setup

    @pytest.mark.parametrize("version,message,expected_version", VERSION_CASES)
    def test_update_valid_version_message_base_path(
        self,
        setup_changelog,
        version,
        message,
        expected_version,
    ):
        temp_dir, changelog_path = setup_changelog()

        result = changelog.update_version(version, message, temp_dir)
        assert result is True

        updated_content = changelog.load(changelog_path)
        if expected_version == "Unreleased":
            assert message in updated_content[0]["changes"]
        else:
            found_version = next(
                (e for e in updated_content if e["version"] == expected_version),
                None,
            )
            assert found_version is not None
            assert message in found_version["changes"]

    def test_update_version_without_v(self, setup_changelog):
        temp_dir, changelog_path = setup_changelog()

        result = changelog.update_version("1.0.0", "Feature", temp_dir)
        assert result is True

        updated_content = changelog.load(changelog_path)
        v_entry = next((e for e in updated_content if e["version"] == "v1.0.0"), None)
        assert v_entry is not None

    def test_update_valid_path_file_load_right_file(self, setup_changelog):
        temp_dir, changelog_path = setup_changelog(CHANGELOG_CONTENT)

        result = changelog.update_version("v1.0.0", "New change", temp_dir)
        assert result is True

        updated_content = changelog.load(changelog_path)
        v1_entry = next(e for e in updated_content if e["version"] == "v1.0.0")
        assert "New change" in v1_entry["changes"]
        assert len(v1_entry["changes"]) >= 2
