//! A task lands with the files it names (451 T294): T270's landing replayed - its section's new module absent from HEAD - is refused
//! in the first pass and lands once the file is committed; each form of line and section is read as the module's doc says.

use l7r_gate_core::ci::fixtures::{git, put};

use super::super::tests::{fx, NOTE};
use super::{missing, refusal, Held};

const HELD: &str = "rust/gate/crates/measure/src/measure/audit/held.rs";

fn tree(files: &[&str]) -> Held {
    Held::of(&files.join("\0"))
}

#[test]
fn t270s_landing_without_its_new_module_is_refused_in_the_first_pass() {
    // RED FIRST (2026-11-27): without the check the first pass answered no stop naming the file
    let fx = fx("named-t270");
    let d = fx.root.join("specs/449-x");
    put(
        &d,
        "tasks.md",
        "## Occasions\n\n- none: T1 - tooling only\n\n## Tasks\n\n- [ ] T1 one\n",
    );
    put(
        &d,
        "plan.md",
        &format!("### T1 (why)\n\n  - **Where.** A new module, `{HELD}` (`class`), called by `runs()` in `audit.rs`.\n"),
    );
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "the tasks"]);
    let tasks = vec!["T1".to_owned()];
    let stops = fx.land.cheap_refusals(&d, &tasks, NOTE, None).unwrap();
    let said = format!("T1: its Occasions line or plan section names `{HELD}` that the landing tree's HEAD does not hold");
    assert!(stops.iter().any(|s| s.starts_with(&said)), "{stops:?}");
    let carry = stops.iter().any(|s| s.contains("`make builder-trees`"));
    assert!(carry);
    // carried, it lands
    put(&fx.root, HELD, "fn held() {}\n");
    git(&fx.root, &["add", "-A"]);
    git(&fx.root, &["commit", "-qm", "451 T1: the carry"]);
    let stops = fx.land.cheap_refusals(&d, &tasks, NOTE, None).unwrap();
    let named = stops.iter().any(|s| s.contains("plan section names"));
    assert!(!named);
}

#[test]
fn a_tree_with_no_head_is_an_error() {
    let fx = fx("named-nohead");
    let empty = fx.dir.join("empty");
    std::fs::create_dir_all(&empty).unwrap();
    git(&empty, &["init", "-q"]);
    let mut fx = fx;
    fx.land.root = fx.land.root.at(empty);
    assert!(matches!(fx.land.held(), Err(why) if why.starts_with("git ls-tree HEAD: ")));
}

#[test]
fn an_occasions_line_names_its_files_by_full_and_short_paths() {
    let held = tree(&[
        "rust/guard/shared/src/guards/set_down_hooks/tests/idle.rs",
        "rust/gate/crates/land/src/land.rs",
        "scripts/land-alone.sh",
        "docs/x.rs",
    ]);
    let tasks = "## Occasions\n\n- none: T7 - tooling only: (`rust/gate/crates/land/src/land.rs`, `land/gone.rs`, `tests/idle.rs`, \
                 `scripts/`, `scripts/land-alone.sh`:, `make land`, `request.md`, `x.rs`, `rust/**/*.rs`)\n  and `rust/wrapped.rs`\n\
                 - none: T8 - `rust/eight.rs`\n- not a declaration `rust/odd.rs`\n\n## Tasks\n\n- [ ] T7 `rust/box.rs`\n";
    // `land/gone.rs` held nowhere, the wrapped continuation read; a short name of another tree (`docs/x.rs`) holds nothing;
    // T8's line, a line of no kind and the task's box are not T7's
    assert_eq!(
        missing(tasks, "", "T7", &held),
        ["land/gone.rs", "x.rs", "rust/wrapped.rs"]
    );
    assert_eq!(missing(tasks, "", "T8", &held), ["rust/eight.rs"]);
    assert!(missing("no section\n", "", "T7", &held).is_empty());
}

#[test]
fn a_bundle_s_line_and_a_declaration_s_tag_are_each_task_s_own() {
    let held = tree(&[]);
    let tasks = "## Occasions\n\n- none: T299, T282 - `rust/a.rs`\n- placement-changed: marsh on kuwabata - T236: `rust/b.rs`\n\
                 - none: T2990 - `rust/c.rs`\n\n- none: T5 - x\n\n  `rust/not-joined.rs`\n";
    assert_eq!(missing(tasks, "", "T282", &held), ["rust/a.rs"]);
    assert_eq!(missing(tasks, "", "T299", &held), ["rust/a.rs"]);
    assert_eq!(missing(tasks, "", "T236", &held), ["rust/b.rs"]);
    assert!(missing(tasks, "", "T5", &held).is_empty());
}

#[test]
fn a_section_s_path_is_read_only_where_it_is_named_new() {
    let held = tree(&["rust/kept.rs"]);
    let plan = "### T3 (why)\n\n- `rust/one.rs`, new; `rust/two.rs` (new, the walk); a new test file `rust/three.rs`; New suite, \
                `tests/four.sh`; a new module `rust/five.rs::item`; `rust/kept.rs`, new\n- read `rust/read.rs`, deleted `rust/gone.rs`\n\
                ### T3 Approach (checklist part A)\n\n- a new crate `rust/six`\n### T4 (other)\n\n- `rust/four.rs`, new\n\
                ### T30, T3 (bundle)\n\n- `rust/one.rs`, new\n";
    assert_eq!(
        missing("", plan, "T3", &held),
        [
            "rust/one.rs",
            "rust/two.rs",
            "rust/three.rs",
            "tests/four.sh",
            "rust/five.rs",
            "rust/six"
        ]
    );
    assert_eq!(missing("", plan, "T4", &held), ["rust/four.rs"]);
}

#[test]
fn a_directory_named_is_held_by_its_files() {
    let held = tree(&["rust/guard/src/guards/sweep/a.rs"]);
    let tasks = "## Occasions\n\n- none: T1 - (`rust/guard/src/guards/sweep/`, `rust/guard`, `rust/guardian`)\n";
    assert_eq!(missing(tasks, "", "T1", &held), ["rust/guardian"]);
}

#[test]
fn the_refusal_names_each_file_and_is_empty_for_none() {
    assert_eq!(refusal(&[]), "");
    let said = refusal(&["rust/a.rs".to_owned(), "b.rs".to_owned()]);
    let head = "its Occasions line or plan section names `rust/a.rs`, `b.rs` that";
    assert!(said.starts_with(head), "{said}");
}
