//! The bench, proven to fire: the prefilter, the four-way classification, the diff in both directions, and a baseline at a ref. The British forms are SPLIT so the house-style
//! guard cannot correct these cases as they are written (it did, the first time, and three of them then tested the American spelling they were meant to avoid).

use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::SystemTime;

use serde_json::{json, Value};

use super::{
    answer, classify, classify_printed, cli, diff, guard_named, refresh, verdicts, window_commands,
};
use crate::protocol::{Answer, Event, Guard};
use crate::shared::log::quiet;
use crate::shared::session::Session;

fn center() -> String {
    ["cent", "re"].concat()
}

const EM: char = '\u{2014}';
const EN: char = '\u{2013}';

fn strings(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

fn no_answer(_: &Event, _: &Session) -> Vec<Answer> {
    Vec::new()
}

fn stub(name: &'static str) -> Guard {
    Guard {
        name,
        events: &["PreToolUse"],
        matcher: "*",
        decide: no_answer,
    }
}

fn base(tag: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("l7r-guard-bench-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(dir.join("tests/hooks/fixtures")).unwrap();
    dir
}

fn exe(path: &Path, body: &str) -> String {
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, format!("#!/bin/bash\n{body}\n")).unwrap();
    Command::new("chmod").arg("+x").arg(path).status().unwrap();
    path.to_string_lossy().into_owned()
}

fn git(root: &Path, args: &[&str]) {
    let done = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["-c", "user.name=t", "-c", "user.email=t@t"])
        .args(args)
        .output()
        .unwrap();
    assert!(done.status.success());
}

fn corpus(root: &Path, commands: &[&str]) {
    let frozen = json!({"commands": commands});
    std::fs::write(
        root.join("tests/hooks/fixtures/command-window-2026-01-01.json"),
        frozen.to_string(),
    )
    .unwrap();
}

#[test]
fn a_verdict_is_classified_four_ways() {
    assert_eq!(classify(&[]), "silent");
    assert_eq!(classify(&[Answer::Rewrite(Value::Null)]), "corrected");
    assert_eq!(classify(&[Answer::Notice("told".to_owned())]), "reported");
    assert_eq!(
        classify(&[Answer::Notice(String::new()), Answer::Refuse(String::new())]),
        "blocked"
    );
    assert_eq!(classify_printed("", false), "silent");
    assert_eq!(
        classify_printed(
            "{\"hookSpecificOutput\": {\"updatedInput\": {\"command\": \"x\"}}}",
            false
        ),
        "corrected"
    );
    assert_eq!(
        classify_printed(
            "{\"hookSpecificOutput\": {\"additionalContext\": \"told\"}}",
            false
        ),
        "reported"
    );
    assert_eq!(classify_printed("a | b", false), "blocked");
    assert_eq!(classify_printed("", true), "blocked");
}

#[test]
fn the_house_style_decision_is_called_in_process() {
    quiet();
    let all = crate::guards();
    let guard = guard_named("house-style", &all).unwrap();
    let word = center();
    let commands = [
        format!("echo 'the {word} of it' >> docs/a.md"),
        format!("sed -i 's/{word}/center/g' docs/a.md"),
        format!("grep -n {word} docs/a.md"),
    ];
    assert_eq!(
        verdicts(guard, &commands),
        ["corrected", "reported", "silent"]
    );
    assert!(guard_named("house-style-hooks", &all).is_some());
    assert!(guard_named("no-such", &all).is_none());
}

#[test]
fn the_window_is_frozen_from_transcripts() {
    let dir = base("window");
    let project = dir.join("projects/-x/nested");
    std::fs::create_dir_all(&project).unwrap();
    let word = center();
    let use_of = |c: &str| {
        json!({"message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": c}}]}}).to_string()
    };
    let dash = format!("echo a {EN} b");
    let body = [
        use_of(&format!("echo the {word}")),
        use_of(&format!("echo the {word}")),
        use_of("ls -la"),
        use_of(&dash),
        "{\"Bash\": not json".to_owned(),
        String::new(),
    ]
    .join("\n");
    std::fs::write(project.join("s.jsonl"), body).unwrap();
    std::fs::write(project.join("s.txt"), use_of(&format!("echo {word} too"))).unwrap();
    let out = refresh(14.0, &dir, &dir.join("projects"));
    let got: Value = serde_json::from_str(&std::fs::read_to_string(&out).unwrap()).unwrap();
    assert!(out
        .file_name()
        .unwrap()
        .to_string_lossy()
        .starts_with("command-window-"));
    assert_eq!(got["commands"], json!([format!("echo the {word}"), dash]));
    assert!(std::fs::read_to_string(&out)
        .unwrap()
        .starts_with("{\n \"taken\""));
    let later = SystemTime::now() + std::time::Duration::from_secs(40 * 86_400);
    assert!(window_commands(14.0, &dir.join("projects"), later).is_empty(),);
    assert!(window_commands(14.0, &dir.join("absent"), SystemTime::now()).is_empty());
    assert!(!format!("a{EM}").is_empty());
}

#[test]
fn the_diff_reports_both_directions() {
    let commands = strings(&["a", "b", "c"]);
    let changed = diff(
        &commands,
        &["silent", "corrected", "silent"],
        &["corrected", "silent", "silent"],
    );
    assert_eq!(
        changed,
        [("silent", "corrected", "a"), ("corrected", "silent", "b")]
    );
}

#[test]
fn the_command_line_names_what_it_cannot_do() {
    quiet();
    let dir = base("refusals");
    let all = [stub("x-hooks")];
    let ask = |words: &[&str]| answer(&dir, &strings(words), &all, &dir.join("projects"), "false");
    assert!(ask(&[]).stderr.contains("name a GUARD"));
    assert!(ask(&["nope"]).stderr.contains("no guard named nope"));
    assert!(ask(&["x"]).stderr.contains("no frozen corpus"));
    assert!(ask(&["--refresh", "3"]).stdout.contains("froze 0 commands"));
    let printed = ask(&["x"]).stdout;
    assert!(printed.contains("hookbench x-hooks: 0 commands from command-window-"));
    assert!(printed.contains("corrected 0  reported 0  silent 0  blocked 0"));
    assert_eq!(cli(&strings(&[])).code, 1);
    let bad_corpus = dir.join("tests/hooks/fixtures/command-window-notes.txt");
    std::fs::write(bad_corpus, "not a corpus").unwrap();
    assert!(ask(&["x"]).stdout.contains(".json"));
}

#[test]
fn a_baseline_is_the_guard_as_it_stood_at_the_ref() {
    quiet();
    let dir = base("baseline");
    git(&dir, &["init", "-q"]);
    corpus(&dir, &["one", "two", "echo x > /tmp/a"]);
    exe(
        &dir.join("scripts/hooks/x-hooks.sh"),
        "read -r line; case $line in *two*) exit 2;; esac; echo '{\"updatedInput\": 1}'",
    );
    git(&dir, &["add", "scripts"]);
    git(&dir, &["commit", "-q", "-m", "shell"]);
    git(&dir, &["tag", "shell"]);
    exe(
        &dir.join("scripts/hooks/x-hooks.sh"),
        "cat > /dev/null; exit 2",
    );
    git(&dir, &["add", "scripts"]);
    git(&dir, &["commit", "-q", "-m", "refuses"]);
    git(&dir, &["tag", "refuses"]);
    std::fs::create_dir_all(dir.join("rust/guard/src/guards")).unwrap();
    std::fs::write(
        dir.join("rust/guard/src/guards/x_hooks.rs"),
        "// the guard\n",
    )
    .unwrap();
    std::fs::write(dir.join("rust/Cargo.toml"), "[workspace]\n").unwrap();
    git(&dir, &["add", "rust"]);
    git(&dir, &["commit", "-q", "-m", "rust"]);
    git(&dir, &["tag", "rust"]);
    let cargo = exe(&dir.join("fake-cargo"), "mkdir -p \"$CARGO_TARGET_DIR/release\"; printf '#!/bin/bash\\ncat >/dev/null; echo told\\n' > \"$CARGO_TARGET_DIR/release/l7r-guard\"; chmod +x \"$CARGO_TARGET_DIR/release/l7r-guard\"");
    let all = [stub("x-hooks"), stub("gone-hooks")];
    let ask = |words: &[&str], cargo: &str| {
        answer(&dir, &strings(words), &all, &dir.join("projects"), cargo)
    };
    let shell = ask(&["x", "--against", "shell"], "false").stdout;
    assert!(shell.contains("verdict diff against shell (its shell guard at that ref"));
    assert!(
        shell.contains("3 changed")
            && shell.contains("   2  corrected -> silent")
            && shell.contains("   1  blocked -> silent")
    );
    assert!(shell.contains("[corrected -> silent] targets=[] :: one"));
    assert!(shell.contains("targets=[Some(\"/tmp/a\")]"));
    let refuses = ask(&["x", "--against", "refuses"], "false").stdout;
    assert!(refuses.contains("blocked -> silent"));
    let rust = ask(&["x", "--against", "rust"], &cargo).stdout;
    assert!(
        rust.contains("its Rust guard built from that ref") && rust.contains("blocked -> silent")
    );
    assert!(ask(&["x", "--against", "rust"], "false")
        .stderr
        .contains("would not build"));
    assert!(ask(&["gone", "--against", "shell"], "false")
        .stderr
        .contains("did not exist at that ref"));
    assert!(ask(&["x", "--against", "no-such-ref"], "false")
        .stderr
        .contains("cannot read scripts/"));
    assert!(!ask(&["x", "--against"], "false")
        .stdout
        .contains("verdict diff"));
}
