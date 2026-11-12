//! `Path.glob(pattern)` as `CPython` 3.14 matches it, for a task block's `old-code:` globs (feature 449 T131): the pattern split on `/`, a
//! `**` part any number of directories (symlinked ones not entered), any other part matched against each name by `fnmatch`'s rules - `*`,
//! `?`, `[...]` and `[!...]`, a leading dot no different - and a part with none of them taken as a literal name. An empty or absolute
//! pattern raises, as Python's does.

use std::path::{Path, PathBuf};

use fancy_regex::Regex;

/// The body of a `[...]` class as `fnmatch._translate` writes it (`pat[i..j]` between the brackets): an empty range dropped (`z-a`),
/// backslashes and a literal hyphen escaped, `&`, `~` and `|` escaped; `None` for a class that matches nothing.
fn class_body(pat: &[char], start: usize, end: usize) -> Option<String> {
    let text = |a: usize, b: usize| pat[a..b].iter().collect::<String>();
    let mut stuff = if pat[start..end].contains(&'-') {
        let mut chunks: Vec<String> = Vec::new();
        let mut i = start;
        let mut k = if pat[start] == '!' {
            start + 2
        } else {
            start + 1
        };
        while let Some(at) = (k..end).find(|&x| pat[x] == '-') {
            chunks.push(text(i, at));
            i = at + 1;
            k = at + 3;
        }
        let chunk = text(i, end);
        if chunk.is_empty() {
            if let Some(last) = chunks.last_mut() {
                last.push('-');
            }
        } else {
            chunks.push(chunk);
        }
        // empty ranges removed: invalid in a regular expression
        let mut k = chunks.len().saturating_sub(1);
        while k > 0 {
            let (before, after) = (chunks[k - 1].chars().last(), chunks[k].chars().next());
            if matches!((before, after), (Some(x), Some(y)) if x > y) {
                let mut joined: String = chunks[k - 1]
                    .chars()
                    .take(chunks[k - 1].chars().count() - 1)
                    .collect();
                joined.extend(chunks[k].chars().skip(1));
                chunks[k - 1] = joined;
                chunks.remove(k);
            }
            k -= 1;
        }
        chunks
            .iter()
            .map(|c| c.replace('\\', "\\\\").replace('-', "\\-"))
            .collect::<Vec<_>>()
            .join("-")
    } else {
        text(start, end).replace('\\', "\\\\")
    };
    for op in ['&', '~', '|'] {
        stuff = stuff.replace(op, &format!("\\{op}"));
    }
    if stuff.is_empty() {
        return None;
    }
    if stuff == "!" {
        return Some(".".to_owned());
    }
    // a `[` inside is literal to Python's `re` and a nested class to this crate's: escaped, the same set
    let body = if let Some(rest) = stuff.strip_prefix('!') {
        format!("^{}", rest.replace('[', "\\["))
    } else if stuff.starts_with('^') {
        format!("\\{}", stuff.replace('[', "\\["))
    } else {
        stuff.replace('[', "\\[")
    };
    Some(format!("[{body}]"))
}

/// `fnmatch.translate` of one part: the name must match whole. A class whose ranges are all empty matches nothing (`(?!)`), as
/// Python's does.
fn part_regex(part: &str) -> Result<Regex, String> {
    let chars: Vec<char> = part.chars().collect();
    let mut out = String::from("(?s)^");
    let mut i = 0;
    while i < chars.len() {
        let c = chars[i];
        i += 1;
        match c {
            '*' => out.push_str(".*"),
            '?' => out.push('.'),
            '[' => {
                let mut j = i;
                if j < chars.len() && chars[j] == '!' {
                    j += 1;
                }
                if j < chars.len() && chars[j] == ']' {
                    j += 1;
                }
                while j < chars.len() && chars[j] != ']' {
                    j += 1;
                }
                if j >= chars.len() {
                    out.push_str("\\[");
                } else {
                    out.push_str(&class_body(&chars, i, j).unwrap_or_else(|| "(?!)".to_owned()));
                    i = j + 1;
                }
            }
            c => out.push_str(&fancy_regex::escape(&c.to_string())),
        }
    }
    out.push('$');
    Regex::new(&out).map_err(|e| format!("re.error: {e}"))
}

fn is_magic(part: &str) -> bool {
    part.contains(['*', '?', '['])
}

/// The directory's entries, its names in no particular order.
fn entries(dir: &Path) -> Vec<(String, PathBuf, bool)> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| {
            let is_dir = e.file_type().is_ok_and(|t| t.is_dir());
            (
                e.file_name().to_string_lossy().into_owned(),
                e.path(),
                is_dir,
            )
        })
        .collect()
}

/// Every directory at or under `dir`, symlinked ones not entered.
fn descend(dir: &Path, out: &mut Vec<PathBuf>) {
    out.push(dir.to_path_buf());
    for (_, path, is_dir) in entries(dir) {
        if is_dir {
            descend(&path, out);
        }
    }
}

fn step(here: Vec<PathBuf>, part: &str, last: bool) -> Result<Vec<PathBuf>, String> {
    let mut next = Vec::new();
    if part == "**" {
        for d in here {
            descend(&d, &mut next);
        }
        if last {
            // a pattern ending in `**` names the files below as well (Python 3.13 on)
            let dirs = next.clone();
            for d in dirs {
                next.extend(entries(&d).into_iter().filter(|e| !e.2).map(|e| e.1));
            }
        }
    } else if !is_magic(part) {
        next.extend(
            here.into_iter()
                .map(|d| d.join(part))
                .filter(|p| p.symlink_metadata().is_ok()),
        );
    } else {
        let pattern = part_regex(part)?;
        for d in here {
            next.extend(
                entries(&d)
                    .into_iter()
                    .filter(|(name, _, is_dir)| {
                        (last || *is_dir || d.join(name).is_dir())
                            && pattern.is_match(name).unwrap_or(false)
                    })
                    .map(|e| e.1),
            );
        }
    }
    Ok(next)
}

/// What `root.glob(pattern)` yields, in no particular order.
///
/// # Errors
/// What Python raises: an empty pattern, or an absolute one.
pub(super) fn glob(root: &Path, pattern: &str) -> Result<Vec<PathBuf>, String> {
    if pattern.is_empty() {
        return Err(format!("ValueError: Unacceptable pattern: {pattern:?}"));
    }
    if pattern.starts_with('/') {
        return Err("NotImplementedError: Non-relative patterns are unsupported".to_owned());
    }
    let parts: Vec<&str> = pattern
        .split('/')
        .filter(|p| !p.is_empty() && *p != ".")
        .collect();
    let mut here = vec![root.to_path_buf()];
    for (i, part) in parts.iter().enumerate() {
        here = step(here, part, i + 1 == parts.len())?;
    }
    // a pattern ending in `/` names directories alone
    if pattern.ends_with('/') {
        here.retain(|p| p.is_dir());
    }
    let mut seen = Vec::new();
    for p in here {
        if !seen.contains(&p) {
            seen.push(p);
        }
    }
    Ok(seen)
}

#[cfg(test)]
mod tests;
