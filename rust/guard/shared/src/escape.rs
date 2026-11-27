//! The escape rule (`scripts/hooks/lib/hm_escape.py`, features 169 and 170): a guard is escaped by its token used AS an escape - a
//! trailing `# TOKEN: why`, a bare word, a `TOKEN="why"` prefix - never by a mention in a heredoc, a quoted string, a search
//! pattern or a `for ... in` word list; and an escape names a reason of two words and eight characters.

use std::sync::LazyLock;

use fancy_regex::Regex;

use super::py_text::{is_space, strip};
use super::shape::{strip_heredocs, strip_quotes};

const SEARCHERS: [&str; 7] = ["grep", "egrep", "fgrep", "rg", "ack", "ag", "ripgrep"];
const REASON_WORDS: usize = 2;
const REASON_CHARS: usize = 8;

static FOR_IN: LazyLock<Regex> = LazyLock::new(|| {
    crate::regex::build(r"\bfor\s+\w+\s+in\b[^;\n]*(?:;|\n|$)").expect("the for pattern")
});
static SEGMENT: LazyLock<Regex> =
    LazyLock::new(|| crate::regex::build(r";|\|\||\||&&|\n").expect("the segment pattern"));
static ASSIGN: LazyLock<Regex> = LazyLock::new(|| {
    crate::regex::build(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$").expect("the assignment pattern")
});
static QUOTED_REASON: LazyLock<Regex> = LazyLock::new(|| {
    crate::regex::build(r#"^\s*(["'])(.*?)\1"#).expect("the quoted reason pattern")
});

/// The reason given for `token`'s escape in `text`, or "" (`escape_reason`): `TOKEN: why` to the end of its line, `TOKEN="why"`,
/// `TOKEN='why'` or `TOKEN=why`.
///
/// # Panics
///
/// Never: the token is escaped before it is built into the pattern.
#[must_use]
pub fn reason(text: &str, token: &str) -> String {
    let pattern = format!(r"{}(\s*[:=]|\s|$)(.*)", fancy_regex::escape(token));
    let Ok(Some(m)) = crate::regex::build(&pattern)
        .expect("the token pattern")
        .captures(text)
    else {
        return String::new();
    };
    let (sep, rest) = (
        m.get(1).map_or("", |g| g.as_str()).trim(),
        m.get(2).map_or("", |g| g.as_str()),
    );
    if let Ok(Some(q)) = QUOTED_REASON.captures(rest) {
        return q.get(2).map_or("", |g| g.as_str()).trim().to_owned();
    }
    if sep == "=" {
        return rest
            .split_whitespace()
            .next()
            .unwrap_or("")
            .trim_matches(['"', '\''])
            .to_owned();
    }
    rest.split('\n')
        .next()
        .unwrap_or("")
        .trim()
        .trim_matches(['"', '\''])
        .to_owned()
}

/// Does `why` clear the floor - eight characters and two words, a hyphen or a slash splitting words (`reason_is_enough`)?
///
/// The words are counted as `re.split(r"[\s\-/]+", why.strip())` counts its pieces - one more than the runs of separators, an empty
/// piece at either end counted - with Python's whitespace, which holds `\x1c`-`\x1f` where the regex crate's `\s` does not (feature 449
/// T129: the reason floor's command, `l7r-gate escape reason-ok`, is held to `hm_escape.py`'s).
#[must_use]
pub fn enough(why: &str) -> bool {
    let separates = |c: char| is_space(c) || c == '-' || c == '/';
    let mut words = 1;
    let mut in_run = false;
    for c in strip(why).chars() {
        if separates(c) && !in_run {
            words += 1;
        }
        in_run = separates(c);
    }
    why.chars().count() >= REASON_CHARS && words >= REASON_WORDS
}

/// Did the session put `token` in `cmd` as an escape, not merely mention it (`escape_used`)?
#[must_use]
pub fn used(cmd: &str, token: &str) -> bool {
    // NO TOKEN, NO PATTERN (`guardlog.sh`'s own shortcut, 2026-09-27): the cleaning only deletes text or inserts a space or quotes,
    // none of which can complete a token, so a token absent from the command is absent from its cleaned form
    if !cmd.contains(token) {
        return false;
    }
    let clean = strip_quotes(&strip_heredocs(cmd));
    drop_search_segments(&FOR_IN.replace_all(&clean, " ")).contains(token)
}

/// `clean` with every search segment's pattern dropped - what a command looks for is not what it does (`drop_search_segments`).
#[must_use]
pub fn drop_search_segments(clean: &str) -> String {
    let kept: Vec<&str> = SEGMENT
        .split(clean)
        .map_while(Result::ok)
        .map(|seg| {
            let head = seg
                .split_whitespace()
                .filter(|w| !ASSIGN.is_match(w).unwrap_or(false))
                .find(|w| !["sudo", "command", "git", "time", "env"].contains(w))
                .unwrap_or("");
            let base = head.rsplit('/').next().unwrap_or(head);
            if SEARCHERS.contains(&base) {
                seg.split_once('#').map_or("", |(_, after)| after)
            } else {
                seg
            }
        })
        .collect();
    kept.join(" ")
}

/// What an `*_OK` token in a command does (`guardlog.sh`'s `escape_or_refuse`, feature 170).
#[derive(Debug, PartialEq, Eq)]
pub enum Escape {
    /// The token is not used: the guard carries on.
    None,
    /// Used with a reason of two words and eight characters: the guard stands aside, the reason recorded.
    Escaped(String),
    /// Used with no reason, or too short a one: refused, since the reason is the session's and no tool can supply it.
    Refused(String),
}

/// Whether `cmd` escapes with `token`, and on what reason.
#[must_use]
pub fn escape_or_refuse(cmd: &str, token: &str) -> Escape {
    if !used(cmd, token) {
        return Escape::None;
    }
    let why = reason(cmd, token);
    if enough(&why) {
        return Escape::Escaped(why);
    }
    Escape::Refused(no_reason(token))
}

/// The refusal of `token` used with no reason, or too short a one. WHY this short (451 T475): the 543-character wording failed
/// message-check BREVITY; the reader needs the token, the bar and the form, and the form is the `TOKEN="<why>"` the guards' own
/// refusals print (the GM's bar, 2026-08-30, feature 170).
fn no_reason(token: &str) -> String {
    format!(
        "BLOCKED: {token} with no reason given. Give one where the token is, two words or more \
         and eight characters; `make audit` shows it:\n\n    {token}=\"<why this case is legitimate>\"\n"
    )
}

#[cfg(test)]
mod tests {
    use super::{drop_search_segments, enough, reason, used};

    #[test]
    fn a_reason_is_read_in_every_form_the_repository_writes() {
        assert_eq!(
            reason("make x  # MEASURE_OK: a batch close here", "MEASURE_OK"),
            "a batch close here"
        );
        assert_eq!(
            reason(r#"MEASURE_OK="the record needs it" make x"#, "MEASURE_OK"),
            "the record needs it"
        );
        assert_eq!(reason("PAIR_OK='two words' make x", "PAIR_OK"), "two words");
        assert_eq!(reason("PAIR_OK=because make x", "PAIR_OK"), "because");
        assert_eq!(reason("make x MEASURE_OK", "MEASURE_OK"), "");
        assert_eq!(reason("make x", "MEASURE_OK"), "");
    }

    #[test]
    fn a_reason_needs_two_words_and_eight_characters_a_hyphen_splitting() {
        assert!(enough("CI is down") && enough("read-only") && enough("a/b-cdefg"));
        assert!(!enough("required") && !enough("ok") && !enough("because"));
        // Python's whitespace splits words, and a separator at either end makes an empty word, as `re.split` does
        assert!(enough("abcd\x1cefgh") && enough("-abcdefgh") && enough(" abcdefgh-"));
        assert!(!enough(" abcdefgh "));
    }

    #[test]
    fn a_mention_is_not_an_escape() {
        assert!(used("make x  # MEASURE_OK: why", "MEASURE_OK"));
        assert!(!used(
            r#"git commit -m "MEASURE_OK is a token""#,
            "MEASURE_OK"
        ));
        assert!(!used("cat <<EOF\nMEASURE_OK\nEOF", "MEASURE_OK"));
        assert!(!used("grep -n MEASURE_OK Makefile", "MEASURE_OK"));
        assert!(used("grep -n x Makefile  # MEASURE_OK: why", "MEASURE_OK"));
        assert!(!used(
            "for t in MEASURE_OK PAIR_OK; do echo $t; done",
            "MEASURE_OK"
        ));
        assert_eq!(
            drop_search_segments("FOO=1 sudo /usr/bin/rg x && ls"),
            "  ls"
        );
    }

    #[test]
    fn an_escape_stands_aside_with_its_reason_and_refuses_without() {
        use super::{escape_or_refuse, Escape};
        assert_eq!(escape_or_refuse("make done", "GATE_OK"), Escape::None);
        assert_eq!(
            escape_or_refuse("make done  # GATE_OK: the files all ran", "GATE_OK"),
            Escape::Escaped("the files all ran".to_owned())
        );
        assert!(
            matches!(escape_or_refuse("make done  # GATE_OK: ok", "GATE_OK"), Escape::Refused(w) if w.contains("GATE_OK with no reason given"))
        );
    }

    /// The refusal says the token, that a reason of two words is owed and the form to give it, in about 230 characters (451 T475:
    /// at 543 it failed message-check BREVITY, key ebf269213127bfc4); the form is the `TOKEN="<why>"` the guards' own refusals print.
    #[test]
    fn the_no_reason_refusal_names_the_token_the_bar_and_the_form_briefly() {
        use super::{escape_or_refuse, no_reason, Escape};
        let w = no_reason("GATE_OK");
        let refused = escape_or_refuse("make done GATE_OK", "GATE_OK");
        assert_eq!(refused, Escape::Refused(w.clone()));
        let (length, form) = (w.chars().count(), w.contains("GATE_OK=\"<why"));
        assert!(length <= 260 && form && w.contains("two words or more"));
        assert!(!w.contains("# GATE_OK:") && !w.contains("GM 2026-08-30"));
    }
}
