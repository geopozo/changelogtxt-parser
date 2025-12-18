# Changelogtxt-parser

<h1
  align="center"
>
	  <img
        height="250"
        width="250"
        alt="changelogtxt_small"
        src="https://raw.githubusercontent.com/geopozo/changelogtxt-parser/main/docs/media/logo.png">
</h1>

## Overview

Changelogtxt-parser is a python api, CLI, and github action for parsing and
verifying a changelog.txt like this:

```txt title="CHANGELOG.txt"
- An unreleased change

v0.2.0
- A change

v0.1.0
- A change
- Another change
```

## How to Install

```shell title="Console"
uv add changelogtxt-parser
# or
pip install changelogtxt-parser
```

## Python API

```python title="Python"
import changelogtxt

x = changelogtxt.load(filename)

# object example
changelogtxt.dump(object)
```

## CLI Examples

```shell title="Console"
# lint
changelogtxt check-format

# verify version exists
changelogtxt get-tag v1.0.1

# add new change or version
changelogtxt update -t "v1.0.2" -m "Change"

# compare two git ref files
changelogtxt summarize-news <origin> <target>
```

## Basic action

```yaml title="action.yml"
- name: Check changelog
  uses: geopozo/changelogtxt-parser@main
  with:
    # Python version to use (default: 3.12)
    python-version: ""

    # Path to the changelog file (default: searches ./CHANGELOG.txt)
    file-path: ""

    # Whether to validate the changelog format (default: "true")
    check-format: "true"

    # Tag to verify. Use "from-push" to get the tag from the latest push
    get-tag: "v1.0.0"

    # Compare changelog files from the current ref to <target_ref>
    # (branch, commit hash, or tag)
    # <file_path> is relative to the `working-directory`
    summarize-news: '["<file_path>", "<target_ref>"]'
```

## License

This project is licensed under the terms of the MIT license.
