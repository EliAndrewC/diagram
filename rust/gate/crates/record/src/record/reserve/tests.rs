//! The prefix reservation (feature 449 T145; each refusal's words `reserve-prefix.py`'s, the T145 differential holding the rest).

use std::collections::HashMap;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_shared::tempdir::TempDir;
use serde_json::json;

use super::*;

const VOCAB: &str = r#"{"period": [{"id": "premodern", "name": "P", "description": "d"}], "region": [{"id": "japan", "name": "J", "description": "d"}],
"kind": [{"id": "primary", "name": "K", "description": "d"}], "canon": {"id": "canon", "name": "C", "description": "d"}}"#;
const LIST: &str = r#"{"domains": [{"domain": "bad.example", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

/// The command line with its archiving at citation a stand-in that fails as a browser that cannot start would (feature 449 T146: the
/// real one starts Chromium); `super::cli`, the real wiring, is asked only of a refusal that stops before it.
fn cli(args: &[String], cwd: &Path) -> crate::Reply {
    cli_with(args, cwd, &|_, url, key, err| {
        let _ = writeln!(err, "Error: BrowserType.launch: none\nreserve: archiving {url} failed (exit 1) - `make archive URL='{url}' KEY={key}` retries it");
        1
    })
}

/// A mirror with a clone under `.clones/`, its record's vocabulary and blocked list.
fn world(tag: &str) -> (TempDir, PathBuf, PathBuf) {
    let d = TempDir::new(tag);
    let mirror = d.join("m");
    let root = mirror.join(".clones/c");
    std::fs::create_dir_all(root.join("research/sources/010-works-cited")).unwrap();
    std::fs::create_dir_all(mirror.join(".specify")).unwrap();
    std::fs::write(root.join("research/source-tags.json"), VOCAB).unwrap();
    std::fs::write(root.join("research/blocked-domains.json"), LIST).unwrap();
    (d, mirror, root)
}

fn env(pairs: &[(&str, &str)]) -> HashMap<String, String> {
    pairs
        .iter()
        .map(|(k, v)| ((*k).to_owned(), (*v).to_owned()))
        .collect()
}

fn ask<'a>(
    kind: &'a str,
    key: &'a str,
    root: &'a Path,
    var: &'a dyn Fn(&str) -> String,
) -> Ask<'a> {
    Ask {
        kind,
        key,
        root,
        mirror: None,
        stub: None,
        timeout: 5.0,
        url: "",
        tags: "",
        command: "t".into(),
        var,
    }
}

fn refusal(got: Result<PathBuf, Refused>) -> String {
    match got {
        Err(Refused::Refusal(why)) => why,
        other => format!("not a refusal: {other:?}"),
    }
}

#[test]
fn each_kind_takes_the_next_prefix_and_writes_its_stub() {
    let (_d, mirror, root) = world("reserve-kinds");
    let none = |_: &str| String::new();
    let g = reserve(&ask("glossary", "a/b%c", &root, &none)).unwrap();
    assert_eq!(g.file_name().unwrap(), "0010-a%2Fb%25c.json");
    assert_eq!(
        std::fs::read_to_string(&g).unwrap(),
        "{\n \"term\": \"a/b%c\",\n \"def\": \"\",\n \"variants\": [\n  \"a/b%c\"\n ]\n}\n"
    );
    let q = reserve(&ask("question", "a-heading", &root, &none)).unwrap();
    assert!(q.ends_with("research/questions/0001-a-heading.html"));
    assert!(std::fs::read_to_string(&q)
        .unwrap()
        .starts_with("<h2 id=\"a-heading\">TITLE</h2>"));
    let mut r = ask("registry", "k-enwiki", &root, &none);
    r.url = "https://e.org/x";
    r.tags = "period=premodern; region=japan; kind=primary";
    let entry = reserve(&r).unwrap();
    assert_eq!(entry.file_name().unwrap(), "0010-k-enwiki.html");
    assert_eq!(
        std::fs::read_to_string(&entry).unwrap(),
        "<h3 id=\"k-enwiki\"><code>k-enwiki</code></h3>\n<p>(https://e.org/x)</p>\n<!-- tags: period=premodern; region=japan; kind=primary -->\n"
    );
    let ledger = std::fs::read_to_string(mirror.join(".specify/sources-consulted.jsonl")).unwrap();
    assert!(ledger.contains("\"outcome\": \"cited:k-enwiki\""));
    let u = reserve(&ask("uncited", "u-key", &root, &none)).unwrap();
    assert_eq!(u.file_name().unwrap(), "0020-u-key.html");
    assert!(std::fs::read_to_string(&u)
        .unwrap()
        .ends_with(&format!("{TAGS_PLACEHOLDER}\n")));
    let rows = std::fs::read_to_string(mirror.join(".specify/prefixes.jsonl")).unwrap();
    assert_eq!(rows.lines().count(), 4);
    assert!(reserved("registry", 10, &mirror, Some("k-enwiki")).unwrap());
    assert!(reserved("registry", 10, &mirror, None).unwrap());
    assert!(!reserved("registry", 10, &mirror, Some("other")).unwrap());
    assert!(!reserved("registry", 10, &root, None).unwrap());
    assert_eq!(prefix_of_name("0010-k.html"), Some(10));
    assert_eq!(prefix_of_name("k.html"), None);
}

#[test]
fn what_a_reservation_refuses() {
    let (_d, mirror, root) = world("reserve-refusals");
    let none = |_: &str| String::new();
    assert_eq!(refusal(Ok(PathBuf::from("x"))), "not a refusal: Ok(\"x\")");
    assert!(refusal(reserve(&ask("nope", "k", &root, &none)))
        .starts_with("KIND must be one of ['glossary', 'question', 'registry', 'uncited']"));
    let mut a = ask("glossary", "k", &root, &none);
    a.url = "x";
    assert!(refusal(reserve(&a)).starts_with("URL= names"));
    let mut a = ask("question", "k", &root, &none);
    a.tags = "x";
    assert!(refusal(reserve(&a)).starts_with("TAGS= are"));
    assert!(refusal(reserve(&ask("glossary", " ", &root, &none))).starts_with("KEY is required"));
    let mut a = ask("registry", "k", &root, &none);
    a.tags = "period=medieval; region=japan; kind=primary";
    assert!(refusal(reserve(&a)).contains("medieval"));
    std::fs::write(
        root.join("research/sources/010-works-cited/0100-held.html"),
        "x",
    )
    .unwrap();
    assert_eq!(refusal(reserve(&ask("registry", "held", &root, &none))), "research/sources/010-works-cited/0100-held.html already holds 'held' - edit it rather than reserving another");
    std::fs::create_dir_all(mirror.join(".clones/other/research/sources/040-uncited-works"))
        .unwrap();
    std::fs::write(
        mirror.join(".clones/other/research/sources/040-uncited-works/0200-there.html"),
        "x",
    )
    .unwrap();
    assert!(refusal(reserve(&ask("registry", "there", &root, &none)))
        .contains(".clones/other - one home per registry key"));
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), "x\n{\"kind\": \"glossary\", \"key\": \"g\", \"prefix\": 500, \"clone\": \"/elsewhere\", \"utc\": \"t\"}\n").unwrap();
    assert_eq!(refusal(reserve(&ask("glossary", "g", &root, &none))), "'g' is already being defined in /elsewhere (reserved 500, t) - one home per glossary key; pull that work in and edit it there");
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), "[1]\n").unwrap();
    assert!(matches!(
        reserve(&ask("glossary", "g", &root, &none)),
        Err(Refused::Raised(..))
    ));
    for prefix in [
        json!("x1"),
        json!(null),
        json!(true),
        json!(2.5),
        json!("12"),
    ] {
        std::fs::write(
            mirror.join(".specify/prefixes.jsonl"),
            json!({"kind": "glossary", "prefix": prefix}).to_string() + "\n",
        )
        .unwrap();
        let _ = reserve(&ask("glossary", "p", &root, &none));
    }
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), "").unwrap();
    let held = l7r_shared::tool::flock_within(&mirror.join(".specify/prefixes.lock"), 1.0)
        .unwrap()
        .unwrap();
    let mut a = ask("glossary", "late", &root, &none);
    a.timeout = 0.05;
    assert!(refusal(reserve(&a)).starts_with("could not take the prefix lock within 0.05s"));
    drop(held);
    std::fs::write(mirror.join(".specify/prefixes.lock"), "").unwrap();
    std::fs::create_dir_all(root.join("research/questions")).unwrap();
    std::fs::write(root.join("blocker"), "").unwrap();
    let blocker = root.join("blocker");
    let mut a = ask("glossary", "nowhere", &root, &none);
    a.mirror = Some(&blocker);
    assert!(matches!(reserve(&a), Err(Refused::Raised(..))));
    let mut a = ask("registry", "grok", &root, &none);
    a.url = "https://bad.example/x";
    assert!(matches!(reserve(&a), Err(Refused::Raised(k, _)) if k == "Blocked"));
}

#[test]
fn a_write_sessions_key_cap() {
    let (d, mirror, root) = world("reserve-cap");
    let rows: String = (1..=3)
        .map(|i| {
            json!({"kind": "registry", "key": format!("k{i}"), "prefix": 10 * i, "session": "s1"})
                .to_string()
                + "\n"
        })
        .collect();
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), &rows).unwrap();
    let logs = d.join("logs").to_string_lossy().into_owned();
    let run = |pairs: &[(&str, &str)]| {
        let mut all = env(pairs);
        all.insert("GUARD_LOG_DIR".into(), logs.clone());
        let var = move |k: &str| all.get(k).cloned().unwrap_or_default();
        reserve(&ask("registry", "capped", &root, &var))
    };
    let why = refusal(run(&[
        ("L7R_PAGE_SESSION", "s1"),
        ("L7R_KEY_CAP", "3"),
        ("L7R_CONTINUE", "/x/b.md"),
    ]));
    assert!(
        why.starts_with("this write session has reserved 3 new registry keys, its cap")
            && why.contains("to /x/b.md as a brief")
    );
    assert!(
        refusal(run(&[("L7R_PAGE_SESSION", "s1"), ("L7R_KEY_CAP", "3")]))
            .contains("to $L7R_CONTINUE as")
    );
    assert!(refusal(run(&[
        ("L7R_PAGE_SESSION", "s1"),
        ("L7R_KEY_CAP", "3"),
        ("KEY_CAP_OK", "x")
    ]))
    .starts_with("KEY_CAP_OK needs a REASON"));
    let escaped = run(&[
        ("L7R_PAGE_SESSION", "s1"),
        ("L7R_KEY_CAP", "3"),
        ("KEY_CAP_OK", "a deliberate larger load"),
    ])
    .unwrap();
    assert!(escaped.ends_with("0040-capped.html"));
    assert_eq!(std::fs::read_dir(d.join("logs")).unwrap().count(), 2);
    std::fs::remove_file(escaped).unwrap();
    assert!(run(&[("L7R_PAGE_SESSION", "s1"), ("L7R_KEY_CAP", "x")])
        .unwrap()
        .ends_with("0050-capped.html"));
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "every form of the command line, one after another"
)]
fn the_command_line() {
    let (_d, mirror, root) = world("reserve-cli");
    let a = |list: &[&str]| list.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
    let r = root.to_string_lossy().into_owned();
    let m = mirror.to_string_lossy().into_owned();
    let got = cli(
        &a(&["glossary", "term", "--root", &r, "--mirror", &m]),
        &root,
    );
    assert_eq!(
        (got.code, got.stdout.trim_end().ends_with("0010-term.json")),
        (0, true)
    );
    assert_eq!(
        cli(
            &a(&["glossary", "term", "--root", &r, "--mirror", &m]),
            &root
        )
        .code,
        2
    );
    assert_eq!(
        cli(
            &a(&[
                "glossary",
                "term",
                "--root",
                &r,
                "--mirror",
                &m,
                "--check",
                "x/0010-term.json"
            ]),
            &root
        )
        .code,
        0
    );
    assert_eq!(
        cli(
            &a(&[
                "glossary",
                "",
                "--root",
                &r,
                "--mirror",
                &m,
                "--check",
                "0010-any.json"
            ]),
            &root
        )
        .code,
        0
    );
    assert_eq!(
        cli(
            &a(&[
                "glossary",
                "term",
                "--root",
                &r,
                "--mirror",
                &m,
                "--check",
                "term.json"
            ]),
            &root
        )
        .code,
        1
    );
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), "[1]\n").unwrap();
    assert_eq!(
        cli(
            &a(&[
                "glossary",
                "term",
                "--root",
                &r,
                "--mirror",
                &m,
                "--check",
                "0010-term.json"
            ]),
            &root
        )
        .code,
        1
    );
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), "").unwrap();
    assert_eq!(cli(&a(&["nope", "k"]), &root).code, 2);
    assert_eq!(cli(&a(&["glossary"]), &root).code, 2);
    assert_eq!(cli(&a(&["glossary", "k", "--bogus"]), &root).code, 2);
    std::fs::create_dir_all(root.join(".git")).unwrap();
    let from_cwd = cli(&a(&["glossary", "cwd-term"]), &root.join("research"));
    assert_eq!(from_cwd.code, 0, "{}", from_cwd.stderr);
    let cited = cli(
        &a(&[
            "registry",
            "cited-key",
            "--root",
            &r,
            "--mirror",
            &m,
            "--url",
            "https://e.org/c",
        ]),
        &root,
    );
    assert!(cited
        .stderr
        .contains("reserve: archiving https://e.org/c failed"));
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), "[1]\n").unwrap();
    assert_eq!(
        cli(&a(&["glossary", "x", "--root", &r, "--mirror", &m]), &root).code,
        1
    );
    // the real command line, on a refusal before any archiving
    assert_eq!(super::cli(&a(&["nope", "k"]), &root).code, 2);
    // archiving at citation, in process (feature 449 T146): a browser that answers nothing marks the URL unreachable and logs the
    // attempt; one that cannot start fails the archiving, never the reservation; the real one stops at a record it cannot read
    let mut err = String::new();
    let store_at = |_: &Path| {
        let mut a = l7r_gate_archive::store::Archive::new(&mirror.join(".specify"), None);
        a.gm = mirror.join("no-gm");
        a
    };
    std::process::Command::new("git")
        .args(["init", "-q"])
        .arg(mirror.join(".specify/source-archive"))
        .status()
        .unwrap();
    std::fs::write(root.join("research/sources/_front.html"), "<main>\n").unwrap();
    std::fs::write(root.join("research/sources/_tail.html"), "</main>\n").unwrap();
    let dead = |_: &Path| -> l7r_gate_archive::Result<Box<dyn l7r_gate_archive::fetch::Client>> {
        Ok(Box::new(Dead))
    };
    assert_eq!(
        archive_at_cite_with(&root, "https://e.org/c", "k", &dead, &store_at, &mut err),
        0
    );
    assert!(err.contains("archive: unreachable - https://e.org/c (gone)"));
    let none = |_: &Path| -> l7r_gate_archive::Result<Box<dyn l7r_gate_archive::fetch::Client>> {
        Err(l7r_gate_archive::Error::new(
            "Error",
            "BrowserType.launch: none",
        ))
    };
    assert_eq!(
        archive_at_cite_with(&root, "https://e.org/c", "k", &none, &store_at, &mut err),
        1
    );
    assert!(err.contains(
        "Error: BrowserType.launch: none\nreserve: archiving https://e.org/c failed (exit 1)"
    ));
    let mut real = String::new();
    assert_eq!(
        archive_at_cite(&root.join("no/such/dir"), "u", "k", &mut real),
        1
    );
    assert!(real.contains("reserve: archiving u failed"), "{real}");
    assert_eq!(
        l7r_gate_archive::fetch::Client::render(&mut Dead, "u"),
        (String::new(), String::new())
    );
}

/// A browser to which every page is dead.
struct Dead;

impl l7r_gate_archive::fetch::Client for Dead {
    fn get(&mut self, url: &str) -> l7r_gate_archive::fetch::Fetched {
        l7r_gate_archive::fetch::Fetched::failed(url, "gone")
    }
    fn render(&mut self, _: &str) -> (String, String) {
        (String::new(), String::new())
    }
}

#[test]
fn the_ledgers_odd_rows_and_a_tree_that_cannot_be_written() {
    let (_d, mirror, root) = world("reserve-odd");
    let none = |_: &str| String::new();
    let rows = [
        json!({"kind": "glossary"}),
        json!({"kind": "glossary", "prefix": 2.9}),
        json!({"kind": "glossary", "key": "w", "clone": "/x"}),
    ];
    let text: String = rows.iter().map(|r| r.to_string() + "\n").collect();
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), text).unwrap();
    assert_eq!(refusal(reserve(&ask("glossary", "w", &root, &none))), "'w' is already being defined in /x (reserved None, None) - one home per glossary key; pull that work in and edit it there");
    assert!(reserve(&ask("glossary", "fresh", &root, &none))
        .unwrap()
        .ends_with("0010-fresh.json"));
    let cap = env(&[("L7R_PAGE_SESSION", "s9"), ("L7R_KEY_CAP", "9")]);
    let var = move |k: &str| cap.get(k).cloned().unwrap_or_default();
    assert!(reserve(&ask("registry", "under-cap", &root, &var)).is_ok());
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), [0xff]).unwrap();
    assert!(
        matches!(reserve(&ask("glossary", "u", &root, &none)), Err(Refused::Raised(k, _)) if k == "UnicodeDecodeError")
    );
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), "").unwrap();
    std::fs::write(root.join("research/source-tags.json"), [0xff]).unwrap();
    let mut b = ask("registry", "t", &root, &none);
    b.tags = "period=premodern";
    assert!(matches!(reserve(&b), Err(Refused::Raised(k, _)) if k == "UnicodeDecodeError"));
    std::fs::remove_file(root.join("research/source-tags.json")).unwrap();
    let mut a = ask("registry", "t", &root, &none);
    a.tags = "period=premodern";
    let _ = reserve(&a);
    std::fs::write(
        root.join("research/questions"),
        "a file where the directory goes",
    )
    .unwrap();
    assert!(
        matches!(reserve(&ask("question", "q", &root, &none)), Err(Refused::Raised(k, _)) if k == "OSError")
    );
}

#[test]
fn the_uncited_filters_reservation_in_process() {
    // feature 449 T147: `uncited.py install`'s reservation, in process where it loaded `reserve-prefix.py`
    let (_d, mirror, root) = world("reserve-uncited");
    let got = reserve_uncited("u-key", &root, "https://e.org/x").unwrap();
    assert!(got.ends_with("research/sources/040-uncited-works/0010-u-key.html"));
    assert!(
        std::fs::read_to_string(mirror.join(".specify/prefixes.jsonl"))
            .unwrap()
            .contains("\"key\": \"u-key\"")
    );
    let held = reserve_uncited("u-key", &root, "").unwrap_err();
    assert_eq!(held.kind, "Refusal");
    assert!(held.message.contains("already"));
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), [0xff]).unwrap();
    let odd = reserve_uncited("w", &root, "").unwrap_err();
    assert_eq!(odd.kind, "RuntimeError");
    assert!(odd.message.starts_with("UnicodeDecodeError: "));
    std::fs::write(mirror.join(".specify/prefixes.jsonl"), "").unwrap();
    std::fs::write(root.join("research/sources/040-uncited-works"), "").ok();
    std::fs::remove_dir_all(root.join("research/sources/040-uncited-works")).ok();
    std::fs::write(
        root.join("research/sources/040-uncited-works"),
        "a file where the folder goes",
    )
    .unwrap();
    let os = reserve_uncited("b", &root, "").unwrap_err();
    assert_eq!(os.kind, "OSError");
}
