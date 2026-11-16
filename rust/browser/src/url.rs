//! An http(s) URL as Playwright's request client read it (feature 449 T146): parsed and serialized by the WHATWG URL rules Node's
//! `new URL()` follows - the scheme and host lowercased, a default port dropped, an empty path made `/`, dot segments resolved, and
//! the characters each part may not hold percent-encoded - because that form is what the request sent and what `response.url`
//! reported, and `archive.py` wrote that report into a capture's record and its manifest row (`final_url`). Observed 2026-11-16 on
//! Playwright 1.62: `http://WWW.Site-A.test:80/a/../p` became `http://www.site-a.test/p`, a space in the path `%20`, `|` kept and
//! `^` encoded in a path, `'` encoded in a query, a fragment kept (method: the T146 differential's `url_probe.py`).
//!
//! Only what a citation can hold is handled: no IPv4 renumbering, no IPv6 zone, a host's non-ASCII labels lowercased and punycoded
//! without UTS 46's full mapping.

use std::fmt::Write as _;

/// The C0 controls and space, and what WHATWG adds for each part.
fn encode_set(part: Part, b: u8) -> bool {
    if b <= 0x20 || b >= 0x7F {
        return true;
    }
    match part {
        Part::Query => matches!(b, b'"' | b'#' | b'<' | b'>' | b'\''),
        Part::Path => matches!(
            b,
            b'"' | b'#' | b'<' | b'>' | b'?' | b'`' | b'{' | b'}' | b'^'
        ),
        Part::Fragment => matches!(b, b'"' | b'<' | b'>' | b'`'),
        Part::User => matches!(
            b,
            b'"' | b'#'
                | b'<'
                | b'>'
                | b'?'
                | b'`'
                | b'{'
                | b'}'
                | b'/'
                | b':'
                | b';'
                | b'='
                | b'@'
                | b'['
                | b'\\'
                | b']'
                | b'^'
                | b'|'
        ),
    }
}

#[derive(Clone, Copy)]
enum Part {
    User,
    Path,
    Query,
    Fragment,
}

fn encode(text: &str, part: Part) -> String {
    let mut out = String::with_capacity(text.len());
    for &b in text.as_bytes() {
        if encode_set(part, b) {
            let _ = write!(out, "%{b:02X}");
        } else {
            out.push(char::from(b));
        }
    }
    out
}

/// RFC 3492's punycode of one label (the `xn--` prefix added by the caller), in its own words: `code` the code point being placed
/// (RFC's `n`), `placed` how many are placed (`h`), `delta` and `bias` its state.
fn punycode(label: &str) -> String {
    const BASE: u32 = 36;
    // RFC 3492's digits: 0-25 are a-z, 26-35 are 0-9
    let digit = |d: u32| {
        char::from_u32(if d < 26 {
            u32::from(b'a') + d
        } else {
            u32::from(b'0') + d - 26
        })
        .unwrap_or('a')
    };
    let chars: Vec<u32> = label.chars().map(u32::from).collect();
    let mut out: String = label.chars().filter(char::is_ascii).collect();
    let basic = u32::try_from(out.len()).unwrap_or(0);
    if basic > 0 {
        out.push('-');
    }
    let (mut code, mut delta, mut bias, mut placed) = (128u32, 0u32, 72u32, basic);
    let total = u32::try_from(chars.len()).unwrap_or(0);
    while placed < total {
        let next = chars
            .iter()
            .copied()
            .filter(|&c| c >= code)
            .min()
            .unwrap_or(code);
        delta = delta.wrapping_add((next - code).wrapping_mul(placed + 1));
        code = next;
        for &c in &chars {
            if c < code {
                delta = delta.wrapping_add(1);
            }
            if c == code {
                let mut q = delta;
                let mut k = BASE;
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
                    out.push(digit(t + (q - t) % (BASE - t)));
                    q = (q - t) / (BASE - t);
                    k += BASE;
                }
                out.push(digit(q));
                bias = adapt(delta, placed + 1, placed == basic);
                delta = 0;
                placed += 1;
            }
        }
        delta += 1;
        code += 1;
    }
    out
}

/// RFC 3492 section 6.1's bias adaptation.
fn adapt(delta: u32, points: u32, first: bool) -> u32 {
    let mut d = if first { delta / 700 } else { delta / 2 };
    d += d / points;
    let mut k = 0;
    while d > 455 {
        d /= 35;
        k += 36;
    }
    k + (36 * d) / (d + 38)
}

fn host_of(raw: &str) -> String {
    raw.to_lowercase()
        .split('.')
        .map(|label| {
            if label.is_ascii() {
                label.to_owned()
            } else {
                format!("xn--{}", punycode(label))
            }
        })
        .collect::<Vec<_>>()
        .join(".")
}

/// Dot segments resolved, as WHATWG's path state does (`.` and `%2e` alike).
fn resolve_path(path: &str) -> String {
    let mut out: Vec<&str> = Vec::new();
    let segments: Vec<&str> = path.split('/').skip(1).collect();
    let last = segments.len().saturating_sub(1);
    for (i, seg) in segments.iter().enumerate() {
        let lower = seg.to_ascii_lowercase();
        let single = matches!(lower.as_str(), "." | "%2e");
        let double = matches!(lower.as_str(), ".." | ".%2e" | "%2e." | "%2e%2e");
        if double {
            out.pop();
            if i == last {
                out.push("");
            }
        } else if single {
            if i == last {
                out.push("");
            }
        } else {
            out.push(seg);
        }
    }
    format!("/{}", out.join("/"))
}

/// A URL in its parts, serialized.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Url {
    pub scheme: String,
    pub host: String,
    pub port: Option<u16>,
    /// `scheme://[user@]host[:port]path[?query]`, the form a request sends (no fragment).
    pub target: String,
    /// The whole serialization, the fragment included: what `response.url` reported where no redirect happened.
    pub href: String,
}

/// `new URL(text)` for an http(s) URL.
///
/// # Errors
/// Playwright's words for a URL it would not request: another scheme, or no host.
pub fn parse(text: &str) -> Result<Url, String> {
    let trimmed: String = text
        .trim_matches(|c: char| c <= ' ')
        .chars()
        .filter(|c| !matches!(c, '\t' | '\n' | '\r'))
        .collect();
    let Some((scheme, rest)) = trimmed.split_once(':') else {
        return Err(format!("Invalid URL: {text}"));
    };
    let scheme = scheme.to_ascii_lowercase();
    if scheme != "http" && scheme != "https" {
        // Node's own words: Playwright handed a URL of any other scheme to `http.request`, which refuses it so (observed 2026-11-16 for
        // `ftp:`, the T146 differential)
        return Err(format!(
            "Protocol \"{scheme}:\" not supported. Expected \"http:\""
        ));
    }
    let rest = rest.replace('\\', "/");
    let rest = rest.trim_start_matches('/');
    let (rest, fragment) = match rest.split_once('#') {
        Some((r, f)) => (r, Some(f)),
        None => (rest, None),
    };
    let (rest, query) = match rest.split_once('?') {
        Some((r, q)) => (r, Some(q)),
        None => (rest, None),
    };
    let (authority, path) = match rest.find('/') {
        Some(i) => (&rest[..i], &rest[i..]),
        None => (rest, ""),
    };
    let (user, hostport) = match authority.rfind('@') {
        Some(i) => (Some(&authority[..i]), &authority[i + 1..]),
        None => (None, authority),
    };
    let (host, port) = match hostport.rfind(':').filter(|_| !hostport.ends_with(']')) {
        Some(i) => (&hostport[..i], &hostport[i + 1..]),
        None => (hostport, ""),
    };
    if host.is_empty() {
        return Err(format!("Invalid URL: {text}"));
    }
    let port: Option<u16> = if port.is_empty() {
        None
    } else {
        Some(port.parse().map_err(|_| format!("Invalid URL: {text}"))?)
    };
    let default = if scheme == "http" { 80 } else { 443 };
    let port = port.filter(|&p| p != default);
    let host = host_of(host);
    let userinfo = user.map_or_else(String::new, |u| {
        let (name, pass) = match u.split_once(':') {
            Some((n, p)) => (n, Some(p)),
            None => (u, None),
        };
        let pass = pass
            .filter(|p| !p.is_empty())
            .map(|p| encode(p, Part::User));
        let name = encode(name, Part::User);
        match pass {
            Some(p) => format!("{name}:{p}@"),
            None if name.is_empty() => String::new(),
            None => format!("{name}@"),
        }
    });
    let path = resolve_path(&encode(
        if path.is_empty() { "/" } else { path },
        Part::Path,
    ));
    let port_text = port.map_or_else(String::new, |p| format!(":{p}"));
    let query_text = query.map_or_else(String::new, |q| format!("?{}", encode(q, Part::Query)));
    let target = format!("{scheme}://{userinfo}{host}{port_text}{path}{query_text}");
    let href = match fragment {
        Some(f) => format!("{target}#{}", encode(f, Part::Fragment)),
        None => target.clone(),
    };
    Ok(Url {
        scheme,
        host,
        port,
        target,
        href,
    })
}

#[cfg(test)]
mod tests;
