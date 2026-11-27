//! The stamp's rules on fixture repositories; every area's key against the Python it replaced is `m:t063-slice2`.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    answer, area_files, area_named, cli, coverage_sources, exclusions, hash_files, in_raw_area,
    listing, matches, record, salt, selftest, selftest_in, selftest_reply, Rule, GATE_RECIPE,
};

fn repo(tag: &str) -> l7r_shared::tempdir::TempDir {
    let dir = l7r_shared::tempdir::TempDir::new(&format!("gate-stamp-{tag}"));
    git(&dir, &["init", "-q", "-b", "main"]);
    git(&dir, &["config", "user.email", "t@t"]);
    git(&dir, &["config", "user.name", "t"]);
    dir
}

fn git(dir: &Path, args: &[&str]) {
    assert!(Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap()
        .status
        .success());
}

fn put(dir: &Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn commit(dir: &Path) {
    git(dir, &["add", "-A"]);
    git(dir, &["commit", "-qm", "c"]);
}

fn call(dir: &Path, args: &[&str]) -> crate::Reply {
    let owned: Vec<String> = args.iter().map(|s| (*s).to_owned()).collect();
    cli(
        &owned,
        Some(dir),
        &mut "l7r/diagram/interactive/assets/page.js
l7r/diagram/ci/delta.py
"
        .as_bytes(),
    )
}

#[test]
fn a_star_crosses_a_slash_and_the_rest_is_literal() {
    assert!(matches("a/b/c.py", "*.py") && matches("c.py", "*.py"));
    assert!(matches("rust/x/Cargo.toml", "rust/*Cargo.toml"));
    assert!(matches("exact", "exact") && !matches("other", "exact"));
    assert!(!matches("x.py", "rust/*.py"));
    assert!(matches("a-b-c", "a*b*c") && !matches("a-c", "a*b*c"));
}

#[test]
fn the_exclusions_are_derived_from_the_coverage_config_and_fail_closed() {
    let dir = repo("config");
    assert_eq!(coverage_sources(&dir), ["l7r/"],);
    let diagram = area_named("diagram").unwrap();
    assert!(!exclusions(diagram, &dir).contains(&"l7r/diagram/ci/"),);
    assert_eq!(
        exclusions(diagram, &dir),
        [
            "tests/",
            "scripts/",
            "specs/",
            ".claude/",
            ".specify/",
            ".clones/",
            "docs/"
        ]
    );
    put(&dir, "pyproject.toml", "[tool.x]\nsource = [\"no\"]\n\n[tool.coverage.run]\nbranch = true\nsource = [\"pool/\", 'other']\n\n[tool.y]\nz = 1\n");
    assert_eq!(coverage_sources(&dir), ["pool/", "other/"]);
    assert!(exclusions(diagram, &dir).contains(&"l7r/diagram/ci/"),);
    assert!(exclusions(area_named("browser").unwrap(), &dir).is_empty(),);
    put(&dir, "pyproject.toml", "[tool.coverage.run]\nsource = []\n");
    assert_eq!(coverage_sources(&dir), ["l7r/"]);
}

#[test]
fn an_area_holds_tracked_and_new_files_and_not_its_exclusions_or_what_is_ignored() {
    let dir = repo("area");
    put(&dir, ".gitignore", "ignored.py\n");
    put(&dir, "a.py", "x = 1\n");
    put(&dir, "tests/t.py", "x = 1\n");
    put(&dir, "bett\u{14d}.py", "x = 1\n");
    put(&dir, "ignored.py", "x = 1\n");
    put(&dir, "rust/a/b.rs", "fn f() {}\n");
    commit(&dir);
    put(&dir, "new.py", "x = 1\n");
    let files = area_files(&dir, area_named("diagram").unwrap()).unwrap();
    assert_eq!(
        listing(&files, &dir),
        "a.py\nbett\u{14d}.py\nnew.py\nrust/a/b.rs\n"
    );
    assert_eq!(listing(&[PathBuf::from("/elsewhere/x")], &dir), "",);
}

/// Every engine path (`delta::is_engine`, the one list) is in the diagram area, so a change the push routes GATED owes the `make done`
/// that stamps it, and `make land` runs it (feature 449 T224: a pool-only `.json`, `.svg` or `.notes.md` change passed the stamp, so
/// the landing skipped `make done` and the push refused it on `merged-engine-green`).
#[test]
fn every_engine_path_is_in_the_diagram_area() {
    let dir = repo("engine-parity");
    let diagram = area_named("diagram").unwrap();
    let excluded = exclusions(diagram, &dir);
    // each engine path outside the area's patterns (none may be)
    let outside: Vec<String> = crate::delta::ENGINE_DIRS
        .iter()
        .flat_map(|(prefix, ends)| {
            ends.iter()
                .map(move |end| format!("{prefix}tier/map/map{end}"))
        })
        .filter(|path| {
            !(crate::delta::is_engine(path)
                && !excluded.iter().any(|e| path.starts_with(e))
                && diagram.patterns.iter().any(|p| matches(path, p)))
        })
        .collect();
    assert_eq!(outside, Vec::<String>::new());
}

#[test]
fn a_pool_only_change_owes_make_done_at_the_push() {
    let dir = repo("pool-only");
    put(&dir, ".gitignore", "*.png\n");
    put(&dir, "pool/t/m/m.compound.json", "{}\n");
    commit(&dir);
    git(&dir, &["branch", "base"]);
    for (rel, text) in [
        ("pool/t/m/m.compound.json", "{\"a\": 1}\n"),
        ("pool/t/m/m.svg", "<svg/>\n"),
        ("pool/t/m/m.notes.md", "notes\n"),
        ("legacy-hand-authored-pool/x/x.json", "{}\n"),
    ] {
        put(&dir, rel, text);
    }
    put(&dir, "pool/t/m/m.png", "ignored render\n");
    commit(&dir);
    let refused = call(&dir, &["--check", "base"]);
    assert!(
        refused
            .stderr
            .contains("diagram: no green gate has been recorded at all (make done stamps it)"),
        "{}",
        refused.stderr
    );
    assert_eq!(
        call(&dir, &["--list", "diagram"]).stdout,
        "legacy-hand-authored-pool/x/x.json\npool/t/m/m.compound.json\npool/t/m/m.notes.md\npool/t/m/m.svg\n"
    );
}

#[test]
fn the_hooks_area_holds_the_makefile_the_suites_drive() {
    let dir = repo("hooks-make");
    put(&dir, "Makefile", "land:\n");
    put(&dir, "scripts/a.sh", "echo\n");
    put(&dir, "rust/Makefile.rs", "fn f() {}\n");
    commit(&dir);
    let files = area_files(&dir, area_named("hooks").unwrap()).unwrap();
    assert_eq!(listing(&files, &dir), "Makefile\nscripts/a.sh\n");
}

#[test]
fn the_hash_is_salted_with_the_gate_s_standard_and_keeps_a_gone_file() {
    let dir = repo("hash");
    let gone = [dir.join("gone.txt")];
    let hash = hash_files(&gone, &dir, false, "salt");
    let text = format!("{GATE_RECIPE}\0salt\0{}\0<missing>\0", gone[0].display());
    assert_eq!(hash, l7r_shared::sha256::hex(text.as_bytes()));
    put(&dir, "a.txt", "1\n");
    let file = [dir.join("a.txt")];
    let semantic = hash_files(&file, &dir, false, "");
    let raw = hash_files(&file, &dir, true, "");
    assert_ne!(semantic, raw, "a blob id is not the sha of the bytes");
}

#[test]
fn only_the_browser_area_has_a_salt() {
    // feature 449 T146: the browser area's salt is the Chromium the pin names, not the installed Playwright
    let dir = repo("salt");
    assert_eq!(salt(area_named("browser").unwrap(), &dir), "absent");
    put(
        &dir,
        "scripts/container/chromium.pin",
        "# the pin\nCHROMIUM_VERSION=151.0.7922.34\nCHROMIUM_SHA256=x\n",
    );
    assert_eq!(
        salt(area_named("browser").unwrap(), &dir),
        "chromium=151.0.7922.34"
    );
    assert_eq!(salt(area_named("page").unwrap(), &dir), "");
    put(
        &dir,
        "scripts/container/chromium.pin",
        "# no version line\n",
    );
    assert_eq!(salt(area_named("browser").unwrap(), &dir), "absent");
}

#[test]
fn a_stamp_is_fresh_until_its_code_changes_and_says_so_at_the_push() {
    let dir = repo("flow");
    put(&dir, "a.py", "x = 1\n");
    commit(&dir);
    git(&dir, &["branch", "base"]);
    assert_eq!(call(&dir, &["--fresh", "diagram"]).code, 1,);
    put(&dir, "a.py", "x = 2\n");
    commit(&dir);
    let refused = call(&dir, &["--check", "base"]);
    assert_eq!(refused.code, 1);
    assert!(
        refused
            .stderr
            .contains("diagram: no green gate has been recorded at all (make done stamps it)")
            && refused.stderr.contains("GATE_STAMP_OK")
    );
    assert_eq!(call(&dir, &["--write", "diagram"]).code, 0);
    assert_eq!(call(&dir, &["--fresh", "diagram"]).code, 0);
    assert_eq!(call(&dir, &["--check", "base"]).code, 0);
    put(&dir, "a.py", "x = 3\n");
    assert_eq!(call(&dir, &["--fresh", "diagram"]).code, 1);
    assert!(call(&dir, &["--check", "base"])
        .stderr
        .contains("diagram: the last green gate ran against DIFFERENT code"));
    let key = call(&dir, &["--key", "diagram"]);
    assert_eq!((key.code, key.stdout.trim().len()), (0, 64));
    assert_eq!(call(&dir, &["--list", "diagram"]).stdout, "a.py\n");
    let usage: String = std::fs::read_to_string(dir.join(".git/tool-usage.jsonl")).unwrap();
    assert!(
        usage.contains("\"tool\": \"gate-stamp\", \"kind\": \"check\", \"outcome\": \"refused\"")
            && usage.contains("\"outcome\": \"passed\"")
    );
    assert_eq!(usage.lines().count(), 7,);
}

#[test]
fn each_area_names_its_own_gate_and_a_skip_key_owes_none() {
    let dir = repo("areas");
    put(&dir, "f.txt", "1\n");
    commit(&dir);
    git(&dir, &["branch", "base"]);
    put(&dir, "scripts/x.sh", "true\n");
    put(&dir, "l7r/diagram/interactive/assets/page.js", "1\n");
    commit(&dir);
    let refused = call(&dir, &["--check", "base"]);
    assert!(
        refused.stderr.contains("make hooks-test stamps it")
            && refused.stderr.contains("make page-check stamps it")
    );
    assert!(!refused.stderr.contains("browser:"));
    assert_eq!(
        call(&dir, &["--raw-match"]).stdout,
        "l7r/diagram/interactive/assets/page.js
"
    );
}

#[test]
fn what_git_cannot_answer_refuses_rather_than_passes() {
    let dir = repo("broken");
    let refused = call(&dir, &["--check", "no-such-base"]);
    assert_eq!(refused.code, 1);
    assert!(refused.stderr.contains("git diff"));
    let not_a_repo = l7r_shared::tempdir::TempDir::new("gate-stamp-none");
    std::fs::create_dir_all(&not_a_repo).unwrap();
    for args in [
        ["--key", "diagram"],
        ["--list", "diagram"],
        ["--write", "diagram"],
    ] {
        assert_eq!(call(&not_a_repo, &args).code, 1, "{args:?}");
    }
    record(&not_a_repo, "passed");
}

#[test]
fn a_byte_hashed_area_is_a_pattern_and_keeps_the_old_answer_on_the_shared_root() {
    let dir = repo("raw");
    let bad = answer(&["--raw-match".to_owned()], Some(&dir), &mut &[0xff_u8][..]);
    assert_eq!(bad.code, 1);
    for path in [
        "l7r/diagram/interactive/classes/not-on-disk.py",
        "l7r/diagram/interactive/assets/x.css",
        "l7r/diagram/interactive/page.py",
        concat!("research", "/anything.html"),
    ] {
        assert!(in_raw_area(&dir, path), "{path}");
    }
    for path in [
        "l7r/diagram/ci/delta.py",
        "docs/x.md",
        "tests/full/interactive/page_browser/test_x.py",
        "l7r/diagram/interactive/classes/a.txt",
    ] {
        assert!(!in_raw_area(&dir, path), "{path}");
    }
}

/// The keys are taken in process since feature 449 T247, so no `python3` is asked: a `.py` file is keyed by its blob id.
#[test]
fn a_python_file_is_keyed_by_its_bytes() {
    let dir = repo("py");
    put(&dir, "a.py", "\"\"\"doc\"\"\"\n");
    let before = call(&dir, &["--key", "diagram"]).stdout;
    put(&dir, "a.py", "\"\"\"words\"\"\"\n");
    let after = call(&dir, &["--key", "diagram"]).stdout;
    assert_ne!(before, after);
}

/// Feature 451 T304: two trees of different content gating in turn keep each other's green keys - the stamp held one, so each
/// tree's gate replaced the other's and the other's next `make done` reran hooks-test; a key past the bound is gated again, and a stamp
/// of the form before T304 (one key, no newline) is read as one.
#[test]
fn trees_of_different_content_keep_each_others_green_keys() {
    let dir = repo("two-trees");
    put(&dir, "a.py", "x = 1\n");
    commit(&dir);
    git(&dir, &["branch", "base"]);
    put(&dir, "a.py", "x = 2\n");
    commit(&dir);
    let stamp = dir.join(".git/gate-green-diagram");
    let first = call(&dir, &["--key", "diagram"]).stdout.trim().to_owned();
    std::fs::write(&stamp, &first).unwrap();
    assert_eq!(call(&dir, &["--fresh", "diagram"]).code, 0);
    put(&dir, "a.py", "x = 3\n");
    assert_eq!(call(&dir, &["--write", "diagram"]).code, 0);
    put(&dir, "a.py", "x = 2\n");
    assert_eq!(call(&dir, &["--fresh", "diagram"]).code, 0);
    assert_eq!(call(&dir, &["--check", "base"]).code, 0);
    assert_eq!(call(&dir, &["--write", "diagram"]).code, 0);
    let kept = std::fs::read_to_string(&stamp).unwrap();
    assert_eq!(
        (kept.lines().count(), kept.lines().next()),
        (2, Some(first.as_str()))
    );
    for n in 4..=9 {
        put(&dir, "a.py", &format!("x = {n}\n"));
        assert_eq!(call(&dir, &["--write", "diagram"]).code, 0);
    }
    assert_eq!(
        std::fs::read_to_string(&stamp).unwrap().lines().count(),
        super::STAMP_KEEP
    );
    put(&dir, "a.py", "x = 2\n");
    assert_eq!(call(&dir, &["--fresh", "diagram"]).code, 1);
    assert!(!std::fs::read_dir(dir.join(".git"))
        .unwrap()
        .flatten()
        .any(|e| e.file_name().to_string_lossy().ends_with(".tmp")));
}

#[test]
fn a_stamp_that_cannot_be_written_is_a_failure() {
    let dir = repo("unwritable");
    std::fs::create_dir_all(dir.join(".git/gate-green-hooks")).unwrap();
    assert!(call(&dir, &["--write", "hooks"])
        .stderr
        .contains("gate-green-hooks"));
}

#[test]
fn outside_a_repository_it_stands_aside_and_nothing_is_fresh() {
    let owned = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    assert_eq!(
        cli(&owned(&["--write", "diagram"]), None, &mut &b""[..]).code,
        0
    );
    assert_eq!(cli(&owned(&["--check", "x"]), None, &mut &b""[..]).code, 0);
    assert_eq!(
        cli(&owned(&["--fresh", "diagram"]), None, &mut &b""[..]).code,
        1
    );
    assert_eq!(cli(&owned(&[]), None, &mut &b""[..]).code, 0);
    assert_eq!(
        answer(&owned(&["--nonsense"]), Some(Path::new(".")), &mut &b""[..]).code,
        2
    );
    assert_eq!(
        answer(
            &owned(&["--write", "no-area"]),
            Some(Path::new(".")),
            &mut &b""[..]
        )
        .code,
        2
    );
}

/// FR-008's one end-to-end test (ask:449-T167-realtree): the stamp's self-test over the real id, passing on it and failing on a row
/// the id cannot satisfy (a code change said to keep the hash).
#[test]
fn the_self_test_passes_on_the_real_id_and_fails_on_a_wrong_row() {
    let dir = repo("self-real");
    assert_eq!(selftest(&dir), Ok(()));
    let scratch = dir.join("scratch");
    let rows = [
        ("a.rs", Some("const X: u8 = 1;\n"), Rule::Baseline, ""),
        ("a.rs", Some("const X: u8 = 2;\n"), Rule::Stays, "moved"),
    ];
    let failed = selftest_in(&scratch, &dir, &rows);
    assert_eq!(failed, Err("moved".to_owned()));
    let ok = answer(&["--selftest".to_owned()], Some(&dir), &mut &b""[..]);
    assert_eq!(ok.code, 0);
    let refused = selftest_reply(Err("why".to_owned()));
    assert_eq!(
        (refused.code, refused.stderr.as_str()),
        (1, "gate-stamp selftest: why\n")
    );
}
