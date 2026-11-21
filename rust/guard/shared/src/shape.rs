//! The shell's shape (`scripts/hooks/lib/hm_shape.py`): a heredoc body and a quoted string are a command's payload, never a command,
//! so both are blanked before a guard matches a command's words. The patterns are the Python's, verbatim (research R8).
//!
//! Each pattern is searched only in a text holding the literal every match of it holds (`shared::regex::Lazy`, 451 T103): `<<` for
//! the three heredoc patterns, a backtick for a span, a `c` and a blank ending the text for an interpreter's `-c`; a quoted string is
//! read by `quoted_spans`, a scan in place of the Python's `QUOTED`. WHY: a hook event is a process of its own, and the strips built
//! their patterns on every Bash start whatever the command held - `HEREDOC`, `QUOTED` and the two heredoc patterns of
//! `executing_backticks` for nearly every one of T93's 9,646 commands, `INTERPRETER_C` for two in three (measured 2026-11-21, the T103
//! plan section's item 4).

use crate::regex::Lazy;

/// Whether a text could open a heredoc: every match of the three heredoc patterns starts `<<`.
fn could_heredoc(text: &str) -> bool {
    text.contains("<<")
}

/// Whether a text could end at an interpreter's `-c`: every match of `INTERPRETER_C` ends the text with `c` and one or more blanks
/// (`c[ \t]+$`, `$` the text's end with no `m` flag), so the text less its trailing blanks is shorter and ends in `c`.
fn could_end_at_dash_c(text: &str) -> bool {
    let bare = text.trim_end_matches([' ', '\t']);
    bare.len() < text.len() && bare.ends_with('c')
}

// A heredoc: its opener's words after the delimiter (`cat <<'EOF' > f`, `python3 - <<'PY' | tee o`) kept as group 2, since they are
// the command's own; the Python's pattern took only a delimiter that ended its line, so such a body was read as commands (feature
// 451 T15, T30 folded in: `cat <<'EOF' > f` holding `make static &` read as a detached make).
static HEREDOC: Lazy = Lazy::new(could_heredoc, || {
    crate::regex::build(r#"(?sm)<<-?[ \t]*['"\\]?(\w+)['"]?([^\n]*)\n.*?^[ \t]*\1\b"#)
        .expect("the heredoc pattern")
});
static QUOTED_HEREDOC: Lazy = Lazy::new(could_heredoc, || {
    crate::regex::build(r#"(?sm)<<-?\s*(?:'(\w+)'|"(\w+)"|\\(\w+))(.*?)^[ \t]*(?:\1|\2|\3)[ \t]*$"#)
        .expect("the quoted heredoc pattern")
});
static UNQUOTED_HEREDOC: Lazy = Lazy::new(could_heredoc, || {
    crate::regex::build(r"(?sm)<<-?\s*([A-Za-z_]\w*)[^\n]*\n(.*?)^[ \t]*\1[ \t]*$")
        .expect("the unquoted heredoc pattern")
});
static BACKTICK_SPAN: Lazy = Lazy::new(
    |t| t.contains('`'),
    || crate::regex::build(r"(?<!\\)`[^`\n]*(?<!\\)`").expect("the backtick pattern"),
);
// An interpreter's `-c` (its flags joined to it too, `bash -lc`, `sh -ec`) ending the text before a quote: the string after it is
// run. The Python's lookbehind kept the string after any `-c ` (`grep -c "make x &"`, `git -c 'a=b'`) and blanked one after
// `-lc` (feature 451 T15, T30 folded in).
static INTERPRETER_C: Lazy = Lazy::new(could_end_at_dash_c, || {
    crate::regex::build(
        r"(?:^|[\s/;&|(])(?:(?:ba|da|z|k)?sh|python[0-9.]*|pypy[0-9.]*|node|perl|ruby)\s+(?:-[A-Za-z-]*\s+)*-[A-Za-z]*c[ \t]+$",
    )
    .expect("the interpreter pattern")
});

/// `cmd` with each heredoc's body replaced by ` <<BODY `, the opener's words after its delimiter kept (`_strip_heredocs`).
#[must_use]
pub fn strip_heredocs(cmd: &str) -> String {
    HEREDOC.replace_all(cmd, " <<BODY $2").into_owned()
}

/// Whether `before` ends at an interpreter's `-c`, so the quote after it opens a string the interpreter runs; read over its last
/// 64 bytes, which hold any such `-c`, so a long command is not rescanned a quote at a time.
fn run_by_interpreter(before: &str) -> bool {
    let from = (before.len().saturating_sub(64)..=before.len())
        .find(|&k| before.is_char_boundary(k))
        .unwrap_or(0);
    INTERPRETER_C.is_match(&before[from..])
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
                .map_while(Result::ok)
                .map(|m| m.as_str().to_owned()),
        );
    }
    walk_backticks(&rest, in_double, &mut spans);
    spans
}

/// `cmd` with each quoted string blanked to its two quote marks - but the one after an interpreter's `-c`, which it runs, kept with
/// the strings quoted inside it blanked in turn (`_strip_quotes`).
#[must_use]
pub fn strip_quotes(cmd: &str) -> String {
    let (mut out, mut from) = (String::new(), 0);
    for (at, end) in quoted_spans(cmd) {
        let q = &cmd[at..=at];
        out.push_str(&cmd[from..at]);
        out.push_str(q);
        if run_by_interpreter(&cmd[..at]) {
            out.push_str(&strip_quotes(&cmd[at + 1..end]));
        }
        out.push_str(q);
        from = end + 1;
    }
    out + &cmd[from..]
}

/// Every quoted string of `text`, in order, as the Python's `QUOTED` (`(["'])(?:\\.|(?!\1).)*\1`) found them: each its opening and its
/// closing quote's byte. Read in one pass (451 T103): the pattern took a backslash with the character after it, or the backslash
/// alone, so its backtracking search tried 2^n readings of the n backslashes after a quote no later quote of its kind closes - a real
/// command held `no-poll-hooks` past 20 s, killed (measured 2026-11-21, the T103 plan section's Found and left). Its first reading,
/// the one the search returns, takes a backslash with the character after it only where a quote of its kind still stands after the
/// pair (else no reading from there reaches one), a backslash alone else, and closes at the first quote of its kind it meets; a quote
/// nothing after it closes opens nothing. A test holds the two equal on every text to 7 characters over `"`, `'`, `\`, `a`, a newline
/// and `é` (`tests/quotes.rs`).
fn quoted_spans(text: &str) -> Vec<(usize, usize)> {
    let b = text.as_bytes();
    let last = |q: u8| b.iter().rposition(|&c| c == q);
    let (double, single) = (last(b'"'), last(b'\''));
    let (mut spans, mut at) = (Vec::new(), 0);
    while at < b.len() {
        let q = b[at];
        let closer = match q {
            b'"' => double,
            b'\'' => single,
            _ => None,
        };
        let Some(last) = closer.filter(|&l| l > at) else {
            at += 1;
            continue;
        };
        let mut p = at + 1;
        while b[p] != q {
            p += if b[p] == b'\\' && p + 2 <= last { 2 } else { 1 };
        }
        spans.push((at, p));
        at = p + 1;
    }
    spans
}

/// `text` with each match replaced by a space, and each match's group `group`.
fn cut(pattern: &Lazy, text: &str, group: usize) -> (String, Vec<String>) {
    let (mut out, mut from, mut groups) = (String::new(), 0, Vec::new());
    for m in pattern.captures_iter(text).map_while(Result::ok) {
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

/// Python's `shlex.split(piece, comments=True)`, or None for an unclosed quote.
#[must_use]
pub fn shlex(piece: &str) -> Option<Vec<String>> {
    let (mut out, mut word, mut started) = (Vec::new(), String::new(), false);
    let mut chars = piece.chars().peekable();
    let mut quote: Option<char> = None;
    while let Some(c) = chars.next() {
        match quote {
            Some('\'') if c == '\'' => quote = None,
            Some('"') if c == '"' => quote = None,
            Some('"') if c == '\\' => match chars.peek() {
                Some(&n @ ('"' | '\\')) => {
                    word.push(n);
                    chars.next();
                }
                _ => word.push(c),
            },
            Some(_) => word.push(c),
            None => match c {
                '\'' | '"' => (quote, started) = (Some(c), true),
                '\\' => {
                    word.extend(chars.next());
                    started = true;
                }
                '#' => break,
                c if c.is_whitespace() => {
                    if started {
                        out.push(std::mem::take(&mut word));
                        started = false;
                    }
                }
                c => {
                    word.push(c);
                    started = true;
                }
            },
        }
    }
    if quote.is_some() {
        return None;
    }
    if started {
        out.push(word);
    }
    Some(out)
}

#[cfg(test)]
mod tests {
    mod builds;
    mod quotes;

    use super::{executing_backticks, shlex, strip_heredocs, strip_quotes};

    /// Moved here with `shlex` from `discard_hooks` (451 T58).
    #[test]
    fn a_command_is_split_as_shlex_splits_it() {
        let words = |s: &str| shlex(s).unwrap();
        assert_eq!(
            words("git  checkout -- 'a b' \"c\\\"d\\x\" e\\ f # note"),
            ["git", "checkout", "--", "a b", "c\"d\\x", "e f"]
        );
        assert_eq!(words("a#b c"), ["a"]);
        assert_eq!(words("'' x"), ["", "x"]);
        assert_eq!(shlex("it's"), None);
        assert_eq!(words(""), Vec::<String>::new());
    }

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

    /// Feature 451 T15 (T30 folded in): a heredoc whose opener line goes on past its delimiter is still a heredoc, the opener's
    /// words kept; a `-c` string is kept only where an interpreter runs it - `bash -lc` too, never `grep -c`.
    #[test]
    fn a_heredoc_with_words_after_it_and_a_dash_c_no_interpreter_runs() {
        assert_eq!(
            strip_heredocs("cat <<'EOF' > /tmp/n.md\nmake static &\nEOF\nls"),
            "cat  <<BODY  > /tmp/n.md\nls"
        );
        assert_eq!(
            strip_heredocs("python3 - <<'PY' | tee o\nmake x\nPY"),
            "python3 -  <<BODY  | tee o"
        );
        assert_eq!(strip_heredocs("cat <<EOF\nEOF"), "cat  <<BODY ");
        assert_eq!(
            strip_quotes(r#"grep -c "make static &" t.jsonl"#),
            r#"grep -c "" t.jsonl"#
        );
        assert_eq!(strip_quotes("git -c 'a=b' log"), "git -c '' log");
        assert_eq!(
            strip_quotes(r#"bash -lc "make x &""#),
            r#"bash -lc "make x &""#
        );
        assert_eq!(
            strip_quotes("/bin/sh -ec 'make x'; zsh -c 'y'"),
            "/bin/sh -ec 'make x'; zsh -c 'y'"
        );
        assert_eq!(
            strip_quotes(r#"python3.12 -c "import x""#),
            r#"python3.12 -c "import x""#
        );
    }
}
