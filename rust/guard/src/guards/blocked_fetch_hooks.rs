//! `blocked-fetch-hooks` (feature 312, FR-002, FR-017, FR-018; ported from the shell of the same name and `lib/hm_fetch.py`, feature 449 T039): A
//! BLOCKED DOMAIN IS NEVER FETCHED (the GM, 2026-10-02: *"if we can literally block ourselves from even checking Grokopedia, that's good"*). The
//! Python routes ask `record/blocked.py`; this covers what Python never sees - an agent's `WebFetch`, a shell fetch, a make fetch target before it
//! starts. Every other `WebFetch` or shell fetch is an attempt on the clone's log, and the URL's earlier attempts come back as context. A mention is
//! not a fetch. There is no escape, deliberately: a domain leaves the list only by the GM's edit of `research/blocked-domains.json`.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

use crate::guards::finished_run_hooks::runs::realpath;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::attempts;
use crate::shared::blocked::{blocked, domains, refusal, Rule};
use crate::shared::checks;
use crate::shared::cited_url::url_id;
use crate::shared::listed;
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "blocked-fetch-hooks",
    events: &["PreToolUse"],
    matcher: "WebFetch|Bash",
    decide,
};

/// CONVENTION: how much of what was sought an attempt keeps (`SOUGHT_CHARS`).
const SOUGHT_CHARS: usize = 300;

fn re(pattern: &str) -> Regex {
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FETCHER: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?:^|[\s;&|(`$])(?:curl|wget|lynx|w3m|xh|https?)\s|python3?\s+-m\s+urllib")
});
/// The make targets that fetch, read by the one make detector (feature 451 D1 - its own pattern took `echo make archive` for one).
const MAKE_FETCH: [&str; 6] = [
    "source-pages",
    "archive",
    "archive-sources",
    "reserve",
    "source-outcome",
    "quote-verbatim",
];
static URL: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?i)(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s'"<>)]*)?"#));
static HEREDOC: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?ms)<<-?\s*(['"]?)(\w+)\1[^\n]*\n.*?^\s*\2\s*$"#));
static HTTP_URL: LazyLock<Regex> = LazyLock::new(|| re(r#"(?i)https?://[^\s'"<>)]+"#));

/// What this guard needs from outside the call.
pub(crate) struct Ctx {
    pub(crate) here: PathBuf,
    pub(crate) tree: PathBuf,
}

/// The list: a missing file is an empty list, and a list that cannot be trusted is None (the loader's refusal, under which every fetch
/// passed) - the record's one reader, `shared::blocked` (feature 449 T144).
fn rules(tree: &Path) -> Option<Vec<Rule>> {
    domains(&tree.join("research")).ok()
}

/// `cmd` with each heredoc gone: a fetch named only in a body is a script's text, refused if blocked yet never logged as an attempt.
fn sans_heredocs(cmd: &str) -> String {
    let (mut out, mut from) = (String::new(), 0);
    for m in HEREDOC.find_iter(cmd).map_while(Result::ok) {
        out.push_str(&cmd[from..m.start()]);
        from = m.end();
    }
    out + &cmd[from..]
}

fn all(pattern: &Regex, cmd: &str) -> Vec<String> {
    pattern
        .find_iter(cmd)
        .map_while(Result::ok)
        .map(|m| m.as_str().to_owned())
        .collect()
}

/// A call's fetch: its URLs, what was sought, whether the guard records it.
struct Fetch {
    urls: Vec<String>,
    sought: String,
    record: bool,
}

fn found(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

fn fetch_of(event: &Event) -> Option<Fetch> {
    let input = event.input.get("tool_input")?;
    if event.tool() == "WebFetch" {
        return Some(Fetch {
            urls: vec![field(input, "url").to_owned()],
            sought: field(input, "prompt").trim().to_owned(),
            record: true,
        });
    }
    if event.tool() != "Bash" {
        return None;
    }
    let cmd = field(input, "command");
    let maker = crate::shared::make::invoked(cmd)
        .iter()
        .any(|t| MAKE_FETCH.contains(&t.as_str()));
    let fetcher = found(&FETCHER, cmd);
    if !(fetcher || maker) {
        return None;
    }
    let mut urls = if maker {
        Vec::new()
    } else {
        all(&HTTP_URL, cmd)
    };
    if urls.is_empty() {
        urls = all(&URL, cmd);
    }
    // As the shell will fetch them: a `;` or `&` ending the command is not the URL's, and a URL built from a shell variable is no page anyone can open.
    let urls = urls
        .iter()
        .filter(|u| !u.contains('$'))
        .map(|u| u.trim_end_matches([';', '&', '|']).to_owned())
        .collect();
    Some(Fetch {
        urls,
        sought: cmd.trim().to_owned(),
        record: fetcher && !maker && found(&FETCHER, &sans_heredocs(cmd)),
    })
}

/// The session clone a command runs in; None for the mirror and anything outside a clone.
fn clone_of(cwd: &str, here: &Path) -> Option<PathBuf> {
    let p = realpath(&here.join(cwd));
    p.ancestors()
        .find(|d| {
            d.parent()
                .and_then(Path::file_name)
                .is_some_and(|n| n == ".clones")
                && d.join(".git").exists()
        })
        .map(Path::to_path_buf)
}

/// Whether the source archive holds a row for the URL, by the archive's own id (`shared::cited_url`, feature 449 T144: this restatement
/// had dropped `hm_fetch.archived`'s unescaping).
fn archived(root: &Path, url: &str) -> bool {
    let uid = url_id(url);
    root.join("research/archive")
        .join(&uid[..2])
        .join(format!("{uid}.json"))
        .is_file()
}

/// Each URL's earlier attempts, the attempts written: `shared::attempts::seen` in process (feature 449 T145, where it ran `attempts.py` by
/// path, T039 decision (c)); a log it cannot read answers nothing, as the Python's failure did.
fn earlier(
    root: &Path,
    urls: &[String],
    fetch: &Fetch,
    route: &str,
    ctx: &Ctx,
) -> Option<Vec<Value>> {
    let kept: String = fetch.sought.chars().take(SOUGHT_CHARS).collect();
    let sought = if kept.is_empty() {
        "(no prompt)"
    } else {
        &kept
    };
    attempts::seen(
        root,
        urls,
        sought,
        route,
        fetch.record,
        &ctx.tree.join("research"),
    )
    .ok()
}

pub(crate) fn judge(event: &Event, session: &Session, ctx: &Ctx) -> Vec<Answer> {
    let Some(fetch) = fetch_of(event) else {
        return Vec::new();
    };
    let Some(list) = rules(&ctx.tree) else {
        return Vec::new();
    };
    let tool = event.tool();
    if let Some((url, rule)) = fetch
        .urls
        .iter()
        .find_map(|u| Some((u, blocked(u, &list)?)))
    {
        let input = event.input.get("tool_input");
        let shown: String = input
            .map_or("", |t| field(t, "command"))
            .chars()
            .take(200)
            .collect();
        log::fire(
            "blocked-fetch",
            "blocked",
            &shown,
            "blocked-domain",
            &event.input,
            session,
        );
        return vec![Answer::Refuse(format!(
            "BLOCKED: {}",
            refusal(url, rule, &format!("this {tool}"))
        ))];
    }
    let urls: Vec<String> = fetch
        .urls
        .iter()
        .filter(|u| {
            if tool == "Bash" {
                u.starts_with("http")
            } else {
                !u.is_empty()
            }
        })
        .cloned()
        .collect();
    let Some(root) = clone_of(field(&event.input, "cwd"), &ctx.here).filter(|_| !urls.is_empty())
    else {
        return Vec::new();
    };
    let Some(reports) = earlier(&root, &urls, &fetch, &tool.to_lowercase(), ctx) else {
        return Vec::new();
    };
    let mut blocks = Vec::new();
    for (url, report) in urls.iter().zip(reports) {
        let said: Vec<String> = report
            .get("lines")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
            .map(str::to_owned)
            .collect();
        let mut block = attempts_said(url, &said);
        if archived(&root, field(&report, "plain")) {
            if !block.is_empty() {
                block.push('\n');
            }
            let _ = write!(block, "archive: a copy of {url} is archived - read it with `make archive-find URL='{url}'` before the web");
        }
        if !block.is_empty() {
            blocks.push(block);
        }
    }
    if blocks.is_empty() {
        return Vec::new();
    }
    // one URL's said, every one's kept (451 T170: a command fetching several URLs said every one's)
    let rest = if blocks.len() > 1 {
        listed::kept(&checks::common_dir(&root), &blocks)
    } else {
        String::new()
    };
    let said = if rest.is_empty() {
        blocks.join("\n")
    } else {
        format!(
            "{}\nand {} more URL(s)' attempts: `{rest}`",
            blocks[0],
            blocks.len() - 1
        )
    };
    vec![Answer::Notice(said)]
}

/// One URL's attempts as the notice says them: its head and the filter's verdict, then its first attempt and `make attempts` for
/// every one (451 T170: one URL's 30-odd attempts reached a builder at 6,077 characters, 2026-11-23).
pub(crate) fn attempts_said(url: &str, said: &[String]) -> String {
    let heads = 1 + usize::from(
        said.get(1)
            .is_some_and(|l| l.starts_with("  filter verdict:")),
    );
    let (head, tried) = said.split_at(heads.min(said.len()));
    let mut out = head.to_vec();
    // 451 T177 (message-check): the head says what an attempt's line holds, since a line read bare (`Q unknown: unknown`) is cryptic
    if let Some(first) = out.first_mut() {
        *first = first.replacen(
            " earlier attempt(s):",
            " earlier attempt(s) (date Q question: outcome - what was sought):",
            1,
        );
    }
    if !tried.is_empty() {
        out.push(listed::capped_n(
            tried,
            1,
            "  ",
            &format!("make attempts URL='{url}'"),
        ));
    }
    out.join("\n")
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.clone(), PathBuf::from);
    judge(event, session, &Ctx { here, tree })
}

#[cfg(test)]
mod tests;
