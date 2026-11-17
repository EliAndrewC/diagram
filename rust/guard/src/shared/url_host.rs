//! A URL's host as the record's blocked-domain list reads it: `blocked.host`, `CPython`'s `urllib.parse.urlsplit(u).hostname` with the
//! record's fallback, ported exactly (feature 449 T148, the note T144's plan review owed: S1's `host` neither dropped tabs nor applied
//! NFKC as `urlsplit` does, and live fetch URLs reach it - the blocked-fetch guard's `WebFetch` and `curl` URLs, the sources' page fetch,
//! the archive's fetch and the uncited lane's list, each through [`super::blocked::blocked`]).
//!
//! The steps, each `urlsplit`'s in `CPython` 3.14.4: the URL stripped of Python's whitespace and read as https where it names no scheme
//! (`^[a-z][a-z0-9+.-]*://`, case blind as `re.I` is, so `İ`, `ı`, `ſ` and the Kelvin sign pass as letters); then its leading C0 controls
//! and spaces dropped and every tab, CR and LF removed; the scheme split at the first colon when ASCII letters and scheme characters lead
//! to it; the network location up to the first `/`, `?` or `#`, refused (`ValueError`) for an unmatched bracket, a bracketed host that is
//! not an IPv6 address or an `IPvFuture` one, or characters that NFKC turns into `/?#@:`; the host the part after the last `@`, inside
//! its brackets or before its colon, lower-cased and its dots trimmed. A refused URL's host is the fallback's: the run of characters
//! after `://` up to `/?#:`, lower-cased, dots and brackets trimmed. Each answer is pinned against `CPython`'s own on 3,844 URLs
//! (`url_host/cpython.jsonl`).

use unicode_normalization::UnicodeNormalization as _;

use super::py_text;

/// Python's `str.lower` (which matched `char::to_lowercase` on every code point, the research crate's `pyre` measured) and `strip(chars)`.
fn lower_strip(text: &str, chars: &[char]) -> String {
    text.to_lowercase().trim_matches(chars).to_owned()
}

/// Whether `c` is one Python's `[a-z]` takes under `re.I` on a `str` pattern.
fn letter(c: char) -> bool {
    c.is_ascii_alphabetic() || matches!(c, '\u{130}' | '\u{131}' | '\u{17f}' | '\u{212a}')
}

/// `^[a-z][a-z0-9+.-]*://` with `re.I`: the length of the scheme where the URL opens with one.
fn scheme_prefix(u: &str) -> Option<usize> {
    let mut chars = u.char_indices();
    let (_, first) = chars.next()?;
    if !letter(first) {
        return None;
    }
    for (at, c) in chars {
        if u[at..].starts_with("://") {
            return Some(at);
        }
        if !(letter(c) || c.is_ascii_digit() || matches!(c, '+' | '.' | '-')) {
            return None;
        }
    }
    None
}

/// `urlsplit`'s network location, or its `ValueError`.
fn netloc(u: &str) -> Result<String, ()> {
    let trimmed = u.trim_start_matches(|c: char| c <= ' ');
    let url: String = trimmed
        .chars()
        .filter(|c| !matches!(c, '\t' | '\r' | '\n'))
        .collect();
    let mut rest = url.as_str();
    // the URL holds a colon: its own scheme's, or the `https://` read in front of it
    let i = url.find(':').unwrap_or(0);
    let head = &url[..i];
    if i > 0
        && head.starts_with(|c: char| c.is_ascii_alphabetic())
        && head
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || matches!(c, '+' | '-' | '.'))
    {
        rest = &url[i + 1..];
    }
    let Some(after) = rest.strip_prefix("//") else {
        return Ok(String::new());
    };
    let net = &after[..after.find(['/', '?', '#']).unwrap_or(after.len())];
    let (open, close) = (net.contains('['), net.contains(']'));
    if open != close {
        return Err(());
    }
    if open {
        bracketed_netloc(net)?;
    }
    check_nfkc(net)?;
    Ok(net.to_owned())
}

/// `_check_bracketed_netloc`: no text before the bracket, none after it but a port, and the bracketed host an address.
fn bracketed_netloc(net: &str) -> Result<(), ()> {
    let host_port = net.rsplit_once('@').map_or(net, |(_, h)| h);
    let host = match host_port.split_once('[') {
        Some((before, bracketed)) => {
            if !before.is_empty() {
                return Err(());
            }
            let (host, port) = bracketed.split_once(']').unwrap_or((bracketed, ""));
            if !port.is_empty() && !port.starts_with(':') {
                return Err(());
            }
            host
        }
        None => host_port.split_once(':').map_or(host_port, |(h, _)| h),
    };
    bracketed_host(host)
}

/// `_check_bracketed_host`: an `IPvFuture` address (`v<hex>.<anything>`) or an IPv6 one, never an IPv4 one.
fn bracketed_host(host: &str) -> Result<(), ()> {
    if let Some(rest) = host.strip_prefix('v') {
        let hex = rest.chars().take_while(char::is_ascii_hexdigit).count();
        let tail = &rest[hex..];
        return if hex > 0 && tail.starts_with('.') && tail.len() > 1 {
            Ok(())
        } else {
            Err(())
        };
    }
    ipv6(host)
}

/// `ipaddress.IPv6Address(text)`: a scope id after one `%`, at most 45 characters, three to nine parts, an IPv4 tail, one `::`, hextets
/// of one to four hex digits.
fn ipv6(text: &str) -> Result<(), ()> {
    let addr = match text.split_once('%') {
        Some((_, scope)) if scope.is_empty() || scope.contains('%') => return Err(()),
        Some((addr, _)) => addr,
        None => text,
    };
    if addr.is_empty() || addr.chars().count() > 45 || addr.contains('/') {
        return Err(());
    }
    let mut parts: Vec<String> = addr.splitn(10, ':').map(str::to_owned).collect();
    if parts.len() < 3 {
        return Err(());
    }
    if parts.last().is_some_and(|p| p.contains('.')) {
        let v4 = ipv4(&parts.pop().unwrap_or_default())?;
        parts.push(format!("{:x}", (v4 >> 16) & 0xffff));
        parts.push(format!("{:x}", v4 & 0xffff));
    }
    if parts.len() > 9 {
        return Err(());
    }
    let n = parts.len();
    let mut skip = None;
    for (i, p) in parts.iter().enumerate().take(n - 1).skip(1) {
        if p.is_empty() {
            if skip.is_some() {
                return Err(());
            }
            skip = Some(i);
        }
    }
    let (hi, lo) = if let Some(at) = skip {
        let (mut hi, mut lo) = (at, n - at - 1);
        if parts[0].is_empty() {
            hi -= 1;
            if hi > 0 {
                return Err(());
            }
        }
        if parts[n - 1].is_empty() {
            lo -= 1;
            if lo > 0 {
                return Err(());
            }
        }
        if 8 < hi + lo + 1 {
            return Err(());
        }
        (hi, lo)
    } else {
        if n != 8 || parts[0].is_empty() || parts[n - 1].is_empty() {
            return Err(());
        }
        (n, 0)
    };
    let hextet =
        |p: &String| !p.is_empty() && p.len() <= 4 && p.chars().all(|c| c.is_ascii_hexdigit());
    if parts[..hi].iter().chain(&parts[n - lo..]).all(hextet) {
        Ok(())
    } else {
        Err(())
    }
}

/// `ipaddress.IPv4Address(text)`'s integer: four decimal octets, no leading zero, none past 255.
fn ipv4(text: &str) -> Result<u32, ()> {
    let octets: Vec<&str> = text.split('.').collect();
    if octets.len() != 4 {
        return Err(());
    }
    let mut out = 0u32;
    for o in octets {
        let ok = !o.is_empty()
            && o.len() <= 3
            && o.bytes().all(|b| b.is_ascii_digit())
            && (o == "0" || !o.starts_with('0'));
        if !ok {
            return Err(());
        }
        let value = o.bytes().fold(0u32, |n, b| n * 10 + u32::from(b - b'0'));
        if value > 255 {
            return Err(());
        }
        out = (out << 8) | value;
    }
    Ok(out)
}

/// `_checknetloc`: a network location whose NFKC form gains one of `/?#@:` is refused.
fn check_nfkc(net: &str) -> Result<(), ()> {
    if net.is_ascii() {
        return Ok(());
    }
    let n: String = net
        .chars()
        .filter(|c| !matches!(c, '@' | ':' | '#' | '?'))
        .collect();
    let folded: String = n.nfkc().collect();
    if folded != n && folded.contains(['/', '?', '#', '@', ':']) {
        return Err(());
    }
    Ok(())
}

/// The host of a network location, as `SplitResult.hostname` reads it.
fn hostname(net: &str) -> &str {
    let info = net.rsplit_once('@').map_or(net, |(_, h)| h);
    match info.split_once('[') {
        Some((_, bracketed)) => bracketed.split_once(']').map_or(bracketed, |(h, _)| h),
        None => info.split_once(':').map_or(info, |(h, _)| h),
    }
}

/// The URL's host, lower-cased; a URL written without its scheme is read as https (`blocked.host`).
#[must_use]
pub fn host(url: &str) -> String {
    let stripped = py_text::strip(url);
    let u = if scheme_prefix(stripped).is_some() {
        stripped.to_owned()
    } else {
        format!("https://{stripped}")
    };
    if let Ok(net) = netloc(&u) {
        return lower_strip(hostname(&net), &['.']);
    }
    let at = scheme_prefix(&u).map_or(0, |s| s + 3);
    let run = &u[at..];
    let run = &run[..run.find(['/', '?', '#', ':']).unwrap_or(run.len())];
    lower_strip(run, &['.', '[', ']'])
}

#[cfg(test)]
mod tests;
