//! The doors Python's `archive.py` forwards through (feature 449 T146).

use std::path::Path;
use std::sync::Mutex;

use serde_json::{json, Value};

use super::super::Reach;
use super::{cli, serve};
use crate::fetch::Client;
use crate::testkit::{git, Fake, World};
use crate::{Error, Reply};

#[expect(
    clippy::unnecessary_wraps,
    reason = "a browser's start, as the commands take it: this one always starts"
)]
fn browser(_: &Path) -> crate::Result<Box<dyn Client>> {
    let mut fake = Fake::default();
    fake.serve("https://e.org/a", 200, "text/html", b"<p>a</p>");
    fake.renders
        .insert("https://e.org/a".into(), ("M".into(), "shown".into()));
    fake.serve(
        "https://e.org/pdf",
        200,
        "application/pdf",
        crate::testkit::PDF,
    );
    let snap = json!({"archived_snapshots": {"closest": {"available": true, "url": "http://web.archive.org/web/2/s", "timestamp": "2"}}});
    let ask = format!(
        "https://archive.org/wayback/available?url={}",
        l7r_gate_research::verbatim::fetch::quote("https://e.org/snap", "")
    );
    fake.serve(&ask, 200, "application/json", snap.to_string().as_bytes());
    let odd = format!(
        "https://archive.org/wayback/available?url={}",
        l7r_gate_research::verbatim::fetch::quote("https://e.org/odd", "")
    );
    fake.serve(&odd, 200, "application/json", b"[]");
    Ok(Box::new(fake))
}

fn door(w: &World, verb: &str, args: &[&str], input: &str) -> (Reply, Vec<String>) {
    let said = Mutex::new(Vec::new());
    let say = |l: &str| said.lock().unwrap().push(l.to_owned());
    let store = |_: &Path| w.store();
    // the doors make their store from `--home`; the one handed in is the commands' (read here so it is a real one)
    assert_eq!(store(&w.root).home, w.home);
    let mut output = Vec::new();
    let mut input = input.as_bytes();
    let mut reach = Reach {
        store: &store,
        start: &browser,
        say: &say,
        input: &mut input,
        output: &mut output,
    };
    let mut all: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
    all.extend([
        "--root".to_owned(),
        w.root.to_string_lossy().into_owned(),
        "--home".to_owned(),
        w.home.to_string_lossy().into_owned(),
    ]);
    let reply = cli(verb, &all, &mut reach);
    let lines = said.into_inner().unwrap();
    (reply, lines)
}

#[test]
fn the_working_copys_writes_under_the_callers_lock() {
    let w = World::new("door-store");
    let _held = w.store().locked(1.0).unwrap();
    std::fs::remove_dir_all(w.home.join("source-archive")).unwrap();
    let remote = w.remote.to_string_lossy().into_owned();
    assert_eq!(door(&w, "ensure", &["--remote", &remote], "").0.code, 0);
    assert!(w.home.join("source-archive/.git").is_dir());
    // the door's store takes the GM's folder from the environment, which the tests leave unset: a name in no folder places nothing
    let (r, _) = door(
        &w,
        "place-gm",
        &["--name", "t146-no-such-download.pdf"],
        "{}",
    );
    assert_eq!((r.code, r.stdout.as_str()), (0, ""));
    let bad = door(&w, "place-gm", &["--name", "x"], "{bad").0;
    assert_eq!(bad.stderr.split(':').next(), Some("JSONDecodeError"));
    let (r, _) = door(&w, "push", &[], "");
    assert_eq!((r.code, r.stdout.as_str()), (0, ""));
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", "/no/such.git"],
    );
    w.store()
        .put("x/T", &[("f".to_owned(), b"1".to_vec())], "one")
        .unwrap();
    let (r, _) = door(&w, "push", &[], "");
    assert_eq!(r.code, 0);
    assert!(!r.stdout.trim().is_empty());
    assert_eq!(door(&w, "ensure", &["--bogus"], "").0.code, 2);
}

#[test]
fn the_manifests_writers() {
    let w = World::new("door-manifest");
    let who = json!({"keys": ["k"], "notes": ["n"]}).to_string();
    let (r, _) = door(
        &w,
        "url-row",
        &["--url", "https://e.org/a", "--no-push"],
        &who,
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    let row: Value = serde_json::from_str(r.stdout.trim()).unwrap();
    assert_eq!(
        (row["outcome"].clone(), row["keys"].clone()),
        (json!("archived"), json!(["k"]))
    );
    let blocked = door(&w, "url-row", &["--url", "https://grokipedia.com/x"], "{}").0;
    assert_eq!(blocked.stderr.split(':').next(), Some("Blocked"));
    let rows = w.dir.path().join("rows.jsonl");
    let rows_arg = rows.to_string_lossy().into_owned();
    let (r, lines) = door(
        &w,
        "lane",
        &["--rows", &rows_arg],
        "https://e.org/dead\n\nhttps://e.org/a\n",
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert_eq!(lines.len(), 2);
    let written = std::fs::read_to_string(&rows).unwrap();
    assert_eq!(written.lines().count(), 2);
    assert!(written.starts_with("{\"url\":\"https://e.org/dead\",\"keys\":"));
    let (r, _) = door(
        &w,
        "lane",
        &["--rows", "/no/such/dir/rows"],
        "https://e.org/dead\n",
    );
    assert_eq!(r.stderr.split(':').next(), Some("OSError"));
    crate::manifest::write_row(
        &w.root,
        "https://e.org/h",
        &json!({"url": "https://e.org/h", "outcome": "pending-upload", "held": "archived"}),
    )
    .unwrap();
    assert_eq!(door(&w, "settle", &[], "").0.stdout, "1\n");
    assert_eq!(door(&w, "sync-gm", &[], "").0.stdout, "0\n");
    let (r, _) = door(
        &w,
        "write-row",
        &["--url", "https://e.org/w"],
        "{\"url\": \"https://e.org/w\", \"outcome\": \"archived\"}",
    );
    assert_eq!(r.code, 0);
    assert!(crate::manifest::read_row(&w.root, "https://e.org/w").is_some());
    std::fs::remove_dir_all(w.research().join("sources")).unwrap();
    assert_eq!(door(&w, "lane", &[], "https://e.org/x\n").0.code, 1);
}

/// A writer that takes this many bytes, then fails.
struct Broken(usize);
impl std::io::Write for Broken {
    fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
        if buf.len() > self.0 {
            return Err(std::io::Error::other("closed"));
        }
        self.0 -= buf.len();
        Ok(buf.len())
    }
    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}

#[test]
fn serve_answers_the_pythons_browser() {
    let w = World::new("door-serve");
    let out = w.dir.path().join("body");
    let o = out.to_string_lossy().into_owned();
    let asked = [
        json!({"op": "get", "url": "https://e.org/a", "out": o}),
        json!({"op": "render", "url": "https://e.org/a"}),
        json!({"op": "fetch", "url": "https://e.org/pdf", "out": o}),
        json!({"op": "fetch", "url": "https://grokipedia.com/x", "out": o}),
        json!({"op": "wayback", "url": "https://e.org/a"}),
        json!({"op": "wayback", "url": "https://e.org/snap"}),
        json!({"op": "wayback", "url": "https://e.org/odd"}),
        json!({"op": "nope"}),
    ]
    .iter()
    .map(|v| v.to_string() + "\n")
    .collect::<String>()
        + "not json\n{\"op\": \"close\"}\n{\"op\": \"get\"}\n";
    let mut said = Vec::new();
    let r = serve(&w.root, &mut asked.as_bytes(), &mut said, &browser);
    assert_eq!(r.code, 0);
    let lines: Vec<Value> = String::from_utf8(said)
        .unwrap()
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    assert_eq!(lines.len(), 10);
    assert_eq!(lines[1]["status"], 200);
    assert_eq!(lines[2]["mhtml"], "M");
    assert_eq!(lines[3]["text"], "Hello PDF\n\u{c}");
    assert_eq!(std::fs::read(&out).unwrap(), crate::testkit::PDF);
    assert_eq!(lines[4]["raise"], "Blocked");
    assert_eq!(lines[5]["snapshot"], Value::Null);
    assert_eq!(
        lines[6]["snapshot"],
        json!(["https://web.archive.org/web/2/s", "2"])
    );
    assert_eq!(lines[7]["raise"], "AttributeError");
    assert_eq!(lines[8]["raise"], "ValueError");
    assert_eq!(lines[9]["message"], "unknown op \"\"");
    let failing = |_: &Path| -> crate::Result<Box<dyn Client>> {
        Err(Error::new("Error", "BrowserType.launch: none"))
    };
    let mut said = Vec::new();
    assert_eq!(
        serve(&w.root, &mut "".as_bytes(), &mut said, &failing).code,
        1
    );
    assert_eq!(
        String::from_utf8(said).unwrap().trim(),
        "{\"raise\":\"Error\",\"message\":\"BrowserType.launch: none\"}"
    );
    let one = "{\"op\": \"render\", \"url\": \"https://e.org/a\"}\n";
    assert_eq!(
        serve(&w.root, &mut one.as_bytes(), &mut Broken(20), &browser).code,
        0
    );
}
