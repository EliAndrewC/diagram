//! A claims check's REPLY, read and recorded (`scripts/record/claims_reply.py`, ported by feature 449 T82): the verdict lines parsed, a
//! reply's elided page names restored, and the index rows it writes.

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use l7r_guard::guards::house_style_hooks::americanize;
use l7r_guard::shared::py_text::strip;
use serde_json::{json, Map, Value};

use super::index::{field, is, Index};
use crate::record::units::re;

pub(crate) const FINDINGS: [&str; 5] = [
    "DRIFTED",
    "NEEDS-RESEARCH",
    "MISLABELED",
    "UNCLAIMED",
    "CANNOT-TELL",
];
pub(crate) const VERDICTS: [&str; 6] = [
    "IN-STEP",
    "DRIFTED",
    "NEEDS-RESEARCH",
    "MISLABELED",
    "UNCLAIMED",
    "CANNOT-TELL",
];
pub(crate) const OUTSIDE: &str = "[outside the change]";

/// A verdict line, read where a reply sets the verdict off with a dash or closes it with a colon (feature 417 T50).
pub(crate) static VERDICT: LazyLock<Regex> = LazyLock::new(|| {
    re(r"\AVERDICT\s+(\S.*?)\s+(?:-\s+)?(IN-STEP|DRIFTED|NEEDS-RESEARCH|MISLABELED|UNCLAIMED|CANNOT-TELL)(?:\s+-\s+|:\s+)(.*)\z")
});
static UNCLAIMED: LazyLock<Regex> = LazyLock::new(|| re(r"\AUNCLAIMED\s+(\S+?::\S.*?)\s+-\s+(.*)\z"));
static RESTS: LazyLock<Regex> = LazyLock::new(|| re(r"\[(§[^\]]*)\]\s*\z"));
static ELIDED: LazyLock<Regex> =
    LazyLock::new(|| re(r"\b(\d{4})-[\w-]*\.\.\.?[\w-]*?((?:\.drawing)?\.html)"));

/// `line.strip().strip("`")`: a reply line as the readers take it.
pub(crate) fn bare(raw: &str) -> &str {
    strip(raw).trim_matches('`')
}

/// (did the check tag it outside the change, the note without the tag).
pub(crate) fn outside_tag(note: &str) -> (bool, String) {
    let s = strip(note);
    s.strip_prefix(OUTSIDE)
        .map_or_else(|| (false, note.to_owned()), |rest| (true, strip(rest).to_owned()))
}

/// The verdicts by key, and each UNCLAIMED (uid, decision), from a check's reply; the notes in the house style.
pub(crate) fn parse_reply(text: &str) -> (HashMap<String, (String, String)>, Vec<(String, String)>) {
    let mut verdicts = HashMap::new();
    let mut unclaimed = Vec::new();
    for raw in text.split('\n') {
        let line = bare(raw);
        if let Some(m) = VERDICT.captures(line).ok().flatten() {
            let key = m[1].trim_matches('`').to_owned();
            verdicts.insert(key, (m[2].to_owned(), americanize(strip(&m[3]))));
        } else if let Some(m) = UNCLAIMED.captures(line).ok().flatten() {
            unclaimed.push((m[1].trim_matches('`').to_owned(), americanize(strip(&m[2]))));
        }
    }
    (verdicts, unclaimed)
}

/// The reply with each pointer a check shortened given its full file name, where one question stem matches.
pub(crate) fn unelide(reply: &str, stems: &[String]) -> String {
    ELIDED
        .replace_all(reply, |m: &Captures| {
            let hits: Vec<&String> = stems
                .iter()
                .filter(|s| s.starts_with(&format!("{}-", &m[1])))
                .collect();
            if hits.len() == 1 {
                format!("{}{}", hits[0], &m[2])
            } else {
                m[0].to_owned()
            }
        })
        .into_owned()
}

/// A verdict note without its closing `[§3, §12]`, and the `page:digest` of each block it names: `[§]` none, no tag at all None.
pub(crate) fn rests_of(note: &str, numbered: &Map<String, Value>) -> (String, Option<Vec<String>>) {
    let Some(m) = RESTS.captures(note).ok().flatten() else {
        return (note.to_owned(), None);
    };
    let start = m.get(0).map_or(note.len(), |g| g.start());
    let names: BTreeSet<String> = m[1]
        .split(',')
        .filter_map(|n| numbered.get(strip(n)).and_then(Value::as_str).map(str::to_owned))
        .collect();
    (note[..start].trim_end_matches(l7r_guard::shared::py_text::is_space).to_owned(), Some(names.into_iter().collect()))
}

/// The index with a check's reply applied, and the messages for the session (spec FR-009).
pub(crate) fn record(index: &Index, units: &Map<String, Value>, reply: &str, today: &str, numbered: &Map<String, Value>) -> (Index, Vec<String>) {
    let (verdicts, unclaimed) = parse_reply(reply);
    let mut msgs = Vec::new();
    let mut out = index.clone();
    let refused: BTreeSet<&String> = verdicts.keys().filter(|k| !units.contains_key(*k)).collect();
    for key in refused {
        msgs.push(format!("refused: `{key}` is not a unit of this bundle"));
    }
    let checked: HashSet<&str> = units.values().map(|u| field(u, "uid")).collect();
    let stale: Vec<String> = out
        .iter()
        .filter(|(k, v)| is(v, "verdict", "UNCLAIMED") && checked.contains(k.rsplit_once('#').map_or(k.as_str(), |p| p.0)))
        .map(|(k, _)| k.clone())
        .collect();
    for key in stale {
        out.shift_remove(&key);
    }
    let by_key: BTreeMap<&String, &Value> = units.iter().collect();
    for (key, fp) in by_key {
        let Some((verdict, note)) = verdicts.get(key.as_str()) else {
            msgs.push(format!("no verdict for `{key}` - it stays owed"));
            continue;
        };
        out.insert(key.clone(), Value::Object(verdict_row(key, fp, verdict, note, today, numbered, &mut msgs)));
    }
    let cores: HashMap<&str, &str> = units.values().map(|u| (field(u, "uid"), field(u, "core"))).collect();
    for (uid, said) in unclaimed {
        let Some(core) = cores.get(uid.as_str()) else {
            msgs.push(format!("refused: UNCLAIMED `{uid}` is not a unit of this bundle"));
            continue;
        };
        let (outside, decision) = outside_tag(&said);
        let mut row = Map::new();
        row.insert("verdict".into(), json!("UNCLAIMED"));
        row.insert("code".into(), json!(core));
        row.insert("core".into(), json!(core));
        row.insert("research".into(), json!(""));
        row.insert("date".into(), json!(today));
        row.insert("note".into(), json!(decision));
        if outside {
            row.insert("outside".into(), json!(true));
        }
        out.insert(format!("{uid}#{decision}"), Value::Object(row));
        msgs.push(format!("UNCLAIMED {uid} - {decision}: write a claim for it, then check it"));
    }
    (out, msgs)
}

fn verdict_row(key: &str, fp: &Value, verdict: &str, note: &str, today: &str, numbered: &Map<String, Value>, msgs: &mut Vec<String>) -> Map<String, Value> {
    let (outside, note) = outside_tag(note);
    let (note, mut rests) = rests_of(&note, numbered);
    if let (Some(r), Some(pages)) = (&rests, fp.get("pages").and_then(Value::as_object)) {
        if !r.is_empty() {
            let page_of = |r: &str| r.rsplit_once(':').map_or(r, |p| p.0).to_owned();
            let foreign: Vec<&String> = r.iter().filter(|x| !pages.contains_key(&page_of(x))).collect();
            if !foreign.is_empty() {
                let named: BTreeSet<String> = foreign.iter().map(|x| page_of(x)).collect();
                msgs.push(format!("`{key}`: rests on {}, a page it does not cite - dropped (was the reply judged against another bundle's numbering?)", named.into_iter().collect::<Vec<_>>().join(", ")));
                let kept: Vec<String> = r.iter().filter(|x| !foreign.contains(x)).cloned().collect();
                rests = (!kept.is_empty()).then_some(kept);
            }
        }
    }
    let mut row = Map::new();
    row.insert("verdict".into(), json!(verdict));
    row.insert("code".into(), fp["code"].clone());
    row.insert("core".into(), fp["core"].clone());
    for f in ["body", "claim"] {
        if let Some(v) = fp.get(f) {
            row.insert(f.into(), v.clone());
        }
    }
    row.insert("research".into(), fp["research"].clone());
    row.insert("date".into(), json!(today));
    row.insert("note".into(), json!(note));
    for f in ["pages", "section"] {
        if let Some(v) = fp.get(f) {
            row.insert(f.into(), v.clone());
        }
    }
    if let Some(r) = rests {
        row.insert("rests".into(), json!(r));
    }
    if outside && FINDINGS.contains(&verdict) {
        row.insert("outside".into(), json!(true));
    }
    row
}

#[cfg(test)]
mod tests;
