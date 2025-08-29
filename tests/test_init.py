import json
from hypothesis import HealthCheck, given, settings, strategies as st

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

valid_change_text = st.text(
    min_size=1,
    max_size=100,
    alphabet=st.characters(
        min_codepoint=32,
        max_codepoint=126,
        blacklist_categories=["Cc", "Cs"],
    ),
).filter(lambda x: x.strip())

version_entry_strategy = st.one_of(
    st.fixed_dictionaries(
        {
            "version": st.just("Unreleased"),
            "changes": st.lists(valid_change_text, max_size=10),
        },
    ),
    st.fixed_dictionaries(
        {
            "version": st.builds(
                lambda major, minor, patch: f"v{major}.{minor}.{patch}",
                major=st.integers(min_value=0, max_value=99),
                minor=st.integers(min_value=0, max_value=99),
                patch=st.integers(min_value=0, max_value=99),
            ),
            "changes": st.lists(valid_change_text, min_size=1, max_size=10),
        },
    ),
)


def assert_json_roundtrip(entries: list[changelog.VersionEntry]) -> None:
    json_str = json.dumps(entries)
    deserialized = json.loads(json_str)
    assert deserialized == entries


class TestLoad:
    def test_load_valid_path(self, tmp_path):
        changelog_file = tmp_path / DEFAULT_FILE
        changelog_file.write_text(CHANGELOG_CONTENT)

        result = changelog.load(str(changelog_file))
        assert result == PARSED_CHANGELOG
        assert_json_roundtrip(result)

    def test_load_return_right_path(self, tmp_path, monkeypatch):
        changelog_file = tmp_path / DEFAULT_FILE
        changelog_file.write_text(CHANGELOG_CONTENT)

        monkeypatch.chdir(tmp_path)
        result = changelog.load(DEFAULT_FILE)
        assert len(result) == 3
        assert result[1]["version"] == "v1.0.0"


class TestDump:
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(st.lists(version_entry_strategy, min_size=1, max_size=5))
    def test_dump_generated_entries(self, tmp_path, entries):
        changelog_file = tmp_path / DEFAULT_FILE

        changelog.dump(entries, str(changelog_file))

        loaded_entries = changelog.load(str(changelog_file))
        assert_json_roundtrip(loaded_entries)


class TestFindChangelogTxtFile:
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(st.lists(version_entry_strategy, min_size=1, max_size=3))
    def test_find_changelog_hypothesis(self, tmp_path, entries):
        changelog_file = tmp_path / DEFAULT_FILE
        changelog.dump(entries, str(changelog_file))

        result = changelog.find_changelogtxt_file(str(tmp_path))
        assert result
        assert result == str(changelog_file)

        loaded_entries = changelog.load(result)
        assert_json_roundtrip(loaded_entries)


class TestUpdateVersion:
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(min_codepoint=48, max_codepoint=57),
        ).filter(lambda x: not x.startswith("v")),
        valid_change_text,
    )
    def test_update_version(self, tmp_path, version, message):
        changelog_file = tmp_path / DEFAULT_FILE
        changelog_file.write_text("Unreleased\n- Some change\n")

        result = changelog.update_version(version, message, str(tmp_path))
        assert result is True

        updated_content = changelog.load(str(changelog_file))
        assert_json_roundtrip(updated_content)


class TestCheckTag:
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(st.lists(version_entry_strategy, min_size=1, max_size=5))
    def test_check_tag(self, tmp_path, entries):
        changelog_file = tmp_path / DEFAULT_FILE
        changelog.dump(entries, str(changelog_file))

        for entry in entries:
            if entry["version"] != "Unreleased":
                result = changelog.check_tag(entry["version"], str(tmp_path))
                assert result

        result = changelog.check_tag("nonexistent-tag", str(tmp_path))
        assert not result


class TestCompareFiles:
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        st.lists(version_entry_strategy, min_size=1, max_size=3),
        st.lists(version_entry_strategy, min_size=1, max_size=3),
    )
    def test_compare_files(self, tmp_path, source_entries, target_entries):
        source_file = tmp_path / "source.txt"
        target_file = tmp_path / "target.txt"

        changelog.dump(source_entries, str(source_file))
        changelog.dump(target_entries, str(target_file))

        result = changelog.compare_files(str(source_file), str(target_file))
        assert isinstance(result, bool)

        loaded_source = changelog.load(str(source_file))
        loaded_target = changelog.load(str(target_file))
        assert_json_roundtrip(loaded_source)
        assert_json_roundtrip(loaded_target)
