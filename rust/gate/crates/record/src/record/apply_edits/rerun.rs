//! A re-run's wording EDITs on text answered before, held and listed (feature 451 T232); its factual ones apply (451 T188). Measured 2026-11-25: on one fingerprint the
//! verdict counts agreed in 6 of 6 re-runs, and the two answers that differed (sheet/guest-quarters' gaps, 2026-11-24, and
//! sheet/barracks' form on the measurement's re-run) each paired an earlier round that judged only a change with a later one that
//! judged more. A re-run's new wording finding is therefore on text an earlier answer stood on: it is listed in the feature's `noted.jsonl`
//! for the next session, not applied mid-landing, where applying it re-owes the checks after it. A research page's record checks are
//! held the same way (451 T249): their re-runs applied and re-owed the checks after them, as the pop-ups' did before T232.

use std::collections::HashSet;
use std::fmt::Write as _;

use l7r_shared::checks::reply::factual;
use l7r_shared::env::Rooted;
use l7r_shared::escape::enough;
use serde_json::json;

use super::Block;
use crate::record::owed::{self, answers};

/// Where a pop-up's text lives: its unit is the path between these.
const MODALS: &str = "l7r/diagram/interactive/assets/modals/";

/// The subject of the unit an EDIT's file is part of, or none: a pop-up's unit, or a research question's number (451 T249) - the
/// subject of its record-format and intro-check units, the record's wording checks, each of which reads the whole question (its
/// page, notes and drawing; `units::fingerprint`). A source write-up under `research/sources/` is no question's unit, and a
/// factual check's EDIT never reaches the unit (quote-check's and translation-check's units are per note), so neither is held.
fn unit_of(path: &str) -> Option<String> {
    let path = path.trim_matches('`');
    if let Some(unit) = path
        .strip_prefix(MODALS)
        .and_then(|p| p.strip_suffix(".md"))
    {
        return Some(unit.to_owned());
    }
    super::QUESTION
        .captures(path)
        .ok()
        .flatten()
        .map(|c| c[1].to_owned())
}

/// One held EDIT: its number, the unit, the result the unit held before the re-run, and the EDIT's file and words.
pub(super) struct Held {
    n: usize,
    slug: String,
    was: String,
    path: String,
    old: String,
    new: String,
}

/// Each wording EDIT not skipped whose pop-up or research question every check of the reply answered before on the text it holds
/// now (a research page's since 451 T249).
pub(super) fn held(
    root: &Rooted,
    report: &str,
    found: &[Block],
    skip: &HashSet<usize>,
) -> Vec<Held> {
    let checks = owed::reply_checks(report);
    let store = answers::store_in(root);
    let mut out = Vec::new();
    for b in found {
        let Block::Edit(e) = b else { continue };
        let Some(unit) = unit_of(&e.path).filter(|_| !skip.contains(&e.n)) else {
            continue;
        };
        // a factual EDIT applies and cascades as a first round's would (451 T188, the GM: only factual findings cascade); and only
        // where every check of the reply re-ran at this text, so a first round's EDIT in the same reply is never held
        if checks.is_empty() || checks.iter().any(|c| factual(c, &e.category)) {
            continue;
        }
        let marks: Vec<(String, Option<String>)> = checks
            .iter()
            .map(|c| {
                let slug = format!("{c}:{unit}");
                let was = answers::rerun_at(&store, &slug);
                (slug, was)
            })
            .collect();
        if let [(slug, Some(was)), ..] = marks.as_slice() {
            if marks.iter().all(|(_, w)| w.is_some()) {
                out.push(Held {
                    n: e.n,
                    slug: slug.clone(),
                    was: was.clone(),
                    path: e.path.clone(),
                    old: e.old.clone(),
                    new: e.new.clone(),
                });
            }
        }
    }
    out
}

/// The held EDITs kept as listed notes and said, their numbers added to `skip`; or, with a reason of two words or more, let through
/// and logged. Err is the refusal of a reason too short.
pub(super) fn hold(
    root: &Rooted,
    skip: &mut HashSet<usize>,
    held: &[Held],
    reason: &str,
) -> Result<String, String> {
    if held.is_empty() {
        return Ok(String::new());
    }
    let units: Vec<&str> = held.iter().map(|h| h.slug.as_str()).collect();
    if !reason.is_empty() {
        if !enough(reason) {
            return Err("apply-edits: RERUN_OK needs a reason of two words or more - it is logged in dev/bypass-log/".to_owned());
        }
        owed::answers::bypass_log(
            root,
            "apply-edits",
            &format!("a re-run's EDITs applied on {}: {reason}", units.join(" ")),
        )
        .map_err(|e| e.to_string())?;
        return Ok(format!(
            "apply-edits: RERUN_OK - a re-run's EDITs applied on {} (451 T232)\n",
            units.join(" ")
        ));
    }
    let mut rows = Vec::new();
    let mut said = String::new();
    for Held {
        n,
        slug,
        was,
        path,
        old,
        new,
    } in held
    {
        skip.insert(*n);
        rows.push(json!({"check": slug.split(':').next().unwrap_or(""), "file": path, "block": format!("EDIT {n}"), "units": slug, "note": format!("a re-run's EDIT on text answered before (was: {was}): {old:?} -> {new:?}")}));
        let _ = writeln!(said, "apply-edits: held EDIT {n} ({path}) - {slug} was answered at this text before (was: {was})");
    }
    let kept = answers::keep_noted_rows(root, &rows).map_err(|e| e.to_string())?;
    let _ = writeln!(said, "apply-edits: a re-run's new wording finding on text nothing changed is listed, not applied, kept in {} (451 T232); fix it as its own task, or RERUN_OK=\"<reason, two words or more>\" to apply it now", kept.as_deref().unwrap_or("no file"));
    Ok(said)
}

/// The rows `hold` keeps, read back (for its tests).
#[cfg(test)]
pub(super) fn kept(root: &std::path::Path) -> Vec<serde_json::Value> {
    let p = root.join("specs/_unfiled/noted.jsonl");
    std::fs::read_to_string(p)
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect()
}
