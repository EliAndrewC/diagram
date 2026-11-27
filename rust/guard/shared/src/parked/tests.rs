//! The parked stages' predicates over a fixture checkout (feature 449 T244).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{
    common_of, held_task, record, refusal, resumed, shell_hits, stage_of, stages, words,
    write_hits, Hit,
};
use crate::tool::ask;

/// A checkout with `rust/parked/src/` holding homesteads (a file and its directory), track and the crate's own lib.rs.
fn world(tag: &str) -> (crate::tempdir::TempDir, PathBuf) {
    let d = crate::tempdir::TempDir::new(&format!("parked-{tag}"));
    let c = d.canonicalize().unwrap().join("c");
    std::fs::create_dir_all(c.join("rust/parked/src/homesteads")).unwrap();
    std::fs::create_dir_all(c.join("rust/phases/src")).unwrap();
    for f in ["homesteads.rs", "track.rs", "lib.rs", "notes.txt"] {
        std::fs::write(c.join("rust/parked/src").join(f), "").unwrap();
    }
    let made = ask(
        Path::new("/"),
        "git",
        &["init", "-q", &c.to_string_lossy()],
        "",
    );
    assert!(made.ok());
    (d, c)
}

fn hit(root: &Path, stage: &str, declares: bool) -> Hit {
    Hit {
        root: root.to_string_lossy().into_owned(),
        stage: stage.to_owned(),
        declares,
    }
}

#[test]
fn the_stages_are_what_the_parked_crate_holds() {
    let (_d, c) = world("stages");
    let found = stages(&c);
    assert_eq!(found, ["homesteads", "track"]);
    let none = stages(&c.join("nowhere"));
    assert!(none.is_empty());
}

#[test]
fn a_task_s_stage_is_its_line_s_phase_or_a_line_of_its_block() {
    let line = stage_of("- [ ] T30 phase: homesteads - every household seated");
    assert_eq!(line.as_deref(), Some("homesteads"));
    let title = stage_of("[P] phase: track - a row village's road");
    assert_eq!(title.as_deref(), Some("track"));
    let block = stage_of("- [ ] T14 the field\n      phase: field\n");
    assert_eq!(block.as_deref(), Some("field"));
    let prose = stage_of("- [ ] T99 the phase: homesteads task's tooling");
    assert_eq!(prose, None);
}

#[test]
fn a_stage_is_held_until_a_row_resumes_it() {
    let (_d, c) = world("held");
    let common = common_of(&c);
    assert_eq!(common, c.join(".git"));
    let held = held_task(&c, &common, "phase: homesteads - every household");
    assert_eq!(held.as_deref(), Some("homesteads"));
    let ported = held_task(&c, &common, "phase: seat - where the settlement sits");
    assert_eq!(ported, None);
    record(
        &common,
        &json!({"stage": "homesteads", "words": "go ahead with homesteads"}),
    )
    .unwrap();
    let after = held_task(&c, &common, "phase: homesteads - every household");
    assert_eq!(after, None);
    assert!(resumed(&common, "homesteads"));
    assert!(!resumed(&common, "track"));
    let unwritable = record(&c.join("missing"), &json!({}));
    assert!(unwritable.is_err());
    let fallback = common_of(&c.join("not-a-checkout"));
    assert_eq!(fallback, c.join("not-a-checkout/.git"));
}

#[test]
fn a_write_of_a_parked_stage_s_file_or_its_mod_line_is_a_hit() {
    let (_d, c) = world("writes");
    let at = |rel: &str| format!("{}/rust/phases/src/{rel}", c.display());
    let moved = write_hits(&at("homesteads.rs"), "", "");
    assert_eq!(moved, [hit(&c, "homesteads", false)]);
    let inner = write_hits(&at("homesteads/cluster.rs"), "", "");
    assert_eq!(inner, [hit(&c, "homesteads", false)]);
    let declared = write_hits(&at("lib.rs"), "mod seat;\npub mod track;\n", "mod seat;\n");
    assert_eq!(declared, [hit(&c, "track", true)]);
    let kept = write_hits(&at("lib.rs"), "mod track; // kept\n", "mod track;\n");
    assert!(kept.is_empty());
    let other = write_hits(&at("seat.rs"), "", "");
    assert!(other.is_empty());
    let dir = write_hits(&at(""), "", "");
    assert!(dir.is_empty());
    let elsewhere = write_hits(
        &format!("{}/rust/phases/srcs/homesteads.rs", c.display()),
        "",
        "",
    );
    assert!(elsewhere.is_empty());
    let outside = write_hits("/tmp/homesteads.rs", "", "");
    assert!(outside.is_empty());
}

#[test]
fn a_shell_move_into_the_phases_is_a_hit_and_a_mention_is_not() {
    let (_d, c) = world("shell");
    let top = c.to_string_lossy().into_owned();
    let home = "/home/nobody";
    let git_mv = shell_hits(
        "git mv rust/parked/src/homesteads.rs rust/phases/src/",
        &top,
        home,
    );
    assert_eq!(git_mv, [hit(&c, "homesteads", false)]);
    let star = shell_hits("mv rust/parked/src/* rust/phases/src/", &top, home);
    let ok1 = star;
    assert_eq!(ok1, [hit(&c, "homesteads", false), hit(&c, "track", false)]);
    let named = shell_hits(
        "cp rust/parked/src/track.rs rust/phases/src/track.rs",
        &top,
        home,
    );
    assert_eq!(named, [hit(&c, "track", false)]);
    let parked = format!("{top}/rust/parked/src");
    let standing = shell_hits("mv track.rs ../../phases/src/", &parked, home);
    assert_eq!(standing, [hit(&c, "track", false)]);
    let declared = shell_hits(
        "echo 'mod homesteads;' >> rust/phases/src/lib.rs",
        &top,
        home,
    );
    assert_eq!(declared, [hit(&c, "homesteads", true)]);
    let read = shell_hits(
        "grep -n 'mod homesteads' rust/phases/src/lib.rs",
        &top,
        home,
    );
    assert!(read.is_empty());
    let mention = shell_hits("echo homesteads rust/parked/src/homesteads.rs", &top, home);
    assert!(mention.is_empty());
    let unrelated = shell_hits("cp a.rs rust/phases/src/", &top, home);
    assert!(unrelated.is_empty());
    let absolute = shell_hits(
        &format!("git mv rust/parked/src/track.rs {top}/rust/phases/src/"),
        &top,
        home,
    );
    assert_eq!(absolute, [hit(&c, "track", false)]);
    let unplaced = shell_hits("echo phases > \"$(mktemp)\"", &top, home);
    assert!(unplaced.is_empty());
    // a write from a directory the walk cannot place lands nowhere it can name
    let lost = shell_hits("cd \"$NOPE\" && touch phases", &top, home);
    assert!(lost.is_empty());
    let unnamed = shell_hits("ls", &top, home);
    assert!(unnamed.is_empty());
    let unknown = shell_hits("cp x \"$DEST\"/phases", &top, home);
    assert!(unknown.is_empty());
}

/// 451 T453: a `git mv` is read to its destination however git is spelled; a program whose name only ends in git is not git.
#[test]
fn a_git_move_is_read_however_git_is_spelled() {
    let (_d, c) = world("spelled");
    let top = c.to_string_lossy().into_owned();
    for s in ["\\", "/usr/bin/", "command ", "env -i ", "A=1 nice -n 5 "] {
        let cmd = format!("{s}git mv rust/parked/src/track.rs rust/phases/src/");
        let got = shell_hits(&cmd, &top, "/home/nobody");
        assert_eq!(got, [hit(&c, "track", false)], "{cmd}");
    }
    let other = shell_hits(
        "/tmp/mygit mv rust/parked/src/track.rs rust/phases/src/",
        &top,
        "/home/nobody",
    );
    assert!(other.is_empty());
}

#[test]
fn the_words_and_the_refusal() {
    let quoted = words("GM_RESUMED=\"go on with homesteads now\" make task-start F=444 T=T30");
    assert_eq!(quoted.as_deref(), Some("go on with homesteads now"));
    let single = words("GM_RESUMED='go on' make x");
    assert_eq!(single.as_deref(), Some("go on"));
    let bare = words("GM_RESUMED=yes make x");
    assert_eq!(bare.as_deref(), Some("yes"));
    let none = words("make task-start F=444 T=T30");
    assert_eq!(none, None);
    let written = words(
        "cat >> notes.md <<'EOF'\nGM_RESUMED=\"his words here\" make task-start F=444 T=T30\nEOF\n",
    );
    assert_eq!(written, None);
    let quoted =
        words("make task-add F=449 TITLE=\"without GM_RESUMED=\\\"<his words>\\\" (recorded)\"");
    assert_eq!(quoted, None);
    let after = words("cd x && GM_RESUMED=\"go on now\" make task-start");
    assert_eq!(after.as_deref(), Some("go on now"));
    let text = refusal("make task-start of 444 T30 (homesteads)");
    assert!(text.contains("2026-11-21"));
    assert!(text.contains("Stop before homesteads, and talk first"));
    assert!(text.contains("GM_RESUMED=\"<the GM's words resuming it>\""));
    assert!(text.contains("make set-down F=444"));
}
