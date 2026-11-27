//! A line-per-record file (`.jsonl`) both sides appended to or pruned (451 T399, built with T300's part 2): the skip log
//! `dev/claims-triage-skips.jsonl` (a480ff8848 against 240c7d89f9's parent, T298's carry) and the baseline
//! `dev/gm-attribution-baseline.jsonl` (1bd5b1721d against e3922827ac's parent, T250's batch 8), 2 of the 30 conflicted carries of
//! 2026-11-26. From its three whole sides: the base's records neither side removed, in the base's order, then the records the
//! clone appended, then the builder's.
//!
//! EACH appended record is kept, an identical line too: the skip log's writer appends one line a skipped triage with its date and
//! no time (`claims/commands.rs`), so two identical lines are two events - the file held 49 such lines on 2026-11-26 - and nothing
//! in the file says otherwise. A side that changed a record in place, or added one anywhere but the end, stops: that is no append
//! and no prune, and where it belongs is a choice.

use l7r_gate_core::difflib::{opcodes, Tag};

/// What one side did to the base's records: which it removed, and what it appended - or why it is left to a hand.
fn side<'t>(base: &[&str], lines: &[&'t str]) -> Result<(Vec<bool>, Vec<&'t str>), String> {
    let mut gone = vec![false; base.len()];
    let mut appended = Vec::new();
    for (tag, i1, i2, j1, j2) in opcodes(base, lines) {
        if tag == Tag::Equal {
            continue;
        }
        // a replace is a record changed where it stood - the last one too, which an append beside it would move
        if tag == Tag::Replace || j2 < lines.len() && j1 < j2 {
            return Err(
                "a record changed in place or added inside the file, not appended".to_owned(),
            );
        }
        gone[i1..i2].fill(true);
        appended.extend(&lines[j1..j2]);
    }
    Ok((gone, appended))
}

/// The three sides merged by record - or why not.
pub(super) fn merged(base: &str, ours: &str, theirs: &str) -> Result<String, String> {
    let b: Vec<&str> = base.lines().collect();
    let (mine, added) = side(&b, &ours.lines().collect::<Vec<_>>())?;
    let (yours, more) = side(&b, &theirs.lines().collect::<Vec<_>>())?;
    let kept = b
        .iter()
        .enumerate()
        .filter(|(n, _)| !mine[*n] && !yours[*n])
        .map(|(_, line)| *line);
    Ok(kept
        .chain(added)
        .chain(more)
        .fold(String::new(), |all, line| all + line + "\n"))
}
