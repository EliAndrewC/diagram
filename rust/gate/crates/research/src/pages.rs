//! The saved-page cache keyed by URL (`scripts/record/sources.py`'s cache half, feature 288; ported by feature 449 T145, phase 4's S2
//! under `ask:449-phase4-slices`): `<mirror>/.specify/page-cache/<h2>/<h>/`, `<h>` the SHA-256 of the normalized URL, holding the page's
//! visible text as fetched (`text.txt`), its saved form in parts (`page.txt`, or `page.p1.txt` ...) and `meta.json`; [`CachedPages`],
//! which asks the cache first, stores what it fetches, and reads the archive behind a page that cannot be read (feature 376). The ledger
//! half is the guard's `shared::consulted`. `sources.py`'s cache half left with its last importers, `uncited.py` and `uncited_imports.py`
//! (feature 449 T147, S3b), so this is the cache's one implementation.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_shared::consulted::{self, norm};
use l7r_shared::py_text::{strip, SPACE_CLASS};
use l7r_shared::pyjson::{dumps, loads, py_str, truthy};
use serde_json::{json, Map, Value};

use crate::verbatim::fetch::{Got, Pages};
use crate::{re, Error, Result};

pub const CACHE: &str = "page-cache";
/// THE AGE RULE: a cached page older than this is fetched again (`REFRESH=1` fetches it at once); feature 288 R1's seven days.
pub const MAX_AGE_DAYS: f64 = 7.0;
/// The most characters one saved file holds (feature 250 D19).
pub const PART: usize = 20_000;

static SENTENCES: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        "(?<=[.!?])[{SPACE_CLASS}]+(?=[^{SPACE_CLASS}])|(?<=[\u{3002}\u{ff01}\u{ff1f}])[{SPACE_CLASS}]*(?=[^{SPACE_CLASS}])"
    ))
});
static PART_NUMBER: LazyLock<Regex> = LazyLock::new(|| re(r"\.p(\d+)\.txt$"));

fn fault(f: l7r_shared::blocked::Fault) -> Error {
    Error::new(f.kind, f.message)
}

/// `wrapped`: one sentence to a line (Latin and CJK stops), so a grep returns a passage.
#[must_use]
pub fn wrapped(text: &str) -> String {
    format!("{}\n", strip(&SENTENCES.replace_all(text, "\n")))
}

/// `str.splitlines(keepends=True)`.
fn lines_kept(text: &str) -> Vec<&str> {
    let mut out = Vec::new();
    let mut start = 0;
    let mut it = text.char_indices().peekable();
    while let Some((i, c)) = it.next() {
        if matches!(
            c,
            '\n' | '\r'
                | '\x0b'
                | '\x0c'
                | '\x1c'
                | '\x1d'
                | '\x1e'
                | '\u{85}'
                | '\u{2028}'
                | '\u{2029}'
        ) {
            let mut end = i + c.len_utf8();
            if c == '\r' && it.peek().is_some_and(|(_, n)| *n == '\n') {
                it.next();
                end += 1;
            }
            out.push(&text[start..end]);
            start = end;
        }
    }
    if start < text.len() {
        out.push(&text[start..]);
    }
    out
}

/// `parts`: `text` cut at line ends into pieces of at most `size` characters (a single longer line cut where it must).
#[must_use]
pub fn parts(text: &str, size: usize) -> Vec<String> {
    let mut out = Vec::new();
    let (mut cur, mut cur_len) = (String::new(), 0);
    for line in lines_kept(text) {
        let mut ln: Vec<char> = line.chars().collect();
        while ln.len() > size {
            if !cur.is_empty() {
                out.push(std::mem::take(&mut cur));
                cur_len = 0;
            }
            out.push(ln[..size].iter().collect());
            ln.drain(..size);
        }
        if cur_len + ln.len() > size {
            out.push(std::mem::take(&mut cur));
            cur_len = 0;
        }
        cur.extend(ln.iter());
        cur_len += ln.len();
    }
    if !cur.is_empty() {
        out.push(cur);
    }
    out
}

/// `entry_dir`: where a URL's page is kept.
#[must_use]
pub fn entry_dir(home: &Path, url: &str) -> PathBuf {
    let h = l7r_shared::sha256::hex(norm(url).as_bytes());
    home.join(CACHE).join(&h[..2]).join(h)
}

/// A page the cache holds.
#[derive(Debug, Clone, PartialEq)]
pub struct Cached {
    pub meta: Map<String, Value>,
    pub text: String,
    pub dir: PathBuf,
    pub files: Vec<String>,
}

impl Cached {
    /// When the page was fetched (`meta["fetched"]`).
    #[must_use]
    pub fn fetched(&self) -> String {
        self.meta.get("fetched").map(py_str).unwrap_or_default()
    }
}

fn now_micros() -> i64 {
    let d = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default();
    i64::try_from(d.as_micros()).unwrap_or(i64::MAX)
}

/// A file read as `read_text(encoding="utf-8")`: universal newlines; None where it cannot be opened, an error where it is not UTF-8.
fn read_text(path: &Path) -> Result<Option<String>> {
    let Ok(raw) = std::fs::read(path) else {
        return Ok(None);
    };
    let text =
        String::from_utf8(raw).map_err(|e| Error::new("UnicodeDecodeError", e.to_string()))?;
    Ok(Some(text.replace("\r\n", "\n").replace('\r', "\n")))
}

/// `cached`: the cached page of `url`, or None - absent, older than the age, or (where `exact`) an imported copy.
///
/// # Errors
/// What the Python raised: a file that is not UTF-8, a `meta.json` with no `fetched` or one `fromisoformat` refuses or a naive time.
pub fn cached(home: &Path, url: &str, max_age_days: f64, exact: bool) -> Result<Option<Cached>> {
    let d = entry_dir(home, url);
    let Some(meta) = read_text(&d.join("meta.json"))? else {
        return Ok(None);
    };
    let Ok(meta) = loads(&meta) else {
        return Ok(None);
    };
    let Some(text) = read_text(&d.join("text.txt"))? else {
        return Ok(None);
    };
    let Value::Object(meta) = meta else {
        return Err(Error::new(
            "TypeError",
            "list indices must be integers or slices, not str",
        ));
    };
    let fetched = meta
        .get("fetched")
        .ok_or_else(|| Error::new("KeyError", "'fetched'"))?;
    let stamp = fetched
        .as_str()
        .ok_or_else(|| Error::new("TypeError", "fromisoformat: argument must be str"))?;
    let (at, zone) = l7r_shared::iso::moment(stamp)
        .ok_or_else(|| Error::new("ValueError", format!("Invalid isoformat string: '{stamp}'")))?;
    let zone = zone.ok_or_else(|| {
        Error::new(
            "TypeError",
            "can't subtract offset-naive and offset-aware datetimes",
        )
    })?;
    #[expect(
        clippy::cast_precision_loss,
        reason = "an age in microseconds, compared with a number of days"
    )]
    let age = (now_micros() - (at - zone)) as f64;
    let wanted_exact = meta.get("exact").is_some_and(truthy);
    if age > max_age_days * 86_400e6 || (exact && !wanted_exact) {
        return Ok(None);
    }
    let mut files: Vec<String> = std::fs::read_dir(&d)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| n.starts_with("page") && crate::has_ext(n, "txt"))
        .collect();
    files.sort();
    let key = |n: &String| -> u64 {
        PART_NUMBER
            .captures(n)
            .ok()
            .flatten()
            .and_then(|c| c[1].parse().ok())
            .unwrap_or(0)
    };
    files.sort_by_key(key);
    Ok(Some(Cached {
        meta,
        text,
        dir: d,
        files,
    }))
}

/// `_write`: written to a temporary name and renamed, so a reader never sees half a file.
fn write_whole(path: &Path, text: &str) -> Result<()> {
    let name = path
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let tmp = path.with_file_name(format!(".{name}.{}.tmp", std::process::id()));
    std::fs::write(&tmp, text)
        .and_then(|()| std::fs::rename(&tmp, path))
        .map_err(|e| Error::new("OSError", e.to_string()))
}

/// How a page came to be stored.
pub struct Stored<'a> {
    pub fetched: Option<&'a str>,
    pub exact: bool,
    pub origin: &'a str,
}

/// `put`: one page stored - its text, its saved form in parts, and `meta.json` last.
///
/// # Errors
/// A blocked URL, the lock, or a write.
pub fn put(
    home: &Path,
    url: &str,
    text: &str,
    how: &Stored<'_>,
    record_dir: &Path,
) -> Result<Cached> {
    consulted::check(url, "the page cache", record_dir).map_err(fault)?;
    let d = entry_dir(home, url);
    std::fs::create_dir_all(&d).map_err(|e| Error::new("OSError", e.to_string()))?;
    let pieces = parts(&wrapped(text), PART);
    let _lock = consulted::locked(home, 30.0).map_err(fault)?;
    for e in std::fs::read_dir(&d).into_iter().flatten().flatten() {
        let n = e.file_name().to_string_lossy().into_owned();
        if n.starts_with("page") && crate::has_ext(&n, "txt") {
            std::fs::remove_file(e.path()).map_err(|e| Error::new("OSError", e.to_string()))?;
        }
    }
    write_whole(&d.join("text.txt"), text)?;
    let names: Vec<String> = if pieces.len() == 1 {
        vec!["page.txt".to_owned()]
    } else {
        (1..=pieces.len())
            .map(|k| format!("page.p{k}.txt"))
            .collect()
    };
    for (name, piece) in names.iter().zip(&pieces) {
        write_whole(&d.join(name), piece)?;
    }
    let mut meta = Map::new();
    meta.insert("url".into(), json!(url));
    meta.insert("norm".into(), json!(norm(url)));
    meta.insert(
        "fetched".into(),
        json!(how.fetched.map_or_else(consulted::now, str::to_owned)),
    );
    meta.insert("chars".into(), json!(text.chars().count()));
    meta.insert("exact".into(), json!(how.exact));
    meta.insert("origin".into(), json!(how.origin));
    write_whole(
        &d.join("meta.json"),
        &(dumps(&Value::Object(meta.clone()), Some(1), false) + "\n"),
    )?;
    Ok(Cached {
        meta,
        text: text.to_owned(),
        dir: d,
        files: names,
    })
}

/// `refresh_wanted`: `REFRESH=1` on any make target that saves or checks a page.
#[must_use]
pub fn refresh_wanted() -> bool {
    !matches!(consulted::var("REFRESH").as_str(), "" | "0")
}

/// `archived_text`: (the readable text of the archive's capture of `url`, its capture date), or None.
#[must_use]
pub fn archived_text(url: &str, manifest_root: &Path, store: &Path) -> Option<(String, String)> {
    let uid = l7r_shared::cited_url::url_id(url);
    let row = std::fs::read(
        manifest_root
            .join("research/archive")
            .join(&uid[..2])
            .join(format!("{uid}.json")),
    )
    .ok()?;
    let row = loads(&String::from_utf8(row).ok()?).ok()?;
    let path = row.get("path")?.as_str()?;
    let bytes = std::fs::read(store.join(path).join("text.txt")).ok()?;
    let text = String::from_utf8_lossy(&bytes)
        .replace("\r\n", "\n")
        .replace('\r', "\n");
    let captured: String = row
        .get("captured")
        .map(py_str)
        .unwrap_or_default()
        .chars()
        .take(10)
        .collect();
    (!strip(&text).is_empty()).then_some((text, captured))
}

/// The fetcher behind the cache: the network's, or none (a cache-only read names a page it does not hold).
pub enum Inner {
    Pages(Pages),
    NotCached,
}

/// `CachedPages`: asks the cache first and stores what it fetches (FR-008 - FR-010).
pub struct CachedPages {
    pub inner: Inner,
    pub home: PathBuf,
    pub refresh: bool,
    pub exact: bool,
    pub max_age: f64,
    /// (the manifest's root, the archive's working copy).
    pub archive: (PathBuf, PathBuf),
    pub record_dir: PathBuf,
}

impl CachedPages {
    #[must_use]
    pub fn new(
        inner: Inner,
        home: &Path,
        refresh: bool,
        exact: bool,
        root: &Path,
        record_dir: &Path,
    ) -> Self {
        Self {
            inner,
            home: home.to_path_buf(),
            refresh,
            exact,
            max_age: MAX_AGE_DAYS,
            archive: (root.to_path_buf(), home.join("source-archive")),
            record_dir: record_dir.to_path_buf(),
        }
    }

    /// The hosts that refused this run.
    #[must_use]
    pub fn refused(&self) -> Vec<(String, String)> {
        match &self.inner {
            Inner::Pages(p) => p.refused.clone(),
            Inner::NotCached => Vec::new(),
        }
    }

    /// `get`: a blocked URL never fetched; the cache, else the fetch (stored), else the archive behind a page that cannot be read.
    ///
    /// # Errors
    /// The blocked list or the cache unreadable, a store that failed, or a URL `urlsplit` refuses.
    pub fn get(&mut self, url: &str) -> Result<Got> {
        let rules = l7r_shared::blocked::domains(&self.record_dir).map_err(fault)?;
        if let Some(rule) = l7r_shared::blocked::blocked(url, &rules) {
            let mut got = Got::state(
                "UNFETCHABLE",
                &l7r_shared::blocked::refusal(url, rule, "a fetch"),
            );
            got.blocked = true;
            return Ok(got);
        }
        if !self.refresh {
            if let Some(hit) = cached(&self.home, url, self.max_age, self.exact)? {
                let mut got = Got::fetched(hit.text.clone());
                got.cached = Some(hit.fetched());
                return Ok(got);
            }
        }
        let got = match &mut self.inner {
            Inner::Pages(p) => p.get(url).map_err(|e| Error::new("ValueError", e))?,
            Inner::NotCached => Got::state(
                "NOT-CACHED",
                "not in the page cache (quote-verbatim could not save it) - fetch it yourself",
            ),
        };
        if got.state == "FETCHED" {
            let how = Stored {
                fetched: None,
                exact: true,
                origin: "fetch",
            };
            put(&self.home, url, &got.text, &how, &self.record_dir)?;
            return Ok(got);
        }
        if got.state == "NOT-CHECKED" || got.state == "UNFETCHABLE" {
            if let Some((text, captured)) = archived_text(url, &self.archive.0, &self.archive.1) {
                let mut kept = Got::fetched(text);
                kept.archived = Some(captured);
                kept.live = got.live;
                return Ok(kept);
            }
        }
        Ok(got)
    }
}

#[cfg(test)]
mod tests;
