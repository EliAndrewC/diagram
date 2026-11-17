//! `memo_check.py`'s port (feature 449 T148): the arguments as its `parse` read them, the inputs as `record_cache.content_ids` read them,
//! a pass kept and replayed while its key holds and a refusal never kept, the command run as `memo_check.run` ran it, and a run recorded
//! in the usage log; the Python's answers on the same calls are the differential's (`make diff-run`, T148's cases).

use std::collections::BTreeSet;
use std::path::Path;
use std::process::Command;

use super::{
    cli, code_key, command, content_ids, general, imported_files, off, off_of, parse, preset, Call,
    Memo, RAISED, USAGE,
};
use crate::fixture::{put, tree};
use l7r_gate_core::checks::scratch;

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

fn git(dir: &Path, a: &[&str]) {
    let done = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(["-c", "user.email=t@t", "-c", "user.name=t"])
        .args(a)
        .output()
        .unwrap();
    assert!(done.status.success());
}

fn repo() -> l7r_gate_core::checks::TempDir {
    let d = scratch("memo-repo");
    git(&d, &["init", "-q"]);
    d
}

fn usage_rows(dir: &Path) -> Vec<String> {
    std::fs::read_to_string(dir.join(".git/tool-usage.jsonl"))
        .unwrap_or_default()
        .lines()
        .map(|l| {
            let v: serde_json::Value = serde_json::from_str(l).unwrap();
            format!(
                "{} {}",
                v["tool"].as_str().unwrap(),
                v["outcome"].as_str().unwrap()
            )
        })
        .collect()
}

#[test]
fn the_arguments_are_read_as_memo_check_read_them() {
    assert_eq!(
        parse(&args(&["record"])),
        Some(Call::Preset("record".into()))
    );
    assert_eq!(
        parse(&args(&["glossary"])),
        Some(Call::Preset("glossary".into()))
    );
    let general = parse(&args(&[
        "n", "--inputs", "a", "b", "--code", "c.py", "--facts", "m:X", "--inputs", "d", "--", "x",
        "--", "y",
    ]));
    assert_eq!(
        general,
        Some(Call::General {
            name: "n".into(),
            inputs: args(&["a", "b", "d"]),
            code: args(&["c.py"]),
            facts: Some("m:X".into()),
            command: args(&["x", "--", "y"])
        })
    );
    for bad in [
        &[][..],
        &["bogus"],
        &["record", "x"],
        &["--", "x"],
        &["--inputs", "a", "--", "x"],
        &["n", "a", "--inputs", "b", "--", "x"],
        &["n", "--inputs", "--", "x"],
        &["n", "--inputs", "a", "--"],
        &["n", "--inputs", "a", "--facts", "m:a", "m:b", "--", "x"],
    ] {
        assert_eq!(parse(&args(bad)), None);
    }
    assert!(
        off_of(Some("1"))
            && off_of(Some("yes"))
            && !off_of(Some("0"))
            && !off_of(Some(""))
            && !off_of(None)
    );
    assert!(!off());
}

#[test]
fn the_inputs_are_read_as_content_ids_read_them() {
    let d = repo();
    put(&d, "in/a.txt", "a");
    put(&d, "in/b.txt", "b");
    put(&d, "in/c.txt", "c");
    put(&d, "out/x.txt", "x");
    put(&d, ".gitignore", "in/ignored.txt\n");
    git(&d, &["add", "-A"]);
    put(&d, "in/b.txt", "changed");
    std::fs::remove_file(d.join("in/c.txt")).unwrap();
    put(&d, "in/new.txt", "new");
    put(&d, "in/ignored.txt", "ignored");
    let ids = content_ids(&d, &["in".to_owned()]);
    let blob = l7r_gate_core::codeid::git_blob_id;
    assert_eq!(
        ids.into_iter().collect::<Vec<_>>(),
        [
            ("in/a.txt".to_owned(), blob(b"a")),
            ("in/b.txt".to_owned(), blob(b"changed")),
            ("in/c.txt".to_owned(), "gone".to_owned()),
            ("in/new.txt".to_owned(), blob(b"new")),
        ]
    );
    assert!(content_ids(&d.join("no-repo"), &[]).is_empty());
}

#[test]
fn the_code_key_follows_the_project_modules_a_file_imports() {
    let d = repo();
    put(&d, "scripts/gates/tool.py", "import os, helper as h\nfrom pkg.mod import (a,\n    b as c)\nfrom . import rel\nfrom x import \\\n  y\n# import commented\n");
    put(&d, "scripts/gates/helper.py", "from pkg import mod\n");
    put(&d, "scripts/record/flat.py", "x = 1\n");
    put(&d, "pkg/__init__.py", "");
    put(&d, "pkg/mod.py", "import flat\n");
    put(&d, "pkg/mod/b.py", "");
    let mut seen = BTreeSet::new();
    imported_files(&d.join("scripts/gates/tool.py"), &d, &mut seen);
    let names: Vec<String> = seen
        .iter()
        .map(|p| {
            p.strip_prefix(crate::resolve(&d))
                .unwrap()
                .display()
                .to_string()
        })
        .collect();
    // the set `record_cache.imported_files` gives on the same tree (HEAD's Python, observed 2026-11-17)
    assert_eq!(
        names,
        [
            "pkg/__init__.py",
            "pkg/mod/b.py",
            "pkg/mod.py",
            "scripts/gates/helper.py",
            "scripts/gates/tool.py"
        ]
    );
    let files = [d.join("scripts/gates/tool.py"), d.join("no-such.py")];
    let before = code_key(&d, "p", &files);
    put(&d, "pkg/mod.py", "import flat  # changed\n");
    assert_ne!(code_key(&d, "p", &files), before);
}

#[test]
fn a_pass_is_kept_and_replayed_and_a_refusal_is_not() {
    let d = repo();
    put(&d, "in/a.txt", "a");
    let count = d.join("count");
    let argv = args(&["sh", "-c", "echo run >> ../count; echo out; echo err >&2"]);
    put(&d, "work/.keep", "");
    let run = |m: &Memo| m.run(|| command(&d.join("work"), &argv)).unwrap();
    let memo = || Memo::new(&d, "n", &["in".to_owned()], "code", &argv, false);
    let first = run(&memo());
    assert_eq!(
        (first.stdout.as_str(), first.stderr.as_str(), first.code),
        ("out\n", "err\n", 0)
    );
    let kept = std::fs::read_to_string(d.join(".git/l7r-cache/memo-n.json")).unwrap();
    assert!(
        kept.starts_with("{\"key\": \"")
            && kept.ends_with("\", \"out\": \"out\\n\", \"err\": \"err\\n\"}")
    );
    assert_eq!(run(&memo()), first);
    assert_eq!(std::fs::read_to_string(&count).unwrap(), "run\n");
    put(&d, "in/a.txt", "moved");
    run(&memo());
    assert_eq!(std::fs::read_to_string(&count).unwrap(), "run\nrun\n");
    run(&Memo::new(&d, "n", &["in".to_owned()], "code", &argv, true));
    assert_eq!(std::fs::read_to_string(&count).unwrap(), "run\nrun\nrun\n");
    let failing = args(&["sh", "-c", "echo no; exit 3"]);
    let refusing = Memo::new(&d, "f", &["in".to_owned()], "code", &failing, false);
    assert_eq!(refusing.run(|| command(&d, &failing)).unwrap().code, 3);
    assert!(!d.join(".git/l7r-cache/memo-f.json").exists());
    put(&d, ".git/l7r-cache/memo-f.json", "not json");
    assert_eq!(refusing.hit(), None);
    std::fs::remove_file(d.join(".git/l7r-cache/memo-f.json")).unwrap();
    std::fs::create_dir_all(d.join(".git/l7r-cache/memo-f.json")).unwrap();
    refusing.keep("o", "e");
    assert!(d.join(".git/l7r-cache/memo-f.json").is_dir());
}

#[test]
fn a_command_runs_as_memo_check_ran_it() {
    let d = scratch("memo-command");
    let r = command(
        &d,
        &args(&["sh", "-c", "printf 'a\\r\\nb\\rc'; printf 'e\\r\\n' >&2"]),
    )
    .unwrap();
    assert_eq!((r.stdout.as_str(), r.stderr.as_str()), ("a\nb\nc", "e\n"));
    assert_eq!(
        command(&d, &args(&["sh", "-c", "kill -9 $$"]))
            .unwrap()
            .code,
        -9
    );
    assert_eq!(
        command(&d, &args(&["sh", "-c", "printf '\\377'"]))
            .unwrap_err()
            .kind,
        "UnicodeDecodeError"
    );
    assert_eq!(
        command(&d, &args(&["/no/such/program"])).unwrap_err().kind,
        "FileNotFoundError"
    );
    put(&d, "ok_mod.py", "print('a\\r')\n");
    let r = command(&d, &args(&["python3", "-m", "ok_mod"])).unwrap();
    assert_eq!((r.stdout.as_str(), r.code), ("a\r\n", 0));
    // the interpreter by its path, as `sys.executable` names it: read as text as written too
    let r = command(&d, &[super::python(), "-m".to_owned(), "ok_mod".to_owned()]).unwrap();
    assert_eq!(r.stdout, "a\r\n");
    put(&d, "bad_mod.py", "print('lost')\nraise KeyError('k')\n");
    let e = command(&d, &args(&["python3", "-m", "bad_mod"])).unwrap_err();
    assert!(e.kind == RAISED && e.message.ends_with("KeyError: 'k'\n"));
    assert_eq!(crate::tools::reply(Err(e.clone())).stderr, e.message);
    put(&d, "exit_mod.py", "import sys\nsys.exit(4)\n");
    assert_eq!(
        command(&d, &args(&["python3", "-m", "exit_mod"]))
            .unwrap()
            .code,
        4
    );
}

#[test]
fn every_call_is_recorded_and_the_record_pass_is_kept() {
    let t = tree();
    git(&t, &["init", "-q"]);
    git(&t, &["add", "-A"]);
    let r = cli(&[], &t, "p").unwrap();
    assert_eq!((r.code, r.stderr.as_str()), (2, USAGE));
    let pass = cli(&args(&["record"]), &t, "p").unwrap();
    assert_eq!(pass.stdout, "record: builds cleanly (20 page(s))\n");
    // the kept pass marked, to tell a replay from a run
    let path = t.join(".git/l7r-cache/memo-record.json");
    let kept = std::fs::read_to_string(&path)
        .unwrap()
        .replace("record: builds cleanly", "KEPT");
    std::fs::write(&path, kept).unwrap();
    assert_eq!(
        preset("record", &t, "p").unwrap().stdout,
        "KEPT (20 page(s))\n"
    );
    assert_eq!(
        cli(&args(&["glossary"]), &t, "p").unwrap().stdout,
        "glossary: in sync (2 terms)\n"
    );
    assert!(t.join(".git/l7r-cache/memo-glossary.json").is_file());
    let general = args(&[
        "n", "--inputs", "research", "--code", "x.py", "--", "sh", "-c", "exit 5",
    ]);
    assert_eq!(cli(&general, &t, "p").unwrap().code, 5);
    std::fs::write(t.join("research/source-tags.json"), [0xff]).unwrap();
    assert_eq!(
        cli(&args(&["record"]), &t, "p").unwrap_err().kind,
        "UnicodeDecodeError"
    );
    assert_eq!(
        usage_rows(&t),
        [
            "memo_check refused",
            "memo_check passed",
            "memo_check passed",
            "memo_check refused"
        ]
    );
}

#[test]
fn a_facts_module_is_imported_before_the_run_and_its_output_not_kept() {
    let d = repo();
    put(&d, "loud.py", "print('imported')\n");
    put(&d, "ok_mod.py", "print('ran')\n");
    let argv = args(&["python3", "-m", "ok_mod"]);
    let memo = Memo::new(&d, "n", &["x".to_owned()], "c", &argv, false);
    let first = general(&d, &memo, &argv, Some("loud:MEMO")).unwrap();
    assert_eq!(first.stdout, "imported\nran\n");
    assert_eq!(
        general(&d, &memo, &argv, Some("loud:MEMO")).unwrap().stdout,
        "ran\n"
    );
    let e = general(
        &d,
        &Memo::new(&d, "m", &[], "c", &argv, true),
        &argv,
        Some("no_such_mod"),
    )
    .unwrap_err();
    assert!(e.kind == RAISED && e.message.contains("ModuleNotFoundError"));
    // a command Python ran as a child is handed no memo: the facts flag is read and nothing imported
    let plain = args(&["sh", "-c", "echo plain"]);
    assert_eq!(
        general(
            &d,
            &Memo::new(&d, "p", &[], "c", &plain, true),
            &plain,
            Some("no_such_mod")
        )
        .unwrap()
        .stdout,
        "plain\n"
    );
}
