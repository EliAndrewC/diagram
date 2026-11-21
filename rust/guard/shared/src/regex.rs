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

use std::borrow::Cow;
use std::sync::LazyLock;

use fancy_regex::{Captures, Error, Match, Regex, RegexBuilder, Replacer};

/// A pattern built on its first use, and only for a text that could hold a match (451 T97): `could` is a NECESSARY condition on the
/// text searched - most often a literal every match holds - so a text it rules out could not have matched, and is answered "no
/// match" with nothing built. Each method gates the same text it searches, and answers as `Regex`'s does with a search's error read
/// as no match, as every caller read it. WHY: a hook event is a process of its own and the walk's patterns cost up to 1.4 ms each to
/// build (2.6 ms the first in a process), so a pattern every command reached was built on every Bash call: `shared::tree`'s walk
/// reached at least 10 for each of T93's 9,646 commands, `ls -la` among them (measured 2026-11-21, the T97 plan section's item 4).
pub struct Lazy {
    could: fn(&str) -> bool,
    regex: LazyLock<Regex>,
}

impl Lazy {
    /// The pattern `build` makes, built on the first search of a text `could` lets through.
    #[must_use]
    pub const fn new(could: fn(&str) -> bool, build: fn() -> Regex) -> Self {
        Self {
            could,
            regex: LazyLock::new(build),
        }
    }

    /// The pattern, built on its first use, where `text` could hold a match; None, nothing built, where it cannot.
    #[must_use]
    pub fn on(&self, text: &str) -> Option<&Regex> {
        (self.could)(text).then(|| &*self.regex)
    }

    /// Whether the pattern matches `text`.
    #[must_use]
    pub fn is_match(&self, text: &str) -> bool {
        self.on(text)
            .is_some_and(|r| r.is_match(text).unwrap_or(false))
    }

    /// The first match's groups.
    #[must_use]
    pub fn captures<'t>(&self, text: &'t str) -> Option<Captures<'t>> {
        self.on(text).and_then(|r| r.captures(text).ok().flatten())
    }

    /// Every match's groups, in order, as `Regex::captures_iter` gives them - a caller's scan ends on its first error
    /// (`.map_while(Result::ok)`, the checks crate's `regex_scans`).
    pub fn captures_iter<'r, 't>(
        &'r self,
        text: &'t str,
    ) -> impl Iterator<Item = Result<Captures<'t>, Error>> + use<'r, 't> {
        self.on(text)
            .into_iter()
            .flat_map(move |r| r.captures_iter(text))
    }

    /// Every match, in order, as `Regex::find_iter` gives them - a caller's scan ends on its first error.
    pub fn find_iter<'r, 't>(
        &'r self,
        text: &'t str,
    ) -> impl Iterator<Item = Result<Match<'t>, Error>> + use<'r, 't> {
        self.on(text)
            .into_iter()
            .flat_map(move |r| r.find_iter(text))
    }

    /// `text` with every match replaced.
    pub fn replace_all<'t, R: Replacer>(&self, text: &'t str, rep: R) -> Cow<'t, str> {
        self.on(text)
            .map_or(Cow::Borrowed(text), |r| r.replace_all(text, rep))
    }

    /// `text` with its first match replaced.
    pub fn replace<'t, R: Replacer>(&self, text: &'t str, rep: R) -> Cow<'t, str> {
        self.on(text)
            .map_or(Cow::Borrowed(text), |r| r.replace(text, rep))
    }
}

/// Every pattern `build` has built in this process, in order, in a test build (451 T97): a pattern is built once a process, so a
/// test counts what a command builds in a process of its own (`tree/tests/builds.rs`).
#[cfg(test)]
pub(crate) static BUILT: std::sync::Mutex<Vec<String>> = std::sync::Mutex::new(Vec::new());

/// `pattern` compiled with no step limit: `Regex::new`'s answer, as a pattern the source spells out or reads at run time.
///
/// # Errors
/// The pattern's own syntax error, as `Regex::new` gives it.
#[expect(
    clippy::result_large_err,
    reason = "`Regex::new`'s own signature, which every caller already handles"
)]
pub fn build(pattern: &str) -> Result<Regex, Error> {
    #[cfg(test)]
    BUILT
        .lock()
        .unwrap_or_else(std::sync::PoisonError::into_inner)
        .push(pattern.to_owned());
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
    use super::{build, builder, Lazy};

    static DIGITS: Lazy = Lazy::new(
        |t| t.contains(|c: char| c.is_ascii_digit()),
        || build(r"(\d)(\d)?").unwrap(),
    );

    /// A gated pattern answers as its `Regex` on a text its gate lets through, and "no match" on one it rules out, each method alike.
    #[test]
    fn a_lazy_pattern_answers_as_its_regex_and_no_match_where_its_gate_rules_out() {
        assert!(DIGITS.on("ab").is_none() && DIGITS.on("a1").is_some());
        assert!(DIGITS.is_match("a12") && !DIGITS.is_match("ab"));
        let first = DIGITS.captures("x12y3").unwrap();
        assert_eq!((&first[1], &first[2]), ("1", "2"));
        assert!(DIGITS.captures("xy").is_none());
        let all: Vec<String> = DIGITS
            .captures_iter("1a23")
            .map_while(Result::ok)
            .map(|c| c[0].to_owned())
            .collect();
        assert_eq!(all, ["1", "23"]);
        assert!(DIGITS.captures_iter("abc").next().is_none());
        let found: Vec<&str> = DIGITS
            .find_iter("1a23")
            .map_while(Result::ok)
            .map(|m| m.as_str())
            .collect();
        assert_eq!(found, ["1", "23"]);
        assert!(DIGITS.find_iter("abc").next().is_none());
        assert_eq!(DIGITS.replace_all("a1b23", "#"), "a#b#");
        assert_eq!(DIGITS.replace("a1b23", "#"), "a#b23");
        assert_eq!(DIGITS.replace_all("ab", "#"), "ab");
        assert_eq!(DIGITS.replace("ab", "#"), "ab");
        // one made at run time, not in a static's constant evaluation
        let x = Lazy::new(|t| t.contains('x'), || build("x+").unwrap());
        assert!(x.is_match("axxb") && !x.is_match("ab"));
    }

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
