//! `gm-tree-hooks` (feature 429; ported from the shell of the same name and `lib/hm_gm_tree.py`, feature 449 T019): NO WRITE LANDS IN
//! GM-ASSISTANT'S MAIN WORKING TREE FROM A DIAGRAM SESSION. A money session left setting-note edits uncommitted there (2026-10-20,
//! diagram#10), and a dirty main tree refuses every gm-assistant push. Judged: the file a file tool names, and a Bash command's WRITE
//! targets as the main-tree guard's interpreter finds them, never a mention. A gm-assistant clone and the rest of `/host-l7r-repo` are
//! not this guard's business, and git's writes there are repo-safety's. `GM_TREE_OK: <reason>` escapes a Bash call, for the GM's explicit
//! say-so; an edit has no escape, because the compliant route is a clone.

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tree::{classify, normpath, walk};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "gm-tree-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

const TREE: &str = "/host-l7r-repo/gm-assistant";

/// The first path the call would write inside the tree (outside its `.clones/`).
pub(crate) fn offending(event: &Event, tree: &str, home: &str) -> Option<String> {
    let input = event.input.get("tool_input")?;
    if event.tool() != "Bash" {
        let named = Some(field(input, "file_path"))
            .filter(|p| !p.is_empty())
            .unwrap_or(field(input, "notebook_path"));
        let path = named.starts_with('/').then(|| normpath(named));
        return path.filter(|p| classify(Some(p), tree) == "main");
    }
    let cmd = field(input, "command");
    let standing = Some(field(&event.input, "cwd")).filter(|c| !c.is_empty());
    if !cmd.contains("gm-assistant") && !standing.is_some_and(|c| c.starts_with(tree)) {
        return None;
    }
    walk(cmd, standing, tree, home)
        .targets
        .into_iter()
        .find(|t| !t.segment.trim_start().starts_with("git") && t.class == "main")
        .map(|t| t.path.unwrap_or_else(|| tree.to_owned()))
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let tree = std::env::var("GM_TREE_ROOT").unwrap_or_else(|_| TREE.to_owned());
    judge(
        event,
        session,
        &tree,
        &std::env::var("HOME").unwrap_or_default(),
    )
}

pub(crate) fn judge(event: &Event, session: &Session, tree: &str, home: &str) -> Vec<Answer> {
    if !event.input.to_string().contains("gm-assistant") {
        return Vec::new();
    }
    let Some(hit) = offending(event, tree, home) else {
        return Vec::new();
    };
    let input = event.input.get("tool_input");
    let cmd = input.map_or("", |t| field(t, "command"));
    let shown: String = input
        .map_or("", |t| {
            Some(field(t, "command"))
                .filter(|c| !c.is_empty())
                .unwrap_or(field(t, "file_path"))
        })
        .chars()
        .take(200)
        .collect();
    if event.tool() == "Bash" {
        match escape_or_refuse(cmd, "GM_TREE_OK") {
            Escape::Escaped(why) => {
                log::fire(
                    "gm-tree",
                    "escaped",
                    &why,
                    "gm-tree-ok",
                    &event.input,
                    session,
                );
                return Vec::new();
            }
            Escape::Refused(text) => {
                log::fire(
                    "gm-tree",
                    "blocked",
                    &shown,
                    "GM_TREE_OK-no-reason",
                    &event.input,
                    session,
                );
                return vec![Answer::Refuse(text)];
            }
            Escape::None => {}
        }
    }
    log::fire(
        "gm-tree",
        "blocked",
        &shown,
        "write-in-gm-tree",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "BLOCKED: a write into gm-assistant's main working tree ({hit}).\n\
A dirty main tree refuses every gm-assistant push. Make the edit in a gm-assistant clone\n\
(git clone /host-l7r-repo/gm-assistant /host-l7r-repo/gm-assistant/.clones/<name>, commit, its scripts/sync-with-main.sh done),\n\
or hand the wording to gm-assistant on an issue: python3 ~/.claude/hooks/issue_watch.py open EliAndrewC/gm-assistant \"<title>\" < body.md"
    ))]
}

#[cfg(test)]
mod tests;
