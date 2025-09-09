import pathlib

import pytest
from hypothesis import HealthCheck, given, settings

from changelogtxt_parser import _utils
from tests import strategies as sts

BASE_SETTINGS = settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
DEFAULT_FILE = "CHANGELOG.txt"


class TestResolvePath:
    @BASE_SETTINGS
    @given(filename=sts.random_string)
    def test_resolve_path_existing_file_returns_path_instance(self, filename, tmp_path):
        file = tmp_path / f"{filename}.txt"
        file.write_text("test content")

        result = _utils.resolve_path(file)

        assert isinstance(result, pathlib.Path)
        assert result.exists()
        assert str(result) == str(file.resolve())

    @BASE_SETTINGS
    @given(filename=sts.random_string)
    def test_resolve_path_with_touch_creates_file(self, filename, tmp_path):
        file = tmp_path / f"{filename}.txt"

        result = _utils.resolve_path(file, touch=True)

        assert isinstance(result, pathlib.Path)
        assert result.exists()
        assert file.exists()

    @BASE_SETTINGS
    @given(filename=sts.random_string)
    def test_resolve_path_nonexistent_raises_file_not_found_error(
        self,
        filename,
        tmp_path,
    ):
        file = tmp_path / f"{filename}.txt"

        with pytest.raises(FileNotFoundError, match="File not found:"):
            _utils.resolve_path(file)

    def test_resolve_path_directory_raises_is_a_directory_error(self, tmp_path):
        directory = tmp_path / "test_dir"
        directory.mkdir()

        with pytest.raises(
            IsADirectoryError,
            match="Expected a file but got a directory:",
        ):
            _utils.resolve_path(directory)

    def test_resolve_path_expanduser_works(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text("content")

        result = _utils.resolve_path(file)
        assert isinstance(result, pathlib.Path)


class TestFindFile:
    def test_find_file_when_path_is_file_returns_same_path(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text("test content")

        result = _utils.find_file(str(file))

        assert result == str(file)

    def test_find_file_finds_changelog_in_directory(self, tmp_path):
        changelog = tmp_path / DEFAULT_FILE
        changelog.write_text("changelog content")

        result = _utils.find_file(str(tmp_path))

        assert result == str(changelog)
        assert DEFAULT_FILE in result

    def test_find_file_no_changelog_raises_file_not_found_error(self, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with pytest.raises(
            FileNotFoundError,
            match=f"{DEFAULT_FILE} file not found in the specified path.",
        ):
            _utils.find_file(str(empty_dir))

    def test_find_file_nonexistent_path_raises_error(self):
        nonexistent_path = "/nonexistent/path/that/does/not/exist"

        with pytest.raises(
            FileNotFoundError,
            match=f"{DEFAULT_FILE} file not found in the specified path.",
        ):
            _utils.find_file(nonexistent_path)
