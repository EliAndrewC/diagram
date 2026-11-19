//! The embedder as the gate reaches it (feature 449 T138, `ask:449-phase4-slices` Q11): `l7r-embed serve` (the embedder crate,
//! `rust/embed/`) run as a program through `scripts/gates/l7r-gate.sh embed`, so the gate never compiles ONNX Runtime's bindings. One
//! process for a build or a search, started at the first texts there are to embed (`semantic_index.py` loaded `fastembed`'s model before
//! anything else; an update with nothing new, or a search by terms alone, now starts no model at all - the outputs the same).
//!
//! The protocol is the embedder's (`rust/embed/src/serve.rs`): a request is a JSON array of texts on one line; the answer `ok <rows> <dim>`
//! and the vectors as little-endian float32, or `err <message>`.

use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};

use crate::{Error, Result};

/// What turns texts into vectors (`semantic_index.Embed`): the program, or a test's stand-in.
pub trait Embed {
    /// One vector per text, in order.
    ///
    /// # Errors
    /// The embedder could not start or refused the texts.
    fn embed(&mut self, texts: &[String]) -> Result<Vec<Vec<f32>>>;
}

struct Running {
    child: Child,
    to: ChildStdin,
    from: BufReader<ChildStdout>,
}

/// `l7r-gate.sh embed serve --cache <cache>`, started on first use.
pub struct Program {
    launcher: PathBuf,
    cache: PathBuf,
    running: Option<Running>,
}

impl Program {
    #[must_use]
    pub fn new(launcher: &Path, cache: &Path) -> Self {
        Self {
            launcher: launcher.to_path_buf(),
            cache: cache.to_path_buf(),
            running: None,
        }
    }

    fn spawn(&self) -> Result<Running> {
        let mut child = Command::new(&self.launcher)
            .args(["embed", "serve", "--cache"])
            .arg(&self.cache)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .spawn()
            .map_err(|e| {
                Error(format!(
                    "the embedder could not start ({}): {e}",
                    self.launcher.display()
                ))
            })?;
        // both pipes were asked for, so both are there (an eager `ok_or`: no line a test cannot reach)
        let (to, out) = child
            .stdin
            .take()
            .zip(child.stdout.take())
            .ok_or(Error(String::new()))?;
        let mut from = BufReader::new(out);
        let mut ready = String::new();
        let _ = from.read_line(&mut ready);
        if ready != "ready\n" {
            drop(to);
            let status = child.wait().map(|s| s.to_string()).unwrap_or_default();
            return Err(Error(format!(
                "the embedder did not start ({status}; its own words are above)"
            )));
        }
        Ok(Running { child, to, from })
    }

    fn start(&mut self) -> Result<&mut Running> {
        let running = match self.running.take() {
            Some(r) => r,
            None => self.spawn()?,
        };
        Ok(self.running.insert(running))
    }
}

/// One answer: `rows` vectors of `dim` read from `from` after its `ok` line.
fn answer(from: &mut dyn BufRead) -> Result<Vec<Vec<f32>>> {
    let mut head = String::new();
    // AN EMBEDDER GONE BEFORE IT ANSWERED IS SAID SO (found beside feature 449 T205): the test of an embedder that closed its input
    // failed once under a loaded `make static` cover run (2026-11-19) and passed alone - the texts' line was taken and the output then
    // ended, the one other way such an embedder can go; read as an answer that was "answered \"\"", now it is "stopped"
    if from.read_line(&mut head).unwrap_or(0) == 0 {
        return Err(Error("the embedder stopped before it answered".to_owned()));
    }
    let words: Vec<&str> = head.trim_end().splitn(3, ' ').collect();
    let (rows, dim) = match words.as_slice() {
        ["ok", rows, dim] => (
            rows.parse::<usize>().unwrap_or(0),
            dim.parse::<usize>().unwrap_or(0),
        ),
        ["err", ..] => {
            return Err(Error(format!(
                "the embedder refused: {}",
                &head[4..].trim_end()
            )))
        }
        _ => {
            return Err(Error(format!(
                "the embedder answered {:?}",
                head.trim_end()
            )))
        }
    };
    let mut bytes = vec![0u8; rows * dim * 4];
    from.read_exact(&mut bytes)
        .map_err(|e| Error(format!("the embedder's vectors were cut short: {e}")))?;
    Ok(bytes
        .chunks(dim * 4)
        .map(|row| {
            row.chunks(4)
                .map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]]))
                .collect()
        })
        .collect())
}

impl Embed for Program {
    fn embed(&mut self, texts: &[String]) -> Result<Vec<Vec<f32>>> {
        if texts.is_empty() {
            return Ok(Vec::new());
        }
        let running = self.start()?;
        let line = serde_json::to_string(texts).unwrap_or_default();
        let to = &mut running.to;
        writeln!(to, "{line}")
            .and_then(|()| to.flush())
            .map_err(|e| Error(format!("the embedder stopped: {e}")))?;
        let got = answer(&mut running.from)?;
        if got.len() != texts.len() {
            return Err(Error(format!(
                "the embedder gave {} vectors for {} texts",
                got.len(),
                texts.len()
            )));
        }
        Ok(got)
    }
}

impl Drop for Program {
    fn drop(&mut self) {
        if let Some(Running { mut child, to, .. }) = self.running.take() {
            drop(to);
            let _ = child.wait();
        }
    }
}

#[cfg(test)]
mod tests;
