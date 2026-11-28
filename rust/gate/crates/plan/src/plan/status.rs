//! Which blocks of a plan a review still owes, and what a feature owes before a tick (feature 449 T066, from `plan_sections.py` and
//! `plan_gate.py`). A review of a plan keeps a verdict per block (feature 375 amendment 11, D60), and only a block added or changed
//! since its CLEAR verdict is owed: sixteen whole-plan reviews of 374 cost 13.7 million input tokens (observed 2026-10-13, method: the
//! review ledger), each re-judging every earlier decision because one edit outside a task's section staled the whole plan's verdict.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use serde_json::{json, Map, Value};

use super::history::History;
use super::sections::{
    below_heading, block_digest, blocks, decides_nothing, digest, heading_text,
    lands_open_appended, leading_task, leading_tasks, quiet_out, repointed, stem, strip_archive,
    task_sections, typo_only, wording_only, PART_B,
};

pub(super) const RECORD: &str = "plan-review.json";
pub(super) const REMOVED: &str = "(removed) ";
/// A ticked box of tasks.md or tasks-done.md and its id.
static TICKED: std::sync::LazyLock<fancy_regex::Regex> =
    std::sync::LazyLock::new(|| super::sections::re(r"(?m)^\s*- \[[xX]\] (T\d+[a-z]?)\b"));
const HOW: &str = "dispatch `spec-fidelity` in its PLAN REVIEW mode with request.md, spec.md and plan.md, then record its JSON: make plan-verdict F=<feature> FILE=<json> AS=spec-fidelity";

pub(super) fn text_of<'v>(value: &'v Value, key: &str) -> Option<&'v str> {
    value.get(key).and_then(Value::as_str)
}

/// A value as Python's `str()` prints it for a digest lookup: a string as itself, a missing one as `None`.
fn sha_of(entry: &Value) -> Option<String> {
    entry
        .get("sha256")
        .filter(|v| truthy(v))
        .map(|v| v.as_str().map_or_else(|| v.to_string(), str::to_owned))
}

fn truthy(value: &Value) -> bool {
    !matches!(value, Value::Null | Value::Bool(false))
        && value != ""
        && value != 0
        && value.as_array().is_none_or(|a| !a.is_empty())
}

/// The block's earlier text: as the record kept it, or from the plan's history at its recorded digest.
fn earlier_text(entry: &Value, key: &str, history: Option<&History>) -> Option<String> {
    if let Some(kept) = text_of(entry, "text").filter(|t| !t.is_empty()) {
        return Some(kept.to_owned());
    }
    history?.block(key, &sha_of(entry)?)
}

/// Whether the task's section carries a CLEAR decision verdict that still matches it, a typo aside.
pub(super) fn task_current(
    review: &Value,
    plan: &str,
    task: &str,
    history: Option<&History>,
) -> bool {
    task_sections(plan)
        .get(task)
        .is_some_and(|section| section_current(review, plan, task, section, history))
}

/// [`task_current`] of `task`'s `section`, as [`task_sections`] cut it from `plan`: a caller judging many sections parses them once
/// (451 T466).
pub(super) fn section_current(
    review: &Value,
    plan: &str,
    task: &str,
    section: &str,
    history: Option<&History>,
) -> bool {
    let empty = json!({});
    let entry = review
        .get("tasks")
        .and_then(|t| t.get(task))
        .unwrap_or(&empty);
    if text_of(entry, "verdict") != Some("CLEAR") {
        return false;
    }
    let recorded = text_of(entry, "section_sha256").unwrap_or("");
    if recorded == digest(section.as_bytes()) {
        return true;
    }
    let section = strip_archive(section);
    let kept = text_of(entry, "section_text")
        .filter(|t| !t.is_empty())
        .map(str::to_owned);
    let Some(earlier) = kept.or_else(|| history?.section(task, recorded)) else {
        return false;
    };
    let (was, now) = (
        quiet_out(&strip_archive(&earlier), plan),
        quiet_out(&section, plan),
    );
    let done = history
        .and_then(|h| h.path().parent().map(super::once::plan_done))
        .unwrap_or_default();
    typo_only(&was, &now) || typo_only(&repointed(&was, &now, task, &format!("{plan}{done}")), &now)
}

/// `{key: {sha256, verdict}}` the record holds: its `blocks`, or, a record from before amendment 11, its one verdict on each block.
pub(super) fn reviewed_blocks(review: &Value) -> Map<String, Value> {
    if let Some(have) = review.get("blocks").and_then(Value::as_object) {
        return have.clone();
    }
    let Some(text) = text_of(review, "plan_text") else {
        return Map::new();
    };
    let verdict = review.get("verdict").cloned().unwrap_or(Value::Null);
    blocks(text)
        .into_iter()
        .map(|(k, body, _)| {
            (
                k,
                json!({"sha256": block_digest(&body), "verdict": verdict, "text": body}),
            )
        })
        .collect()
}

/// The recorded entry this block was moved from: a recorded heading of the same stem, with the same text below its heading line.
fn moved_from(
    have: &Map<String, Value>,
    key: &str,
    body: &str,
    history: Option<&History>,
) -> Option<Value> {
    have.iter()
        .filter(|(k, e)| *k != key && e.is_object() && stem(k) == stem(key))
        .find_map(|(k, e)| {
            let earlier = earlier_text(e, k, history)?;
            (below_heading(&earlier) == below_heading(body)).then(|| {
                let mut moved = e.clone();
                moved["moved"] = json!(true);
                moved
            })
        })
}

fn span_of(plan: &str, section: &str) -> Option<(usize, usize)> {
    plan.find(section).map(|at| (at, at + section.len()))
}

fn inside(spans: &[(usize, usize)], at: usize) -> bool {
    spans.iter().any(|(lo, hi)| *lo <= at && at < *hi)
}

/// (the blocks owed a review, the blocks BLOCKED): every block outside a task section with its own current verdict, judged against the
/// record's verdict at its digest, a typo-scale change aside. A recorded block plan.md no longer has is owed too, as `(removed) <key>`,
/// unless `plan-done.md` holds it.
pub(super) fn block_status(
    review: &Value,
    plan: &str,
    ruled: &BTreeSet<String>,
    history: Option<&History>,
    done: &str,
) -> (Vec<String>, Vec<String>) {
    block_status_of(review, plan, &task_sections(plan), ruled, history, done)
}

/// [`block_status`] over `plan`'s `sections`, parsed once by its caller (451 T466).
pub(super) fn block_status_of(
    review: &Value,
    plan: &str,
    sections: &BTreeMap<String, String>,
    ruled: &BTreeSet<String>,
    history: Option<&History>,
    done: &str,
) -> (Vec<String>, Vec<String>) {
    let out_of: Vec<(usize, usize)> = sections
        .iter()
        .filter(|(t, _)| ruled.contains(*t))
        .filter_map(|(_, s)| span_of(plan, s))
        .collect();
    let words: Vec<(usize, usize)> = sections
        .values()
        .filter(|s| wording_only(s))
        .filter_map(|s| span_of(plan, s))
        .collect();
    let have = reviewed_blocks(review);
    let (mut owed, mut blocked) = (Vec::new(), Vec::new());
    let empty = json!({});
    let now_blocks = blocks(plan);
    for (key, body, at) in &now_blocks {
        let part_b = PART_B.is_match(key).unwrap_or(false);
        if inside(&out_of, *at)
            || (!part_b && inside(&words, *at))
            || (key == "preamble" && strip_archive(body).trim().is_empty())
            || decides_nothing(key, body, plan, done)
        {
            continue;
        }
        let moved = if have.contains_key(key) {
            None
        } else {
            moved_from(&have, key, body, history)
        };
        let entry = have.get(key).or(moved.as_ref()).unwrap_or(&empty);
        if text_of(entry, "sha256") != Some(block_digest(body).as_str())
            && entry.get("moved").is_none()
        {
            let earlier = earlier_text(entry, key, history);
            let was = strip_archive(earlier.as_deref().unwrap_or(""));
            let current =
                strip_archive(&lands_open_appended(earlier.as_deref().unwrap_or(""), body));
            let title = heading_text(key);
            let own = leading_task(&title);
            let forgiven = earlier.is_some()
                && (typo_only(&was, &current)
                    || own.is_some_and(|t| {
                        typo_only(
                            &repointed(&was, &current, t, &format!("{plan}{done}")),
                            &current,
                        )
                    }));
            if !forgiven {
                owed.push(key.clone());
                continue;
            }
        }
        match text_of(entry, "verdict") {
            Some("BLOCKED") => blocked.push(key.clone()),
            Some("CLEAR") => {}
            _ => owed.push(key.clone()),
        }
    }
    owed.extend(removed_blocks(&have, &now_blocks, history, done));
    (owed, blocked)
}

/// The tasks whose own blocks are, every one, a block of the task's unfilled `make task-add` stub ([`super::template::stub_block`]):
/// sections nobody has written (451 T462). A bundle's heading is no task's stub, and one block written makes the whole section written.
pub(super) fn unwritten(plan: &str) -> BTreeSet<String> {
    let mut own: BTreeMap<String, bool> = BTreeMap::new();
    for (key, body, _) in blocks(plan) {
        let title = heading_text(&key);
        if let [task] = leading_tasks(&title)[..] {
            let stub = super::template::stub_block(task, &body);
            *own.entry(task.to_owned()).or_insert(true) &= stub;
        }
    }
    own.into_iter()
        .filter(|(_, s)| *s)
        .map(|(t, _)| t)
        .collect()
}

/// `keys` without the blocks of an unwritten section ([`unwritten`]) but those of `kept`'s tasks. WHY (the round arbiter's process-fault
/// on `round:spec-fidelity|plan:451-time-retro-and-efficiency#T448@3`, 2026-11-27): T448's section, the template verbatim, was owed
/// in every `make plan-delta F=451` bundle, four reviewers ruled that it decided nothing, and those four rounds held every plan-delta
/// dispatch of the feature. A stub decides nothing until it is written; the tick of its own task still owes it (`kept`).
pub(super) fn written_only(keys: Vec<String>, plan: &str, kept: &BTreeSet<String>) -> Vec<String> {
    let blank = unwritten(plan);
    if blank.is_empty() {
        return keys;
    }
    keys.into_iter()
        .filter(|key| {
            let title = heading_text(key);
            !matches!(&leading_tasks(&title)[..], [t] if blank.contains(*t) && !kept.contains(*t))
        })
        .collect()
}

/// Each recorded block plan.md no longer has and the archive does not hold, as `(removed) <key>`: an archived block is judged as a live
/// one is (feature 385 T65), and a re-dated heading is the same block (feature 444 T20, D4).
fn removed_blocks(
    have: &Map<String, Value>,
    now_blocks: &[(String, String, usize)],
    history: Option<&History>,
    done: &str,
) -> Vec<String> {
    let mut owed = Vec::new();
    let done_blocks = if done.is_empty() {
        Vec::new()
    } else {
        blocks(done)
    };
    let archived: BTreeSet<String> = done_blocks
        .iter()
        .map(|(_, b, _)| block_digest(b))
        .collect();
    let done_text: BTreeMap<&str, &str> = done_blocks
        .iter()
        .map(|(k, b, _)| (k.as_str(), b.as_str()))
        .collect();
    let current: BTreeSet<&str> = now_blocks.iter().map(|(k, ..)| k.as_str()).collect();
    let live: BTreeSet<(String, String)> = now_blocks
        .iter()
        .chain(&done_blocks)
        .map(|(k, b, _)| (stem(k), below_heading(b)))
        .collect();
    for (key, entry) in have {
        let sha = text_of(entry, "sha256").unwrap_or("");
        if current.contains(key.as_str())
            || key == "preamble"
            || !entry.is_object()
            || (!sha.is_empty() && archived.contains(sha))
        {
            continue;
        }
        let earlier = earlier_text(entry, key, history);
        if let Some(text) = &earlier {
            if live.contains(&(stem(key), below_heading(text))) {
                continue;
            }
            if done_text
                .get(key.as_str())
                .is_some_and(|d| typo_only(&strip_archive(text), &strip_archive(d)))
            {
                continue;
            }
        }
        owed.push(format!("{REMOVED}{key}"));
    }
    owed
}

/// Every task whose section carries its own current verdict, each judged on its section of `sections`, `plan`'s parsed once. WHY
/// (451 T466): each task's judgment parsed every section again to find its own, about 1.8 s a whole-plan judgment over a 1 MB plan.md
/// of some 300 sections, measured 2026-11-27 (an Instant trace of `l7r-gate tick --land-check` over a scratch clone of diagram-backlog).
pub(super) fn ruled_tasks(
    review: &Value,
    plan: &str,
    sections: &BTreeMap<String, String>,
    history: Option<&History>,
) -> BTreeSet<String> {
    sections
        .iter()
        .filter(|(t, s)| section_current(review, plan, t, s, history))
        .map(|(t, _)| t.clone())
        .collect()
}

/// (rule, reason) when a feature owes a plan review, from the plan's bytes and the record's text.
pub(super) fn judge(
    plan: Option<&[u8]>,
    review_text: Option<&str>,
    history: Option<&History>,
    done: &str,
) -> Option<(&'static str, String)> {
    judge_in(plan, review_text, history, done, None)
}

/// What a judgment answers for: the tasks in its scope, and those of them closed by `make task-withdraw` ([`scope_of`]).
pub(super) struct Scope {
    tasks: BTreeSet<String>,
    withdrawn: BTreeSet<String>,
}

/// The tasks a tick of `asked` answers for (feature 451 T84): `asked` and every task ticked before it - a `[x]` box of `tasks`, the
/// feature's tasks.md and tasks-done.md joined. A box ticked by `make task-withdraw` (`Withdrawn YYYY-MM-DD:`, 451 T359) is among
/// them and named apart: nothing was decided in its section, so its removed stub - where a review had recorded it - holds no tick
/// and no push ([`in_scope`]), while a block that names it and has no other owner is answered for as any ticked task's is, and so
/// is a removed block of its own that was NOT the unfilled stub (a box written by hand in that form, its filled section deleted).
pub(super) fn scope_of(tasks: &str, asked: &[&str]) -> Scope {
    let ticked = |l: &str| TICKED.captures(l).ok().flatten().map(|c| c[1].to_owned());
    let boxes = tasks.lines().filter_map(|l| ticked(l).map(|t| (t, l)));
    let (mut all, mut withdrawn) = (BTreeSet::new(), BTreeSet::new());
    for (task, line) in boxes {
        // ...and a box ticked built inside another task's section (451 T307 part 2): its own section was never decided either
        if l7r_shared::speckit::withdrawn_box(line)
            || super::inside::built_inside_box(line).is_some()
        {
            withdrawn.insert(task.clone());
        }
        all.insert(task);
    }
    all.extend(asked.iter().map(|t| (*t).to_owned()));
    Scope {
        tasks: all,
        withdrawn,
    }
}

/// [`owed`] for a tick of `asked` alone (feature 451 T84): the blocks outside every task's section, and the sections of `asked` and of
/// the tasks ticked before it ([`scope_of`]).
pub(super) fn owed_for(spec_dir: &Path, asked: &[&str]) -> Option<(&'static str, String)> {
    held_for(spec_dir, asked).map(|(rule, reason, _)| (rule, reason))
}

/// [`owed_for`] with the blocks the judgment listed ([`judge_held`]), which an honored escape's record carries (feature 451 T262).
pub(super) fn held_for(spec_dir: &Path, asked: &[&str]) -> Option<Held> {
    held_in(spec_dir, asked, None)
}

/// The part of a tick's plan judgment that no task changes - the plan, its review record and plan-done.md read and judged
/// ([`Base`]) - kept for every tick asked through it (451 T464). WHY: the first pass of a landing (`tick::checks` in the task
/// crate) judged the whole plan again for each of its tasks, about 2.4 s a task over a 1 MB plan.md of 675 blocks: 92 s of the 06:43Z
/// batch's 35 tasks, measured 2026-11-27 (an Instant trace per call over a scratch clone of diagram-backlog). One is made for one
/// `checks` call, which writes nothing the judgment reads, and dropped with it; a tick that writes (the tick itself, its archive)
/// asks without one, so a judgment never outlives the files it read.
#[derive(Default)]
pub struct Shared(std::cell::OnceCell<Base>);

/// [`held_for`], the task-free judgment taken from `shared` where one is given and made there on its first ask.
pub(super) fn held_in(spec_dir: &Path, asked: &[&str], shared: Option<&Shared>) -> Option<Held> {
    let plan_path = spec_dir.join("plan.md");
    let history = History::new(&plan_path, "HEAD");
    let judged = || {
        let plan = std::fs::read(&plan_path).ok();
        let review = std::fs::read_to_string(spec_dir.join(RECORD)).ok();
        let done = l7r_shared::speckit::archive::plan_done(spec_dir);
        base(plan.as_deref(), review.as_deref(), Some(&history), &done)
    };
    let owned;
    let base = if let Some(s) = shared {
        s.0.get_or_init(judged)
    } else {
        owned = judged();
        &owned
    };
    let tasks = l7r_shared::speckit::tasks::joined(
        &std::fs::read_to_string(spec_dir.join("tasks.md")).unwrap_or_default(),
        &l7r_shared::speckit::tasks::done_text(spec_dir).unwrap_or_default(),
    );
    finish(base, Some(&history), Some(&scope_of(&tasks, asked)))
}

/// What [`in_scope`] reads of a plan and its record whatever the scope (451 T464): the recorded blocks, each task section's place and
/// whether it is its task's own (its first heading opens with the id) or a heading that only names it, and each block's offset.
pub(super) struct Layout {
    have: Map<String, Value>,
    spans: Vec<(String, bool, (usize, usize))>,
    offsets: BTreeMap<String, usize>,
}

impl Layout {
    fn of(review: &Value, plan: &str, sections: &BTreeMap<String, String>) -> Self {
        let spans = sections
            .iter()
            .filter_map(|(t, s)| {
                let first = heading_text(s.lines().next().unwrap_or_default());
                let own = leading_tasks(&first).contains(&t.as_str());
                span_of(plan, s).map(|at| (t.clone(), own, at))
            })
            .collect();
        let offsets = blocks(plan).into_iter().map(|(k, _, at)| (k, at)).collect();
        Self {
            have: reviewed_blocks(review),
            spans,
            offsets,
        }
    }
}

/// The keys a judgment `scope` answers for (feature 451 T84, D60's blocks read per task): a block outside every task's section always;
/// a block of a task's section only where `scope` holds the task; a `(removed)` block of a task's own (its heading opens with the id,
/// a filled template's old heading among them) only where `scope` holds the task and its section carries no CLEAR task verdict, which
/// answers for every block it had - and never where the task was withdrawn and the block was a block of its unfilled stub (451 T359,
/// `template::stub_block`; its earlier text unread, it is owed). WHY: measured 2026-11-21 (feature 451's 16 landings of 2026-11-20/21, each replayed on its tick's
/// tree): 14 were refused on the whole feature, 6 of them on other open tasks' sections or a filled template's old heading alone - an
/// open task's section is reviewed when its own task is decided (feature 375 FR-003a), not before another task's tick. A heading that
/// only names a task makes it the owner of no block inside another task's own section (451 T180).
fn in_scope(
    keys: Vec<String>,
    review: &Value,
    layout: &Layout,
    held: &Scope,
    history: Option<&History>,
) -> Vec<String> {
    let scope = &held.tasks;
    let Layout {
        have,
        spans,
        offsets,
    } = layout;
    // was the removed block a block of the task's unfilled stub (`template::stub_block`, the test `make task-withdraw` removes a
    // section by)? Its earlier text unread - no kept text, no history at its digest - it is not known to be one, and is owed
    let stub_of = |gone: &str, t: &str| {
        let was = have.get(gone).and_then(|e| earlier_text(e, gone, history));
        was.is_some_and(|text| super::template::stub_block(t, &text))
    };
    let cleared = |t: &str| {
        review
            .get("tasks")
            .and_then(|all| all.get(t))
            .and_then(|e| text_of(e, "verdict"))
            == Some("CLEAR")
    };
    keys.into_iter()
        .filter(|key| {
            if let Some(gone) = key.strip_prefix(REMOVED) {
                let title = heading_text(gone);
                let own = leading_tasks(&title);
                // a withdrawn task's removed block that was its unfilled stub: nothing decided, nothing owed (451 T359). The box's
                // form alone exempts nothing (D15b): a filled block removed beside a hand-written `Withdrawn` box is a decision
                let owes = |t: &&str| {
                    let stub = held.withdrawn.contains(*t) && stub_of(gone, t);
                    scope.contains(*t) && !cleared(t) && !stub
                };
                return own.is_empty() || own.iter().any(owes);
            }
            // a block inside no task's section always; inside several (a bundle's, 451 T141) where `scope` holds any of them; inside a
            // task's own section, never for a task a heading there only names (451 T180: 449 T377's heading names T351, whose section
            // the tick archived, so T351's "section" was T377's heading and every later tick of the landing was refused on it)
            offsets.get(key).is_none_or(|at| {
                let owners: Vec<&(String, bool, (usize, usize))> = spans
                    .iter()
                    .filter(|(_, _, span)| inside(&[*span], *at))
                    .collect();
                let owned = owners.iter().any(|(_, own, _)| *own);
                owners.is_empty()
                    || owners
                        .iter()
                        .any(|(t, own, _)| (*own || !owned) && scope.contains(t))
            })
        })
        .collect()
}

/// The blocks `make plan-delta` owes a review (FR-043): the whole plan's owed and BLOCKED keys, but an unwritten section's, read through
/// [`in_scope`] with every task in scope - so a `(removed)` block a task's CLEAR verdict answers for is owed there exactly as a tick
/// owes it. WHY (451 T487, 2026-11-27): the two readers asked different questions of one record - plan-delta owed `(removed) ### T475
/// (<why: ...>)`, T475's removed stub heading, which no tick held (T475's CLEAR task verdict answers for it), and a reviewer spent the
/// round bb51ce5d2c on it.
pub(super) fn delta_keys(spec_dir: &Path, history: &History) -> Vec<String> {
    let read = |f: &str| super::once::text(&spec_dir.join(f));
    let text = read("plan.md");
    let review = super::once::record(spec_dir);
    let sections = task_sections(&text);
    let ruled = ruled_tasks(&review, &text, &sections, Some(history));
    let (mut keys, blocked) = block_status_of(
        &review,
        &text,
        &sections,
        &ruled,
        Some(history),
        &super::once::plan_done(spec_dir),
    );
    for key in blocked {
        if !keys.contains(&key) {
            keys.push(key);
        }
    }
    // a section still the `make task-add` template rides in no bundle (451 T462): no reviewer judges it, no round is counted for it
    let keys = written_only(keys, &text, &BTreeSet::new());
    let tasks =
        l7r_shared::speckit::tasks::joined(&read("tasks.md"), &super::once::tasks_done(spec_dir));
    let mut every = scope_of(&tasks, &[]);
    every.tasks.extend(sections.keys().cloned());
    for key in &keys {
        let title = heading_text(key.strip_prefix(REMOVED).unwrap_or(key));
        every
            .tasks
            .extend(leading_tasks(&title).into_iter().map(str::to_owned));
    }
    in_scope(
        keys,
        &review,
        &Layout::of(&review, &text, &sections),
        &every,
        Some(history),
    )
}

/// [`judge`], the blocks read only as far as `scope` reaches ([`in_scope`]); None reads every block.
pub(super) fn judge_in(
    plan: Option<&[u8]>,
    review_text: Option<&str>,
    history: Option<&History>,
    done: &str,
    scope: Option<&Scope>,
) -> Option<(&'static str, String)> {
    judge_held(plan, review_text, history, done, scope).map(|(rule, reason, _)| (rule, reason))
}

/// (rule, reason, the blocks the judgment listed): every key owed a review under `plan-review-stale`, every BLOCKED key under
/// `plan-review-blocked`, none where the plan or its record is missing. The reason shows five keys cut to 60 characters; these are
/// all of them, whole, for the record of an honored escape (feature 451 T262).
pub(super) type Held = (&'static str, String, Vec<String>);

/// [`judge_in`] with the blocks it listed.
pub(super) fn judge_held(
    plan: Option<&[u8]>,
    review_text: Option<&str>,
    history: Option<&History>,
    done: &str,
    scope: Option<&Scope>,
) -> Option<Held> {
    finish(&base(plan, review_text, history, done), history, scope)
}

/// What a judgment reads before its scope: a plan or record missing (its answer whatever the scope), or the record, the plan's
/// text and the blocks owed and BLOCKED over the whole plan ([`ruled_tasks`], [`block_status`]), which no task changes.
pub(super) enum Base {
    Missing(Held),
    Judged {
        review: Value,
        text: String,
        /// the plan's task sections, parsed once for the judgment and its scoped asks (451 T466)
        sections: BTreeMap<String, String>,
        owed: Vec<String>,
        blocked: Vec<String>,
        /// made on the first scoped ask, kept for the rest
        layout: Box<std::cell::OnceCell<Layout>>,
    },
}

/// [`Base`] of a plan, its record and plan-done.md.
fn base(
    plan: Option<&[u8]>,
    review_text: Option<&str>,
    history: Option<&History>,
    done: &str,
) -> Base {
    #[cfg(test)]
    JUDGED.with(|n| n.set(n.get() + 1));
    let Some(plan) = plan else {
        return Base::Missing(("plan-missing", format!("no plan.md - the plan stage is owed before its review can be (spec D5); then {HOW}"), Vec::new()));
    };
    let Some(review_text) = review_text else {
        return Base::Missing((
            "plan-review-missing",
            format!("no {RECORD} - {HOW}"),
            Vec::new(),
        ));
    };
    let Ok(mut review) = serde_json::from_str::<Value>(review_text) else {
        return Base::Missing((
            "plan-review-missing",
            format!("{RECORD} is not JSON - {HOW}"),
            Vec::new(),
        ));
    };
    let text = String::from_utf8_lossy(plan).into_owned();
    if !review.get("blocks").is_some_and(Value::is_object)
        && text_of(&review, "plan_text").is_none()
        && text_of(&review, "plan_sha256") == Some(digest(plan).as_str())
    {
        let verdict = review.get("verdict").cloned().unwrap_or(Value::Null);
        let whole: Map<String, Value> = blocks(&text)
            .into_iter()
            .map(|(k, b, _)| (k, json!({"sha256": block_digest(&b), "verdict": verdict})))
            .collect();
        review["blocks"] = Value::Object(whole);
    }
    let sections = task_sections(&text);
    let ruled = ruled_tasks(&review, &text, &sections, history);
    let (owed, blocked) = block_status_of(&review, &text, &sections, &ruled, history, done);
    Base::Judged {
        review,
        text,
        sections,
        owed,
        blocked,
        layout: Box::default(),
    }
}

/// A judgment's answer from its [`Base`], the blocks read only as far as `scope` reaches.
fn finish(base: &Base, history: Option<&History>, scope: Option<&Scope>) -> Option<Held> {
    let (review, text, sections, layout, mut owed_keys, mut blocked) = match base {
        Base::Missing(held) => return Some(held.clone()),
        Base::Judged {
            review,
            text,
            sections,
            owed,
            blocked,
            layout,
        } => (
            review,
            text.as_str(),
            sections,
            layout,
            owed.clone(),
            blocked.clone(),
        ),
    };
    // an unwritten section is owed by no judgment but its own task's (451 T462): judged per scope, so after the shared base (451 T464)
    let kept = scope.map_or_else(BTreeSet::new, |s| s.tasks.clone());
    owed_keys = written_only(owed_keys, text, &kept);
    blocked = written_only(blocked, text, &kept);
    if let Some(scope) = scope {
        let layout = layout.get_or_init(|| Layout::of(review, text, sections));
        owed_keys = in_scope(owed_keys, review, layout, scope, history);
        blocked = in_scope(blocked, review, layout, scope, history);
    }
    if !owed_keys.is_empty() {
        let shown: Vec<String> = owed_keys
            .iter()
            .take(5)
            .map(|k| k.chars().take(60).collect())
            .collect();
        let more = if owed_keys.len() > 5 {
            format!(" and {} more", owed_keys.len() - 5)
        } else {
            String::new()
        };
        return Some(("plan-review-stale", format!("{} block(s) of plan.md changed since their review by more than a typo (feature 375 FR-043): {}{more} - `make plan-delta F=<n>` builds the review of those blocks alone", owed_keys.len(), shown.join(", ")), owed_keys));
    }
    let whole_not_clear = !matches!(review.get("verdict"), None | Some(Value::Null))
        && text_of(review, "verdict") != Some("CLEAR")
        && !review.get("blocks").is_some_and(Value::is_object);
    if !blocked.is_empty() || whole_not_clear {
        let rows = review
            .get("decisions")
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default();
        let narrowing: Vec<String> = rows
            .iter()
            .filter(|d| text_of(d, "ruling") == Some("NOT LEGITIMATE"))
            .map(|d| text_of(d, "id").unwrap_or("?").to_owned())
            .collect();
        let named = if narrowing.is_empty() {
            "no ruling named".to_owned()
        } else {
            narrowing.join(", ")
        };
        return Some(("plan-review-blocked", format!("the plan review is BLOCKED ({named} ruled NOT LEGITIMATE) - withdraw or overrule the decision in plan.md, then {HOW}"), blocked));
    }
    None
}

/// What this feature owes, read from its directory.
pub(super) fn owed(spec_dir: &Path) -> Option<(&'static str, String)> {
    let plan_path = spec_dir.join("plan.md");
    let plan = std::fs::read(&plan_path).ok();
    let review = std::fs::read_to_string(spec_dir.join(RECORD)).ok();
    let done = l7r_shared::speckit::archive::plan_done(spec_dir);
    judge(
        plan.as_deref(),
        review.as_deref(),
        Some(&History::new(&plan_path, "HEAD")),
        &done,
    )
}

/// How many whole-plan judgments ([`Base`]) this thread has made, for the tests (451 T464).
#[cfg(test)]
pub(super) fn judged() -> usize {
    JUDGED.with(std::cell::Cell::get)
}

#[cfg(test)]
thread_local! {
    static JUDGED: std::cell::Cell<usize> = const { std::cell::Cell::new(0) };
}

/// Every block of the section carries a CLEAR verdict at its digest, or at a text it differs from by a typo only (405 T81, D57).
pub(super) fn section_clear(review: &Value, section: &str, history: Option<&History>) -> bool {
    let have = reviewed_blocks(review);
    let empty = json!({});
    blocks(section)
        .iter()
        .filter(|(k, ..)| k != "preamble")
        .all(|(k, b, _)| {
            let entry = have.get(k).unwrap_or(&empty);
            text_of(entry, "verdict") == Some("CLEAR")
                && (text_of(entry, "sha256") == Some(block_digest(b).as_str())
                    || earlier_text(entry, k, history)
                        .is_some_and(|e| typo_only(&strip_archive(&e), &strip_archive(b))))
        })
}

#[cfg(test)]
mod tests;
