//! `blocked-fetch-hooks` (feature 312, FR-002, FR-017, FR-018; ported from the shell of the same name and `lib/hm_fetch.py`, feature 449 T039): A
//! BLOCKED DOMAIN IS NEVER FETCHED (the GM, 2026-10-02: *"if we can literally block ourselves from even checking Grokopedia, that's good"*). The
//! Python routes ask `record/blocked.py`; this covers what Python never sees - an agent's `WebFetch`, a shell fetch, a make fetch target before it
//! starts. Every other `WebFetch` or shell fetch is an attempt on the clone's log, and the URL's earlier attempts come back as context. A mention is
//! not a fetch. There is no escape, deliberately: a domain leaves the list only by the GM's edit of `research/blocked-domains.json`.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::Duration;

use fancy_regex::Regex;
use serde_json::Value;

use crate::guards::finished_run_hooks::runs::realpath;
use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::sha256;
use crate::shared::state::field;
use crate::shared::tool::ask_within;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "blocked-fetch-hooks",
    events: &["PreToolUse"],
    matcher: "WebFetch|Bash",
    decide,
};

const LIST: &str = "blocked-domains.json";
/// CONVENTION: how much of what was sought an attempt keeps (`SOUGHT_CHARS`).
const SOUGHT_CHARS: usize = 300;
/// CONVENTION: under the 15 s the shell guard's settings entry gave it; a hung log read costs the fetch its context and nothing else.
const ASK_LIMIT: Duration = Duration::from_secs(10);

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static FETCHER: LazyLock<Regex> = LazyLock::new(|| {
    re(r"(?:^|[\s;&|(`$])(?:curl|wget|lynx|w3m|xh|https?)\s|python3?\s+-m\s+urllib")
});
static MAKE_FETCH: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?:^|[\s;&|(])make\s+(?:-[Cs]\s*\S+\s+)*(?:source-pages|archive|archive-sources|reserve|source-outcome|quote-verbatim)\b",
    )
});
static URL: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?i)(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s'"<>)]*)?"#));
static HEREDOC: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?ms)<<-?\s*(['"]?)(\w+)\1[^\n]*\n.*?^\s*\2\s*$"#));
static HTTP_URL: LazyLock<Regex> = LazyLock::new(|| re(r#"(?i)https?://[^\s'"<>)]+"#));
static SCHEME: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)^[a-z][a-z0-9+.-]*://"));

/// One entry of the blocked list.
struct Rule {
    domain: String,
    reason: String,
    approved: String,
}

/// What this guard needs from outside the call.
pub(crate) struct Ctx<'a> {
    pub(crate) here: PathBuf,
    pub(crate) tree: PathBuf,
    pub(crate) python: &'a str,
}

fn rule_of(raw: &Value) -> Option<Rule> {
    let approved = raw.get("approved")?;
    let (domain, reason) = (field(raw, "domain"), field(raw, "reason"));
    let (date, words) = (field(approved, "date"), field(approved, "words"));
    [domain, reason, date, words]
        .iter()
        .all(|f| !f.is_empty())
        .then(|| Rule {
            domain: domain.to_lowercase().trim_matches('.').to_owned(),
            reason: reason.to_owned(),
            approved: format!("{date}: {words}"),
        })
}

/// The list: a missing file is an empty list, and a list that cannot be trusted is None (the loader's refusal, under which every fetch passed).
fn rules(tree: &Path) -> Option<Vec<Rule>> {
    let Ok(text) = std::fs::read_to_string(tree.join("research").join(LIST)) else {
        return Some(Vec::new());
    };
    let data: Value = serde_json::from_str(&text).ok()?;
    data.get("domains")
        .and_then(Value::as_array)
        .map_or(&[][..], Vec::as_slice)
        .iter()
        .map(rule_of)
        .collect()
}

/// The URL's host, lower-cased; a URL written without its scheme is read as https.
fn host(url: &str) -> String {
    let u = url.trim();
    let rest = SCHEME.find(u).ok().flatten().map_or(u, |m| &u[m.end()..]);
    let authority = rest.split(['/', '?', '#']).next().unwrap_or("");
    let at = authority.rsplit('@').next().unwrap_or("");
    let name = match at.strip_prefix('[') {
        Some(inner) => inner.split(']').next().unwrap_or(""),
        None => at.split(':').next().unwrap_or(""),
    };
    name.to_lowercase().trim_matches(['.', '[', ']']).to_owned()
}

/// The rule a URL falls under: its host is the domain or a subdomain, never a name that merely ends with the same letters.
fn blocked<'r>(url: &str, list: &'r [Rule]) -> Option<&'r Rule> {
    let h = host(url);
    list.iter()
        .find(|r| h == r.domain || h.ends_with(&format!(".{}", r.domain)))
}

/// `cmd` with each heredoc gone: a fetch named only in a body is a script's text, refused if blocked yet never logged as an attempt.
fn sans_heredocs(cmd: &str) -> String {
    let (mut out, mut from) = (String::new(), 0);
    for m in HEREDOC.find_iter(cmd).flatten() {
        out.push_str(&cmd[from..m.start()]);
        from = m.end();
    }
    out + &cmd[from..]
}

fn all(pattern: &Regex, cmd: &str) -> Vec<String> {
    pattern
        .find_iter(cmd)
        .flatten()
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
    let (fetcher, maker) = (found(&FETCHER, cmd), found(&MAKE_FETCH, cmd));
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

/// Whether the source archive holds a row for the URL, its entities already decoded (`record/archive.py:clean`, restated).
fn archived(root: &Path, plain: &str) -> bool {
    let mut clean = plain.split('#').next().unwrap_or("");
    loop {
        let close = clean.matches(')').count() > clean.matches('(').count();
        if clean.ends_with(['.', ',', ';', ':']) || (clean.ends_with(')') && close) {
            clean = &clean[..clean.len() - 1];
        } else {
            break;
        }
    }
    let uid = sha256::hex(clean.as_bytes());
    root.join("research/archive")
        .join(&uid[..2])
        .join(format!("{}.json", &uid[..12]))
        .is_file()
}

/// Each URL's earlier attempts, the attempts written: `attempts.py` by path (T039 decision (c)), one process a fetch.
fn earlier(
    root: &Path,
    urls: &[String],
    fetch: &Fetch,
    route: &str,
    ctx: &Ctx,
) -> Option<Vec<Value>> {
    let tool = ctx.tree.join("scripts/record/attempts.py");
    let (tool, at) = (tool.to_string_lossy(), root.to_string_lossy());
    let kept: String = fetch.sought.chars().take(SOUGHT_CHARS).collect();
    let sought = format!(
        "--sought={}",
        if kept.is_empty() {
            "(no prompt)"
        } else {
            &kept
        }
    );
    let mut args = vec![
        tool.as_ref(),
        "seen",
        "--root",
        at.as_ref(),
        sought.as_str(),
        "--route",
        route,
    ];
    if fetch.record {
        args.push("--record");
    }
    args.push("--");
    args.extend(urls.iter().map(String::as_str));
    serde_json::from_str(&ask_within(root, ctx.python, &args, ASK_LIMIT).out).ok()
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
            "BLOCKED: this {tool} refused: {url} is on the blocked list ({LIST}: {} - {}; approved {}). Find the same fact on another page; a blocked site is never read, cited or recorded.",
            rule.domain, rule.reason, rule.approved
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
    let mut lines = Vec::new();
    for (url, report) in urls.iter().zip(reports) {
        let said = report.get("lines").and_then(Value::as_array);
        lines.extend(
            said.into_iter()
                .flatten()
                .filter_map(Value::as_str)
                .map(str::to_owned),
        );
        if archived(&root, field(&report, "plain")) {
            lines.push(format!("archive: a copy of {url} is archived - read it with `make archive-find URL='{url}'` before the web"));
        }
    }
    if lines.is_empty() {
        return Vec::new();
    }
    vec![Answer::Notice(lines.join("\n"))]
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or_else(|_| here.clone(), PathBuf::from);
    judge(
        event,
        session,
        &Ctx {
            here,
            tree,
            python: "python3",
        },
    )
}

#[cfg(test)]
mod tests;
