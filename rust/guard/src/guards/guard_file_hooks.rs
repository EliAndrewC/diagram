//! `guard-file-hooks` (feature 127, layer 3; features 164, 170, 212, 217, 443; ported from the shell of the same name, feature 449 T029): AN EDIT OF A FILE THAT IS A GUARD IS DELIBERATE. It carries
//! `GUARD_EDIT_OK` and a reason, or follows `make guard-edit` within the hour; the root Makefile takes only the second. A recipe comment that would RUN is refused on any Makefile, with no escape: it is a shell
//! fact, not a policy. A Read of a guard file says all this free, before an edit is written.

use std::path::Path;
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard};
use crate::shared::escape::{enough, reason};
use crate::shared::log;
use crate::shared::session::Session;
use crate::shared::shape::executing_backticks;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "guard-file-hooks",
    events: &["PreToolUse"],
    matcher: "Read|Edit|Write|NotebookEdit",
    decide,
};

const TOKEN: &str = "GUARD_EDIT_OK";
/// How long a `make guard-edit` reason stands (`hm_guard_permit.PERMIT_SECONDS`).
const PERMIT_SECONDS: f64 = 3600.0;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

fn hit(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

static READ_GUARD: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(/scripts/[\w-]+-hooks\.sh|/\.claude/settings\.json|/dev/switches\.json|/tests/rolls\.py)$",
    )
});
static SUITE: LazyLock<Regex> = LazyLock::new(|| re(r"/tests/hooks/test-[\w-]+-hooks\.sh$"));
static HOOK_SCRIPT: LazyLock<Regex> = LazyLock::new(|| re(r"/scripts/.*-hooks\.sh$"));
static HELD_SUITE: LazyLock<Regex> = LazyLock::new(|| re(r"/tests/hooks/test-.*-hooks\.sh$"));
static RECIPE_COMMENT: LazyLock<Regex> =
    LazyLock::new(|| re(r#"^\t\s*@?\s*:\s+"((?:[^"\\]|\\.)*)""#));
static UNESCAPED_SUBST: LazyLock<Regex> = LazyLock::new(|| re(r"(?<!\\)\$\$[({]"));

fn git_out(path: &str, arg: &str) -> String {
    let dir = Path::new(path);
    let at = if dir.is_dir() {
        dir
    } else {
        dir.parent().unwrap_or(Path::new("."))
    };
    let text = at.to_string_lossy();
    let shown = if text.is_empty() { "." } else { text.as_ref() };
    ask(Path::new("/"), "git", &["-C", shown, "rev-parse", arg], "")
        .out
        .trim()
        .to_owned()
}

/// Whether `path` is the Makefile at the top of its checkout.
fn root_makefile(path: &str) -> bool {
    path.ends_with("/Makefile")
        && Path::new(path)
            .parent()
            .is_some_and(|p| p.to_string_lossy() == git_out(path, "--show-toplevel"))
}

/// The text a Read of a guard file is told, or None.
pub(crate) fn read_context(path: &str) -> Option<&'static str> {
    let guard = hit(&READ_GUARD, path) || root_makefile(path);
    if !guard || hit(&SUITE, path) {
        return None;
    }
    Some(if path.ends_with("/tests/rolls.py") {
        "This is the ROSTER OF ROLLED HAMLETS, and it is a GUARD file: an edit to it is refused unless the edit itself contains GUARD_EDIT_OK and a short reason. Before adding a row, read constitution VI, THE GATE ROLLS ONLY WHAT THE FLOOR NEEDS: the gate rolls a map only for engine lines no other roll reaches, and the census verdict FAILS a rostered roll with none. Run `make roll-audit` first and point the new row (its audit= field) at the research section recording it; pack the assertion onto a roll already made, make it a unit test, or move the test to tests/soak/ before you add a roll."
    } else if path.ends_with("/Makefile") {
        "This is the root Makefile, a GUARD file. It takes no GUARD_EDIT_OK comment: before editing it, run make guard-edit FILE=Makefile WHY=\"<why this edit is legitimate>\" - the reason goes in the guard log, and belongs in the commit message. Say which you are doing: fixing a guard that fires on correct work, adding a guard or an operation, or making a guard stop blocking something you want (that last one is what the rule exists to catch)."
    } else {
        "This is a GUARD file. An edit to it is refused unless the edit itself contains GUARD_EDIT_OK and a short reason, or make guard-edit FILE=<this file> WHY=\"<reason>\" ran first. Say which you are doing: fixing a guard that fires on correct work, adding a guard or an operation, or making a guard stop blocking something you want (that last one is what the rule exists to catch)."
    })
}

/// (1-based line, the line) of every `: "..."` recipe comment whose string would RUN something.
pub(crate) fn recipe_hazards(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    for (n, line) in text.split('\n').enumerate() {
        let Ok(Some(m)) = RECIPE_COMMENT.captures(line) else {
            continue;
        };
        let body = m.get(1).map_or("", |g| g.as_str());
        if !executing_backticks(body, true).is_empty() || hit(&UNESCAPED_SUBST, body) {
            out.push(format!("{}: {}", n + 1, line.trim()));
        }
    }
    out
}

/// Whether the file is one this guard holds.
fn held(file: &str) -> bool {
    let guarded = file.ends_with("/Makefile")
        || hit(&HOOK_SCRIPT, file)
        || file.ends_with("/.claude/settings.json")
        || file.ends_with("/tests/rolls.py")
        || file.ends_with("/dev/switches.json")
        || file.ends_with("/dev/work-budget.json");
    guarded && !hit(&HELD_SUITE, file)
}

fn now_from(env: Option<String>) -> f64 {
    let seam = env.and_then(|n| n.parse().ok());
    let clock = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0.0, |d| d.as_secs_f64());
    seam.unwrap_or(clock)
}

/// The reason of a live `make guard-edit` permit for this file, or "".
pub(crate) fn permit_reason(file: &str, at: f64) -> String {
    let real = std::fs::canonicalize(file)
        .map_or_else(|_| file.to_owned(), |p| p.to_string_lossy().into_owned());
    let store = git_out(&real, "--absolute-git-dir");
    if store.is_empty() {
        return String::new();
    }
    let text = std::fs::read_to_string(Path::new(&store).join("l7r-guard-permits.jsonl"))
        .unwrap_or_default();
    let rows: Result<Vec<Value>, _> = text
        .lines()
        .filter(|l| !l.trim().is_empty())
        .map(serde_json::from_str)
        .collect();
    let live = |r: &&Value| {
        at - r.get("at").and_then(Value::as_f64).unwrap_or(0.0) < PERMIT_SECONDS
            && field(r, "file") == real
    };
    rows.unwrap_or_default()
        .iter()
        .rev()
        .find(live)
        .map_or_else(String::new, |r| field(r, "reason").to_owned())
}

/// Whether this edit adds a marker to the file.
fn adds_marker(input: &Value, file: &str) -> bool {
    let (old, new) = if input.get("content").is_some() {
        (
            std::fs::read_to_string(file).unwrap_or_default(),
            field(input, "content").to_owned(),
        )
    } else {
        (
            field(input, "old_string").to_owned(),
            field(input, "new_string").to_owned(),
        )
    };
    new.matches(TOKEN).count() > old.matches(TOKEN).count()
}

const MARKER_NO_REASON: &str = "BLOCKED: GUARD_EDIT_OK with no reason given.

The marker is what puts your intent in the diff, where the GM reads it - a bare marker puts
nothing there. Write it the way the rest of the tree does:

    # GUARD_EDIT_OK: <why this edit to a guard is legitimate>

Two words and eight characters is the whole bar (GM 2026-08-30, feature 170).";

const MAKEFILE_MARKER: &str =
    "BLOCKED: this edit adds a GUARD_EDIT_OK comment to the root Makefile, which takes none.

Take the marker out of the text and run this first, then make the same edit:

    make guard-edit FILE=Makefile WHY=\"<why this edit is legitimate>\"

The reason goes in the guard log; put it in the commit message too. (feature 170 amendment 1)";

fn hazard_text(file: &str, found: &[String]) -> String {
    format!(
        "BLOCKED: this edit puts a COMMAND SUBSTITUTION inside a recipe comment of {file}:\n\n{}\n\nA `: \"...\"` recipe comment is a shell string, and a backtick or a $$( inside it RUNS. On 2026-09-07\none such comment naming `make test-full` in backticks ran test-full from inside test-full, 914 levels\ndeep, until the container hit its process limit. Write the name without backticks, or escape them\n(\\` and \\$$( are literal), or use single quotes. There is no escape token for this - it is\na shell fact, not a policy. (rust/guard/src/guards/guard_file_hooks.rs; feature 212)",
        found.join("\n")
    )
}

fn no_marker_text(file: &str) -> String {
    format!(
        "BLOCKED: {file} is a GUARD, not ordinary source.

The guards are what stop an expensive run being started by picking a different command. Weakening
one silently is the only remaining bypass that does not announce itself, so an edit here has to be
deliberate rather than incidental.

If the edit is legitimate - and it often is, these files get maintained like any other - run

    make guard-edit FILE={file} WHY=\"<why this edit is legitimate>\"

and make the same edit again (the root Makefile takes only this), or put GUARD_EDIT_OK in the edit
with a short reason. Either way the reason is recorded; put it in the commit message too.

Before you do, check which of these you are actually doing:
  - fixing a guard that fires on correct work        -> legitimate, and important; say so
  - adding a new guard or a new operation            -> legitimate; say so
  - making a guard stop blocking something you want  -> that is the thing this exists to catch

(rust/guard/src/guards/guard_file_hooks.rs; feature 127)"
    )
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    judge(
        event,
        session,
        now_from(std::env::var("L7R_PERMIT_NOW").ok()),
    )
}

pub(crate) fn judge(event: &Event, session: &Session, at: f64) -> Vec<Answer> {
    let null = Value::Null;
    let input = event.input.get("tool_input").unwrap_or(&null);
    let file = field(input, "file_path");
    let shown: String = file.chars().take(200).collect();
    if event.tool() == "Read" {
        return read_context(file).map_or_else(Vec::new, |context| {
            log::fire(
                "guard-file",
                "reminded",
                &shown,
                "read-reminder",
                &event.input,
                session,
            );
            vec![Answer::Notice(context.to_owned())]
        });
    }
    let body = format!("{}{}", field(input, "new_string"), field(input, "content"));
    let record = |what: &str, detail: &str, rule: &str| {
        log::fire("guard-file", what, detail, rule, &event.input, session);
    };
    let refuse = |rule: &str, text: String| {
        record("blocked", file, rule);
        vec![Answer::Refuse(text)]
    };
    if file.ends_with("/Makefile") || Path::new(file).extension().is_some_and(|e| e == "mk") {
        let found = recipe_hazards(&body);
        if !found.is_empty() {
            return refuse("recipe-comment-substitution", hazard_text(file, &found));
        }
    }
    if !held(file) {
        return Vec::new();
    }
    if root_makefile(
        &std::fs::canonicalize(file)
            .map_or_else(|_| file.to_owned(), |p| p.to_string_lossy().into_owned()),
    ) && adds_marker(input, file)
    {
        return refuse("makefile-marker", MAKEFILE_MARKER.to_owned());
    }
    if body.contains(TOKEN) {
        let why = reason(&body, TOKEN);
        if !enough(&why) {
            return refuse("GUARD_EDIT_OK-no-reason", MARKER_NO_REASON.to_owned());
        }
        record("escaped", &why, "guard-edit-ok");
        return Vec::new();
    }
    let permit = permit_reason(file, at);
    if !permit.is_empty() {
        record("escaped", &permit, "guard-permit");
        return Vec::new();
    }
    refuse("no-marker", no_marker_text(file))
}

#[cfg(test)]
mod tests;
