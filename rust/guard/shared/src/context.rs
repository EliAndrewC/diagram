//! A transcript's context, its last model call's usage - the caller's own last iteration of it, an advisor call's iteration and the
//! one before it left out (451 T68) - read from its tail (feature 451 T12's reader, moved here by 451 T58 so the event log, which the
//! gate's crates read, builds without the context-cap guard).

use std::fs::File;
use std::io::{Read as _, Seek as _, SeekFrom};
use std::path::{Path, PathBuf};

use serde_json::Value;

/// How far back the transcript is read for its last model call: 16 MiB. A transcript row is one tool call's result at most, and the
/// largest builder transcript of the window, 50 MB, was scanned whole in 0.07 s (research R2); a last call further back than this is
/// no call the guard can see, and passes.
pub const TAIL_BYTES: u64 = 16 << 20;

/// The bytes read a step, backwards.
const CHUNK: u64 = 64 << 10;

/// The subagent's own transcript, derived from the session's (D9; R2).
#[must_use]
pub fn own_transcript(session_transcript: &str, agent: &str) -> Option<PathBuf> {
    let stem = session_transcript.strip_suffix(".jsonl")?;
    Some(
        Path::new(stem)
            .join("subagents")
            .join(format!("agent-{agent}.jsonl")),
    )
}

/// The context of a transcript's last model call: its last `assistant` row's [`usage_of`], read backwards in [`CHUNK`]s at most
/// [`TAIL_BYTES`] deep; None where none is found.
#[must_use]
pub fn context(path: &Path) -> Option<u64> {
    let mut f = File::open(path).ok()?;
    let mut pos = f.metadata().ok()?.len();
    // the bytes from `pos` to the end of what is not yet scanned
    let mut buf: Vec<u8> = Vec::new();
    let mut read = 0;
    loop {
        // each line after a newline in `buf` is whole: scanned from the last back
        while let Some(i) = buf.iter().rposition(|&b| b == b'\n') {
            let line = buf.split_off(i + 1);
            buf.pop();
            if let Some(n) = usage_of(&line) {
                return Some(n);
            }
        }
        if pos == 0 {
            return usage_of(&buf);
        }
        if read >= TAIL_BYTES {
            return None;
        }
        let step = CHUNK.min(pos);
        pos -= step;
        f.seek(SeekFrom::Start(pos)).ok()?;
        let mut chunk = vec![0; usize::try_from(step).ok()?];
        f.read_exact(&mut chunk).ok()?;
        chunk.extend_from_slice(&buf);
        buf = chunk;
        read += step;
    }
}

/// The context one transcript row reports: an `assistant` row's input, cache read and cache creation, None for any other row or a
/// sum of zero. They are read from the row's last own iteration (`usage.iterations`' last of type `message`), else its top level:
/// on a row carrying an advisor call the top level is the builder's own two iterations, before and after the call, summed - twice
/// its context - and the advisor's iteration is in neither, so the top level refused 33 of the cap's 34 refusals since T12 at a
/// context of 151k to 290k (451 T68, measured 2026-11-21 on the 581 advisor rows of the session's subagent transcripts and the guard
/// log's past-cap rows). The call's cost, [`call_of`], stays the top level's: both own iterations are billed.
#[must_use]
pub fn usage_of(line: &[u8]) -> Option<u64> {
    let usage = message_of(line)?.get_mut("usage")?.take();
    let prompt = |u: &Value| -> u64 {
        [
            "input_tokens",
            "cache_read_input_tokens",
            "cache_creation_input_tokens",
        ]
        .iter()
        .map(|k| u.get(k).and_then(Value::as_u64).unwrap_or(0))
        .sum()
    };
    let own = usage
        .get("iterations")
        .and_then(Value::as_array)
        .and_then(|its| {
            its.iter()
                .rfind(|i| i.get("type").and_then(Value::as_str) == Some("message"))
        })
        .map(prompt)
        .filter(|&n| n > 0);
    let sum = own.unwrap_or_else(|| prompt(&usage));
    (sum > 0).then_some(sum)
}

/// An `assistant` row's `message`, None for any other row or a row naming no `usage`.
fn message_of(line: &[u8]) -> Option<Value> {
    const NEEDLE: &[u8] = b"\"usage\"";
    if !line.windows(NEEDLE.len()).any(|w| w == NEEDLE) {
        return None;
    }
    let mut row: Value = serde_json::from_slice(line).ok()?;
    if row.get("type").and_then(Value::as_str) != Some("assistant") {
        return None;
    }
    Some(row.get_mut("message")?.take())
}

/// One model call's usage as an `assistant` transcript row reports it at its top level - the event log's `tok` (feature 451 T07,
/// plan D6), a call's cost; the row's parse is the one [`usage_of`], which [`context`] reads, shares (451 T68).
#[derive(Debug, Default, Clone, PartialEq, Eq)]
pub struct Call {
    /// The row's `message.id`: one call's streamed reply is several rows of one id ("" where the row names none).
    pub id: String,
    pub input: u64,
    pub cached: u64,
    pub created: u64,
    pub out: u64,
}

/// An `assistant` row's `message.usage`, None for any other row: a `user` row holding an Agent call's result carries that child's usage.
pub fn call_of(line: &[u8]) -> Option<Call> {
    let message = message_of(line)?;
    let usage = message.get("usage")?;
    let n = |k: &str| usage.get(k).and_then(Value::as_u64).unwrap_or(0);
    Some(Call {
        id: message
            .get("id")
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_owned(),
        input: n("input_tokens"),
        cached: n("cache_read_input_tokens"),
        created: n("cache_creation_input_tokens"),
        out: n("output_tokens"),
    })
}

#[cfg(test)]
mod tests;
