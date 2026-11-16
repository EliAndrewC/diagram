//! The index built, searched and committed (feature 449 T138, `semantic_index.py`'s `build`, `find`, `preview` and `commit`).
//!
//! THE INDEX IS STORED IN THE ARCHIVE (the GM, feature 447: "Do we check that in to the private GitHub repo where we store our research
//! corpus? that probably makes sense to me"): `semantic-index/<model>/<shard>.npz` in the archive's working copy, one shard a folder of
//! the archive and one a hundred questions of the record. A passage is keyed by a fingerprint of the model and its text, so an update
//! embeds only the passages that are new or changed and rewrites only their shards; a change of model is a new folder, a rebuild whole.

use std::collections::HashMap;
use std::path::Path;

use l7r_gate_archive::store::Archive;

use crate::corpus::{files, groups, text_of};
use crate::embed::Embed;
use crate::npz::{f32_to_half, read, write, Shard};
use crate::text::{fingerprint, first, passages, read_lossy, slice, squeeze, strip_html};
use crate::{
    head, index_dir, rank, Error, Result, DIM, INDEX_DIR, MODEL, MODEL_DIR, PASSAGE_CHARS,
    QUESTIONS,
};

/// One passage: its file, its text, its span.
struct Item {
    rel: String,
    text: String,
    span: [i64; 2],
}

fn int(v: usize) -> i64 {
    i64::try_from(v).unwrap_or(i64::MAX)
}

/// Bring every shard up to date: each passage's vector kept where its fingerprint is already in the shard, embedded where it is new; a
/// shard written only where its passages changed. `only` names the shards to do, `limit` stops after that many shards written (a run
/// killed or stopped resumes where it left off: each shard is written as it is done). Each shard written is told to `say`; returns them.
///
/// # Errors
/// A file cannot be read, a shard cannot be read or written, or the embedder failed.
pub fn build(
    archive_dir: &Path,
    root: &Path,
    embed: &mut dyn Embed,
    only: &[String],
    limit: i64,
    when: (u16, u16),
    say: &mut dyn FnMut(&str),
) -> Result<Vec<String>> {
    let out_dir = index_dir(archive_dir);
    let mut written = Vec::new();
    // ONE SHARD IN MEMORY AT A TIME: the corpus comes in path order, so a shard's files are contiguous, and the whole corpus - about 106
    // million characters - is never held at once
    for (shard, group) in groups(files(archive_dir, root)?) {
        if !only.is_empty() && !only.contains(&shard) {
            continue;
        }
        let mut items = Vec::new();
        for f in &group {
            let chars: Vec<char> = text_of(f)?.chars().collect();
            for (s, e) in passages(&chars, PASSAGE_CHARS) {
                items.push(Item {
                    rel: f.rel.clone(),
                    text: chars[s..e].iter().collect(),
                    span: [int(s), int(e)],
                });
            }
        }
        let fps: Vec<String> = items.iter().map(|i| fingerprint(&i.text)).collect();
        let path = out_dir.join(format!("{shard}.npz"));
        let old = read(&path)?;
        let mut have: HashMap<&str, &[u16]> = HashMap::new();
        if let Some(o) = &old {
            if o.fps == fps {
                continue;
            }
            for (i, f) in o.fps.iter().enumerate() {
                have.insert(
                    f,
                    o.vecs.get(i * o.dim..(i + 1) * o.dim).unwrap_or_default(),
                );
            }
        }
        let todo: Vec<usize> = (0..fps.len())
            .filter(|&i| !have.contains_key(fps[i].as_str()))
            .collect();
        let texts: Vec<String> = todo.iter().map(|&i| items[i].text.clone()).collect();
        let new = embed.embed(&texts)?;
        // a passage twice in the shard takes the vector of its LAST embedding, as `dict(zip(...))` kept it
        let got: HashMap<&str, &Vec<f32>> =
            todo.iter().map(|&i| fps[i].as_str()).zip(&new).collect();
        if fps.is_empty() {
            return Err(Error("need at least one array to stack".to_owned()));
        }
        let mut vecs = Vec::with_capacity(fps.len() * DIM);
        for f in &fps {
            match (have.get(f.as_str()), got.get(f.as_str())) {
                (Some(kept), _) => vecs.extend_from_slice(kept),
                (None, Some(v)) if v.len() == DIM => vecs.extend(v.iter().map(|x| f32_to_half(*x))),
                _ => {
                    return Err(Error(format!(
                        "the embedder gave no {DIM}-long vector for a passage of {shard}"
                    )))
                }
            }
        }
        let shard_data = Shard {
            fps,
            vecs,
            dim: DIM,
            paths: items.iter().map(|i| i.rel.clone()).collect(),
            spans: items.iter().map(|i| i.span).collect(),
        };
        write(&path, &shard_data, when)?;
        say(&format!(
            "semantic-index: {shard} - {} passages, {} embedded",
            items.len(),
            todo.len()
        ));
        written.push(shard);
        if limit != 0 && int(written.len()) >= limit {
            break;
        }
    }
    Ok(written)
}

/// The shards in the index folder, in name order (`sorted(out_dir.glob("*.npz"))`).
#[must_use]
pub fn shard_paths(out_dir: &Path) -> Vec<std::path::PathBuf> {
    let mut out: Vec<std::path::PathBuf> = std::fs::read_dir(out_dir)
        .map(|rd| {
            rd.flatten()
                .map(|e| e.path())
                .filter(|p| {
                    p.file_name()
                        .is_some_and(|n| n.to_string_lossy().ends_with(".npz"))
                })
                .collect()
        })
        .unwrap_or_default();
    out.sort();
    out
}

/// A shard that is there (`load_shard` then `assert z is not None`).
///
/// # Errors
/// It cannot be read.
pub fn must_read(path: &Path) -> Result<Shard> {
    read(path)?.ok_or_else(|| Error(format!("AssertionError: {} is not a shard", path.display())))
}

/// One hit: its similarity, its file and span.
pub type Found = (f32, String, i64, i64);

/// The `k` passages nearest `question`, the nearest first.
///
/// # Errors
/// A shard cannot be read, or the embedder failed.
pub fn find(
    archive_dir: &Path,
    question: &str,
    embed: &mut dyn Embed,
    k: i64,
) -> Result<Vec<Found>> {
    let shards = shard_paths(&index_dir(archive_dir));
    if shards.is_empty() {
        return Ok(Vec::new());
    }
    let q = embed
        .embed(&[question.to_owned()])?
        .into_iter()
        .next()
        .unwrap_or_default();
    let mut best: Vec<Found> = Vec::new();
    for p in shards {
        let z = must_read(&p)?;
        let sims = rank::sims(&z.vecs, z.dim, &q);
        let order = rank::order(&sims);
        for &i in &order[..head(order.len(), k)] {
            let span = z.spans.get(i).copied().unwrap_or_default();
            best.push((
                sims[i],
                z.paths.get(i).cloned().unwrap_or_default(),
                span[0],
                span[1],
            ));
        }
    }
    // `sorted(best, reverse=True)`: the similarity, then the path and the span, all descending
    best.sort_by(|a, b| {
        b.0.partial_cmp(&a.0)
            .unwrap_or(std::cmp::Ordering::Equal)
            .then(b.1.cmp(&a.1))
            .then(b.2.cmp(&a.2))
            .then(b.3.cmp(&a.3))
    });
    best.truncate(head(best.len(), k));
    Ok(best)
}

/// A record page's or an archived text's text, as it was indexed (`_text_of`).
///
/// # Errors
/// It cannot be read.
pub fn text_at(archive_dir: &Path, root: &Path, rel: &str) -> Result<String> {
    if rel.starts_with(QUESTIONS) {
        return Ok(strip_html(&read_lossy(&root.join(rel))?));
    }
    read_lossy(&archive_dir.join(rel))
}

/// The passage's opening words, read again from its file (`preview`).
///
/// # Errors
/// It cannot be read.
pub fn preview(
    archive_dir: &Path,
    root: &Path,
    rel: &str,
    start: i64,
    end: i64,
    width: usize,
) -> Result<String> {
    let chars: Vec<char> = text_at(archive_dir, root, rel)?.chars().collect();
    Ok(first(&squeeze(&slice(&chars, start, end)), width))
}

/// Commit the shards written and push, under the archive's lock: empty on success, else git's complaint.
///
/// # Errors
/// The lock, a git step, or the push could not run.
pub fn commit(store: &Archive, written: &[String], say: &mut dyn FnMut(&str)) -> Result<String> {
    if written.is_empty() {
        return Ok(String::new());
    }
    let failed = |e: l7r_gate_archive::Error| Error(e.to_string());
    let why = {
        let _lock = store.locked(600.0).map_err(failed)?;
        store
            .git(&["add", "--", &format!("{INDEX_DIR}/{MODEL_DIR}")], true)
            .map_err(failed)?;
        if store
            .git(&["diff", "--cached", "--quiet"], false)
            .map_err(failed)?
            .status
            .success()
        {
            return Ok(String::new());
        }
        let more = if written.len() > 8 { " ..." } else { "" };
        let message = format!(
            "the semantic index ({MODEL}): {} shard(s) - {}{more}",
            written.len(),
            written[..written.len().min(8)].join(", ")
        );
        store
            .git(&["commit", "-q", "-m", &message], true)
            .map_err(failed)?;
        store.push().map_err(failed)?
    };
    say(&if why.is_empty() {
        "semantic-index: committed and pushed".to_owned()
    } else {
        format!("semantic-index: the push failed - {why}")
    });
    Ok(why)
}

#[cfg(test)]
mod tests;
