import pytest
from hypothesis import strategies as st


@pytest.fixture(scope="session")
def version_strings():
    return st.builds(
        lambda major, minor, patch, post, dev: f"v{major}.{minor}.{patch}{post}{dev}",
        major=st.integers(min_value=0, max_value=99),
        minor=st.integers(min_value=0, max_value=99),
        patch=st.integers(min_value=0, max_value=99),
        post=st.one_of(
            st.just(""),
            st.integers(min_value=0).map(lambda n: f".post{n}"),
        ),
        dev=st.one_of(
            st.just(""),
            st.integers(min_value=0).map(lambda n: f".dev{n}"),
        ),
    )
