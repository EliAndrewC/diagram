//! The assert lines a format pass makes that no passing test runs (feature 451 T114).
//!
//! WHY: rustfmt (no `rustfmt.toml`: `max_width` 100, `fn_call_width` 60) splits an `assert!` or `assert_eq!` too long for one line
//! into one argument a line, so its message stands on a line of its own - a line that runs only when the assert fails, which the
//! coverage floor names. T108's builder ran lint, tests and cover green, then `make format`, and its landing's cover refused the lines
//! after 274 s (2026-11-21); 70 of the 191 refused lines whose text feature 451's transcripts show were such a message (measured
//! 2026-11-21, T114's plan section). `make format` now names each one it made, with the rewrite, where the format pass writes it.
//!
//! WHICH SHAPES (measured 2026-11-21, a fixture crate under `cargo llvm-cov`, toolchain 1.87.0, T114's plan section): a message
//! argument starting on a line no earlier argument reaches is a line no passing test runs - an `assert_eq!`'s or `assert_ne!`'s
//! format string always, an `assert!`'s unless it is a bare `"{}"`, and a format argument that is not a place (`x.len()`; `r.stderr`
//! is a place, and runs). A message sharing a line with the condition runs. Not counted: an item under `#[cfg(feature = ...)]`, which
//! the coverage build compiles out, a file under a `tests/` directory, which the report leaves out, and the `debug_` forms, not
//! measured. A closure no test calls is named on one line or several, so it is no format pass's (the same fixture) and not here.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use super::{cargo, crates, rust_sources, Ran, World};

/// One message no passing test runs: its line, its macro and its first line's words.
#[derive(Debug, PartialEq, Eq)]
pub(super) struct Hit {
    pub(super) line: usize,
    pub(super) mac: &'static str,
    pub(super) text: String,
}

/// The macros and the index of each one's first message argument.
const MACROS: [(&str, usize); 3] = [("assert_eq!(", 2), ("assert_ne!(", 2), ("assert!(", 1)];

/// The fix, printed with every listing and pinned by a test.
pub(super) const FIX: &str = "bind the values to locals first so the assert fits one line (`let got = f(x);` then `assert_eq!(got, want, \"{x:?}\");`, as 451 T108 did)";

/// `text` with every comment and the inside of every string and character literal blanked to spaces, byte for byte, newlines kept.
fn masked(text: &str) -> Vec<u8> {
    let mut b = text.as_bytes().to_vec();
    let mut i = 0;
    while i < b.len() {
        let from = i;
        if b[i..].starts_with(b"//") {
            while i < b.len() && b[i] != b'\n' {
                i += 1;
            }
        } else if b[i..].starts_with(b"/*") {
            i = text[i..].find("*/").map_or(b.len(), |e| i + e + 2);
        } else if b[i] == b'"'
            || (b[i] == b'r' && b[i + 1..].iter().find(|c| **c != b'#') == Some(&b'"'))
        {
            i = string_end(&b, i);
            blank(&mut b, from + 1, i.saturating_sub(1));
            continue;
        } else if b[i] == b'\'' {
            i = char_end(text, i);
            blank(&mut b, from + 1, i.saturating_sub(1));
            continue;
        } else {
            i += 1;
            continue;
        }
        blank(&mut b, from, i);
    }
    b
}

fn blank(b: &mut [u8], from: usize, to: usize) {
    for c in b.iter_mut().take(to).skip(from) {
        if *c != b'\n' {
            *c = b' ';
        }
    }
}

/// The index after a string literal opening at `i`: `"..."` with its escapes, or `r"..."` and `r#"..."#`.
fn string_end(b: &[u8], i: usize) -> usize {
    if b[i] == b'r' {
        let hashes = b[i + 1..].iter().take_while(|c| **c == b'#').count();
        let body = i + 2 + hashes;
        let closes = |p: usize| {
            b[p] == b'"'
                && b[p + 1..]
                    .iter()
                    .take(hashes)
                    .filter(|c| **c == b'#')
                    .count()
                    == hashes
        };
        return (body..b.len())
            .find(|p| closes(*p))
            .map_or(b.len(), |p| p + 1 + hashes);
    }
    let mut j = i + 1;
    while j < b.len() && b[j] != b'"' {
        j += if b[j] == b'\\' { 2 } else { 1 };
    }
    (j + 1).min(b.len())
}

/// The index after a character literal opening at `i`, or `i + 1` where the quote opens a lifetime.
fn char_end(text: &str, i: usize) -> usize {
    let rest = &text[i + 1..];
    if rest.starts_with('\\') {
        return rest
            .get(2..)
            .and_then(|r| r.find('\''))
            .map_or(text.len(), |e| i + e + 4);
    }
    match rest.chars().next() {
        Some(c) if rest[c.len_utf8()..].starts_with('\'') => i + c.len_utf8() + 2,
        _ => i + 1,
    }
}

/// The byte ranges of the items under `#[cfg(feature = ...)]`: the attribute to its item's closing brace.
fn compiled_out(m: &[u8]) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    for at in m
        .windows(13)
        .enumerate()
        .filter(|(_, w)| *w == b"#[cfg(feature")
        .map(|(at, _)| at)
    {
        let Some(open) = m[at..]
            .iter()
            .position(|c| matches!(c, b'{' | b';'))
            .map(|o| at + o)
        else {
            break;
        };
        if m[open] == b'{' {
            out.push((at, close_of(m, open)));
        }
    }
    out
}

/// The index of the bracket closing the one at `open`.
fn close_of(m: &[u8], open: usize) -> usize {
    let mut depth = 0usize;
    for (j, c) in m.iter().enumerate().skip(open) {
        match c {
            b'(' | b'[' | b'{' => depth += 1,
            b')' | b']' | b'}' => {
                depth -= 1;
                if depth == 0 {
                    return j;
                }
            }
            _ => {}
        }
    }
    m.len()
}

/// The top-level arguments of the call whose `(` is at `open`, each trimmed, as byte ranges.
fn arguments(m: &[u8], open: usize) -> Vec<(usize, usize)> {
    let end = close_of(m, open);
    let (mut out, mut depth, mut start) = (Vec::new(), 0usize, open + 1);
    for (j, c) in m.iter().enumerate().take(end + 1).skip(open + 1) {
        match c {
            b'(' | b'[' | b'{' => depth += 1,
            b')' | b']' | b'}' if depth > 0 => depth -= 1,
            b',' | b')' if depth == 0 => {
                let lead = m[start..j]
                    .iter()
                    .take_while(|c| c.is_ascii_whitespace())
                    .count();
                let tail = m[start..j]
                    .iter()
                    .rev()
                    .take_while(|c| c.is_ascii_whitespace())
                    .count();
                if start + lead < j - tail {
                    out.push((start + lead, j - tail));
                }
                start = j + 1;
            }
            _ => {}
        }
    }
    out
}

/// A place: a name and its fields (`r.stderr`, `pair.0`), whose formatting the coverage run counts with the condition's line.
fn is_place(arg: &str) -> bool {
    arg.split('.').all(|p| {
        p.bytes()
            .next()
            .is_some_and(|c| c.is_ascii_alphanumeric() || c == b'_')
            && p.bytes().all(|c| c.is_ascii_alphanumeric() || c == b'_')
    })
}

/// Every assert message in `text` that no passing test runs.
pub(super) fn scan(text: &str) -> Vec<Hit> {
    let m = masked(text);
    let out_ranges = compiled_out(&m);
    // a line's number is the count of the pieces the newlines before it cut
    let line = |at: usize| text.as_bytes()[..at].split(|c| *c == b'\n').count();
    let mut hits: Vec<Hit> = Vec::new();
    for at in 0..m.len() {
        let after_word = at == 0 || !(m[at - 1].is_ascii_alphanumeric() || m[at - 1] == b'_');
        let Some(&(mac, first)) = MACROS
            .iter()
            .find(|(name, _)| after_word && m[at..].starts_with(name.as_bytes()))
        else {
            continue;
        };
        if out_ranges.iter().any(|(s, e)| (*s..=*e).contains(&at)) {
            continue;
        }
        let args = arguments(&m, at + mac.len() - 1);
        let Some(before) = args.get(first - 1) else {
            continue;
        };
        let reach = line(before.1);
        for (k, (s, e)) in args.iter().enumerate().skip(first) {
            let words = &text[*s..*e];
            let runs = if k == first {
                mac == "assert!(" && words == "\"{}\""
            } else {
                is_place(words)
            };
            let at_line = line(*s);
            if at_line > reach && !runs && hits.last().is_none_or(|h| h.line != at_line) {
                hits.push(Hit {
                    line: at_line,
                    mac: &mac[..mac.len() - 2],
                    text: words.lines().next().unwrap_or_default().to_owned(),
                });
            }
        }
    }
    hits
}

/// The hits in `after` that `before` did not hold: those the format pass made, each known by its macro and words.
pub(super) fn created(before: &str, after: &str) -> Vec<Hit> {
    let mut had: BTreeMap<(&'static str, String), usize> = BTreeMap::new();
    for h in scan(before) {
        *had.entry((h.mac, h.text)).or_default() += 1;
    }
    let mut made = Vec::new();
    for h in scan(after) {
        match had.get_mut(&(h.mac, h.text.clone())) {
            Some(n) if *n > 0 => *n -= 1,
            _ => made.push(h),
        }
    }
    made
}

/// Whether the coverage report counts `file` of the crate at `dir`: not under a `tests/` directory of it.
pub(super) fn counted(dir: &Path, file: &Path) -> bool {
    let rel = file.strip_prefix(dir).unwrap_or(file);
    !rel.parent()
        .is_some_and(|p| p.components().any(|c| c.as_os_str() == "tests"))
}

/// The listing of what a format pass made, file by file, with the fix.
pub(super) fn listing(made: &[(String, Vec<Hit>)]) -> String {
    let mut out = String::from("rust-checks: the format pass put an assert's message on a line of its own, a line that runs only when the assert fails, so cover would name it (451 T114):\n");
    for (shown, hits) in made {
        for h in hits {
            let _ = writeln!(out, "  {shown}:{}: {}! message {}", h.line, h.mac, h.text);
        }
    }
    let _ = writeln!(out, "  fix: {FIX}");
    out
}

/// `cargo fmt` over the crate at `manifest`, and what it made: red, naming each line, where it left a message on a line of its own.
pub(super) fn format_crate(world: &World, manifest: &Path) -> Ran {
    let dir = manifest.parent().unwrap_or(&world.root).to_path_buf();
    let nested: Vec<PathBuf> = crates(&world.root, &[])
        .iter()
        .filter_map(|m| m.parent().map(Path::to_path_buf))
        .filter(|d| *d != dir && d.starts_with(&dir))
        .collect();
    let mut files = Vec::new();
    rust_sources(&dir, &mut files);
    files.retain(|f| counted(&dir, f) && !nested.iter().any(|n| f.starts_with(n)));
    let before: Vec<String> = files
        .iter()
        .map(|f| std::fs::read_to_string(f).unwrap_or_default())
        .collect();
    let mut ran = cargo(world, &["fmt"], manifest, &[]);
    let mut made = Vec::new();
    for (file, old) in files.iter().zip(&before) {
        let new = std::fs::read_to_string(file).unwrap_or_default();
        if *old == new {
            continue;
        }
        let hits = created(old, &new);
        if !hits.is_empty() {
            made.push((
                file.strip_prefix(&world.root)
                    .unwrap_or(file)
                    .display()
                    .to_string(),
                hits,
            ));
        }
    }
    if ran.code == 0 && !made.is_empty() {
        ran.code = 1;
        ran.stdout.push_str(&listing(&made));
    }
    ran
}
