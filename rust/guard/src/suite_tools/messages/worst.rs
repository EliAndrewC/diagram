//! THE MESSAGES THAT GROW WITH A LIST, AT THEIR WORST CASE (feature 451 T170). The suites render a list-growing message at the few
//! items their fixtures hold, and sessions met it at many: static-runs' refusal at 7,909 characters over 25 crates where its suite
//! rendered 738, review-round's stale-term refusal at 10,345 over 25 candidates (measured 2026-11-23 over the coordinator's transcript
//! and its subagents', `/tmp/t170/census/var.py`). So `messages check` holds each one here too, rendered at [`MANY`] items - static-runs'
//! at every crate of the tree, its list's real bound - against its kind's budget and a verdict of its wording, the cap being what is
//! held. Each item is as long as the longest the transcripts showed of its kind, cut where the message cuts it.
//!
//! THE CENSUS (451 T170, observed 2026-11-23, method: every guard wording of the coordinator's transcript and its subagents'
//! whose longest rendering is past 600 characters and 1.5 times its shortest, each confirmed from its builder's source as joining a
//! collection): these eight. A ninth, the pop-ups' batch refusal (`shared::checks::handle::batch_said`), is here since 451 T177: its
//! list is its fix command's argument, so it is never capped, and is held whole at [`MANY`] pop-ups as long as the longest the
//! transcripts showed (`choice/byre_form--detached_commons`, 34 characters; the most named in one refusal, 24), measured 2026-11-23.
//! A tenth, set-down's builder-slot block, is here too: its list is the running builders, fewer than the knob (3), each a bundle's
//! tasks; set-down's open-task blocks name one task, its title cut at 80 characters, so they grow with no list and the suite's
//! renderings stand for them (451 T177; the suite renders both, so neither waits on 451 T174).

use std::path::Path;

use super::Message;
use crate::guards::pair_hooks::dropped::{self, Call};
use crate::guards::{
    blocked_fetch_hooks, discard_hooks, finished_run_hooks, pair_hooks, review_round_hooks,
    static_runs_hooks,
};
use crate::shared::checks::{self, git_stdout};
use crate::shared::listed;

/// The items each list holds at its worst case: past [`listed::SHOWN`] many times over, a GUESS (the longest list measured, 2026-11-23:
/// 34 finding ids in one prerequisite, 25 crates, 25 candidates).
pub const MANY: usize = 40;

/// Every crate of the tree at `root`: the packages under `rust/` its tracked files name - static-runs' list at its bound.
#[must_use]
pub fn tree_crates(root: &Path) -> Vec<String> {
    static_runs_hooks::crates_of(root, git_stdout(root, &["ls-files", "rust"]).lines())
}

fn message(guard: &str, kind: &str, text: String) -> (Message, String) {
    let keyed = text.clone();
    let m = Message {
        guard: guard.to_owned(),
        kind: kind.to_owned(),
        chars: text.chars().count(),
        text,
    };
    (m, keyed)
}

fn many(f: impl Fn(usize) -> String) -> Vec<String> {
    (1..=MANY).map(f).collect()
}

const URL: &str = "https://www.city.takayama.lg.jp/s/_res/projects/default_project/_page_/001/005/279/takayama-jinya.pdf";

/// blocked-fetch's attempts notice: [`MANY`] earlier attempts at [`URL`].
fn attempts() -> Vec<String> {
    let sought = "x".repeat(300);
    [
        vec![
            format!("attempts: {URL} - {MANY} earlier attempt(s):"),
            "  filter verdict: KEEP (the record's threshold met)".to_owned(),
        ],
        many(|i| format!("  2026-11-{:02} Q 0088: not-found - {sought}", i % 28 + 1)),
    ]
    .concat()
}

/// review-round's stale-terms list: [`MANY`] candidates, capped as the guard caps it.
fn stale() -> String {
    let block = |i: usize| {
        format!(
            "  specs/451-time-retro-and-efficiency/plan.md:{i}  `REFUSE_BUDGET` still with 1,800\n      the refusal budget stands at 1,800 \
characters, the 90th percentile 967 priced and not taken, set from the wordings make hooks-test HOOKS_ALL=1 rendered\n      \
(changed in specs/451-time-retro-and-efficiency/tasks.md to: the budget is 2,400 characters)"
        )
    };
    let blocks = many(block);
    format!(
        "stale-terms: {MANY} candidate(s) - each names a subject whose value CHANGED and still carries the old value:\n{}",
        listed::capped(&blocks, "  ", "make stale-terms F=451")
    )
}

/// pair-hooks' prerequisite refusal: [`MANY`] reviews whose findings no record verifies.
fn problems() -> String {
    many(|i| {
        format!("FR-003 building-review--county-magistracy-example-{i:02}: finding(s) N1, N2, C1, C2, C3, C4, C5, E1, Q1, N1, N2, N3, N4, C1, \
C2, C3, C4, E1, E2, Q1, N1, N3, N4, C1, C2, C3, C4, N1, N2, C1, C2, C3, C4, C5 from its last review have no record verifying them - add a measurements.json entry with \"verifies\", \"subject\": \
\"building-review--county-magistracy-example\" and \"answers\": \"1e4cd974884d\", or `make review-accept`")
    })
    .join("\n")
}

/// pair-hooks' dropped-calls block: [`MANY`] refused size-audit calls.
fn left() -> Vec<Call> {
    (1..=MANY)
        .map(|i| Call {
            t: String::new(),
            kind: "size-audit".to_owned(),
            key: format!("size-audit: family quarters {i:02} (round-trip)"),
            refused: true,
            why: "round 3 of size-audit--family-quarters for size-audit in this feature - the cap is two (feature 294 FR-009).".to_owned(),
        })
        .collect()
}

/// finished-run's Stop block: [`MANY`] runs, the second with no output file, so its line - waited on by its pid (451 T177), a line
/// no suite renders - is held here too (the round arbiter's ask:guard-wordings-third-round).
fn runs() -> Vec<String> {
    many(|i| {
        let log = if i == 2 {
            "(no file)".to_owned()
        } else {
            format!("/tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/t185/static-{i:02}.log")
        };
        finished_run_hooks::run_said(950_000 + u32::try_from(i).unwrap_or(0), "static", &log)
    })
}

/// Each list-growing message at its worst case - [`MANY`] items, `crates` for static-runs', the lists a message keeps in a file written
/// under `root`'s git directory - and the text its wording is keyed by: its own, but static-runs' over three crates, so a crate added
/// to the tree moves its length, which the budget holds, and not its wording, whose review would stand.
#[must_use]
pub fn worst(crates: &[String], root: &Path) -> Vec<(Message, String)> {
    let git_dir = checks::common_dir(root);
    let triggers = many(|i| {
        format!("reversal:/diagram/.clones/diagram-backlog/rust/guard/src/guards/context_cap_hooks/case_{i:02}.rs")
    });
    let files =
        many(|i| format!("l7r/diagram/interactive/assets/modals/sheet/writing-rooms-{i:02}.md"));
    let kinds = many(|i| format!("choice/byre_form--detached_common{i:02}"));
    // set-down's builder-slot words left with the slot notice itself (451 T183's MODE 4, D10)
    vec![
        {
            let (m, _) = message(
                "static-runs-hooks",
                "refuse",
                static_runs_hooks::refusal("449-rust-codebase", "T252", 2, crates),
            );
            let three = ["rust/a", "rust/b", "rust/c"].map(str::to_owned);
            (
                m,
                static_runs_hooks::refusal("449-rust-codebase", "T252", 2, &three),
            )
        },
        message(
            "review-round-hooks",
            "refuse",
            review_round_hooks::stale_refusal("451-time-retro-and-efficiency", &stale()),
        ),
        message(
            "blocked-fetch-hooks",
            "notice",
            blocked_fetch_hooks::attempts_said(URL, &attempts()),
        ),
        message(
            "checks-hooks",
            "refuse",
            checks::arbiter::refusal_unbatched(&triggers, root),
        ),
        message(
            "pair-hooks",
            "refuse",
            pair_hooks::review::prereq_refusal("glyph-check", &problems(), &git_dir),
        ),
        message("pair-hooks", "block", dropped::refusal(&left(), &git_dir)),
        message("discard-hooks", "refuse", discard_hooks::refusal(&files)),
        message(
            "finished-run-hooks",
            "refuse",
            finished_run_hooks::refusal_of(&runs(), &git_dir),
        ),
        message(
            "check-bundle-hooks",
            "refuse",
            checks::handle::blocked_text(&checks::handle::batch_said("modal-depiction", &kinds)),
        ),
    ]
}
