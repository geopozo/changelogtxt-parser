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

DEFAULT_FILE = "CHANGELOG.txt"
BASE_SETTINGS = settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
ASSUME_LIST = ["v1.0.1", "v1.0.0", "1.0.1", "1.0.0"]


@pytest.fixture
def changelog_path(tmp_path):
    p = tmp_path / DEFAULT_FILE
    p.write_text(CHANGELOG_CONTENT)
    return p


class TestCheckTag:
    @BASE_SETTINGS
    @given(data=st.data())
    def test_check_tag_existing(
        self,
        data,
        changelog_path,
        version_strings,
        random_string,
    ):
        version = data.draw(version_strings)
        message = data.draw(random_string)
        app.update(version, message, changelog_path)
        assume(version not in ASSUME_LIST)
        result = app.check_tag(version, str(changelog_path))

        assert result is None

    @BASE_SETTINGS
    @given(data=st.data())
    def test_check_tag_non_existing(self, data, changelog_path, version_strings):
        tag = data.draw(version_strings)
        assume(tag not in ASSUME_LIST)

        with pytest.raises(
            ValueError,
            match=re.escape(f"Tag '{tag}' not found in changelog"),
        ):
            app.check_tag(tag, str(changelog_path))
