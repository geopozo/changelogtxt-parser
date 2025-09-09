from hypothesis import given, settings

from changelogtxt_parser import serdes
from tests import strategies as sts

BASE_SETTINGS = settings(max_examples=20)
CHANGELOG_CONTENT = "v1.0.1\n- Fixed bug\n\nv1.0.0\n- Initial release"


class TestRoundtrip:
    @BASE_SETTINGS
    @given(entries=sts.list_of_version_entries)
    def test_roundtrip(
        self,
        entries,
        tmp_path_factory,
    ):
        file = tmp_path_factory.mktemp("test") / "CHANGELOG.txt"
        file.write_text(CHANGELOG_CONTENT)
        entries.insert(0, {"version": "", "changes": []})

        serdes.dump(entries, file)
        loaded = serdes.load(file)

        assert loaded == entries
