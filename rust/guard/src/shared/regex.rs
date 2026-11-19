//! Every `fancy_regex` pattern of the Rust tools is built here, its search given no step limit (feature 449 T185).
//!
//! WHY: `fancy_regex` 0.14 runs a pattern with a word boundary (`\b`), a lookaround or a backreference in its own backtracking VM,
//! which gives up a search past `backtrack_limit` steps - a million by default, about one a character on an unanchored search - with an
//! `Err`. A single `is_match` or `find` then quietly read as "no match", `replace_all` panicked, and a `find_iter` or `captures_iter`
//! repeats the error without advancing, so a `.flatten()` over it retried forever at 100% CPU: `make quick` hung on a 157 KB one-line
//! file (T151), `make decide` and `make task-add` on 449's 1 MB of plan (T194). Of the tools' 979 literal patterns, 178 erred at the
//! old limit on 449's 1.1 MB of tasks and plans; run with no limit, none took over 0.4 s on it or on 300 KB of one-line prose, words or
//! JSON, and eight - a trigger word, then an unbounded span to a target, tried from every trigger - took 1.2 to 3.2 s on 30 KB of their
//! own trigger repeated and 14 s to past 30 s on 100 KB, so each now starts at its segment's first trigger (measured 2026-11-18, a
//! scratch harness over `fancy_regex` 0.14, each pattern's `find_iter` to the end, the T185 plan section). A new pattern of that shape
//! (`\bgit\b[^;&|]*\badd`) starts at its segment, `(?:\A|(?<=[;&|]))(?>[^;&|]*?\bgit\b)`, or runs on short text alone. The VM's stack
//! (`MAX_STACK`, a million entries, not configurable) still errs on a greedy span near a megabyte, so a scan ends on its first error:
//! `.map_while(Result::ok)`, never `.flatten()` (the `checks` crate's `documents/regex_scans.rs` holds both rules over the tree).

use fancy_regex::{Error, Regex, RegexBuilder};

/// `pattern` compiled with no step limit: `Regex::new`'s answer, as a pattern the source spells out or reads at run time.
///
/// # Errors
/// The pattern's own syntax error, as `Regex::new` gives it.
#[expect(
    clippy::result_large_err,
    reason = "`Regex::new`'s own signature, which every caller already handles"
)]
pub fn build(pattern: &str) -> Result<Regex, Error> {
    builder(pattern).build()
}

/// A builder for `pattern` with the step limit lifted, for a caller that sets another option before `build()`.
#[must_use]
pub fn builder(pattern: &str) -> RegexBuilder {
    let mut b = RegexBuilder::new(pattern);
    b.backtrack_limit(usize::MAX);
    b
}

#[cfg(test)]
mod tests {
    use super::{build, builder};

    /// A word-boundary pattern's search past the default million steps answers, where `Regex::new`'s erred.
    #[test]
    fn a_search_past_a_million_steps_answers() {
        let text = format!("{}the end", "plain words of a long text\n".repeat(50_000));
        let bounded = fancy_regex::RegexBuilder::new(r"\bend\b").build().unwrap();
        assert!(bounded.is_match(&text).is_err());
        assert_eq!(build(r"\bend\b").unwrap().is_match(&text).ok(), Some(true));
        let sized = builder(r"\bend\b")
            .delegate_size_limit(1 << 20)
            .build()
            .unwrap();
        assert_eq!(sized.is_match(&text).ok(), Some(true));
        assert!(build("(").is_err());
    }
}
