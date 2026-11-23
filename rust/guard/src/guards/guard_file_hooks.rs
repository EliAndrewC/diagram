//! `guard-file-hooks` (feature 127, layer 3; features 164, 170, 212, 217, 443; ported from the shell of the same name, feature 449 T029): AN EDIT OF A FILE THAT IS A GUARD IS DELIBERATE. It carries
//! `GUARD_EDIT_OK` and a reason, or follows `make guard-edit` within the hour; the root Makefile takes only the second. A recipe comment that would RUN is refused on any Makefile, with no escape: it is a shell
//! fact, not a policy. A Read of a guard file says all this free, before an edit is written.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::Value;

use crate::protocol::{Answer, Event, Guard, Reply};
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
    crate::shared::regex::build(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

fn hit(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

static READ_GUARD: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(/scripts/(?:hooks/)?[\w-]+-hooks\.sh|/\.claude/settings\.json|/dev/switches\.json|/tests/rolls\.py)$",
    )
});
static SUITE: LazyLock<Regex> = LazyLock::new(|| re(r"/tests/hooks/test-[\w-]+-hooks\.sh$"));
static HOOK_SCRIPT: LazyLock<Regex> = LazyLock::new(|| re(r"/scripts/.*-hooks\.sh$"));
static HELD_SUITE: LazyLock<Regex> = LazyLock::new(|| re(r"/tests/hooks/test-.*-hooks\.sh$"));
/// The guards' own sources (T229, ask:449-guard-sources-held): every file under `rust/guard/src/` (the `.rs` and the data files the guards read) but the test files, the crate's manifest, the dispatcher script and (451 T169) `scripts/hooks/l7r-hook`, the launcher every hook entry of the settings calls, which chooses the dispatcher the settings' commands chose before.
static GUARD_SOURCE: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(/rust/guard/(?:shared/)?src/.+|/rust/guard/(?:shared/)?Cargo\.toml|/scripts/hooks/(?:l7r-guard\.sh|l7r-hook))$",
    )
});
static GUARD_TEST: LazyLock<Regex> = LazyLock::new(|| re(r"(/tests\.rs|/tests/[^ ]*)$"));
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

static GRANTED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(/scripts/(?:hooks/)?[\w-]+-hooks\.sh|/\.claude/settings\.json|/dev/switches\.json|/tests/rolls\.py)$",
    )
});

/// The files `make guard-edit` grants (feature 170 amendment 1; feature 429: the guards live in scripts/hooks/).
fn grantable(path: &str) -> bool {
    // `<clone>/context-cap:<agent id>`: `make context-ok`'s per-agent permit past the context cap (451 T13, plan D9)
    let context_cap = path.rsplit_once("/context-cap:").is_some_and(|(_, aid)| {
        !aid.is_empty()
            && aid
                .chars()
                .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
    });
    (hit(&GRANTED, path) && !hit(&SUITE, path))
        || root_makefile(path)
        || guard_source(path)
        || context_cap
}

/// A guard's source: a file under `rust/guard/src/` (not its `tests.rs` or a `tests/` directory), the crate's `Cargo.toml`, `scripts/hooks/l7r-guard.sh`, `scripts/hooks/l7r-hook`.
fn guard_source(file: &str) -> bool {
    hit(&GUARD_SOURCE, file) && !hit(&GUARD_TEST, file)
}

/// `l7r-guard permit grant <file> <reason>` (`make guard-edit`, from `hm_guard_permit.py`, feature 449 T051): the reason stated once, outside the file, honored for an hour.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let [verb, file, reason] = args else {
        return Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard permit grant <file> <reason>\n".to_owned(),
            code: 2,
        };
    };
    if verb != "grant" {
        return Reply {
            stdout: String::new(),
            stderr: "usage: l7r-guard permit grant <file> <reason>\n".to_owned(),
            code: 2,
        };
    }
    let (real, at) = (
        real_path(file),
        now_from(crate::shared::env::opt("L7R_PERMIT_NOW")),
    );
    let usage =
        "Usage: make guard-edit FILE=<guard file> WHY=\"<why this edit to a guard is legitimate>\"";
    let refuse = |stderr: String| Reply {
        stdout: String::new(),
        stderr,
        code: 2,
    };
    if !grantable(&real) {
        return refuse(format!(
            "make guard-edit: {real} is not a guard file, so its edits need no permit. {usage}\n"
        ));
    }
    if !enough(reason) {
        return refuse(format!(
            "make guard-edit: give a reason of two words and eight characters or more. {usage}\n"
        ));
    }
    let store = Path::new(&git_out(&real, "--absolute-git-dir")).join("l7r-guard-permits.jsonl");
    let mut rows = live_rows(&store, at);
    rows.push(serde_json::json!({"file": real, "reason": reason, "at": at}));
    let text: String = rows
        .iter()
        .map(|r| format!("{r}\n"))
        .collect::<Vec<_>>()
        .concat();
    let _ = std::fs::write(&store, text);
    let until = ask(
        Path::new("/"),
        "date",
        &["-d", &format!("@{:.0}", at + PERMIT_SECONDS), "+%H:%M"],
        "",
    )
    .out;
    // `make context-ok`'s grant says what it grants (451 T13): an agent past the context cap, not a file to edit
    let stdout = match real.rsplit_once("/context-cap:") {
        Some((_, aid)) => format!(
            "context-ok: agent {aid} may pass the context cap until {} - {reason}\n",
            until.trim()
        ),
        None => format!(
            "guard-edit: {real} may be edited until {} - {reason}\n",
            until.trim()
        ),
    };
    Reply {
        stdout,
        stderr: String::new(),
        code: 0,
    }
}

/// The permits still in force; a store that will not read holds none.
fn live_rows(store: &Path, at: f64) -> Vec<Value> {
    let text = std::fs::read_to_string(store).unwrap_or_default();
    let rows: Result<Vec<Value>, _> = text
        .lines()
        .filter(|l| !l.trim().is_empty())
        .map(serde_json::from_str)
        .collect();
    rows.unwrap_or_default()
        .into_iter()
        .filter(|r| at - r["at"].as_f64().unwrap_or(0.0) < PERMIT_SECONDS)
        .collect()
}

fn real_path(file: &str) -> String {
    std::fs::canonicalize(file)
        .map_or_else(|_| file.to_owned(), |p| p.to_string_lossy().into_owned())
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
    let guard = hit(&READ_GUARD, path) || root_makefile(path) || guard_source(path);
    if !guard || hit(&SUITE, path) {
        return None;
    }
    Some(if path.ends_with("/tests/rolls.py") {
        "This is the ROSTER OF ROLLED HAMLETS, and it is a GUARD file: an edit to it is refused unless the edit itself contains GUARD_EDIT_OK and a short reason. Before adding a row, read constitution VI, THE GATE ROLLS ONLY WHAT THE FLOOR NEEDS: the gate rolls a map only for engine lines no other roll reaches, and the census verdict FAILS a rostered roll with none. Pack the assertion onto a roll already made, make it a unit test, or move the test to tests/soak/ before you add a roll."
    } else if path.ends_with("/Makefile") {
        "This is the root Makefile, a GUARD file. It takes no GUARD_EDIT_OK comment: before editing it, run make guard-edit FILE=Makefile WHY=\"<why this edit is legitimate>\" - the reason goes in the guard log, and belongs in the commit message. Say which you are doing: fixing a guard that fires on correct work, adding a guard or an operation, or making a guard stop blocking something you want (that last one is what the rule exists to catch)."
    } else {
        // 451 T174 (message-check, ad346be4b7b040828): "Say which you are doing" became "Say which", and "(that last one is what the
        // rule exists to catch)" was cut - the rule's why, which changes nothing its reader does; the last choice still names it
        "This is a GUARD file. An edit to it is refused unless the edit itself contains GUARD_EDIT_OK and a short reason, or make guard-edit FILE=<this file> WHY=\"<reason>\" ran first. Say which: fixing a guard that fires on correct work, adding a guard or an operation, or making a guard stop blocking something you want."
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

/// Whether the file is one this guard holds - THE guard file list, which `make_only_hooks` reads for a write from the shell too (T227):
/// a guard file by its name, but not in scratch (451 T87).
pub(crate) fn held(file: &str) -> bool {
    named(file) && !scratch(file)
}

/// A guard file by its name alone, wherever it stands - the whole of `held` before 451 T87.
pub(crate) fn named(file: &str) -> bool {
    let guarded = file.ends_with("/Makefile")
        || hit(&HOOK_SCRIPT, file)
        || file.ends_with("/.claude/settings.json")
        || file.ends_with("/tests/rolls.py")
        || file.ends_with("/dev/switches.json")
        || file.ends_with("/dev/work-budget.json");
    (guarded && !hit(&HELD_SUITE, file)) || guard_source(file)
}

/// The project's trees (451 T87): the mirror with its clones and the l7r mount; `CLONE_MAIN`, the mirror's seam, adds a test's world.
const TREES: [&str; 2] = ["/diagram", "/host-l7r-repo"];

/// Whether a path is scratch, so a guard file's name there is a fixture and no guard file (451 T87, found by T79): its real path - its
/// existing part's links resolved (`tree::realpath`), so a scratch link into a clone is the clone's - lies under the temp directory,
/// `/tmp` or `$TMPDIR` (where `$(mktemp -d)` makes one; a `$TMPDIR` of `/`, the home directory or a place holding it is no scratch of
/// its own), and in no project tree. Every other place keeps the reading by name: `/Makefile`, where the walk puts `$UNSET/Makefile`
/// and `$CLAUDE_PROJECT_DIR/Makefile`, a path the shell computes and the walk cannot place; `~/.claude/settings.json`, which registers
/// the GM's own hooks. Measured 2026-11-21 (the guard log, 96,279 firings): of make-only's 745 guard-write refusals, 110 held a
/// guard file's name under `/tmp` alone; of guard-file's 180, 11 named one under `/tmp` and 2 `~/.claude/settings.json`. A git
/// worktree in scratch of a project repository is a project tree (`project_worktree`): 43 of those 110 wrote into one.
fn scratch(file: &str) -> bool {
    use crate::shared::tree::realpath;
    if !file.starts_with('/') {
        return false;
    }
    let real = realpath(Path::new(file));
    let home = crate::shared::env::var("HOME");
    let temp = crate::shared::env::opt("TMPDIR")
        .filter(|t| t.starts_with('/'))
        .map(|t| realpath(Path::new(&t)))
        .filter(|t| t.as_path() != Path::new("/") && !Path::new(&home).starts_with(t));
    let mut roots = std::iter::once(realpath(Path::new("/tmp"))).chain(temp);
    let trees: Vec<PathBuf> = TREES
        .iter()
        .map(|t| (*t).to_owned())
        .chain(crate::shared::env::opt("CLONE_MAIN").filter(|t| t.starts_with('/')))
        .map(|t| realpath(Path::new(&t)))
        .collect();
    roots.find(|r| real.starts_with(r)).is_some_and(|root| {
        !trees.iter().any(|t| real.starts_with(t)) && !project_worktree(&real, &root, &trees)
    })
}

/// Whether a scratch path lies in a git worktree of a project repository (451 T87, review round 2: `/tmp/t50/wt`, a worktree of a
/// clone): its commits reach that repository, so it is a project tree. The nearest `.git` at or under the scratch root is read once,
/// a directory being a repository of scratch's own, and a file's `gitdir:` (relative to its own directory) leads to the common git
/// dir, its `commondir` (relative to it) or, where none is read, the gitdir itself, so a pointer into a project is held where it points.
fn project_worktree(real: &Path, root: &Path, trees: &[PathBuf]) -> bool {
    let Some(dot) = real
        .ancestors()
        .take_while(|a| a.starts_with(root))
        .map(|a| a.join(".git"))
        .find(|g| g.exists())
    else {
        return false;
    };
    let Ok(text) = std::fs::read_to_string(&dot) else {
        return false;
    };
    let gitdir = dot.with_file_name(text.trim().trim_start_matches("gitdir:").trim());
    let common = std::fs::read_to_string(gitdir.join("commondir"))
        .map_or_else(|_| gitdir.clone(), |c| gitdir.join(c.trim()));
    let common = crate::shared::tree::realpath(&common);
    trees.iter().any(|t| common.starts_with(t))
}

/// The time a permit is granted and judged at: `L7R_PERMIT_NOW`, read through `shared::env` (a test's own environment, never a
/// session's export, feature 451 T32), else the clock.
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
        "BLOCKED: this edit puts a COMMAND SUBSTITUTION inside a recipe comment of {file}:\n\n{}\n\nA `: \"...\"` recipe comment is a shell string, and a backtick or a $$( inside it RUNS. On 2026-09-07\none such comment naming the full gate in backticks ran that gate from inside itself, 914 levels\ndeep, until the container hit its process limit. Write the name without backticks, or escape them\n(\\` and \\$$( are literal), or use single quotes. There is no escape token for this - it is\na shell fact, not a policy. (rust/guard/src/guards/guard_file_hooks.rs; feature 212)",
        found.join("\n")
    )
}

/// `dev/work-budget.json` takes no permit: `make guard-edit` refuses it, and its writers are the budget targets (feature 449 T225).
fn budget_text(file: &str) -> String {
    format!(
        "BLOCKED: {file} is the work budgets, written only by the budget targets - not by an edit, and `make guard-edit` refuses it.

Change a budgeted stage's figure with the GM's own words:

    make budget-change PHASE=<stage> TO=<ops per thing> WORDS=\"<the GM's words>\"

(a stage's FIRST budget is `make budget-set`, the whole roll's `make budget-program`, a rebuilt stage's acceptance `make budget-accept`;
`make help` lists their arguments). The words are checked against the session and logged in dev/work-budget-changes.jsonl.

(rust/guard/src/guards/guard_file_hooks.rs; feature 443, 449 T225)"
    )
}

fn no_marker_text(file: &str) -> String {
    if file.ends_with("/dev/work-budget.json") {
        return budget_text(file);
    }
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
        now_from(crate::shared::env::opt("L7R_PERMIT_NOW")),
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
