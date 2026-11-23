//! `event-log-hooks` (feature 375 FR-008; ported from `scripts/hooks/event-log-hooks.sh` and the hook half of
//! `scripts/measure/event_log.py`, feature 449 T012): ONE LINE A HOOK EVENT into the feature's event log, so where a feature's time
//! went is counted, not remembered (`make feature-report` reads it). It never refuses and never prints: a hook that adds a line to
//! every tool call must not be able to stop one. Its reading half - a log's lines, a session transcript turned into the same events,
//! the reversals - is `read.rs`, ported from `event_log.py`'s other half by T119 (`ask:449-T83-scope`), which deleted the `.py`.
//!
//! WHY (the GM, 2026-10-10): *"maybe the actual solution here is that we have hooks built into our tooling which will save off
//! timestamps that allow us to mechanically and trivially calculate these numbers"*. THE LINE (feature 375 plan D7): one JSON line a
//! `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `UserPromptSubmit` and Stop payload, to `<git common dir>/l7r-events/<feature
//! dir>.jsonl` (`_unassigned.jsonl` with no feature) of the session's clone, else of the tree the call's cwd stands in (451 T74, `tree_of`). Fields: `t` (UTC), `sid`, `ev`, and where they apply `tool`, `id` (`tool_use_id`),
//! `cat` (`category`; a Bash call's by the category table, `BUCKETS`, feature 451 D2), `make` (a Bash call's first make target), `makes` (every target, where it runs more than one - 451 T14) and `task`
//! (the task a tick, task-start, decide or land names, else the dispatch's brief's, its builder's or its page session's, else - the main
//! session's own line alone - its feature's start in force; 451 D2, T161), `fallback`
//! (the line's feature was only the session's or feature.json's, nothing on the line naming one - 451 T26, `filed.rs`, which also says
//! which feature's log a line goes to), `path`, `old`/`new`
//! (digests of an Edit's strings - the reversal wire) and `heading`, `agent`/`aid`/`manifest`/`unit`/`waiver` (an agent's type, id, the
//! MANIFEST its prompt names, its unit, a round on the GM's waiver), `by` (the subagent whose tool call it is, feature 385 amendment 4),
//! `ms` (`PostToolUse`'s duration), `gm` (a prompt the GM typed, not a notification), `verdict` (a returned agent's verdict word, or
//! `clean` / `findings`), `bg` (a backgrounded call's `PostToolUse`: its run's task id) and `inflight` (a `Stop` or `SubagentStop`: the
//! background runs in flight, 451 T04, `fields.rs`), `tok` and `ctx` (a `SubagentStop`: the agent's tokens, each call once, and its last
//! call's context, 451 T07, `fields::agent_cost`). Two line kinds are no hook event's own: `BgEnd`, a background shell's end, written
//! beside the `UserPromptSubmit` of the main session's completion notice and filed beside its launch (`bg_end`: `id`, `bg`, `status`,
//! `exit`, `t0`, the launch's `make`, `cat`, `task`, `fallback`; 451 T04, plan D3), and `Phase`, a gate tool's step ([`append_row`], plan D4); the
//! readers set both aside from the time-gap stream (`measure::events::load_all`). The gap from one `PostToolUse` to the next `PreToolUse`
//! is the model's own time. A clone's git dir outlives its sessions and any compaction, and the report reads every clone's log for the
//! feature.
//!
//! Plan T012's decisions: (a) the line, the log's path and the append are in-process; (b) the reversal test runs here, and the
//! trigger it owes is recorded by `hm_arbiter.py`, asked by path; (c) the event is the payload's; (d) the digests are SHA-1's.

use std::io::Write as _;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{Map, Value};

use crate::checks;
use crate::log::civil;
use crate::protocol::{Answer, Event, Guard};
use crate::session::Session;
use crate::sha1;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "event-log-hooks",
    events: &[
        "PreToolUse",
        "PostToolUse",
        "SubagentStart",
        "SubagentStop",
        "UserPromptSubmit",
        "Stop",
        "PostToolUseFailure",
        "",
    ],
    matcher: "*",
    decide,
};

const RECORD_CHECKS: [&str; 11] = [
    "quote-check",
    "record-format",
    "source-applicability",
    "source-reader",
    "entry-drift",
    "record-style",
    "translation-check",
    "intro-check",
    "modal-form",
    "modal-research",
    "modal-depiction",
];
const REVIEW_CHECKS: [&str; 5] = [
    "glyph-check",
    "settlement-review",
    "fix-check",
    "building-review",
    "size-audit",
];
const EDIT_TOOLS: [&str; 4] = ["Edit", "Write", "NotebookEdit", "MultiEdit"];

fn re(pattern: &str) -> Regex {
    crate::regex::build(pattern).unwrap_or_else(|e| unreachable!("a guard's own pattern: {e}"))
}

macro_rules! pattern {
    ($name:ident, $p:expr) => {
        static $name: LazyLock<Regex> = LazyLock::new(|| re($p));
    };
}

pattern!(MANIFEST, r#"(/[^\s`"'<>)]*MANIFEST\.md)"#);
pattern!(
    FINDING_COUNT,
    r"\b[1-9]\d*\s+(?:findings?|unfootnoted|EDITs?|DOES-NOT-SUPPORT|DRIFTED|MISLABELED|FIX|VOCABULARY|SESSION NOTE|HISTORY)\b"
);
pattern!(CLEAN_SAID, r"(?i)\b(?:nothing to act on|no findings)\b");
pattern!(
    UNIT_SUMMARY,
    r"(?m)^[a-z-]+: \S+ - [A-Z]+ \d+ findings?;.*$"
);
pattern!(
    EMPTY_SAID,
    r"(?i)\blists no (?:changed pages|claims|units)\b|\bbundle (?:was|is) (?:built )?empty\b"
);
pattern!(
    VERDICT,
    r"\b(NOT-REVIEWABLE|NOT FAITHFUL|CHANGES REQUIRED|BLOCKED|FAITHFUL|CLEAR|NEEDS-WORK|PASS|FAIL)\b"
);
pattern!(
    RECORDED,
    r"(?mi)\brecorded (PASS|NEEDS-WORK|NOT-REVIEWABLE) for\b|^\s*VERDICT:\s*(pass|needs-work|not-reviewable)\b"
);
pattern!(NUMBER, r"\b\d+\b");
// a command's `T=`, quoted or not (`T="T05"`); a list's first only - `T="T1,T2"` read whole is T18's
pattern!(TASK, r#"\bT=["']?(T\d+[a-z]?)\b"#);
// the `T<n>` an agent's brief names (`451 T07: ...`)
pattern!(TASK_NAMED, r"\b(T\d+[a-z]?)\b");
pattern!(UNIT, r"\bUNIT:\s*(\S+)");
pattern!(GITDIR, r"gitdir:\s*(.+)");

fn found(p: &Regex, text: &str) -> bool {
    p.is_match(text).unwrap_or(false)
}

fn first_group(p: &Regex, text: &str) -> Option<String> {
    p.captures(text)
        .ok()
        .flatten()
        .and_then(|c| c.get(1))
        .map(|m| m.as_str().to_owned())
}

/// The first `n` characters of `text` (Python's `text[:n]`).
fn head(text: &str, n: usize) -> &str {
    text.char_indices().nth(n).map_or(text, |(i, _)| &text[..i])
}

fn numbers(text: &str) -> Vec<String> {
    NUMBER
        .find_iter(text)
        .map_while(Result::ok)
        .map(|m| m.as_str().to_owned())
        .collect()
}

/// The verdict a returned agent's reply leads with, or `clean`/`findings` from its counts, or "" (`verdict_of`).
#[must_use]
pub fn verdict_of(text: &str) -> String {
    if let Ok(Some(c)) = RECORDED.captures(text) {
        return c
            .get(1)
            .or_else(|| c.get(2))
            .map_or(String::new(), |m| m.as_str().to_uppercase());
    }
    let lead = head(text, 600);
    if let Some(v) = first_group(&VERDICT, lead) {
        return v;
    }
    // Python's `text.strip().splitlines()` and `ln.strip()`: its whitespace and line ends, not Rust's (feature 449 T83, where the ledger
    // write reads a reply's verdict through this)
    let first = crate::checks::reply::py_lines(crate::py_text::strip(text))
        .into_iter()
        .find(|l| !crate::py_text::strip(l).is_empty())
        .unwrap_or("");
    if found(&FINDING_COUNT, first) {
        return "findings".to_owned();
    }
    if found(&CLEAN_SAID, lead) {
        return "clean".to_owned();
    }
    let nums = numbers(first);
    if !nums.is_empty() {
        return if nums.iter().all(|n| n == "0") {
            "clean"
        } else {
            "findings"
        }
        .to_owned();
    }
    let units: Vec<String> = UNIT_SUMMARY
        .find_iter(text)
        .map_while(Result::ok)
        .map(|m| m.as_str().to_owned())
        .collect();
    if !units.is_empty() {
        let any = units.iter().any(|u| {
            u.split_once(" - ")
                .is_some_and(|(_, rest)| numbers(rest).iter().any(|n| n != "0"))
        });
        return if any { "findings" } else { "clean" }.to_owned();
    }
    if found(&EMPTY_SAID, lead) {
        return "empty bundle".to_owned();
    }
    String::new()
}

/// The first make target a Bash command runs, or "" (`make_target`): `shared::make::invoked`'s first, the one detector the guards
/// read too (feature 451 D1 - the writer's own pattern took no `timeout N` or `flock F`, so a timed run logged no target).
#[must_use]
pub fn make_target(command: &str) -> String {
    crate::make::invoked(command)
        .into_iter()
        .next()
        .unwrap_or_default()
}

/// THE CATEGORY TABLE (feature 451 T03, FR-001, plan D2): a make target - and the gate's own `l7r-gate.sh rust <cmd>`, which
/// `shared::make::invoked` reads as `rust-<cmd>` (D1) - to the bucket its minutes go to. The writer books a Bash call's `cat` by it and both
/// readers (`where_time.rs`, `feature_report/tables.rs`) book a line by its `make` field through [`bucket_of`], so a past log re-books too.
/// WHY: the old categorizer knew `quick`, `test-file`, `done` and three spec-kit targets, and booked 210 of a window's tool-minutes "other
/// tool" - `static` 30.8, `format` 20.9, `hooks-test` 20.2, `rust-test` 16.6, `render-sync` 6.1, `map` 3.6 of them (observed 2026-11-20,
/// method: the `ms` of the 449 log's `PostToolUse` lines since 2026-11-19T14:00Z, summed by `make`; research R1). Rows are
/// `data-model.md`'s, finished from the Makefile's `## [tag]` lines; moving a target between buckets is a one-line change. `compile` is
/// no target's: it is the `build`/`cover-build` phase lines inside a tests run (D4, T05), booked by the readers (T08).
pub const BUCKETS: [(&str, &[&str]); 7] = [
    // TESTS: what checks a change while iterating - the `[tests]`/`[static]` checks, the crates' tests and the gate's own crate-scoped
    // forms of them (`rust-test`, `rust-cover`, `rust-lint`, `rust-format`, ...; never a bare `rust-` prefix: `rust-hamlet` is a counting
    // run). `format` is `rust-format` over every crate (data-model's row); `test-file` is pytest's, gone with 449 T213, kept for past logs.
    // `map` (and the one-map drivers `hamlet`, `compound`, `sheet-render`, with `maps-moved` and a sheet's `pack-audit`) is HERE, not with
    // `cohort` under gate: the dev loop pairs it with `make quick` ("Iterate on that ONE map, `make quick` while iterating",
    // `l7r/diagram/CLAUDE.md`) - it is the iteration's own run on the changed engine's output, where a cohort is the after-the-fix sweep
    // the landing's gate reads. `work-budget` and `budget-sheets` check counted work against its budget, as a test checks a figure.
    (
        "tests",
        &[
            "quick",
            "test-file",
            "static",
            "closing-checks",
            "format",
            "rust-test",
            "hooks-test",
            "counters-inert",
            "test-times",
            "rust-cover",
            "rust-lint",
            "rust-format",
            "rust-test-counters",
            "rust-dead",
            "rust-uncovered",
            "rust-test-times",
            "preflight",
            "rust-tooling",
            "inline-census",
            "page-check",
            "parts-sweep",
            "coverage-exempt",
            "map",
            "hamlet",
            "compound",
            "sheet-render",
            "maps-moved",
            "pack-audit",
            "work-budget",
            "budget-sheets",
        ],
    ),
    // GATE: the whole gate and what holds a push or a landing on it - `done` and its paired and idle forms, the wait on it, the cohorts
    // (data-model's row), a gated push's conditions, the push's work-budget ratchet; each a span `task_phases::measured_run` lists in a
    // task's timeline. `push-checks` is the gate crate's verb (no make target today), kept as data-model names it.
    (
        "gate",
        &[
            "done",
            "verify",
            "verify-wait",
            "idle-tests",
            "push-checks",
            "cohort",
            "cohort-landing",
            "gated-check",
            "work-budget-review",
        ],
    ),
    // LAND: a landing and its stop.
    ("land", &["land", "land-batch", "land-tooling", "land-stop"]),
    // REVIEW: a plan's review, a check's bundle and what is owed one, a check's verdict and its arbiter, the GM's filter - the time a
    // review costs the session around its agents.
    (
        "review",
        &[
            "plan-delta",
            "plan-verdict",
            "decide",
            "check-bundle",
            "claims-bundle",
            "arbiter-bundle",
            "modal-bundle",
            "record-owed",
            "claims-owed",
            "claims-triage",
            "claims-triaged",
            "claims-checked",
            "claims-report",
            "claims-report-only",
            "claims-known",
            "claims-carry",
            "claims-coverage",
            "impl-check",
            "modal-triage",
            "modal-triaged",
            "modal-prepass",
            "translation-owed",
            "record-checked",
            "record-prepass",
            "style-prepass",
            "quote-verbatim",
            "review-verdict",
            "review-accept",
            // the settlement-review's paired gate's state (green, running or red): a query about a review, no gate run of its own
            "review-paired-gate",
            "review-census",
            "review-cost",
            "ledger-owed",
            "check-closed",
            "accept",
            "arbiter-ask",
            "arbiter-ruled",
            "arbiter-nit",
            "arbiter-fix-done",
            "arbiter-fix-declined",
            "gm-escalated",
            "step-back",
            "work-budget-bundle",
        ],
    ),
    // DOCS: what builds a page someone reads - the `[docs]` targets, `make docs`, the reports (`feature-report` by data-model's row,
    // `where-time` its sibling over the same reader). `render-sync` is HERE: it rebuilds main's renders, the pool index and the record
    // site for the GM to browse (`scripts/sync-with-main.sh`), run by both `done` and `sync-in`, so it is no landing's own step.
    (
        "docs",
        &[
            "docs",
            "make-docs",
            "record",
            "feature-report",
            "where-time",
            "render-sync",
            "pool-index",
            "pool-index-if-stale",
            "building-programs",
            "citations",
            "footnote-census",
            "glossary",
            "source-tags-contract",
            "money-candidates",
            "money-conversions",
            "fragment-move",
        ],
    ),
    // SPEC-KIT STEP: the feature's own bookkeeping (data-model's row; the old categorizer's `tick` and `claim`; `plan-verdict` is now a
    // review's).
    (
        "spec-kit step",
        &[
            "tick",
            "claim",
            "task-start",
            "task-add",
            "set-down",
            "plan-archive",
            "trial",
            "trial-review",
            "use-feature",
            "speckit-todo",
        ],
    ),
    // OTHER: every target not above, and a Bash call with none - `bucket_of`'s fallback, never a row.
    ("other", &[]),
];

/// The bucket a make target's minutes go to (D2): its [`BUCKETS`] row, else `other` - never dropped (spec edge case).
#[must_use]
pub fn bucket_of(target: &str) -> &'static str {
    BUCKETS
        .iter()
        .find(|(_, targets)| targets.contains(&target))
        .map_or("other", |(bucket, _)| bucket)
}

/// What kind of subagent this is (`agent_category`).
#[must_use]
pub fn agent_category(agent_type: &str, prompt: &str) -> &'static str {
    if agent_type == "impl-drift" || prompt.contains("claims-triage") {
        "claims check"
    } else if RECORD_CHECKS.contains(&agent_type) || prompt.contains("modal-triage") {
        "record check"
    } else if REVIEW_CHECKS.contains(&agent_type) {
        "review check"
    } else if agent_type == "spec-fidelity" || agent_type == "spec-fidelity-verify" {
        "spec review"
    } else if agent_type == "round-arbiter" {
        "round arbiter"
    } else {
        "other subagent"
    }
}

fn text_of(v: Option<&Value>) -> String {
    match v {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Null | Value::Bool(false)) | None => String::new(),
        Some(other) if truthy(other) => other.to_string(),
        _ => String::new(),
    }
}

/// Python's truthiness of a JSON value.
fn truthy(v: &Value) -> bool {
    match v {
        Value::Null => false,
        Value::Bool(b) => *b,
        Value::Number(n) => n.as_f64() != Some(0.0),
        Value::String(s) => !s.is_empty(),
        Value::Array(a) => !a.is_empty(),
        Value::Object(o) => !o.is_empty(),
    }
}

/// The value, or "" where it is not truthy (`payload.get(k) or ""`).
fn or_empty(v: Option<&Value>) -> Value {
    v.filter(|x| truthy(x))
        .cloned()
        .unwrap_or_else(|| Value::String(String::new()))
}

/// The category of one tool call (`category`).
#[must_use]
pub fn category(tool: &str, ti: &Map<String, Value>) -> &'static str {
    if EDIT_TOOLS.contains(&tool) {
        return "edit";
    }
    match tool {
        // a Bash call by the table (D2); its `other` stays the line's `other tool`, the one word every tool with nothing more specific
        // carries, which the readers' `other tool` tables read
        "Bash" => match bucket_of(&make_target(&text_of(ti.get("command")))) {
            "other" => "other tool",
            bucket => bucket,
        },
        "Agent" => agent_category(
            &text_of(ti.get("subagent_type")),
            &text_of(ti.get("prompt")),
        ),
        "Skill" if text_of(ti.get("skill")).starts_with("speckit-") => "spec-kit step",
        _ => "other tool",
    }
}

fn digest(text: &str) -> String {
    sha1::hex(text.as_bytes())[..12].to_owned()
}

/// One Markdown heading line and nothing else (`heading_only`).
fn heading_only(text: &str) -> bool {
    let lines: Vec<&str> = text.lines().filter(|l| !l.trim().is_empty()).collect();
    lines.len() == 1 && lines[0].trim_start().starts_with('#')
}

/// Whether a user message is a prompt the GM typed (`_typed_prompt`).
fn typed_prompt(content: &Value) -> bool {
    let text = match content {
        Value::Array(blocks) => {
            let texts: Vec<String> = blocks
                .iter()
                .filter(|b| b.get("type") == Some(&Value::from("text")))
                .map(|b| text_of(b.get("text")))
                .collect();
            if texts.is_empty()
                || blocks
                    .iter()
                    .any(|b| b.get("type") == Some(&Value::from("tool_result")))
            {
                return false;
            }
            texts.join("\n")
        }
        Value::String(s) => s.clone(),
        other => other.to_string(),
    };
    let text = text.trim_start();
    !text.is_empty()
        && ![
            "<task-notification>",
            "<system-reminder>",
            "<local-command",
            "Caveat:",
        ]
        .iter()
        .any(|p| text.starts_with(p))
}

/// Now as the log writes it: UTC to the millisecond, `Z`.
#[must_use]
pub fn now_stamp(at: SystemTime) -> String {
    let d = at.duration_since(UNIX_EPOCH).unwrap_or_default();
    let (y, mo, day, h, mi, s) = civil(d.as_secs());
    format!(
        "{y:04}-{mo:02}-{day:02}T{h:02}:{mi:02}:{s:02}.{:03}Z",
        d.subsec_millis()
    )
}

/// The log line for one hook payload (`line`).
#[must_use]
pub fn line(payload: &Value, t: &str) -> Map<String, Value> {
    let ev = text_of(payload.get("hook_event_name"));
    let mut out = Map::new();
    out.insert("t".into(), Value::from(t));
    out.insert("sid".into(), or_empty(payload.get("session_id")));
    out.insert("ev".into(), Value::from(ev.clone()));
    let tool = payload.get("tool_name").filter(|v| truthy(v));
    if let Some(tool) = tool {
        let empty = Map::new();
        let ti = payload
            .get("tool_input")
            .and_then(Value::as_object)
            .unwrap_or(&empty);
        let name = text_of(Some(tool));
        out.insert("tool".into(), tool.clone());
        out.insert("id".into(), or_empty(payload.get("tool_use_id")));
        out.insert("cat".into(), Value::from(category(&name, ti)));
        if let Some(by) = payload.get("agent_id").filter(|v| truthy(v)) {
            out.insert("by".into(), by.clone());
        }
        fields::tool_fields(&mut out, &name, ti, payload);
        if payload.get("duration_ms").is_some_and(Value::is_number) {
            out.insert("ms".into(), payload["duration_ms"].clone());
        }
    } else if ev == "UserPromptSubmit" && payload.get("prompt").is_some() {
        out.insert("gm".into(), Value::Bool(typed_prompt(&payload["prompt"])));
    } else if ev == "SubagentStart" || ev == "SubagentStop" {
        let agent = or_empty(payload.get("agent_type"));
        out.insert("agent".into(), agent.clone());
        out.insert("aid".into(), or_empty(payload.get("agent_id")));
        out.insert(
            "cat".into(),
            Value::from(agent_category(&text_of(Some(&agent)), "")),
        );
        let verdict = verdict_of(&text_of(payload.get("last_assistant_message")));
        if !verdict.is_empty() {
            out.insert("verdict".into(), Value::from(verdict));
        }
    }
    fields::run_fields(&mut out, &ev, payload);
    out
}

/// Whether a check type has a round cap: the record checks, the claims check and the review checks (`feature_report.tripwires`' `capped`,
/// feature 449 T119).
#[must_use]
pub fn round_capped(agent_type: &str) -> bool {
    agent_type == "impl-drift"
        || RECORD_CHECKS.contains(&agent_type)
        || REVIEW_CHECKS.contains(&agent_type)
}

/// The working tree holding `cwd`, walked up to its `.git` (`clone_root`).
fn clone_root(cwd: &Path) -> Option<PathBuf> {
    let p = std::fs::canonicalize(cwd).unwrap_or_else(|_| cwd.to_path_buf());
    p.ancestors()
        .find(|d| d.join(".git").exists())
        .map(Path::to_path_buf)
}

/// The git dir a worktree shares with its clone (`common_git_dir`).
#[must_use]
pub fn common_git_dir(root: &Path) -> PathBuf {
    let g = root.join(".git");
    let Some(dir) = std::fs::read_to_string(&g)
        .ok()
        .and_then(|t| first_group(&GITDIR, t.trim()))
    else {
        return g;
    };
    let dir =
        std::fs::canonicalize(root.join(dir.trim())).unwrap_or_else(|_| root.join(dir.trim()));
    match std::fs::read_to_string(dir.join("commondir")) {
        Ok(c) => std::fs::canonicalize(dir.join(c.trim())).unwrap_or_else(|_| dir.join(c.trim())),
        Err(_) => dir,
    }
}

/// The active feature's directory name, or "" (`feature_of`).
fn feature_of(root: &Path, env: &dyn Fn(&str) -> Option<String>) -> String {
    let own = env("L7R_FEATURE_DIRECTORY").unwrap_or_default();
    let own = own.trim().trim_end_matches('/');
    if let Some(name) = Path::new(own).file_name().filter(|_| !own.is_empty()) {
        return name.to_string_lossy().into_owned();
    }
    let named = env("SPECIFY_FEATURE").unwrap_or_default();
    let named = named.trim().trim_matches('/');
    if !named.is_empty() && root.join("specs").join(named).is_dir() {
        return named.to_owned();
    }
    std::fs::read_to_string(root.join(".specify/feature.json"))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
        .map(|d| text_of(d.get("feature_directory")))
        .and_then(|d| {
            Path::new(&d)
                .file_name()
                .map(|n| n.to_string_lossy().into_owned())
        })
        .unwrap_or_default()
}

/// Whether an Edit of `path` puts back text an earlier Edit of that file replaced (`hm_arbiter.reversal`).
fn reversal(log: &Path, path: &Value, old: &Value, new: &Value) -> bool {
    let text = std::fs::read_to_string(log).unwrap_or_default();
    let replaced: Vec<Value> = text
        .lines()
        .filter_map(|l| serde_json::from_str::<Value>(l.trim()).ok())
        .filter(|e| {
            e.get("ev") == Some(&Value::from("PreToolUse"))
                && e.get("tool") == Some(&Value::from("Edit"))
                && e.get("path") == Some(path)
        })
        .map(|e| e.get("old").cloned().unwrap_or(Value::Null))
        .collect();
    truthy(new) && replaced.contains(new) && new != old
}

/// A feature's event log (`event_log.log_path`): under `L7R_EVENTS_DIR`, else the clone's common git dir; `_unassigned` for no feature.
#[must_use]
pub fn log_path(root: &Path, feature: &str) -> PathBuf {
    log_path_in(root, feature, &crate::env::opt)
}

/// [`log_path`] with its environment given (feature 451 T38: a gate crate passes the reader its root carries, `shared::env::Rooted`).
#[must_use]
pub fn log_path_in(root: &Path, feature: &str, env: &dyn Fn(&str) -> Option<String>) -> PathBuf {
    let base = env("L7R_EVENTS_DIR")
        .filter(|d| !d.is_empty())
        .map_or_else(|| common_git_dir(root).join("l7r-events"), PathBuf::from);
    base.join(format!(
        "{}.jsonl",
        if feature.is_empty() {
            "_unassigned"
        } else {
            feature
        }
    ))
}

/// The directory a payload's call ran in: its `cwd`, else `here`.
fn cwd_of(payload: &Value, here: &Path) -> PathBuf {
    payload
        .get("cwd")
        .and_then(Value::as_str)
        .filter(|c| !c.is_empty())
        .map_or_else(|| here.to_path_buf(), PathBuf::from)
}

/// The tree a payload's line is filed in (451 T74): the SESSION'S CLONE - `shared::session`'s resolve, as `context_cap_hooks`' `seat`
/// reads a builder's handoff (451 T60) - where it is a work tree, else the tree the call's cwd stands in; None outside any tree, as
/// before: the cwd still gates, so a call from `/` or `/tmp` writes nothing. WHY: builders whose shells were reset to the mirror filed
/// their lines under the MIRROR's `.git/l7r-events/` - 364 lines of 451's log, 361 a builder's and 3 the main session's, none of them in
/// the clone's, so `make where-time F=451` in the clone booked none of them (observed 2026-11-21, method: a Python count of the mirror's
/// log by session and key, matched to the clone's by `t`, `ev`, agent and tool).
///
/// THE CLAIM MAP ALONE (a deliberate deviation from `seat`, which also reads the session's name): the session's transcript and sessions
/// directory are blanked, so its name - the transcript's last `/rename`, else the sessions json - is never read. WHY: this runs on every
/// hook event, and the name step reads the whole transcript: 142.7 ms a call for a session with no claim map and a 122 MB transcript,
/// against 1.8 ms before (medians of 15, a build reading the name); the claim map alone, 1.7 ms against 1.7 ms, and a claimed session's
/// call from the mirror 2.6 ms against 1.9 ms (medians of 31) - measured 2026-11-21, the guard's binary `--only event-log-hooks`
/// before and after, `L7R_EVENTS_DIR` a scratch directory. What it costs: a session with no
/// claim map but a name naming a clone keeps the cwd's tree, today's answer - 17 of the mirror's 5,296 `_unassigned` lines and 0 of
/// the clone's 82,580 hook lines since 2026-11-14 came from a session with no claim map (measured 2026-11-21, a Python count against
/// `.clones/.session-clones/`), since `clone_sync_hooks` writes the map as a session works in its clone.
fn tree_of(payload: &Value, here: &Path, env: &dyn Fn(&str) -> Option<String>) -> Option<PathBuf> {
    let cwd = cwd_of(payload, here);
    let tree = clone_root(&cwd)?;
    let mut session = Session::with_env(payload, env);
    session.cwd = cwd.to_string_lossy().into_owned();
    session.transcript = String::new();
    session.sessions_dir = PathBuf::new();
    Some(
        session
            .clone_dir()
            .filter(|c| c.join(".git").exists())
            .map(Path::to_path_buf)
            .map_or(tree, |c| std::fs::canonicalize(&c).unwrap_or(c)),
    )
}

/// Where a payload's line is filed - its clone, its feature, that feature's log and its task - as [`append`] files it, nothing written (feature 451
/// T14: `static_runs_hooks` counts a task's runs in the log its call's own line goes to, under the task that line carries, so the main
/// session and its builders share one count) - in the session's clone, as `append` writes it ([`tree_of`], 451 T74). None outside any clone.
pub fn filed_at(
    payload: &Value,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
) -> Option<(PathBuf, String, PathBuf, Option<String>)> {
    let root = tree_of(payload, here, env)?;
    let row = line(payload, "");
    let to = filed::filed(
        payload,
        row.get("task").and_then(Value::as_str),
        None,
        &root,
        &now_stamp(SystemTime::now()),
        env,
    );
    let log = log_path_in(&root, &to.feature, env);
    Some((root, to.feature, log, to.task))
}

/// Append the payload's line to its feature's log - the feature of the task it carries, feature.json's only where nothing else says
/// (451 T26, [`filed`]), in the log of the session's clone (451 T74, [`tree_of`]); None outside any clone (`append`). A file missing or
/// unreadable is no task, never an error: the hook never refuses.
pub fn append(
    payload: &Value,
    t: &str,
    here: &Path,
    env: &dyn Fn(&str) -> Option<String>,
) -> Option<PathBuf> {
    // A PAYLOAD NAMING NO HOOK EVENT IS NO HOOK'S (T207): a test's empty input (and on 11-08 `--self-check`'s fixed one) wrote
    // `{"sid": "", "ev": ""}` rows into the clone's real log on every `make static` and `make rust-test`, which `make where-time` booked as idle
    if text_of(payload.get("hook_event_name")).is_empty() {
        return None;
    }
    let root = tree_of(payload, here, env)?;
    let mut row = line(payload, t);
    let carried = row.get("task").and_then(Value::as_str).map(str::to_owned);
    let to = filed::filed(payload, carried.as_deref(), None, &root, t, env);
    let path = log_path_in(&root, &to.feature, env);
    let base = path.parent().map_or_else(PathBuf::new, Path::to_path_buf);
    std::fs::create_dir_all(&base).ok()?;
    // an Agent call's halves kept for its agent's first start, filed before its meta file exists (451 T53, `dispatches.rs`)
    dispatches::record(&base, payload, t);
    if let Some(task) = to.task {
        row.insert("task".into(), Value::from(task));
    }
    if to.fallback {
        row.insert("fallback".into(), Value::Bool(true));
    }
    if row.get("ev") == Some(&Value::from("SubagentStop")) {
        fields::agent_cost(&mut row, payload);
    }
    let edit = row.get("ev") == Some(&Value::from("PreToolUse"))
        && row.get("tool") == Some(&Value::from("Edit"));
    let null = Value::Null;
    let field = |k: &str| row.get(k).unwrap_or(&null);
    if edit
        && path.is_file()
        && row.get("heading").is_none()
        && reversal(&path, field("path"), field("old"), field("new"))
    {
        let p = text_of(Some(field("path")));
        // owed by the session and builder whose Edit put it back, and held against only their dispatches (449 arbiter fix,
        // 451's rulings on `reversal:<file>` of 2026-11-22: it held every builder in the clone)
        let (sid, by) = (text_of(row.get("sid")), text_of(row.get("by")));
        let _ = checks::arbiter::trip_as(
            &root,
            &format!("reversal:{p}"),
            "reversal",
            &p,
            &format!("an Edit put back text an earlier Edit of {p} replaced (A -> B -> A)"),
            checks::arbiter::Who { sid: &sid, by: &by },
        );
    }
    let notice = (row.get("ev") == Some(&Value::from("UserPromptSubmit")))
        .then(|| payload.get("prompt").and_then(Value::as_str))
        .flatten()
        .and_then(fields::notice_end);
    let sid = row.get("sid").cloned().unwrap_or(Value::Null);
    let task = row.get("task").and_then(Value::as_str).map(str::to_owned);
    let written = write_line(&path, row)?;
    if let Some(end) = notice {
        bg_end(end, t, sid, &written, &base, (task, to.fallback));
    }
    Some(written)
}

/// A background run's END (feature 451 T04, FR-002, plan D3): the `BgEnd` line a shell's completion notice writes, filed BESIDE ITS
/// LAUNCH - in the log holding the launching call's line, whose `make`, `cat`, `task` and `fallback` mark it copies and whose `t` is its `t0`, so the
/// run's span is one pair of lines in one log. WHY beside the launch, not where the prompt's line goes: a notice payload names no
/// command, agent or task, so `filed` gives it the fallback feature (feature.json's), while the launch was filed by its own `F=` or
/// brief (T26) - with two features worked in one clone the end would sit in the other feature's log, and the launch's readers would
/// book the run open to the window's end. A launch no log holds (a run from before this writer, or another clone's) ends beside the
/// prompt, under its feature, task and mark. A notice whose launch line is an Agent call writes none: its `SubagentStop` is its end.
fn bg_end(
    mut end: Map<String, Value>,
    t: &str,
    sid: Value,
    prompt_log: &Path,
    logs: &Path,
    (task, fallback): (Option<String>, bool),
) {
    let id = text_of(end.get("id"));
    let mut row = Map::new();
    row.insert("t".into(), Value::from(t));
    row.insert("sid".into(), sid);
    row.insert("ev".into(), Value::from("BgEnd"));
    row.append(&mut end);
    let to = match launch_line(logs, &id) {
        Some((_, launch)) if launch.get("tool") == Some(&Value::from("Agent")) => return,
        Some((log, launch)) => {
            for key in ["make", "cat", "task", "fallback"] {
                if let Some(v) = launch.get(key) {
                    row.insert(key.into(), v.clone());
                }
            }
            if let Some(t0) = launch.get("t") {
                row.insert("t0".into(), t0.clone());
            }
            log
        }
        None => {
            if let Some(task) = task {
                row.insert("task".into(), Value::from(task));
            }
            if fallback {
                row.insert("fallback".into(), Value::Bool(true));
            }
            prompt_log.to_path_buf()
        }
    };
    let _ = write_line(&to, row);
}

/// The launching call's line for tool-use id `id` and its log: the `PreToolUse` (its start), else the `PostToolUse`, in the first of the
/// logs under `dir` that holds one, the most recently written first (the launch is recent). Each log is scanned for the id's text before
/// any line of it is parsed.
fn launch_line(dir: &Path, id: &str) -> Option<(PathBuf, Map<String, Value>)> {
    let needle = format!("\"id\":{}", Value::from(id));
    let mut logs: Vec<(SystemTime, PathBuf)> = std::fs::read_dir(dir)
        .ok()?
        .filter_map(Result::ok)
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "jsonl"))
        .map(|p| {
            let at = p
                .metadata()
                .and_then(|m| m.modified())
                .unwrap_or(UNIX_EPOCH);
            (at, p)
        })
        .collect();
    logs.sort_by(|a, b| b.0.cmp(&a.0));
    logs.into_iter().find_map(|(_, log)| {
        let text = std::fs::read_to_string(&log).ok()?;
        let hits: Vec<Map<String, Value>> = text
            .lines()
            .filter(|l| l.contains(&needle))
            .filter_map(|l| serde_json::from_str::<Map<String, Value>>(l).ok())
            .filter(|e| e.get("id") == Some(&Value::from(id)))
            .collect();
        ["PreToolUse", "PostToolUse"]
            .iter()
            .find_map(|ev| hits.iter().find(|e| e.get("ev") == Some(&Value::from(*ev))))
            .cloned()
            .map(|e| (log.clone(), e))
    })
}

/// One line appended to a log, its directory made.
fn write_line(path: &Path, row: Map<String, Value>) -> Option<PathBuf> {
    std::fs::create_dir_all(path.parent()?).ok()?;
    let mut text = Value::Object(row).to_string();
    text.push('\n');
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .ok()?
        .write_all(text.as_bytes())
        .ok()?;
    Some(path.to_path_buf())
}

/// A line a gate tool writes in process (feature 451 D4: a make run's `Phase` lines, T05 and T06), through the writer the hooks use: filed
/// by the task it carries as a hook's line is (T26's chain; a line naming none goes to the session's feature, marked), stamped now where
/// it has no `t`, and given the session's id from the process's `CLAUDE_CODE_SESSION_ID` where it names none - a gate tool's line has no
/// hook payload, and a subagent's Bash holds its session's id but no agent's (research R2). A row naming no `ev` writes nothing (T207:
/// a line of no event is no event); None outside a clone the log can be made in.
#[must_use]
pub fn append_row(root: &Path, row: Map<String, Value>) -> Option<PathBuf> {
    append_row_with(root, None, row, &crate::env::opt)
}

/// [`append_row`] for a tool that knows the line's feature (feature 451 T06: a landing's `F=`): filed in the feature `feature` names - a
/// `specs/` directory, or the one `specs/<feature>-*`, read as a make command's `F=` is - before T26's chain asks a task's start, so a
/// landing of a task never started in the clone is filed in its own feature's log, not the session's (where T13 and T14, reading a
/// feature's log for its landings, would not see it). A word naming no one feature leaves the chain as it was.
#[must_use]
pub fn append_row_for(root: &Path, feature: &str, row: Map<String, Value>) -> Option<PathBuf> {
    append_row_with(root, Some(feature), row, &crate::env::opt)
}

/// [`append_row`] (`feature` None) or [`append_row_for`] with its environment given (feature 451 T38): a gate crate's line read through
/// the reader its root carries, so a test's line never reaches a session's exported `L7R_EVENTS_DIR`.
#[must_use]
pub fn append_row_with(
    root: &Path,
    feature: Option<&str>,
    row: Map<String, Value>,
    env: &dyn Fn(&str) -> Option<String>,
) -> Option<PathBuf> {
    append_row_in(root, feature, row, &now_stamp(SystemTime::now()), env)
}

/// One `Phase` line (feature 451 T153: the ONE form every phase writes, the checks' T05 and the landing's T06 built it by hand): `src` the
/// tool, `step` its step, `span` its start and end, `code` its exit, `make` the run's make target (`shared::make::outermost_goal`), and
/// `clone` the tree it ran in - `t` its end, as the readers order it. A writer adds its own fields (a check's `crates`, a landing's
/// `task`, a suite's or a map's `name`) and appends it with [`append_row_with`].
#[must_use]
pub fn phase_row(
    src: &str,
    step: &str,
    span: (SystemTime, SystemTime),
    code: i32,
    make: &str,
    clone: &Path,
) -> Map<String, Value> {
    let t1 = now_stamp(span.1);
    let mut row = Map::new();
    for (k, v) in [
        ("ev", Value::from("Phase")),
        ("src", Value::from(src)),
        ("step", Value::from(step)),
        ("t0", Value::from(now_stamp(span.0))),
        ("t1", Value::from(t1.clone())),
        ("t", Value::from(t1)),
        ("code", Value::from(code)),
        ("make", Value::from(make)),
        ("clone", Value::from(clone.display().to_string())),
    ] {
        row.insert(k.into(), v);
    }
    row
}

pub(crate) fn append_row_in(
    root: &Path,
    feature: Option<&str>,
    mut row: Map<String, Value>,
    t: &str,
    env: &dyn Fn(&str) -> Option<String>,
) -> Option<PathBuf> {
    if text_of(row.get("ev")).is_empty() {
        return None;
    }
    row.entry("t").or_insert_with(|| Value::from(t));
    if !row.get("sid").is_some_and(truthy) {
        let sid = env("CLAUDE_CODE_SESSION_ID").unwrap_or_default();
        row.insert("sid".into(), Value::from(sid));
    }
    let carried = row.get("task").and_then(Value::as_str).map(str::to_owned);
    let to = filed::filed(&Value::Null, carried.as_deref(), feature, root, t, env);
    if let Some(task) = to.task {
        row.insert("task".into(), Value::from(task));
    }
    if to.fallback {
        row.insert("fallback".into(), Value::Bool(true));
    }
    write_line(&log_path_in(root, &to.feature, env), row)
}

/// The payload's line appended now, from the process's directory and environment; nothing for a payload that is no object, which the
/// Python's `payload.get` raised on and its hook swallowed (`event_log.py hook`, feature 449 T119).
pub fn record(payload: &Value) {
    // `shared::env`, here and in the writers above: a test reads its own environment, so a session's exported
    // `L7R_EVENTS_DIR` never takes a test's lines into its real log (feature 451 T32, observed 2026-11-20)
    record_in(payload, &crate::env::opt);
}

/// [`record`] with its environment given (feature 451 T38: the gate's `measure event-log hook`, whose test reads its own).
pub fn record_in(payload: &Value, env: &dyn Fn(&str) -> Option<String>) {
    if payload.is_object() {
        let here = std::env::current_dir().unwrap_or_default();
        let _ = append(payload, &now_stamp(SystemTime::now()), &here, env);
    }
}

// the process's shared session is not asked: its resolve reads the session's name, the whole transcript, on every call (`tree_of`, 451 T74)
fn decide(event: &Event, _session: &Session) -> Vec<Answer> {
    record(&event.input);
    Vec::new()
}

mod dispatches;
mod fields;
mod filed;
pub mod read;

pub use filed::{brief_feature, in_force, started, starts, Start};

#[cfg(test)]
mod tests;
