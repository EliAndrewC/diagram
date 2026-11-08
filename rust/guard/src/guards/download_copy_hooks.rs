//! `download-copy-hooks` (feature 313; ported from the shell of the same name, feature 449 T033): A SESSION DOES NOT WRITE THE GM'S COPY OF THE
//! DOWNLOAD LIST. `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` is his working copy, whose boxes he ticks; the canonical list is
//! `research/to-download.md`. `DOWNLOAD_COPY_OK` with a reason that quotes the GM is the escape.

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{escape_or_refuse, Escape};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::state::field;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "download-copy-hooks",
    events: &["PreToolUse"],
    matcher: "Bash|Edit|Write|NotebookEdit",
    decide,
};

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

const COPY: &str = r"(?:/host-l7r-repo/)?academic-sources/TO-DOWNLOAD\.md";

static FILE: LazyLock<Regex> = LazyLock::new(|| re(r"(^|/)academic-sources/TO-DOWNLOAD\.md$"));
static SHAPES: LazyLock<[Regex; 3]> = LazyLock::new(|| {
    [
        re(&format!(
            r#"(?:>>?\s*|sed\s+-i\b[^;|&]*?|tee\s+(?:-a\s+)?|(?:cp|mv|install)\s+(?:-\S+\s+)*\S+\s+)['"]?[\w./-]*{COPY}"#
        )),
        re(&format!(
            r#"{COPY}['"]\s*\)?\s*\)?\s*\.(?:write_text|write_bytes)"#
        )),
        re(&format!(
            r#"open\(\s*['"][\w./-]*{COPY}['"]\s*,\s*['"][wa]"#
        )),
    ]
});

/// What would write the GM's copy, or None.
pub(crate) fn hit(event: &Event) -> Option<String> {
    let input = event.input.get("tool_input")?;
    if ["Write", "Edit", "NotebookEdit"].contains(&event.tool()) {
        let path = field(input, "file_path");
        return FILE
            .is_match(path)
            .unwrap_or(false)
            .then(|| path.to_owned());
    }
    let cmd = field(input, "command");
    SHAPES
        .iter()
        .find_map(|r| r.find(cmd).ok().flatten().map(|m| m.as_str().to_owned()))
}

fn shown(event: &Event) -> String {
    let input = event.input.get("tool_input");
    let text = input.map_or("", |t| {
        Some(field(t, "command"))
            .filter(|c| !c.is_empty())
            .unwrap_or(field(t, "file_path"))
    });
    text.chars().take(200).collect()
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    if !event.input.to_string().contains("TO-DOWNLOAD") {
        return Vec::new();
    }
    let cmd = event
        .input
        .get("tool_input")
        .map_or("", |t| field(t, "command"));
    match escape_or_refuse(cmd, "DOWNLOAD_COPY_OK") {
        Escape::Escaped(why) => {
            log::fire(
                "download-copy",
                "escaped",
                &why,
                "gm-authorized",
                &event.input,
                session,
            );
            return Vec::new();
        }
        Escape::Refused(text) => {
            log::fire(
                "download-copy",
                "blocked",
                &shown(event),
                "DOWNLOAD_COPY_OK-no-reason",
                &event.input,
                session,
            );
            return vec![Answer::Refuse(text)];
        }
        Escape::None => {}
    }
    if hit(event).is_none() {
        return Vec::new();
    }
    log::fire(
        "download-copy",
        "blocked",
        &shown(event),
        "the-gm-s-copy",
        &event.input,
        session,
    );
    vec![Answer::Refuse(
        "BLOCKED: writing the GM's copy of the download list.\n\n\
/host-l7r-repo/academic-sources/TO-DOWNLOAD.md is the GM's working copy: they tick its boxes as they work. The\n\
canonical list is research/to-download.md (feature 313).\n\n  \
- a source only the GM can fetch:   make download-add FILE=<draft.md>   (entries headed \"### NEW. <the work>\",\n                                       appended at the end)\n  \
- the GM said \"ingest\":             make downloads-ingest\n  \
- the GM said \"sync\":               make downloads-sync   (refused while the copy holds marks not ingested)\n\n\
The one escape is a repair the GM asks for in their own words: DOWNLOAD_COPY_OK with a reason that quotes it.\n\
(rust/guard/src/guards/download_copy_hooks.rs; feature 313)"
            .to_owned(),
    )]
}

#[cfg(test)]
mod tests;
