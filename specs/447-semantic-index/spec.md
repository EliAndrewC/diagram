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
every term required) misses, cheaply enough to keep? And which model: a small, fast multilingual one, or a larger one stronger
across languages? Asked now because the field's size cap (feature 444 FR-018) needs a research pass, and the GM is interested in
the experiment's result for its own sake.

## What is built for it

- The record's pages and the archive's texts cut into passages of a few hundred words, each with its file and place.
- Each passage embedded by a local, open, multilingual model, keyed by a fingerprint of its text: an update embeds only the new
  or changed passages; a change of model rebuilds whole.
- The vectors in a plain file, searched by brute force (the corpus is tens of thousands of passages); a `make` target that takes a
  question and returns the nearest passages with their file and place, beside `make archive-find`, never in its place.
- Nothing leaves the machine: the model runs locally, and the archive's text is never sent to a service (the archive is private,
  CLAUDE.md, "Research").
- Its tooling held to the project's rules: 100% coverage, a test companion, a make target, house style.

## The measurement

1. First, the consensus among practitioners on choosing a multilingual retrieval model for Japanese, Chinese and English text of
   this size - the small and the large candidates, and what thresholds call for the larger (the GM's first task) - from published
   comparisons and benchmarks, recorded with their sources.
2. The cost: the time to build the index over the whole corpus with each model on this machine, and the time an update and a
   search take.
3. The comparison: a handful of past research questions whose answers the record already holds (the passages that answered them
   known), each asked through the index - with each model - and through today's text search; for each, which of the known
   passages each finds in its first results, and what it finds that the other does not.

## The rule

- The index is kept, with the model that finds more of the known passages, where it finds passages today's search missed on at
  least a fair share of the questions at a cost that keeps an update to seconds and a search under a second; the smaller model
  wins a tie. Otherwise the trial is set down, its evidence recorded, the tooling not kept.
- Either way the result is reported to the GM, who asked for the experiment's result.

## The evidence

[Filled as measured: `research/semantic-index-<step>.md` per measurement, each dated with its command and its output beside the
figure.]

## The time

As feature 437 reported it: `make feature-report F=447`.

## Review history
