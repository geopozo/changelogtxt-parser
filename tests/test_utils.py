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


class TestResolveFilePath:
    @BASE_SETTINGS
    @given(filename=sts.random_string)
    def test_resolve_file_path_existing_file_returns_path_instance(
        self,
        filename,
        tmp_path,
    ):
        file = tmp_path / f"{filename}.txt"
        file.write_text("test content")

        result = _utils.resolve_file_path(file)

        assert isinstance(result, pathlib.Path)
        assert result.exists()
        assert str(result) == str(file.resolve())

    @BASE_SETTINGS
    @given(filename=sts.random_string)
    def test_resolve_file_path_with_touch_creates_file(self, filename, tmp_path):
        file = tmp_path / f"{filename}.txt"

        result = _utils.resolve_file_path(file, touch=True)

        assert isinstance(result, pathlib.Path)
        assert result.exists()
        assert file.exists()

    @BASE_SETTINGS
    @given(filename=sts.random_string)
    def test_resolve_file_path_nonexistent_raises_file_not_found_error(
        self,
        filename,
        tmp_path,
    ):
        file = tmp_path / f"{filename}.txt"

        with pytest.raises(FileNotFoundError, match="File not found:"):
            _utils.resolve_file_path(file)

    def test_resolve_path_expanduser_works(self, tmp_path):
        file = tmp_path / DEFAULT_FILE
        file.write_text("content")

        result = _utils.resolve_file_path(file)
        assert isinstance(result, pathlib.Path)
