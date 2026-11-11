//! No bundle for a check nothing owes, and the `intro-check` bundle's text (from `bundle_owed.py`, feature 311, plan D4, D9): a bundle for a check and subject the delta does not owe (`make record-owed`) is refused with the owed list, unless a reason of two words or more is given; every question or source bundle's MANIFEST carries `owed-checks:` and one `unit:` line per unit, at the content copied.

use std::collections::HashSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::pages::read_page;
use l7r_guard::shared::escape::enough;

use crate::record::modals;
use crate::record::owed::{read_at, units as owed_units, FAMILIES};
use crate::record::repo::{read_text, Fail};
use crate::record::units::{self, fingerprint, re, Unit, QUESTIONS};

/// The checks a question bundle is owed for; `record-style` is owed by a declared sweep (feature 292), never by a delta.
pub const GATED: [&str; 5] = [
    "intro-check",
    "record-format",
    "quote-check",
    "translation-check",
    "entry-drift",
];
const NEEDS_REASON: &str =
    "needs a REASON - two words and eight characters - so the audit says why";

static NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"^(\d{1,4})"));

/// (the units a bundle carries, its `owed-checks:` value, a refusal or "").
pub type Owed = (Vec<Unit>, String, String);

/// `hm_escape.reason_is_enough`.
#[must_use]
pub fn reason_ok(text: &str) -> bool {
    enough(text)
}

/// A question's number, four digits (`0412`), or `q` as given.
pub fn question_of(q: &str) -> String {
    NUMBER
        .captures(q)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map_or_else(|| q.to_owned(), |m| format!("{:0>4}", m.as_str()))
}

fn unique_checks(rows: &[Unit]) -> String {
    let mut seen: Vec<&str> = Vec::new();
    for u in rows {
        if !seen.contains(&u.check()) {
            seen.push(u.check());
        }
    }
    seen.join(" ")
}

#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "a page's file name as given, as `str.endswith` read it"
)]
/// The owed units for `make check-bundle Q= FOR=`; `every` is the delta's units when the caller already has them.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn owed_for_question(
    root: &Path,
    q: &str,
    for_: &str,
    not_owed_ok: &str,
    every: Option<&[Unit]>,
) -> Result<Owed, Fail> {
    if for_ == "record-style" {
        return Ok((Vec::new(), "record-style".to_owned(), String::new()));
    }
    let qn = question_of(q);
    let drift = matches!(for_, "entry-drift" | "all");
    let scoped = if let Some(rows) = every {
        rows.to_vec()
    } else {
        let families: &[&str] = if drift {
            &["record", "translation", "entry-drift"]
        } else {
            &["record", "translation"]
        };
        owed_units(root, None, None, families, "")?
    };
    let mut rows: Vec<Unit> = scoped
        .into_iter()
        .filter(|u| units::question(u.subject()) == qn || (u.check() == "entry-drift" && drift))
        .collect();
    if q.ends_with(".html") {
        let drawing = q.contains(".drawing.");
        rows.retain(|u| {
            !u.subject().contains('#')
                || u.subject()
                    .split_once('#')
                    .map_or("", |p| p.0)
                    .contains(".drawing")
                    == drawing
        });
    }
    if for_ != "all" {
        rows.retain(|u| u.check() == for_);
    }
    if !rows.is_empty() {
        let checks = unique_checks(&rows);
        return Ok((rows, checks, String::new()));
    }
    if !not_owed_ok.is_empty() {
        if !reason_ok(not_owed_ok) {
            return Ok((
                Vec::new(),
                String::new(),
                format!("NOT_OWED_OK {NEEDS_REASON}"),
            ));
        }
        let checks: Vec<&str> = if for_ == "all" {
            GATED[..4].to_vec()
        } else {
            vec![for_]
        };
        return Ok((
            tree_units(root, &qn, &checks)?,
            checks.join(" "),
            String::new(),
        ));
    }
    let every = owed_units(root, None, None, &FAMILIES, "")?;
    let listing = if every.is_empty() {
        "    (nothing: no record check is owed by this delta)".to_owned()
    } else {
        every
            .iter()
            .map(|u| format!("    {}", u.slug))
            .collect::<Vec<_>>()
            .join("\n")
    };
    let what = if for_ == "all" { "record" } else { for_ };
    Ok((
        Vec::new(),
        String::new(),
        format!(
            "no {what} check is owed on question {qn} by this delta - a bundle for it would re-run a check on words it already passed. What IS owed:\n{listing}\nA check the GM asked for, or a backfill: NOT_OWED_OK=\"<why>\" on the same command."
        ),
    ))
}

/// The units a `NOT_OWED_OK` bundle carries: every unit of those checks on the question, at today's content.
fn tree_units(root: &Path, q: &str, checks: &[&str]) -> Result<Vec<Unit>, Fail> {
    let rec = read_at(root, None, Some(&HashSet::new()))?;
    let mut slugs: Vec<String> = Vec::new();
    for check in checks {
        if matches!(*check, "intro-check" | "record-format") {
            slugs.push(format!("{check}:{q}"));
        } else if *check == "quote-check" {
            for stem in [q.to_owned(), format!("{q}.drawing")] {
                if let Some(notes) = rec.notes.get(&stem) {
                    slugs.extend(notes.iter().map(|(k, _)| format!("quote-check:{stem}#{k}")));
                }
                slugs.push(format!("quote-check:{stem}#unfootnoted"));
            }
        }
    }
    Ok(slugs
        .iter()
        .map(|s| Unit {
            slug: s.clone(),
            occasion: "not owed - a stated reason".to_owned(),
            fingerprint: fingerprint(&rec, s),
            reading: String::new(),
        })
        .collect())
}

/// The owed units for `make check-bundle KEY= [WHOLE=1]`; `every` is the record family's units when the caller has them.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn owed_for_key(
    root: &Path,
    key: &str,
    whole: bool,
    not_owed_ok: &str,
    new: &str,
    every: Option<&[Unit]>,
) -> Result<Owed, Fail> {
    let every = match every {
        Some(rows) => rows.to_vec(),
        None => owed_units(root, None, None, &["record"], "")?,
    };
    let (rows, check): (Vec<Unit>, &str) = if whole {
        let record = read_at(root, None, Some(&HashSet::new()))?;
        let cited = |u: &Unit| {
            let (stem, note) = u.subject().split_once('#').unwrap_or((u.subject(), ""));
            record
                .cites
                .get(stem)
                .and_then(|c| c.get(note))
                .is_some_and(|keys| keys.iter().any(|k| k == key))
        };
        (
            every
                .into_iter()
                .filter(|u| u.check() == "source-reader" && cited(u))
                .collect(),
            "source-reader",
        )
    } else {
        (
            every
                .into_iter()
                .filter(|u| u.check() == "source-applicability" && u.subject() == key)
                .collect(),
            "source-applicability",
        )
    };
    if !rows.is_empty() {
        return Ok((rows, check.to_owned(), String::new()));
    }
    for (name, value) in [
        ("NEW", if whole { new } else { "" }),
        ("NOT_OWED_OK", not_owed_ok),
    ] {
        if !value.is_empty() {
            return Ok(if reason_ok(value) {
                (Vec::new(), check.to_owned(), String::new())
            } else {
                (Vec::new(), String::new(), format!("{name} {NEEDS_REASON}"))
            });
        }
    }
    let hint = if whole {
        "NEW=\"<the claim, in a few words>\" for a read before its note is written; "
    } else {
        ""
    };
    let words = if whole { "notes" } else { "write-up" };
    Ok((
        Vec::new(),
        String::new(),
        format!(
            "no {check} is owed on `{key}` by this delta - its {words} did not change. {hint}NOT_OWED_OK=\"<why>\" for anything else (a source's numbers about to reach a map or a rule)."
        ),
    ))
}

/// The lines the dispatch hook and `make record-checked` read from a MANIFEST.
#[must_use]
pub fn manifest_lines(rows: &[Unit], owed_checks: &str, escape: &str) -> String {
    let mut lines = vec![
        "## Owed (feature 311)".to_owned(),
        String::new(),
        format!("owed-checks: {owed_checks}"),
    ];
    if !escape.is_empty() {
        lines.push(format!("not-owed: {escape}"));
    }
    lines.extend(
        rows.iter()
            .map(|u| format!("unit: {} {}", u.slug, u.fingerprint)),
    );
    lines.extend(
        rows.iter()
            .filter(|u| !u.occasion.is_empty())
            .map(|u| format!("owed: {} - {}", u.slug, u.occasion)),
    );
    lines.join("\n") + "\n"
}

fn note_of(u: &Unit) -> &str {
    u.subject().split_once('#').map_or("", |p| p.1)
}

/// The owed units ONE quote-check batch can answer: its own notes', and the unfootnoted reading the FIRST batch carries.
#[must_use]
pub(crate) fn batch_units(rows: &[Unit], batch: &HashSet<String>, first: bool) -> Vec<Unit> {
    rows.iter()
        .filter(|u| batch.contains(note_of(u)) || (first && note_of(u) == "unfootnoted"))
        .cloned()
        .collect()
}

/// The owed units ONE modal's entry-drift bundle can answer: that modal's own (feature 319, G4).
#[must_use]
pub fn kind_units(rows: &[Unit], key: &str) -> Vec<Unit> {
    rows.iter()
        .filter(|u| u.check() != "entry-drift" || u.subject() == key)
        .cloned()
        .collect()
}

/// Is a quote-check of the page's unfootnoted blocks among the owed units?
#[must_use]
pub fn unfootnoted_owed(rows: &[Unit]) -> bool {
    rows.iter()
        .any(|u| u.check() == "quote-check" && note_of(u) == "unfootnoted")
}

/// The notes a `FOR=quote-check` bundle with no NOTES= is cut to.
#[must_use]
pub fn owed_notes(rows: &[Unit]) -> HashSet<String> {
    rows.iter()
        .filter(|u| u.check() == "quote-check")
        .map(|u| note_of(u).to_owned())
        .filter(|k| k != "unfootnoted")
        .collect()
}

/// (class name, docstring) of every modal, read once a run.
fn modal_docs(root: &Path) -> Result<Vec<(String, String)>, Fail> {
    Ok(modals::modals_now(root, false)?
        .into_iter()
        .map(|m| {
            let cls = m.cls.split_once('.').map_or("", |p| p.1).to_owned();
            (cls, m.doc)
        })
        .collect())
}

/// The `Name:` of every modal whose `Entry:` names this question page.
fn modals_for(docs: &[(String, String)], page: &str) -> Vec<String> {
    let entry = re(&format!(r"(?m)^\s*Entry:.*\b{}", fancy_regex::escape(page)));
    let name = re(r"(?m)^\s*Name:\s*(.+)$");
    docs.iter()
        .filter(|(_, doc)| entry.is_match(doc).unwrap_or(false))
        .map(|(cls, doc)| {
            let named = name
                .captures(doc)
                .ok()
                .flatten()
                .and_then(|c| c.get(1))
                .map(|m| {
                    m.as_str()
                        .trim_matches(l7r_guard::shared::py_text::is_space)
                        .to_owned()
                });
            format!("- {}", named.unwrap_or_else(|| cls.clone()))
        })
        .collect()
}

/// A page as its reader meets it, one block a line, the intro flagged.
fn page_text(text: &str) -> String {
    let p = read_page(text);
    let mut lines = vec![format!("# {}", p.heading)];
    lines.extend(
        p.blocks
            .iter()
            .map(|b| format!("{}{}", if b.intro { "[INTRO] " } else { "" }, b.words)),
    );
    lines.join("\n")
}

#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the record's page names, as the Python's glob matched them"
)]
/// One question's part of an intro-check bundle: its research page whole, its drawing page, and the map elements written from it.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn intro_bundle_text(
    root: &Path,
    q: &str,
    docs: &mut Option<Vec<(String, String)>>,
) -> Result<String, Fail> {
    let qn = question_of(q);
    let qdir = root.join(QUESTIONS);
    let prefix = format!("{qn}-");
    let mut research: Vec<String> = std::fs::read_dir(&qdir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| {
            n.starts_with(&prefix)
                && n.ends_with(".html")
                && units::stem_of(n).is_some()
                && !n.contains(".drawing.")
        })
        .collect();
    research.sort();
    let Some(page) = research.first() else {
        return Ok(String::new());
    };
    let drawing = qdir.join(format!(
        "{}.drawing.html",
        &page[..page.len() - ".html".len()]
    ));
    let mut parts = vec![
        format!("=== QUESTION {qn} - origin `{QUESTIONS}/{page}`"),
        String::new(),
        "--- the research page".to_owned(),
        page_text(&read_text(&qdir.join(page))?),
    ];
    if drawing.is_file() {
        parts.extend([
            String::new(),
            "--- how our maps draw it (its drawing page)".to_owned(),
            page_text(&read_text(&drawing)?),
        ]);
    }
    if docs.is_none() {
        *docs = Some(modal_docs(root)?);
    }
    let found = modals_for(docs.as_deref().unwrap_or_default(), page);
    parts.extend([
        String::new(),
        "--- the map elements written from it".to_owned(),
    ]);
    if found.is_empty() {
        parts.push("- (none: no modal's Entry names this question)".to_owned());
    } else {
        parts.extend(found);
    }
    parts.push(String::new());
    Ok(parts.join("\n"))
}

#[cfg(test)]
mod tests;
