//! The GM's words on a task's own line of `tasks.md`, which `request.md` must hold before a plan review is dispatched (feature 451
//! T308).
//!
//! WHY: a plan review judges a section against the GM's words in `request.md` and is told to read nothing in the repository, so a
//! task whose words were relayed onto its line of `tasks.md` and nowhere else comes back NOT-REVIEWABLE. Of feature 451's 56 later
//! plan review rounds from 2026-11-24 to 26, 8 were owed for a NOT-REVIEWABLE return, 6 of them for his words missing from
//! `request.md`, a median 4.7 minutes a round after the 2 to 4 the unreviewable round itself took (observed 2026-11-26, method:
//! `dev/measurements/2026-11-26/plan-review-rounds/t308-class.py` over the reviews' transcripts). Three of the six (T243, T245, T285)
//! quoted him on the task line, the form this rule reads; the other three cited him by reference, which no script can follow.

use std::path::Path;

use super::{absent, folded, gm_quotes, GM};

/// The fewest words a quoted span holds to be read as the GM's own (a GUESS knob): a shorter span on a task line is a term in
/// quotes ('other', 'sounds good') far more often than a request.
pub(super) const MIN_WORDS: usize = 4;
/// How far past "the GM", or past the quote before, a single quote may open, in characters (a GUESS knob): the task lines' form is
/// `(the GM, 2026-11-26: '...')`, and a second quote follows the first after a few words.
pub(super) const REACH: usize = 80;

/// `task`'s box line of `tasks`.
fn line_of<'t>(tasks: &'t str, task: &str) -> Option<&'t str> {
    tasks.lines().find(|l| {
        ["- [ ] ", "- [x] ", "- [X] "]
            .iter()
            .filter_map(|b| l.strip_prefix(b))
            .filter_map(|rest| rest.strip_prefix(task))
            .any(|after| !after.starts_with(|c: char| c.is_alphanumeric()))
    })
}

/// Each single-quoted span that follows "the GM" on `line`. A quote opens at a `'` no letter precedes (so "the GM's" opens none) and
/// closes at a `'` no letter follows (so "don't" closes none); a plural's `'` before a space closes it early, and what was read is
/// still his words.
fn single_quoted(line: &str) -> Vec<String> {
    let chars: Vec<(usize, char)> = line.char_indices().collect();
    let mut out: Vec<String> = Vec::new();
    for m in GM.find_iter(line).map_while(Result::ok) {
        let from = chars.partition_point(|(at, _)| *at < m.end());
        let (mut open, mut gap) = (None, 0);
        for i in from..chars.len() {
            let (at, ch) = chars[i];
            let prev = chars[i - 1].1;
            let next = chars.get(i + 1).map_or(' ', |c| c.1);
            match open {
                None if ch == '\'' && !prev.is_alphanumeric() && !next.is_whitespace() => {
                    open = Some(at + 1);
                }
                None => {
                    gap += 1;
                    if gap > REACH {
                        break;
                    }
                }
                Some(start) if ch == '\'' && !next.is_alphanumeric() && !prev.is_whitespace() => {
                    let quote = line[start..at].to_owned();
                    if !out.contains(&quote) {
                        out.push(quote);
                    }
                    (open, gap) = (None, 0);
                }
                Some(_) => {}
            }
        }
    }
    out
}

/// (the task, the quote) for each span of the GM's words on a task's line of `tasks.md` that `request.md` does not hold.
pub(super) fn missing(spec_dir: &Path, tasks: &[String]) -> Vec<(String, String)> {
    let read = |name: &str| std::fs::read_to_string(spec_dir.join(name)).unwrap_or_default();
    let (req, boxes) = (folded(&read("request.md")), read("tasks.md"));
    let mut out = Vec::new();
    for task in tasks {
        let line = line_of(&boxes, task).unwrap_or("");
        let double = gm_quotes(line).into_iter().map(|(_, q)| q);
        for quote in single_quoted(line).into_iter().chain(double) {
            if folded(&quote).split_whitespace().count() >= MIN_WORDS && absent(&quote, &req) {
                out.push((task.clone(), quote));
            }
        }
    }
    out
}
