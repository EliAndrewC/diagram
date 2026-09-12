#!/usr/bin/env bash
# house-style-hooks.sh - the two house-style rules that a regex can actually decide.
#
# CLAUDE.md states both project-wide, for EVERYTHING: generated content, prose, docs, specs, skill
# files, tests, comments, and code identifiers.
#
#   1. Hyphens only - no em-dash (U+2014) or en-dash (U+2013), anywhere.
#   2. American spellings, never British ones. The word list is CLAUDE.md's own.
#
# WHY THESE TWO AND NOT THE REST OF THE STYLE GUIDE. They are decidable without judgment. The rules
# next to them are NOT, and enforcing those would be a mistake: "people" has a caste meaning but is
# correct in narrative and vow voice; office-holders are they/them generically but named characters
# keep their pronouns. A hook cannot see voice, and one that fires on correct prose teaches a session
# to bypass every hook - which this project has already paid for.
#
# THE VIOLATIONS ARE REAL, not hypothetical (audit 2026-08-24): `licence` shipped in
# specs/123-lane-web-and-cluster-shape/tasks.md and `centre` in specs/125-lanes-do-not-break/spec.md,
# both against a rule documented project-wide since long before either.
#
# THREE EXEMPTIONS, and all three are load-bearing:
#
#   - THE GM'S OWN WRITING. Never "correct" text inside a <!-- SOURCE: GM NOTES --> block, or in
#     l7r.md, or a direct quotation of either. Their prose is theirs.
#   - A FILE THAT STATES THE RULE quotes the forbidden words by necessity - CLAUDE.md lists every
#     British spelling it forbids. Flagging those would make the rule unwritable.
#   - A QUOTATION OF SOMEONE ELSE'S TEXT (GUARD_EDIT_OK: GM 2026-09-06: *"The house style should not
#     normalize british spellings or em-dashes inside things we are quoting, because that requires us
#     to edit other people's quotes, which I don't think we should do"*). A passage inside 「」, 『』,
#     “” or <q>/<blockquote> anywhere, or inside straight double quotes in a PROSE file (.md/.html/.txt
#     - in code a double-quoted string is a string, and the rule covers code), keeps the source's own
#     characters. Found by feature 194's backfill: the readers' reports recorded a dozen en-dashes and
#     four British spellings hyphenated and Americanized INSIDE verbatim quotes as they were saved.
set -uo pipefail

MODE="${1:-pretool}"
[ "$MODE" = pretool ] || exit 0
INPUT=$(cat)

# GUARD_EDIT_OK: feature 236 - the scan itself now needs this directory (it shares `_hm_escape`'s
# search-segment rule rather than writing a second copy of it), so the path is resolved BEFORE the
# scan instead of only before the log.
HS_HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export HS_HERE

REPORT=$(printf '%s' "$INPUT" | python3 -c '
import json, os, re, sys   # GUARD_EDIT_OK: feature 236 - the scan reads Bash payloads too, and shares
sys.path.insert(0, os.environ.get("HS_HERE", ""))   # `_hm_escape`s search-segment rule rather than copying it
try:
    from _hm_escape import drop_search_segments
except Exception:                      # a guard never takes the session down with it
    drop_search_segments = lambda s: s
try:
    d = json.load(sys.stdin)
except Exception:
    print(""); raise SystemExit
inp = d.get("tool_input", {}) or {}
path = inp.get("file_path", "") or ""
body = (inp.get("new_string") or "") + (inp.get("content") or "")
is_bash = d.get("tool_name") == "Bash"

# A BASH HEREDOC IS A WRITE TOO. This hook matched only the Edit/Write tools at first, so
# `python3 - <<PY ... write_text(prose) ... PY` walked straight past it - and the author did exactly
# that, minutes after shipping the guard, to write a spec. Same hole layer 3 had, same fix: look at
# what the command actually writes. Only heredoc BODIES are inspected, because that is where prose
# travels; a redirect of a single echo is not worth the false positives.
# GUARD_EDIT_OK: feature 236 (the GM item 4) - THE WHOLE BASH PAYLOAD, NOT ONLY ITS HEREDOC BODIES.
# The heredoc rule above was already the second version of this hole; the third was measured on the
# session that motivated feature 236, where British spellings reached the tree through Bash payloads
# this hook never looked at (`research.md` R3). A command WRITES in more ways than a heredoc - an
# `echo >>`, a `python3 -c` that calls write_text, a `sed -i` replacement - and the cheap, honest rule
# is to read the payload. What that costs is a WARNING rather than a correction (spec D2): a Bash
# payload is often itself the spelling fix (`sed -i \x27s/centre/center/g\x27`), and correcting it
# would turn the fix into a no-op. The `make quick` phase is the half that fails.
if is_bash:
    cmd = inp.get("command", "") or ""
    # what a command LOOKS FOR is not what it writes: `git grep -n "centre"` is correct work
    body = drop_search_segments(cmd)
    # the target matters as much as the text: a heredoc writing the GM own words is exempt below,
    # so pick up any path the command mentions
    path = path or " ".join(re.findall(r"[\w./-]+\.(?:md|py|sh|toml|json)", cmd))
if not body:
    print(""); raise SystemExit
# the GM own writing, and the files that must quote the rule
# gm-request.md is a verbatim transcript of the GM speaking - correcting it would defeat its purpose
if "/host-l7r-repo" in path or path.endswith("l7r.md") or "gm-request.md" in path:
    print(""); raise SystemExit
# A FILE OUTSIDE THE PROJECT IS NOT PROJECT CONTENT (2026-09-06): the rule is project-wide, and a session
# scratchpad under /tmp is not the project. Measured the day the quotation exemption landed: three of five
# reader agents writing verbatim page text into /tmp/.../result.json each had their dashes and spellings
# rewritten, each noticed only by diffing, and each worked around the guard with chr() escapes - a guard that
# fires on correct work is one that gets worked around (CLAUDE.md, "deliberately NOT enforced").
if path.startswith("/tmp/"):
    print(""); raise SystemExit
# GUARD_EDIT_OK: feature 236 - A FIXTURE IS A VERBATIM RECORD. `scripts/fixtures/` holds corpora of
# commands that really ran (the guard-refusal replays, and 236 own 238-command parse corpus); several
# of those commands were house-style sweeps and carry the words by necessity. Correcting one would
# falsify the record and break the measurement it reproduces - the same ground as a quotation.
if "/scripts/fixtures/" in "/" + path:
    print(""); raise SystemExit
# GUARD_EDIT_OK: feature 236 - two more files that must QUOTE the words to state the rule: the delta
# check that reads the BRIT table out of this hook, and its suite. The hook corrected both as they
# were typed, which is the same false positive the three names before them were added for. (No
# apostrophe in this comment: the scan below is a single-quoted program, and one apostrophe ends it -
# GUARD_EDIT_OK: the same trap feature 217 hit in guard-file-hooks, met again here.)
if re.search(r"(^|/)(CLAUDE\.md|constitution\.md|l7r-style\.md|house-style-hooks\.sh|test-house-style-hooks\.sh|test_hooks_cases\.py|check-house-style-delta\.py|test_house_style_delta\.py|test_guard_firing_log\.py)$", path):  # GUARD_EDIT_OK: feature 236 - the census drives the guard with a REAL payload, which must carry a real British spelling or it proves nothing
    print(""); raise SystemExit
# a SOURCE block inside the added text is the GM speaking; drop it before looking
body = re.sub(r"<!--\s*SOURCE: GM NOTES.*?<!--\s*END SOURCE\s*-->", " ", body, flags=re.S | re.I)

# GUARD_EDIT_OK: feature 164 - CORRECT THE TEXT INSTEAD OF REFUSING THE EDIT (GM 2026-08-30: *"a tool
# could do a rewrite or return additional context or whatever"*). Both of the two rules here are exact
# substitutions with no judgment in them, and a session refused for one of them just retypes the same
# edit with the fix - measured: 3 firings, 3 identical re-edits. So the fix is applied and the session
# is told. Three things the correction must never do, each one load-bearing:
#
#   - CORRECT THE GM OWN WORDS. The path exemptions above cover l7r.md and gm-request.md but NOT
#     `specs/NNN-*/request.md`, which is where this repository records the GM verbatim requests -
#     the authority for every spec. Silently rewriting those would breach Principle V, so a file
#     recording the GM speaking stays on the REFUSAL path, where a person decides.
#   - CORRECT A WORD THAT IS BEING NAMED RATHER THAN USED. A backtick span is how the project own
#     prose marks a token it is discussing, and this guard refused feature 164 own plan for NAMING
#     a British spelling in a sentence about how it is handled. Spans are held out of both the
#     detection and the correction.
#   - GUESS. Every pair below is CLAUDE.md own, one American form per word.
CODE = r"\x60{3}.*?\x60{3}|\x60[^\x60]*\x60"  # a code span, written by codepoint: a literal backtick inside $( ) is command substitution
# A QUOTATION IS SOMEONE ELSE TEXT (GM 2026-09-06, header bullet three): corner brackets, curly quotes and
# the two HTML quotation elements anywhere; straight double quotes only in a prose file, where they quote -
# in a .py or .sh they delimit a string, and the rule reaches code. The heredoc path list is joined by spaces.
QUOTE = r"「[^」]*」|『[^』]*』|“[^”]*”|<q\b[^>]*>.*?</q>|<blockquote\b[^>]*>.*?</blockquote>"
# GUARD_EDIT_OK: feature 236 FR-007a - "outside a quoted span" is the HOUSE-STYLE sense, never the
# SHELL one. In a Bash payload a straight double quote is shell quoting, and under a `<<\x27PY\x27`
# heredoc the whole payload is shell-quoted, so admitting that form here would let the exemption
# swallow the rule the payload is being read for.
if not is_bash and re.search(r"\.(?:md|html|txt)(\s|$)", path):
    QUOTE += r"|\x22[^\x22\n]*\x22"
SPAN = re.compile(CODE + "|" + QUOTE, re.S)
PAIRS = {
    "colour": "color", "colours": "colors", "centre": "center", "centres": "centers",
    "centred": "centered", "behaviour": "behavior", "behaviours": "behaviors",
    "neighbour": "neighbor", "neighbours": "neighbors", "neighbourhood": "neighborhood",
    "analyse": "analyze", "analysed": "analyzed", "organise": "organize", "organised": "organized",
    "recognise": "recognize", "recognised": "recognized", "defence": "defense",
    "licence": "license", "practise": "practice", "sceptic": "skeptic", "storey": "story",
    "whilst": "while", "travelled": "traveled", "modelled": "modeled", "programme": "program",
    "metre": "meter", "litre": "liter", "mould": "mold", "plough": "plow", "kerb": "curb",
    "draught": "draft", "ageing": "aging", "marvellous": "marvelous", "jewellery": "jewelry",
    "skilful": "skillful", "artefact": "artifact", "demesne": "domain", "labelled": "labeled",
    "labelling": "labeling", "judgement": "judgment", "catalogue": "catalog", "honour": "honor",
    "honours": "honors", "grey": "gray",
}


def _match_case(src, dst):
    if src.isupper():
        return dst.upper()
    if src[:1].isupper():
        return dst[:1].upper() + dst[1:]
    return dst


def correct(text):
    """The corrected text and what was corrected, leaving backtick spans exactly as they are."""
    out, notes, last = [], [], 0
    for m in SPAN.finditer(text):
        piece, fixed_notes = _correct_plain(text[last:m.start()])
        out.append(piece); notes += fixed_notes
        out.append(m.group(0))               # a span is a MENTION: never touched
        last = m.end()
    piece, fixed_notes = _correct_plain(text[last:])
    out.append(piece); notes += fixed_notes
    return "".join(out), notes


def _correct_plain(text):
    notes = []
    for dash, name in (("—", "em-dash"), ("–", "en-dash")):
        if dash in text:
            text = re.sub(r"\s*%s\s*" % dash, " - ", text)
            notes.append(name + " -> hyphen")
    for brit, amer in PAIRS.items():
        pat = re.compile(r"\b%s\b" % brit, re.I)
        if pat.search(text):
            text = pat.sub(lambda m: _match_case(m.group(0), amer), text)
            notes.append(brit + " -> " + amer)
    return text, notes


# what a session can actually see, with the spans held out
visible = SPAN.sub(" ", body)
hits = []
if "—" in visible: hits.append("em-dash (U+2014)")
if "–" in visible: hits.append("en-dash (U+2013)")
BRIT = ("colour","colours","centre","centres","centred","behaviour","behaviours","neighbour",
        "neighbours","neighbourhood","analyse","analysed","organise","organised","recognise",
        "recognised","defence","licence","practise","sceptic","storey","whilst","travelled",
        "modelled","programme","metre","litre","mould","plough","kerb","draught","ageing",
        "marvellous","jewellery","skilful","artefact","demesne","labelled","labelling","judgement",
        "catalogue","honour","honours","grey")
for w in BRIT:
    if re.search(rf"\b{w}\b", visible, re.I):
        hits.append(w)
if not hits:
    print(""); raise SystemExit

# THE GM SPEAKING IS NEVER CORRECTED - only refused, so a person decides (Principle V).
GM_VERBATIM = re.search(r"specs/[^/]+/request\.md$", path) or path.endswith("gm-request.md")

# CAN THE WHOLE EDIT BE FIXED MECHANICALLY? Only then is it corrected; a violation the table cannot
# reach keeps the refusal, because a partial correction would hide what is left.
fixed_fields, notes = {}, []
for field in ("new_string", "content"):
    if field in inp and isinstance(inp[field], str):
        got, got_notes = correct(inp[field])
        fixed_fields[field] = got
        notes += got_notes
leftover = SPAN.sub(" ", "".join(fixed_fields.values()))
still_bad = "—" in leftover or "–" in leftover or any(
    re.search(rf"\b{w}\b", leftover, re.I) for w in BRIT
)

# GUARD_EDIT_OK: feature 236 FR-007 - A BASH PAYLOAD IS TOLD, NEVER REWRITTEN OR REFUSED. Telling
# costs nothing (an additionalContext at exit 0 spends no model round trip), rewriting would break
# the payload that is itself a spelling fix, and refusing would spend a round trip on something the
# `make quick` phase fails on anyway. Spec D2 records the departure from item 4s "correct it" for
# the GM to rule on.
if is_bash:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            "House style, in this command payload: " + ", ".join(hits[:6]) + ". CLAUDE.md is "
            "project-wide - American spellings, hyphens only - and a write that travels through a "
            "Bash payload owes the rule exactly as an Edit does. Not corrected for you, because a "
            "payload is often itself the fix; a quotation of someone elses text keeps its own "
            "characters. `make quick` fails on a British spelling in the delta, so it is cheaper "
            "to fix now than at the gate."),
    }}))
    raise SystemExit

if fixed_fields and notes and not still_bad and not GM_VERBATIM:
    payload = dict(inp)
    payload.update(fixed_fields)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "updatedInput": payload,
        "additionalContext": (
            "House style was applied to this edit for you (" + ", ".join(notes[:6]) + "). "
            "Both rules are exact substitutions from CLAUDE.md, so the correction is made rather "
            "than the edit refused - a refusal costs a model round trip to say the same thing. "
            "Text inside backticks was left alone: a word in a code span is being named, not used. "
            "Text inside quotation marks was left alone too: a quotation is someone else text (GM 2026-09-06)."),
    }}))
    raise SystemExit

print(" | ".join(hits[:6]) + (" [the GM own words - not corrected, only reported]" if GM_VERBATIM else ""))
')

[ -z "$REPORT" ] && exit 0
# GUARD_EDIT_OK: feature 164 - a JSON verdict is a CORRECTION to pass through, not a report to block on,
# and either way the firing is recorded so `make audit` can price this guard like the others.
# shellcheck source=/dev/null
. "$HS_HERE/_guardlog.sh"
case "$REPORT" in
  # GUARD_EDIT_OK: feature 236 - there are TWO JSON verdicts now, and they are different branches for
  # the audit: a CORRECTION applied to an edit, and a WARNING on a Bash payload that is left as typed.
  '{'*)
    if printf '%s' "$REPORT" | grep -q '"updatedInput"'; then
      guard_log house-style rewrote "$(guard_cmd)" corrected-edit
    else
      guard_log house-style warned "$(guard_cmd)" bash-payload
    fi
    printf '%s\n' "$REPORT"; exit 0 ;;
esac
guard_log house-style blocked "$(guard_cmd)"

cat >&2 <<TAIL
BLOCKED: house style ($REPORT).

CLAUDE.md, project-wide and for everything - generated content, prose, docs, specs, tests, comments
and code identifiers alike:

  - HYPHENS ONLY. No em-dash (U+2014), no en-dash (U+2013). Use " - ".
  - AMERICAN SPELLINGS. color, center, gray, honor, judgment, catalog, labeled, behavior, neighbor,
    analyze/organize/recognize, artifact, defense, license, practice, skeptic, story, while,
    traveled, modeled, program, meter, liter, mold, plow, curb, draft, aging, marvelous, jewelry,
    skillful. And "domain", never "demesne".

NOT flagged, deliberately: the GM's own writing (a SOURCE block, l7r.md, or a direct quotation of
either), and the files that must quote the rule to state it.

If this fired on a legitimate quotation of the GM, that is a bug in this hook worth fixing rather
than working around.

(scripts/house-style-hooks.sh; CLAUDE.md "Generation Behavior")
TAIL
exit 2
