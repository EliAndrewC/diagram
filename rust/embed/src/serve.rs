//! `l7r-embed serve` (feature 449 T138): the model loaded once, then one request a line - a JSON array of texts - answered with
//! `ok <rows> <dim>` and the vectors as little-endian float32, row after row, or `err <message>`; end of input ends it. The gate's
//! `semantic` crate keeps one running for a build or a search, as `semantic_index.py` kept one `TextEmbedding`.
//!
//! A request's texts go through the network in batches of `BATCH`, in order, as `fastembed`'s `embed(texts, batch_size=8)` cut them:
//! a text's vector depends on its batch (`tok.rs` says why), so the batches are the Python's.

use std::io::{BufRead, Write};

use tokenizers::Tokenizer;

use crate::Network;

/// `semantic_index.py`'s `BATCH`, the texts the network takes at once.
pub const BATCH: usize = 8;

/// The vectors of `texts`, `batch` at a time: `rows * dim` floats and `dim` (0 for no texts).
///
/// # Errors
/// The tokenizer or the network refused a batch.
pub fn embed(
    t: &Tokenizer,
    net: &mut dyn Network,
    texts: &[String],
    batch: usize,
) -> Result<(Vec<f32>, usize), String> {
    let mut out = Vec::new();
    let mut dim = 0;
    for chunk in texts.chunks(batch.max(1)) {
        let b = crate::tok::encode(t, chunk)?;
        let (rows, d) = net.cls(b.ids, b.mask, b.rows, b.len)?;
        dim = d;
        out.extend(crate::pool::normalized(&rows, d));
    }
    Ok((out, dim))
}

/// Answers each request line of `input` on `output` until the input ends.
///
/// # Errors
/// The output cannot be written.
pub fn serve(
    t: &mut Tokenizer,
    net: &mut dyn Network,
    batch: usize,
    input: &mut dyn BufRead,
    output: &mut dyn Write,
) -> Result<(), String> {
    let wrote = |e: std::io::Error| format!("the answer could not be written: {e}");
    writeln!(output, "ready").map_err(wrote)?;
    output.flush().map_err(wrote)?;
    let mut line = String::new();
    loop {
        line.clear();
        if input.read_line(&mut line).unwrap_or(0) == 0 {
            return Ok(());
        }
        let texts: Result<Vec<String>, String> = serde_json::from_str(&line)
            .map_err(|e| format!("a request is a JSON array of texts: {e}"));
        match texts.and_then(|texts| embed(t, net, &texts, batch)) {
            Ok((vecs, dim)) => {
                let rows = if dim == 0 { 0 } else { vecs.len() / dim };
                writeln!(output, "ok {rows} {dim}").map_err(wrote)?;
                let bytes: Vec<u8> = vecs.iter().flat_map(|x| x.to_le_bytes()).collect();
                output.write_all(&bytes).map_err(wrote)?;
            }
            Err(e) => writeln!(output, "err {}", e.replace('\n', " ")).map_err(wrote)?,
        }
        output.flush().map_err(wrote)?;
    }
}

#[cfg(test)]
mod tests;
