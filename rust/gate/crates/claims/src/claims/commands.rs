//! `l7r-gate claims <command>`: each command's body (`scripts/record/claims.py`'s `main` and `claims_cli.py`'s handlers, with
//! `claims_accept.py` and `claims_counters.clear`, ported by feature 449 T82).

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
    body_of, judged, live_rows, load_map, owed, page_blocks, rekey, rows_of, save_index,
    save_store, truthy, Cur, Index, PageMemo, Store, CODE_TRIAGE, DEFERRED, INDEX, QUESTIONS,
    STORE, TRIAGED,
};
use super::report::{
    coverage, delta_form_problems, inherited_none, load_deferred, question_names, report,
    split_keys,
};
use super::scope::{all_units, Reader};
use super::triage::{clear_page_moves, keep_texts, read_reply, record_triage, triage_bundle, vet};
use super::units::{sha, Pair};
use crate::record::args::Parsed;
use crate::record::repo::{fail, Fail};
use crate::record::units::digest;

/// Where a bundle goes with no `--out`.
const DEFAULT_OUT: &str = "/tmp/l7r-check";
/// A triage bundle of this many claims or fewer goes straight to impl-drift (feature 430 T06, D6).
const TRIAGE_SKIP_MAX: usize = 3;
/// Where each skipped triage is recorded (feature 430 D6).
const SKIPS: &str = "dev/claims-triage-skips.jsonl";
/// What a claim cleared by the counter-only rule records (feature 446, FR-003).
const COUNTER_CLEARED: &str = "counter-only (feature 446)";
const COUNTER_KINDS: [&str; 4] = ["function", "method", "class", "constant"];

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
            || row.claim.pointers.is_empty()
        {
            continue;
        }
        let mut pages = Map::new();
        for ptr in &row.claim.pointers {
            let name = super::index::page_name(ptr);
            let (fp, blocks) = page_blocks(name, qdir, &mut memo)?;
            pages.insert(name.to_owned(), json!(fp));
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

/// Each row whose stored code is its claim's code under the old fingerprint carried to the new one; how many.
fn refingerprint(
    index: &mut Index,
    old: &HashMap<String, (String, String)>,
    new: &HashMap<String, (String, String)>,
) -> usize {
    let mut n = 0;
    for (key, row) in index.iter_mut() {
        let (Some(o), Some(w)) = (old.get(key), new.get(key)) else {
            continue;
        };
        if o.0 == w.0 || row.get("code").and_then(Value::as_str) != Some(&o.0) {
            continue;
        }
        row["code"] = json!(w.0);
        if row.get("core").and_then(Value::as_str) == Some(&o.1) {
            row["core"] = json!(w.1);
        }
        n += 1;
    }
    n
}

fn codes(pairs: &[Pair]) -> HashMap<String, (String, String)> {
    pairs
        .iter()
        .flat_map(|(u, _)| {
            u.claims
                .iter()
                .map(move |c| (u.key(c), (u.code(c), u.core.clone())))
        })
        .collect()
}

/// At `owed` and `triage`: every claim owed a code triage only because counter blocks were added recorded cleared (feature 446, FR-003).
fn counters_clear(
    reader: &mut Reader,
    root: &Path,
    cur: &Cur,
    index: Index,
    cmd: &str,
    o: &mut Out,
) -> Result<Index, Fail> {
    if cmd != "owed" && cmd != "triage" {
        return Ok(index);
    }
    let keys: Vec<String> = owed(
        cur,
        &index,
        Some(&root.join(QUESTIONS)),
        Some(&Store::new()),
    )?
    .into_iter()
    .filter(|(_, why)| why == CODE_TRIAGE)
    .map(|(k, _)| k)
    .collect();
    if keys.is_empty() {
        return Ok(index);
    }
    let base = crate::record::repo::git(root, &["merge-base", "HEAD", "origin/main"]);
    let base = l7r_guard::shared::py_text::strip(&base).to_owned();
    if base.is_empty() {
        return Ok(index);
    }
    let mut done = Vec::new();
    for k in keys.iter().filter(|k| index.contains_key(*k)) {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        let unit = &row.unit;
        if !COUNTER_KINDS.contains(&unit.kind.as_str())
            || unit.line_keyed()
            || !unit.path.ends_with(".py")
        {
            continue;
        }
        let got = reader.ask(
            "claims_counter_only",
            &json!([
                root.to_string_lossy(),
                base,
                index[k],
                super::units::to_json(unit),
                row.claim.line
            ]),
        )?;
        if got.as_bool() == Some(true) {
            done.push(k.clone());
        }
    }
    let mut out = index;
    for k in &done {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        let mut r = out
            .get(k)
            .and_then(Value::as_object)
            .cloned()
            .unwrap_or_default();
        r.insert("code".into(), json!(row.code));
        r.insert("core".into(), json!(row.unit.core));
        r.insert("body".into(), json!(body_of(root, &row.unit)?));
        r.insert("triaged".into(), json!(crate::record::bundle::today()));
        r.insert("cleared".into(), json!(COUNTER_CLEARED));
        r.shift_remove("triage");
        out.insert(k.clone(), Value::Object(r));
    }
    if !done.is_empty() {
        save_index(&root.join(INDEX), &live_rows(cur, &out))?;
        o.say(&format!("claims-{cmd}: {} claim(s) cleared without a triage - their units only gained counter blocks (feature 446, FR-003)", done.len()));
    }
    Ok(out)
}

/// The drawing pages still stating a changed constant's old figure (`claims_stale.stale`, Python's syntax tree): asked only when the delta changed a `.py` file under `l7r/`.
fn stale(reader: &mut Reader, root: &Path) -> Result<Vec<String>, Fail> {
    let base = crate::record::repo::git_out(root, &["merge-base", "HEAD", "origin/main"]);
    let base = l7r_guard::shared::py_text::strip(&base);
    if base.is_empty() {
        return Ok(Vec::new());
    }
    let changed = crate::record::repo::git_out(root, &["diff", "--name-only", base, "--", "l7r"]);
    if !changed
        .split_whitespace()
        .any(|p| p.ends_with(".py") && root.join(p).is_file())
    {
        return Ok(Vec::new());
    }
    let got = reader.ask("claims_stale", &json!([root.to_string_lossy()]))?;
    Ok(got
        .as_array()
        .into_iter()
        .flatten()
        .map(|v| v.as_str().unwrap_or_default().to_owned())
        .collect())
}

fn owed_cmd(
    reader: &mut Reader,
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
    for x in stale(reader, root)? {
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
    l7r_guard::shared::py_text::split(text).len()
}

fn bundle_cmd(
    reader: &mut Reader,
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
        PathBuf::from(DEFAULT_OUT).join(format!("claims-{slug}"))
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
    let manifest = bundle(reader, root, cur, &keys, &out, &with, &pages)?;
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
    if l7r_guard::shared::py_text::strip(&reply).is_empty() {
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
    reader: &mut Reader,
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
        PathBuf::from(DEFAULT_OUT).join("claims-triage")
    } else {
        PathBuf::from(path_text(out))
    };
    let manifest = triage_bundle(reader, cur, &index, store, &keys, &qdir, &tout)?;
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
    if l7r_guard::shared::py_text::strip(&reply).is_empty() {
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

fn accept_cmd(
    reader: &mut Reader,
    root: &Path,
    cur: &Cur,
    index: &Index,
    p: &Parsed,
    o: &mut Out,
) -> Result<i32, Fail> {
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
    let made = bundle(reader, root, cur, &keys, &tmp, &[], &[])
        .and_then(|_| load_units(&tmp.join("units.json")));
    let _ = std::fs::remove_dir_all(&tmp);
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

fn carry_cmd(reader: &mut Reader, root: &Path, p: &Parsed, o: &mut Out) -> Result<i32, Fail> {
    let (keys_text, ruling) = (p.text("--keys", ""), p.text("--ruling", ""));
    let attempt = (|| -> Result<Result<String, String>, Fail> {
        if keys_text.is_empty() != ruling.is_empty() {
            return Ok(Err("KEYS= and RULING= go together: the findings a round-arbiter ruling carried, and that ruling's trigger".to_owned()));
        }
        let keys: Vec<String> = if keys_text.is_empty() {
            let at = reading(reader, root)?;
            let (_, _, _, carried) = classified(reader, root, &at)?;
            let done = super::carry::filed(super::carry::target(root)?.as_deref())?;
            carried
                .into_iter()
                .map(|(k, _)| k)
                .filter(|k| !done.contains_key(k))
                .collect()
        } else {
            keys_text
                .split(';')
                .map(l7r_guard::shared::py_text::strip)
                .filter(|k| !k.is_empty())
                .map(str::to_owned)
                .collect()
        };
        Ok(carry(
            root,
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
fn reading(reader: &mut Reader, root: &Path) -> Result<Reading, Fail> {
    let pairs = all_units(reader, root, false, true)?;
    Ok(Reading {
        cur: rows_of(pairs, &root.join(QUESTIONS))?,
        index: load_map(&root.join(INDEX))?,
    })
}

fn gate_cmd(reader: &mut Reader, root: &Path, o: &mut Out) -> Result<i32, Fail> {
    let pairs = all_units(reader, root, false, true)?;
    let at = Reading {
        cur: rows_of(pairs.clone(), &root.join(QUESTIONS))?,
        index: load_map(&root.join(INDEX))?,
    };
    let (mut refuse, warn) = carry_gate(reader, root, &at)?;
    refuse.extend(delta_form_problems(root, &pairs));
    for w in &warn {
        o.say(&format!("claims-gate: {w}"));
    }
    for x in &refuse {
        o.say(&format!("claims-gate: REFUSED {x}"));
    }
    Ok(i32::from(!refuse.is_empty()))
}

fn coverage_cmd(reader: &mut Reader, root: &Path, p: &Parsed, o: &mut Out) -> Result<i32, Fail> {
    let path = p.text("--path", "");
    let pairs = all_units(reader, root, false, true)?;
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
    let mut reader = Reader::new(&crate::record::repo::tree_of(root), root);
    match cmd {
        "gate" => return gate_cmd(&mut reader, root, o),
        "carry" => return carry_cmd(&mut reader, root, p, o),
        "known" => {
            let at = reading(&mut reader, root)?;
            let written = record_known(&mut reader, root, &at)?;
            if written.is_empty() {
                o.say("claims-known: no known drift is unrecorded");
            }
            for w in written {
                o.say(&format!("claims-known: recorded {w}"));
            }
            return Ok(0);
        }
        "coverage" => return coverage_cmd(&mut reader, root, p, o),
        _ => {}
    }
    let pairs = all_units(&mut reader, root, false, true)?;
    let cur = rows_of(pairs.clone(), &root.join(QUESTIONS))?;
    let index = load_map(&root.join(INDEX))?;
    let index = counters_clear(&mut reader, root, &cur, index, cmd, o)?;
    let (qdir, store) = (root.join(QUESTIONS), load_map(&root.join(STORE))?);
    match cmd {
        "refingerprint" => {
            let mut index = index;
            let old = codes(&all_units(&mut reader, root, false, false)?);
            let n = refingerprint(&mut index, &old, &codes(&pairs));
            if n > 0 {
                save_index(&root.join(INDEX), &index)?;
            }
            o.say(&format!("claims-refingerprint: {n} claim row(s) carried to the fingerprint the star re-exports give, their code otherwise unchanged"));
            Ok(0)
        }
        "rekey" => {
            let mut index = index;
            let n = rekey(&cur, &mut index);
            if n > 0 {
                save_index(&root.join(INDEX), &index)?;
            }
            o.say(&format!(
                "claims-rekey: {n} claim row(s) carried to the file their unit moved to"
            ));
            Ok(0)
        }
        "accept" => accept_cmd(&mut reader, root, &cur, &index, p, o),
        "owed" => owed_cmd(&mut reader, root, &pairs, &cur, &index, &store, o),
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
        "triage" => triage_cmd(&mut reader, root, &cur, index, &store, p, o),
        "triaged" => triaged_cmd(root, &cur, &index, &store, p, o),
        "report" => {
            let deferred = load_deferred(&root.join(DEFERRED))?;
            let text = report(&cur, &index, &qdir, &store, &deferred, p.on("--all"))?;
            o.out
                .push_str(&super::pager::page(&text, &super::pager::Screen::here()));
            Ok(0)
        }
        "bundle" => bundle_cmd(&mut reader, root, &cur, &index, &store, p, o),
        _ => record_cmd(root, &cur, &index, &store, p, o),
    }
}

#[cfg(test)]
mod more;
#[cfg(test)]
mod tests;
