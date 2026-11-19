//! The sources-consulted ledger (`scripts/record/sources.py`'s ledger half, feature 288; moved here by feature 449 T145, phase 4's S2 under
//! `ask:449-phase4-slices`): the normalized URL, the mirror's `.specify/` the ledger and the page cache live under, the feature, clone and
//! session a line is written under, the polled lock, and the ledger's lines read, appended and shown. In the guard's shared code because
//! the blocked-fetch guard writes an attempt in process (`shared::attempts`) and the attempts log takes this ledger's lock; the gate's
//! `l7r-gate record sources` and `source-pages` call the same functions. `sources.py` keeps only `repo_root` and `home` (and its
//! forwarders' `raised`) for `archive.py`, S4's door, until S4 (feature 449 T147 deleted the rest with `uncited*.py`); an edit of those
//! makes the same change here in the same commit (the ruling's Q1).

use std::fs::File;
use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use crate::shared::blocked::{blocked, domains, refusal, type_name, Fault};
use crate::shared::py_text::{strip, SPACE_CLASS};
use crate::shared::pyjson::{dumps, loads, py_str, truthy};

pub const LEDGER: &str = "sources-consulted.jsonl";
pub const LOCK: &str = "sources-consulted.lock";
/// What `make source-outcome` takes, as its refusal names it.
pub const OUTCOMES: &str =
    "cited:<registry key> | rejected:<why> | nothing-found | unreadable | pending";

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static OUTCOME: LazyLock<Regex> = LazyLock::new(|| {
    re(&format!(
        r"^(?:cited:[a-z0-9][a-z0-9-]*|rejected:[{SPACE_CLASS}]*[^{SPACE_CLASS}][\s\S]*|nothing-found|unreadable|pending)\z"
    ))
});
/// `_URL`: a URL as the registry and the uncited write-ups carry one.
pub static URL: LazyLock<Regex> =
    LazyLock::new(|| re(&format!(r#"https?://[^{SPACE_CLASS}<"']+"#)));
static WIKI_MOBILE: LazyLock<Regex> = LazyLock::new(|| re(r"^([a-z]{2,3})\.m\.wikipedia"));

/// `urllib.parse.unquote`: each `%XX` decoded inside every ASCII run, its bytes read as UTF-8 with a bad sequence replaced.
#[must_use]
pub fn unquote(s: &str) -> String {
    if !s.contains('%') {
        return s.to_owned();
    }
    let mut out = String::with_capacity(s.len());
    let mut run: Vec<u8> = Vec::new();
    let flush = |run: &mut Vec<u8>, out: &mut String| {
        if !run.is_empty() {
            out.push_str(&String::from_utf8_lossy(run));
            run.clear();
        }
    };
    let mut chars = s.char_indices().peekable();
    while let Some((at, c)) = chars.next() {
        if !c.is_ascii() {
            flush(&mut run, &mut out);
            out.push(c);
            continue;
        }
        let pair = s
            .get(at + 1..at + 3)
            .filter(|p| p.bytes().all(|b| b.is_ascii_hexdigit()));
        match pair {
            Some(hex) if c == '%' => {
                run.push(u8::from_str_radix(hex, 16).unwrap_or(0));
                chars.next();
                chars.next();
            }
            _ => run.push(u8::try_from(c).unwrap_or(b'?')),
        }
    }
    flush(&mut run, &mut out);
    out
}

/// `norm`: the normalization of feature 288's measurement - scheme, `www.`, the mobile host, a fragment and a trailing slash dropped;
/// percent-decoded; lower-cased, except a Wikipedia path, whose case is the article's name.
#[must_use]
pub fn norm(u: &str) -> String {
    let u = strip(u).trim_matches(|c| "'\"<>),.;:".contains(c));
    let u = unquote(u);
    let u = u.split('#').next().unwrap_or("");
    let u = u
        .strip_prefix("https://")
        .or_else(|| u.strip_prefix("http://"))
        .unwrap_or(u);
    let u = u.strip_prefix("www.").unwrap_or(u);
    let u = WIKI_MOBILE.replace(u, "$1.wikipedia").into_owned();
    let u = u.strip_prefix("m.").unwrap_or(&u);
    let u = u.trim_end_matches('/');
    if !u.contains("wikipedia") {
        return u.to_lowercase();
    }
    match u.find('/') {
        Some(at) => format!("{}{}", u[..at].to_lowercase(), &u[at..]),
        None => u.to_lowercase(),
    }
}

/// `repo_root`: the nearest directory above `start` (the working directory) holding `.git`.
#[must_use]
pub fn repo_root(start: Option<&Path>) -> PathBuf {
    let here = start.map_or_else(
        || std::env::current_dir().unwrap_or_default(),
        Path::to_path_buf,
    );
    let mut root = std::fs::canonicalize(&here).unwrap_or(here);
    while !root.join(".git").exists() {
        match root.parent() {
            Some(up) => root = up.to_path_buf(),
            None => break,
        }
    }
    root
}

/// `home`: the mirror's `.specify/`, where the ledger and the cache live; `L7R_SOURCES_HOME` moves it (the tests' seam).
#[must_use]
pub fn home(root: &Path) -> PathBuf {
    let at = var("L7R_SOURCES_HOME");
    if !at.is_empty() {
        return PathBuf::from(at);
    }
    let mirror = match root.parent() {
        Some(up) if up.file_name().is_some_and(|n| n == ".clones") => {
            up.parent().unwrap_or(root).to_path_buf()
        }
        _ => root.to_path_buf(),
    };
    mirror.join(".specify")
}

/// An environment variable, "" where unset or not text.
#[cfg(not(test))]
#[must_use]
pub fn var(name: &str) -> String {
    std::env::var(name).unwrap_or_default()
}

#[cfg(test)]
thread_local! {
    /// The tests' environment: each test thread its own, so a test that names a variable never races another.
    pub static VARS: std::cell::RefCell<std::collections::HashMap<String, String>> = std::cell::RefCell::default();
}

/// An environment variable, read from the test thread's own map.
#[cfg(test)]
#[must_use]
pub fn var(name: &str) -> String {
    VARS.with(|v| v.borrow().get(name).cloned().unwrap_or_default())
}

/// `context`: the feature, clone and session a ledger line is written under, as a mapping in that order.
///
/// # Errors
/// Where the Python raised reading `.specify/feature.json`: its value not a mapping, its directory not text, its bytes not UTF-8.
pub fn context(root: &Path) -> Result<Map<String, Value>, Fault> {
    let mut feature = var("SPECIFY_FEATURE");
    let pointer = root.join(".specify").join("feature.json");
    if feature.is_empty() && pointer.is_file() {
        let bytes = std::fs::read(&pointer)
            .map_err(|e| Fault::new("OSError", format!("{}: {e}", pointer.display())))?;
        let text = String::from_utf8(bytes).map_err(|_| {
            Fault::new(
                "UnicodeDecodeError",
                format!("'utf-8' codec can't decode {}", pointer.display()),
            )
        })?;
        if let Ok(data) = loads(&text) {
            let Value::Object(map) = &data else {
                return Err(Fault::new(
                    "AttributeError",
                    format!("'{}' object has no attribute 'get'", type_name(&data)),
                ));
            };
            match map.get("feature_directory") {
                None => {}
                Some(Value::String(dir)) => {
                    feature = Path::new(dir)
                        .file_name()
                        .map(|n| n.to_string_lossy().into_owned())
                        .unwrap_or_default();
                }
                Some(other) => {
                    return Err(Fault::new(
                        "TypeError",
                        format!(
                            "expected str, bytes or os.PathLike object, not {}",
                            type_name(other)
                        ),
                    ))
                }
            }
        }
    }
    let session = Some(var("L7R_PAGE_SESSION"))
        .filter(|s| !s.is_empty())
        .unwrap_or_else(|| var("CLAUDE_CODE_SESSION_ID"));
    let mut out = Map::new();
    out.insert(
        "feature".into(),
        json!(feature.split('-').next().unwrap_or("")),
    );
    out.insert(
        "clone".into(),
        json!(root
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default()),
    );
    out.insert("session".into(), json!(session));
    Ok(out)
}

/// `locked`: `flock` on the ledger's lock file in `dir`, polled so a hung holder is an error rather than a hang; the open file holds it.
///
/// # Errors
/// The directory or the file cannot be made, or the lock is not taken within `timeout` seconds (Python's `TimeoutError`).
pub fn locked(dir: &Path, timeout: f64) -> Result<File, Fault> {
    let path = dir.join(LOCK);
    match crate::shared::tool::flock_within(&path, timeout) {
        Ok(Some(file)) => Ok(file),
        Ok(None) => Err(Fault::new(
            "TimeoutError",
            format!(
                "could not take {} within {}s",
                path.display(),
                crate::shared::py_text::fmt_g(timeout)
            ),
        )),
        Err(e) => Err(Fault::new("OSError", e.to_string())),
    }
}

/// `blocked.check`: a URL on a blocked domain refused before it is stored (feature 312), the list read from `record_dir`.
///
/// # Errors
/// The URL is blocked (`Blocked`), or the list cannot be trusted (the loader's refusal).
pub fn check(url: &str, what: &str, record_dir: &Path) -> Result<(), Fault> {
    let rules = domains(record_dir)?;
    match blocked(url, &rules) {
        Some(rule) => Err(Fault::new("Blocked", refusal(url, rule, what))),
        None => Ok(()),
    }
}

/// A row's field (`r.get(name)`), where the row must be a mapping.
///
/// # Errors
/// A row that is not a mapping (Python's `AttributeError`).
pub fn get<'v>(row: &'v Value, name: &str) -> Result<Option<&'v Value>, Fault> {
    match row {
        Value::Object(map) => Ok(map.get(name)),
        other => Err(Fault::new(
            "AttributeError",
            format!("'{}' object has no attribute 'get'", type_name(other)),
        )),
    }
}

/// `append`: the rows, each URL checked against the blocked list first, appended as JSON lines under the lock.
///
/// # Errors
/// A blocked URL, the lock, or the write.
pub fn append(dir: &Path, rows: &[Value], record_dir: &Path) -> Result<(), Fault> {
    if rows.is_empty() {
        return Ok(());
    }
    for r in rows {
        let raw = get(r, "raw")?.filter(|v| truthy(v)).or(get(r, "url")?);
        check(
            &raw.map(py_str).unwrap_or_default(),
            "a sources-consulted ledger line",
            record_dir,
        )?;
    }
    let _lock = locked(dir, 30.0)?;
    let text: String = rows.iter().map(|r| dumps(r, None, false) + "\n").collect();
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(dir.join(LEDGER))
        .and_then(|mut f| f.write_all(text.as_bytes()))
        .map_err(|e| Fault::new("OSError", e.to_string()))
}

/// `read`: every line of a JSON-lines file that parses, in order (a value of any kind); a missing file is none.
///
/// # Errors
/// A file that is not UTF-8 (`read_text`'s `UnicodeDecodeError`), or that cannot be read.
pub fn read_lines(path: &Path) -> Result<Vec<Value>, Fault> {
    if !path.is_file() {
        return Ok(Vec::new());
    }
    let bytes = std::fs::read(path).map_err(|e| Fault::new("OSError", e.to_string()))?;
    let text = String::from_utf8(bytes).map_err(|e| {
        Fault::new(
            "UnicodeDecodeError",
            format!("'utf-8' codec can't decode {}: {e}", path.display()),
        )
    })?;
    Ok(crate::shared::checks::reply::py_lines(&text)
        .into_iter()
        .filter_map(|l| loads(l).ok())
        .collect())
}

/// `read`: the ledger's lines.
///
/// # Errors
/// As [`read_lines`].
pub fn read(dir: &Path) -> Result<Vec<Value>, Fault> {
    read_lines(&dir.join(LEDGER))
}

/// `now()`: the UTC time to the second, as `isoformat(timespec="seconds")` writes it.
#[must_use]
pub fn now() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = crate::shared::log::civil(secs);
    format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}+00:00")
}

/// `line`: one ledger line, its keys in the Python's order.
#[must_use]
pub fn line(ctx: &Map<String, Value>, url: &str, outcome: &str, questions: &[String]) -> Value {
    let mut row = Map::new();
    row.insert("url".into(), json!(norm(url)));
    row.insert("raw".into(), json!(url));
    row.insert("utc".into(), json!(now()));
    for (k, v) in ctx {
        row.insert(k.clone(), v.clone());
    }
    row.insert("questions".into(), json!(questions));
    row.insert("outcome".into(), json!(outcome));
    Value::Object(row)
}

/// `valid_outcome`.
#[must_use]
pub fn valid_outcome(outcome: &str) -> bool {
    OUTCOME.is_match(strip(outcome)).unwrap_or(false)
}

/// A value Python joins or slices as text.
///
/// # Errors
/// A value that is not a string (Python's `TypeError`).
pub fn text<'v>(v: &'v Value, what: &str) -> Result<&'v str, Fault> {
    v.as_str().ok_or_else(|| {
        Fault::new(
            "TypeError",
            format!("{what}: expected str instance, {} found", type_name(v)),
        )
    })
}

/// `show`: one ledger line as a reader wants it - when, who, what for, what came of it.
///
/// # Errors
/// A line Python could not show: not a mapping, or a field of the wrong kind.
pub fn show(row: &Value) -> Result<String, Fault> {
    let field = |name: &str| get(row, name);
    let mut who: Vec<String> = Vec::new();
    if let Some(f) = field("feature")?.filter(|v| truthy(v)) {
        who.push(format!("f{}", py_str(f)));
    }
    if let Some(c) = field("clone")?.filter(|v| truthy(v)) {
        who.push(text(c, "sequence item 1")?.to_owned());
    }
    if let Some(s) = field("session")?.filter(|v| truthy(v)) {
        let s = text(s, "session")?;
        who.push(format!("s:{}", s.chars().take(8).collect::<String>()));
    }
    let who = who.join(" ");
    let reads = match field("reads")? {
        None => 1.0,
        Some(v) => v
            .as_f64()
            .or_else(|| v.as_bool().map(f64::from))
            .ok_or_else(|| {
                Fault::new(
                    "TypeError",
                    format!(
                        "'>' not supported between instances of '{}' and 'int'",
                        type_name(v)
                    ),
                )
            })?,
    };
    let reads = if reads > 1.0 {
        format!(" x{}", py_str(field("reads")?.unwrap_or(&Value::Null)))
    } else {
        String::new()
    };
    let mut qs: Vec<String> = Vec::new();
    match field("questions")?.filter(|v| truthy(v)) {
        None => {}
        // a string joins its characters, as `"; ".join` iterates one
        Some(Value::String(s)) => qs.extend(s.chars().map(String::from)),
        Some(Value::Array(items)) => {
            for (i, item) in items.iter().enumerate() {
                qs.push(text(item, &format!("sequence item {i}"))?.to_owned());
            }
        }
        Some(_) => {
            return Err(Fault::new(
                "TypeError",
                "can only join an iterable".to_owned(),
            ))
        }
    }
    let qs = qs.join("; ");
    let utc = match field("utc")? {
        None => String::new(),
        Some(v) => text(v, "utc")?.chars().take(10).collect(),
    };
    let outcome = field("outcome")?.map(py_str).unwrap_or_default();
    let tail = if qs.is_empty() {
        String::new()
    } else {
        format!("  q: {}", qs.chars().take(240).collect::<String>())
    };
    Ok(format!(
        "  {utc}  {}{reads}  {outcome}{tail}",
        if who.is_empty() { "-" } else { &who }
    ))
}

/// `earlier`: the ledger's lines for a URL.
///
/// # Errors
/// A line that is not a mapping (Python's `AttributeError`).
pub fn earlier(dir: &Path, url: &str) -> Result<Vec<Value>, Fault> {
    let key = Value::String(norm(url));
    let mut out = Vec::new();
    for r in read(dir)? {
        if get(&r, "url")? == Some(&key) {
            out.push(r);
        }
    }
    Ok(out)
}

/// `by_key`: the `cited:` lines whose key the pattern finds.
///
/// # Errors
/// A pattern that does not compile (`re.error`), or a line that is not a mapping.
pub fn by_key(dir: &Path, pattern: &str) -> Result<Vec<Value>, Fault> {
    let rx = crate::shared::regex::build(pattern)
        .map_err(|e| Fault::new("PatternError", e.to_string()))?;
    let mut out = Vec::new();
    for r in read(dir)? {
        let outcome = get(&r, "outcome")?.map(py_str).unwrap_or_default();
        if let Some(key) = outcome.strip_prefix("cited:") {
            if rx.is_match(key).unwrap_or(false) {
                out.push(r);
            }
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
