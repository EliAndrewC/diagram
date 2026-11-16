//! One fetch of a URL (`archive.py`'s first part, feature 309; ported by feature 449 T146): the bytes from a plain request, and for a
//! web page its render - the MHTML snapshot and the visible text - through the one browser crate (`rust/browser/`, `l7r-browser serve`,
//! `ask:449-phase4-slices` Q4); a PDF's text from `pdftotext`, a text file's from itself. The browser sits behind [`Client`], the seam a
//! test replaces (the Python's `get` and `render`).

use std::path::Path;
use std::process::Command;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::html_text::unescape;
use l7r_guard::shared::py_text::{strip, SPACE_CLASS};
use serde_json::Value;

use crate::{Error, Result};

/// What one fetch of a URL brought back. `error` is set where nothing usable came.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Fetched {
    pub url: String,
    pub status: Option<i64>,
    pub final_url: String,
    pub content_type: String,
    pub body: Vec<u8>,
    pub mhtml: String,
    pub text: String,
    pub error: String,
}

impl Fetched {
    /// `Fetched(url, error=...)`.
    #[must_use]
    pub fn failed(url: &str, error: &str) -> Self {
        Self {
            url: url.to_owned(),
            error: error.to_owned(),
            ..Self::default()
        }
    }

    /// Whether the type names HTML (`"html" in content_type`, as written).
    #[must_use]
    pub fn is_html(&self) -> bool {
        self.content_type.contains("html")
    }

    /// `final_url or url`.
    #[must_use]
    pub fn landed(&self) -> &str {
        if self.final_url.is_empty() {
            &self.url
        } else {
            &self.final_url
        }
    }
}

/// The browser, as `archive.py`'s `Browser` was used: a request and a render, each politely spaced per host and retried as the Python
/// retried them.
pub trait Client {
    /// One request's outcome (`Browser.get`).
    fn get(&mut self, url: &str) -> Fetched;
    /// The page's MHTML and visible text, `("", "")` where it will not render (`Browser.render`).
    fn render(&mut self, url: &str) -> (String, String);
}

/// `mimetypes.guess_extension` as this container's Python 3.14 answers it, every type it knows (generated 2026-11-16 from
/// `mimetypes.init()`'s tables, the system's `/etc/mime.types` read in: the Python read that file at run time, so the table is the
/// Python's answer on this container, the case the differential compared).
static MIME: LazyLock<Vec<(&'static str, &'static str)>> = LazyLock::new(|| {
    include_str!("mimetypes.tsv")
        .lines()
        .filter_map(|l| l.split_once('\t'))
        .collect()
});

/// A URL's path as `urlparse` gives it: no query, no fragment, and no `;params` after its last segment.
fn url_path(url: &str) -> String {
    let parts = l7r_gate_research::verbatim::fetch::urlsplit(url).unwrap_or_default();
    let path = &parts[2];
    let tail = path.rfind('/').map_or(0, |i| i);
    match path[tail..].find(';') {
        Some(i) => path[..tail + i].to_owned(),
        None => path.clone(),
    }
}

/// `PurePosixPath(path).suffix` as Python 3.14 reads it: the name's leading dots dropped, then from its last dot on (`a.` gives `.`).
fn suffix(path: &str) -> String {
    let name = path
        .split('/')
        .filter(|s| !s.is_empty() && *s != ".")
        .next_back()
        .unwrap_or_default()
        .trim_start_matches('.');
    name.rfind('.')
        .map_or_else(String::new, |i| name[i..].to_owned())
}

/// The served file's extension, from its type and then its URL.
#[must_use]
pub fn ext_of(content_type: &str, url: &str) -> String {
    let kind = strip(content_type.split(';').next().unwrap_or_default()).to_lowercase();
    if kind.contains("html") {
        return ".html".to_owned();
    }
    if let Some((_, ext)) = MIME.iter().find(|(t, _)| *t == kind) {
        return match *ext {
            ".jpe" => ".jpg",
            ".htm" => ".html",
            e => e,
        }
        .to_owned();
    }
    let suffix = suffix(&url_path(url)).to_lowercase();
    let fits = suffix.len() >= 2
        && suffix.len() <= 6
        && suffix[1..]
            .bytes()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit());
    if fits {
        suffix
    } else {
        ".bin".to_owned()
    }
}

/// A PDF's text, by `pdftotext` (poppler); empty where it has none or the tool fails.
#[must_use]
pub fn pdf_text(body: &[u8]) -> String {
    let dir = std::env::temp_dir().join(format!(
        "l7r-archive-pdf-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_or(0, |d| d.as_nanos())
    ));
    let path = dir.join("f.pdf");
    let done = std::fs::create_dir_all(&dir)
        .and_then(|()| std::fs::write(&path, body))
        .and_then(|()| {
            Command::new("pdftotext")
                .arg("-layout")
                .arg(&path)
                .arg("-")
                .output()
        });
    let _ = std::fs::remove_dir_all(&dir);
    match done {
        Ok(o) if o.status.success() => String::from_utf8_lossy(&o.stdout).into_owned(),
        _ => String::new(),
    }
}

static TAGS: LazyLock<Regex> = LazyLock::new(|| {
    // `<(script|style|noscript)\b.*?</\1>|<[^>]+>` under `re.S | re.I`, its back-reference spelled out: Python matches `\1` without
    // regard to case (`<SCRIPT>...</script>`), where `fancy_regex`'s back-reference matches the captured text exactly
    crate::re(r"(?si)<script\b.*?</script>|<style\b.*?</style>|<noscript\b.*?</noscript>|<[^>]+>")
});
static BLANKS: LazyLock<Regex> = LazyLock::new(|| crate::re("[ \t]+"));
static LINE_ENDS: LazyLock<Regex> = LazyLock::new(|| crate::re(&format!("[{SPACE_CLASS}]+\n")));
static REVISION: LazyLock<Regex> =
    LazyLock::new(|| crate::re("\"wgRevisionId\"[ \t\n\r\x0b\x0c]*:[ \t\n\r\x0b\x0c]*([0-9]+)"));
static SNAPSHOT_TS: LazyLock<Regex> =
    LazyLock::new(|| crate::re(r"^(https?://web\.archive\.org/web/)(\d{14})/"));

/// A served HTML document's text without a browser - the text of a page that would not render whole.
#[must_use]
pub fn served_text(body: &[u8]) -> String {
    let decoded = String::from_utf8_lossy(body);
    let untagged = TAGS.replace_all(&decoded, " ");
    let unescaped = unescape(&untagged);
    let squeezed = BLANKS.replace_all(&unescaped, " ");
    strip(&LINE_ENDS.replace_all(&squeezed, "\n")).to_owned()
}

/// A `MediaWiki` page's revision id, from its page config (plan D7); empty for any other page.
#[must_use]
pub fn revision(body: &[u8]) -> String {
    let text = String::from_utf8_lossy(body);
    REVISION
        .captures(&text)
        .ok()
        .flatten()
        .map_or_else(String::new, |c| c[1].to_owned())
}

/// The statuses that mean the site is THERE but refuses an automated reader (a bot wall, a login, a rate limit), as against gone: a
/// refused page takes the GM's downloaded copy before a Wayback snapshot, a dead one the reverse (plan D2).
pub const REFUSING: [i64; 5] = [401, 403, 406, 429, 451];

/// `("", "")` where a live fetch brought the page back; else `("dead" | "refused", why)` (plan D10). Dead: a network error, a missing
/// page or a server failure, an empty body, or a redirect from a deeper path to the site's root (a moved page answered by its front
/// page). Refused: a [`REFUSING`] status, or a web page that rendered no text.
#[must_use]
pub fn failure(cited: &str, got: &Fetched) -> (&'static str, String) {
    if !got.error.is_empty() {
        return ("dead", got.error.clone());
    }
    let status = got
        .status
        .map_or_else(|| "None".to_owned(), |s| s.to_string());
    match got.status {
        Some(s) if REFUSING.contains(&s) => return ("refused", format!("HTTP {status}")),
        None => return ("dead", format!("HTTP {status}")),
        Some(s) if s >= 400 => return ("dead", format!("HTTP {status}")),
        _ => {}
    }
    if got.body.is_empty() {
        return ("dead", "an empty response".to_owned());
    }
    let deep = url_path(cited).trim_matches('/').to_owned();
    let landed = url_path(got.landed()).trim_matches('/').to_owned();
    if !deep.is_empty() && landed.is_empty() {
        return (
            "dead",
            format!("redirected to the site's front page ({})", got.final_url),
        );
    }
    if got.is_html() && strip(&got.text).is_empty() {
        return ("refused", "the page showed no text".to_owned());
    }
    ("", String::new())
}

/// A Wayback snapshot's URL for the bytes as archived (`id_`), without the archive's toolbar.
#[must_use]
pub fn snapshot_raw(url: &str) -> String {
    SNAPSHOT_TS.replace(url, "${1}${2}id_/").into_owned()
}

/// One URL's bytes, and for a web page its render; a PDF's text from the PDF, a text file's from itself. A URL on a blocked domain is
/// refused before any request (feature 312 FR-002).
///
/// # Errors
/// `Blocked`, as the Python raised it; or a blocked list that will not load.
pub fn fetch(client: &mut dyn Client, url: &str, record_dir: &Path) -> Result<Fetched> {
    l7r_gate_research::record::blocked::check(url, "an archive fetch", record_dir)?;
    let mut got = client.get(url);
    if !got.error.is_empty() || got.status.is_none_or(|s| s >= 400) {
        return Ok(got);
    }
    if got.is_html() {
        let at = got.landed().to_owned();
        (got.mhtml, got.text) = client.render(&at);
        if got.mhtml.is_empty() {
            got.text = served_text(&got.body);
        }
    } else if got.content_type.contains("pdf") || got.body.starts_with(b"%PDF-") {
        got.text = pdf_text(&got.body);
    } else if got.content_type.starts_with("text/") {
        got.text = String::from_utf8_lossy(&got.body).into_owned();
    }
    Ok(got)
}

/// The Wayback Machine's availability API.
pub const WAYBACK: &str = "https://archive.org/wayback/available?url=";

/// The newest snapshot the Wayback Machine holds of `url`: (its URL, its 14-digit time), or none.
///
/// # Errors
/// An answer the Python's `.get` chain would have raised on (`archived_snapshots` or `closest` not an object).
pub fn wayback(client: &mut dyn Client, url: &str) -> Result<Option<(String, String)>> {
    let asked = format!(
        "{WAYBACK}{}",
        l7r_gate_research::verbatim::fetch::quote(url, "")
    );
    let got = client.get(&asked);
    if !got.error.is_empty() || got.status != Some(200) {
        return Ok(None);
    }
    let Ok(text) = std::str::from_utf8(&got.body) else {
        return Ok(None);
    };
    let Ok(answer) = l7r_guard::shared::pyjson::loads(text) else {
        return Ok(None);
    };
    let attribute = |v: &Value| -> Result<()> {
        if v.is_object() {
            Ok(())
        } else {
            Err(Error::new(
                "AttributeError",
                format!("'{}' object has no attribute 'get'", py_type(v)),
            ))
        }
    };
    attribute(&answer)?;
    let empty = Value::Object(serde_json::Map::new());
    let snaps = answer.get("archived_snapshots").unwrap_or(&empty);
    attribute(snaps)?;
    let closest = snaps.get("closest").unwrap_or(&empty);
    attribute(closest)?;
    let truthy = |k: &str| {
        closest
            .get(k)
            .is_some_and(l7r_guard::shared::pyjson::truthy)
    };
    if !truthy("available") || !truthy("url") {
        return Ok(None);
    }
    let at = l7r_guard::shared::pyjson::py_str(&closest["url"]).replacen("http://", "https://", 1);
    let when = closest
        .get("timestamp")
        .map_or_else(String::new, l7r_guard::shared::pyjson::py_str);
    Ok(Some((at, when)))
}

/// Python's name for a JSON value's type, as an `AttributeError` names it.
fn py_type(v: &Value) -> &'static str {
    match v {
        Value::Null => "NoneType",
        Value::Bool(_) => "bool",
        Value::Number(n) if n.is_f64() => "float",
        Value::Number(_) => "int",
        Value::String(_) => "str",
        Value::Array(_) => "list",
        Value::Object(_) => "dict",
    }
}

#[cfg(test)]
mod tests;
