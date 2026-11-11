//! The claims TRIAGE (`scripts/record/claims_triage.py`, ported by feature 449 T82): one cheap agent over what changed, so a claim is
//! re-judged only when a change bears on it - a cited page's new, changed or removed blocks, a procedure section's, a unit's diff.

#![expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "Python's `str.endswith`, which this port keeps, is case-sensitive"
)]

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks::pages::read_page;
use l7r_guard::shared::pyjson::{dumps, sorted};
use serde_json::{json, Map, Value};

use super::index::{
    field, findings_of, page_blocks, page_name, Cur, Index, PageMemo, Store, INDEX, QUESTIONS,
};
use super::reply::bare;
use super::scope::Reader;
use super::units::{doc_units, from_json};
use crate::record::bundle::py_str;
use crate::record::repo::{fail, git, Fail};
use crate::record::units::{digest, re};

/// The page texts a snapshot was taken of, kept as git blobs in the clone (feature 375 T04): `{findings digest: blob sha}`.
pub(crate) const BLOBS: &str = "claims-page-blobs.json";
/// What a claim cleared without a triage records (feature 432, FR-005 a, plan D7).
pub(crate) const CLEARED: &str =
    "mechanically: a page it cites moved and no block it rests on did (feature 432)";

static TOUCHES: LazyLock<Regex> = LazyLock::new(|| re(r"\ATOUCHES\s+(\S.*?)\s+-\s+(.*)\z"));
pub(crate) static HUNK: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@"));
static QUESTION_PATH: LazyLock<Regex> = LazyLock::new(|| re(r"research/questions/[\w.-]+?\.html"));

fn blob_map(qdir: &Path) -> Option<std::path::PathBuf> {
    let common = git(
        qdir,
        &["rev-parse", "--path-format=absolute", "--git-common-dir"],
    );
    let common = l7r_guard::shared::py_text::strip(&common);
    (!common.is_empty()).then(|| Path::new(common).join(BLOBS))
}

/// Each page a recorded snapshot was taken of kept as a git blob, while the page still stands at it (feature 375 T04).
pub(crate) fn keep_texts(qdir: &Path, units: &Map<String, Value>) -> Result<usize, Fail> {
    let mut pages: BTreeMap<String, String> = BTreeMap::new();
    for u in units.values() {
        for (name, fp) in u
            .get("pages")
            .and_then(Value::as_object)
            .into_iter()
            .flatten()
        {
            pages.insert(name.clone(), fp.as_str().unwrap_or_default().to_owned());
        }
    }
    let Some(path) = blob_map(qdir) else {
        return Ok(0);
    };
    if pages.is_empty() {
        return Ok(0);
    }
    let mut blobs = super::index::load_map(&path)?;
    let mut kept = 0;
    for (name, fp) in &pages {
        let f = qdir.join(name);
        if blobs.contains_key(fp) || !f.is_file() {
            continue;
        }
        let text = crate::record::repo::read_text(&f)?;
        if findings_of(&text) != *fp {
            continue;
        }
        let sha = crate::claims::stdin_git(qdir, &["hash-object", "-w", "--stdin"], &text);
        if let Some(sha) = sha {
            blobs.insert(fp.clone(), json!(l7r_guard::shared::py_text::strip(&sha)));
            kept += 1;
        }
    }
    if kept > 0 {
        std::fs::write(
            &path,
            dumps(&sorted(&Value::Object(blobs)), Some(0), true) + "\n",
        )
        .map_err(fail)?;
    }
    Ok(kept)
}

/// The text of the page snapshot `fp`, from the clone's kept blobs, or "".
pub(crate) fn kept_text(qdir: &Path, fp: &str) -> Result<String, Fail> {
    let blob = match blob_map(qdir) {
        Some(p) if p.is_file() => field(&Value::Object(super::index::load_map(&p)?), fp).to_owned(),
        _ => String::new(),
    };
    Ok(if blob.is_empty() {
        String::new()
    } else {
        git(qdir, &["cat-file", "-p", &blob])
    })
}

/// The words of the blocks `digests` of the question `name` that no longer stand: the snapshot's kept text, then the page's history.
pub(crate) fn removed_words(
    qdir: &Path,
    name: &str,
    digests: &HashSet<String>,
    snapshot: &str,
) -> Result<BTreeMap<String, String>, Fail> {
    let mut found = BTreeMap::new();
    let mut texts = Vec::new();
    if !snapshot.is_empty() {
        texts.push(kept_text(qdir, snapshot)?);
    }
    for sha in git(qdir, &["log", "--format=%H", "-60", "--", name]).split_whitespace() {
        texts.push(git(qdir, &["show", &format!("{sha}:./{name}")]));
    }
    for text in texts {
        for b in read_page(&text).blocks {
            let d = digest(&[&b.words]);
            if digests.contains(&d) && !b.intro {
                found.entry(d).or_insert(b.words);
            }
        }
        if found.len() == digests.len() {
            break;
        }
    }
    Ok(found)
}

/// The words of the blocks `digests` of the procedure section `title` of `path` that no longer stand, from its history (a claimed dictionary's from its module's, by the Python's reader).
pub(crate) fn section_words(
    reader: &mut Reader,
    root: &Path,
    path: &str,
    title: &str,
    digests: &HashSet<String>,
) -> Result<BTreeMap<String, String>, Fail> {
    let mut found = BTreeMap::new();
    for sha in git(root, &["log", "--format=%H", "-60", "--", path]).split_whitespace() {
        let text = git(root, &["show", &format!("{sha}:{path}")]);
        let units = if path.ends_with(".py") {
            let got = reader.ask("claims_module_units", &json!([text, path]))?;
            got.as_array()
                .into_iter()
                .flatten()
                .map(|v| from_json(v).0)
                .collect()
        } else {
            doc_units(&text, path, None)
        };
        for unit in units.iter().filter(|u| u.qualname == title) {
            for b in &unit.blocks {
                let d = digest(&[b]);
                if digests.contains(&d) {
                    found.entry(d).or_insert_with(|| b.clone());
                }
            }
        }
        if found.len() == digests.len() {
            break;
        }
    }
    Ok(found)
}

/// The newest commit of the claims index recording `key` checked at the code fingerprint `code`, or `origin/main`.
pub(crate) fn checked_at(
    root: &Path,
    key: &str,
    code: &str,
    seen: &mut HashMap<String, Value>,
    log: &mut Option<Vec<String>>,
) -> String {
    let shas = log.get_or_insert_with(|| {
        git(root, &["log", "-n60", "--format=%H", "--", INDEX])
            .split_whitespace()
            .map(str::to_owned)
            .collect()
    });
    for sha in shas.iter() {
        let at = seen.entry(sha.clone()).or_insert_with(|| {
            let text = git(root, &["show", &format!("{sha}:{INDEX}")]);
            serde_json::from_str(if text.is_empty() { "{}" } else { &text })
                .unwrap_or_else(|_| json!({}))
        });
        if at
            .get(key)
            .and_then(|r| r.get("code"))
            .and_then(Value::as_str)
            == Some(code)
        {
            return sha.clone();
        }
    }
    "origin/main".to_owned()
}

/// The hunks of `git diff base -- path` whose new lines overlap [lo, hi].
pub(crate) fn code_hunks(root: &Path, path: &str, lo: usize, hi: usize, base: &str) -> Vec<String> {
    let diff = git(root, &["diff", "-U3", base, "--", path]);
    let found: Vec<(usize, usize, usize)> = HUNK
        .captures_iter(&diff)
        .flatten()
        .map(|c| {
            let first: usize = c[1].parse().unwrap_or(0);
            let n: usize = c.get(2).map_or(1, |g| g.as_str().parse().unwrap_or(0));
            (
                c.get(0).map_or(0, |g| g.start()),
                first,
                first + n.max(1) - 1,
            )
        })
        .collect();
    let mut out = Vec::new();
    for (i, (a, first, last)) in found.iter().enumerate() {
        let b = found.get(i + 1).map_or(diff.len(), |n| n.0);
        if *first <= hi && *last >= lo {
            out.push(diff[*a..b].trim_end_matches('\n').to_owned());
        }
    }
    out
}

/// A procedure section's (new or changed blocks, removed blocks, claims).
type Section = (Vec<String>, Vec<String>, Vec<String>);

/// What the triage bundle gathers of each kind of change.
#[derive(Default)]
struct Gathered {
    by_page: BTreeMap<(String, String), Vec<String>>,
    changed: HashMap<String, Vec<String>>,
    gone: HashMap<String, Vec<String>>,
    lost: HashMap<(String, String), bool>,
    forced: BTreeSet<String>,
    sections: BTreeMap<String, Section>,
    codes: BTreeMap<String, (Vec<String>, Vec<String>)>,
}

fn last_verdict(index: &Index, k: &str) -> (String, String) {
    let row = index.get(k);
    let verdict = row.and_then(|r| r.get("verdict")).unwrap_or(&Value::Null);
    let note = row
        .and_then(|r| r.get("note"))
        .map_or_else(String::new, py_str);
    (py_str(verdict), note)
}

fn gather_code(
    g: &mut Gathered,
    cur: &Cur,
    index: &Index,
    key: &str,
    root: &Path,
    seen: &mut HashMap<String, Value>,
    log: &mut Option<Vec<String>>,
) {
    let row = cur.get(key).unwrap_or_else(|| unreachable!());
    let was_code = index.get(key).and_then(|r| r.get("code"));
    if was_code.and_then(Value::as_str) == Some(&row.code) {
        return;
    }
    let uid = row.uid();
    if !g.codes.contains_key(&uid) {
        let shown = py_str(was_code.unwrap_or(&Value::Null));
        let base = checked_at(root, key, &shown, seen, log);
        let hunks = code_hunks(
            root,
            &row.unit.path,
            row.unit.lineno,
            row.unit.end_lineno,
            &base,
        );
        g.codes.insert(uid.clone(), (hunks, Vec::new()));
    }
    let entry = g.codes.get_mut(&uid).unwrap_or_else(|| unreachable!());
    entry.1.push(key.to_owned());
    let line = l7r_guard::shared::py_text::strip(&row.claim.line);
    let added = entry
        .0
        .iter()
        .flat_map(|h| h.split('\n'))
        .filter_map(|x| x.strip_prefix('+'))
        .map(l7r_guard::shared::py_text::strip);
    let mut hit = false;
    for x in added {
        if !line.is_empty() && x.contains(line) {
            hit = true;
            break;
        }
    }
    if entry.0.is_empty() || hit {
        g.forced.insert(key.to_owned());
    }
}

fn gather_section(
    g: &mut Gathered,
    reader: &mut Reader,
    cur: &Cur,
    index: &Index,
    store: &Store,
    key: &str,
    root: &Path,
) -> Result<(), Fail> {
    let row = cur.get(key).unwrap_or_else(|| unreachable!());
    let unit = &row.unit;
    let section = index.get(key).and_then(|r| r.get("section"));
    if !unit.line_keyed()
        || section.is_none_or(Value::is_null)
        || section.and_then(Value::as_str) == Some(&unit.core)
    {
        return Ok(());
    }
    let before: HashSet<String> = store
        .get(section.and_then(Value::as_str).unwrap_or_default())
        .and_then(Value::as_array)
        .map(|a| {
            a.iter()
                .filter_map(|v| v.as_str().map(str::to_owned))
                .collect()
        })
        .unwrap_or_default();
    let fresh: Vec<&String> = unit
        .blocks
        .iter()
        .filter(|b| !before.contains(&digest(&[b])))
        .collect();
    let now: HashSet<String> = unit.blocks.iter().map(|b| digest(&[b])).collect();
    let missing: HashSet<String> = before.difference(&now).cloned().collect();
    let words = if missing.is_empty() {
        BTreeMap::new()
    } else {
        section_words(reader, root, &unit.path, &unit.qualname, &missing)?
    };
    if words.len() < missing.len() {
        g.forced.insert(key.to_owned());
    }
    let got = g
        .sections
        .entry(format!("{}::{}", unit.path, unit.qualname))
        .or_default();
    for w in fresh {
        if !got.0.contains(w) {
            got.0.push(w.clone());
        }
    }
    for w in words.values() {
        if !got.1.contains(w) {
            got.1.push(w.clone());
        }
    }
    got.2.push(key.to_owned());
    Ok(())
}

fn gather_pages(
    g: &mut Gathered,
    index: &Index,
    store: &Store,
    key: &str,
    qdir: &Path,
    memo: &mut PageMemo,
) -> Result<(), Fail> {
    let pages: Vec<(String, String)> = index
        .get(key)
        .and_then(|r| r.get("pages"))
        .and_then(Value::as_object)
        .into_iter()
        .flatten()
        .map(|(n, v)| (n.clone(), v.as_str().unwrap_or_default().to_owned()))
        .collect();
    for (name, old) in pages {
        let (fp, blocks) = page_blocks(&name, qdir, memo)?.clone();
        if fp == old {
            continue;
        }
        let before: HashSet<String> = store
            .get(&old)
            .and_then(Value::as_array)
            .map(|a| {
                a.iter()
                    .filter_map(|v| v.as_str().map(str::to_owned))
                    .collect()
            })
            .unwrap_or_default();
        let now: HashSet<&String> = blocks.iter().map(|(d, _)| d).collect();
        let fresh: Vec<String> = blocks
            .iter()
            .filter(|(d, _)| !before.contains(d))
            .map(|(_, w)| w.clone())
            .collect();
        let pair = (name.clone(), old.clone());
        let tag = format!("{name}|{old}");
        if !g.lost.contains_key(&pair) {
            let missing: HashSet<String> = before
                .iter()
                .filter(|d| !now.contains(d))
                .cloned()
                .collect();
            let words = if missing.is_empty() {
                BTreeMap::new()
            } else {
                removed_words(qdir, &name, &missing, &old)?
            };
            let mut ordered: Vec<&String> = missing.iter().collect();
            ordered.sort();
            g.gone.insert(
                tag.clone(),
                ordered
                    .iter()
                    .filter_map(|d| words.get(*d).cloned())
                    .collect(),
            );
            g.lost.insert(pair.clone(), words.len() < missing.len());
        }
        if g.lost[&pair] {
            g.forced.insert(key.to_owned());
        }
        if !fresh.is_empty() || !g.gone[&tag].is_empty() {
            g.changed.insert(tag, fresh);
            g.by_page.entry(pair).or_default().push(key.to_owned());
        }
    }
    Ok(())
}

fn claims_list(parts: &mut Vec<String>, cur: &Cur, index: &Index, keys: &[String]) {
    let mut keys: Vec<&String> = keys.iter().collect();
    keys.sort();
    for k in keys {
        let (verdict, note) = last_verdict(index, k);
        let line = &cur.get(k).unwrap_or_else(|| unreachable!()).claim.line;
        parts.push(format!(
            "- KEY `{k}`: `{line}` - last verdict {verdict}: {note}"
        ));
    }
    parts.push(String::new());
}

fn quoted(words: &[String]) -> Vec<String> {
    words.iter().map(|w| format!("> {w}\n")).collect()
}

fn manifest(g: &Gathered, cur: &Cur, index: &Index) -> String {
    let mut parts = vec![
        "# Triage of claim re-checks (feature 318)\n".to_owned(),
        "owed-checks: claims-triage\n".to_owned(),
        "For the `claims-triage` agent: rule on each claim below as your contract says, and reply in its form.\n".to_owned(),
    ];
    for (place, (fresh, lost, ks)) in &g.sections {
        parts.push(format!("## {place} (a procedure section; the claims' own lines did not change)\n\nNew or changed blocks:\n"));
        let shown = quoted(fresh);
        parts.extend(if shown.is_empty() {
            vec!["(none)\n".to_owned()]
        } else {
            shown
        });
        if !lost.is_empty() {
            parts.push("Removed blocks (no longer in the section):\n".to_owned());
            parts.extend(quoted(lost));
        }
        parts.push("Claims in it:\n".to_owned());
        claims_list(&mut parts, cur, index, ks);
    }
    for (uid, (hunks, ks)) in &g.codes {
        if hunks.is_empty() {
            continue;
        }
        parts.push(format!(
            "## {uid} (a unit of code; its diff against origin/main)\n\n```diff\n{}\n```\n",
            hunks.join("\n")
        ));
        parts.push("Claims in it:\n".to_owned());
        claims_list(&mut parts, cur, index, ks);
    }
    for ((name, old), ks) in &g.by_page {
        let tag = format!("{name}|{old}");
        let short: String = old.chars().take(12).collect();
        parts.push(format!("## {QUESTIONS}/{name}\n\n(against the version these claims were last checked at, {short})\n\nNew or changed blocks:\n"));
        let shown = quoted(&g.changed[&tag]);
        parts.extend(if shown.is_empty() {
            vec!["(none)\n".to_owned()]
        } else {
            shown
        });
        if g.gone.get(&tag).is_some_and(|v| !v.is_empty()) {
            parts.push("Removed blocks (no longer on the page):\n".to_owned());
            parts.extend(quoted(&g.gone[&tag]));
        }
        parts.push("Claims citing it:\n".to_owned());
        claims_list(&mut parts, cur, index, ks);
    }
    parts.join("\n") + "\n"
}

/// The triage bundle for `keys`: MANIFEST.md, and triage.json (each claim's fingerprints now, today's snapshots, the forced claims).
pub(crate) fn triage_bundle(
    reader: &mut Reader,
    cur: &Cur,
    index: &Index,
    store: &Store,
    keys: &[String],
    qdir: &Path,
    out: &Path,
) -> Result<std::path::PathBuf, Fail> {
    if out.exists() {
        std::fs::remove_dir_all(out).map_err(fail)?;
    }
    std::fs::create_dir_all(out).map_err(fail)?;
    let root = qdir
        .parent()
        .and_then(Path::parent)
        .unwrap_or(Path::new(""))
        .to_path_buf();
    let mut memo = PageMemo::default();
    let mut g = Gathered::default();
    let (mut seen, mut log) = (HashMap::new(), None);
    for key in keys {
        if !index.contains_key(key) {
            g.forced.insert(key.clone());
        }
        gather_code(&mut g, cur, index, key, &root, &mut seen, &mut log);
        gather_section(&mut g, reader, cur, index, store, key, &root)?;
        gather_pages(&mut g, index, store, key, qdir, &mut memo)?;
    }
    let mut shown: HashSet<&String> = g.by_page.values().flatten().collect();
    shown.extend(g.sections.values().flat_map(|s| &s.2));
    shown.extend(
        g.codes
            .values()
            .filter(|c| !c.0.is_empty())
            .flat_map(|c| &c.1),
    );
    let unshown: Vec<String> = keys
        .iter()
        .filter(|k| !shown.contains(k))
        .cloned()
        .collect();
    g.forced.extend(unshown);
    std::fs::write(out.join("MANIFEST.md"), manifest(&g, cur, index)).map_err(fail)?;
    let mut units = Map::new();
    for k in keys {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        let mut u = Map::new();
        u.insert("research".into(), json!(row.research));
        let mut pages = Map::new();
        for ptr in &row.claim.pointers {
            let name = page_name(ptr);
            pages.insert(
                name.to_owned(),
                json!(page_blocks(name, qdir, &mut memo)?.0),
            );
        }
        u.insert("pages".into(), Value::Object(pages));
        if row.unit.line_keyed() {
            u.insert("section".into(), json!(row.unit.core));
        }
        if index
            .get(k)
            .and_then(|r| r.get("code"))
            .and_then(Value::as_str)
            != Some(&row.code)
        {
            u.insert("code".into(), json!(row.code));
            u.insert("core".into(), json!(row.unit.core));
        }
        units.insert(k.clone(), Value::Object(u));
    }
    let mut snaps = memo.snapshots();
    for k in keys {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        if row.unit.line_keyed() {
            snaps.insert(
                row.unit.core.clone(),
                json!(row
                    .unit
                    .blocks
                    .iter()
                    .map(|b| digest(&[b]))
                    .collect::<Vec<_>>()),
            );
        }
    }
    let data = json!({"units": units, "snapshots": snaps, "forced": g.forced.into_iter().collect::<Vec<_>>()});
    std::fs::write(
        out.join("triage.json"),
        dumps(&sorted(&data), Some(1), true) + "\n",
    )
    .map_err(fail)?;
    Ok(out.join("MANIFEST.md"))
}

/// The index with a triage reply applied: a named or forced claim owed `impl-drift`, every other one cleared at the pages as they stand.
pub(crate) fn record_triage(
    index: &Index,
    units: &Map<String, Value>,
    reply: &str,
    today: &str,
    forced: &[String],
) -> (Index, Vec<String>) {
    let mut touched: BTreeMap<String, String> = BTreeMap::new();
    for raw in reply.split('\n') {
        if let Some(m) = TOUCHES.captures(bare(raw)).ok().flatten() {
            touched.insert(m[1].trim_matches('`').to_owned(), m[2].to_owned());
        }
    }
    let mut msgs: Vec<String> = touched
        .keys()
        .filter(|k| !units.contains_key(*k))
        .map(|k| format!("refused: `{k}` is not a claim of this triage"))
        .collect();
    for k in forced {
        if units.contains_key(k) && !touched.contains_key(k) {
            touched.insert(
                k.clone(),
                "a removed block the history no longer shows".to_owned(),
            );
        }
    }
    let mut out = index.clone();
    let by_key: BTreeMap<&String, &Value> = units.iter().collect();
    for (key, fp) in by_key {
        let mut row = out
            .get(key)
            .and_then(Value::as_object)
            .cloned()
            .unwrap_or_default();
        if let Some(why) = touched.get(key) {
            row.insert("triage".into(), json!("touched"));
            msgs.push(format!("touched: {key} - {why}"));
        } else {
            row.insert("research".into(), fp["research"].clone());
            row.insert("pages".into(), fp["pages"].clone());
            row.insert("triaged".into(), json!(today));
            for f in ["section", "code", "core"] {
                if let Some(v) = fp.get(f) {
                    row.insert(f.into(), v.clone());
                }
            }
            row.shift_remove("triage");
        }
        out.insert(key.clone(), Value::Object(row));
    }
    (out, msgs)
}

/// (the index with `keys` cleared, the page snapshots to store): each claim owed a triage only because a cited page moved while every block it rests on stands (feature 432).
pub(crate) fn clear_page_moves(
    cur: &Cur,
    index: &Index,
    keys: &[String],
    qdir: &Path,
    today: &str,
) -> Result<(Index, Store), Fail> {
    let mut memo = PageMemo::default();
    let mut out = index.clone();
    for k in keys {
        let row = cur.get(k).unwrap_or_else(|| unreachable!());
        let mut pages = Map::new();
        for ptr in &row.claim.pointers {
            let name = page_name(ptr);
            pages.insert(
                name.to_owned(),
                json!(page_blocks(name, qdir, &mut memo)?.0),
            );
        }
        let mut r = out
            .get(k)
            .and_then(Value::as_object)
            .cloned()
            .unwrap_or_default();
        r.insert("research".into(), json!(row.research));
        r.insert("pages".into(), Value::Object(pages));
        r.insert("triaged".into(), json!(today));
        r.insert("cleared".into(), json!(CLEARED));
        r.shift_remove("triage");
        out.insert(k.clone(), Value::Object(r));
    }
    Ok((out, memo.snapshots()))
}

/// The reply without its VERDICT lines that cannot be recorded as written, and those lines; the outside-the-change rows filed; what was said.
pub(crate) fn vet(
    reply: &str,
    units: &Map<String, Value>,
    root: &Path,
    said: &mut String,
    warned: &mut String,
) -> Result<(String, Vec<String>), Fail> {
    let (mut keep, mut bad) = (Vec::new(), Vec::new());
    for raw in reply.split('\n') {
        let line = bare(raw);
        if line.starts_with("VERDICT ") {
            let m = super::reply::VERDICT.captures(line).ok().flatten();
            let gone: Vec<String> = QUESTION_PATH
                .find_iter(line)
                .flatten()
                .map(|p| p.as_str().to_owned())
                .filter(|p| !root.join(p).is_file())
                .collect();
            let why = match &m {
                None => "no verdict it can read".to_owned(),
                Some(m) if !units.contains_key(m[1].trim_matches('`')) => {
                    "not a claim of this bundle".to_owned()
                }
                Some(_) if !gone.is_empty() => {
                    format!("no such question file: {}", gone.join(", "))
                }
                Some(_) => String::new(),
            };
            if !why.is_empty() {
                let cut: String = line.chars().take(160).collect();
                bad.push(format!("{why}: {cut}"));
                continue;
            }
        }
        keep.push(raw);
    }
    for row in crate::record::owed::answers::file_outside(root, "impl-drift", reply)? {
        let get = |k: &str| {
            row.get(k)
                .and_then(Value::as_str)
                .unwrap_or_default()
                .to_owned()
        };
        let _ = writeln!(
            said,
            "claims-checked: filed, not fixed - {} | {} | {}",
            get("file"),
            get("block"),
            get("finding")
        );
    }
    for b in &bad {
        let _ = writeln!(warned, "claims-checked: REFUSED line - {b}");
    }
    if !bad.is_empty() {
        warned.push_str("claims-checked: correct each refused line in the reply file (the claim's path as the bundle names it; a verdict of IN-STEP, DRIFTED, NEEDS-RESEARCH, MISLABELED or CANNOT-TELL; a pointer to a question file that exists) and run it again - the lines it recorded stay recorded\n");
    }
    Ok((keep.join("\n"), bad))
}

/// The reply `make <cmd>` is given, a transcript's last reply (`apply_edits.reply_of`, by command); with no text, the refusal said and "" returned.
pub(crate) fn read_reply(
    root: &Path,
    path: &str,
    cmd: &str,
    nothing: &str,
    warned: &mut String,
) -> Result<String, Fail> {
    let reply = crate::record::owed::answers::reply_of(root, path)?;
    if l7r_guard::shared::py_text::strip(&reply).is_empty() {
        let _ = writeln!(
            warned,
            "{cmd}: refused - no reply text in {path}; {nothing}"
        );
    }
    Ok(reply)
}

#[cfg(test)]
mod tests;
