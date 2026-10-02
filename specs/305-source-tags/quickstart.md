# Feature 305 - quickstart

- Add a source: `make reserve KIND=registry KEY=<key> URL=<url> TAGS="period=premodern; region=china; kind=primary"`,
  then write its citation line and write-ups; the limits paragraph says only what is specific to this source - its
  labels already carry the category's standard limits (read them in `research/source-tags.json`).
- Retag: edit the marker on the entry's last line; `make record CHECK=1` checks it.
- Regroup: edit `research/source-sections.json` only; rebuild with `make record`.
- Change a label's explanation: edit `research/source-tags.json`, then `make source-tags-contract`.
