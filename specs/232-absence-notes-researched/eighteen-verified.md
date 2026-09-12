# The eighteen, verified against the files (2026-09-12)

*`spec-fidelity` round 5 on feature 235 found that four of the triage's eighteen class-A rows described
sentences those footnotes do not annotate. I then read all eighteen markers in the record. The triage was
wrong on most of them, and this file is the corrected classification. The method that produced the error is
recorded at the end, because it is the same error the record itself kept making.*

## What each footnote actually hangs on

**GENUINELY no citation owed - 5.** Each says, in its own words, that the figure is this project's
calibration or that no source was found, and none asserts a fact about the world beyond that.

| note | the sentence it annotates | reason |
|---|---|---|
| `cities/sizing.html` fn-2 | "that band is a calibration against the cities this project has drawn rather than a historical share, because no readable source gives a percentage of a walled city's interior for its civic buildings" | measured on our own maps |
| `religion-and-death.html` fn-49 | "No source gives a village shrine a footprint: the whole band is this project's own calibration on the drawn maps." | measured on our own maps |
| `religion-and-death.html` fn-57 | "How wide that collar ran is in no source read: the figure below is this project's own." | measured on our own maps |
| `religion-and-death.html` fn-75 | "A pauper bone mound is drawn at 10 to 30 ft across with nothing behind the band" | measured on our own maps |
| `religion-and-death.html` fn-78 | "is not remembered for a mound; no page read describes one raised there" | the record's own silence |

**BORDERLINE - 1.** `fields.html` fn-85 - "the bund is what holds the water in and the ditch is what takes
it away, so a bund drawn across the collector is a basin with its wall standing in the drain". The
conclusion really is a necessity of what the two things are, but the sentence labels itself general reading.
It is the one case where `follows from the definitions` is arguable, and it should be argued at the point of
change rather than assumed here.

**GENUINE OPEN ABSENCES - 12.** Every one of these asserts something about how a place was built, worked or
used, and every one carries "this rests on general reading; no source is cited" or its equivalent. Under
FR-003 none of them may be a grounds note. They are research, and they belong in the backlog.

`archetypes.html` fn-93 (a bund junction is the most worked point in a field - four basins push water at it,
it carries the crossing traffic, it is where someone stands to work the water, it slumps first);
`cities/defenses.html` fn-18 (a fortified city keeps a clear lap inside its rampart so troops can be moved);
`cities/fabric.html` fn-18 (a wall footed in water is undermined, and a quay is working ground);
`cities/fabric.html` fn-22 (the ruling class did not record the lodging of the poor, and the surviving
gazetteers foreground the post-stations); `cities/fabric.html` fn-24 (family hatago that were not distinct
buildings - shophouses whose back rooms took lodgers); `cities/fabric.html` fn-29 (an open road-town's field
gaps are natural breaks, so a tower does not earn its cost); `cities/hinterland.html` fn-10 (a field's fan
has a hand, and both hands were real); `cities/river-cities.html` fn-17 (a river moat was kept full by the
river's own stage rather than flushed through); `religion-and-death.html` fn-50 (a shrine's precinct was a
swept raked-gravel or flagged surface); `religion-and-death.html` fn-54 (the path and the ground under each
arch were swept the whole length); `towns.html` fn-23 (that a road-town's field gaps do the work of a fire
break); `water.html` fn-2 (a field ditch is about 1/300 of the paddy it feeds - and its own input figure is
footnoted to an absence note).

## The count, corrected

| | triage said | the files say |
|---|---|---|
| no citation owed | 18 | **5**, with 1 arguable |
| genuine open absences among those 18 | 0 | **12** |

## How the error happened, and why it is the feature's own subject

The triage was written from `notes-worklist.md`, whose per-note "claim" field was extracted by taking the
sentence nearest the footnote marker in the paragraph. That heuristic lands on the wrong sentence whenever a
paragraph's marker sits mid-way, which is common. I then classified from those extracts **without opening
the pages**, and wrote a spec on top of the classification.

This is the same failure the whole of feature 232 exists to correct: **a rule written from a DESCRIPTION of
the record rather than from the record.** Feature 235's D4 already records one instance of it, caught at
round 3 and covering two rows. Round 5 found two more, and reading all eighteen found thirteen. The lesson
is not "check your work" but something narrower and more useful: **an extraction heuristic over HTML is
evidence about the heuristic, and a classification built on one is worth nothing until the pages are read.**
