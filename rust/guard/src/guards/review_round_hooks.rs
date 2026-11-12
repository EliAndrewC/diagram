//! `review-round-hooks` (feature 249; features 251, 253, 266, 295, 379; ported from the shell of the same name and `lib/hm_review_round.py`, feature 449 T045): A SPEC-FIDELITY ROUND AFTER THE FIRST READS
//! THE DIFF, BY THE TOOLING'S HAND (the GM, 2026-09-14: "I want this all to be automatic"). On a later round of a spec review the prompt is rewritten: the round, the previous verdict verbatim, the diff of the
//! feature directory since the last dispatch, then the session's own prompt, and the dispatch is routed to `spec-fidelity-verify`. A MODE 4 plan review and a MODE 1 exception check pass. The old value of
//! something changed is looked for before a round is spent; past the round caps the round arbiter rules. `REVIEW_ROUND_OK`, `STALE_TERMS_OK` and `ARBITER_OK`, each with a reason, are the escapes.

use std::path::{Path, PathBuf};
use std::sync::LazyLock;
use std::time::{SystemTime, UNIX_EPOCH};

use fancy_regex::Regex;
use serde_json::{json, Value};

use crate::guards::agent_prefix_hooks::lines_kept;
use crate::protocol::{Answer, Event, Guard, Reply};
use crate::shared::checks;
use crate::shared::difflib::unified;
use crate::shared::escape::{enough, reason};
use crate::shared::log::{self, civil};
use crate::shared::session::Session;
use crate::shared::state::field;
use crate::shared::tool::ask;

/// The guard.
pub const GUARD: Guard = Guard {
    name: "review-round-hooks",
    events: &["PreToolUse"],
    matcher: "Agent",
    decide,
};

/// A spec review's rounds before the round arbiter rules (feature 379 amendment 2; the five is the GM's 2026-09-12 ruling).
const SPEC_ROUND_CAP: u64 = 5;
/// A plan review's rounds on one task before the round arbiter rules: CLAUDE.md's tripwire, "a check's third round on one subject".
const PLAN_ROUND_CAP: u64 = 2;
const ARBITER_TOKEN: &str = "ARBITER_OK";
const STALE_TOKEN: &str = "STALE_TERMS_OK";
const TOKEN: &str = "REVIEW_ROUND_OK";
const AGENT: &str = "spec-fidelity";
const TWIN: &str = "spec-fidelity-verify";
const VERDICTS: [&str; 3] = ["CHANGES REQUIRED", "FAITHFUL", "NOT-REVIEWABLE"];
const SNAP_SUFFIXES: [&str; 6] = ["md", "json", "txt", "py", "html", "csv"];
/// CONVENTION: the largest file a snapshot holds, as `hm_review_round.py` held it.
const SNAP_MAX_BYTES: u64 = 2_000_000;

fn re(pattern: &str) -> Regex {
    Regex::new(pattern).unwrap_or_else(|e| unreachable!("{e}"))
}

fn hit(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

static FEATURE: LazyLock<Regex> = LazyLock::new(|| re(r"specs/(\d{3}-[a-z0-9][a-z0-9-]*)"));
static SPEC_MODE: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bMODE\s*[23]\b"));
static PLAN_MODE: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bMODE\s*4\b|\bPLAN REVIEW\b"));
static EXCEPTION_MODE: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?i)\bMODE\s*1\b|\bEXCEPTION CHECK\b"));
static MODE_LINE: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^\s*MODE\b[\s:-]*(.*)$"));
static WORD_EXCEPTION: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bEXCEPTION\b"));
static WORD_PLAN: LazyLock<Regex> = LazyLock::new(|| re(r"(?i)\bPLAN\b"));
static REWRITTEN: LazyLock<Regex> =
    LazyLock::new(|| re(r"^MODE 3 \(VERIFY\) - round \d+ of feature (\d{3}-[a-z0-9][a-z0-9-]*)"));
static STATED: LazyLock<Regex> =
    LazyLock::new(|| re(r"[Vv]erdict\W{0,6}(CHANGES REQUIRED|FAITHFUL|NOT-REVIEWABLE)"));
static HISTORY: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^## Review history\s*$"));
static NEXT_SECTION: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^## "));

/// What this guard needs from outside the call: the tree whose `scripts/gates/l7r-gate.sh` it asks.
pub(crate) struct Ctx {
    pub(crate) tree: PathBuf,
}

fn production(tree: PathBuf) -> Ctx {
    Ctx { tree }
}

fn arbiter_trip(root: &Path, trigger: &str, unit: &str, detail: &str) -> String {
    let _ = checks::arbiter::trip(root, trigger, "round", unit, detail, &Value::Null, "");
    checks::arbiter::refusal(&[trigger.to_owned()], None)
}

/// `spec`, `plan` or `exception`, read with precedence: a MODE 2/3 marker wins, then the dispatch's own MODE line, then the contract's heading forms.
pub(crate) fn classify_mode(prompt: &str) -> &'static str {
    if hit(&SPEC_MODE, prompt) {
        return "spec";
    }
    if let Ok(Some(m)) = MODE_LINE.captures(prompt) {
        let words = m.get(1).map_or("", |g| g.as_str());
        if hit(&WORD_EXCEPTION, words) {
            return "exception";
        }
        if hit(&WORD_PLAN, words) {
            return "plan";
        }
    }
    if hit(&PLAN_MODE, prompt) {
        return "plan";
    }
    if hit(&EXCEPTION_MODE, prompt) {
        return "exception";
    }
    "spec"
}

fn group_of(pattern: &Regex, text: &str) -> Option<String> {
    Some(pattern.captures(text).ok()??.get(1)?.as_str().to_owned())
}

fn feature_of(prompt: &str) -> String {
    group_of(&FEATURE, prompt).unwrap_or_default()
}

/// The feature a review's dispatch prompt REVIEWS: a rewritten round names it first; a first round's prompt names it as its first `specs/` path.
fn reviewed_feature(prompt: &str) -> String {
    group_of(&REWRITTEN, prompt.trim_start()).unwrap_or_else(|| feature_of(prompt))
}

fn text_of(content: Option<&Value>) -> String {
    match content {
        Some(Value::String(s)) => s.clone(),
        Some(Value::Array(b)) => b
            .iter()
            .filter(|x| field(x, "type") == "text")
            .map(|x| field(x, "text"))
            .collect::<Vec<_>>()
            .join("\n"),
        _ => String::new(),
    }
}

/// The verdict a reviewer's final message carries: an explicit "Verdict: <word>" line, else the last of the three words.
pub(crate) fn verdict_of(text: &str) -> String {
    if let Some(word) = group_of(&STATED, text) {
        return word;
    }
    let mut best = ("", None);
    for v in VERDICTS {
        let at = text.rfind(v);
        if at > best.1 {
            best = (v, at);
        }
    }
    best.0.to_owned()
}

/// A subagent transcript's lines, newest first in the caller's order; only what can be read.
fn subagent_files(transcript: &str) -> Vec<PathBuf> {
    let Some(stem) = transcript.strip_suffix(".jsonl") else {
        return Vec::new();
    };
    let mut files: Vec<(SystemTime, PathBuf)> =
        std::fs::read_dir(Path::new(stem).join("subagents"))
            .into_iter()
            .flatten()
            .filter_map(Result::ok)
            .filter(|e| {
                let name = e.file_name().to_string_lossy().into_owned();
                name.starts_with("agent-")
                    && Path::new(&name).extension().is_some_and(|e| e == "jsonl")
            })
            .filter_map(|e| Some((e.metadata().ok()?.modified().ok()?, e.path())))
            .collect();
    files.sort_by(|a, b| b.0.cmp(&a.0));
    files.into_iter().map(|(_, p)| p).collect()
}

/// (verdict text, verdict word) from the newest subagent transcript that reviewed this feature.
fn previous_verdict(transcript: &str, feature: &str) -> (String, String) {
    for file in subagent_files(transcript) {
        let bytes = std::fs::read(file).unwrap_or_default();
        let text = String::from_utf8_lossy(&bytes);
        let lines: Vec<&str> = text.lines().filter(|l| !l.trim().is_empty()).collect();
        let Some(first) = lines
            .first()
            .and_then(|l| serde_json::from_str::<Value>(l).ok())
        else {
            continue;
        };
        if reviewed_feature(&text_of(first.pointer("/message/content"))) != feature {
            continue;
        }
        for raw in lines.iter().rev() {
            let Ok(rec) = serde_json::from_str::<Value>(raw) else {
                continue;
            };
            let msg = rec.get("message").cloned().unwrap_or_default();
            let said = text_of(msg.get("content"));
            if field(&msg, "role") != "assistant" || said.trim().is_empty() {
                continue;
            }
            let word = verdict_of(&said);
            if !word.is_empty() {
                return (said, word);
            }
            break;
        }
    }
    (String::new(), String::new())
}

/// The Review history section's last entry, or "" - the fallback when no transcript answers.
fn review_history(spec_md: &Path) -> String {
    let Ok(bytes) = std::fs::read(spec_md) else {
        return String::new();
    };
    let text = String::from_utf8_lossy(&bytes).into_owned();
    let Ok(Some(head)) = HISTORY.find(&text) else {
        return String::new();
    };
    let mut body = &text[head.end()..];
    if let Ok(Some(next)) = NEXT_SECTION.find(body) {
        body = &body[..next.start()];
    }
    let (mut last, mut current): (Option<String>, Option<String>) = (None, None);
    for line in body.split_inclusive('\n') {
        if line.starts_with("- ") {
            last = current.take().or(last);
            current = Some(line.to_owned());
        } else if let Some(entry) = current.as_mut() {
            entry.push_str(line);
        }
    }
    current
        .or(last)
        .map_or_else(String::new, |e| e.trim().to_owned())
}

fn has_review_round(spec_md: &Path) -> bool {
    let entry = review_history(spec_md);
    ["spec-fidelity", "CHANGES REQUIRED", "FAITHFUL"]
        .iter()
        .any(|w| entry.contains(w))
}

/// Each file a snapshot holds, relative to `root`, in order.
fn snap_files(root: &Path) -> Vec<PathBuf> {
    fn walk_into(dir: &Path, root: &Path, out: &mut Vec<PathBuf>) {
        for entry in std::fs::read_dir(dir)
            .into_iter()
            .flatten()
            .filter_map(Result::ok)
        {
            let path = entry.path();
            if path.is_dir() {
                if entry.file_name() != "__pycache__" {
                    walk_into(&path, root, out);
                }
            } else if path
                .extension()
                .is_some_and(|e| SNAP_SUFFIXES.iter().any(|s| e == *s))
                && entry.metadata().is_ok_and(|m| m.len() <= SNAP_MAX_BYTES)
            {
                out.extend(path.strip_prefix(root).ok().map(Path::to_path_buf));
            }
        }
    }
    let mut out = Vec::new();
    walk_into(root, root, &mut out);
    out.sort();
    out
}

fn take_snapshot(feature_dir: &Path, snap: &Path) {
    let _ = std::fs::remove_dir_all(snap);
    for rel in snap_files(feature_dir) {
        let dst = snap.join(&rel);
        if let Some(parent) = dst.parent() {
            let _ = std::fs::create_dir_all(parent);
        }
        let _ = std::fs::copy(feature_dir.join(&rel), dst);
    }
}

/// A file's lines with their endings, as Python reads it in text mode: invalid UTF-8 replaced, every line ending made `\n`.
fn text_lines(path: &Path) -> String {
    let bytes = std::fs::read(path).unwrap_or_default();
    String::from_utf8_lossy(&bytes)
        .replace("\r\n", "\n")
        .replace('\r', "\n")
}

/// The unified diff of the feature directory against its snapshot (T045 decision (c)).
fn diff_since(snap: &Path, feature_dir: &Path) -> String {
    let mut names: Vec<PathBuf> = snap_files(snap);
    names.extend(snap_files(feature_dir));
    names.sort();
    names.dedup();
    let mut out = String::new();
    for rel in names {
        let (old, new) = (
            text_lines(&snap.join(&rel)),
            text_lines(&feature_dir.join(&rel)),
        );
        if old == new {
            continue;
        }
        let shown = rel.to_string_lossy();
        out += &unified(
            &lines_kept(&old),
            &lines_kept(&new),
            &format!("a/{shown}"),
            &format!("b/{shown}"),
        );
    }
    out
}

fn preamble(
    feature: &str,
    round_no: u64,
    new_pass: bool,
    verdict_text: &str,
    verdict_from: &str,
    diff: &str,
) -> String {
    let mut parts = vec![
        format!("MODE 3 (VERIFY) - round {round_no} of feature {feature}, assembled by the tooling at dispatch (rust/guard/src/guards/review_round_hooks.rs, feature 249)."),
        String::new(),
        "THE RULE (the GM, 2026-09-14): a round after the first reviews the paragraphs that changed, not the whole spec. Read ONLY this preamble and the passages a grep of the feature directory for the ids and terms it names turns up. Do not read spec.md, request.md or tasks.md end to end. Where the session's prompt below asks a whole-spec question (every FR has an SC, every task id is defined), answer it from the diff and a grep, never from a re-read. Say which passages you read in full.".to_owned(),
    ];
    if new_pass {
        parts.push(String::new());
        parts.push("This is round 1 of a NEW PASS: the previous verdict was FAITHFUL, so the diff below amends an accepted spec and the five-round cap counts from here (the GM's 2026-09-12 ruling).".to_owned());
    }
    let head = match verdict_from {
        "transcript" => "=== The previous round's verdict, VERBATIM from the reviewer's own transcript ===",
        "history" => "=== The previous round as the SESSION recorded it in the spec's Review history (the reviewer's own words were not recoverable from the transcripts - judge the items against the request, not against this summary) ===",
        _ => "=== No previous verdict could be recovered - the spec's Review history is empty ===",
    };
    let verdict = if verdict_text.trim().is_empty() {
        "(none)"
    } else {
        verdict_text.trim()
    };
    let body = if diff.trim().is_empty() {
        "Nothing in the feature directory changed since the previous dispatch."
    } else {
        diff.trim()
    };
    parts.extend([String::new(), head.to_owned(), String::new(), verdict.to_owned(), String::new(), format!("=== What changed in specs/{feature} since that round was dispatched (unified diff) ==="), String::new(), body.to_owned(), String::new(), "=== The session's prompt follows ===".to_owned(), String::new()]);
    parts.join("\n")
}

fn no_reason(token: &str) -> String {
    format!(
        "BLOCKED: {token} with no reason given.\n\nAn escape is a workaround, and a workaround nobody can audit is indistinguishable from the\nrule not existing. Say why, in the prompt, and it ships with it:\n\n    {token}=\"<why this dispatch needs the whole spec read again>\"\n\nTwo words and eight characters is the whole bar - \"restructured spec\" clears it.\n(GM 2026-08-30, feature 170; the reasons are what `make audit` shows you.)\n"
    )
}

fn stale_refusal(feature: &str, rendered: &str) -> String {
    let number = feature.split('-').next().unwrap_or(feature);
    format!(
        "\n\u{1b}[1mBLOCKED: specs/{feature} still carries the OLD value of something this change moved - look before a review round is spent on it.\u{1b}[0m\n{rendered}\n\nA later spec-fidelity round costs nearly what a first reading does, and the commonest thing it finds is text left saying the\nold thing (feature 253, the GM 2026-09-19). Nothing was dispatched and no round was counted. Either:\n  - fix the lines above (and anything else the change made untrue), then dispatch again; or\n  - if they are NOT stale, dispatch again with {STALE_TOKEN}=\"<why they stand>\" in the prompt.\n`make stale-terms F={number}` re-runs the search. (scripts/reviews/stale_terms.py, rust/guard/src/guards/review_round_hooks.rs)\n"
    )
}

fn read_number(path: &Path) -> Option<u64> {
    std::fs::read_to_string(path).ok()?.trim().parse().ok()
}

fn read_round(state: &Path) -> u64 {
    read_number(&state.join("round")).unwrap_or(0)
}

fn read_pass(state: &Path) -> u64 {
    read_number(&state.join("pass")).unwrap_or(1)
}

fn write_state(state: &Path, round_no: u64) {
    let _ = std::fs::create_dir_all(state);
    let _ = std::fs::write(state.join("round"), format!("{round_no}\n"));
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    let (y, mo, d, h, mi, s) = civil(secs);
    let _ = std::fs::write(
        state.join("dispatched"),
        format!("{y:04}-{mo:02}-{d:02}T{h:02}:{mi:02}:{s:02}Z\n"),
    );
}

fn write_pass(state: &Path, pass_no: u64) {
    let _ = std::fs::write(state.join("pass"), format!("{pass_no}\n"));
}

fn spec_cap_prefix(feature: &str, pass_no: u64) -> String {
    format!("round:spec-fidelity|{feature}#{pass_no}@")
}

/// Why a spec review's round waits for the round arbiter, or "". Each `continue` on this pass lifts its cap by one round.
fn spec_cap_refusal(root: &Path, feature: &str, round_no: u64, pass_no: u64) -> String {
    if round_no <= SPEC_ROUND_CAP {
        return String::new();
    }
    let prefix = spec_cap_prefix(feature, pass_no);
    let lifted: u64 = checks::arbiter::continues(root, &prefix, 0);
    if round_no - SPEC_ROUND_CAP <= lifted {
        return String::new();
    }
    let trigger = format!("{prefix}{round_no}");
    let refusal = arbiter_trip(
        root,
        &trigger,
        &format!("spec-fidelity|{feature}"),
        &format!("round {round_no} of specs/{feature}'s spec review"),
    );
    format!("BLOCKED: round {round_no} of specs/{feature}'s spec review - past the five-round cap the round arbiter rules, not the GM (feature 379). Nothing was dispatched and no round was counted.\n{refusal}")
}

/// The rounds `task`'s plan blocks have had since their last CLEAR.
pub(crate) fn plan_rounds(feature_dir: &Path, task: &str) -> u64 {
    let Some(doc) = std::fs::read_to_string(feature_dir.join("plan-review.json"))
        .ok()
        .and_then(|t| serde_json::from_str::<Value>(&t).ok())
    else {
        return 0;
    };
    let head = re(&format!(r"^#{{2,4}}\s+{}\b", fancy_regex::escape(task)));
    let reviews = doc
        .get("block_reviews")
        .and_then(Value::as_array)
        .map_or(&[][..], Vec::as_slice);
    let names = |r: &&Value| {
        r.get("blocks")
            .and_then(Value::as_array)
            .is_some_and(|b| b.iter().filter_map(Value::as_str).any(|s| hit(&head, s)))
    };
    let n = reviews
        .iter()
        .rev()
        .filter(names)
        .take_while(|r| field(r, "verdict") != "CLEAR")
        .count();
    u64::try_from(n).unwrap_or(0)
}

/// Why the active task's next plan round waits for the round arbiter, or "".
fn plan_cap_refusal(root: &Path, ctx: &Ctx) -> String {
    // the active feature's directory and task, `[dir, task]` from the plan gate (`l7r-gate plan door active-task`), asked directly: an
    // inline python3 snippet only ran that command and read its JSON, starting Python on each spec-fidelity dispatch (feature 449 T141);
    // a failed run, unreadable JSON, a null directory or an empty task hold nothing, as the snippet's did
    let gate = ctx.tree.join("scripts/gates/l7r-gate.sh");
    let said = ask(
        root,
        &gate.to_string_lossy(),
        &["plan", "door", "active-task", &root.to_string_lossy()],
        "",
    );
    let pair: Value = if said.code == 0 {
        serde_json::from_str(&said.out).unwrap_or(Value::Null)
    } else {
        Value::Null
    };
    let (Some(dir), Some(task)) = (pair[0].as_str(), pair[1].as_str()) else {
        return String::new();
    };
    if task.is_empty() {
        return String::new();
    }
    let d = Path::new(dir);
    let round_no = plan_rounds(d, task) + 1;
    if round_no <= PLAN_ROUND_CAP {
        return String::new();
    }
    let name = d
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let prefix = format!("round:spec-fidelity|plan:{name}#{task}@");
    let lifted: u64 = checks::arbiter::continues(root, &prefix, 0);
    if round_no - PLAN_ROUND_CAP <= lifted {
        return String::new();
    }
    let trigger = format!("{prefix}{round_no}");
    let refusal = arbiter_trip(
        root,
        &trigger,
        &format!("spec-fidelity|plan:{name}#{task}"),
        &format!("round {round_no} of {task}'s plan review"),
    );
    format!("BLOCKED: round {round_no} of {task}'s plan review - a check's third round on one subject owes the round arbiter's ruling first (CLAUDE.md, the tripwires). Nothing was dispatched.\n{refusal}")
}

/// One branch's record and answer.
pub(crate) struct Outcome {
    pub(crate) event: &'static str,
    pub(crate) rule: String,
    pub(crate) detail: String,
    pub(crate) answer: Vec<Answer>,
}

fn outcome(event: &'static str, rule: &str, detail: impl Into<String>) -> Outcome {
    Outcome {
        event,
        rule: rule.to_owned(),
        detail: detail.into(),
        answer: Vec::new(),
    }
}

fn refused(rule: &str, detail: impl Into<String>, text: String) -> Outcome {
    Outcome {
        answer: vec![Answer::Refuse(text)],
        ..outcome("blocked", rule, detail)
    }
}

fn accepted_pass(input: &Value, feature: &str, spec_md: &Path, root: &Path, state: &Path) -> bool {
    let (text, word) = previous_verdict(field(input, "transcript_path"), feature);
    let word = if text.is_empty() {
        let entry = review_history(spec_md);
        if entry.is_empty() {
            String::new()
        } else {
            verdict_of(&entry)
        }
    } else {
        word
    };
    word == "FAITHFUL"
        || !checks::arbiter::closed(root, &spec_cap_prefix(feature, read_pass(state)), None)
            .is_empty()
}

fn first_chars(text: &str, n: usize) -> String {
    text.chars().take(n).collect()
}

fn later_round(
    input: &Value,
    ti: &Value,
    prompt: &str,
    feature: &str,
    root: &Path,
    dirs: (&Path, &Path, &Path),
    ctx: &Ctx,
) -> Outcome {
    let (feature_dir, state, snap) = dirs;
    let spec_md = feature_dir.join("spec.md");
    let (mut text, mut word) = previous_verdict(field(input, "transcript_path"), feature);
    let mut from = if text.is_empty() { "" } else { "transcript" };
    if text.is_empty() {
        text = review_history(&spec_md);
        if !text.is_empty() {
            from = "history";
            word = verdict_of(&text);
        }
    }
    let prev_round = Some(read_round(state)).filter(|r| *r > 0).unwrap_or(1);
    if word == "NOT-REVIEWABLE" && prev_round <= 1 {
        take_snapshot(feature_dir, snap);
        write_state(state, 1);
        return outcome("permitted", "first-reading-after-not-reviewable", feature);
    }
    let mut note = String::new();
    if prompt.contains(STALE_TOKEN) {
        let why = reason(prompt, STALE_TOKEN);
        if !enough(&why) {
            return refused(
                &format!("{STALE_TOKEN}-no-reason"),
                first_chars(prompt, 200),
                no_reason(STALE_TOKEN),
            );
        }
        note = format!(" {STALE_TOKEN}: {why}");
    } else {
        let gate = ctx.tree.join("scripts/gates/l7r-gate.sh");
        let said = ask(
            root,
            &gate.to_string_lossy(),
            &[
                "record",
                "stale-dirs",
                &snap.to_string_lossy(),
                &feature_dir.to_string_lossy(),
            ],
            "",
        );
        if let Some((count, rendered)) = said.out.split_once('\n') {
            return refused(
                "stale-terms",
                format!("{feature}: {count} candidate(s)"),
                stale_refusal(feature, rendered),
            );
        }
    }
    let diff = diff_since(snap, feature_dir);
    let closed = !checks::arbiter::closed(root, &spec_cap_prefix(feature, read_pass(state)), None)
        .is_empty();
    let new_pass = word == "FAITHFUL" || closed;
    let round_no = if new_pass {
        1
    } else if word == "NOT-REVIEWABLE" {
        prev_round
    } else {
        prev_round + 1
    };
    let pass_no = read_pass(state) + u64::from(new_pass);
    let held = spec_cap_refusal(root, feature, round_no, pass_no);
    if !held.is_empty() {
        let why = reason(prompt, ARBITER_TOKEN);
        if !enough(&why) {
            return refused(
                "spec-round-cap",
                format!("{feature} round {round_no}"),
                held,
            );
        }
        note = format!("{note} {ARBITER_TOKEN}: {why}");
    }
    let new_prompt = preamble(feature, round_no, new_pass, &text, from, &diff) + prompt;
    take_snapshot(feature_dir, snap);
    write_state(state, round_no);
    write_pass(state, pass_no);
    let mut updated = ti.clone();
    updated["prompt"] = json!(new_prompt);
    updated["subagent_type"] = json!(TWIN);
    let context = format!("review-round: this dispatch was rewritten into MODE 3 round {round_no} of specs/{feature} and ROUTED to `{TWIN}` (the same review's later-round contract - feature 251, the GM 2026-09-19) (feature 249, the GM 2026-09-14): the previous round's verdict and the diff of the feature directory since that dispatch were prepended, and the reviewer is told to read those plus grep hits only. Your own prompt follows them unchanged. For a deliberate full re-read, put {TOKEN}=\"<reason>\" in the prompt.");
    let rule = if note.is_empty() {
        "mode-3-preamble"
    } else {
        "mode-3-preamble-stale-ok"
    };
    Outcome {
        answer: vec![Answer::Rewrite(updated), Answer::Notice(context)],
        ..outcome("rewrote", rule, format!("{feature} round {round_no}{note}"))
    }
}

fn plan_gate_outcome(prompt: &str, root: &Path, ctx: &Ctx) -> Option<Outcome> {
    let held = plan_cap_refusal(root, ctx);
    if held.is_empty() {
        return None;
    }
    let why = reason(prompt, ARBITER_TOKEN);
    if enough(&why) {
        return Some(outcome("escaped", "plan-round-cap", why));
    }
    let first = first_chars(held.lines().next().unwrap_or(""), 200);
    Some(refused("plan-round-cap", first, held))
}

fn escaped(input: &Value, prompt: &str, feature: &str, root: Option<&Path>) -> Outcome {
    let why = reason(prompt, TOKEN);
    if !enough(&why) {
        return refused(
            &format!("{TOKEN}-no-reason"),
            first_chars(prompt, 200),
            no_reason(TOKEN),
        );
    }
    if let Some(root) = root {
        let feature_dir = root.join("specs").join(feature);
        if !feature.is_empty() && feature_dir.is_dir() {
            let state = root.join(".git/review-round").join(feature);
            take_snapshot(&feature_dir, &state.join("snapshot"));
            if accepted_pass(input, feature, &feature_dir.join("spec.md"), root, &state) {
                write_state(&state, 1);
                write_pass(&state, read_pass(&state) + 1);
            } else {
                write_state(
                    &state,
                    Some(read_round(&state)).filter(|r| *r > 0).unwrap_or(1),
                );
            }
        }
    }
    outcome("escaped", "review-round-ok", why)
}

/// The whole decision, or None for a call this guard has nothing to say of.
pub(crate) fn verdict(input: &Value, tool: &str, clone: &str, ctx: &Ctx) -> Option<Outcome> {
    let null = Value::Null;
    let ti = input.get("tool_input").unwrap_or(&null);
    if tool != "Agent" || ![AGENT, TWIN].contains(&field(ti, "subagent_type")) {
        return None;
    }
    let prompt = field(ti, "prompt");
    let mode = classify_mode(prompt);
    let root = Some(Path::new(clone)).filter(|_| !clone.is_empty());
    if mode == "plan" {
        if let Some(found) = root.and_then(|r| plan_gate_outcome(prompt, r, ctx)) {
            return Some(found);
        }
    }
    if mode != "spec" {
        return Some(outcome(
            "permitted",
            "other-mode",
            format!("{mode} review passes untouched"),
        ));
    }
    let feature = feature_of(prompt);
    if prompt.contains(TOKEN) {
        return Some(escaped(input, prompt, &feature, root));
    }
    let Some(root) =
        root.filter(|r| !feature.is_empty() && r.join("specs").join(&feature).is_dir())
    else {
        let detail = if feature.is_empty() {
            "no specs/NNN-slug in the prompt".to_owned()
        } else {
            feature
        };
        return Some(outcome("permitted", "no-feature", detail));
    };
    let feature_dir = root.join("specs").join(&feature);
    let state = root.join(".git/review-round").join(&feature);
    let snap = state.join("snapshot");
    if !snap.is_dir() {
        take_snapshot(&feature_dir, &snap);
        write_state(&state, 1);
        if has_review_round(&feature_dir.join("spec.md")) {
            let context = format!("review-round: specs/{feature} already records a review round, but the tooling holds no earlier snapshot of it to diff against, so this dispatch is not rewritten. This is a round after the first: dispatch `{TWIN}` (the later-round contract) rather than `{AGENT}`, and make sure the prompt carries the previous round's items and ONLY the passages that changed. From this dispatch on the tooling snapshots the directory and builds the diff itself.");
            return Some(Outcome {
                answer: vec![Answer::Notice(context)],
                ..outcome("reminded", "history-without-snapshot", feature)
            });
        }
        return Some(outcome("permitted", "first-round", feature));
    }
    Some(later_round(
        input,
        ti,
        prompt,
        &feature,
        root,
        (&feature_dir, &state, &snap),
        ctx,
    ))
}

/// This session's clone as the guard resolved it, else the work tree `cwd` stands in.
fn clone_for(event: &Event, session: &Session) -> String {
    if let Some(dir) = session.clone_dir().filter(|d| d.is_dir()) {
        return dir.to_string_lossy().into_owned();
    }
    let given = field(&event.input, "cwd");
    let at = if given.is_empty() { "." } else { given };
    let said = ask(
        Path::new("."),
        "git",
        &["-C", at, "rev-parse", "--show-toplevel"],
        "",
    );
    if said.ok() {
        said.out.trim().to_owned()
    } else {
        String::new()
    }
}

pub(crate) fn answer(event: &Event, session: &Session, clone: &str, ctx: &Ctx) -> Vec<Answer> {
    let Some(found) = verdict(&event.input, event.tool(), clone, ctx) else {
        return Vec::new();
    };
    let detail = found.detail.replace(['\t', '\n'], " ");
    log::fire(
        "review-round",
        found.event,
        &detail,
        &found.rule,
        &event.input,
        session,
    );
    found.answer
}

fn decide(event: &Event, session: &Session) -> Vec<Answer> {
    if event.tool() != "Agent" {
        return Vec::new();
    }
    let here = std::env::current_dir().unwrap_or_default();
    let tree = std::env::var("L7R_GUARD_TREE").map_or(here, PathBuf::from);
    answer(
        event,
        session,
        &clone_for(event, session),
        &production(tree),
    )
}

/// The guard's entries that are no hook event: `state <clone> <feature>`, `verdict-of <text>`.
#[must_use]
pub fn cli(args: &[String]) -> Reply {
    let say = |stdout: String, code: i32| Reply {
        stdout,
        stderr: String::new(),
        code,
    };
    let arg = |i: usize| args.get(i).map_or("", String::as_str);
    match arg(0) {
        "state" => {
            let state = Path::new(arg(1)).join(".git/review-round").join(arg(2));
            let snapshot = if state.join("snapshot").is_dir() {
                "yes"
            } else {
                "no"
            };
            say(
                format!("round={} snapshot={snapshot}", read_round(&state)),
                0,
            )
        }
        "verdict-of" => say(verdict_of(arg(1)), 0),
        other => say(
            format!("review-round-hooks: unknown mode '{other}' (want: state <clone> <feature>)"),
            1,
        ),
    }
}

#[cfg(test)]
mod tests;
