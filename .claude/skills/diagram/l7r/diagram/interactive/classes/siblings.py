"""The sibling PAIR texts - how each class differs from the one a reader is likeliest to confuse it with.

Kept as string constants rather than docstrings on purpose (spec 189 FR-004 / D4): since 2026-08-28 the
page renders sibling LINKS, not these texts, so they are a record and not documentation visible in the
user interface. Installed in both directions by `_base.install_siblings`.

THE TEXTS ARE DATA - `assets/siblings.json` (feature 207): a `texts` object of shared passages and a `pairs`
list of `[class a, class b, text]`, where a text beginning `@` names a shared passage, so the one text
written for four crop-dike pairs stays ONE text. Editing a text owes `make page-check`, not the gate.

The record behind the two shared passages (JSON carries no comments, so it is kept here):

- `crop-vs-perimeter`: One text for all four rolled crop-dike values - the distinction from the perimeter dike is identical whichever crop the knob rolled, and four copies is four chances for a later edit to fix one and leave three (settlement-review, 2026-08-29). The walk figures are measured on Kuwabata: the crop dike loops run a median 815 ft (3.1 min at 260 ft/min), the perimeter dike 4,591 ft along its CREST (18 min) - the walkable top of the bank, which is the thing you would walk. The first version of this line said half an hour, on the manifest's `outline`: that is the band POLYGON, outer face plus inner face returned, 1.99x the crest, so it counted the same walk twice (settlement-review round 2).
- `pond-vs-polder-sluice`: The near-homonym the GM's own list did not name, and the pair a reader is likeliest to confuse on a dike-pond map: both are "sluice", both are boards in a cut (settlement-review, 2026-08-29).
"""

from __future__ import annotations

from ..content import content

_RAW = content("siblings.json")
_TEXTS: dict[str, str] = _RAW["texts"]
_PAIRS: dict[tuple[str, str], str] = {(a, b): (_TEXTS[text[1:]] if text.startswith("@") else text) for a, b, text in _RAW["pairs"]}
