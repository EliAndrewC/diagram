# The GM's request (verbatim, 2026-09-20)

<!-- SOURCE: GM NOTES -->

Sent immediately after feature 258 landed, on reading the session's report that the shared glossary
asset "is read by every `record-format` run and cannot be scoped away".

> Why can the glossary asset not be scoped away? I mean, why could we not just do the same thing with the glossary that we are doing with other files and then split it into individual files within a directory? For example, each word in the glossary could be the name of the file in the glossary directory.

and, on the measured answer:

> Yes, please claim a number and proceed with doing that. implement the entire thing start to finish. Thanks.

<!-- /SOURCE -->

## What the GM was told before they said yes

The session had claimed, in feature 258's report, that the glossary "cannot be scoped away". The GM's
question found that claim too strong, and the measurement agreed with the GM:

| | bytes |
|---|---:|
| `research/assets/glossary.js`, what a check reads today | 144,524 |
| the 720 term NAMES alone | 5,808 |
| names + their variants | 20,981 |
| the definitions | 114,727 |

A check that only needs "is this word already defined?" needs 4% to 15% of what it reads today. The
session had conflated "it needs the whole term list" with "it needs the whole file"; those differ by
114,727 bytes.

The answer the GM approved, in the session's own words:

1. **The source splits; the derived asset stays whole.** `interactive/assets/glossary.json` is the
   hand-edited file; `research/assets/glossary.js` is derived from it and must stay a single file,
   because a page opened from `file://` cannot fetch a sibling. So: one file per word, assembled back
   into the one `.json` and the one `.js`, checked at the gate exactly as `make record` is.
2. **The lookup differs from a question's, and that is what makes it cheap.** For a question a check
   knows which entry it wants; for the glossary it is testing membership over an open set of candidate
   words - so the FILENAMES answer it, with no file contents read at all, and the directory is the
   index.
3. **Variants are the one thing filenames cannot carry.** "girders" must resolve to "girder", and the
   variants are 15,173 of the 20,981 bytes. That wants one small DERIVED index beside the directory.
4. The effect on the case feature 258 measured: a scoped `record-format` run would read about 7 KB of
   fragments plus about 21 KB of term index - **28 KB instead of 151 KB**, an 81% cut against the 58%
   it gets today - and when the check does want a definition it reads that one file, about 160 bytes.
5. The cost: 720 new files, an assembly step in `make glossary`, the guard extended to the glossary,
   and its tests - a smaller job than 258 because the format is already JSON with one object per term.
