import semver
from packaging import version


def parse_version(content: str) -> semver.Version | version.Version | None:
    content = content.removeprefix("v")
    v = None
    try:
        v = version.Version(content)
    except version.InvalidVersion:
        pass
    try:
        v = semver.Version.parse(content)
    except ValueError:
        pass
    if not v:
        return None
    return v
