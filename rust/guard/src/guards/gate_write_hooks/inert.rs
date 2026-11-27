//! THE TEXT THE COMMIT PATTERN READS (451 T531): the command with each heredoc body blanked whose reader is KNOWN not to run it, every
//! other body kept, so a `git commit` only in a body that runs is still held as a commit, failing closed (451 T530's
//! `a_commit_in_a_heredoc_body_or_spelled_in_quotes_is_held`). WHY: T530 held a commit that was only a heredoc's TEXT - a note `cat`
//! writes to a file, a commit's `-F -` message - while a gate ran and the tree had moved, a false refusal; round 2 of its plan review
//! ruled a strip of every body but a shell's unbounded, since a body is run by a shell reading it, a pipe, a substitution, a wrapper,
//! an interpreter or a script a later segment runs.
//!
//! THE METHOD, a closed allowlist, anything outside it kept as at HEAD (the whole command unstripped):
//! - every heredoc parses as bash reads one: `<<`, `<<-`, a word delimiter bare, quoted or `\`-escaped, the body to the first line
//!   that is the delimiter exactly (tabs stripped for `<<-`); a `<<` the parse cannot read, or a second opener on one line, strips
//!   nothing;
//! - each opener stands outside quotes: the text before it, bodies removed, holds an even count of each quote and no backslash;
//! - the command less its bodies and terminators holds no substitution (`$(`, a backtick, `<(`, `>(`) and no variable (`$` then a
//!   name or `{`), and every segment of it (cut at `;`, `&`, `|`, a newline, a parenthesis or a brace) opens with a command of
//!   [`QUIET`] - none of which runs a file or its input - git only with a read or commit subcommand ([`GIT_SUBS`]) and no `-c` or
//!   `--config`: so no later segment runs what a `cat` wrote, by its name, a glob, a variable or an implicit file; `make`, which runs
//!   the repository's recipes, is quiet only beside a `cat` whose file is DATA ([`DATA`], never a program a recipe runs, as a `.rs`
//!   under `make rust-test` or a script is) and named nowhere else in the command; a `>&` redirect is no separator;
//! - a body is blanked only where its reader is `cat` alone, its output one plain file (no `$`, glob, `&`, `/dev/`, `/proc/`, `.git`
//!   or `hooks`), or a `git commit` reading its message from `-F -` or `--file=-`; neither fed from nor into a pipe; and an unquoted
//!   delimiter's body holds no `$(` or backtick, which the shell runs as it expands the body.
//!
//! Measured 2026-11-27 over the `-diagram*` transcripts of the last four days (`t531-scan.py`, each unique Bash command holding
//! `<<`, and `t531-rule.py`, this method in Python over them): 23,311 commands, 153 whose only commit match was in a body; the
//! method frees 4 (a `cat` note or plan append, then `make` or nothing) and holds 149 - every `python3 -` body (about 80), and each
//! `cat` whose command also runs an interpreter (`python3 -c` reading the file it wrote, about 30), names a variable (`cat > $S/f`,
//! 18) or a program `make` runs (`cat >> tests.rs` then `make rust-test`). Those are held as at HEAD: telling a Python program that
//! only reads the file from one that runs it is the unbounded class round 2 ruled out.

/// The commands a segment may open with: none runs a file it is handed, its input, or a program its options name.
const QUIET: [&str; 12] = [
    "cat", "cd", "mkdir", "echo", "printf", "wc", "ls", "head", "tail", "grep", "true", "git",
];

/// The extensions of a file no recipe runs: records, notes and data (a GUESS knob, from the measured shapes' targets).
const DATA: [&str; 8] = [
    ".md", ".json", ".jsonl", ".txt", ".tsv", ".csv", ".html", ".log",
];

/// The git subcommands a segment may run: reads, and the commit and add the pattern judges as commits wherever they stand.
const GIT_SUBS: [&str; 7] = [
    "status",
    "diff",
    "log",
    "show",
    "add",
    "commit",
    "rev-parse",
];

/// One heredoc as the shell reads it: where its opener's `<<` and its delimiter end, its opener line's end, its body and its
/// terminator line's end.
struct Doc {
    at: usize,
    delim_end: usize,
    line_end: usize,
    body: (usize, usize),
    term_end: usize,
    quoted: bool,
}

/// `cmd` with each inert heredoc body blanked; `cmd` itself where any part of the method does not hold.
pub(super) fn text_read(cmd: &str) -> String {
    let Some(docs) = parse(cmd) else {
        return cmd.to_owned();
    };
    let rest = outside(cmd, &docs);
    let Some(make) = quiet(&rest).filter(|_| !docs.is_empty()) else {
        return cmd.to_owned();
    };
    let mut out = String::new();
    let mut pos = 0;
    for d in docs
        .iter()
        .filter(|d| inert(cmd, d, make.then_some(rest.as_str())))
    {
        out.push_str(&cmd[pos..d.body.0]);
        pos = d.body.1;
    }
    out.push_str(&cmd[pos..]);
    out
}

/// Every heredoc of `cmd` in order, None where one cannot be read as the shell reads it or stands inside quotes.
fn parse(cmd: &str) -> Option<Vec<Doc>> {
    let b = cmd.as_bytes();
    let mut docs: Vec<Doc> = Vec::new();
    let mut from = 0;
    while let Some(off) = cmd[from..].find("<<") {
        let at = from + off;
        // a here-string; a `<` before the `<<` cannot be, since each search starts at a line's end
        if b.get(at + 2) == Some(&b'<') {
            return None;
        }
        let mut i = at + 2;
        let dash = b.get(i) == Some(&b'-');
        i += usize::from(dash);
        while matches!(b.get(i), Some(b' ' | b'\t')) {
            i += 1;
        }
        let open = b
            .get(i)
            .copied()
            .filter(|c| matches!(c, b'\'' | b'"' | b'\\'));
        i += usize::from(open.is_some());
        let start = i;
        while b
            .get(i)
            .is_some_and(|c| c.is_ascii_alphanumeric() || *c == b'_')
        {
            i += 1;
        }
        let delim = &cmd[start..i];
        if delim.is_empty() {
            return None;
        }
        if let Some(q @ (b'\'' | b'"')) = open {
            if b.get(i) != Some(&q) {
                return None;
            }
            i += 1;
        }
        let line_end = i + cmd[i..].find('\n')?;
        if cmd[i..line_end].contains("<<") || !balanced(&prefix(cmd, &docs, at)) {
            return None;
        }
        let body0 = line_end + 1;
        let mut k = body0;
        let (body1, term_end) = loop {
            let end = cmd[k..].find('\n').map_or(cmd.len(), |e| k + e);
            let line = &cmd[k..end];
            let line = if dash {
                line.trim_start_matches('\t')
            } else {
                line
            };
            if line == delim {
                break (k, end);
            }
            if end >= cmd.len() {
                return None;
            }
            k = end + 1;
        };
        docs.push(Doc {
            at,
            delim_end: i,
            line_end,
            body: (body0, body1),
            term_end,
            quoted: open.is_some(),
        });
        from = term_end;
    }
    Some(docs)
}

/// `cmd` up to `at`, the bodies and terminators of `docs` before it removed.
fn prefix(cmd: &str, docs: &[Doc], at: usize) -> String {
    outside(&cmd[..at], docs)
}

/// `text` with every body and terminator line of `docs` removed (each lies wholly before `text`'s end or past it).
fn outside(text: &str, docs: &[Doc]) -> String {
    let mut out = String::new();
    let mut pos = 0;
    for d in docs.iter().filter(|d| d.term_end <= text.len()) {
        out.push_str(&text[pos..d.body.0]);
        pos = d.term_end;
    }
    out.push_str(&text[pos..]);
    out
}

/// Whether the text before an opener leaves it outside quotes: an even count of each quote, and no backslash to escape one.
fn balanced(before: &str) -> bool {
    !before.contains('\\')
        && before.matches('\'').count() % 2 == 0
        && before.matches('"').count() % 2 == 0
}

/// Whether the command less its bodies runs nothing a body could be - no substitution, no variable, each segment a [`QUIET`] one
/// or `make` - and, where it is, whether a segment is `make`; None where it is not.
fn quiet(text: &str) -> Option<bool> {
    let b = text.as_bytes();
    let variable = b.windows(2).any(|w| {
        w[0] == b'$' && (w[1].is_ascii_alphabetic() || matches!(w[1], b'_' | b'{' | b'('))
    });
    if variable || ["`", "<(", ">("].iter().any(|s| text.contains(s)) {
        return None;
    }
    let mut make = false;
    // `2>&1` duplicates a stream: no separator, so its `&` is not cut at
    let text = text.replace(">&", "> ");
    text.split(['\n', ';', '&', '|', '(', ')', '{', '}'])
        .map(str::split_whitespace)
        .all(|mut words| match words.next() {
            None => true,
            Some("git") => git_quiet(words),
            Some("make") => {
                make = true;
                true
            }
            Some(head) => QUIET.contains(&head),
        })
        .then_some(make)
}

/// Whether a git segment's words, past `git`, name a [`GIT_SUBS`] subcommand, past `-C <dir>`, and no config of its own.
fn git_quiet<'a>(mut words: impl Iterator<Item = &'a str>) -> bool {
    while let Some(w) = words.next() {
        match w {
            "-C" => {
                words.next();
            }
            _ if w.starts_with('-') => return false,
            sub => {
                let rest: Vec<&str> = words.collect();
                return GIT_SUBS.contains(&sub)
                    && !rest
                        .iter()
                        .any(|w| *w == "-c" || w.starts_with("--config") || w.contains('!'));
            }
        }
    }
    false
}

/// Whether a heredoc's reader is known not to run its body: `cat` to one plain file, or a commit's `-F -` message. `made` is the
/// command less its bodies where it runs `make`, whose `cat` must write a [`DATA`] file named nowhere else in it.
fn inert(cmd: &str, d: &Doc, made: Option<&str>) -> bool {
    let body = &cmd[d.body.0..d.body.1];
    if !d.quoted && (body.contains("$(") || body.contains('`')) {
        return false;
    }
    let line = &cmd[cmd[..d.at].rfind('\n').map_or(0, |n| n + 1)..d.at];
    let cut = line.rfind([';', '&', '|']).map_or(0, |n| n + 1);
    if line[..cut].ends_with('|') && !line[..cut].ends_with("||") {
        return false;
    }
    let rest = &cmd[d.delim_end..d.line_end];
    let rest_cut = rest.find([';', '&', '|']).unwrap_or(rest.len());
    if rest[rest_cut..].starts_with('|') && !rest[rest_cut..].starts_with("||") {
        return false;
    }
    let words: Vec<&str> = line[cut..]
        .split_whitespace()
        .chain(rest[..rest_cut].split_whitespace())
        .collect();
    match words.first() {
        Some(&"cat") => cat_to_file(&words[1..]).is_some_and(|file| {
            made.is_none_or(|rest| {
                let name = file.rsplit('/').next().unwrap_or(file);
                DATA.iter().any(|x| name.ends_with(x)) && rest.matches(name).count() == 1
            })
        }),
        Some(&"git") => {
            words.contains(&"commit")
                && (words
                    .windows(2)
                    .any(|w| w == ["-F", "-"] || w == ["--file", "-"])
                    || words.iter().any(|w| *w == "-F-" || *w == "--file=-"))
        }
        _ => false,
    }
}

/// The plain file `cat`'s words, past its name, redirect its output to, None where they are anything else.
fn cat_to_file<'a>(words: &[&'a str]) -> Option<&'a str> {
    let target = match words {
        [">" | ">>", file] => *file,
        [joined] => joined
            .strip_prefix(">>")
            .or_else(|| joined.strip_prefix('>'))
            .filter(|f| !f.is_empty())?,
        _ => return None,
    };
    (!target.contains(['$', '*', '?', '[', '&', '`', '\'', '"'])
        && !["/dev/", "/proc/"].iter().any(|p| target.starts_with(p))
        && !target.contains(".git")
        && !target.contains("hooks"))
    .then_some(target)
}
