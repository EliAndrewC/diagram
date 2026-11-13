//! The text every dispatch of a check shares lives in its agent file, in step with its source (feature 383 amendment 6, D35):
//! `tests/test_agent_sync.py`'s three tests, ported by feature 449 T136 (`ask:449-phase3-remainder`), and the raises the Python met.

use std::path::{Path, PathBuf};

use super::super::tests::{dir, put};
use super::{cli, render, stale, write, SyncTable, HEAD, SYNC};

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

fn sources(pairs: &[(&'static str, &str)]) -> Vec<(&'static str, String)> {
    pairs.iter().map(|(s, t)| (*s, (*t).to_owned())).collect()
}

const STALE: &str = "an agent file's generated guidelines differ from their source - run `make agent-sync` and commit the agent file";

/// `test_every_agent_file_carries_its_sources_as_they_are`: the real tree's three agent files.
#[test]
fn every_agent_file_carries_its_sources_as_they_are() {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../..");
    let bad = stale(&root, SYNC).unwrap();
    assert!(bad.is_empty(), "{STALE}: {bad:?}");
}

/// `test_render_replaces_the_generated_part_and_keeps_the_agents_own_text`.
#[test]
fn render_replaces_the_generated_part_and_keeps_the_agents_own_text() {
    let own = "---\nname: x\n---\nThe agent's own contract.";
    let once = render(
        own,
        &sources(&[("dev/a.md", "rule one\n"), ("dev/b.md", "rule two\n")]),
    );
    assert!(once.starts_with(own));
    assert!(once.contains("<!-- generated: dev/a.md -->\nrule one\n<!-- /generated: dev/a.md -->"));
    let revised = sources(&[
        ("dev/a.md", "rule one, revised\n"),
        ("dev/b.md", "rule two\n"),
    ]);
    let again = render(&once, &revised);
    assert_eq!(again.matches(HEAD).count(), 1);
    assert!(again.contains("rule one, revised"));
    let after = again
        .split(HEAD)
        .nth(1)
        .unwrap()
        .replace("rule one, revised", "");
    assert!(!after.contains("rule one\n"));
    assert_eq!(render(&again, &revised), again, "idempotent");
    // a section left inside the agent's own part (before the heading) is taken out
    let stray = render(
        "own\n<!-- generated: dev/a.md -->\nold\n<!-- /generated: dev/a.md -->\nmore",
        &sources(&[("dev/a.md", "new")]),
    );
    assert_eq!(
        stray,
        format!("own\nmore\n\n{HEAD}\n\n<!-- generated: dev/a.md -->\nnew\n<!-- /generated: dev/a.md -->\n")
    );
}

/// A scratch clone holding one agent file `c.md` that carries `dev/g.md`.
fn scratch(name: &str) -> l7r_guard::shared::tempdir::Held<PathBuf> {
    let d = dir(name);
    put(&d, "dev/g.md", "the rule\n");
    put(&d, ".claude/agents/c.md", "contract\n");
    d
}

const ONE: SyncTable<'static> = &[(".claude/agents/c.md", &["dev/g.md"])];

/// `test_check_and_write_name_what_moved`.
#[test]
fn check_and_write_name_what_moved() {
    let d = scratch("agent-sync-cycle");
    let got = cli(&args(&["--check"]), &d, ONE);
    assert_eq!(got.code, 1);
    assert!(got.stdout.contains("run `make agent-sync`"));
    assert_eq!(
        got.stdout,
        "agent-sync: .claude/agents/c.md differs from dev/g.md - run `make agent-sync` and commit the agent file\n"
    );
    let got = cli(&[], &d, ONE);
    assert_eq!(got.code, 0);
    assert!(got.stdout.contains("1 agent file(s) written"));
    assert_eq!(
        got.stdout,
        "agent-sync: 1 agent file(s) written: .claude/agents/c.md\n"
    );
    let got = cli(&args(&["--check"]), &d, ONE);
    assert_eq!((got.code, got.stdout.as_str()), (0, ""));
    let text = std::fs::read_to_string(d.join(".claude/agents/c.md")).unwrap();
    assert!(text.contains("the rule"));
    let got = cli(&[], &d, ONE);
    assert_eq!(got.code, 0);
    assert!(got.stdout.contains("all in step"));
}

/// Python's text mode: a `\r\n` file is read with `\n`, so one in step is left as it is; one out of step is written with `\n`.
#[test]
fn a_crlf_file_is_read_as_python_text_mode_reads_it() {
    let d = scratch("agent-sync-crlf");
    assert_eq!(write(&d, ONE).unwrap(), [".claude/agents/c.md"]);
    let synced = std::fs::read_to_string(d.join(".claude/agents/c.md")).unwrap();
    std::fs::write(d.join(".claude/agents/c.md"), synced.replace('\n', "\r\n")).unwrap();
    assert_eq!(stale(&d, ONE).unwrap(), []);
    put(&d, "dev/g.md", "the rule\r\nrevised\r");
    assert_eq!(write(&d, ONE).unwrap(), [".claude/agents/c.md"]);
    let now = std::fs::read_to_string(d.join(".claude/agents/c.md")).unwrap();
    assert!(!now.contains('\r') && now.contains("the rule\nrevised\n<!-- /generated"));
}

/// A missing or undecodable file, or an agent file that cannot be written, is the Python's raise: exit 1, nothing on stdout.
#[test]
fn a_file_unread_or_unwritten_is_the_pythons_raise() {
    let raised = |root: &Path, words: &[&str], sync: SyncTable<'_>| {
        let got = cli(&args(words), root, sync);
        (
            got.code,
            got.stdout.is_empty(),
            got.stderr
                .starts_with("Traceback (most recent call last):\n  l7r-gate reviews agent-sync\n"),
        )
    };
    let d = scratch("agent-sync-raise");
    let no_source: SyncTable<'static> = &[(".claude/agents/c.md", &["dev/none.md"])];
    let no_agent: SyncTable<'static> = &[(".claude/agents/none.md", &["dev/g.md"])];
    for words in [&[][..], &["--check"][..]] {
        assert_eq!(raised(&d, words, no_source), (1, true, true));
        assert_eq!(raised(&d, words, no_agent), (1, true, true));
    }
    std::fs::write(d.join("dev/g.md"), [0xff_u8]).unwrap();
    assert_eq!(raised(&d, &[], ONE), (1, true, true));
    // the first agent file is written before the second, read-only, refuses: it stays written
    put(&d, "dev/g.md", "the rule\n");
    put(&d, ".claude/agents/d.md", "read only\n");
    let ro = d.join(".claude/agents/d.md");
    let mut perms = std::fs::metadata(&ro).unwrap().permissions();
    perms.set_readonly(true);
    std::fs::set_permissions(&ro, perms).unwrap();
    let two: SyncTable<'static> = &[
        (".claude/agents/c.md", &["dev/g.md"]),
        (".claude/agents/d.md", &["dev/g.md"]),
    ];
    assert_eq!(raised(&d, &[], two), (1, true, true));
    let first = std::fs::read_to_string(d.join(".claude/agents/c.md")).unwrap();
    assert!(first.contains(HEAD));
}

#[test]
fn a_bad_command_line_is_argparses_exit_two() {
    let got = cli(&args(&["extra"]), Path::new("."), ONE);
    assert_eq!((got.code, got.stdout.as_str()), (2, ""));
    assert!(got.stderr.contains("usage: l7r-gate reviews agent-sync"));
    assert_eq!(super::super::cli(&args(&["agent-sync", "--bogus"])).code, 2);
}
