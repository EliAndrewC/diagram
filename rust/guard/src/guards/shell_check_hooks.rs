//! `shell-check-hooks` (feature 236; ported from the shell of the same name and `lib/hm_shell.py`, feature 449 T035): WHAT A BASH COMMAND WOULD DO WRONG, DECIDED
//! BEFORE IT RUNS. Four rules, each measured before it was written: it does not parse, a backtick span that would run, a `git commit -m` that needs a heredoc, a
//! co-author address that is not ours. A `-m` whose message is unambiguous is rewritten into a quoted `-F -` heredoc (the GM, 2026-10-02: "I do indeed want that git
//! commit rewrite"). `SHELL_CHECK_OK` with a reason is the escape.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::Duration;

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::shape::{executing_backticks, strip_heredocs};
use crate::shared::state::field;
use crate::shared::tool::ask_within;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "shell-check-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

const CO_AUTHOR_ADDRESS: &str = "noreply@anthropic.com";
/// CONVENTION: the parse's limit, as `hm_shell.py` gave it; a parse that hangs refuses nothing.
const PARSE_LIMIT: Duration = Duration::from_secs(10);
/// CONVENTION: the largest `-F <file>` message read, as `hm_shell.py` read it.
const MESSAGE_FILE_BYTES: u64 = 200_000;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

fn hit(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

static ASSIGNED: LazyLock<Regex> = LazyLock::new(|| re(r"^\w+="));
static BUNDLED_M: LazyLock<Regex> = LazyLock::new(|| re(r"^-[a-zA-Z]*m$"));
static GLUED_M: LazyLock<Regex> = LazyLock::new(|| re(r"^-[a-zA-Z]*m."));
static HEREDOC_BODY: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?sm)<<-?\s*['"]?\w+['"]?\n(.*?)\n\s*\w+\s*$"#));
static CO_AUTHOR: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?im)^\s*co-authored-by\s*:\s*(.+?)\s*$"));
static ADDRESS: LazyLock<Regex> = LazyLock::new(|| re(r"<([^>]+)>"));

/// One shell word, kept with the raw text it was written as: `-m "a "b" c"` parses into one good word, which is the failure.
#[derive(Clone, Debug, Default)]
struct Word {
    value: String,
    raw: String,
    chunks: usize,
    quoted: bool,
}

/// `cmd` split at unquoted separators into segments of words.
fn segments(cmd: &str) -> Vec<Vec<Word>> {
    let chars: Vec<char> = cmd.chars().collect();
    let n = chars.len();
    let mut out: Vec<Vec<Word>> = vec![Vec::new()];
    let (mut word, mut started) = (Word::default(), false);
    let mut i = 0;
    while i < n {
        let ch = chars[i];
        if matches!(ch, ' ' | '\t' | ';' | '&' | '|' | '\n') {
            if started {
                if let Some(last) = out.last_mut() {
                    last.push(std::mem::take(&mut word));
                }
                started = false;
            }
            if !matches!(ch, ' ' | '\t') && out.last().is_some_and(|s| !s.is_empty()) {
                out.push(Vec::new());
            }
            i += 1;
            continue;
        }
        started = true;
        i = take_piece(&chars, i, &mut word);
    }
    if started {
        if let Some(last) = out.last_mut() {
            last.push(word);
        }
    }
    out.retain(|s| !s.is_empty());
    out
}

fn text_of(chars: &[char]) -> String {
    chars.iter().collect()
}

/// One piece of a word at `i`: an escape, a quoted chunk or a plain character. The index after it.
fn take_piece(chars: &[char], i: usize, word: &mut Word) -> usize {
    let n = chars.len();
    let ch = chars[i];
    if ch == '\\' && i + 1 < n {
        word.value.push(chars[i + 1]);
        word.raw.push_str(&text_of(&chars[i..i + 2]));
        return i + 2;
    }
    if ch == '\'' {
        let j = chars[i + 1..]
            .iter()
            .position(|c| *c == '\'')
            .map_or(n, |p| i + 1 + p);
        word.value.push_str(&text_of(&chars[i + 1..j]));
        word.raw.push_str(&text_of(&chars[i..(j + 1).min(n)]));
        word.chunks += 1;
        word.quoted = true;
        return j + 1;
    }
    if ch == '"' {
        let mut j = i + 1;
        while j < n && chars[j] != '"' {
            if chars[j] == '\\' && j + 1 < n {
                word.value.push(chars[j + 1]); // `\"` inside a double-quoted string IS a quote character
                j += 2;
                continue;
            }
            word.value.push(chars[j]);
            j += 1;
        }
        word.raw.push_str(&text_of(&chars[i..(j + 1).min(n)]));
        word.chunks += 1;
        word.quoted = true;
        return j + 1;
    }
    word.value.push(ch);
    word.raw.push(ch);
    i + 1
}

/// The parser's own message when bash cannot parse `cmd`: `-O extglob` is the parse the tool performs (research R6).
fn parse_error(cmd: &str) -> Option<String> {
    let said = ask_within(
        Path::new("/"),
        "bash",
        &["-O", "extglob", "-n", "-c", cmd],
        PARSE_LIMIT,
    );
    parse_refusal(said.code, said.err.trim())
}

/// A parse that failed is refused with bash's own words; a parse that could not run refuses nothing.
fn parse_refusal(code: i32, err: &str) -> Option<String> {
    (code > 0).then(|| {
        if err.is_empty() {
            format!("bash refused to parse the command (exit {code})")
        } else {
            err.to_owned()
        }
    })
}

fn backtick_problem(cmd: &str) -> Option<String> {
    let spans = executing_backticks(cmd, false);
    if spans.is_empty() {
        return None;
    }
    let shown: Vec<&str> = spans.iter().take(3).map(String::as_str).collect();
    let more = if spans.len() > 3 {
        format!(" (and {} more)", spans.len() - 3)
    } else {
        String::new()
    };
    Some(format!(
        "a backtick span that bash will EXECUTE: {}{more}",
        shown.join(", ")
    ))
}

fn is_git_commit(seg: &[Word]) -> bool {
    let words: Vec<&str> = seg
        .iter()
        .map(|w| w.value.as_str())
        .filter(|v| !v.split(' ').next().unwrap_or("").contains('=') || !hit(&ASSIGNED, v))
        .collect();
    let head: Vec<&str> = words
        .into_iter()
        .filter(|w| !["sudo", "time", "env"].contains(w))
        .collect();
    let Some(first) = head.first() else {
        return false;
    };
    if Path::new(first).file_name().is_none_or(|n| n != "git") {
        return false;
    }
    head[1..]
        .iter()
        .find(|w| !w.starts_with('-'))
        .is_some_and(|w| *w == "commit")
}

fn dash_m_words(seg: &[Word]) -> Vec<Word> {
    let (mut out, mut take_next) = (Vec::new(), false);
    for w in seg {
        if take_next {
            out.push(w.clone());
            take_next = false;
        } else if w.value == "-m" || w.value == "--message" || hit(&BUNDLED_M, &w.value) {
            take_next = true;
        } else if let Some(rest) = w.value.strip_prefix("--message=") {
            out.push(Word {
                value: rest.to_owned(),
                raw: w
                    .raw
                    .split_once('=')
                    .map_or(w.raw.clone(), |(_, r)| r.to_owned()),
                ..w.clone()
            });
        } else if hit(&GLUED_M, &w.value) && !w.value.starts_with("--") {
            let rest = w.value.split_once('m').map_or("", |(_, r)| r);
            out.push(Word {
                value: rest.to_owned(),
                ..w.clone()
            });
        }
    }
    out
}

fn commit_dash_m_problem(cmd: &str) -> Option<String> {
    for seg in segments(&strip_heredocs(cmd))
        .iter()
        .filter(|s| is_git_commit(s))
    {
        let ms = dash_m_words(seg);
        if ms.len() > 1 {
            return Some(format!("{} separate -m messages", ms.len()));
        }
        for w in &ms {
            if w.value.contains('\n') {
                return Some("a newline inside a -m message".to_owned());
            }
            if w.value.contains('"') {
                return Some("a double quote inside a -m message".to_owned());
            }
            if w.chunks > 1 {
                let shown: String = w.raw.chars().take(60).collect();
                return Some(format!("a -m message assembled from several quoted pieces ({shown}) - the shell closes the first quote early, so git receives a message nobody wrote"));
            }
        }
    }
    None
}

/// The word's value is exactly what its one quoted piece says.
fn literal(w: &Word) -> bool {
    if w.chunks != 1 || w.raw.chars().count() < 2 {
        return false;
    }
    let single = w.raw.starts_with('\'') && w.raw.ends_with('\'');
    let double =
        w.raw.starts_with('"') && w.raw.ends_with('"') && !w.raw.contains(['$', '`', '\\']);
    single || double
}

/// (the flag as written, its message) of each `-m`, or None for a shape not rewritten.
fn message_pairs(seg: &[Word]) -> Option<Vec<(String, Word)>> {
    let writes_file = |w: &Word| {
        w.value == "-F"
            || w.value == "--file"
            || w.value.starts_with("--file=")
            || w.value.starts_with("--message=")
    };
    if seg.iter().any(writes_file) {
        return None;
    }
    let (mut pairs, mut take) = (Vec::new(), None::<String>);
    for w in seg {
        if let Some(flag) = take.take() {
            pairs.push((flag, w.clone()));
        } else if w.value == "-m" || w.value == "--message" || hit(&BUNDLED_M, &w.value) {
            take = Some(w.raw.clone());
        } else if hit(&GLUED_M, &w.value) && !w.value.starts_with("--") {
            return None;
        }
    }
    (!pairs.is_empty() && take.is_none() && pairs.iter().all(|(_, w)| literal(w))).then_some(pairs)
}

/// The command with its `-m` messages moved into a quoted `-F -` heredoc, or None when that cannot be done exactly.
fn commit_dash_m_rewrite(cmd: &str) -> Option<String> {
    if cmd.contains("<<") {
        return None;
    }
    let all = segments(cmd);
    let commits: Vec<&Vec<Word>> = all.iter().filter(|s| is_git_commit(s)).collect();
    let [seg] = commits[..] else {
        return None;
    };
    let pairs = message_pairs(seg)?;
    let mut out = cmd.to_owned();
    let mut first = None;
    for (flag, w) in &pairs {
        let pattern = re(&format!(
            r"{}[ \t]+{}",
            fancy_regex::escape(flag),
            fancy_regex::escape(&w.raw)
        ));
        let found: Vec<(usize, usize)> = pattern
            .find_iter(&out)
            .flatten()
            .map(|m| (m.start(), m.end()))
            .collect();
        let [(start, end)] = found[..] else {
            return None;
        };
        let keep = if flag.starts_with('-') && !flag.starts_with("--") && flag.len() > 2 {
            format!("{} ", &flag[..flag.len() - 1])
        } else {
            String::new()
        };
        if first.is_none() {
            out = format!("{}{keep}-F - <<'@@HEREDOC@@'{}", &out[..start], &out[end..]);
            first = Some(start);
        } else {
            let extra = if keep.is_empty() {
                String::new()
            } else {
                format!(" {}", keep.trim())
            };
            out = format!(
                "{}{extra}{}",
                out[..start].trim_end_matches([' ', '\t']),
                &out[end..]
            );
        }
    }
    let body = pairs
        .iter()
        .map(|(_, w)| w.value.as_str())
        .collect::<Vec<_>>()
        .join("\n\n");
    let mut delim = "EOF".to_owned();
    while body.split('\n').any(|l| l == delim) {
        delim.push('_');
    }
    let out = out.replacen("@@HEREDOC@@", &delim, 1);
    let tail = format!("\n{body}\n{delim}");
    let out = match out[first?..].find('\n') {
        None => out + &tail,
        Some(at) => {
            let nl = first? + at;
            format!("{}{tail}{}", &out[..nl], &out[nl..])
        }
    };
    (parse_error(&out).is_none()
        && commit_dash_m_problem(&out).is_none()
        && backtick_problem(&out).is_none())
    .then_some(out)
}

/// A message file's text, if it is a small file.
fn file_text(path: &Path) -> Option<String> {
    let meta = std::fs::metadata(path).ok()?;
    if !meta.is_file() || meta.len() >= MESSAGE_FILE_BYTES {
        return None;
    }
    Some(String::from_utf8_lossy(&std::fs::read(path).ok()?).into_owned())
}

/// Every text that could carry a trailer: `-m`, `--trailer`, `-F -` (the heredoc) and `-F <file>`.
fn messages(cmd: &str, base: &Path) -> Vec<String> {
    let mut texts = Vec::new();
    for seg in segments(&strip_heredocs(cmd))
        .iter()
        .filter(|s| is_git_commit(s))
    {
        texts.extend(dash_m_words(seg).into_iter().map(|w| w.value));
        let mut take = "";
        for w in seg {
            if take == "trailer" {
                texts.push(w.value.clone());
                take = "";
            } else if take == "file" {
                take = "";
                if w.value == "-" {
                    texts.extend(
                        HEREDOC_BODY
                            .captures_iter(cmd)
                            .flatten()
                            .filter_map(|m| Some(m.get(1)?.as_str().to_owned())),
                    );
                } else {
                    texts.extend(file_text(&base.join(&w.value)));
                }
            } else if w.value == "--trailer" {
                take = "trailer";
            } else if let Some(rest) = w.value.strip_prefix("--trailer=") {
                texts.push(rest.to_owned());
            } else if w.value == "-F" || w.value == "--file" {
                take = "file";
            } else if let Some(rest) = w.value.strip_prefix("--file=") {
                texts.extend(file_text(Path::new(rest)));
            }
        }
    }
    texts
}

fn coauthor_problem(cmd: &str, base: &Path) -> Option<String> {
    for text in messages(cmd, base) {
        for m in CO_AUTHOR.captures_iter(&text).flatten() {
            let line = m.get(1).map_or("", |g| g.as_str());
            let inner = ADDRESS.captures(line).ok().flatten();
            let named = inner
                .as_ref()
                .and_then(|c| c.get(1))
                .map_or(line, |g| g.as_str());
            let address = named.trim().to_lowercase();
            if address != CO_AUTHOR_ADDRESS {
                return Some(format!("a co-author trailer addressed to '{address}'"));
            }
        }
    }
    None
}

/// (rule, message) for the first rule `cmd` breaks, or None.
pub(crate) fn verdict(cmd: &str, base: &Path) -> Option<(&'static str, String)> {
    if let Some(err) = parse_error(cmd) {
        return Some(("parse", format!("the command does not parse:\n\n{err}\n\nBash refuses it before it runs, so this round trip buys nothing. Fix the quoting - a message or a document goes in a quoted heredoc (`<<'EOF'`), where nothing in it is shell grammar.")));
    }
    if let Some(bad) = backtick_problem(cmd) {
        return Some(("executing-backtick", format!("{bad}.\n\nInside double quotes, and in an unquoted `<<EOF` body, backticks are COMMAND SUBSTITUTION: bash runs what is between them and puts the output in their place, so the text you meant to write is corrupted and something runs that you did not ask for. Write a code span in single quotes or in a quoted heredoc (`<<'EOF'`); write a deliberate substitution as `$(...)`, which is what this project uses everywhere.")));
    }
    if let Some(bad) = commit_dash_m_problem(cmd) {
        return Some(("commit-dash-m", format!("{bad}.\n\nUse the heredoc form, whose body is literal:\n\n    git commit -F - <<'EOF'\n    <your message, quotes and newlines and all>\n    EOF\n\nThe delimiter is QUOTED (`<<'EOF'`, not `<<EOF`) so nothing in the message is expanded or executed. This is a refusal rather than a rewrite because the broken form parses cleanly into the WRONG message.")));
    }
    let bad = coauthor_problem(cmd, base)?;
    Some(("coauthor-address", format!("{bad}.\n\nThe co-author address is <{CO_AUTHOR_ADDRESS}>. A placeholder address reached main once through an `||` fallback and the history cannot be rewritten to take it out. Other trailers (`Claude-Session:`) are fine.")))
}

fn refusal(rule: &str, message: &str) -> String {
    format!(
        "BLOCKED: {message}\n\nThis is caught here because it is cheap here: the same mistake found by running the\ncommand costs a failed command, a model turn reading the failure, and a second attempt.\n(rust/guard/src/guards/shell_check_hooks.rs, rule \"{rule}\"; feature 236, the GM: \"reject it early\")\n\nIf this fired on correct work, that is a defect in the guard worth fixing rather than\nworking around - the escape is SHELL_CHECK_OK with a reason, and it is recorded:\n\n    <your command>  # SHELL_CHECK_OK: <why this case is legitimate>"
    )
}

/// A command of plain words alone (no quote, separator, bracket, redirect or newline, and no reserved word first): none of the rules can fire and `bash -n` has nothing to
/// find, so it is not started (T052: 3.0 ms of a plain Bash call).
fn plain_words(cmd: &str) -> bool {
    const RESERVED: [&str; 16] = [
        "if", "then", "elif", "else", "fi", "for", "while", "until", "do", "done", "case", "esac",
        "select", "function", "in", "time",
    ];
    cmd.chars()
        .all(|c| c.is_ascii_alphanumeric() || " /._-=:+,@%".contains(c))
        && !cmd
            .split_whitespace()
            .next()
            .is_some_and(|w| RESERVED.contains(&w))
}

pub(crate) fn judge(event: &Event, session: &Session, here: PathBuf) -> Vec<Answer> {
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    let cmd = field(input, "command");
    if cmd.is_empty() {
        return Vec::new();
    }
    let shown: String = cmd.chars().take(200).collect();
    let fire = |kind: &str, detail: &str, rule: &str| {
        log::fire("shell-check", kind, detail, rule, &event.input, session);
    };
    match escape_or_refuse(cmd, "SHELL_CHECK_OK") {
        Escape::Escaped(why) => {
            fire("escaped", &why, "shell-check-ok");
            return Vec::new();
        }
        Escape::Refused(text) => {
            fire("blocked", &shown, "SHELL_CHECK_OK-no-reason");
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    if plain_words(cmd) {
        return Vec::new();
    }
    let given = field(&event.input, "cwd");
    let base = if given.is_empty() {
        here
    } else {
        PathBuf::from(given)
    };
    let Some((rule, message)) = verdict(cmd, &base) else {
        return Vec::new();
    };
    // Rewritten when it can be done exactly, and only when the result passes every rule.
    if rule == "commit-dash-m" {
        if let Some(rewritten) = commit_dash_m_rewrite(cmd).filter(|r| verdict(r, &base).is_none())
        {
            fire("rewrote", &shown, "commit-dash-m-heredoc");
            let mut updated = input.clone();
            updated["command"] = Value::String(rewritten);
            return vec![
                Answer::Rewrite(updated),
                Answer::Notice("shell-check: the commit message was moved from -m into a quoted -F - heredoc (same message, same commit).".to_owned()),
            ];
        }
    }
    fire("blocked", &shown, rule);
    vec![Answer::Refuse(refusal(rule, &message))]
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    judge(event, session, std::env::current_dir().unwrap_or_default())
}

#[cfg(test)]
mod tests;
