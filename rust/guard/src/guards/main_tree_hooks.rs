//! `main-tree-hooks` (features 169, 204; ported from `scripts/hooks/main-tree-hooks.sh`, feature 449 T010): A WRITE THAT WOULD LAND
//! IN THE MIRROR IS MOVED TO THE SESSION'S CLONE; ONE THAT NAMES THE MIRROR IS REFUSED. The verdict is `shared::tree::judge`; the
//! clone is resolved only when a write would land in main. `MAIN_TREE_OK` with a reason stands it aside. The history behind the
//! verdict's shape stands in the shell's comments, kept in git history.
//!
//! Plan T010's decisions: (a) `hm_tree.py` is `shared::tree`; (b) the clone comes from the session's facts; (c) the mirror from the
//! work tree's top, cut at `/.clones/`; (d) the messages name this file.

use std::path::{Path, PathBuf};

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tree::{context_line, explain, judge as tree_judge, Verdict};

/// The guard.
pub const GUARD: Guard = Guard {
    name: "main-tree-hooks",
    events: &["PreToolUse"],
    matcher: "Bash",
    decide,
};

/// The mirror for a hook standing in `cwd`: its work tree's top, cut at `/.clones/` (`git rev-parse --show-toplevel`).
fn mirror(cwd: &Path) -> Option<PathBuf> {
    let top = cwd.ancestors().find(|d| d.join(".git").exists())?;
    let s = top.to_string_lossy();
    Some(PathBuf::from(s.split("/.clones/").next().unwrap_or(&s)))
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    let home = std::env::var("HOME").ok();
    judge(
        event,
        session,
        std::env::current_dir().ok().as_deref(),
        home.as_deref().unwrap_or("/home/agent"),
    )
}

pub(crate) fn judge(
    event: &Event,
    session: &Session,
    here: Option<&Path>,
    home: &str,
) -> Vec<Answer> {
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    if cmd.is_empty() {
        return Vec::new();
    }
    let shown: String = cmd.chars().take(200).collect();
    match escape_or_refuse(cmd, "MAIN_TREE_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "main-tree",
                "escaped",
                &why,
                "main-tree-ok",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            log::fire(
                "main-tree",
                "blocked",
                &shown,
                "MAIN_TREE_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    let Some(main) = here.and_then(mirror) else {
        return Vec::new();
    };
    let main = main.to_string_lossy().into_owned();
    let mut v: Verdict = tree_judge(&event.input, &main, None, home, false);
    if v.verdict == "needs-clone" {
        let clone = session
            .clone_dir()
            .map(|c| c.to_string_lossy().into_owned());
        v = tree_judge(&event.input, &main, clone.as_deref(), home, true);
    }
    let note = |kind: &str, rule: &str| {
        let _ = log::write(&log::Entry {
            guard: "main-tree",
            event: kind,
            detail: &shown,
            rule,
            context: Some(v.context()),
            input: &event.input,
            session_name: &session.name(),
        });
    };
    match v.verdict {
        "allow" => Vec::new(),
        "rewrite" => {
            note("rewrote", "moved-to-clone");
            let mut updated = event.input.get("tool_input").cloned().unwrap_or_default();
            updated["command"] = serde_json::Value::String(v.command.clone().unwrap_or_default());
            vec![
                Answer::Rewrite(updated),
                Answer::Notice(context_line(&v, &main)),
            ]
        }
        _ => {
            note("blocked", v.reason);
            vec![Answer::Refuse(explain(&v, main.trim_end_matches('/')))]
        }
    }
}

#[cfg(test)]
mod tests;
