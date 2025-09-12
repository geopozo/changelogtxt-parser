from hypothesis import strategies as st

# para strategies yo uso version_st
version_strings = st.builds(
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

random_string = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")),
    min_size=8,
    max_size=16,
)

list_of_strings = st.lists(random_string, min_size=2, max_size=10, unique=True)
# necesario unique?

list_of_version_entries = st.one_of(
    st.just([]),
    st.lists(
        st.builds( # me gusta build
            lambda version, change: {"version": version, "changes": [change]},
            version=version_strings,
            change=random_string, # por que no una lista???
        ),
        min_size=2,
        max_size=10,
        unique_by=lambda entry: str(entry["version"]),
    ),
)
