//! Fetching a page (`quote_verbatim.Pages`, feature 449 T145): each URL once, each host at most once after it refuses, a timeout on every
//! fetch, the charset honored, a PDF not read. THE ONE SEAM TO THE NETWORK: [`Transport`], whose real form runs `curl` as an external
//! program - as `pdftotext` stays one (`ask:449-T80-order`), and no HTTP or TLS crate enters the gate's build - asked to behave as Python's
//! `urllib.request.urlopen` did: HTTP/1.1, the same two headers, redirects followed (ten at most), a 20 s stall a failure, a status
//! outside 2xx `HTTPError: HTTP Error <code>: <reason>` from the last response's own status line. The proxy settings of the environment
//! (`http_proxy`, `https_proxy`, `no_proxy`) reach curl as they reached urllib. A failure below HTTP (a refused connection, a bad
//! certificate, a stall) is named by curl's own words inside the Python's fixed form `<kind>: <words>`, the library's text being the
//! Rust's (`ask:449-T066-json-message`).

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_shared::py_text::strip;
use unicode_normalization::UnicodeNormalization as _;

use super::{decode, visible_text};

/// What a fetch came to: `FETCHED` with its text, or a state and why.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Got {
    pub state: String,
    pub text: String,
    pub why: String,
    /// The page cache's copy: when it was fetched.
    pub cached: Option<String>,
    /// The archive's text: the capture's date.
    pub archived: Option<String>,
    /// The link answered this run.
    pub live: bool,
    /// Refused by the blocked list, never fetched.
    pub blocked: bool,
}

impl Got {
    #[must_use]
    pub fn state(state: &str, why: &str) -> Self {
        Self {
            state: state.to_owned(),
            why: why.to_owned(),
            ..Self::default()
        }
    }

    #[must_use]
    pub fn fetched(text: String) -> Self {
        Self {
            state: "FETCHED".to_owned(),
            text,
            ..Self::default()
        }
    }
}

/// `urllib.parse.urlsplit`'s five parts, or its `ValueError`.
///
/// # Errors
/// A netloc with one bracket, a bracketed host that is not an IPv6 address, or one NFKC turns into a delimiter.
pub fn urlsplit(url: &str) -> Result<[String; 5], String> {
    let url = url.trim_start_matches(|c: char| c <= ' ');
    let mut url: String = url
        .chars()
        .filter(|c| !matches!(c, '\t' | '\r' | '\n'))
        .collect();
    let mut scheme = String::new();
    if let Some(i) = url.find(':').filter(|&i| i > 0) {
        let head = &url[..i];
        let first = head.chars().next().unwrap_or(' ');
        if first.is_ascii_alphabetic()
            && head
                .chars()
                .all(|c| c.is_ascii_alphanumeric() || matches!(c, '+' | '-' | '.'))
        {
            scheme = head.to_ascii_lowercase();
            url = url[i + 1..].to_owned();
        }
    }
    let mut netloc = String::new();
    if url.starts_with("//") {
        let end = url[2..].find(['/', '?', '#']).map_or(url.len(), |p| p + 2);
        url[2..end].clone_into(&mut netloc);
        url = url[end..].to_owned();
        if netloc.contains('[') != netloc.contains(']') {
            return Err("Invalid IPv6 URL".to_owned());
        }
        if netloc.contains('[') {
            bracketed(&netloc)?;
        }
    }
    let mut fragment = String::new();
    if let Some((u, f)) = url.split_once('#') {
        f.clone_into(&mut fragment);
        url = u.to_owned();
    }
    let mut query = String::new();
    if let Some((u, q)) = url.split_once('?') {
        q.clone_into(&mut query);
        url = u.to_owned();
    }
    check_netloc(&netloc)?;
    Ok([scheme, netloc, url, query, fragment])
}

/// `_check_bracketed_netloc` and `_check_bracketed_host`.
fn bracketed(netloc: &str) -> Result<(), String> {
    let host_port = netloc.rsplit('@').next().unwrap_or("");
    let invalid = || Err("Invalid IPv6 URL".to_owned());
    let host = match host_port.split_once('[') {
        Some((before, rest)) => {
            if !before.is_empty() {
                return invalid();
            }
            let (host, port) = rest.split_once(']').unwrap_or((rest, ""));
            if !port.is_empty() && !port.starts_with(':') {
                return invalid();
            }
            host
        }
        None => host_port.split(':').next().unwrap_or(""),
    };
    if let Some(rest) = host.strip_prefix('v') {
        let (hex, tail) = rest.split_once('.').unwrap_or((rest, ""));
        if hex.is_empty() || !hex.chars().all(|c| c.is_ascii_hexdigit()) || tail.is_empty() {
            return Err("IPvFuture address is invalid".to_owned());
        }
        return Ok(());
    }
    if host.parse::<std::net::Ipv4Addr>().is_ok() {
        return Err("An IPv4 address cannot be in brackets".to_owned());
    }
    host.split('%')
        .next()
        .unwrap_or("")
        .parse::<std::net::Ipv6Addr>()
        .map(|_| ())
        .map_err(|_| format!("'{host}' does not appear to be an IPv4 or IPv6 address"))
}

/// `_checknetloc`: a netloc whose NFKC form holds a delimiter it did not.
fn check_netloc(netloc: &str) -> Result<(), String> {
    if netloc.is_ascii() {
        return Ok(());
    }
    let n: String = netloc
        .chars()
        .filter(|c| !matches!(c, '@' | ':' | '#' | '?'))
        .collect();
    let folded: String = n.nfkc().collect();
    if n != folded && folded.contains(['/', '?', '#', '@', ':']) {
        return Err(format!(
            "netloc '{netloc}' contains invalid characters under NFKC normalization"
        ));
    }
    Ok(())
}

/// `urllib.parse.quote(text, safe)`: each byte of the UTF-8 outside the always-safe set and `safe` as `%XX`.
#[must_use]
pub fn quote(text: &str, safe: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for b in text.bytes() {
        if b.is_ascii_alphanumeric() || b"_.-~".contains(&b) || safe.as_bytes().contains(&b) {
            out.push(char::from(b));
        } else {
            let _ = write!(out, "%{b:02X}");
        }
    }
    out
}

/// Punycode (RFC 3492) of one label's characters.
#[expect(
    clippy::many_single_char_names,
    reason = "RFC 3492's own names for the encoder's state, as `encodings.punycode` keeps them"
)]
fn punycode(label: &str) -> String {
    let cps: Vec<u32> = label.chars().map(u32::from).collect();
    let mut out: String = label.chars().filter(char::is_ascii).collect();
    let basic = out.len();
    if basic > 0 {
        out.push('-');
    }
    let (mut n, mut delta, mut bias, mut h) = (128u32, 0u32, 72u32, basic);
    let digit = |d: u32| char::from_u32(if d < 26 { d + 97 } else { d + 22 }).unwrap_or('a');
    while h < cps.len() {
        let m = cps.iter().copied().filter(|&c| c >= n).min().unwrap_or(n);
        delta = delta.wrapping_add((m - n).wrapping_mul(u32::try_from(h + 1).unwrap_or(u32::MAX)));
        n = m;
        for &c in &cps {
            if c < n {
                delta = delta.wrapping_add(1);
            }
            if c == n {
                let mut q = delta;
                let mut k = 36;
                loop {
                    let t = if k <= bias {
                        1
                    } else if k >= bias + 26 {
                        26
                    } else {
                        k - bias
                    };
                    if q < t {
                        break;
                    }
                    out.push(digit(t + (q - t) % (36 - t)));
                    q = (q - t) / (36 - t);
                    k += 36;
                }
                out.push(digit(q));
                let first = h == basic;
                let mut d = if first { delta / 700 } else { delta / 2 };
                d += d / u32::try_from(h + 1).unwrap_or(1);
                let mut k = 0;
                while d > 455 {
                    d /= 35;
                    k += 36;
                }
                bias = k + 36 * d / (d + 38);
                delta = 0;
                h += 1;
            }
        }
        delta += 1;
        n += 1;
    }
    out
}

/// `netloc.encode("idna")`: an ASCII netloc as it is, each label checked; another label nameprepped (folded and NFKC) and punycoded.
///
/// # Errors
/// An empty label before the last, or one of 64 characters or more (Python's `UnicodeError`).
pub fn idna(netloc: &str) -> Result<String, String> {
    let labels: Vec<&str> = netloc
        .split(['.', '\u{3002}', '\u{ff0e}', '\u{ff61}'])
        .collect();
    let mut out = Vec::new();
    for (i, label) in labels.iter().enumerate() {
        let encoded = if label.is_ascii() {
            (*label).to_owned()
        } else {
            let prepped: String = crate::pyre::casefold(label).nfkc().collect();
            if prepped.is_ascii() {
                prepped
            } else {
                format!("xn--{}", punycode(&prepped))
            }
        };
        if (encoded.is_empty() && i + 1 < labels.len()) || encoded.len() >= 64 {
            return Err("label empty or too long".to_owned());
        }
        out.push(encoded);
    }
    Ok(out.join("."))
}

/// `quoted_url`: `url` with a non-ASCII path or query percent-encoded and its host in IDNA, the fragment dropped.
///
/// # Errors
/// What `urlsplit` or the IDNA encoding refused.
pub fn quoted_url(url: &str) -> Result<String, String> {
    let [scheme, netloc, path, query, _] = urlsplit(url)?;
    let netloc = if netloc.is_empty() {
        netloc
    } else {
        idna(&netloc).map_err(|e| format!("UnicodeEncodeError: {e}"))?
    };
    let path = quote(&path, "/%:@!$&'()*+,;=~-._");
    let query = quote(&query, "=&%:@!$'()*+,;/?~-._");
    // `urlunsplit` keeps an empty netloc for a scheme that uses one and a path that is empty or absolute
    let uses_netloc = [
        "",
        "ftp",
        "http",
        "gopher",
        "nntp",
        "telnet",
        "imap",
        "wais",
        "file",
        "mms",
        "https",
        "shttp",
        "snews",
        "prospero",
        "rtsp",
        "rtsps",
        "rtspu",
        "rsync",
        "svn",
        "svn+ssh",
        "sftp",
        "nfs",
        "git",
        "git+ssh",
        "ws",
        "wss",
        "itms-services",
    ];
    let kept = !netloc.is_empty()
        || (!scheme.is_empty()
            && uses_netloc.contains(&scheme.as_str())
            && (path.is_empty() || path.starts_with('/')));
    // `urlunsplit` puts a `/` between a netloc and a relative path; split from a URL here, the path after a netloc is empty or starts
    // with one, so it never has to
    let mut out = if kept {
        format!("//{netloc}{path}")
    } else if path.starts_with("//") {
        format!("//{path}")
    } else {
        path
    };
    if !scheme.is_empty() {
        out = format!("{scheme}:{out}");
    }
    if !query.is_empty() {
        out = format!("{out}?{query}");
    }
    Ok(out)
}

/// `is_pdf`: by its type, or a path ending in `.pdf` or `/_pdf`.
#[must_use]
pub fn is_pdf(url: &str, content_type: &str) -> bool {
    let path = urlsplit(url)
        .map(|p| p[2].to_lowercase())
        .unwrap_or_default();
    content_type.to_lowercase().contains("pdf")
        || crate::has_ext(&path, "pdf")
        || path.ends_with("/_pdf")
}

/// `Pages.name_for`: an offline copy's file name, the URL's hash.
#[must_use]
pub fn name_for(url: &str) -> String {
    let hex = l7r_shared::sha256::hex(url.as_bytes());
    format!("{}.html", &hex[..16])
}

/// An answer from the network: the last response's content type and charset, and its body.
#[derive(Debug)]
pub struct Response {
    pub content_type: String,
    pub charset: String,
    pub body: Vec<u8>,
}

/// The one seam to the network: fetch `url` (already quoted), its PDF body left unread where the type says PDF.
pub trait Transport {
    /// # Errors
    /// What the Python's `urlopen` raised, as `<kind>: <words>`.
    fn open(&mut self, url: &str) -> Result<Response, String>;
}

/// `email.message`'s `get_content_charset` of a `Content-Type` value: the `charset` parameter, unquoted and lower-cased.
#[must_use]
pub fn charset_of(content_type: &str) -> String {
    content_type
        .split(';')
        .skip(1)
        .filter_map(|p| p.split_once('='))
        .find(|(k, _)| strip(k).eq_ignore_ascii_case("charset"))
        .map(|(_, v)| strip(v).trim_matches('"').to_lowercase())
        .unwrap_or_default()
}

pub const TIMEOUT: u32 = 20;
pub const UA: &str = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0";

/// The real transport: `curl`, asked to behave as `urlopen` did (`program` the command run, the tests' seam).
pub struct Curl {
    pub program: String,
}

impl Default for Curl {
    fn default() -> Self {
        Self {
            program: "curl".to_owned(),
        }
    }
}

/// The last status line's code and reason among `headers` (each response of a redirect chain writes its own block).
#[must_use]
pub fn last_status(headers: &str) -> (u32, String, String) {
    let (mut code, mut reason, mut ctype) = (0, String::new(), String::new());
    for line in headers.lines() {
        let line = line.trim_end_matches('\r');
        if let Some(rest) = line.strip_prefix("HTTP/") {
            let mut parts = rest.splitn(3, ' ');
            parts.next();
            code = parts.next().and_then(|c| c.parse().ok()).unwrap_or(0);
            strip(parts.next().unwrap_or("")).clone_into(&mut reason);
            ctype.clear();
        } else if let Some((k, v)) = line.split_once(':') {
            if k.eq_ignore_ascii_case("content-type") {
                strip(v).clone_into(&mut ctype);
            }
        }
    }
    (code, reason, ctype)
}

impl Transport for Curl {
    fn open(&mut self, url: &str) -> Result<Response, String> {
        let dir = l7r_shared::tempdir::TempDir::new("quote-verbatim-fetch");
        let (head, body) = (dir.join("head"), dir.join("body"));
        let timeout = TIMEOUT.to_string();
        let done = Command::new(&self.program)
            .args([
                "-sS",
                "-g",
                "--http1.1",
                "-L",
                "--max-redirs",
                "10",
                "--connect-timeout",
                &timeout,
            ])
            .args(["--speed-limit", "1", "--speed-time", &timeout, "-A", UA])
            .args(["-H", "Accept-Language: en,ja,zh,ko", "-D"])
            .arg(&head)
            .arg("-o")
            .arg(&body)
            .arg("--")
            .arg(url)
            .output()
            .map_err(|e| format!("OSError: {e}"))?;
        let headers =
            String::from_utf8_lossy(&std::fs::read(&head).unwrap_or_default()).into_owned();
        // TOO MANY REDIRECTS (curl's 47): `urlopen`'s own refusal, named by the last redirect's status line - it allows ten, as curl is
        // told to, and refuses a URL visited a fifth time sooner, with the same words
        if done.status.code() == Some(47) {
            let (code, reason, _) = last_status(&headers);
            return Err(format!("HTTPError: HTTP Error {code}: The HTTP server returned a redirect error that would lead to an infinite loop.\nThe last 30x error message was:\n{reason}"));
        }
        if !done.status.success() {
            let said = String::from_utf8_lossy(&done.stderr);
            return Err(format!(
                "URLError: <urlopen error {}>",
                strip(said.trim_start_matches("curl: "))
            ));
        }
        let (code, reason, ctype) = last_status(&headers);
        if !(200..300).contains(&code) {
            return Err(format!("HTTPError: HTTP Error {code}: {reason}"));
        }
        let body = std::fs::read(&body).unwrap_or_default();
        Ok(Response {
            charset: charset_of(&ctype),
            content_type: ctype,
            body,
        })
    }
}

/// `Pages`: each URL fetched once, each host at most once after it refuses; `offline` reads saved pages by URL hash.
pub struct Pages {
    pub offline: Option<PathBuf>,
    pub transport: Box<dyn Transport>,
    seen: HashMap<String, Got>,
    /// The hosts that refused this run, in the order they did.
    pub refused: Vec<(String, String)>,
}

impl Pages {
    #[must_use]
    pub fn new(offline: Option<&Path>, transport: Box<dyn Transport>) -> Self {
        Self {
            offline: offline.map(Path::to_path_buf),
            transport,
            seen: HashMap::new(),
            refused: Vec::new(),
        }
    }

    /// `get`: the page, fetched the first time it is asked for.
    ///
    /// # Errors
    /// A URL `urlsplit` refuses (Python's `ValueError`, which the Python's run did not catch).
    pub fn get(&mut self, url: &str) -> Result<Got, String> {
        if let Some(got) = self.seen.get(url) {
            return Ok(got.clone());
        }
        let got = self.fetch(url)?;
        self.seen.insert(url.to_owned(), got.clone());
        Ok(got)
    }

    fn refusal(&self, host: &str) -> Option<&String> {
        self.refused.iter().find(|(h, _)| h == host).map(|(_, w)| w)
    }

    fn fetch(&mut self, url: &str) -> Result<Got, String> {
        let host = urlsplit(url)?[1].clone();
        let low = url.to_lowercase();
        if !(low.starts_with("http://") || low.starts_with("https://")) {
            return Ok(Got::state(
                "OWN",
                "a link into this project, not a public page",
            ));
        }
        let (raw, declared, ctype) = if let Some(dir) = &self.offline {
            if is_pdf(url, "") {
                return Ok(Got::state(
                    "NOT-CHECKED",
                    "a PDF - no text layer can be read here",
                ));
            }
            let Ok(raw) = std::fs::read(dir.join(name_for(url))) else {
                return Ok(Got::state("UNFETCHABLE", "no offline copy"));
            };
            (raw, String::new(), "text/html".to_owned())
        } else {
            if let Some(why) = self.refusal(&host) {
                return Ok(Got::state(
                    "UNFETCHABLE",
                    &format!("{host} already refused this run: {why}"),
                ));
            }
            match quoted_url(url).and_then(|q| self.transport.open(&q)) {
                Ok(r) => (r.body, r.charset, r.content_type),
                Err(e) => {
                    let why: String = e.chars().take(160).collect();
                    self.refused.push((host, why.clone()));
                    return Ok(Got::state("UNFETCHABLE", &why));
                }
            }
        };
        if is_pdf(url, &ctype) {
            let mut got = Got::state("NOT-CHECKED", "a PDF - no text layer can be read here");
            got.live = true;
            return Ok(got);
        }
        Ok(match decode(&raw, &declared) {
            Some(text) => Got::fetched(visible_text(&text)),
            None => Got::state(
                "NOT-CHECKED",
                "the page would not decode in any charset tried",
            ),
        })
    }
}

#[cfg(test)]
mod tests;
