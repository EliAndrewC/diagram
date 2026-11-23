//! What a feature's `## Occasions` must say for a delta (feature 449 T238): a Rust stage's placement change refused undeclared, a
//! declaration naming no element or no pool map refused with its form, a tweak's commit line never refused, and only a line naming the
//! started task - or a commit's `Occasion:` line - answering the delta.

use super::*;

/// A Rust stage outside the drawing code `redrawn` reads: the seat's gap, a test module beside it, and a compound's layout.
const SEAT: &str = "//! the seat\nconst GAP_FT: f64 = 7.0;\n\npub fn seat(n: usize) -> f64 {\n    n as f64 * GAP_FT\n}\n\n\
                    #[cfg(test)]\nmod tests {\n    fn t() {\n        let _ = 1;\n    }\n}\n";

/// `path`'s text with `from` replaced by `to`.
fn swap(root: &Path, path: &str, from: &str, to: &str) {
    let text = std::fs::read_to_string(root.join(path)).unwrap();
    assert!(text.contains(from), "{from:?} in {path}");
    put(root, path, &text.replacen(from, to, 1));
}

/// RED FIRST (449 T238): a change to a Rust stage's placement - `rust/phases/src/` outside the driver, the Mode A compound's layout -
/// owed nothing and refused nothing, where the deleted Python's placement code (`l7r/**/*.py`, `CODE`) was refused at push until the
/// feature declared its occasions. A stage whose non-test code changed is refused undeclared, naming the file; a comment, a test
/// module, a test file or a file only moved is no change.
#[test]
fn a_rust_stages_change_is_refused_until_an_occasion_is_declared() {
    let r = repo("stages");
    put(&r, "rust/phases/src/seat.rs", SEAT);
    put(&r, "rust/phases/src/seat/tests.rs", "fn t() {}\n");
    put(
        &r,
        "rust/mode_a/src/compound/layout.rs",
        "pub fn court(w: f64) -> f64 {\n    w / 2.0\n}\n",
    );
    put(&r, "rust/mode_a/src/compound/gen_tests.rs", "fn t() {}\n");
    commit(&r, "stages");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    let reset = || {
        sh(
            &r,
            "git checkout -q -- rust && git clean -qfd rust specs .specify",
        );
    };
    swap(
        &r,
        "rust/phases/src/seat.rs",
        "//! the seat",
        "//! the seat, its gap",
    );
    swap(&r, "rust/phases/src/seat.rs", "let _ = 1;", "let _ = 2;");
    put(
        &r,
        "rust/phases/src/seat/tests.rs",
        "fn t() { let _ = 3; }\n",
    );
    put(
        &r,
        "rust/mode_a/src/compound/gen_tests.rs",
        "fn t() { let _ = 3; }\n",
    );
    assert_eq!(check_declared(&r), None);
    swap(&r, "rust/phases/src/seat.rs", "7.0", "8.0");
    let refusal = check_declared(&r).unwrap();
    assert!(refusal.starts_with(
        "drawing or placement code moved (rust/phases/src/seat.rs) and no declaration answers"
    ));
    // it owes no unit by itself: the feature declares what it re-places
    assert!(owed_slugs(&r).is_empty());
    started(&r, "900-x", "T1");
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- none: T1 - the gap a guess moved\n",
    );
    assert_eq!(check_declared(&r), None);
    reset();
    swap(
        &r,
        "rust/mode_a/src/compound/layout.rs",
        "w / 2.0",
        "w / 3.0",
    );
    assert!(check_declared(&r)
        .unwrap()
        .contains("(rust/mode_a/src/compound/layout.rs)"));
    reset();
    sh(
        &r,
        "git mv rust/phases/src/seat.rs rust/phases/src/seats.rs",
    );
    assert_eq!(check_declared(&r), None);
}

/// RED FIRST (449 T238): a declaration naming no element (`placement-changed: - on kuwabata`) became a unit `glyph-check--` on no map
/// that nobody could run, refused at push as owed with no verdict; it is refused with its form, owing nothing - with no code touched
/// too - and so is a line naming nothing at all, an unknown occasion, and a line of another kind naming no map or sheet.
#[test]
fn a_declaration_naming_no_element_is_refused_with_its_form() {
    let r = repo("no-element");
    hamlet(&r, "kuwabata", &["marsh"]);
    commit(&r, "map");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- placement-changed: - on kuwabata\n",
    );
    let (_, units, problems) = all_owed(&r);
    assert!(units.is_empty(), "{:?}", slugs(&units));
    let line = "`- placement-changed: - on kuwabata` (specs/900-x) names no element";
    assert!(problems.iter().any(|p| p.contains(line)), "{problems:?}");
    let refusal = check_declared(&r).unwrap();
    assert!(refusal.contains(line), "{refusal}");
    assert!(refusal
        .contains("`- placement-changed: <element>` or `- placement-changed: <element> on <map>`"));
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- glyph-redrawn:\n- new-form: ?\n- new-program: granary\n- new-program: ? s\n- placement-change: marsh\n- none:\n",
    );
    assert!(all_owed(&r).1.is_empty());
    let refusal = check_declared(&r).unwrap();
    for part in [
        "`- glyph-redrawn:` (specs/900-x) names no element",
        "`- new-form: ?` (specs/900-x) names no map",
        "`- new-program: granary` (specs/900-x) names no sheet",
        "`- new-program: ? s` (specs/900-x) names no program",
        "`- none:` (specs/900-x) names no reason - write it `- none: <why>`",
        "`- placement-change: marsh` (specs/900-x) is no occasion (one of glyph-redrawn,",
    ] {
        assert!(refusal.contains(part), "{part} in {refusal}");
    }
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- placement-changed: marsh on kuwabata - T236\n",
    );
    assert_eq!(owed_slugs(&r), ["glyph-check--marsh--kuwabata"]);
    assert_eq!(check_declared(&r), None);
}

/// RED FIRST (449 T238, found in its scratch gate run): a Mode A sheet's placeholder marks (`data-kind="-"`, the compound's title) read
/// as an element, so a sheet whose base drawing could not be read owed `glyph-check----<sheet>` and `size-audit--`, units nobody can
/// run; a sheet's kinds leave out what is no element, as a hamlet's ink census does.
#[test]
fn a_sheets_placeholder_mark_is_no_element() {
    let r = repo("placeholder");
    sheet(&r, "pool", "s", &["gate", "-", "place"]);
    let owed = owed_slugs(&r);
    assert_eq!(
        owed,
        [
            "building-review--s",
            "glyph-check--gate--s",
            "size-audit--gate"
        ]
    );
}

/// A tweak's `Occasion:` commit line is never refused with its form (449 T238): a commit message cannot be rewritten, so the refusal
/// could not be met. A line naming no element owes no unit and is a problem line; one with nothing after its colon declares nothing,
/// as before (`Occasion: none:` is no declaration), so undeclared code is still refused.
#[test]
fn a_tweaks_commit_line_is_never_refused_with_its_form() {
    let r = repo("tweak-form");
    hamlet(&r, "kuwabata", &["marsh"]);
    put(&r, "rust/phases/src/seat.rs", SEAT);
    commit(&r, "map");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    sh(&r, "git commit -q --allow-empty -m tweak -m 'Occasion: placement-changed: - on kuwabata' -m 'Occasion: bogus: x'");
    let (_, units, problems) = all_owed(&r);
    assert!(units.is_empty());
    assert!(problems[0].starts_with(
        "`- placement-changed: - on kuwabata` (the delta's commit messages) names no element"
    ));
    assert_eq!(check_declared(&r), None);
    let r = repo("tweak-blank");
    put(&r, "rust/phases/src/seat.rs", SEAT);
    commit(&r, "stage");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(&r, "rust/phases/src/seat.rs", "7.0", "8.0");
    commit(&r, "the gap");
    sh(
        &r,
        "git commit -q --allow-empty -m tweak -m 'Occasion: none:'",
    );
    assert!(check_declared(&r)
        .unwrap()
        .starts_with("drawing or placement code moved (rust/phases/src/seat.rs)"));
}

/// RED FIRST (449 T238 round 2): a tweak's commit line is never refused with its form, but one that owes nothing anyone can run - an
/// unknown occasion, a line naming no element, a map the pool does not hold - answered the refusal of undeclared placement code all the
/// same, as a section did: it answers nothing, and a later commit can carry a line that does.
#[test]
fn a_misformed_commit_line_answers_no_undeclared_code() {
    let r = repo("tweak-misformed");
    hamlet(&r, "kuwabata", &["marsh"]);
    put(&r, "rust/phases/src/seat.rs", SEAT);
    commit(&r, "stage");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(&r, "rust/phases/src/seat.rs", "7.0", "8.0");
    commit(&r, "the gap");
    for line in [
        "Occasion: bogus: x",
        "Occasion: placement-changed: - on kuwabata",
        "Occasion: placement-changed: marsh on nowhere",
    ] {
        sh(
            &r,
            &format!("git commit -q --allow-empty -m tweak -m '{line}'"),
        );
        assert!(check_declared(&r)
            .unwrap()
            .starts_with("drawing or placement code moved (rust/phases/src/seat.rs)"));
    }
    sh(
        &r,
        "git commit -q --allow-empty -m tweak -m 'Occasion: placement-changed: marsh on kuwabata - the gap'",
    );
    assert_eq!(check_declared(&r), None);
}

/// RED FIRST (449 T238 round 2): ANY `## Occasions` section silenced the refusal - one whose every line had landed, another feature's.
/// T236's commit (0f7583f1b) replayed with its own line taken out was refused nothing: 444's and 451's sections, touched by the delta
/// and every line on main, and 449's, naming other tasks, each answered it. The refusal is met only by a declaration that answers THIS
/// delta: a line of an active feature's section naming the task the landing holds (`make task-start`'s mark, a task not ticked at the
/// base), or a commit's `Occasion:` line. The fixture is T236's shape: a stage's code changed, a stage's comment, three sections.
#[test]
fn only_a_line_naming_the_started_task_answers_the_delta() {
    let r = repo("t236");
    put(
        &r,
        "rust/phases/src/waterward.rs",
        "pub fn strip(w: f64) -> f64 {\n    w\n}\n",
    );
    put(
        &r,
        "rust/phases/src/field/dike.rs",
        "// the dike\npub fn dike() {}\n",
    );
    feature(
        &r,
        "444-w",
        "- [x] T16 the field\n- [ ] T17 next\n\n## Occasions\n\n- none: T01 - tooling\n",
    );
    feature(
        &r,
        "451-t",
        "- [ ] T26 the event log\n\n## Occasions\n\n- none: tooling only - no map feature, glyph or placement rule\n",
    );
    feature(
        &r,
        "449-r",
        "- [x] T234 the sluice\n- [ ] T236 the reed strip\n\n## Occasions\n\n- none: phase 1 moves the guards\n\
         - none: T234 - the sluice's frame, set aside\n",
    );
    commit(&r, "base");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(
        &r,
        "rust/phases/src/waterward.rs",
        "    w\n",
        "    w - 1.0\n",
    );
    swap(
        &r,
        "rust/phases/src/field/dike.rs",
        "// the dike",
        "// the dike's face",
    );
    swap(&r, "specs/444-w/tasks.md", "- [ ] T17", "- [x] T17");
    swap(&r, "specs/451-t/tasks.md", "- [ ] T26", "- [x] T26");
    commit(&r, "449 T236 and 451 T26");
    started(&r, "449-r", "T236");
    let refusal = check_declared(&r).unwrap();
    assert!(
        refusal.starts_with("drawing or placement code moved (rust/phases/src/waterward.rs) and")
    );
    assert!(refusal.contains(
        "the started task, specs/449-r T236 (`make task-start`), is named by no line of its `## Occasions`"
    ));
    assert!(refusal.contains("`- none: T236 - <why>`"), "{refusal}");
    // a line naming another task, or one whose id only begins with this one's, answers nothing
    swap(
        &r,
        "specs/449-r/tasks.md",
        "set aside\n",
        "set aside\n- none: T23 - and T2360, other tasks\n",
    );
    assert!(check_declared(&r).is_some());
    // with no task started, no feature's line answers the delta
    std::fs::remove_file(r.join(".git/active-task")).unwrap();
    assert!(check_declared(&r).unwrap().contains(
        "no task of an active feature is started (`make task-start F=<feature> T=<task>`)"
    ));
    // a mark left by a task ticked at the base answers nothing, though its own line is there
    started(&r, "449-r", "T234");
    assert!(check_declared(&r)
        .unwrap()
        .contains("the started task, specs/449-r T234, was ticked on main already"));
    // a mark on another feature's task its section does not name
    started(&r, "451-t", "T26");
    assert!(check_declared(&r)
        .unwrap()
        .contains("specs/451-t T26 (`make task-start`), is named by no line"));
    // the started task's line answers it, whatever its kind
    started(&r, "449-r", "T236");
    swap(
        &r,
        "specs/449-r/tasks.md",
        "- none: T23 -",
        "- placement-changed: - on x - T236\n- none: T236: the strip's ground, no element re-placed\n- none: T23 -",
    );
    assert!(check_declared(&r)
        .unwrap()
        .starts_with("an `## Occasions` declaration owes a review nobody can run"));
    swap(
        &r,
        "specs/449-r/tasks.md",
        "- placement-changed: - on x - T236\n",
        "",
    );
    assert_eq!(check_declared(&r), None);
    // and so does a line already on main (a declaration pushed with the spec, before the code)
    commit(&r, "declared");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(&r, "rust/phases/src/waterward.rs", "w - 1.0", "w - 2.0");
    assert_eq!(check_declared(&r), None);
    // and a commit's `Occasion:` line, with no task started
    std::fs::remove_file(r.join(".git/active-task")).unwrap();
    assert!(check_declared(&r).is_some());
    commit(
        &r,
        "tweak\n\nOccasion: none: the strip's width, no element re-placed",
    );
    assert_eq!(check_declared(&r), None);
}

/// RED FIRST (449 T238 round 2): a declaration naming a map that is no pool map or sheet (`well on nowhere`) became a unit on no map and
/// a problem line. A map's NAME is checkable with no redraw (the pool walk alone), so it is refused with its form, naming the pool's
/// closest maps, and owes no unit; a tweak's commit line so formed is a problem line, never refused. An element not drawn on a real map
/// is left as it was: it may be new to the map, its drawing stale until the gate redraws it.
#[test]
fn a_declaration_naming_no_pool_map_is_refused_naming_the_closest() {
    let r = repo("no-map");
    hamlet(&r, "kuwabata", &["marsh"]);
    hamlet(&r, "inashiro", &["paddy"]);
    sheet(&r, "pool", "ochiba", &["gate"]);
    commit(&r, "maps");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- glyph-redrawn: well on kuwabta - T1\n",
    );
    let (_, units, problems) = all_owed(&r);
    assert!(units.is_empty(), "{:?}", slugs(&units));
    let line = "`- glyph-redrawn: well on kuwabta - T1` (specs/900-x) names `kuwabta`, no pool map or sheet - the closest: kuwabata, ";
    assert!(problems.iter().any(|p| p.starts_with(line)), "{problems:?}");
    let refusal = check_declared(&r).unwrap();
    assert!(refusal.contains(line), "{refusal}");
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- new-form: inashro\n- gm-fix: nowhere - the complaint\n- layout-revised: ochba\n\
         - new-program: granary ochba\n- placement-changed: well on nowhere\n",
    );
    assert!(all_owed(&r).1.is_empty());
    let refusal = check_declared(&r).unwrap();
    for part in [
        "`- new-form: inashro` (specs/900-x) names `inashro`, no pool map or sheet - the closest: inashiro, ",
        "`- gm-fix: nowhere - the complaint` (specs/900-x) names `nowhere`",
        "`- layout-revised: ochba` (specs/900-x) names `ochba`, no pool map or sheet - the closest: ochiba, ",
        "`- new-program: granary ochba` (specs/900-x) names `ochba`",
        "`- placement-changed: well on nowhere` (specs/900-x) names `nowhere`",
    ] {
        assert!(refusal.contains(part), "{part} in {refusal}");
    }
    // an element a real map's current drawing does not hold is no matter for `--check-declared`, which reads no drawing: it is
    // `--check-drawn`'s, after the gate's redraw (`a_declared_element_its_current_drawing_does_not_hold_is_refused`)
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- glyph-redrawn: well on kuwabata - T1\n",
    );
    assert!(all_owed(&r).1.is_empty());
    assert_eq!(check_declared(&r), None);
    assert!(check_drawn(&r).is_some());
    // a tweak's commit line naming no map owes no unit and is a problem line, never refused
    sh(&r, "rm -rf specs .specify");
    sh(
        &r,
        "git commit -q --allow-empty -m tweak -m 'Occasion: glyph-redrawn: well on nowhere'",
    );
    let (_, units, problems) = all_owed(&r);
    assert!(units.is_empty(), "{:?}", slugs(&units));
    assert!(problems.iter().any(|p| p.starts_with(
        "`- glyph-redrawn: well on nowhere` (the delta's commit messages) names `nowhere`, no pool map or sheet"
    )), "{problems:?}");
    assert_eq!(check_declared(&r), None);
    // a pool with no map names none
    let empty = repo("no-pool");
    feature(
        &empty,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- new-form: m\n",
    );
    assert!(check_declared(&empty)
        .unwrap()
        .contains("names `m`, no pool map or sheet - the pool has none;"));
}

/// RED FIRST (449 T238 round 2): a line that only MENTIONS the started task (`found by T236`, inside another task's line) answered the
/// delta, the same hole as a section answering: the task named anywhere in the argument matched. A line answers only when the task is
/// its own: a `none:` line's first word, a declaration's tag - the first word after its subject's ` - ` (`- T236: <why>`, the form the
/// refusal prints) - or its trailing parenthetical (`(... T236 ...)`, read across a wrapped line). Each of 449's and 444's lines naming
/// its task, as written there (observed 2026-11-20), still answers its own task.
#[test]
fn a_line_answers_only_for_its_own_task() {
    let r = repo("own-task");
    hamlet(&r, "kuwabata", &["marsh", "sluice gate"]);
    hamlet(&r, "inashiro", &["paddy"]);
    put(&r, "rust/phases/src/seat.rs", SEAT);
    feature(
        &r,
        "449-r",
        "- [ ] T236 the strip\n- [ ] T239 the seat\n- [ ] T234 the sluice\n- [ ] T16 the field\n",
    );
    commit(&r, "base");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(&r, "rust/phases/src/seat.rs", "7.0", "8.0");
    let with = |lines: &str| {
        feature(
            &r,
            "449-r",
            &format!("- [ ] T236 the strip\n- [ ] T239 the seat\n- [ ] T234 the sluice\n- [ ] T16 the field\n\n## Occasions\n\n{lines}"),
        );
        check_declared(&r)
    };
    started(&r, "449-r", "T236");
    // a feature with no section names it nowhere
    assert!(check_declared(&r).unwrap().contains("is named by no line"));
    // a mention answers nothing
    for line in [
        "- none: T239 - the seat's ring, found by T236\n",
        "- placement-changed: marsh on kuwabata - the strip T236 laid, re-placed\n",
        "- none: the strip (T236) re-laid by hand - a reason\n",
    ] {
        assert!(with(line).is_some(), "{line}");
    }
    // the task's own forms answer: the lines as 449 and 444 wrote them, a trailing parenthetical, one wrapped onto the next line
    for (task, line) in [
        ("T234", "- glyph-redrawn: sluice gate on kuwabata - T234: the polder's sluice redrawn; set aside at rust-only (444 FR-023)\n"),
        ("T236", "- placement-changed: marsh on kuwabata - T236: the waterside reed strip laid from the dike's outer face\n"),
        ("T239", "- none: T239 - the seat on a polder handed a ring off the dike's outer face\n"),
        ("T16", "- placement-changed: paddy on inashiro - T16 rebuilt the comb field's placement in Rust (the fan,\n  the brook and its weir)\n"),
        ("T236", "- none: the strip's ground, no element re-placed (449 T236)\n"),
        ("T236", "- placement-changed: marsh on kuwabata - the reed strip re-laid\n  from the dike's face (T236)\n"),
    ] {
        started(&r, "449-r", task);
        assert_eq!(with(line), None, "{line}");
    }
}

/// RED FIRST (449 T238 round 2, the plan review's D9): a declared line naming an element its map's drawing does not hold (`sluice gat on
/// kuwabata`) still became a unit on no map, which nobody can run. Where the map's drawing is current - after the review gate's redraw,
/// when it asks what is owed - the legend is known, so `--check-drawn` refuses the line with its form, naming the map's closest drawn
/// kinds, and it owes no unit; an element with no map named is refused once every live map's legend is known. A drawing not current
/// leaves it as it was (the element may be new to it); a tweak's commit line so formed is a problem line, never refused.
#[test]
fn a_declared_element_its_current_drawing_does_not_hold_is_refused() {
    let r = repo("undrawn-element");
    hamlet(&r, "kuwabata", &["marsh", "sluice gate"]);
    sheet(&r, "pool", "ochiba", &["gate"]);
    commit(&r, "maps");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    let drawn_check = |r: &Path| check_drawn(r);
    assert_eq!(drawn_check(&r), None);
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- glyph-redrawn: sluice gat on kuwabata - T1: the frame\n- placement-changed: gat - T1\n\
         - glyph-redrawn: marsh on kuwabata - T1\n- glyph-redrawn: qq on kuwabata - T1\n",
    );
    let (_, units, problems) = all_owed(&r);
    assert_eq!(slugs(&units), ["glyph-check--marsh--kuwabata"]);
    assert_eq!(cli_in(&r, &["--check-drawn"]).code, 1);
    let refusal = drawn_check(&r).unwrap();
    // kinds alike in their distance from the name are named in order
    assert!(refusal.contains("names `qq`, which kuwabata's drawing does not hold - its closest drawn kinds: marsh, sluice gate;"));
    for part in [
        "`- glyph-redrawn: sluice gat on kuwabata - T1: the frame` (specs/900-x) names `sluice gat`, which kuwabata's drawing does not \
         hold - its closest drawn kinds: sluice gate, ",
        "`- placement-changed: gat - T1` (specs/900-x) names `gat`, which no pool map or sheet draws - the closest drawn kinds: gate, ",
    ] {
        assert!(refusal.contains(part), "{part} in {refusal}");
        assert!(problems.iter().any(|p| part.starts_with(p.as_str()) || p.starts_with(part)), "{part} in {problems:?}");
    }
    // a drawing not current is left as it was: a unit on no map and a problem line, refused nothing
    put(
        &r,
        "pool/hamlets/kuwabata/kuwabata.spec.json",
        "{\"seed\": 2}",
    );
    let (_, units, _) = all_owed(&r);
    assert!(
        slugs(&units).contains(&"glyph-check--sluice-gat".to_owned()),
        "{:?}",
        slugs(&units)
    );
    assert_eq!(drawn_check(&r), None);
    // a tweak's commit line is a problem line, never refused
    sh(&r, "git checkout -q -- pool && rm -rf specs .specify");
    sh(&r, "git commit -q --allow-empty -m tweak -m 'Occasion: glyph-redrawn: sluice gat on kuwabata - the frame'");
    let (_, units, problems) = all_owed(&r);
    assert!(units.is_empty(), "{:?}", slugs(&units));
    assert!(
        problems
            .iter()
            .any(|p| p.contains("names `sluice gat`, which kuwabata's drawing does not hold")),
        "{problems:?}"
    );
    assert_eq!(drawn_check(&r), None);
}

/// RED FIRST (449 T238 round 2, the plan review's D9c): a commit `Occasion:` line naming an element its map's current drawing does not
/// hold (`placement-changed: sluice gat on kuwabata`) passed `--check-declared`, answered the delta's placement code, and after D9 owed no
/// unit - so the code shipped unreviewed. At `--check-drawn`, where the drawing is current, such a line answers nothing: the delta's
/// undeclared placement code is refused there (the line itself is still never refused). A map not current is left as it was (D9r).
#[test]
fn a_commit_line_naming_an_undrawn_element_answers_nothing_once_drawn() {
    let r = repo("tweak-undrawn");
    hamlet(&r, "kuwabata", &["marsh", "sluice gate"]);
    put(&r, "rust/phases/src/seat.rs", SEAT);
    commit(&r, "stage");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(&r, "rust/phases/src/seat.rs", "7.0", "8.0");
    commit(
        &r,
        "the gap\n\nOccasion: placement-changed: sluice gat on kuwabata - the gap",
    );
    assert_eq!(check_declared(&r), None);
    assert!(all_owed(&r).1.is_empty());
    let refusal = check_drawn(&r).unwrap();
    assert!(
        refusal.starts_with("drawing or placement code moved (rust/phases/src/seat.rs) and no declaration answers this delta: the \
             delta's `Occasion:` commit lines name only elements their maps' current drawings do not hold"),
        "{refusal}"
    );
    // its drawing not current, the line is left to answer as before (D9r)
    put(
        &r,
        "pool/hamlets/kuwabata/kuwabata.spec.json",
        "{\"seed\": 2}",
    );
    assert_eq!(check_drawn(&r), None);
    sh(&r, "git checkout -q -- pool");
    // a line of another kind answers it, as does one naming what the drawing holds
    sh(&r, "git commit -q --allow-empty -m tweak -m 'Occasion: none: the gap, nothing drawn re-placed'");
    assert_eq!(check_drawn(&r), None);
    sh(&r, "git reset -q --soft HEAD~1");
    assert!(check_drawn(&r).is_some());
    sh(&r, "git commit -q --allow-empty -m tweak -m 'Occasion: placement-changed: sluice gate on kuwabata - the gap'");
    assert_eq!(check_drawn(&r), None);
}

/// A drawing made by an engine older than the one the tree builds now is not current (the plan review's D9r): a delta that adds an element
/// and declares it is never refused for the old drawing's legend. The stand-in engine changed, its id moves, the drawing is not current,
/// and the declared new element is left as before - a unit and a problem line - until the redraw by the delta's own engine.
#[test]
fn a_drawing_by_an_older_engine_refuses_no_declared_new_element() {
    let r = repo("older-engine");
    hamlet(&r, "kuwabata", &["marsh"]);
    commit(&r, "map");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    feature(
        &r,
        "900-x",
        "- [ ] T1\n\n## Occasions\n\n- glyph-redrawn: sluice frame on kuwabata - T1: new\n",
    );
    assert!(check_drawn(&r).is_some());
    put(
        &r,
        ".git/engine.bin",
        "the engine rebuilt from the delta's sources",
    );
    assert_eq!(check_drawn(&r), None);
    assert_eq!(owed_slugs(&r), ["glyph-check--sluice-frame"]);
    // redrawn by it, the drawing holds the new element, and it owes its glyph-check on the map
    drawn(&r, "kuwabata", &["marsh", "sluice frame"]);
    assert_eq!(check_drawn(&r), None);
    assert_eq!(owed_slugs(&r), ["glyph-check--sluice-frame--kuwabata"]);
}

/// A PIN (449 T238 round 2, the plan review's round 3, green on the D9c code as written): a commit glyph line naming NO map (`Occasion:
/// placement-changed: sluice gat - the gap`) is decided at `--check-drawn` as the `tasks.md` side decides one: it answers nothing once every
/// live legend is known and none holds the element, it answers when some legend holds it, and while any live legend is unknown it is left
/// to answer (D9r).
#[test]
fn a_commit_line_naming_no_map_is_decided_by_every_legend() {
    let r = repo("tweak-no-map");
    hamlet(&r, "kuwabata", &["marsh", "sluice gate"]);
    put(&r, "rust/phases/src/seat.rs", SEAT);
    commit(&r, "stage");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(&r, "rust/phases/src/seat.rs", "7.0", "8.0");
    commit(
        &r,
        "the gap\n\nOccasion: placement-changed: sluice gat - the gap",
    );
    assert_eq!(check_declared(&r), None);
    assert!(check_drawn(&r)
        .unwrap()
        .starts_with("drawing or placement code moved (rust/phases/src/seat.rs) and no declaration answers this delta"));
    // a live legend unknown: left to answer (D9r)
    put(
        &r,
        "pool/hamlets/kuwabata/kuwabata.spec.json",
        "{\"seed\": 2}",
    );
    assert_eq!(check_drawn(&r), None);
    sh(&r, "git checkout -q -- pool");
    // some legend holds the element: it answers
    sh(&r, "git commit -q --allow-empty -m tweak -m 'Occasion: placement-changed: sluice gate - the gap'");
    assert_eq!(check_drawn(&r), None);
}

/// RED FIRST (451 T166): `make verify` judges the occasions in the review tree, whose `.specify/feature.json` is gitignored and so absent,
/// by the clone's ONE started-task mark - which another builder's `make task-start` or `make set-down` moves (measured 2026-11-23: 449
/// T328's two verify runs met it cleared by a 449 set-down at 03:02:52Z and naming 451 T90 at 03:24Z, and each printed "no task of an
/// active feature is started" over lines naming T328). Verify carries its bundle in, `L7R_VERIFY_STARTED="<feature> <tasks>"`, read in
/// place of the mark: its feature (a number, a directory or `specs/<dir>`) is active as the pointer's is, and its first task - the one
/// `make task-start` marks and the landing's holding box reads - is the started one. A feature naming no directory leaves the mark's rule.
#[test]
fn verify_judges_its_own_bundle_not_the_clones_shared_mark() {
    let r = repo("verify-started");
    hamlet(&r, "kuwabata", &["marsh", "sluice gate"]);
    put(&r, "rust/phases/src/seat.rs", SEAT);
    feature(&r, "449-r", "- [ ] T236 the strip\n- [ ] T239 the seat\n");
    std::fs::remove_file(r.join(".specify/feature.json")).unwrap();
    commit(&r, "base");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(&r, "rust/phases/src/seat.rs", "7.0", "8.0");
    put(
        &r,
        "specs/449-r/tasks.md",
        "- [ ] T236 the strip\n- [ ] T239 the seat\n\n## Occasions\n\n- none: T236 - the strip's gap\n",
    );
    let verify = |bundle: &str| {
        let env = Rooted::with(&*r, &[("L7R_VERIFY_STARTED", bundle)]);
        let args = [
            "--root".to_owned(),
            r.display().to_string(),
            "--check-declared".to_owned(),
        ];
        let said = crate::reviews::owed::cli_in(&args, &env);
        (said.code, said.stdout)
    };
    let none = "no task of an active feature is started";
    // the shared mark names another feature's task (03:24Z), or none (03:12Z): refused without the bundle, answered with it
    started(&r, "451-t", "T90");
    assert!(verify("").1.contains(none));
    for bundle in ["449 T236", "449-r T236,T239", "specs/449-r/ T236 T239"] {
        assert_eq!(verify(bundle), (0, String::new()), "{bundle}");
    }
    std::fs::remove_file(r.join(".git/active-task")).unwrap();
    assert!(verify("").1.contains(none));
    assert_eq!(verify("449 T236"), (0, String::new()));
    // another active feature's tasks, the mark's or not, are passed over for the bundle's
    put(&r, "specs/300-o/tasks.md", "- [ ] T1 another builder's\n");
    sh(&r, "git add -N specs/300-o");
    started(&r, "300-o", "T1");
    assert!(verify("").1.contains("the started task, specs/300-o T1"));
    assert_eq!(verify("449 T236"), (0, String::new()));
    sh(
        &r,
        "git rm -q --cached specs/300-o/tasks.md && rm -r specs/300-o",
    );
    // the bundle's first task is the started one, as the mark's is: a line naming only another of its tasks answers nothing
    let (code, said) = verify("449 T239,T236");
    assert_eq!(code, 1);
    assert!(
        said.contains(
            "the started task, specs/449-r T239 (`make task-start`), is named by no line"
        ),
        "{said}"
    );
    // a feature naming no directory, or no task, leaves the mark's rule
    started(&r, "449-r", "T236");
    assert_eq!(verify("999 T1"), (0, String::new()));
    assert_eq!(verify("449"), (0, String::new()));
    started(&r, "451-t", "T90");
    assert!(verify("999 T1").1.contains(none));
    // a task ticked at the base is refused as the mark's is
    put(
        &r,
        "specs/449-r/tasks.md",
        "- [x] T236 the strip\n- [ ] T239 the seat\n",
    );
    commit(&r, "ticked");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    swap(&r, "rust/phases/src/seat.rs", "8.0", "9.0");
    assert!(verify("449 T236")
        .1
        .contains("the started task, specs/449-r T236, was ticked on main already"));
}
