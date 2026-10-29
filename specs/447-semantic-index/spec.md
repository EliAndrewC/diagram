# Trial: does a local semantic index find what the archive's text search misses?

**Form**: trial

**Created**: 2026-10-29

**Status**: Running

**Affects**: tooling

**Approved**: the GM, 2026-10-29, "Either way, go ahead and file the feature"

**Input**: `request.md` (the GM's words, verbatim).

## The question

Would a semantic index over the research record (`research/questions/`) and the private source archive's texts find the passages
a research question needs - the same idea in other words, or in another language - that today's text search (`make archive-find`,
every term required) misses, cheaply enough to keep? The model is fixed: the larger multilingual one, BGE-M3, stronger at matching an English question to
a Japanese or Chinese passage (the GM 2026-10-29: "let's just go ahead and lock in the larger one"); no smaller model is
measured. Asked now because the field's size cap (feature 444 FR-018) needs a research pass, and the GM is interested in
the experiment's result for its own sake.

## What is built for it

- The record's pages and the archive's texts cut into passages of a few hundred words, each with its file and place.
- Each passage embedded by BGE-M3, run locally, keyed by a fingerprint of its text: an update embeds only the new or changed
  passages; a change of model rebuilds whole.
- The vectors in a plain file, searched by brute force (the corpus is tens of thousands of passages); a `make` target that takes a
  question and returns the nearest passages with their file and place, beside `make archive-find`, never in its place.
- The index is stored in the private research archive's repository (`EliAndrewC/diagram-research`, checked out at
  `.specify/source-archive/`), beside the texts it indexes, as binary shards: the vectors at reduced precision, each shard holding
  the passages of a group of source files and kept under GitHub's file-size limits, so an update commits only the shards whose
  passages changed; pushed with the archive, so it survives the container, and rebuildable from the texts if ever lost.
- Nothing leaves the machine: the model runs locally, and the archive's text is never sent to a service (the archive is private,
  CLAUDE.md, "Research").
- Its tooling held to the project's rules: 100% coverage, a test companion, a make target, house style.

## Resuming

The build is long (about 120,700 passages; 110-160 a minute measured on 2026-10-29, so 12-18 hours) and is safe to interrupt:

- Each shard is written to the archive's working copy (`.specify/source-archive/semantic-index/bge-m3-int8/<shard>.npz`, on
  the host's disk) as soon as it is done; a rerun of `make semantic-index` skips every shard whose passages are unchanged, so an
  interruption loses only the shard in progress. The commit and push to the archive's repository come at the end of a build.
- The model is BGE-M3's 8-bit build (`Xenova/bge-m3`, `onnx/model_int8.onnx`), cached in `.specify/model-cache/`; the
  docstring of `scripts/record/semantic_index.py` says why not the full one.
- To resume: `make semantic-index` (it picks up where it stopped). Then run the comparison, `trial.py` beside this spec - its 17
  questions (ten English, seven answered by Japanese sources), each with the archive capture known to answer it - as
  `python3 specs/447-semantic-index/trial.py <out.json>`, and record it under "The evidence".

## The measurement

1. The cost: the time to build the index over the whole corpus on this machine, its size on disk, and the time an update and a
   search take.
2. The comparison: a handful of past research questions whose answers the record already holds (the passages that answered them
   known), each asked through the index and through today's text search; for each, which of the known passages each finds in its
   first results, and what it finds that the other does not.

## The rule

- The index is kept where it finds passages today's search missed on at least a fair share of the questions, at a cost that keeps
  an update to seconds and a search under a second. Otherwise the trial is set down, its evidence recorded, the tooling not kept.
- Either way the result is reported to the GM, who asked for the experiment's result.

## The evidence

[Filled as measured: `research/semantic-index-<step>.md` per measurement, each dated with its command and its output beside the
figure.]

## The time

As feature 437 reported it: `make feature-report F=447`.

## Review history
