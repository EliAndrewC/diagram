//! 451 T202: after a landing the clone takes main's tick back. Observed 2026-11-23: the take gave up on T187+T191's landing
//! (d601eee011) and on T184+T196's (74b68e3644) - each on an archive mark the tick rewrote while the clone's only change to it was the
//! blank line after it - so the clone never held main's tick, and the next landing's push conflicted on plan.md (and, merged by hand,
//! arbiter.jsonl) three times; and T195+T197's landing was refused on the Makefile, whose only uncommitted lines were T198's, because
//! T197's builder had added a line there and removed it again.

use std::path::Path;

use l7r_gate_core::ci::fixtures::put;

use super::super::REFUSED_FIRST;
use super::{alone, sh, world};

/// `text`'s lines but its blank ones.
fn unblank(text: &str) -> Vec<&str> {
    text.lines().filter(|l| !l.trim().is_empty()).collect()
}

/// The stub landing's `STUB_MID`: each `(rel, text)` written over the worktree's file, then staged, for the stub's commit.
fn landing_writes(dir: &Path, files: &[(&str, &str)]) -> String {
    let mut steps = Vec::new();
    for (k, (rel, text)) in files.iter().enumerate() {
        put(dir, &format!("tip/{k}"), text);
        steps.push(format!("cp {}/tip/{k} {rel}", dir.display()));
    }
    steps.push("git add -A".to_owned());
    steps.join(" && ")
}

/// T184+T196's landing (`fixtures/t196-take/`, the sides as they were, each section cut to its first lines; T187+T191's had the same
/// shape on T188-T190's mark): the tick archived T196's section and rewrote the marks after T186's, and the clone's one change to
/// T186's mark was the blank line it put after it, before T193's new section. A piece changed only in its blank lines is no change of
/// the clone's: taken as the tip has it, T196's section dropped, T193's kept.
#[test]
fn an_archive_mark_the_clone_changed_only_by_a_blank_line_is_taken_from_main() {
    let (dir, c) = world("alone-t196");
    let side = |which: &str| match which {
        "base" => include_str!("../fixtures/t196-take/plan.md.base"),
        "ours" => include_str!("../fixtures/t196-take/plan.md.ours"),
        "theirs" => include_str!("../fixtures/t196-take/plan.md.theirs"),
        _ => include_str!("../fixtures/t196-take/plan.md.resolved"),
    };
    put(&c, "specs/451-x/plan.md", side("base"));
    sh(
        &c,
        "git add -A && git commit -qm 'the records' && git push -q origin HEAD:main 2>/dev/null",
    );
    put(&c, "specs/451-x/plan.md", side("ours"));
    let mid = landing_writes(&dir, &[("specs/451-x/plan.md", side("theirs"))]);
    let (rc, said) = alone(&dir, &c, &[("STUB_MID", &mid)]);
    assert_eq!(rc, 0, "{said}");
    let tip = sh(&dir, "git -C origin.git rev-parse main");
    assert_eq!(
        sh(&c, "git rev-parse HEAD"),
        tip,
        "the clone holds main's tick"
    );
    let plan = std::fs::read_to_string(c.join("specs/451-x/plan.md")).unwrap();
    assert_eq!(unblank(&plan), unblank(side("resolved")));
    assert!(!plan.contains("### T196"), "{plan}");
    assert!(!plan.contains("T186 to T186"), "{plan}");
    assert!(plan.contains("### T193 (the GM"), "{plan}");
}

/// The arbiter's log, appended on both sides (the clone's `make arbiter-ask` row, the landing's settled row): an append-only `.jsonl`
/// keeps both sides' new lines, the clone's first; a line both sides wrote is kept once.
#[test]
fn an_append_only_log_appended_on_both_sides_keeps_both() {
    let (dir, c) = world("alone-jsonl");
    let rel = "specs/451-x/arbiter.jsonl";
    put(&c, rel, "{\"trigger\": \"a\"}\n");
    sh(
        &c,
        "git add -A && git commit -qm 'the log' && git push -q origin HEAD:main 2>/dev/null",
    );
    put(
        &c,
        rel,
        "{\"trigger\": \"a\"}\n{\"trigger\": \"same\"}\n{\"trigger\": \"the clone's\"}\n",
    );
    let tip = "{\"trigger\": \"a\"}\n{\"trigger\": \"same\"}\n{\"trigger\": \"the landing's\"}\n";
    let mid = landing_writes(&dir, &[(rel, tip)]);
    let (rc, said) = alone(&dir, &c, &[("STUB_MID", &mid)]);
    assert_eq!(rc, 0, "{said}");
    assert_eq!(
        std::fs::read_to_string(c.join(rel)).unwrap(),
        "{\"trigger\": \"a\"}\n{\"trigger\": \"same\"}\n{\"trigger\": \"the clone's\"}\n{\"trigger\": \"the landing's\"}\n"
    );
    // a line of the log rewritten on both sides is still a conflict, named
    let (dir, c) = world("alone-jsonl-rewrite");
    put(&c, rel, "{\"trigger\": \"a\"}\n");
    sh(
        &c,
        "git add -A && git commit -qm 'the log' && git push -q origin HEAD:main 2>/dev/null",
    );
    put(&c, rel, "{\"trigger\": \"a\", \"by\": \"the clone\"}\n");
    let mid = landing_writes(
        &dir,
        &[(rel, "{\"trigger\": \"a\", \"by\": \"the landing\"}\n")],
    );
    let (rc, said) = alone(&dir, &c, &[("STUB_MID", &mid)]);
    assert_eq!(rc, 4, "{said}");
}

/// The Makefile as T195+T197's landing found it, cut to two targets: modal-triage's lines, which T197's builder rewrote and put back.
const MAKEFILE: &str = "modal-triage: ## [project] the triage bundle for every pop-up owed only because a page it names moved   [OUT=<dir>]\n\t@cd \"$$(git rev-parse --show-toplevel)\" && scripts/gates/l7r-gate.sh record modal-triage --root . bundle $(if $(OUT),--out \"$(OUT)\",)\n\n_quick:\n\t@\"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh\" check spec-lint --delta .\n";

/// T197's first edit (its builder `ae25`): the REJUDGE= words and their step added.
const ADD_OLD: &str = "moved   [OUT=<dir>]\n\t@cd \"$$(git rev-parse --show-toplevel)\" && scripts";
const ADD_NEW: &str = "moved; REJUDGE= first withdraws those units' marks (451 T197)   [OUT=<dir>] [REJUDGE=\"<uid> ...\"]\n\t@cd \"$$(git rev-parse --show-toplevel)\" && $(if $(REJUDGE),scripts/gates/l7r-gate.sh record modal-triage --root . rejudge --units \"$(REJUDGE)\" &&,) scripts";
/// T198's line, another builder's, uncommitted in the same file.
const T198: &str =
    "\t@\"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh\" make-docs . --check\n";

/// An Edit's end in the event log and its call in its builder's transcript: `task`'s builder `by`, call `id`, `old` to `new` in `rel`.
fn edit(dir: &Path, c: &Path, who: (&str, &str, &str), rel: &str, strings: (&str, &str)) {
    edit_as(dir, c, who, rel, strings, false);
}

/// `edit`, its call's `replace_all` flag `all`.
fn edit_as(
    dir: &Path,
    c: &Path,
    (task, by, id): (&str, &str, &str),
    rel: &str,
    (old, new): (&str, &str),
    all: bool,
) {
    let path = format!("{}/{rel}", c.display());
    let line = serde_json::json!({"t": "2099-01-01T00:00:00Z", "sid": "s1", "ev": "PostToolUse", "tool": "Edit", "id": id,
                                  "cat": "edit", "by": by, "path": path, "task": task});
    let log = dir.join("events/451-x.jsonl");
    let was = std::fs::read_to_string(&log).unwrap_or_default();
    std::fs::write(&log, format!("{was}{line}\n")).unwrap();
    let call = serde_json::json!({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": id, "name": "Edit",
                                  "input": {"file_path": path, "old_string": old, "new_string": new,
                                  "replace_all": all}}]}});
    let transcript = dir.join(format!("projects/-c/s1/subagents/agent-{by}.jsonl"));
    std::fs::create_dir_all(transcript.parent().unwrap()).unwrap();
    let was = std::fs::read_to_string(&transcript).unwrap_or_default();
    std::fs::write(&transcript, format!("{was}not json\n{call}\n")).unwrap();
}

/// T195+T197's landing, refused on 2026-11-23 for the Makefile, whose only uncommitted lines were T198's: T197's builder had added
/// the REJUDGE= lines and taken them out again. A file is a task's own only where its edits leave a change of their own in it - a hunk
/// of the file's uncommitted diff holding a line one of its edits wrote or removed; an edit whose call cannot be read counts as own.
#[test]
fn a_file_the_task_edited_and_put_back_is_not_its_own() {
    let (dir, c) = world("alone-net-zero");
    let rel = "Makefile";
    put(&c, rel, MAKEFILE);
    sh(
        &c,
        "git add -A && git commit -qm 'the Makefile' && git push -q origin HEAD:main 2>/dev/null",
    );
    let projects = dir.join("projects");
    let projects = projects.to_string_lossy();
    let env = [("L7R_PROJECTS_DIR", &*projects)];
    // T198's line, uncommitted, and T1's edit there and back
    let with_t198 = MAKEFILE.replace(" --delta .\n", &format!(" --delta .\n{T198}"));
    put(&c, rel, &with_t198);
    edit(
        &dir,
        &c,
        ("T2", "a198", "toolu_t198"),
        rel,
        (" --delta .\n", &format!(" --delta .\n{T198}")),
    );
    edit(
        &dir,
        &c,
        ("T1", "ae25", "toolu_add"),
        rel,
        (ADD_OLD, ADD_NEW),
    );
    edit(
        &dir,
        &c,
        ("T1", "a912", "toolu_back"),
        rel,
        (ADD_NEW, ADD_OLD),
    );
    let (rc, said) = alone(&dir, &c, &env);
    assert_eq!(rc, 0, "{said}");
    assert!(!said.contains("own edits are uncommitted"), "{said}");
    assert!(said.contains("Makefile"), "named as left: {said}");
    assert_eq!(
        std::fs::read_to_string(c.join(rel)).unwrap(),
        with_t198,
        "T198's line kept, uncommitted"
    );
    // T1's edit that stays is its own: refused, named
    let (dir, c) = world("alone-net-kept");
    put(&c, rel, MAKEFILE);
    sh(
        &c,
        "git add -A && git commit -qm 'the Makefile' && git push -q origin HEAD:main 2>/dev/null",
    );
    let projects = dir.join("projects");
    let projects = projects.to_string_lossy();
    let env = [("L7R_PROJECTS_DIR", &*projects)];
    put(&c, rel, &MAKEFILE.replace(ADD_OLD, ADD_NEW));
    edit(
        &dir,
        &c,
        ("T1", "ae25", "toolu_add"),
        rel,
        (ADD_OLD, ADD_NEW),
    );
    let (rc, said) = alone(&dir, &c, &env);
    assert_eq!(rc, REFUSED_FIRST, "{said}");
    assert!(
        said.contains("T1's own edits are uncommitted - commit them, then land again"),
        "{said}"
    );
    assert!(said.contains("-- Makefile"), "{said}");
    // a word changed inside one line, the edit's strings no whole line
    put(&c, rel, &MAKEFILE.replace("bundle $(if", "bundles $(if"));
    edit(
        &dir,
        &c,
        ("T1", "ae25", "toolu_word"),
        rel,
        ("bundle $(if", "bundles $(if"),
    );
    let (rc, said) = alone(&dir, &c, &env);
    assert_eq!(rc, REFUSED_FIRST, "{said}");
    // its call unread (no transcript): own, failing toward the refusal
    let (rc, said) = alone(&dir, &c, &[("L7R_PROJECTS_DIR", "/nonexistent")]);
    assert_eq!(rc, REFUSED_FIRST, "{said}");
}

/// A `replace_all` edit's string is one the file repeats, so another task's line holding it is no line the edit wrote (451 T202's
/// MODE 4, D8): its line counts only as one of its replacements - the line with the string put back on the hunk's other side. Put
/// back, the file is not the task's own; kept, it is.
#[test]
fn a_replace_all_edit_put_back_is_not_its_own() {
    let rel = "notes.txt";
    let base = "a: old\nb: old\n";
    let other = "c: old\n";
    let (dir, c) = world("alone-all-back");
    put(&c, rel, base);
    sh(
        &c,
        "git add -A && git commit -qm 'the notes' && git push -q origin HEAD:main 2>/dev/null",
    );
    let projects = dir.join("projects");
    let projects = projects.to_string_lossy();
    let env = [("L7R_PROJECTS_DIR", &*projects)];
    put(&c, rel, &format!("{base}{other}"));
    edit(
        &dir,
        &c,
        ("T2", "a2", "toolu_other"),
        rel,
        ("b: old\n", &format!("b: old\n{other}")),
    );
    edit_as(
        &dir,
        &c,
        ("T1", "a1", "toolu_all"),
        rel,
        ("old", "new"),
        true,
    );
    edit_as(
        &dir,
        &c,
        ("T1", "a1", "toolu_all_back"),
        rel,
        ("new", "old"),
        true,
    );
    let (rc, said) = alone(&dir, &c, &env);
    assert_eq!(rc, 0, "{said}");
    assert!(!said.contains("own edits are uncommitted"), "{said}");
    assert_eq!(
        std::fs::read_to_string(c.join(rel)).unwrap(),
        format!("{base}{other}"),
        "T2's line kept, uncommitted"
    );
    // kept, the replacements are its own: refused, named
    let (dir, c) = world("alone-all-kept");
    put(&c, rel, base);
    sh(
        &c,
        "git add -A && git commit -qm 'the notes' && git push -q origin HEAD:main 2>/dev/null",
    );
    let projects = dir.join("projects");
    let projects = projects.to_string_lossy();
    let env = [("L7R_PROJECTS_DIR", &*projects)];
    put(&c, rel, &base.replace("old", "new"));
    edit_as(
        &dir,
        &c,
        ("T1", "a1", "toolu_all"),
        rel,
        ("old", "new"),
        true,
    );
    let (rc, said) = alone(&dir, &c, &env);
    assert_eq!(rc, REFUSED_FIRST, "{said}");
    assert!(said.contains("-- notes.txt"), "{said}");
}
