//! `l7r-gate claims <command>`: each command's body (`scripts/record/claims.py`'s `main` and `claims_cli.py`'s handlers, with
//! `claims_accept.py` and `claims_counters.clear`, ported by feature 449 T82); the counter-only clear and the stale-figure check are
//! [`super::counters`] and [`super::stale`], which read a Rust unit natively (feature 449 T165).

#![expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "Python's `str.endswith`, which this port keeps, is case-sensitive"
)]

use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::io::Write as _;
use std::path::{Path, PathBuf};

use serde_json::{json, Map, Value};

use super::bundle::bundle;
use super::carry::{carry, classified, gate as carry_gate, record_known, Reading};
use super::index::{
    judged, live_rows, load_map, owed, page_blocks, rekey, rows_of, save_index, save_store, truthy,
    Cur, Index, PageMemo, Store, DEFERRED, INDEX, QUESTIONS, STORE, TRIAGED,
};
use super::report::{
    coverage, delta_form_problems, inherited_none, load_deferred, question_names, report,
    split_keys,
};
use super::scope::all_units;
use super::triage::{clear_page_moves, keep_texts, read_reply, record_triage, triage_bundle, vet};
use super::units::{sha, Pair};
use crate::record::args::Parsed;
use crate::record::repo::{fail, Fail};
use crate::record::units::digest;

/// A triage bundle of this many claims or fewer goes straight to impl-drift (feature 430 T06, D6).
const TRIAGE_SKIP_MAX: usize = 3;
/// Where each skipped triage is recorded (feature 430 D6).
const SKIPS: &str = "dev/claims-triage-skips.jsonl";

/// What a command printed: its stdout and its stderr, in order.
#[derive(Default)]
pub struct Out {
    pub out: String,
    pub err: String,
}

impl Out {
    pub fn say(&mut self, line: &str) {
        let _ = writeln!(self.out, "{line}");
    }

    pub fn warn(&mut self, line: &str) {
        let _ = writeln!(self.err, "{line}");
    }
}

/// `pathlib.Path(text)` as `str()` gives it back: repeated and trailing slashes and `.` parts dropped.
pub fn path_text(text: &str) -> String {
    if text.is_empty() {
        return ".".to_owned();
    }
    let abs = text.starts_with('/');
    let lead = if text.starts_with("//") && !text.starts_with("///") {
        "//"
    } else if abs {
        "/"
    } else {
        ""
    };
    let parts: Vec<&str> = text
        .split('/')
        .filter(|p| !p.is_empty() && *p != ".")
        .collect();
    let joined = parts.join("/");
    if joined.is_empty() {
        return if lead.is_empty() {
            ".".to_owned()
        } else {
            lead.to_owned()
        };
    }
    format!("{lead}{joined}")
}

/// Every procedure-section claim re-keyed to its own line's fingerprint without owing it; how many.
pub fn backfill_sections(cur: &Cur, index: &mut Index, store: &mut Store) -> usize {
    let mut n = 0;
    for row in cur.iter() {
        let Some(Value::Object(was)) = index.get_mut(&row.key) else {
            continue;
        };
        if !row.unit.line_keyed() || was.contains_key("section") {
            continue;
        }
        let old = sha(&format!("{}\x1f{}", row.unit.core, row.claim.normalized()));
        if was.get("code").and_then(Value::as_str) == Some(&old) {
            was.insert("code".into(), json!(row.code));
            was.insert("section".into(), json!(row.unit.core));
            store.insert(
                row.unit.core.clone(),
                json!(row
                    .unit
                    .blocks
                    .iter()
                    .map(|b| digest(&[b]))
                    .collect::<Vec<_>>()),
            );
            n += 1;
        }
    }
    n
}

/// Every row checked at today's research given the pages it was checked at, and those pages snapshotted; how many.
fn backfill(cur: &Cur, index: &mut Index, qdir: &Path, store: &mut Store) -> Result<usize, Fail> {
    let mut memo = PageMemo::default();
    let mut n = 0;
    for row in cur.iter() {
        let Some(Value::Object(was)) = index.get_mut(&row.key) else {
            continue;
        };
        if was.contains_key("pages")
            || was.get("research").and_then(Value::as_str) != Some(&row.research)
            || row.research.is_empty()
        {
            continue;
        }
        let mut pages = Map::new();
        for name in super::bundle::cited_pages(&row.claim) {
            let (fp, blocks) = page_blocks(&name, qdir, &mut memo)?;
            pages.insert(name.clone(), json!(fp));
            store.insert(
                fp.clone(),
                json!(blocks.iter().map(|(d, _)| d.clone()).collect::<Vec<_>>()),
            );
        }
        was.insert("pages".into(), Value::Object(pages));
        n += 1;
    }
    Ok(n)
}

/// Each row whose stored code is its claim's code under the old fingerprint carried to the new one - an UNCLAIMED row, keyed by its
/// decision and holding its unit's core, by its unit's, and a row whose code holds the claim as it was recorded (a relabel its
/// MISLABELED verdict prescribed, answered since), by that text (feature 449 T166) - and the keys carried.
fn refingerprint(
    index: &mut Index,
    old: &HashMap<String, (String, String)>,
    new: &HashMap<String, (String, String)>,
) -> Vec<String> {
    let mut n = Vec::new();
    for (key, row) in index.iter_mut() {
        let uid = key.rsplit_once('#').map_or(key.as_str(), |p| p.0);
        let unclaimed = super::index::is(row, "verdict", "UNCLAIMED");
        let pick = |m| -> Option<(String, String)> {
            let m: &HashMap<String, (String, String)> = m;
            m.get(key)
                .or_else(|| m.get(uid).filter(|_| unclaimed))
                .cloned()
        };
        let (Some(o), Some(w)) = (pick(old), pick(new)) else {
            continue;
        };
        let (o, w) = if o.0.is_empty() {
            ((o.1.clone(), o.1), (w.1.clone(), w.1))
        } else {
            let said = super::index::field(row, "claim");
            let at = |core: &str| sha(&format!("{core}\x1f{said}"));
            if said.is_empty() || super::index::is(row, "code", &o.0) {
                (o, w)
            } else {
                ((at(&o.1), o.1.clone()), (at(&w.1), w.1))
            }
        };
        if o.0 == w.0 || row.get("code").and_then(Value::as_str) != Some(&o.0) {
            continue;
        }
        row["code"] = json!(w.0);
        if row.get("core").and_then(Value::as_str) == Some(&o.1) {
            row["core"] = json!(w.1);
        }
        n.push(key.clone());
    }
    n
}

/// key -> (code, core) for each claim of `pairs`, and uid -> ("", core) for each unit (an UNCLAIMED row's).
fn codes(pairs: &[Pair]) -> HashMap<String, (String, String)> {
    let mut out: HashMap<String, (String, String)> = pairs
        .iter()
        .map(|(u, _)| (u.uid(), (String::new(), u.core.clone())))
        .collect();
    out.extend(pairs.iter().flat_map(|(u, _)| {
        u.claims
            .iter()
            .map(move |c| (u.key(c), (u.code(c), u.core.clone())))
    }));
    out
}

fn owed_cmd(
    root: &Path,
    pairs: &[Pair],
    cur: &Cur,
    index: &Index,
    store: &Store,
    o: &mut Out,
) -> Result<i32, Fail> {
    for x in coverage(pairs, &question_names(root)) {
        o.say(&format!(
            "claims-form: {x} - the gate's test_claims_coverage fails on it"
        ));
    }
    for x in super::stale::stale(root)? {
        o.say(&x);
    }
    let qdir = root.join(QUESTIONS);
    let due = owed(cur, index, Some(&qdir), Some(store))?;
    let keys: Vec<String> = due.iter().map(|(k, _)| k.clone()).collect();
    for x in super::labels::flags(cur, &keys, &qdir) {
        o.say(&x);
    }
    if due.is_empty() {
        o.say("claims-owed: no claim is owed");
        return Ok(0);
    }
    let full = judged(&due);
    let mods: HashSet<&str> = full
        .iter()
        .filter_map(|k| cur.get(k))
        .map(|r| r.unit.path.as_str())
        .collect();
    for (key, why) in &due {
        o.say(&format!("{why:<16} {key}"));
    }
    for x in inherited_none(cur, &due) {
        o.say(&x);
    }
    if !full.is_empty() {
        o.say(&format!("claims-owed: {} claim(s) in {} file(s) owe impl-drift; bundle per file with `make claims-bundle MODULE=<path>`, or OWED=1 for all", full.len(), mods.len()));
    }
    if due.len() > full.len() {
        o.say(&format!("claims-owed: {} claim(s) owe only a TRIAGE of what changed on their pages or in their code - `make claims-triage` first; it sends on only the claims a change bears on", due.len() - full.len()));
    }
    Ok(0)
}

/// `str.split()`'s word count.
fn words(text: &str) -> usize {
    l7r_shared::py_text::split(text).len()
}

fn bundle_cmd(
    root: &Path,
    cur: &Cur,
    index: &Index,
    store: &Store,
    p: &Parsed,
    o: &mut Out,
) -> Result<i32, Fail> {
    let due: HashMap<String, String> = owed(cur, index, Some(&root.join(QUESTIONS)), Some(store))?
        .into_iter()
        .filter(|(_, why)| !TRIAGED.contains(&why.as_str()))
        .collect();
    let (module, units) = (p.text("--module", ""), p.text("--units", ""));
    let keys: Vec<String> = if p.on("--owed") {
        let mut k: Vec<String> = due.keys().cloned().collect();
        k.sort();
        k
    } else if !module.is_empty() {
        let mut k: Vec<String> = cur
            .iter()
            .filter(|r| r.unit.path == module || r.unit.path.ends_with(&format!("/{module}")))
            .map(|r| r.key.clone())
            .collect();
        k.sort();
        k
    } else {
        split_keys(units, ',', &|k| cur.contains(k))
    };
    let named = if !module.is_empty() {
        module.to_owned()
    } else if p.on("--owed") {
        "owed".to_owned()
    } else {
        keys.first().cloned().unwrap_or_else(|| "none".to_owned())
    };
    let slug = crate::record::units::re("[^a-z0-9]+")
        .replace_all(&named.to_lowercase(), "-")
        .trim_matches('-')
        .to_owned();
    let slug: String = slug
        .chars()
        .rev()
        .take(60)
        .collect::<Vec<_>>()
        .into_iter()
        .rev()
        .collect();
    let out = if p.text("--out", "").is_empty() {
        // the bundles' root (`/tmp/l7r-check`; a test's own, never the real one - feature 449 T101)
        l7r_gate_core::record::bundle::default_root().join(format!("claims-{slug}"))
    } else {
        PathBuf::from(path_text(p.text("--out", "")))
    };
    let _ = std::fs::remove_dir_all(&out);
    let unknown: Vec<&String> = keys.iter().filter(|k| !cur.contains(k)).collect();
    if !unknown.is_empty() || keys.is_empty() {
        let unknown_names: Vec<&str> = unknown.iter().map(|s| s.as_str()).collect();
        o.warn(&format!(
            "claims-bundle: no such claim(s): {}",
            if unknown_names.is_empty() {
                "(none selected)".to_owned()
            } else {
                unknown_names.join(", ")
            }
        ));
        return Ok(2);
    }
    let reason = p.text("--reason", "");
    let not_owed: Vec<&String> = keys.iter().filter(|k| !due.contains_key(*k)).collect();
    if !not_owed.is_empty() && words(reason) < 2 {
        o.warn(&format!("claims-bundle: {} of these claims are not owed (first: {}); a re-check needs REASON=\"<why>\"", not_owed.len(), not_owed[0]));
        return Ok(3);
    }
    let asked: Vec<(String, String)> = keys
        .iter()
        .map(|k| (k.clone(), due.get(k).cloned().unwrap_or_default()))
        .collect();
    for x in inherited_none(cur, &asked) {
        o.say(&x);
    }
    let with: Vec<String> = p
        .text("--with", "")
        .split(',')
        .filter(|c| !c.is_empty())
        .map(str::to_owned)
        .collect();
    let pages: Vec<String> = p
        .text("--pages", "")
        .split(',')
        .filter(|c| !c.is_empty())
        .map(str::to_owned)
        .collect();
    let manifest = bundle(root, cur, &keys, &out, &with, &pages)?;
    o.say(&manifest.to_string_lossy());
    super::flight::mark(root, &out)?;
    if !not_owed.is_empty() {
        o.say(&format!(
            "claims-bundle: re-check of {} claim(s) not owed, because: {reason}",
            not_owed.len()
        ));
    }
    Ok(0)
}

fn record_cmd(
    root: &Path,
    cur: &Cur,
    index: &Index,
    store: &Store,
    p: &Parsed,
    o: &mut Out,
) -> Result<i32, Fail> {
    let bundle_dir = PathBuf::from(p.text("--bundle", ""));
    let units = load_units(&bundle_dir.join("units.json"))?;
    let mut stems: Vec<String> = std::fs::read_dir(root.join(QUESTIONS))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| {
            n.len() > 5
                && n.as_bytes()[..4].iter().all(u8::is_ascii_digit)
                && n.as_bytes()[4] == b'-'
                && n.ends_with(".html")
        })
        .map(|n| n.split('.').next().unwrap_or_default().to_owned())
        .collect::<HashSet<_>>()
        .into_iter()
        .collect();
    stems.sort();
    let reply = read_reply(
        root,
        p.text("--reply", ""),
        "claims-checked",
        "nothing recorded",
        &mut o.err,
    )?;
    if l7r_shared::py_text::strip(&reply).is_empty() {
        return Ok(2);
    }
    let (reply, bad) = vet(
        &super::reply::unelide(&reply, &stems),
        &units,
        root,
        &mut o.out,
        &mut o.err,
    )?;
    let blocks_file = bundle_dir.join("blocks.json");
    let blocks = if blocks_file.is_file() {
        Value::Object(load_map(&blocks_file)?)
    } else {
        json!({"numbered": {}, "snapshots": {}})
    };
    let numbered = blocks["numbered"].as_object().cloned().unwrap_or_default();
    let (new, msgs) = super::reply::record(
        index,
        &units,
        &reply,
        &crate::record::bundle::today(),
        &numbered,
    );
    save_index(&root.join(INDEX), &live_rows(cur, &new))?;
    let mut merged = store.clone();
    merged.extend(blocks["snapshots"].as_object().cloned().unwrap_or_default());
    save_store(&root.join(STORE), &merged)?;
    keep_texts(&root.join(QUESTIONS), &units)?;
    for m in &msgs {
        o.say(&format!("claims-checked: {m}"));
    }
    let n = units
        .iter()
        .filter(|(k, u)| new.get(*k).and_then(|r| r.get("code")) == u.get("code"))
        .count();
    o.say(&format!("claims-checked: {n} of {} recorded", units.len()));
    super::flight::clear(root, &bundle_dir);
    Ok(if bad.is_empty() { 0 } else { 3 })
}

fn load_units(path: &Path) -> Result<Map<String, Value>, Fail> {
    let text = std::fs::read_to_string(path)
        .map_err(|e| format!("FileNotFoundError: {}: {e}", path.display()))?;
    match serde_json::from_str::<Value>(&text)
        .map_err(|e| format!("json.decoder.JSONDecodeError: {e}"))?
    {
        Value::Object(m) => Ok(m),
        _ => Ok(Map::new()),
    }
}

fn small_triage(root: &Path, keys: &[String], out: &str, o: &mut Out) -> Result<i32, Fail> {
    let why = format!("a claims triage of {} claim(s), at most {TRIAGE_SKIP_MAX}, goes straight to impl-drift (feature 430 D6)", keys.len());
    let mut args: Vec<String> = [
        "--root",
        &root.to_string_lossy(),
        "bundle",
        "--units",
        &keys.join(","),
        "--reason",
        &why,
    ]
    .iter()
    .map(|s| (*s).to_owned())
    .collect();
    if !out.is_empty() {
        args.extend(["--out".to_owned(), out.to_owned()]);
    }
    let done = super::cli(&args);
    o.out.push_str(&done.stdout);
    o.err.push_str(&done.stderr);
    if done.code == 0 {
        let row = json!({"date": crate::record::bundle::today(), "claims": keys.len(), "keys": keys, "why": why});
        let mut fh = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(root.join(SKIPS))
            .map_err(fail)?;
        fh.write_all((crate::logs::one_line_utf8(&row) + "\n").as_bytes())
            .map_err(fail)?;
        o.say(&format!("claims-triage: {why} - dispatch `impl-drift` on the MANIFEST above, then `make claims-checked BUNDLE=<dir> REPLY=<file>`; the skip is in {SKIPS}"));
    }
    Ok(done.code)
}

fn triage_cmd(
    root: &Path,
    cur: &Cur,
    index: Index,
    store: &Store,
    p: &Parsed,
    o: &mut Out,
) -> Result<i32, Fail> {
    let qdir = root.join(QUESTIONS);
    let today = crate::record::bundle::today();
    let due = owed(cur, &index, Some(&qdir), Some(store))?;
    let pages: Vec<String> = due
        .iter()
        .filter(|(k, why)| why == "triage" && truthy(index.get(k).and_then(|r| r.get("rests"))))
        .map(|(k, _)| k.clone())
        .collect();
    let mut index = index;
    if !pages.is_empty() {
        let (cleared, snaps) = clear_page_moves(cur, &index, &pages, &qdir, &today)?;
        index = cleared;
        save_index(&root.join(INDEX), &live_rows(cur, &index))?;
        let mut merged = store.clone();
        merged.extend(snaps);
        save_store(&root.join(STORE), &merged)?;
        o.say(&format!("claims-triage: {} claim(s) cleared without a triage - a page each cites moved and no block it rests on did (feature 432, FR-005 a)", pages.len()));
    }
    let keys: Vec<String> = due
        .iter()
        .filter(|(k, why)| TRIAGED.contains(&why.as_str()) && !pages.contains(k))
        .map(|(k, _)| k.clone())
        .collect();
    if keys.is_empty() {
        o.say("claims-triage: no claim is owed a triage");
        return Ok(0);
    }
    let out = p.text("--out", "");
    if keys.len() <= TRIAGE_SKIP_MAX {
        return small_triage(root, &keys, out, o);
    }
    let tout = if out.is_empty() {
        l7r_gate_core::record::bundle::default_root().join("claims-triage")
    } else {
        PathBuf::from(path_text(out))
    };
    let manifest = triage_bundle(cur, &index, store, &keys, &qdir, &tout)?;
    let data = Value::Object(load_map(&tout.join("triage.json"))?);
    let forced: Vec<String> = data["forced"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(|v| v.as_str().map(str::to_owned))
        .collect();
    let units = data["units"].as_object().cloned().unwrap_or_default();
    if keys.iter().all(|k| forced.contains(k)) {
        let (new, _msgs) = record_triage(&index, &units, "", &today, &forced);
        save_index(&root.join(INDEX), &live_rows(cur, &new))?;
        let mut merged = store.clone();
        merged.extend(data["snapshots"].as_object().cloned().unwrap_or_default());
        save_store(&root.join(STORE), &merged)?;
        keep_texts(&qdir, &units)?;
        o.say(&format!("claims-triage: all {} claim(s) are cx.owed in full (no diff or removed block to show) - no triage to dispatch; they go straight to impl-drift: `make claims-bundle OWED=1`, then `make claims-checked BUNDLE=<dir> REPLY=<file>`", keys.len()));
        return Ok(0);
    }
    o.say(&manifest.to_string_lossy());
    super::flight::mark(root, &tout)?;
    o.say(&format!("claims-triage: {} claim(s); dispatch the `claims-triage` agent on the MANIFEST (a session started before 2026-10-17's amendment 6 landed: restart to load it), save its reply, then `make claims-triaged BUNDLE=<dir> REPLY=<file>`", keys.len()));
    Ok(0)
}

fn triaged_cmd(
    root: &Path,
    cur: &Cur,
    index: &Index,
    store: &Store,
    p: &Parsed,
    o: &mut Out,
) -> Result<i32, Fail> {
    let bundle_dir = PathBuf::from(p.text("--bundle", ""));
    let data = Value::Object(load_units(&bundle_dir.join("triage.json"))?);
    let reply = read_reply(
        root,
        p.text("--reply", ""),
        "claims-triaged",
        "nothing cleared",
        &mut o.err,
    )?;
    if l7r_shared::py_text::strip(&reply).is_empty() {
        return Ok(2);
    }
    let units = data["units"].as_object().cloned().unwrap_or_default();
    let forced: Vec<String> = data
        .get("forced")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|v| v.as_str().map(str::to_owned))
        .collect();
    let (new, msgs) = record_triage(
        index,
        &units,
        &reply,
        &crate::record::bundle::today(),
        &forced,
    );
    save_index(&root.join(INDEX), &live_rows(cur, &new))?;
    let mut merged = store.clone();
    merged.extend(data["snapshots"].as_object().cloned().unwrap_or_default());
    save_store(&root.join(STORE), &merged)?;
    keep_texts(&root.join(QUESTIONS), &units)?;
    for m in &msgs {
        o.say(&format!("claims-triaged: {m}"));
    }
    let touched = msgs.iter().filter(|m| m.starts_with("touched")).count();
    let named = msgs
        .iter()
        .filter(|m| {
            m.starts_with("touched")
                && !m.contains(" - a removed block the history no longer shows")
        })
        .count();
    let forced_n = touched - named;
    let tail = if forced_n > 0 {
        format!(", {forced_n} cx.owed in full: a removed block's words could not be shown")
    } else {
        String::new()
    };
    o.say(&format!("claims-triaged: {touched} of {} sent on to impl-drift ({named} named by the reply{tail}); the rest cleared", units.len()));
    super::flight::clear(root, &bundle_dir);
    Ok(0)
}

fn accept_line(key: &str, was: &Value, trigger: &str) -> String {
    if super::index::is(was, "verdict", "DRIFTED") {
        return format!("VERDICT {key} DRIFTED - {}; a known drift accepted by the round arbiter ({trigger}) to land as filed", super::index::field(was, "note"));
    }
    format!("VERDICT {key} IN-STEP - accepted by the round arbiter ({trigger}), binding")
}

fn accept_cmd(root: &Path, cur: &Cur, index: &Index, p: &Parsed, o: &mut Out) -> Result<i32, Fail> {
    let keys = split_keys(p.text("--keys", ""), ';', &|k| cur.contains(k));
    let missing: Vec<&str> = keys
        .iter()
        .filter(|k| !cur.contains(k))
        .map(String::as_str)
        .collect();
    if !missing.is_empty() || keys.is_empty() {
        o.warn(&format!(
            "claims-accept: no such claim: {}",
            if missing.is_empty() {
                "(none named)".to_owned()
            } else {
                missing.join(", ")
            }
        ));
        return Ok(2);
    }
    let tmp = super::temp_dir("accept");
    let made =
        bundle(root, cur, &keys, &tmp, &[], &[]).and_then(|_| load_units(&tmp.join("units.json")));
    drop(tmp);
    let units = made?;
    let trigger = p.text("--trigger", "");
    let empty = json!({});
    let reply: Vec<String> = keys
        .iter()
        .map(|k| {
            accept_line(
                k,
                index.get(k).filter(|v| truthy(Some(v))).unwrap_or(&empty),
                trigger,
            )
        })
        .collect();
    let (new, msgs) = super::reply::record(
        index,
        &units,
        &reply.join("\n"),
        &crate::record::bundle::today(),
        &Map::new(),
    );
    save_index(&root.join(INDEX), &live_rows(cur, &new))?;
    for m in &msgs {
        o.say(&format!("claims-accept: {m}"));
    }
    let kept = keys
        .iter()
        .filter(|k| {
            index
                .get(*k)
                .is_some_and(|v| super::index::is(v, "verdict", "DRIFTED"))
        })
        .count();
    o.say(&format!("claims-accept: {} claim(s) recorded IN-STEP and {kept} kept DRIFTED (a known drift) on {trigger}'s accept", keys.len() - kept));
    Ok(0)
}

fn carry_cmd(root: &Path, p: &Parsed, o: &mut Out) -> Result<i32, Fail> {
    let (keys_text, ruling) = (p.text("--keys", ""), p.text("--ruling", ""));
    let attempt = (|| -> Result<Result<String, String>, Fail> {
        if keys_text.is_empty() != ruling.is_empty() {
            return Ok(Err("KEYS= and RULING= go together: the findings a round-arbiter ruling carried, and that ruling's trigger".to_owned()));
        }
        let mut here = None;
        let keys: Vec<String> = if keys_text.is_empty() {
            let at = reading(root)?;
            let (_, _, _, carried) = classified(root, &at)?;
            let target = super::carry::target(root)?;
            let done = super::carry::filed(target.as_deref())?;
            here = Some(target);
            carried
                .into_iter()
                .map(|(k, _)| k)
                .filter(|k| !done.contains_key(k))
                .collect()
        } else {
            keys_text
                .split(';')
                .map(l7r_shared::py_text::strip)
                .filter(|k| !k.is_empty())
                .map(str::to_owned)
                .collect()
        };
        let read = |r: &Path| match &here {
            Some(t) => Ok(t.clone()),
            None => super::carry::target(r),
        };
        Ok(carry(
            root,
            &read,
            p.text("--feature", ""),
            p.text("--task", ""),
            &keys,
            ruling,
        ))
    })()?;
    match attempt {
        Ok(said) => {
            o.say(&said);
            Ok(0)
        }
        Err(e) => {
            o.warn(&format!("claims-carry: {e}"));
            Ok(2)
        }
    }
}

/// The rows now and the index, as the gate reads them.
fn reading(root: &Path) -> Result<Reading, Fail> {
    let pairs = all_units(root, true)?;
    Ok(Reading {
        cur: rows_of(pairs, &root.join(QUESTIONS))?,
        index: load_map(&root.join(INDEX))?,
    })
}

fn gate_cmd(root: &Path, o: &mut Out) -> Result<i32, Fail> {
    let pairs = all_units(root, true)?;
    let at = Reading {
        cur: rows_of(pairs.clone(), &root.join(QUESTIONS))?,
        index: load_map(&root.join(INDEX))?,
    };
    let (mut refuse, warn) = carry_gate(root, &at)?;
    refuse.extend(delta_form_problems(root, &pairs));
    for w in &warn {
        o.say(&format!("claims-gate: {w}"));
    }
    for x in &refuse {
        o.say(&format!("claims-gate: REFUSED {x}"));
    }
    Ok(i32::from(!refuse.is_empty()))
}

/// `claims coverage --rust`, `make static`'s form check (feature 449 T169): every unit of the crates the claims walk reads
/// ([`super::units::walked`]) carries a well-formed claim. WHY: T168's new crate lacked a `Research:` line on every unit, and only
/// `make claims-owed` at the landing named it - no gate before did; read from the Rust alone (no Python started), about a tenth of a
/// second over the whole of `rust/`, so `make static` runs it over every walked crate rather than the changed ones.
fn rust_form(root: &Path, o: &mut Out) -> Result<i32, Fail> {
    let pairs = super::units::all_rust_units(root, "", false)?;
    let probs = coverage(&pairs, &question_names(root));
    if probs.is_empty() {
        o.say("claims-form: every unit of the Rust crates the claims walk reads carries a claim");
        return Ok(0);
    }
    o.say(&probs.join("\n"));
    o.say(&format!(
        "claims-form: {} problem(s) in the Rust crates the claims walk reads, which `make claims-owed` refuses at the landing. Fix: give \
         each unit named a `Research:` claim (`/// Research: <label> - <backing>`), or its file a module-level one that its units inherit \
         (`//! Research:` then `//!     <label> - NONE: <why it decides nothing physical>`). The form: {}",
        probs.len(),
        super::grammar::GRAMMAR
    ));
    Ok(1)
}

fn coverage_cmd(root: &Path, p: &Parsed, o: &mut Out) -> Result<i32, Fail> {
    if p.on("--rust") {
        return rust_form(root, o);
    }
    let path = p.text("--path", "");
    let pairs = all_units(root, true)?;
    let probs: Vec<String> = coverage(&pairs, &question_names(root))
        .into_iter()
        .filter(|x| x.split(' ').next().unwrap_or_default().contains(path))
        .collect();
    if probs.is_empty() {
        let under = if path.is_empty() {
            String::new()
        } else {
            format!(" under {path}")
        };
        o.say(&format!(
            "claims-coverage: every unit{under} carries a claim"
        ));
        return Ok(0);
    }
    o.say(&probs.join("\n"));
    o.say(&format!(
        "claims-coverage: {} problem(s). The form: {}",
        probs.len(),
        super::grammar::GRAMMAR
    ));
    Ok(1)
}

/// One command at `root`; its exit status, what it printed in `o`.
pub fn run(cmd: &str, p: &Parsed, root: &Path, o: &mut Out) -> Result<i32, Fail> {
    match cmd {
        "gate" => return gate_cmd(root, o),
        "carry" => return carry_cmd(root, p, o),
        "known" => {
            let at = reading(root)?;
            let written = record_known(root, &at)?;
            if written.is_empty() {
                o.say("claims-known: no known drift is unrecorded");
            }
            for w in written {
                o.say(&format!("claims-known: recorded {w}"));
            }
            return Ok(0);
        }
        "coverage" => return coverage_cmd(root, p, o),
        _ => {}
    }
    let pairs = all_units(root, true)?;
    let cur = rows_of(pairs.clone(), &root.join(QUESTIONS))?;
    let index = load_map(&root.join(INDEX))?;
    let index = super::counters::counters_clear(root, &cur, index, cmd, o)?;
    let (qdir, store) = (root.join(QUESTIONS), load_map(&root.join(STORE))?);
    match cmd {
        "refingerprint" => {
            let mut index = index;
            let old = codes(&all_units(root, false)?);
            let keys = refingerprint(&mut index, &old, &codes(&pairs));
            // each carried row of a Rust unit records the constants its code reads, as a check would have (feature 449 T166)
            let reads: HashMap<String, &str> = pairs
                .iter()
                .map(|(u, _)| (u.uid(), u.reads.as_str()))
                .collect();
            for k in &keys {
                let uid = k.rsplit_once('#').map_or(k.as_str(), |p| p.0);
                if let (Some(Value::Object(row)), Some(r)) = (index.get_mut(k), reads.get(uid)) {
                    super::reads::stamp(row, Some(r));
                }
            }
            if !keys.is_empty() {
                save_index(&root.join(INDEX), &index)?;
                super::reads::record_migration(root, &keys)?;
            }
            o.say(&format!("claims-refingerprint: {} claim row(s) carried to the current fingerprint (a `.py` unit's star re-exports, 417 T54; a Rust unit's constant reads, 449 T166), their code otherwise unchanged", keys.len()));
            Ok(0)
        }
        "rekey" => {
            let mut index = index;
            let n = rekey(&cur, &mut index);
            // and across a port, by the port map (feature 449 T166, `ask:449-phase4-slices` Q10)
            let ported = super::ports::rekey_ports(root, &cur, &mut index)?;
            if n > 0
                || !ported.carried.is_empty()
                || !ported.dropped.is_empty()
                || !ported.retired.is_empty()
                || !ported.rebuilt.is_empty()
            {
                save_index(&root.join(INDEX), &index)?;
            }
            o.say(&format!(
                "claims-rekey: {n} claim row(s) carried to the file their unit moved to"
            ));
            Ok(super::ports::say(&ported, o))
        }
        "accept" => accept_cmd(root, &cur, &index, p, o),
        "owed" => owed_cmd(root, &pairs, &cur, &index, &store, o),
        "backfill-sections" | "backfill" => {
            let (mut index, mut store) = (index, store);
            let n = if cmd == "backfill" {
                backfill(&cur, &mut index, &qdir, &mut store)?
            } else {
                backfill_sections(&cur, &mut index, &mut store)
            };
            save_index(&root.join(INDEX), &live_rows(&cur, &index))?;
            save_store(&root.join(STORE), &store)?;
            o.say(&if cmd == "backfill" {
                format!("claims-backfill: {n} row(s) given the pages they were checked at")
            } else {
                format!("claims-backfill-sections: {n} section claim(s) re-keyed to their own line; none owed by it")
            });
            Ok(0)
        }
        "triage-owed" => {
            let n = owed(&cur, &index, Some(&qdir), Some(&store))?
                .iter()
                .filter(|(_, w)| TRIAGED.contains(&w.as_str()))
                .count();
            o.say(&n.to_string());
            Ok(0)
        }
        "triage" => triage_cmd(root, &cur, index, &store, p, o),
        "triaged" => triaged_cmd(root, &cur, &index, &store, p, o),
        "report" => {
            let deferred = load_deferred(&root.join(DEFERRED))?;
            let text = report(&cur, &index, &qdir, &store, &deferred, p.on("--all"))?;
            o.out
                .push_str(&super::pager::page(&text, &super::pager::Screen::here()));
            Ok(0)
        }
        "bundle" => bundle_cmd(root, &cur, &index, &store, p, o),
        _ => record_cmd(root, &cur, &index, &store, p, o),
    }
}

#[cfg(test)]
mod more;
#[cfg(test)]
mod tests;
