from changelogtxt_parser import serdes
from changelogtxt_parser import version as version_tools

CHANGELOG_DATA: list[version_tools.VersionEntry] = [
    {"version": "unreleased", "changes": ["New change"]},
    {"version": "v1.0.0", "changes": ["First version"]},
]


class TestRoundtrip:
    def test_roundtrip(self, tmp_path):
        file_path = tmp_path / "changelog.txt"
        serdes.dump(CHANGELOG_DATA, file_path)
        loaded = serdes.load(file_path)

        assert loaded == CHANGELOG_DATA
