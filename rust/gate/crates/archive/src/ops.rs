//! The source archive's housekeeping and lookups (`scripts/record/archive_ops.py`, feature 309 Amendment 1; ported by feature 449 T147,
//! phase 4's S3b under `ask:449-phase4-slices`) - beside the capture, which [`crate::manifest`] does.
//!
//! THE INBOX (FR-013; the GM, 2026-10-02: use the download directory *"as a queue of sorts ... once something has been added to the
//! diagram research repository and then pushed, then we can delete it from the academic sources directory"*). Every file or saved-page
//! folder in the GM's downloads but the GM's two lists is copied to `gm-copies/<name>` of the archive once its keys are known (a new
//! download waits until the session matches it: MATCH= or NONE=), the push is CONFIRMED (the path is in `origin/main`'s tree), and only
//! then is it deleted from the inbox. `research/archive/gm-copies.json` keeps each processed file's name, keys and archive path, so a
//! copy is still found after its file is gone; a file that copies no cited source is archived all the same (*"store sources which we
//! ourselves do not end up citing"*), its keys `[]`.
//!
//! THE KEPT UNCITED PAGES (feature 312 FR-011): [`consulted`] archives the pages feature 312's filter kept, and no other, in lanes as the
//! cited backfill does. THE LOOKUP (FR-015, FR-016; the GM: *"first check to see if we already have something, rather than going out
//! and trying to find it on the internet"*): [`find::find`] answers by URL, key or words in the archived text, naming each copy's local
//! path. THE CITED PAGES READ (FR-014): [`archive_urls`], which `make source-outcome OUTCOME=cited:<key>` asks in process. THE
//! RELAYOUT, one time: [`relayout::relayout`].

use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::{Arc, Mutex};

use l7r_shared::attempts;
use l7r_shared::cited_url::clean;
use l7r_shared::consulted::{self, norm};
use l7r_shared::pyjson::{dumps, py_str};
use serde_json::{json, Map, Value};

use crate::backfill::{lane, lanes, Lane};
use crate::fetch::Client;
use crate::manifest::{
    archive_url, gm_table, load_row, manifest_dir, place_gm, research, row_files, settle, LOCK_WAIT,
};
use crate::store::Archive;
use crate::{Error, Result};

pub mod find;
pub mod relayout;

/// The GM's own notes in the inbox, never processed: they are lists of what to fetch, not sources.
pub const GM_LISTS: [&str; 2] = ["TO-DOWNLOAD.md", "for-the-gm-fetch-list.md"];
/// GitHub refuses a pushed file over 100 MB, and the archive is a GitHub repository.
pub const GITHUB_FILE_LIMIT: u64 = 100 * 1024 * 1024;
/// Feature 312's work list of the pages its filter kept (plan D8), read here by [`kept_urls`]; its one writer is the `uncited` crate.
pub const KEPT: &str = "specs/312-uncited-source-catalog/kept.jsonl";

pub(crate) fn os_error(e: &std::io::Error, what: &Path) -> Error {
    Error::new("OSError", format!("{e}: '{}'", what.display()))
}

/// A directory made with its parents.
pub(crate) fn mkdir(p: &Path) -> Result<()> {
    std::fs::create_dir_all(p).map_err(|e| os_error(&e, p))
}

/// An empty directory removed.
pub(crate) fn rmdir(p: &Path) -> Result<()> {
    std::fs::remove_dir(p).map_err(|e| os_error(&e, p))
}

/// A file removed.
pub(crate) fn unlink(p: &Path) -> Result<()> {
    std::fs::remove_file(p).map_err(|e| os_error(&e, p))
}

/// A tree removed (`shutil.rmtree`).
pub(crate) fn rmtree(p: &Path) -> Result<()> {
    std::fs::remove_dir_all(p).map_err(|e| os_error(&e, p))
}

/// A file written whole.
pub(crate) fn write_file(p: &Path, text: &str) -> Result<()> {
    std::fs::write(p, text).map_err(|e| os_error(&e, p))
}

/// A value's `x[k]`: a missing field is the Python's `KeyError`, a value that is no mapping its `TypeError`.
///
/// # Errors
/// As the Python's subscript raised.
pub fn field(x: &Value, k: &str) -> Result<String> {
    match x {
        Value::Object(m) => m
            .get(k)
            .map(py_str)
            .ok_or_else(|| Error::new("KeyError", format!("'{k}'"))),
        Value::Array(_) => Err(Error::new(
            "TypeError",
            "list indices must be integers or slices, not str",
        )),
        Value::String(_) => Err(Error::new(
            "TypeError",
            "string indices must be integers, not 'str'",
        )),
        other => Err(Error::new(
            "TypeError",
            format!(
                "'{}' object is not subscriptable",
                l7r_shared::blocked::type_name(other)
            ),
        )),
    }
}

/// `x.get(k, "")` as text: a value that is no mapping is the Python's `AttributeError`.
///
/// # Errors
/// As the Python's `.get` raised.
pub fn get_text(x: &Value, k: &str) -> Result<String> {
    match x {
        Value::Object(m) => Ok(m.get(k).map(py_str).unwrap_or_default()),
        other => Err(Error::new(
            "AttributeError",
            format!(
                "'{}' object has no attribute 'get'",
                l7r_shared::blocked::type_name(other)
            ),
        )),
    }
}

/// `json.loads(p.read_text())["url"]` of a row file.
///
/// # Errors
/// A row that will not read, or has no `url`.
pub fn row_url(path: &Path) -> Result<String> {
    field(&load_row(path)?, "url")
}

/// The table of the GM's files written whole: the file's other fields kept, `files` sorted by name, indented by one.
///
/// # Errors
/// A table that is not JSON or not a mapping, or the write.
pub fn write_table(root: &Path, table: &Map<String, Value>) -> Result<()> {
    let path = manifest_dir(root).join(l7r_gate_research::record::archive::GM_COPIES);
    let mut doc = if path.is_file() {
        load_row(&path)?
    } else {
        json!({"_about": "Feature 309: the GM's downloaded files."})
    };
    let mut names: Vec<&String> = table.keys().collect();
    names.sort();
    let files: Map<String, Value> = names
        .into_iter()
        .map(|k| (k.clone(), table[k].clone()))
        .collect();
    let Value::Object(m) = &mut doc else {
        return Err(Error::new(
            "TypeError",
            "list indices must be integers or slices, not str",
        ));
    };
    m.insert("files".into(), Value::Object(files));
    let up = path.parent().unwrap_or(&path);
    mkdir(up)?;
    write_file(&path, &(dumps(&doc, Some(1), false) + "\n"))
}

/// Whether `rel` is in the tree of `origin/main` as this copy last pushed or fetched it.
///
/// # Errors
/// git cannot start.
pub fn on_github(store: &Archive, rel: &str) -> Result<bool> {
    let done = store.git(&["ls-tree", "--name-only", "origin/main", "--", rel], false)?;
    Ok(done.status.success() && !String::from_utf8_lossy(&done.stdout).trim().is_empty())
}

/// A directory's entries in its own order (`os.scandir`'s, unsorted), each with whether it is a directory itself, a link not followed.
fn scan(dir: &Path) -> Vec<(PathBuf, bool)> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| (e.path(), e.file_type().is_ok_and(|t| t.is_dir())))
        .collect()
}

/// `path.rglob("*")`'s files in its own order (feature 449 T147, the plan review: FR-002 holds the order the Python named them in).
/// `Path.rglob("*")` is the pattern `**/*`: `CPython` 3.14's `_GlobberBase.recursive_selector` makes `select_recursive`, which first lists
/// the root's own children (the `*` selector, `scandir` order), then works a stack - pop a directory (LIFO), `scandir` it, and for each
/// entry that is a directory (`is_dir(follow_symlinks=False)`: a symlinked one is listed but never entered) list that directory's
/// children at once and push it (observed 2026-11-16, method: `glob.py` lines 472-531 read, and `rglob` against this walk on a tree with
/// files, nested and sibling directories and a symlinked directory, the same order). `too_big` keeps what `is_file` takes, a link to a
/// file among them.
fn files_under(path: &Path, out: &mut Vec<PathBuf>) {
    let files = |dir: &Path, out: &mut Vec<PathBuf>| {
        out.extend(
            scan(dir)
                .into_iter()
                .map(|(p, _)| p)
                .filter(|p| p.is_file()),
        );
    };
    files(path, out);
    let mut stack = vec![path.to_path_buf()];
    while let Some(dir) = stack.pop() {
        for (sub, is_dir) in scan(&dir) {
            if is_dir {
                files(&sub, out);
                stack.push(sub);
            }
        }
    }
}

fn size_of(path: &Path) -> u64 {
    std::fs::metadata(path).map_or(0, |m| m.len())
}

/// The files under `path` (itself, or inside a directory) that GitHub would refuse, each with its size in MB. Checked BEFORE anything is
/// committed (feature 395's step-back, hour:395@1): download #31 (434 MB) was committed to the shared archive and its push refused,
/// which wedged every later archive push until the commit was undone by hand. A folder's files in `rglob`'s own order (`files_under`).
#[must_use]
pub fn too_big(path: &Path) -> Vec<String> {
    let mut files = Vec::new();
    if path.is_file() {
        files.push(path.to_path_buf());
    } else {
        files_under(path, &mut files);
    }
    files
        .iter()
        .filter(|f| size_of(f) > GITHUB_FILE_LIMIT)
        .map(|f| {
            let name = f
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
                .unwrap_or_default();
            format!("{name} ({} MB)", size_of(f) / (1024 * 1024))
        })
        .collect()
}

/// The refusal for an inbox entry over GitHub's limit, with the split that fits: parts of at most 90% of the limit, so `--split-pages`
/// is the PDF's pages divided by that many parts. Its first form named a fixed `--split-pages=200`, which on the 433 MB Morisada scan
/// (333 pages) gives parts of about 270 MB, still refused (the money session, 2026-10-19).
#[must_use]
pub fn refused_line(name: &str, big: &[String], path: &Path) -> String {
    let size = if path.is_file() { size_of(path) } else { 0 };
    #[expect(
        clippy::cast_precision_loss,
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "math.ceil of a file's size over a float, as the Python computed it"
    )]
    let parts = ((size as f64) / (0.9 * GITHUB_FILE_LIMIT as f64))
        .ceil()
        .max(2.0) as u64;
    format!(
        "  REFUSED {name}: over GitHub's 100 MB file limit ({}), so it is not archived - split the PDF into at least {parts} parts \
         (`qpdf --show-npages {name}` gives N; `qpdf --split-pages=<N / {parts}, rounded up> {name} <stem>-part.pdf`), check each part is \
         under 90 MB, archive the parts with MATCH='<part>=<key> ...', then delete the original; it stays in the inbox",
        big.join(", ")
    )
}

/// What the session said of the inbox's new files: each name's keys (in the order first named, a later word for a name replacing an
/// earlier one, as the Python's dict did), and the download-list entry each answers.
#[derive(Debug, Default, Clone, PartialEq, Eq)]
pub struct Matched {
    pub keys: Vec<(String, Vec<String>)>,
    pub downloads: Vec<(String, String)>,
}

fn upsert<T>(list: &mut Vec<(String, T)>, name: &str, value: T) {
    match list.iter_mut().find(|(n, _)| n == name) {
        Some((_, v)) => *v = value,
        None => list.push((name.to_owned(), value)),
    }
}

impl Matched {
    /// A name's keys, set.
    pub fn set(&mut self, name: &str, keys: Vec<String>) {
        upsert(&mut self.keys, name, keys);
    }
}

/// Python's `\d` and `int()`'s digits: a decimal digit of any script (`Nd`) and its value. The Unicode `Nd` digits run in tens from a
/// zero, so a digit is a character in the ten from one of these zeros (every `Nd` zero of Python 3.14's Unicode 16, all below U+20000,
/// observed 2026-11-16, method: `[c for c in map(chr, range(0x20000)) if unicodedata.decimal(c, -1) == 0]`).
#[must_use]
pub fn decimal(c: char) -> Option<u32> {
    const ZEROS: &[u32] = &[
        0x30, 0x660, 0x6F0, 0x7C0, 0x966, 0x9E6, 0xA66, 0xAE6, 0xB66, 0xBE6, 0xC66, 0xCE6, 0xD66,
        0xDE6, 0xE50, 0xED0, 0xF20, 0x1040, 0x1090, 0x17E0, 0x1810, 0x1946, 0x19D0, 0x1A80, 0x1A90,
        0x1B50, 0x1BB0, 0x1C40, 0x1C50, 0xA620, 0xA8D0, 0xA900, 0xA9D0, 0xA9F0, 0xAA50, 0xABF0,
        0xFF10, 0x104A0, 0x10D30, 0x10D40, 0x11066, 0x110F0, 0x11136, 0x111D0, 0x112F0, 0x11450,
        0x114D0, 0x11650, 0x116C0, 0x116D0, 0x116DA, 0x11730, 0x118E0, 0x11950, 0x11BF0, 0x11C50,
        0x11D50, 0x11DA0, 0x11F50, 0x16130, 0x16A60, 0x16AC0, 0x16B50, 0x16D70, 0x1CCF0, 0x1D7CE,
        0x1D7D8, 0x1D7E2, 0x1D7EC, 0x1D7F6, 0x1E140, 0x1E2F0, 0x1E4F0, 0x1E5F1, 0x1E950, 0x1FBF0,
    ];
    let n = u32::from(c);
    ZEROS
        .iter()
        .find(|z| (**z..**z + 10).contains(&n))
        .map(|z| n - z)
}

/// `int(text)` of a command-line value: Python's whitespace around it, a sign, digits of any script with single underscores between
/// them; past `i64` it saturates (no count here reaches it). None where Python raised `ValueError`.
#[must_use]
pub fn py_int(text: &str) -> Option<i64> {
    let t = l7r_shared::py_text::strip(text);
    let (neg, digits) = match t.strip_prefix('-') {
        Some(d) => (true, d),
        None => (false, t.strip_prefix('+').unwrap_or(t)),
    };
    if digits.is_empty()
        || digits.starts_with('_')
        || digits.ends_with('_')
        || digits.contains("__")
    {
        return None;
    }
    let mut n: i64 = 0;
    for c in digits.chars().filter(|c| *c != '_') {
        n = n.saturating_mul(10).saturating_add(i64::from(decimal(c)?));
    }
    Some(if neg { -n } else { n })
}

/// `^#?(H?\d+)$` on a value already stripped: an entry id of the download list, `#17` or `H3` (its group, without the `#`).
fn entry_id(value: &str) -> Option<&str> {
    let v = value.strip_prefix('#').unwrap_or(value);
    let digits = v.strip_prefix('H').unwrap_or(v);
    (!digits.is_empty() && digits.chars().all(|c| decimal(c).is_some())).then_some(v)
}

/// `<file>=<key>[,<key>]` or `<file>=#17` / `<file>=H3` (feature 313 FR-006): an entry id resolves to the registry keys that download-list
/// entry names, `[]` where it names none, and is kept beside them. A word with no `=` is passed over, as the Python did.
///
/// # Errors
/// An id the list lacks, or a list that will not load: the access tags' own line (the Python's `SystemExit`).
pub fn resolve_matches(root: &Path, raw: &[String]) -> std::result::Result<Matched, String> {
    let mut out = Matched::default();
    for m in raw {
        let Some((name, value)) = m.split_once('=') else {
            continue;
        };
        let Some(eid) = entry_id(l7r_shared::py_text::strip(value)) else {
            out.set(
                name,
                value
                    .split(',')
                    .filter(|k| !k.is_empty())
                    .map(str::to_owned)
                    .collect(),
            );
            continue;
        };
        let keys = l7r_gate_downloads::record::access_tags::entry_keys_of(eid, root)?;
        out.set(name, keys);
        upsert(&mut out.downloads, name, eid.to_owned());
    }
    Ok(out)
}

fn entry_mut<'a>(
    table: &'a mut Map<String, Value>,
    name: &str,
    made: Value,
) -> Result<&'a mut Map<String, Value>> {
    match table.entry(name.to_owned()).or_insert(made) {
        Value::Object(m) => Ok(m),
        other => Err(Error::new(
            "TypeError",
            format!(
                "'{}' object does not support item assignment",
                l7r_shared::blocked::type_name(other)
            ),
        )),
    }
}

/// What the inbox did: each placed name with its archive path, and the names left waiting.
pub type Placed = (Vec<(String, String)>, Vec<String>);

/// Archive every inbox entry the table places, confirm the push, then delete it (FR-013): an entry is deleted only where its path is
/// confirmed in `origin/main`, so a failed push deletes nothing. A NEW entry - not in `gm-copies.json` - is processed only once `matched`
/// gives its keys (`[]` for one judged to copy no cited source, `make archive-inbox NONE=<file>`): FR-012 matches every GM file to its
/// key, and a file archived keyless and deleted would never be matched (plan review, Amendment 1). Until then it waits in the inbox.
/// The download-list entry each file answers (feature 313 FR-006) is recorded beside its keys, so a keyless entry's copy is found again
/// once its work enters the registry. The inbox is the store's GM folder.
///
/// # Errors
/// The table, the lock, a copy or a commit; a failed push (`RuntimeError`), after the table is written.
pub fn process_inbox(root: &Path, store: &Archive, matched: &Matched) -> Result<Placed> {
    let inbox = &store.gm;
    let mut table = gm_table(root)?;
    for (name, keys) in &matched.keys {
        let made = json!({"evidence": "matched by the session at the inbox (feature 309 FR-012)"});
        entry_mut(&mut table, name, made)?.insert("keys".into(), json!(keys));
    }
    for (name, eid) in &matched.downloads {
        entry_mut(&mut table, name, json!({"keys": []}))?.insert("download".into(), json!(eid));
    }
    let names: Vec<String> = sorted_entries(inbox, false)
        .iter()
        .filter_map(|p| p.file_name().map(|n| n.to_string_lossy().into_owned()))
        .filter(|n| !GM_LISTS.contains(&n.as_str()))
        .collect();
    // an entry over GitHub's file limit WAITS even once matched: it never reaches a commit (main says LFS or a split)
    let (waiting, names): (Vec<String>, Vec<String>) = names
        .into_iter()
        .partition(|n| !table.contains_key(n) || !too_big(&inbox.join(n)).is_empty());
    let mut placed = Vec::new();
    if names.is_empty() {
        return Ok((placed, waiting));
    }
    let failure = {
        let _held = store.locked(LOCK_WAIT)?;
        store.ensure()?;
        for name in &names {
            let dest = place_gm(store, name, &table[name])?;
            if !dest.is_empty() {
                entry_mut(&mut table, name, Value::Null)?.insert("archived".into(), json!(dest));
                placed.push((name.clone(), dest));
            }
        }
        store.push()?
    };
    write_table(root, &table)?;
    if !failure.is_empty() {
        return Err(Error::new(
            "RuntimeError",
            format!("the inbox is archived locally but the push failed, so nothing was deleted: {failure}"),
        ));
    }
    let confirmed = placed
        .iter()
        .map(|(name, dest)| on_github(store, dest).map(|held| (name, held)))
        .collect::<Result<Vec<_>>>()?;
    for (name, _) in confirmed.into_iter().filter(|(_, held)| *held) {
        let target = inbox.join(name);
        if target.is_dir() && !target.is_symlink() {
            rmtree(&target)?;
        } else {
            unlink(&target)?;
        }
    }
    Ok((placed, waiting))
}

/// `make archive-inbox`'s report: the placed files, then each waiting one - refused over GitHub's limit, or waiting on its keys - and
/// the GM's copies told to their rows.
///
/// # Errors
/// As [`process_inbox`], then `sync_gm_copies`.
pub fn inbox(root: &Path, store: &Archive, matched: &Matched, out: &mut String) -> Result<()> {
    let (placed, waiting) = process_inbox(root, store, matched)?;
    let _ = writeln!(
        out,
        "archive: {} inbox file(s) archived, pushed and removed from {}",
        placed.len(),
        store.gm.display()
    );
    for (name, dest) in &placed {
        let _ = writeln!(out, "  {name} -> {dest}");
    }
    for name in &waiting {
        let big = too_big(&store.gm.join(name));
        if big.is_empty() {
            let _ = writeln!(
                out,
                "  WAITING {name}: a new download - read its first page, find the source it copies, then `make archive-inbox \
                 MATCH='{name}=<key>'` - or MATCH='{name}=#<id>' for the download-list entry it answers (feature 313), or NONE='{name}' \
                 if it copies no cited source"
            );
        } else {
            let _ = writeln!(out, "{}", refused_line(name, &big, &store.gm.join(name)));
        }
    }
    crate::manifest::sync_gm_copies(root, store)?;
    Ok(())
}

/// A directory's entries in path order (none where it is no directory); `hidden` keeps the names a glob's `*` passes over.
#[must_use]
pub fn sorted_entries(dir: &Path, hidden: bool) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .filter(|e| hidden || !e.file_name().to_string_lossy().starts_with('.'))
        .map(|e| e.path())
        .collect();
    out.sort();
    out
}

/// The `.html` files of a directory in name order (`sorted(d.glob("*.html"))`, a hidden name taken as pathlib takes it), none where it is
/// no directory.
#[must_use]
pub fn html_files(dir: &Path) -> Vec<PathBuf> {
    sorted_entries(dir, true)
        .into_iter()
        .filter(|p| p.extension().is_some_and(|x| x == "html"))
        .collect()
}

/// A file read as `read_text(encoding="utf-8")`.
///
/// # Errors
/// Unreadable, or not UTF-8.
pub fn read_text(path: &Path) -> Result<String> {
    let bytes = std::fs::read(path).map_err(|e| os_error(&e, path))?;
    String::from_utf8(bytes).map_err(|e| {
        Error::new(
            "UnicodeDecodeError",
            format!("'utf-8' codec can't decode: {e}"),
        )
    })
}

/// Every URL the registry's pattern finds in a text (`_URL.findall`).
#[must_use]
pub fn urls_in(text: &str) -> Vec<String> {
    consulted::URL
        .find_iter(text)
        .map_while(std::result::Result::ok)
        .map(|m| m.as_str().to_owned())
        .collect()
}

/// Every URL a session has read (the page cache's own URLs first, then the sources-consulted ledger) with no row yet, sorted.
///
/// # Errors
/// A row, a cache entry's meta or the ledger that will not read.
pub fn consulted_urls(root: &Path) -> Result<Vec<String>> {
    let home = consulted::home(root);
    let mut seen_norm = HashSet::new();
    for p in row_files(root) {
        seen_norm.insert(norm(&row_url(&p)?));
    }
    let mut urls: Vec<(String, String)> = Vec::new();
    let mut index: HashMap<String, usize> = HashMap::new();
    let mut add = |n: String, u: String| {
        if !index.contains_key(&n) {
            index.insert(n.clone(), urls.len());
            urls.push((n, u));
        }
    };
    // `Path.glob("*/*/meta.json")`, whose `*` takes a hidden name too (pathlib's, unlike the `glob` module's)
    for shard in sorted_entries(&home.join(l7r_gate_research::pages::CACHE), true) {
        for entry in sorted_entries(&shard, true) {
            let meta = entry.join("meta.json");
            if meta.is_file() {
                let url = get_text(&load_row(&meta)?, "url")?;
                if url.starts_with("http") {
                    add(norm(&url), clean(&url));
                }
            }
        }
    }
    for row in consulted::read(&home)? {
        let n = get_text(&row, "url")?;
        if !n.is_empty() {
            // its spelling as read: the normalized form drops `www.`, which some hosts need (J-STAGE, feature 312)
            let raw = get_text(&row, "raw")?;
            add(
                n.clone(),
                if raw.starts_with("http") {
                    clean(&raw)
                } else {
                    format!("https://{n}")
                },
            );
        }
    }
    let mut out: Vec<String> = urls
        .into_iter()
        .filter(|(n, _)| !seen_norm.contains(n))
        .map(|(_, u)| u)
        .collect();
    out.sort();
    Ok(out)
}

/// The pages feature 312's filter kept: its work list and every uncited entry's URL (plan D8).
///
/// # Errors
/// The kept list or an entry that will not read.
pub fn kept_urls(root: &Path) -> Result<Vec<String>> {
    let mut out = Vec::new();
    for x in attempts::read(root, KEPT)? {
        out.push(field(&x, "raw")?);
    }
    for f in html_files(&attempts::base(root).join(attempts::UNCITED)) {
        out.extend(urls_in(&read_text(&f)?));
    }
    Ok(out)
}

/// The URLs, cleaned, that have no archive row yet - a page read again is not captured again (FR-014).
///
/// # Errors
/// A row that will not read.
pub fn unarchived(root: &Path, urls: &[String]) -> Result<Vec<String>> {
    let mut have = HashSet::new();
    for p in row_files(root) {
        have.insert(norm(&row_url(&p)?));
    }
    let mut out: Vec<String> = Vec::new();
    for url in urls.iter().map(|u| clean(u)) {
        if url.starts_with("http") && !have.contains(&norm(&url)) && !out.contains(&url) {
            out.push(url);
        }
    }
    Ok(out)
}

/// FR-011: of `urls`, the kept ones with no archive row - a page the filter did not keep is never archived.
///
/// # Errors
/// As [`kept_urls`] and [`unarchived`].
pub fn kept_only(root: &Path, urls: &[String]) -> Result<Vec<String>> {
    let keep: HashSet<String> = kept_urls(root)?.iter().map(|u| norm(u)).collect();
    Ok(unarchived(root, urls)?
        .into_iter()
        .filter(|u| keep.contains(&norm(u)))
        .collect())
}

/// Python's `xs[:n]` for an `int` from the command line: a negative `n` drops that many from the end.
#[must_use]
pub fn head<T: Clone>(xs: &[T], n: i64) -> Vec<T> {
    let len = i64::try_from(xs.len()).unwrap_or(i64::MAX);
    let end = if n >= 0 { n.min(len) } else { (len + n).max(0) };
    xs[..usize::try_from(end).unwrap_or(0)].to_vec()
}

/// What a run of lanes reaches: the browser, where each line goes as it is said, and the working copy.
pub struct Reach<'a> {
    pub start: &'a (dyn Fn(&Path) -> Result<Box<dyn Client>> + Sync),
    pub say: &'a (dyn Fn(&str) + Sync),
    pub store: &'a Archive,
}

/// `make archive-sources CONSULTED=1`: the kept uncited pages archived in lanes, as the cited backfill is - one lane ran 1,086 pages at
/// about 30 s each, some nine hours (2026-10-02), where the backfill's lanes, one host to a lane, share the waiting. Exit 1 where the
/// last push failed. The Python's lanes were processes, each its own `l7r-gate record archive lane`; these are threads, as the backfill's.
///
/// # Errors
/// The lists, the lock, a lane's error (the first a lane met), the rows settled.
pub fn consulted(root: &Path, limit: i64, workers: i64, reach: &Reach<'_>) -> Result<i32> {
    let mut all = consulted_urls(root)?;
    all.extend(kept_urls(root)?);
    let todo = kept_only(root, &all)?;
    let mut todo = if limit == 0 { todo } else { head(&todo, limit) };
    (reach.say)(&format!(
        "archive: {} kept uncited URL(s) with no copy yet, in up to {workers} lane(s) (feature 312: only what the filter kept)",
        todo.len()
    ));
    let store = reach.store;
    {
        let _held = store.locked(LOCK_WAIT)?;
        store.ensure()?;
    }
    todo.sort();
    let who = l7r_gate_research::record::archive::cited(&research(root))?;
    let jobs = lanes(&todo, usize::try_from(workers.max(1)).unwrap_or(1));
    let first_error: Arc<Mutex<Option<Error>>> = Arc::new(Mutex::new(None));
    std::thread::scope(|s| {
        for job in &jobs {
            let (who, first_error) = (&who, Arc::clone(&first_error));
            s.spawn(move || {
                let how = Lane {
                    root,
                    who,
                    start: reach.start,
                    say: reach.say,
                };
                if let Err(e) = lane(&how, job, store) {
                    if let Ok(mut f) = first_error.lock() {
                        f.get_or_insert(e);
                    }
                }
            });
        }
    });
    if let Some(e) = first_error.lock().ok().and_then(|mut f| f.take()) {
        return Err(e);
    }
    let failure = {
        let _held = store.locked(LOCK_WAIT)?;
        store.push()?
    };
    settle(root)?;
    Ok(i32::from(!failure.is_empty()))
}

/// The pages just read that have no row, archived with one browser and a push each (FR-014), each outcome said on `err`; the working
/// copy made only where a page is owed, as the Python made it (its credential is a process). The Python's forwarder started a browser
/// a URL; one serves them all here, the same pages fetched in the same order.
///
/// # Errors
/// The record, the browser, or a capture, as the Python raised them.
pub fn archive_urls(
    root: &Path,
    urls: &[String],
    start: &dyn Fn(&Path) -> Result<Box<dyn Client>>,
    store: &dyn Fn(&Path) -> Archive,
    err: &mut String,
) -> Result<()> {
    let todo = unarchived(root, urls)?;
    if todo.is_empty() {
        return Ok(());
    }
    let store = store(root);
    let store = &store;
    let who = l7r_gate_research::record::archive::cited(&research(root))?;
    let mut client = start(root)?;
    for url in &todo {
        let cited = who
            .iter()
            .find(|(u, _)| u == url)
            .map(|(_, c)| c.clone())
            .unwrap_or_default();
        let row = archive_url(root, url, &cited, client.as_mut(), store, true)?;
        let _ = writeln!(
            err,
            "archive: {} - {url}",
            row.get("outcome").map(py_str).unwrap_or_default()
        );
    }
    Ok(())
}

#[cfg(test)]
mod tests;
