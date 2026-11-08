//! The shell's shape (`scripts/hooks/lib/hm_shape.py`): a heredoc body and a quoted string are a command's payload, never a command,
//! so both are blanked before a guard matches a command's words. The patterns are the Python's, verbatim (research R8).

use std::sync::LazyLock;

use fancy_regex::Regex;

static HEREDOC: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?s)<<-?\s*['"]?(\w+)['"]?\n.*?\n\s*\1\b"#).expect("the heredoc pattern")
});
static QUOTED: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?s)(?<!-c )(?<!-c\t)(["'])(?:\\.|(?!\1).)*\1"#).expect("the quoted pattern")
});

/// `cmd` with each heredoc's body replaced by ` <<BODY ` (`_strip_heredocs`).
#[must_use]
pub fn strip_heredocs(cmd: &str) -> String {
    HEREDOC.replace_all(cmd, " <<BODY ").into_owned()
}

/// `cmd` with each quoted string blanked to its two quote marks - but the one after `-c`, which an interpreter runs
/// (`_strip_quotes`).
#[must_use]
pub fn strip_quotes(cmd: &str) -> String {
    QUOTED.replace_all(cmd, "$1$1").into_owned()
}

#[cfg(test)]
mod tests {
    use super::{strip_heredocs, strip_quotes};

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
