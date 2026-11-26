//! How a command word names its program (451 T295): the one reader every guard asks "is this git" (or `rm`, `make`, a wrapper).
//! WHY: each guard read git by its bare name - the walk's `*head == "git"`, a reader's `t == "git"`, a pattern's `git\b` at a command
//! position - so `/usr/bin/git worktree add <clones>/x`, `\git checkout -- f` and `command git rebase` passed the builder-pool, discard
//! and history guards that refuse the bare spelling (measured 2026-11-26: the suites' `spelled` tests, red on that code).
//!
//! A program is named by its word's last path part, past a leading `\` (which skips an alias) and its quotes: `/usr/bin/git`,
//! `\git`, `"git"` and `'/usr/bin/git'` are git, and `/tmp/mygit`, `legit`, `git.sh` and `/tmp/git/run` are not - the name is
//! compared whole. A wrapper's own options are read past (`env -i git`, `sudo -u x git`, `nice -n 5 git`: [`options`]). What it
//! does not read: a name built by the shell (`g\it`, `$GIT`, `$(which git)`) and a program run by another (`xargs git`,
//! `sh -c 'git ...'`).

/// The wrappers a command can stand behind, which a reader of its command word reads past (`tree::HEAD_WRAPPERS`, with `timeout`
/// and its duration).
pub const WRAPPERS: [&str; 10] = [
    "sudo", "nohup", "setsid", "env", "command", "exec", "time", "nice", "builtin", "timeout",
];

/// The pattern text that stands before `program`'s name at a command position: a leading `\` or quote, the path's directories,
/// and a look ahead that the name ends the word (`/tmp/git/run` and `git.sh` are other programs). A pattern reading `git\b`
/// after `before("git")` reads every spelling [`names`] does.
#[must_use]
pub fn before(program: &str) -> String {
    format!(r#"["'\\]*(?:[^\s;&|"'=]*/)?(?={program}(?:["'\s;&|)]|$))"#)
}

/// The pattern text of the wrappers a command can stand behind, each with its options and the space after it, `timeout` with its
/// duration: for a pattern's prefix group, beside its own `VAR=value` words. An option that takes a value is read with it
/// ([`VALUED`]'s letters, for every wrapper alike: a pattern cannot ask which wrapper it follows).
pub const WRAPPER_WORDS: &str = r"(?:\S*/)?(?:sudo|nohup|setsid|env|command|exec|time|nice|builtin)\s+(?:-[ugCDRThpnaS]\s+\S+\s+|-\S+\s+)*|(?:\S*/)?timeout\s+(?:-[ks]\s+\S+\s+|-\S+\s+)*\S+\s+";

/// Each wrapper's options that take the next word as their value (read from each one's manual, 2026-11-26: sudo 1.9, coreutils
/// 9 `env`, `nice` and `timeout`, bash's `exec`); an option written `--name=value` or `-n5` is one word.
const VALUED: [(&str, &[&str]); 5] = [
    (
        "sudo",
        &[
            "-u", "-g", "-C", "-D", "-R", "-T", "-h", "-p", "-U", "--user", "--group", "--chdir",
            "--host", "--prompt",
        ],
    ),
    ("env", &["-u", "-C", "-S", "--unset", "--chdir"]),
    ("nice", &["-n", "--adjustment"]),
    ("timeout", &["-k", "-s", "--kill-after", "--signal"]),
    ("exec", &["-a"]),
];

/// How many of `rest`, the words after `wrapper`, are its own options: each word opening `-`, with the next where the option
/// takes its value there; `--` ends them and is one.
#[must_use]
pub fn options<S: AsRef<str>>(wrapper: &str, rest: &[S]) -> usize {
    let valued = VALUED
        .iter()
        .find(|(w, _)| *w == wrapper)
        .map_or(&[][..], |(_, v)| *v);
    let mut at = 0;
    while let Some(w) = rest.get(at).map(AsRef::as_ref) {
        if !w.starts_with('-') || w == "-" {
            break;
        }
        at += if valued.contains(&w) { 2 } else { 1 };
        if w == "--" {
            break;
        }
    }
    at.min(rest.len())
}

/// The program a command word names: its last path part, a leading `\` and its quotes dropped.
#[must_use]
pub fn name_of(word: &str) -> &str {
    let bare = word.trim_matches(['"', '\'']).trim_start_matches('\\');
    bare.rsplit('/').next().unwrap_or(bare)
}

/// Whether `word` names `program`, however it is spelled.
#[must_use]
pub fn names(word: &str, program: &str) -> bool {
    name_of(word) == program
}

/// `command -v <name>` and `command -V <name>` look a program up and run nothing: `command` is then the command word itself.
#[must_use]
pub fn lookup(wrapper: &str, next: Option<&str>) -> bool {
    wrapper == "command" && matches!(next, Some("-v" | "-V"))
}

/// A `VAR=value` word: a name, then `=`.
fn assignment(word: &str) -> bool {
    word.split_once('=').is_some_and(|(k, _)| {
        !k.is_empty()
            && !k.starts_with(|c: char| c.is_ascii_digit())
            && k.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
    })
}

/// Where the command word stands among a command's `words`: past its `VAR=value` words and its wrappers, `timeout`'s duration
/// with it. `words.len()` for a command of wrappers alone.
#[must_use]
pub fn command_at<S: AsRef<str>>(words: &[S]) -> usize {
    let mut at = 0;
    while let Some(w) = words.get(at).map(AsRef::as_ref) {
        let name = name_of(w);
        if lookup(name, words.get(at + 1).map(AsRef::as_ref)) {
            break;
        }
        if WRAPPERS.contains(&name) {
            at += 1;
            at += options(name, words.get(at..).unwrap_or_default());
            // `timeout`'s duration
            at += usize::from(name == "timeout");
        } else if assignment(w) {
            at += 1;
        } else {
            break;
        }
    }
    at.min(words.len())
}

/// The program a command's head names (`tree::command_head`'s text, or any command's words split at spaces): its command word's
/// name, "" for none.
#[must_use]
pub fn program_of(head: &str) -> &str {
    let words: Vec<&str> = head.split_whitespace().collect();
    words.get(command_at(&words)).map_or("", |w| name_of(w))
}

#[cfg(test)]
mod tests;
