//! The claims TRIAGE (`scripts/record/claims_triage.py`, ported by feature 449 T82): one cheap agent over what changed, so a claim is
//! re-judged only when a change bears on it - a cited page's new, changed or removed blocks, a procedure section's, a unit's diff.

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use crate::record::triage::change;
use fancy_regex::Regex;
use l7r_shared::pyjson::{dumps, sorted};
use serde_json::{json, Map, Value};

use super::bundle::read_pages;
use super::index::{code_kept, page_blocks, Cur, Index, PageMemo, Store, INDEX, QUESTIONS};
use super::reply::bare;
use crate::record::bundle::py_str;
use crate::record::repo::{fail, git, Fail};
use crate::record::units::{digest, re};

/// The page texts a snapshot was taken of, kept as git blobs in the clone (feature 375 T04): `{findings digest: blob sha}`.
pub const BLOBS: &str = "claims-page-blobs.json";
/// What a claim cleared without a triage records (feature 432, FR-005 a, plan D7).
pub const CLEARED: &str =
    "mechanically: a page it cites moved and no block it rests on did (feature 432)";
/// What a claim T186's filter cleared records (feature 451 T191).
pub const TOOL_CLEARED: &str =
    "by the tool: no edit of the text it rests on is claim-bearing (feature 451 T191)";

static TOUCHES: LazyLock<Regex> = LazyLock::new(|| re(r"\ATOUCHES\s+(\S.*?)\s+-\s+(.*)\z"));
pub static HUNK: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@"));
static QUESTION_PATH: LazyLock<Regex> = LazyLock::new(|| re(r"research/questions/[\w.-]+?\.html"));
/// This module's patterns, for the command's start to compile side by side ([`super::warm`], feature 449 T167).
pub(super) static WARM: [&LazyLock<Regex>; 3] = [&TOUCHES, &HUNK, &QUESTION_PATH];

mod kept;
pub use kept::{
    keep_sections, keep_texts, kept_text, removed_words, section_texts, section_words,
    SECTION_TEXTS,
};

/// The newest commit of the claims index recording `key` checked at the code fingerprint `code`, or `origin/main`.
pub fn checked_at(
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
pub fn code_hunks(root: &Path, path: &str, lo: usize, hi: usize, base: &str) -> Vec<String> {
    let diff = git(root, &["diff", "-U3", base, "--", path]);
    let found: Vec<(usize, usize, usize)> = HUNK
        .captures_iter(&diff)
        .map_while(Result::ok)
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

/// One changed page or procedure section as the claims citing it read it (feature 451 T191): what is left of its edit after the tool's
/// clears ([`change::blocks_change`], T186's, shared), its blocks now, the pages its pointers reach, and the new findings it adds.
#[derive(Default)]
struct Moved {
    change: change::Change,
    now: Vec<String>,
    reached: HashSet<String>,
    found: Vec<String>,
}

impl Moved {
    /// Why this edit still owes the claim reading `claim` its triage, or None: T186's first filter, [`change::fires`], the claim the
    /// reader (no note key is a claim's, so none gone counts), and the echo read from a rewrite's new side too,
    /// [`change::echo_rewritten`].
    fn fires(&self, claim: &str) -> Option<String> {
        if self.change.is_clear() {
            return None;
        }
        change::fires(&self.change, &self.now, &self.reached, claim, &self.found)
            .or_else(|| change::echo_rewritten(&self.change, claim))
    }

    /// Its blocks for the MANIFEST: (new or changed, removed or changed from, moved with an edit as shown); a block moved with an
    /// edit to a page the pointers reach is shown as moved, with its diff, never as removed (451 T196, T194's for the pop-ups).
    fn shown(&self) -> (Vec<String>, Vec<String>, Vec<String>) {
        let c = &self.change;
        (
            c.pairs
                .iter()
                .map(|p| p.1.clone())
                .chain(c.added.iter().cloned())
                .collect(),
            c.pairs
                .iter()
                .map(|p| p.0.clone())
                .chain(change::removed_unmoved(c))
                .collect(),
            change::moved_edited_lines(c, "a page its pointers reach"),
        )
    }
}

/// What the triage bundle gathers of each kind of change.
#[derive(Default)]
struct Gathered {
    /// (page, the snapshot its claims were checked at) -> the claims citing it.
    by_page: BTreeMap<(String, String), Vec<String>>,
    pages: HashMap<String, Moved>,
    lost: HashMap<(String, String), bool>,
    /// `path::section|snapshot` -> whether a removed block's words could not be found (451 T210).
    section_lost: HashMap<String, bool>,
    forced: BTreeSet<String>,
    /// `path::section` -> (its change, the claims in it).
    sections: BTreeMap<String, (Moved, Vec<String>)>,
    codes: BTreeMap<String, (Vec<String>, Vec<String>)>,
}

/// What a claim states, as the echo rule reads it: its label and account, without the question paths it cites.
fn claim_text(cur: &Cur, key: &str) -> String {
    let claim = &cur.get(key).unwrap_or_else(|| unreachable!()).claim;
    QUESTION_PATH
        .replace_all(&format!("{}. {}", claim.label, claim.account), " ")
        .into_owned()
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
    let was = index.get(key);
    if was.is_some_and(|w| code_kept(w, row)) {
        return;
    }
    let was_code = was.and_then(|r| r.get("code"));
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
    let line = l7r_shared::py_text::strip(&row.claim.line);
    let added = entry
        .0
        .iter()
        .flat_map(|h| h.split('\n'))
        .filter_map(|x| x.strip_prefix('+'))
        .map(l7r_shared::py_text::strip);
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
    let snapshot = section.and_then(Value::as_str).unwrap_or_default();
    let place = format!("{}::{}|{snapshot}", unit.path, unit.qualname);
    // each section's edit read once, its claims sharing it: its removed words were sought once a claim, 60 commits each (451 T210)
    if !g.sections.contains_key(&place) {
        let before: HashSet<String> = store
            .get(snapshot)
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
            section_words(root, &unit.path, &unit.qualname, &missing, snapshot)?
        };
        // a section's Markdown read as a page's words, so a link, markup or code-tick edit is cleared by the tool (feature 451 T191)
        let md = |w: &String| change::md_words(w);
        let was: Vec<String> = words.values().map(md).collect();
        let empty = HashSet::new();
        let c = change::blocks_change(
            &was,
            &fresh.iter().map(|w| md(w)).collect::<Vec<_>>(),
            &[],
            &empty,
            &empty,
            &[],
        );
        let found = c.added.clone();
        let moved = Moved {
            change: c,
            now: unit.blocks.iter().map(md).collect(),
            reached: HashSet::new(),
            found,
        };
        g.sections.insert(place.clone(), (moved, Vec::new()));
        // THE ONE FORCE LEFT (451 T210): a removed block whose words neither the kept snapshot nor the history holds - a snapshot taken
        // before T210 kept its words, or in another clone, of words no commit holds. No echo of the new words can see a claim that
        // repeated only the lost ones, so its claims are owed in full.
        g.section_lost
            .insert(place.clone(), words.len() < missing.len());
    }
    if g.section_lost[&place] {
        g.forced.insert(key.to_owned());
    }
    let got = g.sections.get_mut(&place).unwrap_or_else(|| unreachable!());
    got.1.push(key.to_owned());
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
        let pair = (name.clone(), old.clone());
        if !g.lost.contains_key(&pair) {
            let now: HashSet<&String> = blocks.iter().map(|(d, _)| d).collect();
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
            let was: Vec<String> = ordered
                .iter()
                .filter_map(|d| words.get(*d).cloned())
                .collect();
            let fresh: Vec<String> = blocks
                .iter()
                .filter(|(d, _)| !before.contains(d))
                .map(|(_, w)| w.clone())
                .collect();
            // a split is a move (feature 451 T185), and a marker, markup or link edit no claim (T186), both T186's change, shared
            let html = crate::record::repo::read_text(&qdir.join(&name)).unwrap_or_default();
            let reached = change::reached_by_pointers(&html, qdir);
            let c = change::blocks_change(
                &was,
                &fresh,
                &change::pointer_texts(&html),
                &reached,
                &HashSet::new(),
                &[],
            );
            let old_text = kept_text(qdir, &old)?;
            let found = if old_text.is_empty() {
                c.added.clone()
            } else {
                change::new_findings(&old_text, &html)
            };
            let moved = Moved {
                change: c,
                now: blocks.iter().map(|(_, w)| w.clone()).collect(),
                reached,
                found,
            };
            g.pages.insert(format!("{name}|{old}"), moved);
            g.lost.insert(pair.clone(), words.len() < missing.len());
        }
        if g.lost[&pair] {
            g.forced.insert(key.to_owned());
        }
        g.by_page.entry(pair).or_default().push(key.to_owned());
    }
    Ok(())
}

/// T186's first filter over the gathered changes, per claim (feature 451 T191; the GM 2026-11-23, the convergence talk): a page's or a
/// section's edit stays in the MANIFEST only for the claims it still owes - a forced claim, or one [`Moved::fires`] names; the claims
/// every edit of which is cleared, and no code hunk or forced check holds, are returned, cleared by the tool.
fn filter(g: &mut Gathered, cur: &Cur, index: &Index) -> BTreeSet<String> {
    let (mut held, mut seen) = (HashSet::new(), BTreeSet::new());
    let mut owes = |m: &Moved, ks: &mut Vec<String>, forced: &BTreeSet<String>| {
        ks.retain(|k| {
            seen.insert(k.clone());
            let keep = if forced.contains(k) {
                !m.change.is_clear()
            } else {
                m.fires(&claim_text(cur, k)).is_some()
            };
            if keep {
                held.insert(k.clone());
            }
            keep
        });
    };
    for ((name, old), ks) in &mut g.by_page {
        owes(&g.pages[&format!("{name}|{old}")], ks, &g.forced);
    }
    for (m, ks) in g.sections.values_mut() {
        owes(m, ks, &g.forced);
    }
    g.by_page.retain(|_, ks| !ks.is_empty());
    g.sections.retain(|_, s| !s.1.is_empty());
    held.extend(
        g.codes
            .values()
            .filter(|c| !c.0.is_empty())
            .flat_map(|c| c.1.iter().cloned()),
    );
    seen.into_iter()
        .filter(|k| !held.contains(k) && !g.forced.contains(k) && index.contains_key(k))
        .collect()
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
    for (place, (m, ks)) in &g.sections {
        let (fresh, lost, moved) = m.shown();
        let place = place.rsplit_once('|').map_or(place.as_str(), |p| p.0);
        parts.push(format!("## {place} (a procedure section; the claims' own lines did not change)\n\nNew or changed blocks:\n"));
        let shown = quoted(&fresh);
        parts.extend(if shown.is_empty() {
            vec!["(none)\n".to_owned()]
        } else {
            shown
        });
        if !lost.is_empty() {
            parts.push("Removed blocks (no longer in the section):\n".to_owned());
            parts.extend(quoted(&lost));
        }
        parts.extend(moved);
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
        let (fresh, gone, moved) = g.pages[&tag].shown();
        let shown = quoted(&fresh);
        parts.extend(if shown.is_empty() {
            vec!["(none)\n".to_owned()]
        } else {
            shown
        });
        if !gone.is_empty() {
            parts.push("Removed blocks (no longer on the page):\n".to_owned());
            parts.extend(quoted(&gone));
        }
        parts.extend(moved);
        parts.push("Claims citing it:\n".to_owned());
        claims_list(&mut parts, cur, index, ks);
    }
    parts.join("\n") + "\n"
}

/// The triage bundle for `keys`: MANIFEST.md, and triage.json (each claim's fingerprints now, today's snapshots, the forced claims;
/// under `cleared`, the claims T186's filter cleared by the tool, feature 451 T191, which the MANIFEST does not name).
pub fn triage_bundle(
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
        gather_section(&mut g, cur, index, store, key, &root)?;
        gather_pages(&mut g, index, store, key, qdir, &mut memo)?;
    }
    let cleared = filter(&mut g, cur, index);
    let mut shown: HashSet<&String> = g.by_page.values().flatten().collect();
    shown.extend(cleared.iter());
    shown.extend(g.sections.values().flat_map(|s| &s.1));
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
        for name in read_pages(&row.claim, qdir) {
            let fp = json!(page_blocks(&name, qdir, &mut memo)?.0);
            pages.insert(name, fp);
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
            // the constant reads the new code holds, which a cleared triage records with it (feature 449 T166)
            u.insert("reads".into(), json!(row.unit.reads));
        }
        units.insert(k.clone(), Value::Object(u));
    }
    let tool: Map<String, Value> = cleared
        .iter()
        .filter_map(|k| units.shift_remove(k).map(|u| (k.clone(), u)))
        .collect();
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
    let data = json!({"units": units, "cleared": tool, "snapshots": snaps, SECTION_TEXTS: section_texts(cur, keys), "forced": g.forced.into_iter().collect::<Vec<_>>()});
    std::fs::write(
        out.join("triage.json"),
        dumps(&sorted(&data), Some(1), true) + "\n",
    )
    .map_err(fail)?;
    Ok(out.join("MANIFEST.md"))
}

/// The form of a triage reply's line, as a refusal names it (the agent file's `## Your reply`).
const FORM: &str = "`TOUCHES <key> - <which block, a few words>` (plain text: no bullet, no bold, an ASCII ` - `), or the one line `NONE`";

/// Why a triage reply is refused, or `None` for a reply every line of which reads, FAIL CLOSED (feature 451 T195, gap audit item 3):
/// a line not blank, not `NONE` and not in the form, a key not of this triage, or `NONE` beside a TOUCHES line refuses the whole
/// reply, each line named with the form, before anything is recorded. WHY: a `- TOUCHES` bullet, `**TOUCHES**` or a non-ASCII dash
/// matched nothing, and every claim it meant was cleared as triaged - its re-check skipped, durably, with no one told.
#[must_use]
pub fn refused(reply: &str, units: &Map<String, Value>) -> Option<String> {
    let mut bad: Vec<String> = Vec::new();
    let (mut none, mut named) = (false, false);
    for (i, raw) in reply.split('\n').enumerate() {
        let line = l7r_shared::py_text::strip(raw);
        if line.is_empty() {
            continue;
        }
        if line == "NONE" {
            none = true;
            continue;
        }
        match TOUCHES.captures(bare(raw)).ok().flatten() {
            None => bad.push(format!("line {}: `{line}` is not in the form", i + 1)),
            Some(m) if !units.contains_key(m[1].trim_matches('`')) => bad.push(format!(
                "line {}: `{}` is not a claim of this triage",
                i + 1,
                m[1].trim_matches('`')
            )),
            Some(_) => named = true,
        }
    }
    if none && named {
        bad.push("`NONE` stands beside TOUCHES lines: say one or the other".to_owned());
    }
    (!bad.is_empty()).then(|| {
        format!(
            "claims-triaged: refused, nothing recorded - each line of the reply is {FORM} (451 T195):\n  {}\nput each line in the form and run it again",
            bad.join("\n  ")
        )
    })
}

/// The index with a triage reply applied: a named or forced claim owed `impl-drift`, every other one cleared at the pages as they stand.
pub fn record_triage(
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
    // a key not of this triage is refused before this, by `refused` (451 T195)
    let mut msgs: Vec<String> = Vec::new();
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
            super::reads::stamp(&mut row, fp.get("reads").and_then(Value::as_str));
            row.shift_remove("triage");
            // the build that cleared it, kept only where it held uncommitted code, so the tracked index moves only then (451 T197)
            match l7r_gate_core::build::current()
                .filter(|b| !l7r_gate_core::build::dirty(b).is_empty())
            {
                Some(b) => row.insert("build".into(), b),
                None => row.shift_remove("build"),
            };
        }
        out.insert(key.clone(), Value::Object(row));
    }
    (out, msgs)
}

/// The index with the claims the filter cleared (a triage bundle's `cleared`) cleared at the text as it stands, as a triage clears
/// them, each saying why (feature 451 T191).
pub fn record_cleared(index: &Index, cleared: &Map<String, Value>, today: &str) -> Index {
    let (mut out, _) = record_triage(index, cleared, "", today, &[]);
    for k in cleared.keys() {
        if let Some(r) = out.get_mut(k).and_then(Value::as_object_mut) {
            r.insert("cleared".into(), json!(TOOL_CLEARED));
        }
    }
    out
}

/// (the index with `keys` cleared, the page snapshots to store): each claim owed a triage only because a cited page moved while every block it rests on stands (feature 432).
pub fn clear_page_moves(
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
        for name in read_pages(&row.claim, qdir) {
            let fp = json!(page_blocks(&name, qdir, &mut memo)?.0);
            pages.insert(name, fp);
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

/// The form a DRIFTED note names its fix in (constitution XIV v2.36.0, feature 449 T196): the claim restated where the behavior is
/// fine, the code only for a wrong outcome.
pub const FIX_FORM: &str = "`fix: claim` or `fix: code`, then `effect: <what a reader of the map would see differently, the finding contradicted, the check or tool that answers wrongly, or none>`, before the `[§...]`";

/// Does a DRIFTED note say which side moves, the claim or the code?
fn names_fix(note: &str) -> bool {
    note.contains("fix: claim") || note.contains("fix: code")
}

/// The reply without its VERDICT lines that cannot be recorded as written, and those lines; the outside-the-change rows filed; what was said.
pub fn vet(
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
                .map_while(Result::ok)
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
                Some(m) if &m[2] == "DRIFTED" && !names_fix(&m[3]) => {
                    format!("a DRIFTED note names no fix ({FIX_FORM})")
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
        let _ = writeln!(warned, "claims-checked: correct each refused line in the reply file (the claim's path as the bundle names it; a verdict of IN-STEP, DRIFTED, NEEDS-RESEARCH, MISLABELED or CANNOT-TELL; a pointer to a question file that exists; a DRIFTED note's {FIX_FORM}) and run it again - the lines it recorded stay recorded");
    }
    Ok((keep.join("\n"), bad))
}

/// The reply `make <cmd>` is given, a transcript's last reply (`apply_edits.reply_of`, by command); with no text, the refusal said and "" returned.
pub fn read_reply(
    root: &Path,
    path: &str,
    cmd: &str,
    nothing: &str,
    warned: &mut String,
) -> Result<String, Fail> {
    let reply = crate::record::owed::answers::reply_of(root, path)?;
    if l7r_shared::py_text::strip(&reply).is_empty() {
        let _ = writeln!(
            warned,
            "{cmd}: refused - no reply text in {path}; {nothing}"
        );
    }
    Ok(reply)
}

#[cfg(test)]
mod tests;
