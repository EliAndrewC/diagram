//! The category table (feature 451 T03, D2), moved out of `event_log_hooks.rs` past its 1,000-line bar (462 T321), unchanged.

/// THE CATEGORY TABLE (feature 451 T03, FR-001, plan D2): a make target - and the gate's own `l7r-gate.sh rust <cmd>`, which
/// `shared::make::invoked` reads as `rust-<cmd>` (D1) - to the bucket its minutes go to. The writer books a Bash call's `cat` by it and both
/// readers (`where_time.rs`, `feature_report/tables.rs`) book a line by its `make` field through [`bucket_of`], so a past log re-books too.
/// WHY: the old categorizer knew `quick`, `test-file`, `done` and three spec-kit targets, and booked 210 of a window's tool-minutes "other
/// tool" - `static` 30.8, `format` 20.9, `hooks-test` 20.2, `rust-test` 16.6, `render-sync` 6.1, `map` 3.6 of them (observed 2026-11-20,
/// method: the `ms` of the 449 log's `PostToolUse` lines since 2026-11-19T14:00Z, summed by `make`; research R1). Rows are
/// `data-model.md`'s, finished from the Makefile's `## [tag]` lines; moving a target between buckets is a one-line change. `compile` is
/// no target's: it is the `build`/`cover-build` phase lines inside a tests run (D4, T05), booked by the readers (T08). It feeds the
/// task time breakdown (`make task-time`, 451 T243), which lists by name each target a row here leaves `other`.
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
            // a failure reproduced under load (462 T321): its loops are test runs; its own `under-load` Phase line books to none
            "under-load",
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
            "task-time",
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
