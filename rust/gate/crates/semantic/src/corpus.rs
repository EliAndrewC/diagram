//! What the index holds, shard by shard (feature 449 T138, `semantic_index.py`'s `corpus`): every archived text - its path relative to
//! the archive, its shard its first folder - and every page of the record but its originals - its path relative to the repository, its
//! shard `record-<n>` a hundred questions. In the Python's order: the archive's `sorted(rglob("*.txt"))` (paths compared part by part,
//! hidden files and links to files taken, linked folders not entered), then the record's `sorted(glob("*.html"))`; a shard is a run of
//! files with one name (`itertools.groupby`), so a shard named twice apart would be two runs, as there.

use std::path::{Path, PathBuf};

use crate::{text, Error, Result, INDEX_DIR, QUESTIONS, RECORD_SHARD};

/// One file of the corpus.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct File {
    pub shard: String,
    pub rel: String,
    pub path: PathBuf,
    pub record: bool,
}

fn names(dir: &Path) -> Vec<(String, std::fs::FileType)> {
    let mut out: Vec<(String, std::fs::FileType)> = std::fs::read_dir(dir)
        .map(|rd| {
            rd.flatten()
                .filter_map(|e| {
                    Some((
                        e.file_name().to_string_lossy().into_owned(),
                        e.file_type().ok()?,
                    ))
                })
                .collect()
        })
        .unwrap_or_default();
    out.sort_by(|a, b| a.0.cmp(&b.0));
    out
}

/// Every `*.txt` under `dir`, as parts relative to it (`rglob`: real folders entered, links to folders not).
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "`rglob(\"*.txt\")` is case-sensitive on POSIX, as the Python ran it"
)]
fn rglob_txt(dir: &Path, parts: &mut Vec<String>, out: &mut Vec<Vec<String>>) {
    for (name, kind) in names(&dir.join(parts.join("/"))) {
        parts.push(name.clone());
        if name.ends_with(".txt") {
            out.push(parts.clone());
        }
        if kind.is_dir() {
            rglob_txt(dir, parts, out);
        }
        parts.pop();
    }
}

/// The record shard of a page's name: its number's hundred (`int(name.split("-", 1)[0])` where the name opens with four digits, else 0).
///
/// # Errors
/// A name opening with four digits whose number does not parse (the Python's `int()` raised).
pub fn record_shard(name: &str) -> Result<String> {
    let num = if name.chars().take(4).filter(char::is_ascii_digit).count() == 4 {
        let head = name.split('-').next().unwrap_or_default();
        head.parse::<i64>()
            .map_err(|_| Error(format!("invalid literal for int() with base 10: '{head}'")))?
    } else {
        0
    };
    Ok(format!("record-{:02}", num.div_euclid(RECORD_SHARD)))
}

/// Every file of the corpus, in the Python's order.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "`glob(\"*.html\")` is case-sensitive on POSIX, as the Python ran it"
)]
///
/// # Errors
/// A record page's number does not parse.
pub fn files(archive_dir: &Path, root: &Path) -> Result<Vec<File>> {
    let mut out = Vec::new();
    if archive_dir.is_dir() {
        let mut found = Vec::new();
        rglob_txt(archive_dir, &mut Vec::new(), &mut found);
        found.sort();
        for parts in found {
            if parts.len() < 2 || parts[0] == ".git" || parts[0] == INDEX_DIR {
                continue;
            }
            let rel = parts.join("/");
            out.push(File {
                shard: parts[0].clone(),
                path: archive_dir.join(&rel),
                rel,
                record: false,
            });
        }
    }
    for (name, _) in names(&root.join(QUESTIONS)) {
        if !name.ends_with(".html") || name.ends_with(".originals.html") {
            continue;
        }
        out.push(File {
            shard: record_shard(&name)?,
            rel: format!("{QUESTIONS}/{name}"),
            path: root.join(QUESTIONS).join(&name),
            record: true,
        });
    }
    Ok(out)
}

/// A file's text as the index read it: an archived text as it is, a record page through `strip_html`.
///
/// # Errors
/// It cannot be read.
pub fn text_of(f: &File) -> Result<String> {
    let raw = text::read_lossy(&f.path)?;
    Ok(if f.record {
        text::strip_html(&raw)
    } else {
        raw
    })
}

/// The runs of files sharing a shard, in order (`itertools.groupby`).
#[must_use]
pub fn groups(files: Vec<File>) -> Vec<(String, Vec<File>)> {
    let mut out: Vec<(String, Vec<File>)> = Vec::new();
    for f in files {
        match out.last_mut() {
            Some((shard, run)) if *shard == f.shard => run.push(f),
            _ => out.push((f.shard.clone(), vec![f])),
        }
    }
    out
}

#[cfg(test)]
mod tests;
