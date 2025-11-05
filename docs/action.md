[Go back](../README.md)

# Setup action

```yaml
name: Check Changelog
  # puedes poner aca on: push toto eso
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
