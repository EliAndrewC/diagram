# 292 sweep water G02 - handoff (session 1: write)

## Where the ditch leaves the brook: the intake and its weir (toshuko and seki)

- SECTION=water/where-the-ditch-leaves-the-brook-the-intake-and-its-weir-toshuko-and-seki
- RENDERING=rendering/water/how-our-maps-draw-the-intake-and-its-weir
- OLD=research/water/250-where-does-the-brook-stop-being-a-brook-and-become-the-ditch-at-an-intake-on-its-bank---and-the-brook-runs-on.html research/water/310-what-does-the-intake-mouth-look-like-and-what-decides-whether-a-weir-is-built.html research/water/253-is-there-a-weir-at-the-intake-some-hamlets-build-one-some-take-the-water-off-the-bare-bank.html research/water/256-where-on-the-brooks-bank-is-the-intake-and-how-far-is-it-to-the-fork.html research/water/300-what-was-a-village-weir-built-of-and-how-thick-was-it.html research/water/640-was-a-weir-of-stakes-and-woven-reed-only-a-modern-form-the-woven-stake-weir-is-ancient-its-reed-is-found-only-today.html
- MODALS=IrrigationDitch Weir
- BASE=484b7eb0c

No section was left out: none of the six is held IN PROGRESS by another feature today. Nothing was cut but framing
(250's question and its verdict on it, the pointer paragraphs, the six `Sources:` rosters, all keys cited). maff-toshuko-history-3
quoted the same passage as maff-toshuko-history and is now that one note. Every old-form absence note was converted;
253's (no period drawing of a village weir) is cited from the rendering section only. The glossary term "Seki" (the
post town) is now `cased`, because its lowercase variant would have wrapped the "seki" in the new title with the post
town's definition; lowercase "seki" is instead glossed in the text ("the weir (<em>seki</em>)"). The research section
is 19,868 bytes against the 20,000 cap: its header comments were kept short to fit, so one more bullet may force a
split. Two notes had kanji the prepass failed: the 1902 treatise's title now carries its reading and meaning, and the
"misprint" remark on suido-ishizue-iseki-3 went into an HTML comment (both in both notes files). The fixture
`classes_before_189.json` has no irrigation ditch or weir class, so it did not change. Code comments in
`hamletgen/consts.py` and `hamletgen/water/brook.py` now name the new titles, and the `fence` comment says brushwood
instead of reed, to match water 640.
