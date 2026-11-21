//! The cases of the stale-value search, and every way of asking.

use std::path::Path;

use super::{
    all_found, cli, criteria_left_behind, dirs_cli, read_dir, render, stale_candidates, tokens,
    watched_lines, Files,
};

fn files(list: &[(&str, &str)]) -> Files {
    list.iter()
        .map(|(n, t)| ((*n).to_owned(), (*t).to_owned()))
        .collect()
}

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

const OLD: &str = "the `tier` runs on Sonnet here\n";
const NEW: &str = "the `tier` runs on Opus here\n";

#[test]
fn a_line_naming_the_subject_with_the_old_value_is_a_candidate() {
    let old = files(&[("spec.md", OLD), ("plan.md", "keep `tier` on Sonnet\n")]);
    let new = files(&[("spec.md", NEW), ("plan.md", "keep `tier` on Sonnet\n")]);
    let found = stale_candidates(&old, &new);
    assert_eq!(found.len(), 1);
    assert_eq!(
        (
            found[0].file.as_str(),
            found[0].line,
            found[0].subject.as_str()
        ),
        ("plan.md", 1, "tier")
    );
    assert_eq!(found[0].old_values, ["sonnet"]);
    assert!(render(&found).contains("plan.md:1  `tier` still with sonnet\n      keep `tier` on Sonnet\n      (changed in spec.md to: the `tier` runs on Opus here)"));
}

#[test]
fn no_subject_no_value_or_a_pure_insertion_yields_nothing() {
    let one = |a: &str, b: &str| {
        stale_candidates(
            &files(&[("s.md", a)]),
            &files(&[("s.md", b), ("p.md", "`tier` Sonnet\n")]),
        )
    };
    assert!(one("no ticks on Sonnet\n", "no ticks on Opus\n").is_empty());
    assert!(one("`tier` the\n", "`tier` was\n").is_empty());
    assert!(one("`tier` only\n", "`tier` only\nanother line\n").is_empty());
    assert!(stale_candidates(&files(&[]), &files(&[("s.md", NEW)])).is_empty());
}

#[test]
fn skipped_files_and_history_and_verify_notes_keep_their_old_values() {
    assert!(watched_lines("request.md", "x\n").is_empty());
    assert!(watched_lines("measure/a.md", "x\n").is_empty());
    let text = "a\n## Review history\nb\n## Next\nc\n      verify: d\n";
    assert_eq!(
        watched_lines("s.md", text)
            .iter()
            .map(|l| l.1)
            .collect::<Vec<_>>(),
        ["a", "## Next", "c"]
    );
    let old = files(&[("request.md", OLD)]);
    let new = files(&[("request.md", NEW), ("p.md", "`tier` Sonnet\n")]);
    assert!(stale_candidates(&old, &new).is_empty());
}

#[test]
fn a_line_rewritten_from_one_naming_the_subject_was_revisited_on_purpose() {
    let old = files(&[("s.md", OLD), ("p.md", "about `tier` before\n")]);
    let new = files(&[("s.md", NEW), ("p.md", "about `tier` on Sonnet now\n")]);
    assert!(stale_candidates(&old, &new).is_empty());
    let fresh = files(&[("s.md", OLD), ("p.md", "about nothing\n")]);
    assert_eq!(stale_candidates(&fresh, &new).len(), 1);
}

#[test]
fn a_subjects_own_words_are_no_old_value_and_each_line_is_named_once() {
    let old = files(&[(
        "s.md",
        "the `tier list` x-value Sonnet\nthe `tier list` Haiku here\n",
    )]);
    let new = files(&[
        (
            "s.md",
            "the `tier list` x-value Opus\nthe `tier list` Fable here\n",
        ),
        ("p.md", "`tier list` Sonnet Haiku\n"),
    ]);
    let found = stale_candidates(&old, &new);
    assert_eq!(found.len(), 1);
    assert_eq!(found[0].old_values, ["sonnet"]);
    assert!(!tokens("the Sonnet").contains("the"));
}

const SPEC_A: &str =
    "- **FR-001**: must do one\n  and more\n- **SC-001** (FR-001, FR-002): holds\n";
const SPEC_B: &str =
    "- **FR-001**: must do two\n  and more\n- **SC-001** (FR-001, FR-002): holds\n";

#[test]
fn a_criterion_citing_a_rewritten_requirement_and_left_untouched_is_named() {
    let found = criteria_left_behind(
        &files(&[("spec.md", SPEC_A)]),
        &files(&[("spec.md", SPEC_B)]),
    );
    assert_eq!(found.len(), 1);
    assert_eq!(found[0].old_values, ["FR-001"]);
    let shown = render(&found);
    assert!(shown.contains("spec.md:3  `SC-001` cites FR-001, which the change rewrote - the criterion was not touched"), "{shown}");
    let touched = "- **FR-001**: must do two\n- **SC-001** (FR-001): holds, changed\n";
    assert!(criteria_left_behind(
        &files(&[("spec.md", SPEC_A)]),
        &files(&[("spec.md", touched)])
    )
    .is_empty());
    assert!(criteria_left_behind(
        &files(&[("plan.md", SPEC_A)]),
        &files(&[("plan.md", SPEC_B)])
    )
    .is_empty());
    assert!(criteria_left_behind(&files(&[]), &files(&[("spec.md", SPEC_B)])).is_empty());
    let unrelated = "- **FR-001**: must do one\n- **SC-001** (FR-009): holds\n";
    assert!(criteria_left_behind(
        &files(&[("spec.md", unrelated)]),
        &files(&[("spec.md", unrelated)])
    )
    .is_empty());
}

fn lines(one: impl Fn(usize) -> String) -> String {
    (0..30).map(one).collect::<Vec<_>>().join("\n") + "\n"
}

#[test]
fn the_report_says_none_and_trims_past_twenty_five() {
    assert!(render(&[]).starts_with("stale-terms: no candidate"));
    let old = lines(|i| format!("`s{i}` value{i}x"));
    let new = lines(|i| format!("`s{i}` other{i}y"));
    let also = lines(|i| format!("`s{i}` value{i}x again"));
    let found = all_found(
        &files(&[("a.md", &old)]),
        &files(&[("a.md", &new), ("b.md", &also)]),
    );
    assert_eq!(found.len(), 30);
    assert!(render(&found).ends_with("... and 5 more"));
}

fn write(root: &Path, name: &str, text: &[u8]) {
    let path = root.join(name);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

#[test]
fn a_directory_is_read_as_text_alone() {
    let d = crate::checks::scratch("stale-read");
    write(&d, "deep/a.md", b"x");
    write(&d, "__pycache__/b.md", b"y");
    write(&d, "bin.dat", &[0xff, 0xfe]);
    write(&d, "big.md", &vec![b'x'; 1_000_001]);
    assert_eq!(read_dir(&d).keys().collect::<Vec<_>>(), ["deep/a.md"]);
}

fn clone(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    for args in [
        &["init", "-q"][..],
        &["config", "user.email", "t@t"],
        &["config", "user.name", "t"],
    ] {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(&root)
            .args(args)
            .status()
            .unwrap()
            .success());
    }
    write(&root, "specs/449-x/spec.md", OLD.as_bytes());
    write(&root, "specs/449-x/plan.md", b"keep `tier` on Sonnet\n");
    write(&root, "specs/449-x/raw.dat", &[0xff]);
    for args in [&["add", "-A"][..], &["commit", "-qm", "a"]] {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(&root)
            .args(args)
            .status()
            .unwrap()
            .success());
    }
    write(&root, "specs/449-x/spec.md", NEW.as_bytes());
    root
}

#[test]
fn a_ref_a_snapshot_and_their_absence_are_each_answered() {
    let root = clone("stale-cli");
    let there = root.display().to_string();
    let got = cli(&words(&["449", "--clone", &there, "--against", "HEAD"]));
    assert_eq!(got.code, 1, "{}", got.stderr);
    assert!(got.stdout.contains("plan.md:1"));
    let got = cli(&words(&["449-x", "--clone", &there]));
    assert!(got.code == 2 && got.stderr.contains("no snapshot of 449-x"));
    write(
        &root,
        ".git/review-round/449-x/snapshot/spec.md",
        NEW.as_bytes(),
    );
    let got = cli(&words(&["449", "--clone", &there]));
    assert!(got.code == 0 && got.stdout.starts_with("stale-terms: no candidate"));
    assert_eq!(cli(&words(&["zzz", "--clone", &there])).code, 2);
    assert_eq!(cli(&[]).code, 2);
    assert_eq!(cli(&words(&["--clone", &there])).code, 2);
    assert_eq!(cli(&words(&["449", "--clone", "/nonexistent/c"])).code, 2);
}

#[test]
fn the_guards_question_gives_the_count_and_the_report_or_nothing() {
    let root = crate::checks::scratch("stale-dirs");
    write(&root, "old/s.md", OLD.as_bytes());
    write(&root, "old/p.md", b"keep `tier` on Sonnet\n");
    write(&root, "new/s.md", NEW.as_bytes());
    write(&root, "new/p.md", b"keep `tier` on Sonnet\n");
    let (old, new) = (
        root.join("old").display().to_string(),
        root.join("new").display().to_string(),
    );
    let got = dirs_cli(&words(&[&old, &new]));
    assert!(
        got.stdout.starts_with("1\nstale-terms: 1 candidate(s)"),
        "{}",
        got.stdout
    );
    assert_eq!(dirs_cli(&words(&[&new, &new])).stdout, "");
    assert_eq!(dirs_cli(&[]).code, 2);
}

/// 451 T54: the FR-013 amendment's spec review was refused with 66 candidates, every one the backticked `end` (the event log's `end`
/// line) found as the word "end" or inside another word - Independent, `append_row`, a sentence's end - and among them one line still
/// saying the definition the change replaced: `contracts/refusals.md:12`, a landing as "D5's `end` line of code 0". The lines are the
/// feature's own, verbatim (reconstructed 2026-11-21 from commits 76635031f1 and 62a9b98d44: 67 candidates, 56 of them `end`).
const LANDING_OLD: &str = "- **A landing** (one definition, D11's too) is a `make land` of the task that SUCCEEDED: D5's `end` line of code 0 whose `tasks` names\ntask; the REWORK counts refused landings (D5's `end` lines with a non-zero code) and plan re-rounds (a task's `spec-fidelity` and\n";
const LANDING_NEW: &str = "- **A landing** (one definition, D11's too) is a `make land` of the task that SUCCEEDED: D5's `end` line whose `landed` is true (its\ntask; the REWORK counts refused landings (D5's `end` lines whose `landed` is false: a push that went out with a later raise, or\n";
const HISTORY: &str = "  - the unit figure's unit is the clause, cut at `;` too and even inside a code span, so a label at a sentence's end does not
5. **The order.** Independent of T03-T24. It touches the plan crate alone, beside T23's `rustc` and the builder in `rust/phases/`.
  - **The end is filed beside its launch.** It goes in the log that holds the launching call's line, not feature.json's fallback log where the prompt's line goes (a notice names no command or brief, so T26's chain has nothing to file it by). Its fields are data-model's: `id`, `bg`, `status`, and `exit`, the summary's last `exit code N`.
  - **`append_row`** stamps `t` where the row has none. It takes `sid` from `CLAUDE_CODE_SESSION_ID` where the row names none, files the row by its `task` through T26's chain.
";
const CONTRACT: &str = "| FR-007 | `static_runs_hooks` (new guard), PreToolUse Bash | the third `make static` of a task since its last landing that succeeded (D5's `end` line of code 0 naming it), or since its first start if it has never landed |\n";

#[test]
fn a_plain_word_subject_is_named_only_as_its_code_span_and_the_real_catch_stands() {
    let old = files(&[
        ("plan.md", LANDING_OLD),
        ("plan-done.md", HISTORY),
        ("contracts/refusals.md", CONTRACT),
    ]);
    let new = files(&[
        ("plan.md", LANDING_NEW),
        ("plan-done.md", HISTORY),
        ("contracts/refusals.md", CONTRACT),
    ]);
    let found = stale_candidates(&old, &new);
    let named: Vec<(&str, usize, &str)> = found
        .iter()
        .map(|c| (c.file.as_str(), c.line, c.subject.as_str()))
        .collect();
    assert_eq!(named, [("contracts/refusals.md", 1, "end")], "{found:#?}");
    assert_eq!(found[0].old_values, ["0", "code"]);
}

/// The catches the log shows on BARE text, which a code-span-only rule would lose: 283's `780 sq ft` (a phrase, the sheet's old
/// size, rewritten at the next dispatch) and 285's `GUESS` (a capitalized name, "The word GUESS" rewritten "The label GUESS"),
/// reconstructed 2026-11-21 from the commits at the snapshot and the refusal (the guard log's 2026-09-28T17:13 and 18:49 refusals).
#[test]
fn a_phrase_or_a_capitalized_name_is_named_bare_but_not_inside_a_longer_word() {
    let size = (
        "  `780 sq ft` it drew (observed 2026-09-28; method: its rect 88 x 80 px at 3 px a foot, as the rear strip's 160 x 44): its sunny corner holds no more without moving the roji, and that is recorded in its notes.\n",
        "  `780 sq ft` (observed 2026-09-28; method: its rect 88 x 80 px at 3 px a foot, as the rear strip's 160 x 44), under that\n",
        "  the inner garden; the pines, the well and the roji's last stones moved clear. The sheet drew it at 780 sq ft, under\n",
    );
    let label = (
        "  - *guess*: each occurrence of the capitalized word `GUESS` in the question's visible text; the item's text is the\n",
        "  - *guess*: each occurrence of the capitalized label `GUESS` (or its plural `GUESSES`, research.md R3) in the question's visible text; the item's text is the\n",
        "- The word GUESS in a heading or a quoted source passage is still a label the reader sees; it is listed.\n",
    );
    for (was, now, other, subject) in [
        (size.0, size.1, size.2, "780 sq ft"),
        (label.0, label.1, label.2, "GUESS"),
    ] {
        let found = stale_candidates(
            &files(&[("plan.md", was), ("spec.md", other)]),
            &files(&[("plan.md", now), ("spec.md", other)]),
        );
        assert_eq!(found.len(), 1, "{subject}: {found:#?}");
        assert_eq!(
            (found[0].file.as_str(), found[0].subject.as_str()),
            ("spec.md", subject)
        );
    }
    let inside = |line: &str| {
        stale_candidates(
            &files(&[("plan.md", label.0), ("spec.md", line)]),
            &files(&[("plan.md", label.1), ("spec.md", line)]),
        )
    };
    assert!(inside("- The word GUESSES in a heading\n").is_empty());
    assert!(inside("- The word XGUESS in a heading\n").is_empty());
    assert_eq!(inside("- The word GUESS.\n").len(), 1);
}

/// 274's line, rewritten by the change from one that wrote "the split" in prose, names `split` with its new list: revisited on
/// purpose, so not a candidate, though the old block never wrote the span (the guard log's 2026-09-27T23:07 refusal, reconstructed
/// 2026-11-21; reading the old block by `names` added this candidate and no real one over the 82 reconstructed refusals).
#[test]
fn a_line_rewritten_from_one_writing_the_word_in_any_form_was_revisited_on_purpose() {
    let before = "  counting more than four, or counting none without an exempt kind, naming the split and the escape. Only three named\n  kinds are exempt, and feature 250's `brief.py` MUST declare them on the briefs that are those kinds.\n";
    let after = "  Only four named kinds are exempt (`check`, `assertions`, `split`, `handover`), and feature 250's `brief.py` MUST declare\n";
    let old = files(&[
        (
            "plan.md",
            "  the `split` kind is feature 250's handover brief\n",
        ),
        ("spec.md", before),
    ]);
    let new = files(&[
        (
            "plan.md",
            "  the `split` kind is the over-cap question's own brief\n",
        ),
        ("spec.md", after),
    ]);
    assert!(stale_candidates(&old, &new).is_empty());
    let fresh = files(&[
        (
            "plan.md",
            "  the `split` kind is feature 250's handover brief\n",
        ),
        ("spec.md", "  nothing about it\n"),
    ]);
    assert_eq!(stale_candidates(&fresh, &new).len(), 1);
}

/// 451's plan.md:107 opens inside a span wrapped from the line before, so pairing its backticks in order reads its `end` as prose:
/// the plain word's span is found as the literal `` `end` `` (451 T54, found 2026-11-21 comparing the reconstruction's 17 spans of
/// `end` with the binary's 16).
#[test]
fn a_plain_words_span_is_read_on_a_line_that_opens_inside_a_wrapped_span() {
    let wrapped = "done`), `cohort` (`make cohort-landing`), `claims` (the wait), `push` - and a last `end` line with its exit code and `tasks`, the task\n";
    let found = stale_candidates(
        &files(&[("plan.md", LANDING_OLD), ("w.md", wrapped)]),
        &files(&[("plan.md", LANDING_NEW), ("w.md", wrapped)]),
    );
    assert_eq!(found.len(), 1, "{found:#?}");
    assert_eq!(
        (found[0].file.as_str(), found[0].subject.as_str()),
        ("w.md", "end")
    );
}
