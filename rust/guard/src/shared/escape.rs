//! The escape rule (`scripts/hooks/lib/hm_escape.py`, features 169 and 170): a guard is escaped by its token used AS an escape - a
//! trailing `# TOKEN: why`, a bare word, a `TOKEN="why"` prefix - never by a mention in a heredoc, a quoted string, a search
//! pattern or a `for ... in` word list; and an escape names a reason of two words and eight characters.

use std::sync::LazyLock;

use fancy_regex::Regex;

use super::shape::{strip_heredocs, strip_quotes};

const SEARCHERS: [&str; 7] = ["grep", "egrep", "fgrep", "rg", "ack", "ag", "ripgrep"];
const REASON_WORDS: usize = 2;
const REASON_CHARS: usize = 8;

static FOR_IN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\bfor\s+\w+\s+in\b[^;\n]*(?:;|\n|$)").expect("the for pattern"));
static SEGMENT: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r";|\|\||\||&&|\n").expect("the segment pattern"));
static ASSIGN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$").expect("the assignment pattern"));
static QUOTED_REASON: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r#"^\s*(["'])(.*?)\1"#).expect("the quoted reason pattern"));
static WORDS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[\s\-/]+").expect("the word pattern"));

/// The reason given for `token`'s escape in `text`, or "" (`escape_reason`): `TOKEN: why` to the end of its line, `TOKEN="why"`,
/// `TOKEN='why'` or `TOKEN=why`.
///
/// # Panics
///
/// Never: the token is escaped before it is built into the pattern.
#[must_use]
pub fn reason(text: &str, token: &str) -> String {
    let pattern = format!(r"{}(\s*[:=]|\s|$)(.*)", fancy_regex::escape(token));
    let Ok(Some(m)) = Regex::new(&pattern)
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
#[must_use]
pub fn enough(why: &str) -> bool {
    why.chars().count() >= REASON_CHARS
        && WORDS.split(why.trim()).filter_map(Result::ok).count() >= REASON_WORDS
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
        .filter_map(Result::ok)
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
    Escape::Refused(format!(
        "BLOCKED: {token} with no reason given.\n\n\
         An escape is a workaround, and a workaround nobody can audit is indistinguishable from the\n\
         rule not existing. Say why, in the command, and it ships with it:\n\n    \
         <your command>  # {token}: <why this case is legitimate>\n\n\
         Two words and eight characters is the whole bar - \"CI is down\" clears it. What it stops is a\n\
         bare token and \"{token}: ok\", which record that a rule was bypassed and nothing about why.\n\
         (GM 2026-08-30, feature 170; the reasons are what `make audit` shows you.)\n"
    ))
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
            matches!(escape_or_refuse("make done  # GATE_OK: ok", "GATE_OK"), Escape::Refused(w) if w.contains("GATE_OK: ok"))
        );
    }
}
