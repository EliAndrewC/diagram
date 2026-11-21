//! `make archive-find` (`archive_ops.find`, feature 309 FR-015; ported by feature 449 T147): what the archive already holds - rows by
//! URL or key, and archived texts holding every term - each with its local path; exit 0 with hits, 1 with none, so a session knows to
//! go to the web.

use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::process::Command;

use l7r_shared::attempts::{self, Ask, More};
use l7r_shared::consulted::norm;
use l7r_shared::pyjson::py_str;
use serde_json::Value;

use super::{field, os_error};
use crate::manifest::{gm_table, load_row, research, row_files};
use crate::store::Archive;
use crate::{Error, Result};

/// `"\n".join(attempts.report(root, url=u))`, the attempts on a URL as `make attempts` prints them.
fn tried(root: &Path, url: &str, out: &mut String) -> Result<()> {
    let lines = attempts::report(root, Ask::Url(url))?;
    let _ = writeln!(out, "{}", lines.join("\n").trim_end_matches('\n'));
    Ok(())
}

/// `str(base / rel)`: the path joined and normalized as `pathlib` writes it (repeated and trailing slashes and `.` parts dropped).
fn joined(base: &Path, rel: &str) -> String {
    base.join(rel)
        .components()
        .collect::<PathBuf>()
        .to_string_lossy()
        .into_owned()
}

/// `f"{value:26}"` of a string: padded on the right to 26 characters.
fn pad26(v: &Value) -> Result<String> {
    match v {
        Value::String(s) => Ok(format!("{s:26}")),
        Value::Null => Err(Error::new(
            "TypeError",
            "unsupported format string passed to NoneType.__format__",
        )),
        other => Ok(format!("{:>26}", py_str(other))),
    }
}

fn strings(v: Option<&Value>) -> Vec<String> {
    v.and_then(Value::as_array)
        .map(|a| a.iter().map(py_str).collect())
        .unwrap_or_default()
}

fn rows_hit(
    root: &Path,
    store: &Archive,
    rows: &[Value],
    want: &str,
    key: &str,
    out: &mut String,
) -> Result<usize> {
    let mut hits = 0;
    for row in rows {
        let keys = strings(row.get("keys"));
        // `row["url"]` read only where the Python's `and` reached it: a row with no URL is a refusal only when a URL is asked or it is a hit
        let url_hit = !want.is_empty() && norm(&field(row, "url")?) == want;
        if !(url_hit || (!key.is_empty() && keys.iter().any(|k| k == key))) {
            continue;
        }
        let url = field(row, "url")?;
        hits += 1;
        let local = row
            .get("path")
            .filter(|p| l7r_shared::pyjson::truthy(p))
            .map_or_else(
                || "(no copy)".to_owned(),
                |p| joined(&store.dir, &py_str(p)),
            );
        let outcome = pad26(
            row.get("outcome")
                .ok_or_else(|| Error::new("KeyError", "'outcome'"))?,
        )?;
        let shown = keys.join(", ");
        let _ = writeln!(
            out,
            "{outcome} {url}\n  local: {local}\n  keys: {}",
            if shown.is_empty() { "-" } else { &shown }
        );
        for gm in strings(row.get("gm_copies")) {
            let _ = writeln!(out, "  the GM's copy: {}", joined(&store.dir, &gm));
        }
        if want.is_empty() {
            // feature 312 FR-018: a source found by its key shows what it was tried for, too
            tried(root, &url, out)?;
        }
    }
    Ok(hits)
}

/// `grep -rlIiF` of one word over the archived texts: the files holding it, the git directory's left out.
fn grep(word: &str, dir: &Path) -> Result<Vec<String>> {
    let done = Command::new("grep")
        .args([
            "-rlIiF",
            "--include=text.txt",
            "--include=*.pdf.txt",
            "--include=*.txt",
            "--",
            word,
        ])
        .arg(dir)
        .output()
        .map_err(spawn_failed)?;
    Ok(
        l7r_shared::speckit::splitlines(&String::from_utf8_lossy(&done.stdout))
            .into_iter()
            .filter(|f| !f.contains("/.git/"))
            .map(str::to_owned)
            .collect(),
    )
}

/// grep that would not start, as the Python's `subprocess.run` raised it.
#[expect(
    clippy::needless_pass_by_value,
    reason = "a `map_err` adapter, named so its call stays one line"
)]
pub(crate) fn spawn_failed(e: std::io::Error) -> Error {
    os_error(&e, Path::new("grep"))
}

fn parent(f: &str) -> String {
    Path::new(f)
        .parent()
        .map(|p| {
            p.components()
                .collect::<PathBuf>()
                .to_string_lossy()
                .into_owned()
        })
        .unwrap_or_default()
}

/// The GM's copies of a key the table places, each a hit.
fn gm_hits(root: &Path, store: &Archive, key: &str, out: &mut String) -> Result<usize> {
    let mut hits = 0;
    let table = gm_table(root)?;
    let mut names: Vec<&String> = table.keys().collect();
    names.sort();
    for name in names {
        let entry = &table[name];
        let archived = entry
            .get("archived")
            .filter(|a| l7r_shared::pyjson::truthy(a));
        if let (true, Some(a)) = (
            strings(entry.get("keys")).iter().any(|k| k == key),
            archived,
        ) {
            hits += 1;
            let _ = writeln!(
                out,
                "the GM's copy of {key}: {}",
                joined(&store.dir, &py_str(a))
            );
        }
    }
    Ok(hits)
}

/// The archived texts holding every word, each a hit with its row's URL and what was tried for it; `each` counts the texts holding
/// each word alone.
fn word_hits<'w>(
    root: &Path,
    store: &Archive,
    rows: &[Value],
    words: &[&'w str],
    each: &mut Vec<(&'w str, usize)>,
    out: &mut String,
) -> Result<usize> {
    let mut hits = 0;
    let mut found: Option<Vec<String>> = None;
    for word in words {
        let files = grep(word, &store.dir)?;
        let dirs: std::collections::BTreeSet<String> = files.iter().map(|f| parent(f)).collect();
        match each.iter_mut().find(|(w, _)| w == word) {
            Some((_, n)) => *n = dirs.len(),
            None => each.push((word, dirs.len())),
        }
        found = Some(match found {
            None => files,
            Some(had) => had.into_iter().filter(|f| files.contains(f)).collect(),
        });
    }
    let mut all = found.unwrap_or_default();
    all.sort();
    all.dedup();
    let by_dir: BTreeMap<String, String> = all.into_iter().map(|f| (parent(&f), f)).collect();
    let url_of: Vec<(String, String)> = rows
        .iter()
        .filter(|r| r.get("path").is_some_and(l7r_shared::pyjson::truthy))
        .map(|r| Ok((joined(&store.dir, &field(r, "path")?), field(r, "url")?)))
        .collect::<Result<_>>()?;
    let shown = words.join(" + ");
    for (d, f) in &by_dir {
        hits += 1;
        // the last row of a path, as the Python's dict kept it
        let row_url = url_of
            .iter()
            .rev()
            .find(|(p, _)| p == d)
            .map(|(_, u)| u.clone());
        let _ = write!(out, "text holds {shown}: {f}");
        match row_url {
            Some(u) => {
                let _ = writeln!(out, "\n  url: {u}");
                tried(root, &u, out)?;
            }
            None => out.push('\n'),
        }
    }
    Ok(hits)
}

/// What the archive already holds (FR-015): rows by URL or key, and archived texts holding every term; each with its local path. A URL
/// asked shows what was tried for it first, then records this look on the attempts log (feature 312 FR-017, FR-018). Exit 0 with
/// hits, 1 with none.
///
/// # Errors
/// A row, the table or the attempts log, as the Python raised them.
pub fn find(
    root: &Path,
    store: &Archive,
    url: &str,
    key: &str,
    terms: &str,
    out: &mut String,
) -> Result<i32> {
    let mut hits = 0;
    let rows: Vec<Value> = row_files(root)
        .iter()
        .map(|p| load_row(p))
        .collect::<Result<_>>()?;
    let want = if url.is_empty() {
        String::new()
    } else {
        norm(url)
    };
    if !url.is_empty() {
        tried(root, url, out)?;
        let more = More {
            route: "archive-find",
            ..More::default()
        };
        attempts::add(
            root,
            url,
            "unknown",
            "is it in the archive (make archive-find)",
            "unknown",
            &more,
            &research(root),
        )?;
    }
    hits += rows_hit(root, store, &rows, &want, key, out)?;
    if !key.is_empty() {
        hits += gm_hits(root, store, key, out)?;
    }
    let words: Vec<&str> = terms
        .split('|')
        .map(l7r_shared::py_text::strip)
        .filter(|t| !t.is_empty())
        .collect();
    // texts holding each word alone, by word in the order first asked (a dict: a word asked twice counts once) - the tip when none holds them all
    let mut each: Vec<(&str, usize)> = Vec::new();
    if !words.is_empty() && store.dir.is_dir() {
        hits += word_hits(root, store, &rows, &words, &mut each, out)?;
    }
    if hits == 0 && words.len() > 1 && each.iter().any(|(_, n)| *n > 0) {
        // THE TERMS ARE ALL REQUIRED (`a|b` is a and b, not a or b), and four research passes of feature 376 read "nothing held" as an
        // empty archive and went to the web for texts the archive held under one word alone
        let held: Vec<String> = each.iter().map(|(w, n)| format!("{w} {n}")).collect();
        let most = each
            .iter()
            .fold(None::<&(&str, usize)>, |best, x| match best {
                Some(b) if b.1 >= x.1 => Some(b),
                _ => Some(x),
            });
        let _ = writeln!(
            out,
            "archive: no text holds ALL of {} (TERMS are all required). Texts holding each alone: {} - ask one term at a time: `make \
             archive-find TERMS=\"{}\"`",
            words.join(" + "),
            held.join(", "),
            most.map_or("", |m| m.0)
        );
        return Ok(1);
    }
    if hits == 0 {
        let _ = writeln!(
            out,
            "archive: nothing held - search the web (a page you cite is archived by `make source-outcome OUTCOME=cited:<key>`)"
        );
    }
    Ok(i32::from(hits == 0))
}
