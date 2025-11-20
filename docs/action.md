# Setup action

```yaml
on:
  push:
    tags:
      - "*"
    branches:
      - "*"
  pull_request:
    branches:
      - main

name: Check Changelog
jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - name: Run composite action
        id: changelog
        uses: geopozo/changelogtxt-parser@main
        with:
          get-tag: "from-push"
          summarize-news: '["./CHANGELOG.txt", "main"]'
```
