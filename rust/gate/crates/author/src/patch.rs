//! `l7r-gate patch <file>` - anchored edits to one file, EACH EDIT ITS OWN WRITE (feature 236, the GM's item 1); ported whole from
//! `scripts/patch.py` by feature 449 T135 (`ask:449-phase3-remainder`). On stdin, a JSON list of `[anchor, replacement]` pairs or of
//! `{"anchor": ..., "replacement": ...}` objects; `--selftest` runs its own cases.
//!
//! WHY THIS EXISTS. `Edit` is still the default and this does not replace it (docs/efficiency-tooling.md). This is for the sweep that
//! genuinely must be scripted - the same mechanical change over many files - and it exists because the ad-hoc form of that script cost
//! a whole session's worth of rework three times in one day: a patch script held every edit in memory and wrote the file at the end, so
//! ONE anchor that no longer matched (usually a sentence somebody had already reflowed) discarded the substantive edits beside it, and
//! nothing was reported as lost. So the two properties here are the whole point:
//!
//!   1. EACH EDIT IS ITS OWN WRITE. An anchor that matches zero times, or more than once, is REPORTED and SKIPPED, and every other edit
//!      in the batch still lands. A batch is not a transaction: these edits are independent by construction.
//!   2. ANCHORS MATCH WHITESPACE-INSENSITIVELY. Four of the six anchor misses in the record spanned a LINE WRAP
//!      (`specs/236-catch-mistakes-early-and-cheaply/research.md` R7). Exact matching leaves the commonest miss in place.
//!
//! An anchor that matches MORE than once is skipped rather than applied to the first hit: which one the caller meant is exactly the
//! thing the tool cannot know, and guessing writes the wrong place silently.

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::Reply;
use l7r_guard::shared::py_text::{is_space, repr, split, SPACE_CLASS};
use l7r_guard::shared::pyjson::py_str;
use serde_json::Value;

use crate::{raised, read_strict, reply};

static INDENT: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[ \t]*").unwrap_or_else(|e| unreachable!("{e}")));

/// `anchor` as a pattern in which any run of whitespace matches any other run. A line wrap is whitespace, so an anchor copied from
/// rendered prose matches the file's own wrapped copy of it; every other character is escaped, so `(`, `*` or `.` match literally.
fn anchor_regex(anchor: &str) -> Regex {
    let words: Vec<String> = split(anchor)
        .into_iter()
        .map(|w| fancy_regex::escape(w).into_owned())
        .collect();
    // every word escaped: the pattern always compiles
    Regex::new(&words.join(&format!("[{SPACE_CLASS}]+"))).unwrap_or_else(|e| unreachable!("{e}"))
}

/// `replacement`'s continuation lines given the indent the matched text stood at.
///
/// THE BUG THIS FIXES, from the session that motivated the tool: an anchor whose match began at a WORD rather than at the start of a
/// line, replaced by multi-line text, produced continuation lines flush against the left margin inside an indented block. The first
/// line is not touched (it continues whatever is already on that line); a continuation line that carries its own leading whitespace is
/// not touched either, because the caller has then said what it wants.
fn reindent(replacement: &str, prefix: &str) -> String {
    if prefix.is_empty() || !replacement.contains('\n') {
        return replacement.to_owned();
    }
    let mut lines = replacement.split('\n');
    let mut out = lines.next().unwrap_or("").to_owned();
    for line in lines {
        out.push('\n');
        if !line.is_empty() && !line.starts_with(is_space) {
            out.push_str(prefix);
        }
        out.push_str(line);
    }
    out
}

/// `repr()` of what `json.loads` made: a string quoted, a list or dict as `str()` prints it (its strings quoted already).
fn py_repr(v: &Value) -> String {
    match v {
        Value::String(s) => repr(s),
        other => py_str(other),
    }
}

/// One edit as the payload gave it: the anchor and the replacement, each whatever JSON value it was.
type Edit = (Value, Value);

/// What `apply_edits` raised on a value that is not text, as its traceback's last line named it.
fn not_text(v: &Value, what: &str) -> String {
    format!("TypeError: the {what} {} is not text", py_repr(v))
}

/// Each edit applied to `path` independently: the report's lines and how many were skipped, or what raised (an edit before it is
/// already written, as the Python's was).
fn apply_edits(path: &Path, edits: &[Edit], report: &mut Vec<String>) -> Result<usize, String> {
    let mut skipped = 0;
    for (anchor, replacement) in edits {
        // re-read per edit: an earlier edit may have moved this one
        let text = read_strict(path)?;
        let Value::String(anchor) = anchor else {
            return Err(not_text(anchor, "anchor"));
        };
        let hits: Vec<(usize, usize)> = anchor_regex(anchor)
            .find_iter(&text)
            .flatten()
            .map(|m| (m.start(), m.end()))
            .collect();
        let label: String = split(anchor).join(" ").chars().take(60).collect();
        let [(start, end)] = hits[..] else {
            skipped += 1;
            report.push(format!("SKIPPED ({} matches): {label}", hits.len()));
            continue;
        };
        let Value::String(replacement) = replacement else {
            return Err(not_text(replacement, "replacement"));
        };
        let line_start = text[..start].rfind('\n').map_or(0, |i| i + 1);
        // the LINE'S OWN indent, not everything before the match: an anchor starting at a word inside `    - a point ...` must continue
        // at the block's indent, and the earlier form (only a wholly blank prefix counted) left exactly that case flush to the margin
        let before = &text[line_start..start];
        let indent = INDENT
            .find(before)
            .ok()
            .flatten()
            .map_or("", |m| m.as_str());
        let mut body = reindent(replacement, indent);
        // AN ANCHOR IGNORES ITS OWN LEADING WHITESPACE, so a caller that copied an indented line into BOTH the anchor and the replacement
        // would have that indent applied twice: the match begins at the first non-space character, and the replacement carries the
        // indent again. Found using it on `hm_make.py` an hour after writing it: the line came out at sixteen spaces.
        if !indent.is_empty() && before == indent {
            body = body.trim_start_matches([' ', '\t']).to_owned();
        }
        std::fs::write(path, format!("{}{body}{}", &text[..start], &text[end..]))
            .map_err(|e| format!("{}: {e}", path.display()))?;
        report.push(format!("applied: {label}"));
    }
    Ok(skipped)
}

/// The `(anchor, replacement)` pairs of the parsed payload, in either shape it arrives in.
///
/// A LIST OF PAIRS is the documented form. A list of OBJECTS keyed `anchor`/`replacement` is what a caller writes when it thinks in this
/// tool's own names - and the first version unpacked those into the KEYS, so it searched each file for the literal text "anchor",
/// printed `SKIPPED (0 matches): anchor` once per edit and changed nothing, which is indistinguishable from a batch of stale anchors
/// (measured 2026-09-13: twelve edits reported as missed while the file was untouched). Anything else is refused by name.
fn read_edits(data: &Value) -> Result<Vec<Edit>, String> {
    let items = match data {
        Value::Array(items) => items.clone(),
        other => vec![other.clone()],
    };
    let mut out = Vec::new();
    for item in &items {
        match item {
            Value::Object(m) => {
                if m.len() != 2 || !m.contains_key("anchor") || !m.contains_key("replacement") {
                    return Err(format!("_patch: an edit object carries exactly `anchor` and `replacement`: {}", py_repr(item)));
                }
                out.push((m["anchor"].clone(), m["replacement"].clone()));
            }
            Value::Array(pair) if pair.len() == 2 && pair.iter().all(Value::is_string) => {
                out.push((pair[0].clone(), pair[1].clone()));
            }
            _ => {
                return Err(format!(
                    "_patch: an edit is [anchor, replacement] or {{\"anchor\": ..., \"replacement\": ...}}: {}",
                    py_repr(item)
                ))
            }
        }
    }
    Ok(out)
}

/// One self-test case on the scratch file `f`: `text` written, `edits` applied, the file and the skipped count compared with `want` and
/// `skips`; a case that fails names itself.
fn case(
    f: &Path,
    name: &str,
    text: &str,
    edits: &[(&str, &str)],
    want: (&str, usize),
) -> Result<(), String> {
    std::fs::write(f, text).map_err(|e| format!("{}: {e}", f.display()))?;
    let edits: Vec<Edit> = edits
        .iter()
        .map(|(a, r)| (Value::from(*a), Value::from(*r)))
        .collect();
    let mut report = Vec::new();
    let skipped = apply_edits(f, &edits, &mut report)?;
    let got = read_strict(f)?;
    if (got.as_str(), skipped) == want {
        Ok(())
    } else {
        Err(format!(
            "_patch selftest: {name}: {got:?} with {skipped} skipped ({report:?})"
        ))
    }
}

/// A self-test case: its name, the file's text, the edits, and the text and skipped count it must come to.
type Case<'a> = (&'a str, &'a str, &'a [(&'a str, &'a str)], (&'a str, usize));

/// The tool's own cases, on a scratch file in `dir`: the motivating batch (the middle anchor gone, the other two must still land), a
/// wrapped anchor, a doubled one, a word-start match's continuation indent and an indent carried twice.
fn selftest(dir: &Path) -> Result<(), String> {
    let f = dir.join("x.md");
    let cases: [Case; 5] = [
        (
            "one stale anchor",
            "alpha one\nbeta two\ngamma three\n",
            &[
                ("alpha one", "ALPHA"),
                ("nowhere at all", "X"),
                ("gamma three", "GAMMA"),
            ],
            ("ALPHA\nbeta two\nGAMMA\n", 1),
        ),
        (
            "a wrapped anchor",
            "the sections and keys the new text\nwas written from stay put\n",
            &[("keys the new text was written from", "keys it came from")],
            ("the sections and keys it came from stay put\n", 0),
        ),
        (
            "a doubled anchor",
            "same line\nsame line\n",
            &[("same line", "different")],
            ("same line\nsame line\n", 1),
        ),
        (
            "a word-start match",
            "    - a point that needs more\n",
            &[("a point that needs more", "a point\nand another")],
            ("    - a point\n    and another\n", 0),
        ),
        (
            "an indent carried twice",
            "def x():\n    if a and b:\n        pass\n",
            &[("    if a and b:", "    if a and c:")],
            ("def x():\n    if a and c:\n        pass\n", 0),
        ),
    ];
    for (name, text, edits, want) in cases {
        case(&f, name, text, edits, want)?;
    }
    Ok(())
}

/// `l7r-gate patch <file>` with the edits on `stdin`, or `--selftest` in `scratch`.
#[must_use]
pub fn cli(args: &[String], stdin: &mut dyn std::io::Read, scratch: &Path) -> Reply {
    if args.iter().any(|a| a == "--selftest") {
        return match selftest(scratch) {
            Ok(()) => reply("_patch selftest ok\n".to_owned(), String::new(), 0),
            Err(why) => raised("patch", String::new(), "", &why),
        };
    }
    if args.len() != 1 {
        return reply(
            String::new(),
            "usage: l7r-gate patch <file>   # on stdin, a JSON list of [anchor, replacement] pairs (or of {\"anchor\": ..., \"replacement\": ...} objects)\n".to_owned(),
            2,
        );
    }
    let mut input = String::new();
    // stdin not UTF-8 is the Python's `UnicodeDecodeError`, its message left to the traceback's last line
    let data = stdin
        .read_to_string(&mut input)
        .map_err(|_| "UnicodeDecodeError: stdin is not UTF-8".to_owned())
        .and_then(|_| {
            serde_json::from_str::<Value>(&input)
                .map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))
        });
    let edits = match data {
        Ok(d) => match read_edits(&d) {
            Ok(e) => e,
            // `raise SystemExit(message)`: the message on stderr, exit 1
            Err(why) => return reply(String::new(), format!("{why}\n"), 1),
        },
        Err(why) => return raised("patch", String::new(), "", &why),
    };
    let mut report = Vec::new();
    match apply_edits(Path::new(&args[0]), &edits, &mut report) {
        Ok(skipped) => {
            let mut out = report.join("\n");
            let _ = writeln!(out);
            reply(out, String::new(), i32::from(skipped > 0))
        }
        Err(why) => raised("patch", String::new(), "", &why),
    }
}

#[cfg(test)]
mod tests;
