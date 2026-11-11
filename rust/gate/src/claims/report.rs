//! The report and the push's reading of the index (`scripts/record/claims.py`'s `report`, `open_findings`, `classify`, `base_tree` and
//! the form check, ported by feature 449 T82): counts by verdict, the open findings, and whether a finding is introduced, pre-existing or
//! carried against the merge base with origin/main.

use std::collections::{BTreeMap, HashMap, HashSet};
use std::io::Write as _;
use std::path::Path;
use std::process::{Command, Stdio};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use super::grammar::GRAMMAR;
use super::index::{
    field, is, live_rows, load_map, owed, research_fp, Cur, Index, Store, QUESTIONS,
};
use super::reply::{FINDINGS, VERDICTS};
use super::scope::{all_units, Reader};
use super::units::Pair;
use crate::record::repo::{fail, git, Fail};
use crate::record::units::re;

/// A constant's name as a decision names it.
static CONSTANT: LazyLock<Regex> = LazyLock::new(|| re(r"\b[A-Z][A-Z0-9_]{2,}\b"));
static CONSTANT_WHOLE: LazyLock<Regex> = LazyLock::new(|| re(r"\A(?:\b[A-Z][A-Z0-9_]{2,}\b)\z"));
/// What the base read needs: the engine, the procedure documents and the questions.
pub(crate) const BASE_PATHS: [&str; 4] = ["l7r", "docs/buildings.md", "docs/buildings", QUESTIONS];

/// Every coverage failure: a unit with no claim own or inherited, a claim that does not parse, a pointer to no question file.
pub(crate) fn coverage(units: &[Pair], questions: &HashSet<String>) -> Vec<String> {
    let mut problems = Vec::new();
    let mut seen: HashSet<(String, String)> = HashSet::new();
    for (unit, module_errors) in units {
        let place = format!("{}:{} {}", unit.path, unit.lineno, unit.qualname);
        for err in module_errors {
            if seen.insert((unit.path.clone(), err.clone())) {
                problems.push(format!("{} module docstring: {err}", unit.path));
            }
        }
        problems.extend(unit.errors.iter().map(|e| format!("{place}: {e}")));
        if unit.claims.is_empty() && unit.errors.is_empty() {
            let what = if unit.kind == "section" {
                "a `<!-- Research: <label> - <backing> -->` comment"
            } else {
                "a `Research:` claim (own, or in its module docstring)"
            };
            problems.push(format!("{place}: no claim - add {what}"));
        }
        for claim in &unit.claims {
            for ptr in &claim.pointers {
                if !questions.contains(super::index::page_name(ptr)) {
                    problems.push(format!("{place}: `{ptr}` names no question file (find it with a glob on its heading id; `make fragment-move` renames)"));
                }
            }
        }
    }
    problems
}

/// The question files' names under `root`.
pub(crate) fn question_names(root: &Path) -> HashSet<String> {
    std::fs::read_dir(root.join(QUESTIONS))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| n.ends_with(".html"))
        .collect()
}

/// Each form problem whose file changed since `base`; a form is fixed, never carried.
pub(crate) fn delta_form_problems(root: &Path, pairs: &[Pair]) -> Vec<String> {
    let diff = git(root, &["diff", "--name-only", "origin/main...HEAD"]);
    let changed: HashSet<&str> = diff.split_whitespace().collect();
    if changed.is_empty() {
        return Vec::new();
    }
    coverage(pairs, &question_names(root))
        .into_iter()
        .filter(|x| changed.contains(x.split_once(':').map_or(x.as_str(), |p| p.0)))
        .map(|x| format!("{x} - the claims grammar: {GRAMMAR}"))
        .collect()
}

/// The units and single claims whose findings are DEFERRED (`dev/claims-deferred.json`), or none.
pub(crate) fn load_deferred(path: &Path) -> Result<HashSet<String>, Fail> {
    let doc = Value::Object(load_map(path)?);
    let mut out = HashSet::new();
    for part in ["units", "keys"] {
        out.extend(
            doc.get(part)
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .filter_map(|v| v.as_str().map(str::to_owned)),
        );
    }
    Ok(out)
}

/// A finding's verdict as the report shows it: DEFERRED where its unit is deferred, else its own.
pub(crate) fn shown(key: &str, verdict: &str, deferred: &HashSet<String>) -> String {
    let unit = key.rsplit_once('#').map_or(key, |p| p.0);
    if FINDINGS.contains(&verdict) && (deferred.contains(key) || deferred.contains(unit)) {
        "DEFERRED".to_owned()
    } else {
        verdict.to_owned()
    }
}

/// A row's verdict: the failure Python's `v["verdict"]` raises where it has none.
pub(crate) fn verdict_of<'a>(v: &'a Value) -> Result<&'a str, Fail> {
    match v.get("verdict") {
        Some(Value::String(s)) => Ok(s),
        Some(other) => Err(format!("TypeError: a verdict {other}")),
        None => Err("KeyError: 'verdict'".to_owned()),
    }
}

/// (verdict as shown, key, note) for every finding the report lists by default, sorted by key.
pub(crate) fn open_findings(
    rows: &Index,
    deferred: &HashSet<String>,
) -> Result<Vec<(String, String, String)>, Fail> {
    let mut keys: Vec<&String> = rows.keys().collect();
    keys.sort();
    let claimed = in_step_constants(rows);
    let mut out = Vec::new();
    for k in keys {
        let v = &rows[k.as_str()];
        let verdict = shown(k, verdict_of(v)?, deferred);
        if verdict == "IN-STEP"
            || verdict == "DEFERRED"
            || (verdict == "UNCLAIMED" && names_claimed(k, &claimed))
        {
            continue;
        }
        out.push((verdict, k.clone(), field(v, "note").to_owned()));
    }
    Ok(out)
}

/// (path, NAME) of each constant whose every claim stands IN-STEP.
pub(crate) fn in_step_constants(rows: &Index) -> HashSet<(String, String)> {
    let mut seen: HashMap<(String, String), bool> = HashMap::new();
    for (k, v) in rows {
        let (path, rest) = k.split_once("::").unwrap_or((k, ""));
        let name = rest.split_once('#').map_or(rest, |p| p.0);
        if CONSTANT_WHOLE.is_match(name).unwrap_or(false) && !is(v, "verdict", "UNCLAIMED") {
            let e = seen
                .entry((path.to_owned(), name.to_owned()))
                .or_insert(true);
            *e = *e && is(v, "verdict", "IN-STEP");
        }
    }
    seen.into_iter()
        .filter(|(_, ok)| *ok)
        .map(|(k, _)| k)
        .collect()
}

/// Whether an UNCLAIMED decision names a constant of its own file whose claims stand IN-STEP.
pub(crate) fn names_claimed(key: &str, claimed: &HashSet<(String, String)>) -> bool {
    let (path, rest) = key.split_once("::").unwrap_or((key, ""));
    let decision = rest.split_once('#').map_or("", |p| p.1);
    CONSTANT
        .find_iter(decision)
        .flatten()
        .any(|n| claimed.contains(&(path.to_owned(), n.as_str().to_owned())))
}

/// `f"{text:<14}"`.
pub(crate) fn padded(text: &str) -> String {
    let n = text.chars().count();
    format!("{text}{}", " ".repeat(14usize.saturating_sub(n)))
}

/// Counts by verdict, the owed count, then every finding and every UNRESEARCHED claim (spec FR-011).
pub(crate) fn report(
    cur: &Cur,
    index: &Index,
    qdir: &Path,
    store: &Store,
    deferred: &HashSet<String>,
    show_deferred: bool,
) -> Result<String, Fail> {
    let rows: Index = live_rows(cur, index)
        .into_iter()
        .filter(|(_, v)| v.get("verdict").is_some())
        .collect();
    let due = owed(cur, index, Some(qdir), Some(store))?;
    let mut counts: HashMap<String, usize> = HashMap::new();
    for (k, v) in &rows {
        *counts
            .entry(shown(k, verdict_of(v)?, deferred))
            .or_default() += 1;
    }
    let count = |v: &str| counts.get(v).copied().unwrap_or(0);
    let tally: Vec<String> = VERDICTS
        .iter()
        .chain(&["DEFERRED"])
        .filter(|v| count(v) > 0)
        .map(|v| format!("{v} {}", count(v)))
        .collect();
    let tally = if tally.is_empty() {
        "no verdicts yet".to_owned()
    } else {
        tally.join(", ")
    };
    let mut lines = vec![format!(
        "claims: {} in scope; {tally}; owed {}",
        cur.len(),
        due.len()
    )];
    if show_deferred {
        let mut keys: Vec<&String> = rows.keys().collect();
        keys.sort();
        for key in keys {
            let v = &rows[key.as_str()];
            let verdict = shown(key, verdict_of(v)?, deferred);
            if verdict != "IN-STEP" {
                lines.push(format!(
                    "  {} {key} - {}",
                    padded(&verdict),
                    field(v, "note")
                ));
            }
        }
    } else {
        for (verdict, key, note) in open_findings(&rows, deferred)? {
            lines.push(format!("  {} {key} - {note}", padded(&verdict)));
        }
    }
    if count("DEFERRED") > 0 && !show_deferred {
        lines.push(format!(
            "({} DEFERRED findings not listed: make claims-report ALL=1 lists them)",
            count("DEFERRED")
        ));
    }
    let mut unres: Vec<&String> = cur
        .iter()
        .filter(|r| r.claim.backing == "UNRESEARCHED")
        .map(|r| &r.key)
        .collect();
    unres.sort();
    if !unres.is_empty() {
        lines.push(format!(
            "UNRESEARCHED claims (the open research): {}",
            unres.len()
        ));
        lines.extend(unres.iter().map(|k| format!("  {k}")));
    }
    Ok(lines.join("\n"))
}

/// The engine, procedures and questions at `base`, extracted under `into`.
pub(crate) fn base_tree(root: &Path, base: &str, into: &Path) -> Result<(), Fail> {
    let present: Vec<&str> = BASE_PATHS
        .iter()
        .copied()
        .filter(|p| {
            Command::new("git")
                .arg("-C")
                .arg(root)
                .args(["cat-file", "-e", &format!("{base}:{p}")])
                .stderr(Stdio::null())
                .status()
                .is_ok_and(|s| s.success())
        })
        .collect();
    if !present.is_empty() {
        let archive = Command::new("git")
            .arg("-C")
            .arg(root)
            .args(["archive", "--format=tar", base, "--"])
            .args(&present)
            .output()
            .map_err(fail)?;
        if !archive.status.success() {
            return Err(format!(
                "RuntimeError: claims: the base tree could not be read at {base}: {}",
                l7r_guard::shared::py_text::strip(&String::from_utf8_lossy(&archive.stderr))
            ));
        }
        let mut tar = Command::new("tar")
            .arg("-x")
            .arg("-C")
            .arg(into)
            .stdin(Stdio::piped())
            .spawn()
            .map_err(fail)?;
        if let Some(mut pipe) = tar.stdin.take() {
            pipe.write_all(&archive.stdout).map_err(fail)?;
        }
        tar.wait().map_err(fail)?;
    }
    std::fs::create_dir_all(into.join("l7r/diagram/hamletgen")).map_err(fail)
}

/// uid -> core for every unit at a tree, claimed or not: the base the push compares with.
pub(crate) fn base_cores(
    reader: &mut Reader,
    skill: &Path,
) -> Result<HashMap<String, String>, Fail> {
    Ok(all_units(reader, skill, true, true)?
        .into_iter()
        .map(|(u, _)| (u.uid(), u.core))
        .collect())
}

/// What `classify` judges against: the merge base's index, cores and questions, the deferred and the answered.
pub(crate) struct Base<'a> {
    pub(crate) index: &'a Index,
    pub(crate) cores: &'a HashMap<String, String>,
    pub(crate) qdir: &'a Path,
    pub(crate) deferred: &'a HashSet<String>,
    pub(crate) answered: &'a HashSet<String>,
}

/// (introduced, pre-existing, carried) findings (spec FR-010; carried: 385 FR-013).
pub(crate) fn classify(
    cur: &Cur,
    index: &Index,
    base: &Base,
) -> Result<(Vec<String>, Vec<String>, Vec<(String, String)>), Fail> {
    let head_uids = cur.uids();
    let gone_cores: HashSet<&String> = base
        .cores
        .iter()
        .filter(|(u, _)| !head_uids.contains(*u))
        .map(|(_, c)| c)
        .collect();
    let mut memo = HashMap::new();
    let (mut intro, mut pre, mut carried) = (Vec::new(), Vec::new(), Vec::new());
    let rows: BTreeMap<String, Value> = live_rows(cur, index).into_iter().collect();
    for (key, v) in &rows {
        let verdict = verdict_of(v)?;
        if !FINDINGS.contains(&verdict)
            || base.answered.contains(key)
            || shown(key, verdict, base.deferred) == "DEFERRED"
        {
            continue;
        }
        let was = base.index.get(key);
        let line = format!("{} {key} - {}", padded(verdict), field(v, "note"));
        if was
            .and_then(|w| w.get("verdict"))
            .and_then(Value::as_str)
            .is_some_and(|w| FINDINGS.contains(&w))
        {
            pre.push(line);
            continue;
        }
        let same_claim = was.is_some_and(|w| {
            super::index::truthy(w.get("claim")) && w.get("claim") == v.get("claim")
        });
        if super::index::truthy(v.get("outside")) && (verdict == "UNCLAIMED" || same_claim) {
            carried.push((key.clone(), line));
            continue;
        }
        let uid = key.rsplit_once('#').map_or(key.as_str(), |p| p.0);
        let core = field(v, "core");
        let row = cur.get(key);
        if let Some(was) = was {
            if row.is_some_and(|r| is(was, "code", &r.code)) {
                carried.push((key.clone(), line));
            } else {
                intro.push(line);
            }
            continue;
        }
        let research_changed = match row {
            Some(r) => research_fp(&r.claim.pointers, base.qdir, &mut memo)? != r.research,
            None => false,
        };
        let same_core = base.cores.get(uid).is_some_and(|c| c == core);
        if same_core && research_changed {
            carried.push((key.clone(), line));
        } else {
            let code_changed = !(same_core || gone_cores.contains(&core.to_owned()));
            if code_changed || research_changed {
                intro.push(line);
            } else {
                pre.push(line);
            }
        }
    }
    Ok((intro, pre, carried))
}

/// A notice for each NEW unit whose only claim is its module's inherited `NONE` (feature 405 T37, D11).
pub(crate) fn inherited_none(cur: &Cur, due: &[(String, String)]) -> Vec<String> {
    due.iter()
        .filter(|(k, why)| why == "new" && cur.get(k).is_some_and(|r| r.unit.inherited && r.claim.backing == "NONE"))
        .map(|(k, _)| {
            let uid = cur.get(k).map(super::index::Row::uid).unwrap_or_default();
            format!("claims-owed: {uid} is new and carries only its module's NONE - if it decides anything about the place, give it its own `Research:` line before the check")
        })
        .collect()
}

/// The claim keys a `sep`-separated `text` names, a label's own separator joined back into the longest run that is a known key.
pub(crate) fn split_keys(text: &str, sep: char, known: &dyn Fn(&str) -> bool) -> Vec<String> {
    let parts: Vec<&str> = text.split(sep).collect();
    let mut keys = Vec::new();
    let mut i = 0;
    let joined = |a: usize, b: usize| parts[a..b].join(&sep.to_string());
    while i < parts.len() {
        let j = (i + 1..=parts.len())
            .rev()
            .find(|&j| known(l7r_guard::shared::py_text::strip(&joined(i, j))))
            .unwrap_or(i + 1);
        let key = joined(i, j);
        let key = l7r_guard::shared::py_text::strip(&key);
        if !key.is_empty() {
            keys.push(key.to_owned());
        }
        i = j;
    }
    keys
}

#[cfg(test)]
mod tests;
