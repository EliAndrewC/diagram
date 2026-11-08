//! `discard-hooks` (feature 133 T33; ported from the shell of the same name, feature 449 T022): A GIT COMMAND THAT WOULD DISCARD
//! UNCOMMITTED WORK DOES NOT RUN UNANNOUNCED. A session typed `git checkout -- ways.py` into a command as a NOTE, and the shell ran it:
//! the task's working diff was gone (GM 2026-08-27). Only a checkout or restore whose target is a PATH, and only a path git says is
//! actually modified; a clean file, a branch switch and a `--staged`-only restore pass. While `MERGE_HEAD` exists `--ours`/`--theirs` is
//! conflict resolution, not a discard (the GM's ruling, feature 165). `DISCARD_OK` with a reason is the escape.

use std::path::Path;
use std::time::Duration;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::{ask, ask_within};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "discard-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

/// Python's `shlex.split(piece, comments=True)`, or None for an unclosed quote.
pub(crate) fn shlex(piece: &str) -> Option<Vec<String>> {
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

fn is_hash(s: &str) -> bool {
    (7..=40).contains(&s.len()) && s.chars().all(|c| matches!(c, '0'..='9' | 'a'..='f'))
}

fn in_merge(repo: &str) -> bool {
    let gitdir = ask(
        Path::new("."),
        "git",
        &["-C", repo, "rev-parse", "--git-dir"],
        "",
    )
    .out;
    !gitdir.is_empty() && Path::new(repo).join(gitdir).join("MERGE_HEAD").exists()
}

/// The paths this one git invocation would overwrite in the worktree, with the tree it names.
fn targets(piece: &str, cwd: &str) -> Vec<(String, String)> {
    let toks =
        shlex(piece).unwrap_or_else(|| piece.split_whitespace().map(str::to_owned).collect());
    let Some(g) = toks.iter().position(|t| t == "git") else {
        return Vec::new();
    };
    let mut rest = &toks[g + 1..];
    let mut repo = cwd.to_owned();
    while rest.len() >= 2 && (rest[0] == "-C" || rest[0] == "-c") {
        if rest[0] == "-C" {
            repo.clone_from(&rest[1]);
        }
        rest = &rest[2..];
    }
    let Some((sub, args)) = rest.split_first() else {
        return Vec::new();
    };
    let has = |names: &[&str]| args.iter().any(|a| names.contains(&a.as_str()));
    let checkout = sub == "checkout";
    if !(checkout || sub == "restore")
        || (checkout && has(&["-b", "-B", "--branch", "--orphan"]))
        || (!checkout && has(&["--staged"]) && !has(&["--worktree", "-W"]))
        || (has(&["--ours", "--theirs"]) && in_merge(&repo))
    {
        return Vec::new();
    }
    let (mut paths, mut dashes) = (Vec::new(), false);
    for a in args {
        if a == "--" {
            dashes = true;
        } else if dashes || !a.starts_with('-') {
            paths.push(a.as_str());
        }
    }
    if checkout && !dashes {
        // `git checkout X`: a branch or ref switch is fine; a PATH discards
        if paths.len() == 1 && !paths[0].contains('/') && !paths[0].contains('.') && paths[0] != "*"
        {
            return Vec::new();
        }
        if paths.first().is_some_and(|p| *p == "HEAD" || is_hash(p)) {
            paths.remove(0); // `git checkout HEAD -- path` without the dashes
        }
    }
    paths
        .into_iter()
        .map(|p| (repo.clone(), p.to_owned()))
        .collect()
}

/// The modified files the command would discard.
pub(crate) fn dirty(cmd: &str, base: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for piece in cmd
        .split("&&")
        .flat_map(|p| p.split("||"))
        .flat_map(|p| p.split([';', '|']))
    {
        for (repo, path) in targets(piece, base) {
            let said = ask_within(
                Path::new("."),
                "git",
                &["-C", &repo, "status", "--porcelain", "--", &path],
                Duration::from_secs(5),
            );
            for line in said
                .out
                .lines()
                .filter(|l| !l.get(..2).unwrap_or("").trim().is_empty() && l.get(..2) != Some("??"))
            {
                let name = line.get(3..).unwrap_or("").to_owned();
                if !out.contains(&name) {
                    out.push(name);
                }
            }
        }
    }
    out
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let cwd = std::env::current_dir().unwrap_or_default();
    judge(event, session, &cwd.to_string_lossy())
}

pub(crate) fn judge(event: &Event, session: &Session, base: &str) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    if cmd.is_empty() {
        return Vec::new();
    }
    let shown: String = cmd.chars().take(200).collect();
    match escape_or_refuse(cmd, "DISCARD_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "discard",
                "escaped",
                &why,
                "discard-ok",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            log::fire(
                "discard",
                "blocked",
                &shown,
                "DISCARD_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    if !["git checkout", "git restore", "git -C"]
        .iter()
        .any(|g| cmd.contains(g))
    {
        return Vec::new();
    }
    let found = dirty(cmd, base);
    if found.is_empty() {
        return Vec::new();
    }
    log::fire(
        "discard",
        "blocked",
        &shown,
        "would-discard-dirty",
        &event.input,
        session,
    );
    let listed = found
        .iter()
        .map(|p| format!("  {p}"))
        .collect::<Vec<_>>()
        .join("\n");
    vec![Answer::Refuse(format!(
        "BLOCKED (discard): this command would throw away UNCOMMITTED work in:\n{listed}\n\n\
A checkout or restore of a modified file cannot be undone - git keeps no copy of what it\n\
overwrites. On 2026-08-27 (feature 133 T31) a session lost its whole working diff to a\n\
`git checkout -- ways.py` typed into a command as a NOTE, and spent five minutes recovering it from\n\
the transcript; the ten-minute task took thirty-nine.\n\n\
If you mean it: commit first (mid-task commits inside your clone are always fine), or put\n\
DISCARD_OK in the command with a note saying why. If you did not mean it, the command was carrying\n\
text the shell read as an instruction - rewrite it without the checkout.\n\
(rust/guard/src/guards/discard_hooks.rs; feature 133 T33)"
    ))]
}

#[cfg(test)]
mod tests;
