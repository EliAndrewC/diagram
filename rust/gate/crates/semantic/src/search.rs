//! The combined search of the record and the archive (feature 449 T138, `research_search.py`; feature 447 amendment 3) - the meaning
//! search and the text search in one call, their hits merged by SOURCE, each source printed once.
//!
//! WHY (the GM, 2026-10-30, `specs/447-semantic-index/request.md`): on feature 444's field-size question each search found sources the
//! other missed, so a research pass runs both - "optimizing for finding things that are relevant rather than doing something which is
//! cheaper because it misses actual matches" - and finds what is held locally before it goes to the web. A source is an archive capture
//! (`<xx>/<id>`), a GM copy (`gm-copies/<file>`) or a record page (`record <NNNN>`); the two searches' rankings are fused by reciprocal
//! rank (each list adds 1/(60 + rank), the usual constant), so a source both find rises. Under a KEY the sources already printed are
//! remembered (`<archive home>/search-seen/<key>.json`) and a later call prints only new ones: nothing is read twice.

use std::collections::{BTreeSet, HashMap};
use std::path::{Path, PathBuf};
use std::process::Command;

use serde_json::Value;

use crate::embed::Embed;
use crate::index::{must_read, shard_paths, text_at};
use crate::text::{first, slice, squeeze};
use crate::{head, rank, Error, Result, INDEX_DIR, QUESTIONS};

/// Archive sources a call prints: a knob, so a broad term set no longer prints a hundred files' download histories (FR-A3-2).
pub const LIMIT: i64 = 15;
/// Record pages a call prints, apart: the record's pages, in English and in its own words, outrank every archive source on the meaning
/// search (measured on the field-size question 2026-10-30: the first eight were all record pages).
pub const RECORD_LIMIT: i64 = 5;
/// Sources each meaning search contributes to the fusion.
pub const PER_QUESTION: usize = 30;
/// The reciprocal-rank constant: rank 1 scores 1/61, rank 30 scores 1/90.
pub const FUSE: f64 = 60.0;
pub const SEEN_DIR: &str = "search-seen";
/// How long a key remembers what it printed: one question's session of searching, then forgotten.
pub const SEEN_DAYS: u64 = 1;
pub const SNIPPET: usize = 240;
/// Passages a source shows by meaning, and measures it shows: one passage was the wrong one in ten drops (t05-why.md).
pub const PASSAGES: usize = 2;

/// (source, path, start, end).
pub type Hit = (String, String, i64, i64);
/// (path, start, end).
pub type Span = (String, i64, i64);

/// The source a passage's file belongs to.
#[must_use]
pub fn source_of(rel: &str) -> String {
    if rel.starts_with(QUESTIONS) {
        let name = rel.rsplit('/').next().unwrap_or_default();
        return format!("record {}", first(name, 4));
    }
    rel.split('/')
        .filter(|p| !p.is_empty() && *p != ".")
        .take(2)
        .collect::<Vec<_>>()
        .join("/")
}

/// Every shard's vectors, paths and spans, in one array each (`load_index`).
#[derive(Debug, Default)]
pub struct Index {
    pub vecs: Vec<u16>,
    pub dim: usize,
    pub paths: Vec<String>,
    pub spans: Vec<[i64; 2]>,
}

/// # Errors
/// A shard cannot be read.
pub fn load_index(out_dir: &Path) -> Result<Index> {
    let mut ix = Index::default();
    for p in shard_paths(out_dir) {
        let z = must_read(&p)?;
        ix.dim = z.dim;
        ix.vecs.extend(z.vecs);
        ix.paths.extend(z.paths);
        ix.spans.extend(z.spans);
    }
    Ok(ix)
}

/// For each question, its nearest sources, nearest first, each with up to PASSAGES of its nearest passages (a source's second passage
/// listed after its first, the source's rank its first's).
///
/// # Errors
/// The embedder failed.
pub fn meaning(
    ix: &Index,
    questions: &[String],
    embed: &mut dyn Embed,
    per: usize,
) -> Result<Vec<Vec<Hit>>> {
    if questions.is_empty() || ix.paths.is_empty() {
        return Ok(vec![Vec::new(); questions.len()]);
    }
    let qs = embed.embed(questions)?;
    let mut out = Vec::new();
    for q in &qs {
        let sims = rank::sims(&ix.vecs, ix.dim, q);
        let order = rank::order(&sims);
        let mut by: Vec<(String, Vec<Hit>)> = Vec::new();
        let mut at: HashMap<String, usize> = HashMap::new();
        for &i in &order[..head(order.len(), i64::try_from(per * 20).unwrap_or(0))] {
            let src = source_of(&ix.paths[i]);
            let slot = match at.get(&src) {
                Some(&n) => n,
                None if by.len() < per => {
                    at.insert(src.clone(), by.len());
                    by.push((src.clone(), Vec::new()));
                    by.len() - 1
                }
                None => continue,
            };
            if by[slot].1.len() < PASSAGES {
                let [s, e] = ix.spans[i];
                by[slot].1.push((src, ix.paths[i].clone(), s, e));
            }
        }
        out.push(by.into_iter().flat_map(|(_, h)| h).collect());
    }
    Ok(out)
}

/// Every indexed file holding `term` (any case), relative to the archive or to the repository: `grep -rlIiF`, as the Python ran it.
///
/// # Errors
/// grep cannot run.
pub fn files_with(archive_dir: &Path, root: &Path, term: &str) -> Result<BTreeSet<String>> {
    files_with_by("grep", archive_dir, root, term)
}

/// [`files_with`] with the grep it runs named (a test's missing one).
///
/// # Errors
/// grep cannot run.
pub fn files_with_by(
    grep: &str,
    archive_dir: &Path,
    root: &Path,
    term: &str,
) -> Result<BTreeSet<String>> {
    let mut got = BTreeSet::new();
    let record = root.join(QUESTIONS);
    for (base, rel_to, include) in [
        (archive_dir, archive_dir, "*.txt"),
        (record.as_path(), root, "*.html"),
    ] {
        if !base.is_dir() {
            continue;
        }
        let out = Command::new(grep)
            .args([
                "-rlIiF",
                &format!("--include={include}"),
                "--exclude-dir=.git",
                &format!("--exclude-dir={INDEX_DIR}"),
                "--",
                term,
            ])
            .arg(base)
            .output()
            .map_err(|e| Error(format!("grep: {e}")))?;
        let prefix = format!("{}/", rel_to.display());
        for f in String::from_utf8_lossy(&out.stdout).lines() {
            let rel = f.strip_prefix(&prefix).unwrap_or(f);
            if !rel.ends_with(".originals.html")
                && rel.split('/').filter(|p| !p.is_empty()).count() >= 2
            {
                got.insert(rel.to_owned());
            }
        }
    }
    Ok(got)
}

/// Where `needle` first stands in `hay`, in characters (`str.find`), or -1.
fn find_chars(hay: &str, needle: &str) -> i64 {
    hay.find(needle)
        .map_or(-1, |b| i64::try_from(hay[..b].chars().count()).unwrap_or(0))
}

/// For each term set, the sources holding every term, the most mentions first, each with the place its first term first appears.
///
/// # Errors
/// grep cannot run, or a file cannot be read.
pub fn text(archive_dir: &Path, root: &Path, term_sets: &[Vec<String>]) -> Result<Vec<Vec<Hit>>> {
    let mut out = Vec::new();
    for terms in term_sets {
        let mut files: Option<BTreeSet<String>> = None;
        for t in terms {
            let got = files_with(archive_dir, root, t)?;
            files = Some(match files {
                None => got,
                Some(f) => f.intersection(&got).cloned().collect(),
            });
        }
        let mut scored = Vec::new();
        for rel in files.unwrap_or_default() {
            let body = text_at(archive_dir, root, &rel)?;
            let low = body.to_lowercase();
            let at = find_chars(&low, &terms[0].to_lowercase());
            let start = (at - i64::try_from(SNIPPET / 2).unwrap_or(0)).max(0);
            let len = i64::try_from(body.chars().count()).unwrap_or(0);
            let count: usize = terms
                .iter()
                .map(|t| low.matches(&t.to_lowercase()).count())
                .sum();
            let end = len.min(start + i64::try_from(SNIPPET).unwrap_or(0));
            scored.push((std::cmp::Reverse(count), source_of(&rel), rel, start, end));
        }
        scored.sort();
        let mut seen = BTreeSet::new();
        let mut hits = Vec::new();
        for (_, src, rel, s, e) in scored {
            if seen.insert(src.clone()) {
                hits.push((src, rel, s, e));
            }
        }
        out.push(hits);
    }
    Ok(out)
}

/// One fused source: its score, which searches found it, and its best passages of each (`index`, `text`).
#[derive(Debug, Clone, PartialEq)]
pub struct Row {
    pub source: String,
    pub score: f64,
    pub by: BTreeSet<&'static str>,
    pub index: Vec<Span>,
    pub text: Vec<Span>,
}

/// The sources of every list, ranked by reciprocal-rank fusion.
#[must_use]
pub fn fuse(meaning_lists: &[Vec<Hit>], text_lists: &[Vec<Hit>]) -> Vec<Row> {
    let mut rows: Vec<Row> = Vec::new();
    let mut at: HashMap<String, usize> = HashMap::new();
    for (kind, lists) in [("index", meaning_lists), ("text", text_lists)] {
        for hits in lists {
            let mut ranked: Vec<&str> = Vec::new();
            for (src, rel, s, e) in hits {
                let n = *at.entry(src.clone()).or_insert_with(|| {
                    rows.push(Row {
                        source: src.clone(),
                        score: 0.0,
                        by: BTreeSet::new(),
                        index: Vec::new(),
                        text: Vec::new(),
                    });
                    rows.len() - 1
                });
                let row = &mut rows[n];
                if !ranked.contains(&src.as_str()) {
                    ranked.push(src);
                    #[expect(clippy::cast_precision_loss, reason = "a rank, far below 2^52")]
                    let rank = ranked.len() as f64;
                    row.score += 1.0 / (FUSE + rank);
                }
                row.by.insert(kind);
                let (kept, cap) = if kind == "index" {
                    (&mut row.index, PASSAGES)
                } else {
                    (&mut row.text, 1)
                };
                let span = (rel.clone(), *s, *e);
                if kept.len() < cap && !kept.contains(&span) {
                    kept.push(span);
                }
            }
        }
    }
    rows.sort_by(|a, b| {
        b.score
            .partial_cmp(&a.score)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then_with(|| a.source.cmp(&b.source))
    });
    rows
}

pub mod measure;

pub use measure::measure_passages;

/// Where a key's shown sources are remembered.
#[must_use]
pub fn seen_path(home: &Path, key: &str) -> PathBuf {
    let mut name = String::new();
    let mut run = false;
    for c in key.chars() {
        if c.is_ascii_alphanumeric() || matches!(c, '.' | '_' | '-') {
            name.push(c);
            run = false;
        } else if !run {
            name.push('-');
            run = true;
        }
    }
    home.join(SEEN_DIR).join(format!("{name}.json"))
}

/// What a search found: the rows to print, how many sources in all, how many held back as already shown.
pub struct Found {
    pub rows: Vec<Row>,
    pub found: usize,
    pub held: usize,
}

/// The sources to print - the record's pages first, then the archive's, each in its own rank - with the counts.
///
/// # Errors
/// The index, a file or the seen list cannot be read, the seen list cannot be written, or the embedder failed.
#[expect(
    clippy::too_many_arguments,
    reason = "the Python's own parameters, one for one"
)]
pub fn search(
    archive_dir: &Path,
    root: &Path,
    home: &Path,
    questions: &[String],
    term_sets: &[Vec<String>],
    embed: &mut dyn Embed,
    key: &str,
    limits: (i64, i64),
) -> Result<Found> {
    // the index is read only where a question asks it (the Python read it on every call; the outputs the same)
    let ix = if questions.is_empty() {
        Index::default()
    } else {
        load_index(&crate::index_dir(archive_dir))?
    };
    let rows = fuse(
        &meaning(&ix, questions, embed, PER_QUESTION)?,
        &text(archive_dir, root, term_sets)?,
    );
    let path = (!key.is_empty()).then(|| seen_path(home, key));
    let mut shown: BTreeSet<String> = BTreeSet::new();
    if let Some(p) = path.as_ref().filter(|p| p.is_file()) {
        let fresh = std::fs::metadata(p)
            .and_then(|m| m.modified())
            .ok()
            .and_then(|t| t.elapsed().ok())
            .is_some_and(|age| age < std::time::Duration::from_secs(SEEN_DAYS * 86_400));
        if fresh {
            let raw =
                std::fs::read_to_string(p).map_err(|e| Error(format!("{e}: '{}'", p.display())))?;
            let v: Value =
                serde_json::from_str(&raw).map_err(|e| Error(format!("JSONDecodeError: {e}")))?;
            shown = v
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(|s| s.as_str().map(str::to_owned))
                .collect();
        }
    }
    let fresh: Vec<&Row> = rows.iter().filter(|r| !shown.contains(&r.source)).collect();
    let record: Vec<&Row> = fresh
        .iter()
        .copied()
        .filter(|r| r.source.starts_with("record "))
        .collect();
    let other: Vec<&Row> = fresh
        .iter()
        .copied()
        .filter(|r| !r.source.starts_with("record "))
        .collect();
    let out: Vec<Row> = record[..head(record.len(), limits.1)]
        .iter()
        .chain(&other[..head(other.len(), limits.0)])
        .map(|r| (*r).clone())
        .collect();
    if let Some(p) = &path {
        let all: BTreeSet<String> = shown
            .into_iter()
            .chain(out.iter().map(|r| r.source.clone()))
            .collect();
        let list = Value::Array(all.into_iter().map(Value::String).collect());
        let dir = p.parent().unwrap_or(Path::new("."));
        std::fs::create_dir_all(dir).map_err(|e| Error(format!("{e}: '{}'", dir.display())))?;
        std::fs::write(p, l7r_guard::shared::pyjson::dumps(&list, None, true))
            .map_err(|e| Error(format!("{e}: '{}'", p.display())))?;
    }
    let held = rows.len() - fresh.len();
    Ok(Found {
        found: rows.len(),
        held,
        rows: out,
    })
}

fn snippet(archive_dir: &Path, root: &Path, rel: &str, s: i64, e: i64) -> Result<String> {
    let chars: Vec<char> = text_at(archive_dir, root, rel)?.chars().collect();
    Ok(first(&squeeze(&slice(&chars, s, e)), SNIPPET))
}

/// Each source with its passages: up to PASSAGES nearest by meaning, its text-search hit, and up to PASSAGES measures nearest the terms
/// that those do not already show.
///
/// # Errors
/// A file cannot be read.
pub fn render(
    archive_dir: &Path,
    root: &Path,
    rows: &[Row],
    terms: &[String],
) -> Result<Vec<String>> {
    let mut lines = Vec::new();
    for (n, r) in rows.iter().enumerate() {
        let record = r.source.starts_with("record ");
        if n == 0 || record != rows[n - 1].source.starts_with("record ") {
            lines.push(
                if record {
                    "-- the record's pages (already answered?) --"
                } else {
                    "-- the archive's sources --"
                }
                .to_owned(),
            );
        }
        lines.push(format!(
            "{:2}. {}  [{}]",
            n + 1,
            r.source,
            r.by.iter().copied().collect::<Vec<_>>().join("+")
        ));
        let mut shown: Vec<Span> = Vec::new();
        for (label, kept) in [("meaning", &r.index), ("text", &r.text)] {
            for (rel, s, e) in kept {
                shown.push((
                    rel.clone(),
                    *s,
                    (*e).min(s + i64::try_from(SNIPPET).unwrap_or(0)),
                ));
                lines.push(format!(
                    "    {label}: {rel} [{s}:{e}] {}",
                    snippet(archive_dir, root, rel, *s, *e)?
                ));
            }
        }
        let rel = shown[0].0.clone();
        for (s, e) in measure_passages(&text_at(archive_dir, root, &rel)?, terms, PASSAGES) {
            if !shown
                .iter()
                .any(|(r2, s2, e2)| *r2 == rel && *s2 < e && s < *e2)
            {
                lines.push(format!(
                    "    measure: {rel} [{s}:{e}] {}",
                    snippet(archive_dir, root, &rel, s, e)?
                ));
            }
        }
    }
    Ok(lines)
}

#[cfg(test)]
mod tests;
