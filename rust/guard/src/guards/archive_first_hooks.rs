//! `archive-first-hooks` (feature 376 FR-006; ported from the shell of the same name and `lib/hm_archive_first.py`, feature 449 T030): THE FIRST
//! WEBFETCH OF A PAGE THE SOURCE ARCHIVE ALREADY HOLDS IS REFUSED WITH THE ARCHIVED TEXT'S PATH (the GM, 2026-10-10: "search our existing research
//! findings prior to going out and doing new research"). The same URL fetched again by the same actor passes: the actor has seen the
//! archived copy and wants the live page.

use std::io::Write;
use std::path::{Path, PathBuf};

use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::sha256::hex;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "archive-first-hooks",
    events: &["PreToolUse"],
    matcher: "WebFetch",
    decide,
};

/// A decoded character reference, for a URL's `&amp;` and its kin (`html.unescape`, for what a URL carries).
fn unescape(url: &str) -> String {
    let named = [
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", "\""),
        ("&#39;", "'"),
        ("&#x27;", "'"),
    ];
    named
        .iter()
        .fold(url.to_owned(), |text, (from, to)| text.replace(from, to))
}

/// A URL as the archive's manifest ids it (`sources._cited`, the one rule).
pub(crate) fn cited(url: &str) -> String {
    let whole = unescape(url);
    let mut text = whole.split('#').next().unwrap_or("").to_owned();
    while text.ends_with(['.', ',', ';', ':'])
        || (text.ends_with(')') && text.matches(')').count() > text.matches('(').count())
    {
        text.pop();
    }
    text
}

/// The archived text's path and its capture date, where the archive holds readable text of `url`.
pub(crate) fn held(url: &str, root: &Path, store: Option<&str>) -> Option<(String, String)> {
    let mirror = if root
        .parent()
        .and_then(Path::file_name)
        .is_some_and(|n| n == ".clones")
    {
        root.parent()?.parent()?
    } else {
        root
    };
    let store = store.map_or_else(|| mirror.join(".specify/source-archive"), PathBuf::from);
    let uid: String = hex(cited(url).as_bytes()).chars().take(12).collect();
    let row: Value = serde_json::from_str(
        &std::fs::read_to_string(
            root.join("research/archive")
                .join(&uid[..2])
                .join(format!("{uid}.json")),
        )
        .ok()?,
    )
    .ok()?;
    let text = store.join(row.get("path")?.as_str()?).join("text.txt");
    let captured: String = field(&row, "captured").chars().take(10).collect();
    (std::fs::metadata(&text).ok()?.len() > 0)
        .then(|| (text.to_string_lossy().into_owned(), captured))
}

/// Has this actor been refused this URL already, so this fetch is the deliberate second? Records it if not.
fn seen_before(state: &Path, actor: &str, url: &str) -> bool {
    let _ = std::fs::create_dir_all(state);
    let name: String = actor
        .chars()
        .map(|c| {
            if c.is_alphanumeric() || "_.-".contains(c) {
                c
            } else {
                '_'
            }
        })
        .take(120)
        .collect();
    let path = state.join(format!("{name}.txt"));
    if std::fs::read_to_string(&path).is_ok_and(|t| t.lines().any(|l| l == url)) {
        return true;
    }
    if let Ok(mut f) = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
    {
        let _ = writeln!(f, "{url}");
    }
    false
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let here = std::env::current_dir().unwrap_or_default();
    let state = std::env::var("L7R_ARCHIVE_FIRST_STATE")
        .unwrap_or_else(|_| "/tmp/l7r-archive-first".to_owned());
    judge(
        event,
        session,
        &here,
        Path::new(&state),
        std::env::var("L7R_ARCHIVE_STORE").ok().as_deref(),
    )
}

pub(crate) fn judge(
    event: &Event,
    session: &Session,
    here: &Path,
    state: &Path,
    store: Option<&str>,
) -> Vec<Answer> {
    let url = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "url"));
    if event.tool() != "WebFetch" || !(url.starts_with("http://") || url.starts_with("https://")) {
        return Vec::new();
    }
    let root = here
        .ancestors()
        .find(|d| d.join(".git").exists())
        .unwrap_or(here);
    let Some((text, when)) = held(url, root, store) else {
        return Vec::new();
    };
    let agent = Some(field(&event.input, "agent_id"))
        .filter(|a| !a.is_empty())
        .unwrap_or("main");
    let actor = format!("{}.{agent}", field(&event.input, "session_id"));
    if seen_before(state, &actor, url) {
        return Vec::new();
    }
    log::fire(
        "archive-first",
        "blocked",
        "first-fetch",
        "archived-page",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "\n\u{1b}[1mThe source archive already holds this page (captured {when}) - read it first:\u{1b}[0m\n  {text}\n\n\
Read that file (its readable text; a PDF's extracted). It is exact where a fetch gives a summary.\n\
If you need the LIVE page - is the link still public, has it changed - fetch the same URL again: the second\n\
fetch passes. (The GM, 2026-10-10: look at what we have before going out to the web.)\n"
    ))]
}

#[cfg(test)]
mod tests;
