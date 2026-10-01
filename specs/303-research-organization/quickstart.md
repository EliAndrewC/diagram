# Quickstart - feature 303

- Read a question: `research/questions/NNNN-<slug>.html` (a glob on the slug finds it); its drawing page beside it.
- Add a question: `make reserve KIND=question KEY=<heading id>` -> write the stem's files -> the `tags` marker ->
  `make record` (a refusal names what is missing).
- Regroup: edit `research/contents.json` (order, nesting, `takes`); `make record`. No question file changes.
- Check one question: `make check-bundle Q=NNNN`; whole section: `make record-prepass IN=<section id>`.
