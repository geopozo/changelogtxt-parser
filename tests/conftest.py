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


@pytest.fixture(scope="session")
def random_string():
    return st.text(
        alphabet=st.characters(whitelist_categories=("Ll", "Lu", "And")),
        min_size=8,
        max_size=16,
    )


@pytest.fixture(scope="session")
def list_of_strings(random_string):
    return st.lists(random_string, min_size=2, max_size=10, unique=True)
