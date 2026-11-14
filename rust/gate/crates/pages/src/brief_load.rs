//! How many research questions a page-session brief ASSIGNS (feature 274 D1): the one count the write cap rests on. Ported whole from
//! `scripts/pages/brief_load.py` by feature 449 T137 (`ask:449-phase3-remainder`); the runner asks it in process, and its command form
//! stays as `l7r-gate brief-load <record dir> <brief> ...` (T119's rule: no form vanishes unannounced).
//!
//! WHY (feature 274, research R1). After feature 250 the cost per thing checked held, but the largest context doubled, and it was the
//! write sessions: a write session's cost follows its turn count (r = 0.92), groups had grown to twice R11's size, and because every
//! turn re-reads the context so far a session's cost grows roughly with the square of its length. One 272 write session cost 24.5 M over
//! 109 turns. So a WRITE session takes at most four questions ([`CAP`]), and the runner counts every brief before it starts one,
//! whatever generator wrote it (spec, round 3: a required declaration would have broken the other features' generators until each
//! changed).
//!
//! WHAT IS COUNTED - only what the brief assigns (spec, round 4): the `## Your items` section (to the next `## `), and the `**Your
//! questions:**` and `**Your pairs**` lines or blocks. Never a "do not edit" paragraph, which names other sessions' sections and would
//! count them. Since feature 303 a question is named by its stem number, which is unique across the record
//! (`questions/NNNN-<slug>.html` under the record):
//!   - in the check-brief form, `Q=NNNN` (or `Q=NNNN, NNNN`) counts one each; a pair (`KIND=X (Q=NNNN)`) one per question;
//!   - in an item line, every four-digit number inside a backtick span (`0412`, `0215, 0221`) that is a stem on disk; code and
//!     fact-check references (`file.py:195-304`, `fc:2113`) are stripped first;
//!   - a line naming no question counts one question per distinct item id (`B30`, `D52`), and at least one.
//!
//! It errs toward over-counting, the safe side for a cap. Prototyped on the real briefs of 269, 271 and 272 (plan D1).
//!
//! THE EXEMPT KINDS (spec, Edge Cases). A brief that is not a group's writing declares one line, `<!-- page-load: kind=<kind> -->`:
//! `check` (a check-and-apply session, which the cap does not cover), `assertions` (feature 250's FR-002 briefs, many assertions inside
//! existing questions), `split` (splitting an over-cap question) or `handover` (a group handed to another feature). Any other kind is
//! refused, and so is a brief that assigns nothing countable and declares no kind: the count never fails open.

use std::collections::BTreeSet;
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::{py_suffix_stem, raised, read_strict, reply};
use l7r_gate_core::Reply;

/// Questions a write session takes at most.
pub const CAP: usize = 4;
/// The kinds a brief may declare to be exempt from the count.
pub const KINDS: [&str; 4] = ["check", "assertions", "split", "handover"];

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

// `re.match` anchors at the start, `re.fullmatch` at both ends: `^` and `\z` stand for them; `\Z` is the regex crate's `\z`
static KIND_LINE: LazyLock<Regex> =
    LazyLock::new(|| re(r"<!--\s*page-load:\s*kind=([\w-]+)\s*-->"));
static STEM: LazyLock<Regex> = LazyLock::new(|| re(r"^(\d{4})-[^.]+(?:\.drawing)?\.html\n?\z"));
static CODE_REF: LazyLock<Regex> =
    LazyLock::new(|| re(r"[\w/.-]+\.(?:py|json|md|js|svg|txt|sh)(?::[\d,-]+)?|\b[a-z]+:\d[\d,-]*"));
static Q_LIST: LazyLock<Regex> = LazyLock::new(|| re(r"Q=(\d{4}(?:\s*,\s*\d{4})*)"));
static FOUR: LazyLock<Regex> = LazyLock::new(|| re(r"\d{4}"));
static NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"(?<![\d.])\d{4}(?![\d])"));
static ITEM_ID: LazyLock<Regex> = LazyLock::new(|| re(r"\b[A-Z]{1,2}\d{2,3}\b"));
static LEAD_IDS: LazyLock<Regex> =
    LazyLock::new(|| re(r"^(?:\s*,?\s*[A-Z]{1,2}\d{2,3}(?:-[A-Z]{1,2}\d{2,3})?\b)+"));
static ITEMS: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?ms)^## Your items[^\n]*\n(.*?)(?=^## |\z)"));
static BLOCK_HEAD: LazyLock<Regex> = LazyLock::new(|| re(r"^\*\*Your (?:questions|pairs)\b"));
static BLOCK_END: LazyLock<Regex> = LazyLock::new(|| re(r"^(?:\*\*|#|\d+\.\s)"));
static TICKED: LazyLock<Regex> = LazyLock::new(|| re(r"`([^`]*)`"));
static ID_WORD: LazyLock<Regex> = LazyLock::new(|| re(r"^[A-Z]{1,2}\d+\z"));

/// Every match of `rx` in `text`, as `re.findall` gives them (the first group where there is one).
fn findall(rx: &Regex, text: &str, group: usize) -> Vec<String> {
    rx.captures_iter(text)
        .filter_map(Result::ok)
        .filter_map(|c| c.get(group).map(|m| m.as_str().to_owned()))
        .collect()
}

/// `int()` of a run of digits (`\d` is any decimal digit, as Python's is; one no `u32` reads is skipped, a case no brief reaches).
fn numbers(texts: &[String]) -> Vec<u32> {
    texts.iter().filter_map(|t| t.parse().ok()).collect()
}

/// Every question's number in the record (`<record>/questions/NNNN-<slug>.html`). Derived, never listed, so a question added later is
/// counted without an edit here.
#[must_use]
pub fn stems(record: &Path) -> BTreeSet<u32> {
    let q = record.join("questions");
    let Ok(entries) = std::fs::read_dir(&q) else {
        return BTreeSet::new();
    };
    entries
        .filter_map(Result::ok)
        .map(|e| e.file_name().to_string_lossy().into_owned())
        // the glob `[0-9][0-9][0-9][0-9]-*.html`, then the stem's own pattern
        .filter(|n| {
            n.len() > 9
                && n.as_bytes()[..4].iter().all(u8::is_ascii_digit)
                && n.as_bytes()[4] == b'-'
                && Path::new(n).extension().is_some_and(|x| x == "html")
        })
        .filter_map(|n| {
            STEM.captures(&n)
                .ok()
                .flatten()
                .and_then(|c| c[1].parse().ok())
        })
        .collect()
}

/// The kind the brief declares, or "" when it declares none.
#[must_use]
pub fn declared(text: &str) -> String {
    KIND_LINE
        .captures(text)
        .ok()
        .flatten()
        .map_or_else(String::new, |c| c[1].to_owned())
}

/// (the `## Your items` section, the `**Your questions:**` and `**Your pairs**` blocks) - all a brief assigns.
fn assignment_lists(text: &str) -> (String, String) {
    let items = ITEMS
        .captures(text)
        .ok()
        .flatten()
        .map_or_else(String::new, |c| c[1].to_owned());
    let lines = l7r_guard::shared::speckit::splitlines(text);
    let mut blocks = Vec::new();
    for (i, line) in lines.iter().enumerate() {
        if BLOCK_HEAD.is_match(line).unwrap_or(false) {
            let mut block = vec![*line];
            for nxt in &lines[i + 1..] {
                if l7r_guard::shared::py_text::strip(nxt).is_empty()
                    || BLOCK_END.is_match(nxt).unwrap_or(false)
                {
                    break;
                }
                block.push(nxt);
            }
            blocks.push(block.join("\n"));
        }
    }
    (items, blocks.join("\n"))
}

/// The four-digit numbers of every `Q=` list in `text`.
fn q_lists(text: &str) -> Vec<u32> {
    findall(&Q_LIST, text, 1)
        .iter()
        .flat_map(|l| numbers(&findall(&FOUR, l, 0)))
        .collect()
}

/// `re.split(r"\n(?=- )", items)`: the items cut at each newline that a `- ` follows.
fn item_lines(items: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut start = 0;
    for (at, _) in items.match_indices('\n') {
        if items[at + 1..].starts_with("- ") {
            out.push(&items[start..at]);
            start = at + 1;
        }
    }
    out.push(&items[start..]);
    out
}

/// (questions assigned, what was counted: `NNNN` for a question, the item id for a new question). An item line of nothing but `- `
/// is the Python's `IndexError` (`line[2:].split()[0]`), which the runner's caller met as a crash.
///
/// # Errors
///
/// The Python's raise on such a line.
pub fn count(text: &str, record: &Path) -> Result<(usize, Vec<String>), String> {
    let on_disk = stems(record);
    let (items, blocks) = assignment_lists(text);
    let mut found: BTreeSet<u32> = q_lists(&blocks).into_iter().collect();
    let mut new: Vec<String> = Vec::new();
    for line in item_lines(&items) {
        let Some(rest) = line.strip_prefix("- ") else {
            continue;
        };
        let clean = CODE_REF.replace_all(line, " ");
        let mut got: BTreeSet<u32> = q_lists(&clean).into_iter().collect();
        for span in findall(&TICKED, &clean, 1) {
            got.extend(numbers(&findall(&NUMBER, &span, 0)));
        }
        got.retain(|n| on_disk.contains(n));
        if got.is_empty() {
            // The ids that LEAD the line are its questions ("- A133 A135 D49 D52-D56 ..." assigns each); an id later in its prose is a
            // citation ("B16's finding"), and counting those made 269's FX1 six where it had four (feature 347's measurement).
            if let Some(head) = LEAD_IDS.find(rest).ok().flatten() {
                // `list(dict.fromkeys(...))`: one line's ids deduplicated, first seen first; a repeat across lines still counts twice
                let mut ids: Vec<String> = Vec::new();
                for id in findall(&ITEM_ID, head.as_str(), 0) {
                    if !ids.contains(&id) {
                        ids.push(id);
                    }
                }
                new.extend(ids);
            } else {
                let word = l7r_guard::shared::py_text::split(rest)
                    .first()
                    .map(|w| (*w).to_owned())
                    .ok_or_else(|| "IndexError: list index out of range".to_owned())?;
                new.push(word);
            }
        } else {
            found.extend(got);
        }
    }
    let n = found.len() + new.len();
    let detail = found.iter().map(|n| format!("{n:04}")).chain(new).collect();
    Ok((n, detail))
}

/// (the declared kind or "", questions assigned, what was counted).
///
/// # Errors
///
/// What [`count`] raised.
pub fn load(text: &str, record: &Path) -> Result<(String, usize, Vec<String>), String> {
    let (n, detail) = count(text, record)?;
    Ok((declared(text), n, detail))
}

/// The briefs a group of `n` questions splits into, at most [`CAP`] each: `v2-write.md` -> `v2a-write.md`, `v2b-...`.
#[must_use]
pub fn split_names(brief: &Path, n: usize) -> Vec<String> {
    let (stem, suffix) = py_suffix_stem(brief);
    let (group, tail) = stem
        .strip_suffix("-write")
        .map_or((stem.as_str(), ""), |g| (g, "-write"));
    (0..n.div_ceil(CAP))
        .map(|i| {
            let letter = char::from_u32(97 + u32::try_from(i).unwrap_or(0)).unwrap_or('?');
            format!("{group}{letter}{tail}{suffix}")
        })
        .collect()
}

/// Why the runner must not start this brief, or "" when it may.
///
/// # Errors
///
/// What [`count`] raised.
pub fn refusal(brief: &Path, text: &str, record: &Path) -> Result<String, String> {
    let (kind, n, detail) = load(text, record)?;
    if !kind.is_empty() {
        return Ok(if KINDS.contains(&kind.as_str()) {
            String::new()
        } else {
            format!(
                "it declares kind={kind}, which is not an exempt kind ({})",
                KINDS.join(", ")
            )
        });
    }
    if n == 0 {
        return Ok(format!(
            "it assigns nothing the count can read (no `## Your items`, `**Your questions:**` or `**Your pairs**` naming a question) and \
             declares no kind - add `<!-- page-load: kind=<{}> -->` if it is not a group's writing",
            KINDS.join("|")
        ));
    }
    if n > CAP {
        let parts = split_names(brief, n);
        return Ok(format!(
            "it assigns {n} questions ({}); a write session takes at most {CAP} (feature 274: a write session's cost grows with the square \
             of its length). Split it into {} briefs of at most {CAP} - {} - each with its own handoff, and queue them one after another; \
             or, for a deliberate larger load, set WRITE_CAP_OK='<reason>'{}",
            detail.join(", "),
            parts.len(),
            parts.join(", "),
            parts_tip(&detail)
        ));
    }
    Ok(String::new())
}

/// `str.isdigit()`: every character a digit, and at least one (a Unicode digit read as `char::is_numeric`, which also takes a fraction
/// or a Roman numeral that Python's does not - a first word no brief carries).
fn isdigit(word: &str) -> bool {
    !word.is_empty() && word.chars().all(char::is_numeric)
}

/// The tip when the count fell back to a line's first word: those lines named no question and led with no item id, so each was counted
/// one question - which is right for a new question but wrong for the parts of one (feature 404's brief: five bold bullets of 0260
/// counted five).
fn parts_tip(detail: &[String]) -> String {
    let words: Vec<&str> = detail
        .iter()
        .map(String::as_str)
        .filter(|d| !isdigit(d) && !ID_WORD.is_match(d).unwrap_or(false))
        .collect();
    if words.is_empty() {
        return String::new();
    }
    format!(
        ". The lines counted as {} name no question and lead with no item id; if they are the parts of one question, nest them as indented \
         sub-bullets under one `- B1 ...` line naming it (`NNNN` in backticks)",
        words.join(", ")
    )
}

/// `l7r-gate brief-load <record dir> <brief> ...`: `<kind or write> <count> <brief>: <what was counted>` for each, and why it is refused
/// beneath one the cap refuses; exit 1 when one is. A brief that cannot be read strictly as UTF-8 is the Python's raise.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    if args.len() < 2 {
        return reply(
            String::new(),
            "usage: l7r-gate brief-load <record dir> <brief> ...\n".to_owned(),
            2,
        );
    }
    let record = l7r_guard::shared::speckit::py_path(&args[0]);
    let mut out = String::new();
    let mut bad = false;
    for b in &args[1..] {
        let brief = l7r_guard::shared::speckit::py_path(b);
        let said = read_strict(&brief).and_then(|text| {
            let (kind, n, detail) = load(&text, &record)?;
            Ok((kind, n, detail, refusal(&brief, &text, &record)?))
        });
        let (kind, n, detail, why) = match said {
            Ok(got) => got,
            Err(why) => return raised("brief-load", out, &why),
        };
        bad |= !why.is_empty();
        let name = l7r_guard::shared::speckit::py_name(&brief);
        let counted = if detail.is_empty() {
            "-".to_owned()
        } else {
            detail.join(", ")
        };
        let kind = if kind.is_empty() { "write" } else { &kind };
        let _ = writeln!(out, "{kind} {n} {name}: {counted}");
        if !why.is_empty() {
            let _ = writeln!(out, "  REFUSED: {why}");
        }
    }
    reply(out, String::new(), i32::from(bad))
}

#[cfg(test)]
mod tests;
