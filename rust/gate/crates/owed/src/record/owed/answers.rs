//! The record of what a check answered (from `record_owed.py`, feature 449 T87): `<git common dir>/record-checks/<slug>.json`, per unit, its fingerprint and every fingerprint ever answered. One writer here; the guards read it.

use std::collections::HashSet;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::checks;
use l7r_guard::shared::escape::enough;
use l7r_guard::shared::html_text::unescape;
use l7r_guard::shared::pyjson;
use serde_json::{json, Map, Value};

use super::{listing, merge_base, units, zfill4, FAMILIES};
use crate::record::args::Parsed;
use crate::record::modals;
use crate::record::repo::{self, fail, git, python, read_universal, tree_of, utc_now, Fail};
use crate::record::units::{
    self as ru, pairs_of, question, re, Unit, HREF, NOTE, ORIG_STORED, ORIG_TOKEN, PASSAGE,
};
use crate::Reply;

mod depiction;
pub use depiction::{amendment1_depiction_answered, legacy_depiction_answered};

/// A round's own EDIT blocks settled it.
pub const SETTLED: &str = "settled - only its round's own EDIT blocks were applied, verbatim, since it was answered (make apply-edits)";
/// Another check's fix outside the quotation and its claim settled it.
pub const FIXED: &str = "settled - another check's fix outside the quotation and its claim";
/// The checks a reply's counts line may name.
const BATCH_CHECKS: [&str; 7] = [
    "modal-depiction",
    "modal-form",
    "modal-research",
    "quote-check",
    "record-format",
    "intro-check",
    "entry-drift",
];

static REPLY_FIRST: LazyLock<Regex> = LazyLock::new(|| re(r"^`?([a-z]+(?:-[a-z]+)+):"));
static REPLY_ANY: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r"(?m)^`?({}): \S", BATCH_CHECKS.join("|"))));
static RUN: LazyLock<Regex> = LazyLock::new(|| re("\u{300c}([^\u{300c}\u{300d}]+)\u{300d}"));
static TAG: LazyLock<Regex> = LazyLock::new(|| re(r"<[^>]+>"));
static OUTSIDE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^#*\s*\**OUTSIDE THE CHANGE\**\s*:?\s*$"));
static ROW: LazyLock<Regex> =
    LazyLock::new(|| re(r"^\s*-\s*`?([^|`]+?)`?\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$"));
static PAGE_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^page: (\S+) ([0-9a-f]{40})$"));
static UNIT_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^unit: (.+) (\S+)$"));

const REPLY_OF: &str = r"import json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1] + '/scripts/record')
sys.dont_write_bytecode = True
import apply_edits
print(json.dumps(apply_edits.reply_of(Path(sys.argv[2]))))";

/// The checks an agent's dispatch answers: `CHECK=modal-research` answers its three units.
fn agent_checks(check: &str) -> Vec<String> {
    if check == "modal-research" {
        modals::RESEARCH_CHECKS
            .iter()
            .map(|c| (*c).to_owned())
            .collect()
    } else {
        vec![check.to_owned()]
    }
}

/// `urllib.parse.quote(slug, safe="")`.
fn quoted(slug: &str) -> String {
    let mut out = String::new();
    for b in slug.bytes() {
        if b.is_ascii_alphanumeric() || b"_.-~".contains(&b) {
            out.push(char::from(b));
        } else {
            let _ = write!(out, "%{b:02X}");
        }
    }
    out
}

/// The clone's answer records: `RECORD_CHECKS_DIR` (a test's throwaway store), else its git dir.
#[must_use]
pub fn store(root: &Path) -> PathBuf {
    store_given(root, std::env::var_os("RECORD_CHECKS_DIR"))
}

/// [`store`] with `RECORD_CHECKS_DIR` given.
pub(super) fn store_given(root: &Path, named: Option<std::ffi::OsString>) -> PathBuf {
    if let Some(dir) = named.filter(|d| !d.is_empty()) {
        return dir.into();
    }
    let common = git(root, &["rev-parse", "--git-common-dir"]);
    let common = common.trim();
    root.join(if common.is_empty() { ".git" } else { common })
        .join("record-checks")
}

fn file_of(store_dir: &Path, slug: &str) -> PathBuf {
    store_dir.join(quoted(slug) + ".json")
}

/// A unit's record, or `{}` for none or an unreadable one.
#[must_use]
pub fn read_answer(store_dir: &Path, slug: &str) -> Map<String, Value> {
    std::fs::read_to_string(file_of(store_dir, slug))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .and_then(|v| v.as_object().cloned())
        .unwrap_or_default()
}

fn write_record(
    store_dir: &Path,
    slug: &str,
    rec: &Map<String, Value>,
    indent: Option<usize>,
    ascii: bool,
) -> Result<(), Fail> {
    let body = pyjson::dumps(&Value::Object(rec.clone()), indent, ascii) + "\n";
    std::fs::write(file_of(store_dir, slug), body).map_err(fail)
}

fn strings(v: Option<&Value>) -> Vec<String> {
    v.and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|s| s.as_str().map(str::to_owned))
        .collect()
}

fn holds(rec: &Map<String, Value>, field: &str, text: &str) -> bool {
    rec.get(field)
        .and_then(Value::as_array)
        .is_some_and(|a| a.iter().any(|v| v.as_str() == Some(text)))
}

/// Record an answer: every fingerprint ever answered is kept.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn write_answer(
    store_dir: &Path,
    slug: &str,
    fp: &str,
    result: &str,
    pages: Option<&Value>,
) -> Result<(), Fail> {
    std::fs::create_dir_all(store_dir).map_err(fail)?;
    let old = read_answer(store_dir, slug);
    let mut seen: Vec<Value> = old
        .get("answered")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter(|f| f.as_str() != Some(fp))
        .cloned()
        .collect();
    seen.push(json!(fp));
    let mut settles = old
        .get("settles")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();
    if let Some(after) = settles.remove(fp) {
        seen.push(after);
    }
    let mut rec = Map::new();
    rec.insert("unit".to_owned(), json!(slug));
    rec.insert("fingerprint".to_owned(), json!(fp));
    rec.insert("answered".to_owned(), Value::Array(seen));
    rec.insert("result".to_owned(), json!(result));
    rec.insert("utc".to_owned(), json!(utc_now()));
    if let Some(p) = pages.filter(|p| p.as_object().is_some_and(|m| !m.is_empty())) {
        rec.insert("pages".to_owned(), p.clone());
    }
    if !settles.is_empty() {
        rec.insert("settles".to_owned(), Value::Object(settles));
    }
    for k in ["readings", "passages", "hrefs", "reply_quotes"] {
        if let Some(v) = old
            .get(k)
            .filter(|v| v.as_array().is_some_and(|a| !a.is_empty()))
        {
            rec.insert(k.to_owned(), v.clone());
        }
    }
    write_record(store_dir, slug, &rec, Some(1), true)
}

/// A unit whose content moved from `before` to `after` by nothing but its round's own EDIT blocks is not owed that check again ("answered" or "pending"; "" for neither).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn settle(store_dir: &Path, slug: &str, before: &str, after: &str) -> Result<String, Fail> {
    if before.is_empty() || after.is_empty() || before == after {
        return Ok(String::new());
    }
    let mut rec = read_answer(store_dir, slug);
    if answered(store_dir, slug, before, "") {
        if !holds(&rec, "answered", after) {
            let result = format!(
                "{SETTLED}; was: {}",
                rec.get("result").and_then(Value::as_str).unwrap_or("")
            );
            write_answer(store_dir, slug, after, &result, rec.get("pages"))?;
        }
        return Ok("answered".to_owned());
    }
    std::fs::create_dir_all(store_dir).map_err(fail)?;
    if !rec.contains_key("unit") {
        rec.insert("unit".to_owned(), json!(slug));
    }
    let mut settles = rec
        .get("settles")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();
    settles.insert(before.to_owned(), json!(after));
    rec.insert("settles".to_owned(), Value::Object(settles));
    write_record(store_dir, slug, &rec, Some(1), true)?;
    Ok("pending".to_owned())
}

/// The checks whose units a reply answers.
pub fn reply_checks(reply: &str) -> Vec<String> {
    let first = reply
        .lines()
        .map(l7r_guard::shared::py_text::strip)
        .find(|l| !l.is_empty())
        .unwrap_or("");
    let found = REPLY_FIRST
        .captures(first)
        .ok()
        .flatten()
        .or_else(|| REPLY_ANY.captures(reply).ok().flatten());
    found.map_or_else(Vec::new, |m| {
        if &m[1] == "modal-research" {
            agent_checks("modal-research")
        } else {
            vec![m[1].to_owned()]
        }
    })
}

/// `fp` answered, or, for a source-reader note, its `reading` answered under another fingerprint.
pub fn answered(store_dir: &Path, slug: &str, fp: &str, reading: &str) -> bool {
    let rec = read_answer(store_dir, slug);
    rec.get("fingerprint").and_then(Value::as_str) == Some(fp)
        || holds(&rec, "answered", fp)
        || (!reading.is_empty() && holds(&rec, "readings", reading))
}

/// The other session clones' answer stores.
fn sibling_stores(root: &Path) -> Vec<PathBuf> {
    siblings_given(root, std::env::var_os("RECORD_CHECKS_DIR"))
}

/// [`sibling_stores`] with `RECORD_CHECKS_DIR` given: a test's throwaway store has no siblings.
pub(super) fn siblings_given(root: &Path, named: Option<std::ffi::OsString>) -> Vec<PathBuf> {
    let clones = root
        .parent()
        .filter(|p| p.file_name().is_some_and(|n| n == ".clones"));
    let Some(parent) = clones.filter(|_| named.is_none_or(|d| d.is_empty())) else {
        return Vec::new();
    };
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(parent)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|d| d != root)
        .collect();
    dirs.sort();
    dirs.into_iter()
        .map(|d| d.join(".git/record-checks"))
        .filter(|d| d.is_dir())
        .collect()
}

/// An answer at these exact words in another clone's store, copied into this one.
fn adopt(s: &Path, others: &[PathBuf], slug: &str, fp: &str, reading: &str) -> Result<bool, Fail> {
    for o in others {
        if !answered(o, slug, fp, reading) {
            continue;
        }
        let rec = read_answer(o, slug);
        std::fs::create_dir_all(s).map_err(fail)?;
        let mut mine = read_answer(s, slug);
        let mut have = strings(mine.get("answered"));
        let mut extra: Vec<String> = rec
            .get("fingerprint")
            .and_then(Value::as_str)
            .filter(|f| !f.is_empty())
            .map(str::to_owned)
            .into_iter()
            .collect();
        extra.extend(
            strings(rec.get("answered"))
                .into_iter()
                .filter(|f| !f.is_empty()),
        );
        for f in extra {
            if !have.contains(&f) {
                have.push(f);
            }
        }
        mine.insert("answered".to_owned(), json!(have));
        let mut readings: Vec<String> = strings(mine.get("readings"));
        readings.extend(strings(rec.get("readings")));
        readings.sort();
        readings.dedup();
        mine.insert("readings".to_owned(), json!(readings));
        if !mine.contains_key("fingerprint") {
            mine.insert(
                "fingerprint".to_owned(),
                rec.get("fingerprint").cloned().unwrap_or(Value::Null),
            );
        }
        write_record(s, slug, &mine, None, false)?;
        return Ok(true);
    }
    Ok(false)
}

/// The 「...」 runs of a text, whitespace dropped; the text itself where it has none.
fn runs_of(text: &str) -> Vec<String> {
    let squeeze = |t: &str| {
        t.chars()
            .filter(|c| !l7r_guard::shared::py_text::is_space(*c))
            .collect::<String>()
    };
    let found: Vec<String> = RUN
        .captures_iter(text)
        .flatten()
        .map(|c| squeeze(&c[1]))
        .collect();
    if found.is_empty() {
        vec![squeeze(text)]
    } else {
        found
    }
}

/// (the pages, the passages' runs) a source-reader reads of one note in the tree now; both empty for a note not found.
fn note_parts(root: &Path, subject: &str) -> Result<(Vec<String>, Vec<String>), Fail> {
    let (stem, note) = subject.split_once('#').unwrap_or((subject, ""));
    if stem.contains('.') {
        return Ok((Vec::new(), Vec::new()));
    }
    let dir = root.join("research/questions");
    let prefix = format!("{stem}-");
    let mut names: Vec<String> = std::fs::read_dir(&dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| n.starts_with(&prefix) && n.as_bytes().ends_with(b".notes.html"))
        .collect();
    names.sort();
    for name in names {
        let originals = dir.join(format!(
            "{}.originals.html",
            name.trim_end_matches(".notes.html")
        ));
        let table: std::collections::HashMap<String, String> = read_universal(&originals)?
            .map_or_else(Vec::new, |t| pairs_of(&ORIG_STORED, &t))
            .into_iter()
            .collect();
        let text = repo::read_text(&dir.join(&name))?;
        if let Some(body) = pairs_of(&NOTE, &text)
            .into_iter()
            .find(|(k, _)| k == note)
            .map(|p| p.1)
        {
            let origs: Vec<String> = ORIG_TOKEN
                .captures_iter(&body)
                .flatten()
                .map(|c| table.get(&c[1]).cloned().unwrap_or_default())
                .collect();
            let passages = if origs.is_empty() {
                let token_free = ORIG_TOKEN.replace_all(&body, "");
                let bare = TAG.replace_all(&token_free, "");
                pairs_of(&PASSAGE, &unescape(&bare))
                    .into_iter()
                    .map(|(a, b)| if a.is_empty() { b } else { a })
                    .collect()
            } else {
                origs
            };
            let hrefs = pairs_of(&HREF, &body).into_iter().map(|p| p.0).collect();
            return Ok((hrefs, passages.iter().flat_map(|p| runs_of(p)).collect()));
        }
    }
    Ok((Vec::new(), Vec::new()))
}

fn sorted_union(old: Vec<String>, new: Vec<String>) -> Value {
    let mut all = old;
    all.extend(new);
    all.sort();
    all.dedup();
    json!(all)
}

/// Add what a source-reader answer read - its pages and passages - and the passages its reply quoted.
pub(super) fn keep_parts(
    store_dir: &Path,
    slug: &str,
    root: &Path,
    reply: &str,
) -> Result<(), Fail> {
    let mut rec = read_answer(store_dir, slug);
    if rec.is_empty() {
        return Ok(());
    }
    let (hrefs, runs) = note_parts(root, slug.split_once(':').map_or("", |p| p.1))?;
    let old_hrefs = strings(rec.get("hrefs"));
    rec.insert("hrefs".to_owned(), sorted_union(old_hrefs, hrefs));
    let old_passages = strings(rec.get("passages"));
    rec.insert("passages".to_owned(), sorted_union(old_passages, runs));
    if !reply.is_empty() {
        let quotes = runs_of(reply)
            .into_iter()
            .filter(|r| r.chars().count() > 1)
            .collect();
        let old_quotes = strings(rec.get("reply_quotes"));
        rec.insert("reply_quotes".to_owned(), sorted_union(old_quotes, quotes));
    }
    write_record(store_dir, slug, &rec, Some(1), true)
}

/// A source-reader note changed by nothing but passages its last reader quoted itself, on the pages it read: not owed again.
fn readers_own(root: &Path, store_dir: &Path, slug: &str) -> Result<bool, Fail> {
    let rec = read_answer(store_dir, slug);
    let known: HashSet<String> = strings(rec.get("passages")).into_iter().collect();
    if known.is_empty() {
        return Ok(false);
    }
    let (hrefs, runs) = note_parts(root, slug.split_once(':').map_or("", |p| p.1))?;
    let quoted = strings(rec.get("reply_quotes"));
    let read: HashSet<String> = strings(rec.get("hrefs")).into_iter().collect();
    Ok(!runs.is_empty()
        && hrefs.iter().all(|h| read.contains(h))
        && runs.iter().any(|r| known.contains(r))
        && runs
            .iter()
            .all(|r| known.contains(r) || quoted.iter().any(|q| q.contains(r.as_str()))))
}

/// Add a source-reader or quote-check answer's `reading` to its record (with `qkeys`, a quote-check answer's quotation key).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn keep_reading(store_dir: &Path, slug: &str, reading: &str, field: &str) -> Result<(), Fail> {
    let mut rec = read_answer(store_dir, slug);
    if reading.is_empty() || rec.is_empty() || holds(&rec, field, reading) {
        return Ok(());
    }
    let mut list = rec
        .get(field)
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    list.push(json!(reading));
    rec.insert(field.to_owned(), Value::Array(list));
    write_record(store_dir, slug, &rec, Some(1), true)
}

/// Every owed unit with no current answer.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn unanswered(root: &Path) -> Result<Vec<Unit>, Fail> {
    unanswered_of(root, units(root, None, None, &FAMILIES, "")?)
}

/// Those of `rows` (every owed unit of the tree now) with no current answer.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn unanswered_of(root: &Path, rows: Vec<Unit>) -> Result<Vec<Unit>, Fail> {
    let s = store(root);
    let others = sibling_stores(root);
    let modals_now = modals::modals_now(root, true)?;
    let mut owed: Vec<Unit> = Vec::new();
    for u in rows {
        if answered(&s, &u.slug, &u.fingerprint, &u.reading)
            || adopt(&s, &others, &u.slug, &u.fingerprint, &u.reading)?
            || legacy_depiction_answered(root, &s, &u.slug, &modals_now)?
            || amendment1_depiction_answered(root, &s, &u.slug, &modals_now)?
        {
            continue;
        }
        owed.push(u);
    }
    let quote_owed: HashSet<String> = owed
        .iter()
        .filter(|u| u.check() == "quote-check")
        .map(|u| u.subject().to_owned())
        .collect();
    let mut out = Vec::new();
    for u in owed {
        if u.check() == "source-reader"
            && !quote_owed.contains(u.subject())
            && readers_own(root, &s, &u.slug)?
        {
            continue;
        }
        out.push(u);
    }
    Ok(out)
}

/// `secrets.token_hex(3)`.
fn token_hex() -> String {
    let mut bytes = [0u8; 3];
    let _ = std::fs::File::open("/dev/urandom")
        .and_then(|mut f| std::io::Read::read_exact(&mut f, &mut bytes));
    bytes.iter().fold(String::new(), |mut out, b| {
        let _ = write!(out, "{b:02x}");
        out
    })
}

/// A stated reason, written where `make audit` reads every escape.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn bypass_log(root: &Path, target: &str, why: &str) -> Result<(), Fail> {
    let now = utc_now();
    let bl = root.join("dev/bypass-log").join(&now[..7]);
    std::fs::create_dir_all(&bl).map_err(fail)?;
    let head = git(root, &["rev-parse", "--short", "HEAD"]);
    let rec = json!({"utc": now, "target": target, "commit": head.trim(), "why": why});
    let stamp = format!("{}Z", now.replace(['-', ':'], "").trim_end_matches('Z'));
    let name = format!("{stamp}-{}.json", token_hex());
    std::fs::write(bl.join(name), pyjson::dumps(&rec, Some(2), true) + "\n").map_err(fail)
}

/// {slug: `quotation_key`} of quote-check note units at `rev` (None: the working tree); no write-up is read.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn quotation_keys(
    root: &Path,
    rev: Option<&str>,
    slugs: &[String],
) -> Result<std::collections::HashMap<String, String>, Fail> {
    let record = super::read_at(root, rev, Some(&HashSet::new()))?;
    Ok(slugs
        .iter()
        .filter(|s| s.starts_with("quote-check:") && !s.ends_with("#unfootnoted"))
        .map(|s| (s.clone(), ru::quotation_key(&record, s)))
        .collect())
}

/// A hand fix of another check's finding, declared on quote-check notes: answered at today's words where the quotation and its claim stand, all or none.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn fixed_answer(
    root: &Path,
    q: &str,
    notes: &str,
    fixed_by: &str,
) -> Result<(Vec<String>, Vec<String>), Fail> {
    let wanted: HashSet<&str> = notes.split(',').filter(|k| !k.is_empty()).collect();
    let s = store(root);
    let owed: Vec<Unit> = unanswered(root)?
        .into_iter()
        .filter(|u| {
            u.check() == "quote-check"
                && question(u.subject()) == zfill4(q)
                && wanted.contains(u.subject().split_once('#').map_or("", |p| p.1))
        })
        .collect();
    let slugs: Vec<String> = owed.iter().map(|u| u.slug.clone()).collect();
    let now = quotation_keys(root, None, &slugs)?;
    let base_rev = merge_base(root);
    let base = if base_rev.is_empty() {
        std::collections::HashMap::default()
    } else {
        quotation_keys(root, Some(&base_rev), &slugs)?
    };
    let refused: Vec<String> = owed
        .iter()
        .filter(|u| {
            now.get(&u.slug).is_none_or(|key| {
                !holds(&read_answer(&s, &u.slug), "qkeys", key) && Some(key) != base.get(&u.slug)
            })
        })
        .map(|u| u.slug.clone())
        .collect();
    if !refused.is_empty() {
        return Ok((Vec::new(), refused));
    }
    for u in &owed {
        let pages = read_answer(&s, &u.slug).get("pages").cloned();
        write_answer(
            &s,
            &u.slug,
            &u.fingerprint,
            &format!("{FIXED}: {fixed_by}"),
            pages.as_ref(),
        )?;
        keep_reading(
            &s,
            &u.slug,
            now.get(&u.slug).map_or("", String::as_str),
            "qkeys",
        )?;
    }
    Ok((owed.into_iter().map(|u| u.slug).collect(), Vec::new()))
}

/// Why a record without a bundle is refused, or "".
#[must_use]
pub fn bundle_less_refusal(check: &str, notes: &str, reason: &str) -> String {
    if check == "source-reader" && !notes.is_empty() {
        return String::new();
    }
    if !reason.is_empty() && enough(reason) {
        return String::new();
    }
    if !reason.is_empty() {
        return "REASON needs two words and eight characters - it ships to dev/bypass-log/ for the audit".to_owned();
    }
    format!(
        "a {check} answer without BUNDLE= records today's content, which the check may never have read: pass the BUNDLE= it read, or REASON=\"<why>\" (written to dev/bypass-log/). A fix that applies a check's findings is owed its second round."
    )
}

/// What the named subject of an answer is: its q, note keys, key and kind names.
pub struct Named<'a> {
    pub q: &'a str,
    pub notes: &'a str,
    pub key: &'a str,
    pub kind: &'a str,
}

/// The bundle's answer, from its `MANIFEST.md`.
fn answer_from_bundle(
    s: &Path,
    checks: &[String],
    result: &str,
    bundle: &str,
) -> Result<Vec<String>, Fail> {
    let manifest = Path::new(bundle).join("MANIFEST.md");
    let text = read_universal(&manifest)?.unwrap_or_default();
    let mut pages = Map::new();
    for c in PAGE_LINE.captures_iter(&text).flatten() {
        pages.insert(c[1].to_owned(), json!(c[2].to_owned()));
    }
    let pages = Value::Object(pages);
    let mut done = Vec::new();
    for c in UNIT_LINE.captures_iter(&text).flatten() {
        if checks.iter().any(|ch| c[1].split(':').next() == Some(ch)) {
            write_answer(s, &c[1], &c[2], result, Some(&pages))?;
            done.push(c[1].to_owned());
        }
    }
    Ok(done)
}

fn answer_inner(
    root: &Path,
    check: &str,
    result: &str,
    bundle: &str,
    named: &Named,
) -> Result<Vec<String>, Fail> {
    let s = store(root);
    let checks = agent_checks(check);
    if !bundle.is_empty() {
        return answer_from_bundle(&s, &checks, result, bundle);
    }
    let wanted: HashSet<&str> = named.notes.split(',').filter(|k| !k.is_empty()).collect();
    let mut done = Vec::new();
    for u in units(root, None, None, &FAMILIES, "")? {
        if !checks.iter().any(|c| c == u.check()) {
            continue;
        }
        let note = u.subject().split_once('#').map_or("", |p| p.1);
        let by_q = !named.q.is_empty()
            && question(u.subject()) == zfill4(named.q)
            && (wanted.is_empty() || wanted.contains(note));
        let by_key = !named.key.is_empty() && u.subject() == named.key;
        let by_kind = !named.kind.is_empty() && named.kind.split(',').any(|k| k == u.subject());
        if by_q || by_key || by_kind {
            write_answer(&s, &u.slug, &u.fingerprint, result, None)?;
            done.push(u.slug.clone());
        }
    }
    Ok(done)
}

/// Record the answer for every unit of `check` the bundle carried, or that the tree owes on the named subject, and close that check's dispatches on those subjects.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn answer(
    root: &Path,
    check: &str,
    result: &str,
    bundle: &str,
    named: &Named,
    reply: &str,
) -> Result<Vec<String>, Fail> {
    let done = answer_inner(root, check, result, bundle, named)?;
    if !done.is_empty() && (check == "source-reader" || check == "quote-check") {
        let (s, now): (PathBuf, Vec<Unit>) = (store(root), units(root, None, None, &FAMILIES, "")?);
        let readings: std::collections::HashMap<&str, &str> = now
            .iter()
            .filter(|u| u.check() == check)
            .map(|u| (u.slug.as_str(), u.reading.as_str()))
            .collect();
        let qk = if check == "quote-check" {
            quotation_keys(root, None, &done)?
        } else {
            std::collections::HashMap::default()
        };
        for slug in &done {
            keep_reading(
                &s,
                slug,
                readings.get(slug.as_str()).copied().unwrap_or(""),
                "readings",
            )?;
            keep_reading(&s, slug, qk.get(slug).map_or("", String::as_str), "qkeys")?;
            if check == "source-reader" {
                keep_parts(&s, slug, root, reply)?;
            }
        }
    }
    if !done.is_empty() {
        checks::rounds::record_answer(root, check, &done);
    }
    Ok(done)
}

/// (file, block, finding) of every line under a reply's `OUTSIDE THE CHANGE` heading.
fn outside(reply: &str) -> Vec<(String, String, String)> {
    let Ok(Some(m)) = OUTSIDE.find(reply) else {
        return Vec::new();
    };
    let mut rows = Vec::new();
    for line in crate::record::py_lines(&reply[m.end()..]) {
        if line.starts_with('#') {
            break;
        }
        if let Ok(Some(r)) = ROW.captures(line) {
            rows.push((
                l7r_guard::shared::py_text::strip(&r[1]).to_owned(),
                r[2].to_owned(),
                r[3].to_owned(),
            ));
        }
    }
    rows
}

/// Append a reply's OUTSIDE THE CHANGE findings to the active feature's `found.jsonl` as open rows.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn file_outside(
    root: &Path,
    check: &str,
    reply: &str,
) -> Result<Vec<Map<String, Value>>, Fail> {
    let rows = outside(reply);
    if rows.is_empty() {
        return Ok(Vec::new());
    }
    let utc = utc_now();
    let target = checks::arbiter::feature_dir(root, "")
        .unwrap_or_else(|| root.join("specs/_unfiled"))
        .join("found.jsonl");
    std::fs::create_dir_all(target.parent().unwrap_or(root)).map_err(fail)?;
    let mut body = String::new();
    let mut out = Vec::new();
    for (file, block, finding) in rows {
        let row = json!({"check": check, "file": file, "block": block, "finding": finding, "status": "open", "utc": utc});
        body.push_str(&pyjson::dumps(&row, None, false));
        body.push('\n');
        out.push(row.as_object().cloned().unwrap_or_default());
    }
    std::io::Write::write_all(
        &mut std::fs::OpenOptions::new()
            .append(true)
            .create(true)
            .open(&target)
            .map_err(fail)?,
        body.as_bytes(),
    )
    .map_err(fail)?;
    Ok(out)
}

fn fail_line(code: i32, stderr: &str) -> Reply {
    Reply {
        stdout: String::new(),
        stderr: format!("{stderr}\n"),
        code,
    }
}

fn run_fixed(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let (q, notes) = (parsed.text("--q", ""), parsed.text("--notes", ""));
    if parsed.text("--answer", "") != "quote-check" || q.is_empty() || notes.is_empty() {
        return Ok(fail_line(2, "record-checked: FIXED_BY= declares a fix of another check's finding on quote-check notes: CHECK=quote-check Q=<NNNN> NOTES=<k,k> FIXED_BY=\"<check>: <its finding>\""));
    }
    let (done, refused) = fixed_answer(root, q, notes, parsed.text("--fixed-by", ""))?;
    if !refused.is_empty() {
        return Ok(fail_line(
            2,
            &format!(
                "record-checked: REFUSED - the quotation or its claim changed, so quote-check is owed (feature 399): {} - check it: make check-bundle Q={} FOR=quote-check NOTES={notes}",
                refused.join(" "),
                zfill4(q)
            ),
        ));
    }
    if done.is_empty() {
        return Ok(fail_line(
            3,
            &format!("_record_owed: no owed quote-check unit on {notes} - nothing recorded"),
        ));
    }
    Ok(Reply {
        stdout: format!(
            "record-checked: {} unit(s) answered as another check's fix - {}\n",
            done.len(),
            done.join(" ")
        ),
        stderr: String::new(),
        code: 0,
    })
}

/// A transcript's last reply, as `make apply-edits` reads one (`apply_edits.reply_of`, phase 4, by command).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn reply_of(root: &Path, path: &str) -> Result<String, Fail> {
    let tree = tree_of(root);
    let said = python(REPLY_OF, &[&tree.to_string_lossy(), path], "")?;
    serde_json::from_str(&said).map_err(fail)
}

fn run_answer(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    let (check, result, bundle) = (
        parsed.text("--answer", ""),
        parsed.text("--result", ""),
        parsed.text("--bundle", ""),
    );
    if result.is_empty() {
        return Ok(fail_line(
            2,
            "_record_owed: --answer needs --result \"<the check's counts>\"",
        ));
    }
    let (notes, reason) = (parsed.text("--notes", ""), parsed.text("--reason", ""));
    let refusal = if bundle.is_empty() {
        bundle_less_refusal(check, notes, reason)
    } else {
        String::new()
    };
    if !refusal.is_empty() {
        return Ok(fail_line(
            2,
            &format!("record-checked: REFUSED - {refusal}"),
        ));
    }
    let reply_arg = parsed.text("--reply", "");
    let reply = if reply_arg.is_empty() {
        String::new()
    } else {
        reply_of(root, reply_arg)?
    };
    let named = Named {
        q: parsed.text("--q", ""),
        notes,
        key: parsed.text("--key", ""),
        kind: parsed.text("--kind", ""),
    };
    let done = answer(root, check, result, bundle, &named, &reply)?;
    let mut out = String::new();
    if !reply.is_empty() {
        for row in file_outside(root, check, &reply)? {
            let text = |k: &str| row.get(k).and_then(Value::as_str).unwrap_or("").to_owned();
            let _ = writeln!(
                out,
                "record-checked: filed, not fixed - {} | {} | {}",
                text("file"),
                text("block"),
                text("finding")
            );
        }
    }
    if !done.is_empty() && bundle.is_empty() && !reason.is_empty() {
        bypass_log(
            root,
            "record-checked",
            &format!("{check} on {}: {reason}", done.join(" ")),
        )?;
    }
    if done.is_empty() {
        return Ok(Reply { stdout: out, stderr: format!("_record_owed: no owed {check} unit matched - nothing recorded (`make record-owed` lists what is owed)\n"), code: 3 });
    }
    let _ = writeln!(
        out,
        "record-checked: {} unit(s) answered - {}",
        done.len(),
        done.join(" ")
    );
    Ok(Reply {
        stdout: out,
        stderr: String::new(),
        code: 0,
    })
}

/// The command line's modes, past `--root`.
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn run(root: &Path, parsed: &Parsed) -> Result<Reply, Fail> {
    if !parsed.text("--answer", "").is_empty() && !parsed.text("--fixed-by", "").is_empty() {
        return run_fixed(root, parsed);
    }
    if !parsed.text("--answer", "").is_empty() {
        return run_answer(root, parsed);
    }
    listing(root, parsed)
}
