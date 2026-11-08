//! `claims-file-hooks` (feature 376 FR-002; ported from the shell of the same name, feature 449 T031): THE RESEARCH CLAIMS SHEET IS CLAIMED AND
//! ASKED THROUGH `make research-claim` AND `make research-claims`, NEVER OPENED BY HAND (the GM, 2026-10-10: any time a process requires editing a
//! potentially large file, it uses tooling to edit it). A read, an edit, or a Bash command that really touches the file is refused; a `git` command
//! and a search that merely names it in its pattern are not. There is no escape: the tool reads every old line and releases any claim.

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "claims-file-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Read|Edit|Write|NotebookEdit",
    decide,
};

const SHEET: &str = "RESEARCH-CLAIMS";

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

static PATH: LazyLock<Regex> =
    LazyLock::new(|| re(r#"(?:^|[\s'"=<>])(?:\S*/)?RESEARCH-CLAIMS\.md(?![\w.-])"#));
static VERB: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?:^|[\s;&|(])(?:cat|head|tail|less|more|sed|awk|grep|egrep|rg|tee|cp|mv|rm|wc|vi|vim|nano|python3?|perl|truncate|touch)\b|>|<|make\s+(?:lines|append)\b",
    )
});
static GIT: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*git\b"));

/// Whether this one piece of a command really touches the sheet: a search's pattern is not the file it searches.
fn piece_touches(piece: &str) -> bool {
    let words: Vec<&str> = piece.split_whitespace().collect();
    let mut text = piece.to_owned();
    if words
        .first()
        .is_some_and(|w| ["grep", "egrep", "rg"].contains(w))
    {
        if let Some(pattern) = words[1..].iter().find(|w| !w.starts_with('-')) {
            text = text.replacen(pattern, " ", 1);
        }
    }
    let rest = PATH.replace_all(&text, " ");
    PATH.is_match(&text).unwrap_or(false)
        && !GIT.is_match(&text).unwrap_or(false)
        && VERB.is_match(&rest).unwrap_or(false)
}

/// The tool that would touch the sheet, or None.
pub(crate) fn hit(event: &Event) -> Option<String> {
    let tool = event.tool();
    let input = event.input.get("tool_input")?;
    if ["Read", "Edit", "Write", "MultiEdit", "NotebookEdit"].contains(&tool) {
        let touches = field(input, "file_path").contains(SHEET)
            || field(input, "notebook_path").contains(SHEET);
        return touches.then(|| tool.to_owned());
    }
    let cmd = field(input, "command");
    let touches = tool == "Bash"
        && cmd
            .split("&&")
            .flat_map(|p| p.split("||"))
            .flat_map(|p| p.split([';', '\n']))
            .any(piece_touches);
    touches.then(|| "Bash".to_owned())
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    if !event.input.to_string().contains(SHEET) {
        return Vec::new();
    }
    let Some(tool) = hit(event) else {
        return Vec::new();
    };
    log::fire(
        "claims-file",
        "blocked",
        &tool,
        "hand-edit-of-claims-sheet",
        &event.input,
        session,
    );
    vec![Answer::Refuse(format!(
        "\n\u{1b}[1mBLOCKED: the research claims sheet is not opened by hand ({tool}).\u{1b}[0m\n\n\
Ask and claim through the tool - it prints only the claims on your questions, and records under a lock:\n  \
make research-claims Q=\"0060 0246\"                        who holds these questions now\n  \
make research-claim Q=\"0060 0246\" FEATURE=<n>             claim them (refused if another session holds one)\n  \
make research-claim Q=\"0060 0246\" FEATURE=<n> STATUS=done  release them when the work is done\n  \
make research-claim Q=0060 FEATURE=<n> RELEASE=<owner> WHY=\"<why it is stale>\"   free a stale claim\n\n\
The GM, 2026-10-10: any time a process requires editing a potentially large file, it uses tooling to edit it.\n\
There is no escape variable: the tool reads every old line and releases any claim, so nothing needs the file.\n"
    ))]
}

#[cfg(test)]
mod tests;
