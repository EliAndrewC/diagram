//! The stamp's rules on fixture repositories; every area's key against the Python it replaced is `m:t063-slice2`.

use std::path::{Path, PathBuf};
use std::process::Command;

use super::{
    answer, area_files, area_named, cli, coverage_sources, exclusions, hash_files, in_raw_area,
    listing, matches, record, salt, selftest, GATE_RECIPE,
};

fn repo(tag: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("l7r-gate-stamp-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
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

/// A `python` that names every file it is asked about by a hash of its bytes.
fn fake_python(dir: &Path) -> String {
    let path = dir.join("fake-python");
    std::fs::write(
        &path,
        "#!/bin/bash\nshift; shift; for f in \"$@\"; do sha1sum \"$f\" | cut -d' ' -f1; done\n",
    )
    .unwrap();
    Command::new("chmod").arg("+x").arg(&path).status().unwrap();
    path.to_string_lossy().into_owned()
}

fn call(dir: &Path, python: &str, args: &[&str]) -> crate::Reply {
    let owned: Vec<String> = args.iter().map(|s| (*s).to_owned()).collect();
    cli(
        &owned,
        Some(dir),
        python,
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
            "buildspec/",
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

#[test]
fn the_hash_is_salted_with_the_gate_s_standard_and_keeps_a_gone_file() {
    let dir = repo("hash");
    let gone = [dir.join("gone.txt")];
    let hash = hash_files(&gone, &dir, false, "salt", "python3").unwrap();
    let text = format!("{GATE_RECIPE}\0salt\0{}\0<missing>\0", gone[0].display());
    assert_eq!(hash, l7r_guard::shared::sha256::hex(text.as_bytes()));
    put(&dir, "a.txt", "1\n");
    let file = [dir.join("a.txt")];
    let semantic = hash_files(&file, &dir, false, "", "python3").unwrap();
    let raw = hash_files(&file, &dir, true, "", "python3").unwrap();
    assert_ne!(semantic, raw, "a blob id is not the sha of the bytes");
}

#[test]
fn only_the_browser_area_has_a_salt() {
    let dir = repo("salt");
    let python = dir.join("salty");
    std::fs::write(
        &python,
        "#!/bin/bash\nprintf 'playwright=1;chromium=none'\n",
    )
    .unwrap();
    Command::new("chmod")
        .arg("+x")
        .arg(&python)
        .status()
        .unwrap();
    let python = python.to_string_lossy().into_owned();
    assert_eq!(
        salt(area_named("browser").unwrap(), &python),
        "playwright=1;chromium=none"
    );
    assert_eq!(salt(area_named("page").unwrap(), &python), "");
    let real = salt(area_named("browser").unwrap(), "python3");
    assert!(real == "absent" || (real.starts_with("playwright=") && real.contains(";chromium=")),);
    assert_eq!(
        salt(area_named("browser").unwrap(), "/no/such/python"),
        "absent"
    );
}

#[test]
fn a_stamp_is_fresh_until_its_code_changes_and_says_so_at_the_push() {
    let dir = repo("flow");
    let python = fake_python(&dir);
    put(&dir, ".gitignore", "fake-python\n");
    put(&dir, "a.py", "x = 1\n");
    commit(&dir);
    git(&dir, &["branch", "base"]);
    assert_eq!(call(&dir, &python, &["--fresh", "diagram"]).code, 1,);
    put(&dir, "a.py", "x = 2\n");
    commit(&dir);
    let refused = call(&dir, &python, &["--check", "base"]);
    assert_eq!(refused.code, 1);
    assert!(
        refused
            .stderr
            .contains("diagram: no green gate has been recorded at all (make done stamps it)")
            && refused.stderr.contains("GATE_STAMP_OK")
    );
    assert_eq!(call(&dir, &python, &["--write", "diagram"]).code, 0);
    assert_eq!(call(&dir, &python, &["--fresh", "diagram"]).code, 0);
    assert_eq!(call(&dir, &python, &["--check", "base"]).code, 0);
    put(&dir, "a.py", "x = 3\n");
    assert_eq!(call(&dir, &python, &["--fresh", "diagram"]).code, 1);
    assert!(call(&dir, &python, &["--check", "base"])
        .stderr
        .contains("diagram: the last green gate ran against DIFFERENT code"));
    let key = call(&dir, &python, &["--key", "diagram"]);
    assert_eq!((key.code, key.stdout.trim().len()), (0, 64));
    assert_eq!(call(&dir, &python, &["--list", "diagram"]).stdout, "a.py\n");
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
    let python = fake_python(&dir);
    put(&dir, ".gitignore", "fake-python\n");
    put(&dir, "f.txt", "1\n");
    commit(&dir);
    git(&dir, &["branch", "base"]);
    put(&dir, "scripts/x.sh", "true\n");
    put(&dir, "l7r/diagram/interactive/assets/page.js", "1\n");
    commit(&dir);
    let refused = call(&dir, &python, &["--check", "base"]);
    assert!(
        refused.stderr.contains("make hooks-test stamps it")
            && refused.stderr.contains("make page-check stamps it")
    );
    assert!(!refused.stderr.contains("browser:"));
    assert_eq!(
        call(&dir, &python, &["--raw-match"]).stdout,
        "l7r/diagram/interactive/assets/page.js
"
    );
}

#[test]
fn what_git_cannot_answer_refuses_rather_than_passes() {
    let dir = repo("broken");
    let refused = call(&dir, "python3", &["--check", "no-such-base"]);
    assert_eq!(refused.code, 1);
    assert!(refused.stderr.contains("git diff"));
    let not_a_repo =
        std::env::temp_dir().join(format!("l7r-gate-stamp-none-{}", std::process::id()));
    std::fs::create_dir_all(&not_a_repo).unwrap();
    for args in [
        ["--key", "diagram"],
        ["--list", "diagram"],
        ["--write", "diagram"],
    ] {
        assert_eq!(call(&not_a_repo, "python3", &args).code, 1, "{args:?}");
    }
    record(&not_a_repo, "passed");
}

#[test]
fn a_byte_hashed_area_is_a_pattern_and_keeps_the_old_answer_on_the_shared_root() {
    let dir = repo("raw");
    let bad = answer(
        &["--raw-match".to_owned()],
        Some(&dir),
        "python3",
        &mut &[0xff_u8][..],
    );
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

#[test]
fn a_python_that_cannot_answer_is_a_refusal() {
    let dir = repo("py");
    put(&dir, "a.py", "x = 1\n");
    commit(&dir);
    git(&dir, &["branch", "base"]);
    put(&dir, "a.py", "x = 2\n");
    commit(&dir);
    for args in [
        ["--key", "diagram"],
        ["--write", "diagram"],
        ["--check", "base"],
    ] {
        assert_eq!(call(&dir, "/no/such/python", &args).code, 1, "{args:?}");
    }
    assert_eq!(
        call(&dir, "/no/such/python", &["--fresh", "diagram"]).code,
        1
    );
}

#[test]
fn a_stamp_that_cannot_be_written_is_a_failure() {
    let dir = repo("unwritable");
    let python = fake_python(&dir);
    std::fs::create_dir_all(dir.join(".git/gate-green-hooks")).unwrap();
    assert!(call(&dir, &python, &["--write", "hooks"])
        .stderr
        .contains("gate-green-hooks"));
}

#[test]
fn outside_a_repository_it_stands_aside_and_nothing_is_fresh() {
    let owned = |a: &[&str]| a.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    assert_eq!(
        cli(
            &owned(&["--write", "diagram"]),
            None,
            "python3",
            &mut &b""[..]
        )
        .code,
        0
    );
    assert_eq!(
        cli(&owned(&["--check", "x"]), None, "python3", &mut &b""[..]).code,
        0
    );
    assert_eq!(
        cli(
            &owned(&["--fresh", "diagram"]),
            None,
            "python3",
            &mut &b""[..]
        )
        .code,
        1
    );
    assert_eq!(cli(&owned(&[]), None, "python3", &mut &b""[..]).code, 0);
    assert_eq!(
        answer(
            &owned(&["--nonsense"]),
            Some(Path::new(".")),
            "python3",
            &mut &b""[..]
        )
        .code,
        2
    );
    assert_eq!(
        answer(
            &owned(&["--write", "no-area"]),
            Some(Path::new(".")),
            "python3",
            &mut &b""[..]
        )
        .code,
        2
    );
}

/// A repository that can answer for Python itself: the real `codeid.py` and the module it records through.
fn with_codeid(tag: &str) -> PathBuf {
    let dir = repo(tag);
    let real = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../scripts");
    for rel in ["gates/codeid.py", "hooks/lib/usage_log.py"] {
        let to = dir.join("scripts").join(rel);
        std::fs::create_dir_all(to.parent().unwrap()).unwrap();
        std::fs::copy(real.join(rel), to).unwrap();
    }
    dir
}

#[test]
fn the_self_test_passes_on_the_real_id_and_fails_on_a_broken_one() {
    assert_eq!(selftest(&with_codeid("self-real"), "python3"), Ok(()));
    let broken = with_codeid("self-broken");
    let constant = broken.join("constant");
    std::fs::write(
        &constant,
        "#!/bin/bash\nshift; shift; for f in \"$@\"; do echo same; done\n",
    )
    .unwrap();
    Command::new("chmod")
        .arg("+x")
        .arg(&constant)
        .status()
        .unwrap();
    assert!(selftest(&broken, &constant.to_string_lossy())
        .unwrap_err()
        .contains("changed .py"));
    let dead = with_codeid("self-dead");
    assert!(answer(
        &["--selftest".to_owned()],
        Some(&dead),
        "/no/such/python",
        &mut &b""[..]
    )
    .stderr
    .contains("selftest"));
    assert_eq!(
        answer(
            &["--selftest".to_owned()],
            Some(&with_codeid("self-ok")),
            "python3",
            &mut &b""[..]
        )
        .code,
        0
    );
}
