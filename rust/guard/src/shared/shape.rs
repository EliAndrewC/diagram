//! The shell's shape (`scripts/hooks/lib/hm_shape.py`): a heredoc body and a quoted string are a command's payload, never a command,
//! so both are blanked before a guard matches a command's words. The patterns are the Python's, verbatim (research R8).

use std::sync::LazyLock;

use fancy_regex::Regex;

static HEREDOC: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?s)<<-?\s*['"]?(\w+)['"]?\n.*?\n\s*\1\b"#).expect("the heredoc pattern")
});
static QUOTED_HEREDOC: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?sm)<<-?\s*(?:'(\w+)'|"(\w+)"|\\(\w+))(.*?)^[ \t]*(?:\1|\2|\3)[ \t]*$"#)
        .expect("the quoted heredoc pattern")
});
static UNQUOTED_HEREDOC: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?sm)<<-?\s*([A-Za-z_]\w*)[^\n]*\n(.*?)^[ \t]*\1[ \t]*$")
        .expect("the unquoted heredoc pattern")
});
static BACKTICK_SPAN: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?<!\\)`[^`\n]*(?<!\\)`").expect("the backtick pattern"));
static QUOTED: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?s)(?<!-c )(?<!-c\t)(["'])(?:\\.|(?!\1).)*\1"#).expect("the quoted pattern")
});

/// `cmd` with each heredoc's body replaced by ` <<BODY ` (`_strip_heredocs`).
#[must_use]
pub fn strip_heredocs(cmd: &str) -> String {
    HEREDOC.replace_all(cmd, " <<BODY ").into_owned()
}

/// Every backtick span in `text` that bash would EXECUTE, in order (`hm_shape.executing_backticks`). A span inside single quotes, in a heredoc whose delimiter is quoted,
/// escaped, or after an unquoted `#` does not run; a span in an unquoted heredoc body does, and that body's quote characters are literal. `in_double` starts the walk inside
/// a double-quoted string.
#[must_use]
pub fn executing_backticks(text: &str, in_double: bool) -> Vec<String> {
    let mut spans = Vec::new();
    let (bare, _) = cut(&QUOTED_HEREDOC, text, 0);
    let (rest, bodies) = cut(&UNQUOTED_HEREDOC, &bare, 2);
    for body in &bodies {
        spans.extend(
            BACKTICK_SPAN
                .find_iter(body)
                .flatten()
                .map(|m| m.as_str().to_owned()),
        );
    }
    walk_backticks(&rest, in_double, &mut spans);
    spans
}

/// `cmd` with each quoted string blanked to its two quote marks - but the one after `-c`, which an interpreter runs
/// (`_strip_quotes`).
#[must_use]
pub fn strip_quotes(cmd: &str) -> String {
    QUOTED.replace_all(cmd, "$1$1").into_owned()
}

/// `text` with each match replaced by a space, and each match's group `group`.
fn cut(pattern: &Regex, text: &str, group: usize) -> (String, Vec<String>) {
    let (mut out, mut from, mut groups) = (String::new(), 0, Vec::new());
    for m in pattern.captures_iter(text).flatten() {
        let (start, end) = m.get(0).map_or((from, from), |w| (w.start(), w.end()));
        out.push_str(&text[from..start]);
        out.push(' ');
        from = end;
        groups.extend(m.get(group).map(|g| g.as_str().to_owned()));
    }
    (out + &text[from..], groups)
}

/// The quote walk over text whose heredocs are gone.
fn walk_backticks(text: &str, in_double: bool, spans: &mut Vec<String>) {
    let chars: Vec<char> = text.chars().collect();
    let n = chars.len();
    let (mut sq, mut esc, mut dq) = (false, false, in_double);
    let mut i = 0;
    while i < n {
        let ch = chars[i];
        if esc {
            esc = false;
        } else if ch == '\\' && !sq {
            esc = true;
        } else if sq {
            sq = ch != '\'';
        } else if ch == '\'' && !dq {
            sq = true;
        } else if ch == '"' {
            dq = !dq;
        } else if ch == '#' && !dq && (i == 0 || " \t\n;&|(".contains(chars[i - 1])) {
            i = chars[i..]
                .iter()
                .position(|c| *c == '\n')
                .map_or(n, |p| i + p);
        } else if ch == '`' {
            let close = (i + 1..n).find(|j| chars[*j] == '`' && chars[*j - 1] != '\\');
            if let Some(j) = close {
                spans.push(chars[i..=j].iter().collect());
                i = j;
            }
        }
        i += 1;
    }
}

#[cfg(test)]
mod tests {
    use super::{executing_backticks, strip_heredocs, strip_quotes};

    #[test]
    fn a_backtick_span_runs_where_bash_would_run_it() {
        assert_eq!(executing_backticks("echo \"a `b` c\"", false), ["`b`"]);
        assert_eq!(
            executing_backticks("cat <<EOF\nit's `make done`\nEOF", false),
            ["`make done`"]
        );
        for quiet in [
            "echo 'a `b`'",
            "cat <<'E'\n`b`\nE",
            "cat <<\"E\"\n`b`\nE",
            "cat <<\\E\n`b`\nE",
            "echo \"\\` x\"",
            "ls  # `b`",
            "# `b`",
        ] {
            assert!(executing_backticks(quiet, false).is_empty(), "{quiet}");
        }
        assert_eq!(executing_backticks("a `b` c", true), ["`b`"]);
        assert!(executing_backticks("an ` unclosed", false).is_empty());
        assert_eq!(executing_backticks("ls # `x`\necho `y`", false), ["`y`"]);
    }

    #[test]
    fn a_heredoc_body_and_a_quoted_string_are_blanked_but_a_dash_c_string_is_kept() {
        assert_eq!(
            strip_heredocs("cat <<'EOF'\nmake test\nEOF\necho done"),
            "cat  <<BODY \necho done"
        );
        assert_eq!(
            strip_quotes(r#"grep -E "^(ruff|pytest)=" x"#),
            r#"grep -E "" x"#
        );
        assert_eq!(
            strip_quotes("python3 -c 'import pytest'"),
            "python3 -c 'import pytest'"
        );
        assert_eq!(strip_quotes(r#"echo "a \" b" 'c'"#), r#"echo "" ''"#);
    }
}
