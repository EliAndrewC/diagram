//! A conflict in a file outside a feature's spec directory resolved hunk by hunk (451 T300, part 2): a hunk with base lines is
//! merged by words ([`super::words`]); a hunk with NONE - each side added whole lines at one place - keeps both sides' blocks,
//! the clone's first, where the file's kind says what a block is:
//!
//! - a Makefile: each side's lines open at a block's first line (not a recipe's tab-indented one) and hold a target's line, and
//!   no target is added by both - two targets' blocks (022170716b against b1d4a453fe's parent, T334's carry: `sampler` and its
//!   three, `builder-brief`); ours, ONE blank line, theirs, the blank line a side ended with kept at the end;
//! - a Markdown file: each side's lines are list lines with their continuation lines, kept as a tasks.md's are ([`super::both`]) -
//!   a bullet of theirs ours holds whole is not doubled, one bullet with different lines under it on each side stops.
//!
//! Anything else added at one place by both - two functions of a Rust source, two paragraphs - stops: their order can matter.

use super::words::{self, Prose};
use super::{both, Kind};

/// The names of the targets `side` defines.
fn targets(side: &str) -> Vec<&str> {
    side.lines()
        .filter(|l| !l.starts_with(['\t', '#', '.', ' ']))
        .filter_map(|l| l.split_once(':'))
        .map(|(name, _)| name.trim())
        .collect()
}

/// Two blocks of Makefile targets added at one place, kept both - or why not.
fn make_blocks(ours: &str, theirs: &str) -> Result<String, String> {
    let (mine, yours) = (targets(ours), targets(theirs));
    let opens = |side: &str| side.trim_start_matches('\n').starts_with('\t');
    if mine.is_empty() || yours.is_empty() || opens(ours) || opens(theirs) {
        return Err(
            "both sides added lines at one place, not each a target's whole block".to_owned(),
        );
    }
    if let Some(twice) = yours.iter().find(|name| mine.contains(name)) {
        return Err(format!("both sides added the target `{twice}`"));
    }
    let end = if ours.ends_with("\n\n") || theirs.ends_with("\n\n") {
        "\n\n"
    } else {
        "\n"
    };
    Ok(format!(
        "{}\n\n{}{end}",
        ours.trim_end_matches('\n'),
        theirs.trim_end_matches('\n')
    ))
}

/// One hunk both sides only added to.
fn blocks(ours: &str, theirs: &str, kind: Prose) -> Result<String, String> {
    match kind {
        Prose::Makefile => make_blocks(ours, theirs),
        Prose::Markdown => both(&split(ours), &split(theirs), Kind::Tasks),
        Prose::Rust => Err("both sides added lines at one place of a source file".to_owned()),
    }
}

fn split(side: &str) -> Vec<&str> {
    side.split_inclusive('\n').collect()
}

/// A diff3 merge (`git merge-file -p --diff3`) with every conflict resolved by its hunk's rule, and the rules used - or why not.
pub(super) fn merged(text: &str, kind: Prose) -> Result<(String, &'static str), String> {
    let mut out = String::new();
    // 0 outside a conflict, 1 in ours, 2 in the base, 3 in theirs
    let mut part = 0;
    let mut sides = [String::new(), String::new(), String::new()];
    let (mut by_words, mut by_block) = (false, false);
    for line in text.split_inclusive('\n') {
        match (part, line.get(..7)) {
            (0, Some("<<<<<<<")) => part = 1,
            (1, Some("|||||||")) => part = 2,
            (2, Some("=======")) => part = 3,
            (3, Some(">>>>>>>")) => {
                part = 0;
                let [ours, base, theirs] = &sides;
                if base.is_empty() {
                    by_block = true;
                    out += &blocks(ours, theirs, kind)?;
                } else {
                    by_words = true;
                    out += &words::merged(base, ours, theirs, kind)?;
                }
                sides = [String::new(), String::new(), String::new()];
            }
            (0, _) => out += line,
            (n, _) => sides[n - 1] += line,
        }
    }
    let rule = match (by_words, by_block) {
        (true, true) => "by words and both sides' added blocks",
        (true, false) => "by words",
        (_, _) => "both sides' added blocks",
    };
    Ok((out, rule))
}
