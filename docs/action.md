[Go back](../README.md)

# Setup action

```yaml
name: Check Changelog

jobs:
  changelog:
    runs-on: ubuntu-latest
    steps:
      - name: Run composite action
        id: changelog
        uses: geopozo/changelogtxt-parser@main
        with:
          check-tag: "from-push"
          summarize-news: '["./CHANGELOG.txt", "main"]'
```
