//! The tests' embedder and world (feature 449 T138): a stand-in [`Embed`] whose vector is a text's characters folded into 1,024 places,
//! so like texts are near and the same text is the same vector, and a record and archive laid out as the real ones are.

use std::cell::RefCell;
use std::path::Path;

use crate::embed::Embed;
use crate::{Error, Result, DIM};

/// A vector for `text`: each character's code point adds to a place, then the whole normalized.
#[must_use]
pub fn vector(text: &str) -> Vec<f32> {
    let mut v = vec![0.0_f32; DIM];
    for (i, c) in text.chars().enumerate() {
        v[(u32::from(c) as usize + i % 3) % DIM] += 1.0;
    }
    let norm = v.iter().map(|x| x * x).sum::<f32>().sqrt().max(1e-12);
    v.iter().map(|x| x / norm).collect()
}

/// The stand-in: each call's texts recorded; `fail` refuses, `short` answers one vector too few, `narrow` gives 3-long vectors.
#[derive(Default)]
pub struct Fake {
    pub calls: RefCell<Vec<Vec<String>>>,
    pub fail: bool,
    pub narrow: bool,
}

impl Embed for Fake {
    fn embed(&mut self, texts: &[String]) -> Result<Vec<Vec<f32>>> {
        if self.fail {
            return Err(Error("the stand-in refused".to_owned()));
        }
        if texts.is_empty() {
            return Ok(Vec::new());
        }
        self.calls.borrow_mut().push(texts.to_vec());
        Ok(texts
            .iter()
            .map(|t| {
                if self.narrow {
                    vec![1.0, 0.0, 0.0]
                } else {
                    vector(t)
                }
            })
            .collect())
    }
}

/// A record page's path in the repository, from its name (built from parts, so no fixture names a question of the real record).
#[must_use]
pub fn q(name: &str) -> String {
    format!("{}/{name}", crate::QUESTIONS)
}

/// A file written, its folders made.
pub fn put(path: &Path, text: &str) {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// An archive of texts under `dir` (`<shard>/<id>/<stamp>/text.txt`) and record pages under `root`.
pub fn corpus(dir: &Path, root: &Path) {
    put(
        &dir.join("ab/abc123/20260101T000000Z/text.txt"),
        "The paddy field was ten tan, a large single field of rice.",
    );
    put(
        &dir.join("ab/abd456/20260101T000000Z/text.txt"),
        "一枚の田の広さは一反ほどで、畦で区切られていた。",
    );
    put(
        &dir.join("cd/cde789/20260101T000000Z/text.txt"),
        "Thatched roofs were replaced every twenty years by the village.",
    );
    put(
        &dir.join("gm-copies/book.txt"),
        "A copy of a book about charcoal yards and twenty yards square fields.",
    );
    put(&dir.join("top.txt"), "a file at the top is no source");
    put(&dir.join(".git/x/y.txt"), "git's own");
    put(
        &root.join(q("0101-paddy-size.html")),
        "<h2>How large was a paddy?</h2><p>A single paddy was a tan or two.</p>",
    );
    put(
        &root.join(q("0102-roofs.html")),
        "<h2>Roofs</h2><p>Thatch, renewed by the village every twenty years.</p>",
    );
    put(
        &root.join(q("0102-roofs.originals.html")),
        "<p>originals</p>",
    );
}
