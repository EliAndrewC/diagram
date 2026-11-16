//! A plain request in the browser's context: what Playwright's `context.request.get` did for `archive.py` (feature 449 T146). Playwright
//! sent it from its own HTTP client, not from the page, with the context's user agent and cookies, and stored the cookies the response
//! set back into the context, so a page rendered after it carried them (observed 2026-11-16: `Storage.getCookies` before the request,
//! `Storage.setCookies` after, in Playwright's protocol log). Here `curl` is that client, run as an external program as the gate's
//! `research::verbatim::fetch` runs it (`ask:449-T80-order`: pdftotext and curl stay external programs), its cookie jar filled from the
//! context before and read back into it after.
//!
//! A failure reads as Playwright's did (`APIRequestContext.get: <why>`), Node's words for the common ones - `connect ECONNREFUSED`,
//! `getaddrinfo ENOTFOUND`, the timeout, the redirect cap - and curl's own words for the rest (`ask:449-T066-json-message`: a library's
//! own error text inside the fixed words).

use std::net::ToSocketAddrs;
use std::path::Path;
use std::process::Command;
use std::time::Duration;

use serde_json::{json, Value};

use crate::page::Browser;
use crate::url;

/// What came back.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Got {
    pub status: u16,
    pub url: String,
    pub content_type: String,
}

/// A request's settings.
pub struct Ask<'a> {
    pub url: &'a str,
    pub headers: &'a [(String, String)],
    pub timeout: Duration,
    pub max_redirects: u32,
    pub user_agent: &'a str,
    /// The client run (`curl`; a test names one that is not there).
    pub program: &'a str,
}

/// One cookie as a Netscape jar line (curl's `-b` file).
fn jar_line(c: &Value) -> String {
    let text = |k: &str| c.get(k).and_then(Value::as_str).unwrap_or_default();
    let flag = |b: bool| if b { "TRUE" } else { "FALSE" };
    let domain = text("domain");
    #[expect(
        clippy::cast_possible_truncation,
        reason = "a cookie's expiry in whole seconds, as a jar writes it"
    )]
    let expires = c
        .get("expires")
        .and_then(Value::as_f64)
        .filter(|e| *e > 0.0)
        .map_or(0, |e| e as i64);
    let http_only = c.get("httpOnly").and_then(Value::as_bool).unwrap_or(false);
    format!(
        "{}{domain}\t{}\t{}\t{}\t{expires}\t{}\t{}\n",
        if http_only { "#HttpOnly_" } else { "" },
        flag(domain.starts_with('.')),
        text("path"),
        flag(c.get("secure").and_then(Value::as_bool).unwrap_or(false)),
        text("name"),
        text("value"),
    )
}

/// The cookies of a Netscape jar, as `Storage.setCookies` takes them - `sameSite` Lax, as Playwright stored a response's cookie that
/// named none.
fn jar_cookies(jar: &str) -> Vec<Value> {
    let mut out = Vec::new();
    for line in jar.lines() {
        let (http_only, line) = match line.strip_prefix("#HttpOnly_") {
            Some(rest) => (true, rest),
            None if line.starts_with('#') => continue,
            None => (false, line),
        };
        let f: Vec<&str> = line.split('\t').collect();
        if f.len() < 7 {
            continue;
        }
        let expires: f64 = f[4].parse().unwrap_or(0.0);
        out.push(
            json!({"name": f[5], "value": f[6], "domain": f[0], "path": f[2],
                        "expires": if expires > 0.0 { expires } else { -1.0 },
                        "httpOnly": http_only, "secure": f[3] == "TRUE", "sameSite": "Lax"}),
        );
    }
    out
}

/// The cookie identity a jar keeps: domain, path and name.
fn identity(c: &Value) -> (String, String, String) {
    let text = |k: &str| {
        c.get(k)
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_owned()
    };
    (text("domain"), text("path"), text("name"))
}

/// How a host resolves: its first address, or the resolver's own words for why not (`getaddrinfo` through the standard library).
pub type Resolve = dyn Fn(&str, u16) -> Result<String, String>;

/// The system resolver.
fn system_resolve(host: &str, port: u16) -> Result<String, String> {
    let mut found = (host, port).to_socket_addrs().map_err(|e| e.to_string())?;
    Ok(found
        .next()
        .map_or_else(String::new, |a| a.ip().to_string()))
}

/// Node's words for a curl failure, after `APIRequestContext.get: `.
fn why(
    code: Option<i32>,
    stderr: &str,
    parsed: &url::Url,
    timeout: Duration,
    resolve: &Resolve,
) -> String {
    let port = parsed
        .port
        .unwrap_or(if parsed.scheme == "http" { 80 } else { 443 });
    match code {
        // Node named the resolver's own answer: EAI_AGAIN where no name server answered (a host with no network), ENOTFOUND where the
        // name does not exist; asked again here, as `getaddrinfo` is what both read
        Some(6) => {
            let code = match resolve(&parsed.host, port) {
                Err(e) if e.contains("Temporary failure") => "EAI_AGAIN",
                _ => "ENOTFOUND",
            };
            format!("getaddrinfo {code} {}", parsed.host)
        }
        Some(7) => {
            let ip = resolve(&parsed.host, port).unwrap_or_else(|_| parsed.host.clone());
            format!("connect ECONNREFUSED {ip}:{port}")
        }
        Some(28) => format!("Timeout {}ms exceeded.", timeout.as_millis()),
        Some(47) => "Max redirect count exceeded".to_owned(),
        Some(52) => "socket hang up".to_owned(),
        Some(56) => "read ECONNRESET".to_owned(),
        _ => {
            let line = stderr.lines().next().unwrap_or_default();
            let line = line.strip_prefix("curl: ").unwrap_or(line);
            match line.split_once(") ") {
                Some((head, rest)) if head.starts_with('(') => rest.to_owned(),
                _ => line.to_owned(),
            }
        }
    }
}

/// The request: its body written to `out`, the context's cookies sent and the response's stored.
///
/// # Errors
/// `APIRequestContext.get: <why>` where no response came; a protocol failure of the cookie store.
pub fn get(browser: &mut Browser, ask: &Ask<'_>, out: &Path) -> Result<Got, String> {
    let failed = |w: String| format!("APIRequestContext.get: {w}");
    let parsed = url::parse(ask.url).map_err(failed)?;
    let before = browser.cookies()?;
    let jar = out.with_extension("jar");
    let jar_text: String = before.iter().map(jar_line).collect();
    std::fs::write(&jar, format!("# Netscape HTTP Cookie File\n{jar_text}"))
        .map_err(|e| format!("{}: {e}", jar.display()))?;
    let mut cmd = Command::new(ask.program);
    cmd.args([
        "-sS",
        "-k",
        "--compressed",
        "-L",
        "--proto",
        "=http,https",
        "--proto-redir",
        "=http,https",
    ])
    .arg("--max-redirs")
    .arg(ask.max_redirects.to_string())
    .arg("--max-time")
    .arg(format!("{}", ask.timeout.as_secs_f64()))
    .arg("-A")
    .arg(ask.user_agent)
    .args(["-H", "Accept-Encoding: gzip,deflate,br"]);
    for (k, v) in ask.headers {
        cmd.arg("-H").arg(format!("{k}: {v}"));
    }
    let done = cmd
        .arg("-b")
        .arg(&jar)
        .arg("-c")
        .arg(&jar)
        .arg("-o")
        .arg(out)
        .args([
            "-w",
            "%{http_code}\\n%{url_effective}\\n%{content_type}\\n%{num_redirects}",
        ])
        .arg("--")
        .arg(&parsed.target)
        .output()
        .map_err(|e| failed(format!("curl: {e}")))?;
    let after = std::fs::read_to_string(&jar).unwrap_or_default();
    let _ = std::fs::remove_file(&jar);
    let now = jar_cookies(&after);
    let changed: Vec<Value> = now
        .iter()
        .filter(|c| !before.contains(c))
        .cloned()
        .collect();
    let gone: Vec<Value> = before
        .iter()
        .filter(|c| !now.iter().any(|n| identity(n) == identity(c)))
        .map(|c| {
            let mut dead = c.clone();
            dead["expires"] = json!(1);
            dead
        })
        .collect();
    browser.set_cookies(&[changed, gone].concat())?;
    if !done.status.success() {
        let _ = std::fs::remove_file(out);
        let stderr = String::from_utf8_lossy(&done.stderr);
        return Err(failed(why(
            done.status.code(),
            &stderr,
            &parsed,
            ask.timeout,
            &system_resolve,
        )));
    }
    let said = String::from_utf8_lossy(&done.stdout).into_owned();
    let mut lines = said.split('\n');
    let mut next = || lines.next().unwrap_or_default().to_owned();
    let status: u16 = next().parse().unwrap_or(0);
    let effective = next();
    let content_type = next();
    let redirects: u32 = next().parse().unwrap_or(0);
    // no redirect: the URL as asked, its fragment kept, as `response.url` reported it; else where the redirects ended, read as Node
    // read it
    let final_url = if redirects == 0 {
        parsed.href
    } else {
        url::parse(&effective).map_or(effective, |u| u.href)
    };
    Ok(Got {
        status,
        url: final_url,
        content_type,
    })
}

#[cfg(test)]
mod tests;
