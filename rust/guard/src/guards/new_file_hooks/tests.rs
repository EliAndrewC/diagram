//! The decider over a fixture mirror and clone (`tests/hooks/test-new-file-hooks.sh`, replayed through the shim, is the verdict).

use std::path::Path;

use serde_json::{json, Value};

use super::{decide, depth, mirror_of, strip_companion, top, verdict};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const GLOSSARY: &str = "l7r/diagram/interactive/assets/glossary";
const REGISTRY: &str = "research/sources/010-works-cited";
const QUESTIONS: &str = "research/questions";

/// A mirror with one clone, an old file in each directory, and one reservation.
fn world(tag: &str) -> String {
    crate::shared::log::quiet();
    let d = std::env::temp_dir().join(format!("l7r-guard-newfile-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&d);
    let clone = d.join("mirror/.clones/q");
    for dir in [GLOSSARY, REGISTRY, QUESTIONS, ".git"] {
        std::fs::create_dir_all(clone.join(dir)).unwrap();
    }
    std::fs::create_dir_all(d.join("mirror/.specify")).unwrap();
    std::fs::write(clone.join(GLOSSARY).join("0100-old.json"), "{}").unwrap();
    std::fs::write(clone.join(QUESTIONS).join("0243-the-last.html"), "x").unwrap();
    let rows = [
        json!({"kind": "registry", "prefix": 150, "key": "held-key"}).to_string(),
        "not json".to_owned(),
    ];
    std::fs::write(d.join("mirror/.specify/prefixes.jsonl"), rows.join("\n")).unwrap();
    clone.canonicalize().unwrap().to_string_lossy().into_owned()
}

fn event(tool: &str, input: &Value, at: &str) -> Event {
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "cwd": at, "tool_input": input}),
    }
}

fn write(path: &str, at: &str) -> Option<(&'static str, String)> {
    verdict(
        &event("Write", &json!({"file_path": path}), at),
        Path::new(at),
    )
}

fn bash(cmd: &str, at: &str) -> Option<(&'static str, String)> {
    verdict(&event("Bash", &json!({"command": cmd}), at), Path::new(at))
}

fn hit(kind: &'static str, key: &str) -> (&'static str, String) {
    (kind, key.to_owned())
}

#[test]
fn a_write_creating_an_unreserved_file_is_named() {
    let at = world("write");
    assert_eq!(
        write(&format!("{at}/{GLOSSARY}/0200-hito%2Fyado.json"), &at),
        Some(hit("glossary", "hito/yado"))
    );
    assert_eq!(
        write(&format!("{at}/{REGISTRY}/0200-suzhou.html"), &at),
        Some(hit("registry", "suzhou"))
    );
    assert_eq!(
        write(&format!("{at}/{QUESTIONS}/0244-new.html"), &at),
        Some(hit("question", "new"))
    );
    assert_eq!(
        write(&format!("{at}/{REGISTRY}/0150-other.html"), &at),
        Some(hit("registry", "other"))
    );
}

#[test]
fn an_existing_file_a_reservation_or_a_stems_companion_passes() {
    let at = world("pass");
    assert_eq!(write(&format!("{at}/{GLOSSARY}/0100-old.json"), &at), None);
    assert_eq!(
        write(&format!("{at}/{REGISTRY}/0150-held-key.html"), &at),
        None
    );
    assert_eq!(
        write(&format!("{at}/{QUESTIONS}/0243-the-last.notes.html"), &at),
        None
    );
    assert_eq!(
        write(&format!("{at}/{QUESTIONS}/0243-the-last.drawing.html"), &at),
        None
    );
    assert_eq!(
        write(&format!("{at}/research/fields/0300-q.html"), &at),
        None
    );
    assert_eq!(write(&format!("{at}/{GLOSSARY}/notes.json"), &at), None);
    assert_eq!(write("relative.json", &at), None);
}

#[test]
fn a_redirect_is_judged_by_its_resolved_path() {
    let at = world("shell");
    assert_eq!(
        bash("G=x; cat > \"$H/0300-wakato.json\" <<EOF\n{}\nEOF", &at),
        Some(hit("glossary", "wakato"))
    );
    assert_eq!(
        bash("cat > $H/0300-wakato.html", &at),
        Some(hit("registry", "wakato"))
    );
    assert_eq!(
        bash(&format!("echo x > {at}/{REGISTRY}/10990-five.html"), &at),
        Some(hit("registry", "five"))
    );
    assert_eq!(
        bash("Q=research/questions; echo x > $Q/0245-un.html", &at),
        Some(hit("question", "un"))
    );
    assert_eq!(
        bash(
            "Q='research/questions'; echo x | tee -a $Q/0245-un.html",
            &at
        ),
        Some(hit("question", "un"))
    );
    assert_eq!(
        bash(
            "echo {} > research/fields/0600-probe.json; echo x > /tmp/0600-foo.html",
            &at
        ),
        None
    );
    assert_eq!(bash("echo done > /tmp/out.txt; ls 0400-x.json", &at), None);
    assert_eq!(
        bash(
            "D=$(mktemp -d); echo x > $D/research/questions/0041-a.html",
            &at
        ),
        None
    );
    let other = format!("{at}-other");
    std::fs::create_dir_all(format!("{other}/.git")).unwrap();
    assert_eq!(
        bash(
            &format!("D={other}; echo x > $D/research/questions/0042-b.html"),
            &at
        ),
        None
    );
    assert_eq!(
        bash(
            &format!("echo x > {other}/research/questions/0043-c.html"),
            &at
        ),
        None
    );
    assert_eq!(
        bash(
            &format!("echo x > \"{at}/{REGISTRY}/99999999999999999999-long.html\""),
            &at
        ),
        None
    );
}

#[test]
fn each_kinds_depth_is_its_directorys() {
    for (kind, dir) in [
        ("glossary", GLOSSARY),
        ("registry", REGISTRY),
        ("question", QUESTIONS),
    ] {
        assert_eq!(depth(kind), Path::new(dir).components().count());
    }
}

#[test]
fn other_tools_and_empty_input_pass() {
    let at = world("other");
    assert_eq!(
        verdict(
            &event("Read", &json!({"file_path": "x"}), &at),
            Path::new(&at)
        ),
        None
    );
    let bare = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Write"}),
    };
    assert_eq!(verdict(&bare, Path::new(&at)), None);
    let here = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "cat > $H/0300-a.json"}}),
    };
    assert_eq!(verdict(&here, Path::new(&at)), Some(hit("glossary", "a")));
    assert_eq!(
        (
            strip_companion("a.drawing.notes"),
            strip_companion("a.originals"),
            strip_companion("a.notes.drawing")
        ),
        ("a", "a", "a.notes")
    );
    assert_eq!(
        top(Path::new("/no/such/place")),
        Path::new("/no/such/place")
    );
    assert_eq!(mirror_of("/".into()), Path::new("/"));
    assert_eq!(mirror_of("/m/x".into()), Path::new("/m/x"));
}

#[test]
fn the_refusal_names_the_command_and_the_escape_needs_a_reason() {
    let at = world("refuse");
    let run = |input: &Value, tool: &str| {
        let e = event(tool, input, &at);
        decide(&e, &Session::from_input(&e.input))
    };
    let refused =
        |got: &[Answer], words: &str| matches!(got, [Answer::Refuse(t)] if t.contains(words));
    let file = run(
        &json!({"file_path": format!("{at}/{GLOSSARY}/0200-a.json")}),
        "Write",
    );
    assert!(refused(&file, "make reserve KIND=glossary KEY=\"a\""));
    let cmd = "cat > \"$H/0500-x.json\" <<EOF\n{}\nEOF";
    assert!(refused(
        &run(&json!({"command": cmd}), "Bash"),
        "RESERVED prefix"
    ));
    assert!(run(
        &json!({"command": format!("{cmd}\n# RESERVE_OK: restoring a file deleted in a merge")}),
        "Bash"
    )
    .is_empty());
    assert!(refused(
        &run(&json!({"command": format!("{cmd}\n# RESERVE_OK")}), "Bash"),
        "with no reason"
    ));
    assert!(run(&json!({"command": "ls"}), "Bash").is_empty());
}
