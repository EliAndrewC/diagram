# Brief - feature 292 (how a research section is presented), the sweep: buildings group G05, session 1: write

You are a FRESH session for one part of feature 292. This brief is the whole of what you need; do not read the
feature's spec, plan or tasks. Work in this clone (`/diagram/.clones/diagram-reorg`); the research record's
`CLAUDE.md` applies to you (it auto-loads when you read a research file).

**What the feature is for.** The research record grew one section per question a session asked, so one subject is
spread over several sections, and its sections read as answers to questions no reader asked. The GM asked for it to
be reorganized into one section per TOPIC and rewritten under the style guide `research/STYLE.md`: a plain-English
topic title; a short opening that says what the thing was and why, with its headline numbers; then lead-line bullets
(a bold statement for a plain fact, a bold question for a range, an approximation or a guess), one finding each; no
`Sources:` roster; nothing addressed to a session outside an HTML comment; how OUR MAPS draw the thing in a separate
RENDERING section. Three pilot topics were written that way and the GM accepted them, the process and the checks on
2026-09-30. You are applying the same process to the topics below.

**The model to copy.** The third pilot is the closest model of a finished topic: the research section
`research/questions/0038-sunlight-and-shade-on-the-farm.html` (with its `.notes.html`) and its rendering section
`research/questions/0038-sunlight-and-shade-on-the-farm.drawing.html`. Read those two fragments
and the style guide before you write.

## Your items

- **The office hall and its clerks (goyakusho)** - fold `buildings/710-how-big-was-a-county-magistrates-office-hall.html`, `buildings/050-clerks-are-few-local-and-heimen.html`, `buildings/430-where-did-the-clerks-work---in-a-room-of-the-office-hall-or-a-building-of-their-own.html`
  - rendering section: How our maps draw the office hall and the clerks' rooms
  - modals whose `Entry:` names a folded section: ClerksRoom
  - note: 050 rests partly on the setting's caste notes (scribes are heimen) - canon, no citation; the hearing room inside the hall is T7.

## The procedure (session 1: write)

1. **Claims first:** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md KEY="buildings"` (in `.claude/skills/diagram`);
   a section another feature holds IN PROGRESS today is not edited - leave it out of your fold, and say so in the
   handoff. Then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram reorg (diagram-reorg) | 292 | sweep buildings G05 in progress (0113 buildings/050 buildings/430) | 2026-09-30"`.
2. **Read, all in one message:** `research/STYLE.md`; the two model fragments named above; every fragment your
   topics fold and its `.notes.html` (not its `.originals.html` - the originals are stored apart and `make record`
   puts them back; you copy their lines, below, without needing to read them). Note the commit you start from
   (`git -C /diagram/.clones/diagram-reorg rev-parse --short HEAD`) - the handoff names it as BASE.
3. **Write each topic** as a research fragment and, where the folded sections say anything about how our maps draw
   the thing, a rendering fragment:
   - **The research fragment** is `research/questions/<NNNN>-<id>.html`, `<NNN>` the lead folded section's prefix and
     `<id>` the title's anchor (lowercase; letters, digits and spaces kept; spaces to hyphens: "Threshing and drying
     yards at farmhouses (niwa)" is `threshing-and-drying-yards-at-farmhouses-niwa`). It opens with
     `<h2 id="<id>"><title></h2>`, then the comments: `<!-- feature 292 sweep, 2026-09-30: folded from <the old ids> -->`,
     the folded sections' `Grounds:` and `Evidence:` fields merged into one of each, and a `REMOVED` comment for any
     claim you cut under STYLE.md section 4 (what it said and why it went). Then the opening paragraphs, then the
     bullets, as the model does.
   - **The rendering fragment** is `research/questions/<NNNN>-<id>.drawing.html`, titled to mirror the research title
     ("How our maps draw ..."), its second line `<!-- about: buildings.html#<id> -->` - `make record` then links the two
     both ways; never type a link between them. It follows the style guide too, and cites the research it rests on.
     The map's rules, the sizes chosen, conventions, knobs, what the generator places where, and why, go here, and
     nowhere in the research section. A topic with nothing about the map has no rendering fragment.
   - **The notes.** Each new fragment has its `.notes.html` beside it: every note its prose cites, COPIED from the old
     notes character for character (never retyped, never retranslated, never quoted from memory). Keys are unique
     within the page (the research page and the rendering page are two pages): a repeat of one work is `key`,
     `key-2`, ...; a passage quoted in two old sections is one note. An absence note the old sections wrote in the old
     form (its search in visible parentheses) is converted: `no publicly readable source<!-- searched YYYY-MM-DD: what
     was tried -->` then, visibly, what the search found (the comment MUST begin `<!-- searched YYYY-MM-DD:` with one
     date). A note may be cited from both fragments only by being copied into both notes files.
   - **The originals.** For each note you keep, copy its lines from the old `.originals.html` into the new one beside
     your notes: `grep 'data-orig="<old key>#' <old>.originals.html`. If you renamed a note's key, rename its
     `data-orig="<key>#n"` to match, and the placeholder `<span class="orig" data-orig="<key>#n"></span>` in the note.
   - **Never lose a citation or a finding.** Every note key and every quoted passage of the folded sections is cited
     in the new research or rendering fragment, or its claim is cut under a rule of STYLE.md section 4 with a REMOVED
     comment. Every GUESS stays labeled where its claim stands. A decision is the project's choice, never "the GM
     ruled": the ruling, its date and words go in an HTML comment beside the sentence.
   - **Delete the folded fragments** with their `.notes.html` and `.originals.html`: `git -C /diagram/.clones/diagram-reorg rm <paths>`.
   - **Re-aim every link to an old anchor.** For each old id, grep the record's fragments
     (`grep -rl '<old id>' .claude/skills/diagram/research --include='*.html' | grep -v citations/`), the modal
     classes (`.claude/skills/diagram/l7r/diagram/interactive/classes/`, `.../compound_kinds/`), the code comments
     under `.claude/skills/diagram/l7r/` and `.claude/skills/diagram/tests/fixtures/classes_before_189.json`. A link
     goes to the new research section, or to the rendering section where it pointed at a map rule (from another page:
     `rendering/buildings.html#<rid>`; from a rendering page: `../buildings.html#<id>`). A modal's `Entry:` names the new
     titles - the research title under `research/contents.json#compounds - '<title>'` and the rendering title under
     `research/contents.json#compounds - '<title>'` - and the fixture's `"entry"` for that class is changed to the same
     string. A code comment that named an old heading names the new one.
   - **Confusable pairs** you meet (two things a reader could mistake for each other): `make append
     FILE=/diagram/.clones/diagram-reorg/specs/292-research-presentation-style/confusables.md LINE="- <title> / <title>: <the difference>"`.
4. **Build and test**, in `.claude/skills/diagram`: `make glossary` if you added or changed a glossary term (a new
   one takes its prefix from `make reserve KIND=glossary KEY=<term>`; never a common English word as a variant);
   `make record && make citations`; then for each research and rendering section `make style-prepass Q=<NNNN>` (the rendering one with `IN=compounds`) and fix everything in its FAIL lists (a metric figure
   with no feet, "GM" in the visible text, a paragraph over 150 words, an absence note in the old form, kanji without
   its `(romaji, "meaning")` gloss); then `make test-file FILE=tests/interactive` and
   `python3 scripts/check-question-size.py` from the clone root. Fix what fails and re-run once.
5. **Hand off.** Write `specs/292-research-presentation-style/sweep/buildings-G05-handoff.md`, per topic:
   `- SECTION=buildings/<id>`, `- RENDERING=rendering/buildings/<rid>` (or `- RENDERING=none`), `- OLD=<the folded
   fragments' paths, space-separated, relative to .claude/skills/diagram>`, `- MODALS=<the classes whose Entry you
   changed, space-separated>`; one line `- BASE=<the commit you started from>`; then a sentence per topic on anything
   left open (a section you left out because another feature holds it, a claim you cut, a link you could not
   resolve). Commit only the files you changed (`git -C` with paths), message beginning `292 sweep buildings G05:`.
   Do NOT run the record checks and do NOT push. Your last message is one paragraph saying what you wrote.
