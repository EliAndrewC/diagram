//! The lean bundle a plan review reads (feature 375 amendment 11, FR-046, plan D64; feature 449 T066, from `plan_bundle.py`). The GM,
//! 2026-10-13: *"Is feature 374 growing too large in a way that eats tokens"*. A section's decisions answer to the requirements they
//! cite, so the bundle carries those in full, a one-line index of the rest, the GM's own words whole, the blocks under review and their
//! earlier text - built out of the repository, where no `CLAUDE.md` rides along.

#![expect(
    clippy::format_collect,
    reason = "a bundle's strings are short, and each map reads as the text it writes"
)]

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use serde_json::{json, Map, Value};

use super::history::History;
use super::sections::{block_digest, blocks, digest, re, task_sections};
use super::status::{reviewed_blocks, text_of, REMOVED};

static IDS: LazyLock<Regex> = LazyLock::new(|| re(r"\b((?:FR|SC)-\d{3}[a-z]?|D\d+[a-z]?)\b"));
/// A requirement or decision id, and a list of them run on with commas, "and" or "or", which one qualifier names whole ("feature 204's
/// D5 and D6", "feature 204 spec D5, D6"; 451 T46).
const ID: &str = r"(?:(?:FR|SC)-\d{3}[a-z]?|D\d+[a-z]?)";
/// Each id of a run may carry a gloss in parentheses that names no id, `D3 (the pid file names the sampler), D13 (...), D5` (461 T68:
/// 461 T61's "451 T274's D3 (...), D13 (...), D5 (...)" ended its run at the first gloss, and D13 and D5 were read bare).
const RUN_ON: &str = r"(?:(?:\s*\((?:(?!(?:FR|SC)-\d|\bD\d)[^()])*\))?(?:,\s*|,?\s+(?:and|or)\s+)(?:(?:FR|SC)-\d{3}[a-z]?|D\d+[a-z]?)\b)*";
/// Another feature's requirements or decisions, named with its number (feature 385 T66, T71, T123; the `spec` form, the run-on list
/// and a task's possessive after the number, "444 T20's FR-043", 451 T46): the number group 1, its run group 2. Or, group 3, a run no
/// number names, followed by a clause naming a feature by its number ("FR-010 of feature 134", "D1 and D3 in 999's sections"), all of
/// it that feature's (451 T48: 4 of the 5 real clauses over every plan carried the reviewed feature's same-named id, measured 2026-11-21).
static QUALIFIED: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"(?<![-\w])(?:[Ff]eature\s+)?(\d{{3}})(?:'s|,)?\s+(?:amendment\s+\d+,?\s+)?(?:T\d+[a-z]?'s\s+)?\(?(?:(?:plan|spec)\s+)?({ID}\b{RUN_ON})|(?<![-\w])({ID}\b{RUN_ON})(?=\s+(?:in|of|from)\s+(?:[Ff]eature\s+)?\d{{3}}\b)"
    ))
});
/// An id named with a possessive that is no feature number ("house style's D11", "the spec's FR-002"; 451 T46): the name before `'s`
/// says whose it is, and only `OWN_NAMES` say this feature's.
static NAMED: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"(?<![\w.-])(?:([A-Za-z][\w-]*)\s+)?([A-Za-z][\w.-]*)'s\s+({ID}\b{RUN_ON})"
    ))
});
static ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \*\*((?:FR|SC)-\d{3}[a-z]?)\b"));
/// A requirement in any form the specs write it: the list item `ITEM` reads, a bold paragraph with no list dash, `**FR-007** ...` or
/// `**FR-004 - title.** ...`, which 24 specs of features 129 to 271 write some in and 21 write some id in alone, or an indented
/// sub-item with its own id, `  - **FR-005a**`, 184's and 295's (451 T82, measured 2026-11-21 over every `specs/*/spec.md`);
/// `spec_amendments` keeps `ITEM`, no spec writing a dashless id under an amendment heading.
static ANY_ITEM: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^(?:[ \t]*- )?\*\*((?:FR|SC)-\d{3}[a-z]?)\b"));
static RANGE: LazyLock<Regex> =
    LazyLock::new(|| re(r"\b(FR|SC)-(\d{3})\s*(?:-|to|through)\s*(?:(?:FR|SC)-)?(\d{3})\b"));
static DRANGE: LazyLock<Regex> = LazyLock::new(|| re(r"\bD(\d+)\s*(?:-|to|through)\s*D(\d+)\b"));
/// Every form the plans write a decision in (405 T133, D123; feature 449's plan's unbolded list item; a heading, `### D7 - title`, which
/// 48 plans write, 461's every decision among them, measured 2026-11-27 over every `specs/*/plan.md`: 461 T68).
static DECISION: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?m)^(?:#{2,4} |- \*\*|\*\*|- (?=D\d+[a-z]? - ))(D\d+[a-z]?)(?: - |\*\*|\.| |$)")
});
static HEAD_ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,4} ((?:FR|SC)-\d{3}[a-z]?)\b"));
static AMEND: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^## Amendment (\d+)\b"));
static SPEC_AMEND: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^### Amendment (\d+)\b"));
static KEY_AMEND: LazyLock<Regex> = LazyLock::new(|| re(r"\bAmendment (\d+)\b"));
static BODY_AMEND: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*#+ Amendment (\d+)\b"));
static NEXT_TOP: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{1,4} "));
/// A heading of any level, where a cited decision or requirement ends (451 T37).
static HEADING: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{1,6} "));
static NEXT_TWO: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^##"));
static MKEY: LazyLock<Regex> = LazyLock::new(|| re(r"\bm:([a-z0-9][a-z0-9-]*)"));
static BLOCK_TASK: LazyLock<Regex> = LazyLock::new(|| re(r"^#+ (T\d+)\b"));

const TOO_LONG: usize = 40;

/// A task section's own decision label, `T256-D1` (451 T257's review, 2026-11-25): not the spec's D1, which `IDS` read in it - the `-` is a
/// word boundary - so every task-section bundle carried the spec's D1 to D5 as cited; the label is dropped before the ids are read.
static TASK_LABEL: LazyLock<Regex> = LazyLock::new(|| re(r"\bT\d+[a-z]?-D\d+[a-z]?\b"));

/// `text` with each cited requirement or decision range written out id by id (at most 40 ids a range; a longer one is left as it is).
fn expand_ranges(text: &str) -> String {
    let text = &TASK_LABEL.replace_all(text, "");
    let first = RANGE.replace_all(text, |c: &Captures<'_>| {
        let (a, b): (usize, usize) = (c[2].parse().unwrap_or(0), c[3].parse().unwrap_or(0));
        if b > a && b - a <= TOO_LONG {
            (a..=b)
                .map(|n| format!("{}-{n:03}", &c[1]))
                .collect::<Vec<_>>()
                .join(", ")
        } else {
            c[0].to_owned()
        }
    });
    DRANGE
        .replace_all(&first, |c: &Captures<'_>| {
            let (a, b): (usize, usize) = (c[1].parse().unwrap_or(0), c[2].parse().unwrap_or(0));
            if b > a && b - a <= TOO_LONG {
                (a..=b)
                    .map(|n| format!("D{n}"))
                    .collect::<Vec<_>>()
                    .join(", ")
            } else {
                c[0].to_owned()
            }
        })
        .into_owned()
}

/// Where a list item's text ends inside `window` (which starts at the item): at the first blank line whose next line is not indented,
/// so an item runs on into its own indented lines, a nested list or table among them, and stops before its siblings' text.
fn item_end(window: &str) -> usize {
    let mut from = 0;
    while let Some(p) = window[from..].find("\n\n") {
        let blank = from + p;
        let rest = window[blank..].trim_start_matches('\n');
        if !rest.starts_with([' ', '\t']) {
            return blank;
        }
        from = window.len() - rest.len();
    }
    window.len()
}

/// `{id: its text}`, each carried whole (feature 451 T37: a cut at the first blank line stopped D15 at its colon and D16 at "Two things
/// make the comparison real:", and a reviewer judged each without its bullets). Each match runs to the next match or the next heading;
/// one written as a list item (`- **FR-NNN**`, `- **D7**`, an indented `  - **FR-005a**`) stops sooner, at a blank line its own
/// indented lines do not follow.
fn paragraphs(text: &str, pattern: &Regex) -> Map<String, Value> {
    let starts: Vec<(usize, String)> = pattern
        .captures_iter(text)
        .map_while(Result::ok)
        .map(|c| (c.get(0).map_or(0, |g| g.start()), c[1].to_owned()))
        .collect();
    let mut out = Map::new();
    for (i, (at, id)) in starts.iter().enumerate() {
        let next = starts.get(i + 1).map_or(text.len(), |(a, _)| *a);
        // the heading after the match's first line: a match's own line never opens with `#`
        let line_end = text[*at..next].find('\n').map_or(next, |p| at + p);
        let mut end = HEADING
            .find(&text[line_end..next])
            .ok()
            .flatten()
            .map_or(next, |h| line_end + h.start());
        if text[*at..]
            .trim_start_matches([' ', '\t'])
            .starts_with("- ")
        {
            end = at + item_end(&text[*at..end]);
        }
        out.entry(id.clone())
            .or_insert_with(|| Value::from(format!("{}\n", text[*at..end].trim_end())));
    }
    out
}

/// `{FR or SC id: its text}`: a `- **FR-NNN**` item as `paragraphs` carries it, a `### FR-NNN` heading to the next heading, and a
/// `**FR-NNN**` paragraph with no list dash to the next requirement of any form or the next heading, as a dashless decision runs, and
/// an indented sub-item as a list item (451 T82: each was NOT FOUND, 449's "FR-007 of feature 239" among them). An id the first two
/// forms give keeps their text, a dashless line restating it being commentary: 170's `### FR-006` restated in bold under it, 177's
/// "FR-006a, PROVEN" after its item.
fn requirements(spec: &str) -> Map<String, Value> {
    let mut out = paragraphs(spec, &ITEM);
    for c in HEAD_ITEM.captures_iter(spec).map_while(Result::ok) {
        let whole = c.get(0).map_or((0, 0), |g| (g.start(), g.end()));
        let rest = &spec[whole.1..];
        let end = NEXT_TOP
            .find(rest)
            .ok()
            .flatten()
            .map_or(spec.len(), |n| whole.1 + n.start());
        out.entry(c[1].to_owned())
            .or_insert_with(|| Value::from(format!("{}\n", spec[whole.0..end].trim_end())));
    }
    for (id, text) in paragraphs(spec, &ANY_ITEM) {
        out.entry(id).or_insert(text);
    }
    out
}

/// `request.md` as (the original request, [(amendment number, its section)]).
fn request_sections(text: &str) -> (&str, Vec<(u32, &str)>) {
    let starts: Vec<(usize, u32)> = AMEND
        .captures_iter(text)
        .map_while(Result::ok)
        .map(|c| (c.get(0).map_or(0, |g| g.start()), c[1].parse().unwrap_or(0)))
        .collect();
    let Some(first) = starts.first() else {
        return (text, Vec::new());
    };
    let parts = starts
        .iter()
        .enumerate()
        .map(|(i, (at, n))| {
            (
                *n,
                &text[*at..starts.get(i + 1).map_or(text.len(), |s| s.0)],
            )
        })
        .collect();
    (&text[..first.0], parts)
}

/// `{FR or SC id: the amendment whose spec section holds it}`.
fn spec_amendments(spec: &str) -> BTreeMap<String, u32> {
    let mut out = BTreeMap::new();
    for c in SPEC_AMEND.captures_iter(spec).map_while(Result::ok) {
        let start = c.get(0).map_or(0, |g| g.end());
        let rest = &spec[start..];
        let body = NEXT_TWO
            .find(rest)
            .ok()
            .flatten()
            .map_or(rest, |n| &rest[..n.start()]);
        for item in ITEM.captures_iter(body).map_while(Result::ok) {
            out.entry(item[1].to_owned())
                .or_insert(c[1].parse().unwrap_or(0));
        }
    }
    out
}

/// The earliest amendment the blocks answer; None when any block answers none (the original plan, judged against the whole request).
fn answered(under: &[(String, String)], spec: &str) -> Option<u32> {
    let of = spec_amendments(spec);
    let mut found = Vec::new();
    for (key, body) in under {
        let named = KEY_AMEND
            .captures(key)
            .ok()
            .flatten()
            .or(BODY_AMEND.captures(body).ok().flatten())
            .map(|c| c[1].parse().unwrap_or(0));
        let joined = TASK_LABEL
            .replace_all(&format!("{key}\n{body}"), "")
            .into_owned();
        let ns: Vec<u32> = named
            .into_iter()
            .chain(
                IDS.captures_iter(&joined)
                    .map_while(Result::ok)
                    .filter_map(|i| of.get(&i[1]).copied()),
            )
            .collect();
        found.push(*ns.iter().min()?);
    }
    found.into_iter().min()
}

/// (the request a review of amendment `n` reads, the index of what it leaves out). Every amendment from `n` on is kept.
fn trimmed_request(text: &str, n: Option<u32>) -> (String, String) {
    let (head, parts) = request_sections(text);
    let Some(n) = n.filter(|_| !parts.is_empty()) else {
        return (text.to_owned(), String::new());
    };
    let kept: String = parts
        .iter()
        .filter(|(k, _)| *k >= n)
        .map(|(_, b)| *b)
        .collect();
    let index: String = parts
        .iter()
        .filter(|(k, _)| *k < n)
        .map(|(_, body)| {
            let mut lines = body.lines();
            let first = lines.next().unwrap_or("");
            let next: String = lines
                .find(|l| !l.trim().is_empty())
                .unwrap_or("")
                .trim()
                .chars()
                .take(160)
                .collect();
            format!("{first} - {next}\n")
        })
        .collect();
    (format!("{head}{kept}"), index)
}

fn read(path: &Path) -> String {
    super::once::text(path)
}

fn plans_of(dir: &Path) -> String {
    read(&dir.join("plan.md")) + &super::once::plan_done(dir)
}

/// Each `m:` figure the blocks cite, in full from the feature's `measurements.json`.
fn measured(spec_dir: &Path, bodies: &[&str]) -> String {
    let mut keys: Vec<String> = Vec::new();
    for body in bodies {
        for c in MKEY.captures_iter(body).map_while(Result::ok) {
            if !keys.iter().any(|k| *k == c[1]) {
                keys.push(c[1].to_owned());
            }
        }
    }
    let figures: Value =
        serde_json::from_str(&read(&spec_dir.join("measurements.json"))).unwrap_or(json!({}));
    let found: Vec<String> = keys
        .iter()
        .filter_map(|k| {
            let entry = figures.get(k)?.as_object()?;
            let lines: String = entry
                .iter()
                .map(|(f, v)| {
                    format!(
                        "- **{f}**: {}\n",
                        v.as_str()
                            .map_or_else(|| crate::checks::py_repr(v), str::to_owned)
                    )
                })
                .collect();
            Some(format!("### m:{k}\n\n{lines}"))
        })
        .collect();
    if found.is_empty() {
        String::new()
    } else {
        format!(
            "\n\n## The measurements the blocks cite (`measurements.json`)\n\n{}",
            found.join("\n")
        )
    }
}

fn json_str(text: &str) -> String {
    serde_json::to_string(text).unwrap_or_default()
}

/// A Python `json.dumps` of a text: non-ASCII escaped.
fn ascii_json(text: &str) -> String {
    json_str(text)
        .chars()
        .flat_map(|c| {
            if c.is_ascii() {
                vec![c.to_string()]
            } else {
                c.encode_utf16(&mut [0; 2])
                    .iter()
                    .map(|u| format!("\\u{u:04x}"))
                    .collect()
            }
        })
        .collect()
}

/// The longest index line, in characters, before it is cut at a word and marked ` [...]` (451 T46, the coordinator 2026-11-20: the
/// index is for grepping, and the defect was the SILENT cut, not the length). A CONVENTION, "about 400": 420 keeps FR-009's sentence,
/// the defect's own line, whole at 418, measured 2026-11-20 (`/tmp/t46-scripts/idx2.py`: 267 of 4,686 lines marked at 420, 315 at 400).
const INDEX_CAP: usize = 420;

/// Whether the `.` before `after` ends no sentence: its next word starts lowercase (451 T46, the coordinator 2026-11-20: a real sentence
/// starts with a capital, a digit, a backtick or a bold mark, so "(e.g. a well)", "... of things" and a plain word's ". then" run on and
/// no cut is left unmarked).
fn runs_on(after: &str) -> bool {
    after
        .trim_start()
        .chars()
        .next()
        .is_some_and(char::is_lowercase)
}

/// A requirement's index line: its first sentence, ending at a `.` before a space or the end, outside a code span and not before a
/// lowercase word (`runs_on`), its hard-wrapped lines joined (451 T46: the first line alone cut FR-009 mid-sentence), past `INDEX_CAP`
/// cut at a word and marked ` [...]`.
fn lead(text: &str) -> String {
    let joined = paragraph(text);
    let mut code = false;
    let mut end = joined.len();
    for (i, c) in joined.char_indices() {
        if c == '`' {
            code = !code;
        } else if c == '.'
            && !code
            && joined[i + 1..].chars().next().is_none_or(|n| n == ' ')
            && !runs_on(&joined[i + 1..])
        {
            end = i + 1;
            break;
        }
    }
    let sentence = &joined[..end];
    // a line shorter than its lead paragraph always ends marked, whatever ended it (451 T46 round 2: no cut is silent by construction)
    let short = sentence.trim_end().len() < joined.trim_end().len();
    let line = if sentence.chars().count() <= INDEX_CAP {
        sentence.to_owned()
    } else {
        let cut: String = sentence.chars().take(INDEX_CAP).collect();
        let at = cut.rfind(' ').unwrap_or(cut.len());
        return format!("{} [...]", &cut[..at]);
    };
    if short {
        format!("{line} [...]")
    } else {
        line
    }
}

/// A requirement's lead paragraph on one line, its wrapped lines joined; a nested list, table or fence under it is the requirement's
/// own text, not its index line; a heading requirement is its heading. A wrapped line opening with `#` is prose: since T37 no item's
/// text holds a heading line.
fn paragraph(text: &str) -> String {
    let mut lines = text.lines();
    let mut out = lines.next().unwrap_or("").trim_end().to_owned();
    if out.starts_with('#') {
        return out;
    }
    for line in lines {
        let t = line.trim();
        let numbered = t
            .split_once(". ")
            .is_some_and(|(n, _)| !n.is_empty() && n.bytes().all(|b| b.is_ascii_digit()));
        if t.is_empty()
            || numbered
            || ["- ", "* ", "+ ", "|", "```"]
                .iter()
                .any(|m| t.starts_with(m))
        {
            break;
        }
        out.push(' ');
        out.push_str(t);
    }
    out
}

/// Write the bundle for the blocks `under` and return its MANIFEST; `earlier` is `{key: (its text when last judged, the verdict it got)}`.
pub(super) fn build(
    spec_dir: &Path,
    out_root: &Path,
    name: &str,
    under: &[(String, String)],
    earlier: &[(String, String, String)],
    how: &str,
) -> Result<PathBuf, String> {
    let feature = spec_dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    // NO REQUEST, NO BUNDLE (feature 405 T30, D2): a review against the spec alone tests the plan for self-consistency only.
    if !spec_dir.join("request.md").is_file() {
        return Err(format!("plan bundle: specs/{feature}/request.md is missing - write the GM's words there verbatim (the request and every amendment, as the spec's 'The request' quotes them), commit it, and build again"));
    }
    // ...A NAME THAT FITS THE FILE SYSTEM (feature 449, 2026-11-07): past 120 characters it is cut, the rest kept as a hash.
    let name = if name.chars().count() > 120 {
        format!(
            "{}-{}",
            name.chars().take(80).collect::<String>(),
            &digest(name.as_bytes())[..12]
        )
    } else {
        name.to_owned()
    };
    let out = out_root.join(format!("plan-{feature}-{name}"));
    let _ = std::fs::remove_dir_all(&out);
    let _ = std::fs::create_dir_all(&out);
    let spec = read(&spec_dir.join("spec.md"));
    let (items, decisions) = (
        requirements(&spec),
        paragraphs(&plans_of(spec_dir), &DECISION),
    );
    let owners = owners_of(spec_dir, under, &SECTION_DECISION);
    let (parts, cited) = cited_text(spec_dir, &feature, under, &owners, &items, &decisions);
    let bodies: Vec<&str> = under.iter().map(|(_, b)| b.as_str()).collect();
    let write = |file: &str, text: String| {
        let _ = std::fs::write(out.join(file), text);
    };
    write(
        "spec-cited.md",
        format!(
            "# The requirements and decisions the blocks name, in full\n\n{}{}",
            parts.join("\n"),
            measured(spec_dir, &bodies)
        ),
    );
    let index: String = items
        .iter()
        .filter(|(i, _)| !cited.contains(*i))
        .map(|(_, p)| format!("{}\n", lead(p.as_str().unwrap_or(""))))
        .collect();
    // every ruling a block cites, its record's ruling, why, what and tooling fix (feature 449 T169, 451 T177): the reviewer reads nothing in the repository
    write("rulings.md", rulings::rulings(spec_dir, &bodies));
    write(
        "spec-index.md",
        format!("# Every other requirement, its first sentence on one line (past {INDEX_CAP} characters cut at a word and marked [...])\n\n{index}"),
    );
    let ours = ours(&feature, under, &owners);
    let (req, left) = trimmed_request(&read(&spec_dir.join("request.md")), answered(&ours, &spec));
    write("request.md", req);
    let shown = if left.is_empty() {
        "(none - the whole request is in request.md)\n".to_owned()
    } else {
        left
    };
    write("request-index.md", format!("# The request's sections left out - each earlier amendment, its heading and first line\n\n{shown}"));
    write(
        "blocks.md",
        under
            .iter()
            .map(|(k, b)| {
                // ...ITS KEY AS PLAN.MD HOLDS IT (461 T70): the reviewer copies it into `make plan-verdict BLOCKS=1`; JSON-escaped, a
                // heading's `"` read `\"` and T32,T33's first record was refused. The hold's reader anchors on the digest's tail.
                format!("<!-- block \"{k}\" sha256 {} -->\n{b}\n", block_digest(b))
            })
            .collect(),
    );
    let before: String = earlier
        .iter()
        .map(|(k, t, v)| {
            format!(
                "<!-- block \"{k}\" verdict {} -->\n{t}\n",
                if v.is_empty() {
                    "no verdict recorded"
                } else {
                    v
                }
            )
        })
        .collect();
    let before = if before.is_empty() {
        "(none - every block here is new)\n".to_owned()
    } else {
        before
    };
    write(
        "earlier.md",
        format!("# Each changed block's text when last judged, with that verdict\n\n{before}"),
    );
    let manifest = out.join("MANIFEST.md");
    let _ = std::fs::write(&manifest, format!("# Plan review bundle - {feature}, {name}\n\nA MODE 4 plan review of the blocks in `blocks.md` and nothing else of the plan (feature 375 amendment 11). Read the files beside\nthis MANIFEST and nothing in the repository: `request.md` is the GM's words verbatim - the original request and every amendment\nfrom the one these blocks answer on, the earlier ones indexed in `request-index.md`; `spec-cited.md` holds every requirement,\ndecision and `m:` measurement the blocks name, in full; `rulings.md` the round arbiter's ruling, why, what and tooling fix, verbatim, for every `ask:`\nruling the blocks cite; `spec-index.md` every other requirement's first sentence on one line, a long one cut and marked `[...]` - grep it for one the blocks\nshould have named; `earlier.md` what a changed block said when last judged, and the verdict it got.\n\nBuilt from the tree `{tree}`: record the verdict there, by the command below (451 T257).\n\nFind each decision in the blocks, class it `within` or `narrowing`, and rule on each narrowing (LEGITIMATE / NOT LEGITIMATE).\n\n{how}\n", tree = tree_of(spec_dir)));
    Ok(manifest)
}

/// The tree a bundle is built from (451 T257): the spec directory's, absolute, where the reviewed text is and where its verdict records.
pub(super) fn tree_of(spec_dir: &Path) -> String {
    let root = spec_dir
        .parent()
        .and_then(Path::parent)
        .unwrap_or(Path::new("."));
    std::path::absolute(root)
        .unwrap_or_default()
        .display()
        .to_string()
}

fn review_of(spec_dir: &Path) -> std::rc::Rc<Value> {
    super::once::record(spec_dir)
}

fn number_of(spec_dir: &Path) -> String {
    spec_dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .split('-')
        .next()
        .unwrap_or("")
        .to_owned()
}

/// `make decide`'s dispatch (FR-003(a)) on the bundle of one task's section.
pub(super) fn task_prompt(spec_dir: &Path, out_root: &Path, task: &str) -> Result<String, String> {
    let plan = spec_dir.join("plan.md");
    let section = task_sections(&read(&plan)).remove(task).unwrap_or_default();
    let review = review_of(spec_dir);
    let entry = review
        .get("tasks")
        .and_then(|t| t.get(task))
        .cloned()
        .unwrap_or(json!({}));
    let was = text_of(&entry, "section_sha256")
        .filter(|s| !s.is_empty())
        .and_then(|s| History::new(&plan, "HEAD").section(task, s));
    let n = number_of(spec_dir);
    let how = format!("Record it: the JSON is `{{\"section_sha256\": \"{}\", \"decisions\": [...]}}`, written under /tmp, then `make -C {} plan-verdict F={n} TASK={task} FILE=<it> AS=spec-fidelity`.", digest(section.as_bytes()), tree_of(spec_dir));
    let earlier: Vec<(String, String, String)> = was
        .into_iter()
        .map(|t| {
            (
                task.to_owned(),
                t,
                text_of(&entry, "verdict").unwrap_or("").to_owned(),
            )
        })
        .collect();
    // THE TREE'S OWN DIRECTORY (451 T288): since 451 T369 a task is started in a pool tree and the clone both, and the second
    // `make decide` rewrote the first's bundle under the first's reviewer. The tree is hashed into the name as `make plan-delta`'s
    // bundles are (T271), `plan-<feature>-<task>-<8 hex>`, the shape the plan hold (`checks::planhold`'s BUNDLE) matches.
    let name = format!("{task}-{}", &digest(tree_of(spec_dir).as_bytes())[..8]);
    let manifest = build(
        spec_dir,
        out_root,
        &name,
        &[(format!("the section of {task}"), section)],
        &earlier,
        &how,
    )?;
    let feature = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    Ok(format!("MODE 4: PLAN REVIEW of one task's section - feature {feature}, task {task} (a decision preflight, feature 375 FR-003a), on its bundle: read {} and the files beside it, and nothing in the repository.", manifest.display()))
}

/// `make plan-delta`'s dispatch (FR-043) on the bundle of the plan's changed blocks.
pub(super) fn delta_prompt(
    spec_dir: &Path,
    out_root: &Path,
    keys: &[String],
) -> Result<String, String> {
    let plan = spec_dir.join("plan.md");
    let text = read(&plan);
    let under: Vec<(String, String)> = blocks(&text)
        .into_iter()
        .filter(|(k, ..)| keys.contains(k))
        .map(|(k, b, _)| (k, b))
        .collect();
    let have = reviewed_blocks(&review_of(spec_dir));
    let history = History::new(&plan, "HEAD");
    let removed: Vec<&str> = keys
        .iter()
        .filter_map(|k| k.strip_prefix(REMOVED))
        .collect();
    let text_at = |k: &str| -> String {
        let entry = &have[k];
        text_of(entry, "text")
            .filter(|t| !t.is_empty())
            .map(str::to_owned)
            .or_else(|| history.block(k, text_of(entry, "sha256").unwrap_or("None")))
            .unwrap_or_default()
    };
    let verdict_at = |k: &str| text_of(&have[k], "verdict").unwrap_or("").to_owned();
    let mut earlier: Vec<(String, String, String)> = Vec::new();
    for (k, _) in under.iter().filter(|(k, _)| have.contains_key(k)) {
        earlier.push((k.clone(), text_at(k), verdict_at(k)));
    }
    for k in removed.iter().filter(|k| have.contains_key(**k)) {
        earlier.push((format!("{REMOVED}{k}"), text_at(k), verdict_at(k)));
    }
    let n = number_of(spec_dir);
    let mut shas: Vec<String> = under
        .iter()
        .map(|(k, b)| format!("{}: \"{}\"", ascii_json(k), block_digest(b)))
        .collect();
    shas.extend(
        removed
            .iter()
            .map(|k| format!("{}: \"removed\"", ascii_json(&format!("{REMOVED}{k}")))),
    );
    let shas = format!("{{{}}}", shas.join(", "));
    let how = format!("Record it: the JSON is `{{\"blocks\": {shas}, \"decisions\": [...]}}`, written under /tmp, then `make -C {} plan-verdict F={n} BLOCKS=1 FILE=<it> AS=spec-fidelity`.", tree_of(spec_dir));
    let tasks: BTreeSet<String> = under
        .iter()
        .filter_map(|(k, _)| {
            BLOCK_TASK
                .captures(k)
                .ok()
                .flatten()
                .map(|c| c[1].to_owned())
        })
        .collect();
    let label = if tasks.is_empty() {
        "plan".to_owned()
    } else {
        tasks.into_iter().collect::<Vec<_>>().join("-")
    };
    // THE TREE'S OWN DIRECTORY (451 T271): every worktree writes under one bundles root, and two trees whose plans agree owe the
    // same blocks at the same digests - the second `make plan-delta` rewrote the first's bundle, its tree line and recording command
    // the other tree's, under the first's reviewer. The tree is hashed with the blocks, so the name keeps its shape
    // (`blocks-<tasks>-<8 hex>`) for the readers that match it: the plan hold, the plan-round cap, the ledger's subject.
    let keyed = format!("{shas}\n{}", tree_of(spec_dir));
    let name = format!("blocks-{label}-{}", &digest(keyed.as_bytes())[..8]);
    let kept: Vec<(String, String, String)> = earlier
        .into_iter()
        .filter(|(_, t, _)| !t.is_empty())
        .collect();
    let manifest = build(spec_dir, out_root, &name, &under, &kept, &how)?;
    let feature = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    Ok(format!("MODE 4: PLAN REVIEW of {} changed block(s) of feature {feature}'s plan (feature 375 FR-043), on their bundle: read {} and the files beside it, and nothing in the repository.", under.len() + removed.len(), manifest.display()))
}

mod cited;
mod rulings;
mod section;

#[cfg(test)]
use cited::ids_in;
use cited::{cited_text, named, SECTION_DECISION};
use section::{ours, owners_of};

#[cfg(test)]
mod tests;
