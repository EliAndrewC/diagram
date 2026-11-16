//! The ledger's and the attempts log's commands (feature 449 T145; the T145 differential holds them to `sources.py` and `attempts.py`
//! on the real ledgers, these tests every branch on a scratch one).

use std::os::unix::fs::PermissionsExt as _;
use std::path::{Path, PathBuf};

use l7r_guard::shared::tempdir::TempDir;
use serde_json::json;

use super::{attempts_cli, cli, mark_filled, registry};

const LIST: &str = r#"{"domains": [{"domain": "bad.example", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

/// A mirror with a clone under `.clones/` holding a registry of two entries and the blocked list.
fn world(tag: &str) -> (TempDir, PathBuf, PathBuf) {
    let d = TempDir::new(tag);
    let root = d.join("m/.clones/c");
    let reg = root.join("research/sources/010-works-cited");
    std::fs::create_dir_all(&reg).unwrap();
    std::fs::create_dir_all(root.join(".git")).unwrap();
    std::fs::create_dir_all(d.join("m/.specify")).unwrap();
    std::fs::write(root.join("research/blocked-domains.json"), LIST).unwrap();
    std::fs::write(
        reg.join("0010-a-key.html"),
        "<p>(https://a.org/a)</p>\n<p>also https://b.org/b</p>",
    )
    .unwrap();
    std::fs::write(reg.join("0020-no-pointer.html"), "<p>none</p>").unwrap();
    std::fs::write(reg.join("x-skipped.html"), "<p>(https://c.org)</p>").unwrap();
    let home = d.join("m/.specify");
    (d, root, home)
}

fn a(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn ledger(home: &Path) -> String {
    std::fs::read_to_string(home.join("sources-consulted.jsonl")).unwrap_or_default()
}

#[test]
fn the_registry_is_marked_cited_once() {
    let (_d, root, home) = world("sources-registry");
    assert_eq!(
        registry(&root).unwrap(),
        vec![("a-key".to_owned(), "https://a.org/a".to_owned())]
    );
    assert_eq!(mark_filled(&root, &home).unwrap().len(), 1);
    assert!(mark_filled(&root, &home).unwrap().is_empty());
    let said = cli(&a(&["mark-filled"]), &root);
    assert_eq!(
        said.stdout,
        "sources-consulted: 0 filled registry entries marked cited\n"
    );
    std::fs::write(
        root.join("research/sources/010-works-cited/0030-grok.html"),
        "<p>(https://bad.example/x)</p>",
    )
    .unwrap();
    assert_eq!(cli(&a(&["mark-filled"]), &root).code, 1);
    std::fs::write(
        root.join("research/sources/010-works-cited/0040-bad.html"),
        [0xff],
    )
    .unwrap();
    assert!(registry(&root).is_err());
    std::fs::write(home.join("sources-consulted.jsonl"), "[1]\n").unwrap();
    assert!(mark_filled(&root, &home).is_err());
}

#[test]
fn an_outcome_is_recorded_on_the_ledger_and_the_log() {
    let (_d, root, home) = world("sources-outcome");
    let got = cli(
        &a(&[
            "outcome",
            "https://www.a.org/p/",
            "cited:a-key",
            "--question",
            "0012",
            "--sought",
            "the walls",
        ]),
        &root,
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.starts_with("source-outcome: recorded  "));
    assert!(got.stdout.contains("cited:a-key  q: 0012"));
    assert!(got
        .stderr
        .contains("archive: archiving the pages read failed (exit "));
    assert!(ledger(&home).contains("\"url\": \"a.org/p\""));
    let log = std::fs::read_to_string(root.join("research/source-attempts.jsonl")).unwrap();
    assert!(
        log.contains("\"sought\": \"the walls\"") && log.contains("\"route\": \"source-outcome\"")
    );
    let plain = cli(&a(&["outcome", "https://a.org/q", " pending "]), &root);
    assert_eq!((plain.code, plain.stderr.as_str()), (0, ""));
    let bad = cli(&a(&["outcome", "https://a.org/q", "found"]), &root);
    assert_eq!(bad.stderr, "source-outcome: OUTCOME='found' is not one of: cited:<registry key> | rejected:<why> | nothing-found | unreadable | pending\n");
    assert_eq!(bad.code, 2);
    assert_eq!(cli(&a(&["outcome", "x"]), &root).code, 2);
    assert_eq!(
        cli(&a(&["outcome", "x", "pending", "--nope"]), &root).code,
        2
    );
    assert_eq!(
        cli(&a(&["outcome", "https://bad.example/x", "pending"]), &root).code,
        1
    );
    std::fs::write(root.join("research/source-attempts.jsonl"), "[1]\n").unwrap();
    assert_eq!(
        cli(&a(&["outcome", "https://a.org/z", "pending"]), &root).code,
        1
    );
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(root.join(".specify/feature.json"), "[1]").unwrap();
    assert_eq!(
        cli(&a(&["outcome", "https://a.org/z", "pending"]), &root).code,
        1
    );
}

#[test]
fn the_ledger_is_looked_up_by_url_or_by_key() {
    let (_d, root, home) = world("sources-lookup");
    std::fs::write(
        home.join("sources-consulted.jsonl"),
        json!({"url": "a.org/a", "outcome": "pending", "utc": "2026-10-01T00:00:00+00:00"})
            .to_string()
            + "\n",
    )
    .unwrap();
    let url = cli(&a(&["lookup", "--url", "https://a.org/a/"]), &root);
    assert!(url.stdout.starts_with("sources-consulted: 2 line(s) for a.org/a (1 newly filled registry entry marked cited first)\n"));
    let key = cli(&a(&["lookup", "--key", "^a-"]), &root);
    assert!(key
        .stdout
        .starts_with("sources-consulted: 1 line(s) for keys matching '^a-'\n  a.org/a\n  "));
    assert_eq!(
        cli(&a(&["lookup"]), &root).stderr,
        "sources-consulted: URL=<u> or KEY=<regex> is required\n"
    );
    assert_eq!(cli(&a(&["lookup", "--key", "("]), &root).code, 1);
    assert_eq!(cli(&a(&["lookup", "--x"]), &root).code, 2);
    std::fs::write(
        home.join("sources-consulted.jsonl"),
        json!({"outcome": "cited:a-key"}).to_string() + "\n",
    )
    .unwrap();
    assert_eq!(cli(&a(&["lookup", "--key", "a"]), &root).code, 1);
    assert_eq!(cli(&a(&[]), &root).code, 2);
}

#[test]
fn the_one_time_seed_and_import() {
    let (d, root, home) = world("sources-import");
    let per = d.join("per_url.json");
    std::fs::write(&per, json!({"a.org/a": [{"ts": "2026-09-26T10:00:00Z", "session": "s", "feature": 257, "why": " the  walls "}, {"ts": "2026-09-25T10:00:00Z", "session": "s", "feature": "257"}],
                                "z.org": [{"ts": "x", "session": "t"}]}).to_string()).unwrap();
    let scratch = d.join("scratch");
    let put = |rel: &str, text: &str| {
        let p = scratch.join(rel);
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(p, text).unwrap();
    };
    put("r1/MANIFEST.txt", "pointer | file | state\nhttps://a.org/x | 01-a.txt | FETCHED - 3\nhttps://b.org/y | 02-b.p1.txt ... | FETCHED - 4\nhttps://c.org/z | 03-c.txt | FETCHED - excerpt\nhttps://d.org | - | UNFETCHABLE\nhttps://e.org | 05-e.txt | FETCHED\nhttps://f.org | 06-f.txt | FETCHED\nx | 07.txt | FETCHED\n");
    put("r1/01-a.txt", "page a\r\n");
    put("r1/02-b.p1.txt", "one\n");
    put("r1/02-b.p2.txt", "two\n");
    put("r1/06-f.txt", "[EXCERPT of f]\n");
    put(
        "r2/MANIFEST.txt",
        "pointer | file | state\nhttps://www.a.org/x/ | 01-a.txt | FETCHED\n",
    );
    put("r2/01-a.txt", "older a\n");
    let old = std::time::SystemTime::UNIX_EPOCH + std::time::Duration::from_secs(1_000_000_000);
    std::fs::File::options()
        .write(true)
        .open(scratch.join("r2/01-a.txt"))
        .unwrap()
        .set_modified(old)
        .unwrap();
    let (p, s) = (
        per.to_string_lossy().into_owned(),
        scratch.to_string_lossy().into_owned(),
    );
    std::fs::write(
        root.join("research/sources/010-works-cited/1a-x.html"),
        "<p>(https://x.org)</p>",
    )
    .unwrap();
    std::fs::write(
        home.join("sources-consulted.jsonl"),
        "{\"url\": \"earlier.org\", \"outcome\": \"pending\"}\n",
    )
    .unwrap();
    let got = cli(&a(&["import", "--per-url", &p, "--scratch", &s]), &root);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.starts_with(&format!(
        "sources-import: seeded 2 ledger line(s) from {p} (0: already seeded, or no file)\n"
    )));
    assert!(got.stdout.contains("{\"manifests\": 2, \"rows\": 6, \"excerpts\": 2, \"missing\": 1, \"distinct\": 2, \"imported\": 2, \"already\": 0}"));
    assert!(ledger(&home).contains("\"questions\": [\"the walls\"]"));
    let again = cli(&a(&["import", "--per-url", &p, "--scratch", &s]), &root);
    assert!(again.stdout.contains("seeded 0 ledger") && again.stdout.contains("\"already\": 2"));
    let none = cli(
        &a(&["import", "--per-url", "/no/such", "--scratch", "/no/such"]),
        &root,
    );
    assert!(none.stdout.ends_with("sources-import: page cache {}\n"));
    std::fs::write(home.join("sources-consulted.jsonl"), "").unwrap();
    std::fs::write(&per, "{").unwrap();
    assert_eq!(
        cli(&a(&["import", "--per-url", &p, "--scratch", "/no"]), &root).code,
        1
    );
    std::fs::write(&per, "[]").unwrap();
    assert_eq!(
        cli(&a(&["import", "--per-url", &p, "--scratch", "/no"]), &root).code,
        1
    );
    std::fs::write(&per, r#"{"u": "a string", "v": "", "w": {}}"#).unwrap();
    assert_eq!(
        cli(&a(&["import", "--per-url", &p, "--scratch", "/no"]), &root).code,
        1
    );
    std::fs::write(&per, r#"{"v": "", "w": {}}"#).unwrap();
    assert_eq!(
        cli(&a(&["import", "--per-url", &p, "--scratch", "/no"]), &root).code,
        0
    );
    std::fs::write(home.join("sources-consulted.jsonl"), "[1]\n").unwrap();
    assert_eq!(
        cli(&a(&["import", "--per-url", &p, "--scratch", "/no"]), &root).code,
        1
    );
    std::fs::write(home.join("sources-consulted.jsonl"), "").unwrap();
    let meta = l7r_gate_research::pages::entry_dir(&home, "https://b.org/y").join("meta.json");
    std::fs::write(meta, "[]").unwrap();
    assert_eq!(
        cli(&a(&["import", "--per-url", "/no", "--scratch", &s]), &root).code,
        1
    );
    assert_eq!(cli(&a(&["import", "--x"]), &root).code, 2);
    let _ = std::fs::remove_dir_all(home.join("page-cache"));
    std::fs::write(home.join("page-cache"), "a file where the cache goes").unwrap();
    assert_eq!(
        cli(&a(&["import", "--per-url", "/no", "--scratch", &s]), &root).code,
        1
    );
}

#[test]
fn the_attempts_commands() {
    let (_d, root, _home) = world("sources-attempts");
    let r = root.to_string_lossy().into_owned();
    let seen = attempts_cli(
        &a(&[
            "seen",
            "--root",
            &r,
            "--sought",
            "s",
            "--route",
            "bash",
            "--record",
            "--",
            "https://a.org/&amp;x",
            "--odd",
        ]),
        &root,
    );
    assert_eq!(seen.stdout, "[{\"lines\": [], \"plain\": \"https://a.org/&x\"}, {\"lines\": [], \"plain\": \"--odd\"}]\n");
    assert_eq!(attempts_cli(&a(&["seen", "--root", &r]), &root).code, 2);
    assert_eq!(attempts_cli(&a(&["seen", "--bogus"]), &root).code, 2);
    let add = attempts_cli(
        &a(&[
            "add",
            "--url",
            "https://a.org/y",
            "--q",
            "0012",
            "--sought",
            "s",
            "--outcome",
            "found",
            "--route",
            "r",
            "--key",
            "k",
        ]),
        &root,
    );
    assert_eq!(add.code, 0);
    assert_eq!(
        attempts_cli(
            &a(&["add", "--url", "u", "--sought", "s", "--outcome", "maybe"]),
            &root
        )
        .code,
        2
    );
    assert_eq!(attempts_cli(&a(&["add", "--url", "u"]), &root).code, 2);
    assert_eq!(
        attempts_cli(
            &a(&["add", "--url", "https://bad.example/x", "--sought", "s"]),
            &root
        )
        .code,
        1
    );
    assert_eq!(attempts_cli(&a(&["add", "--x"]), &root).code, 2);
    let show = |args: &[&str]| attempts_cli(&a(args), &root);
    assert!(show(&["show", "--url", "https://a.org/y"])
        .stdout
        .starts_with("attempts: https://a.org/y - 1 earlier attempt(s):\n"));
    assert!(show(&["show", "--key", "k"])
        .stdout
        .starts_with("attempts: key k - 1 attempt(s)\n"));
    assert!(show(&["show", "--q", "0012"])
        .stdout
        .starts_with("attempts: question 0012 - 1 attempt(s)\n"));
    assert_eq!(
        show(&["show", "--url", ""]).stdout,
        "attempts: question  - 0 attempt(s)\n"
    );
    assert_eq!(show(&["show"]).code, 2);
    assert_eq!(show(&["show", "--url", "a", "--key", "b"]).code, 2);
    assert_eq!(show(&["show", "--nope"]).code, 2);
    let seeded = attempts_cli(&a(&["seed"]), &root);
    assert_eq!(
        (seeded.code, seeded.stderr.as_str()),
        (
            0,
            "attempts: every ledger row has an attempt line - nothing written\n"
        )
    );
    std::fs::write(root.join("research/source-attempts.jsonl"), "[1]\n").unwrap();
    assert_eq!(show(&["show", "--q", "x"]).code, 1);
    assert_eq!(attempts_cli(&a(&["seed"]), &root).code, 1);
    assert_eq!(
        attempts_cli(
            &a(&["seen", "--root", &r, "--sought", "s", "--route", "b", "u"]),
            &root
        )
        .code,
        1
    );
    assert_eq!(attempts_cli(&a(&["nope"]), &root).code, 2);
}

#[test]
fn an_odd_registry_and_the_archive_switch() {
    let (_d, root, _home) = world("sources-odd");
    let reg = root.join("research/sources/010-works-cited");
    std::fs::write(reg.join("1a-x.html"), "<p>(https://x.org)</p>").unwrap();
    assert_eq!(registry(&root).unwrap().len(), 1);
    let mut err = String::new();
    super::archive_reads(&root, &["https://a.org"], &mut err, &|_| "0".to_owned());
    assert!(err.is_empty());
    // the test's stand-in browser (the real one is the archive's production wiring, never started by a test)
    assert_eq!(
        super::reads_browser(&root).err().map(|e| e.kind),
        Some("Error")
    );
    std::fs::set_permissions(
        reg.join("0010-a-key.html"),
        std::fs::Permissions::from_mode(0o000),
    )
    .unwrap();
    assert_eq!(registry(&root).unwrap_err().kind, "OSError");
    std::fs::set_permissions(
        reg.join("0010-a-key.html"),
        std::fs::Permissions::from_mode(0o644),
    )
    .unwrap();
}
