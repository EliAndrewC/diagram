//! Feature 451 T93: a Bash call's write targets on its `PostToolUse` line (`writes`), from `shared::tree`'s walk, so T86's closing
//! checks set another task's shell-written files aside as they do its Edit and Write lines (`scripts/gates/closing-checks.sh`).

use std::path::Path;

use serde_json::{json, Value};

use super::super::{append, line};
use super::{clone, last_line, none};

fn bash(ev: &str, cwd: &str, command: &str) -> Value {
    json!({"hook_event_name": ev, "session_id": "s", "tool_name": "Bash", "tool_use_id": "u", "cwd": cwd, "tool_input": {"command": command}})
}

fn writes(ev: &str, cwd: &str, command: &str) -> Value {
    line(&bash(ev, cwd, command), "T")
        .remove("writes")
        .unwrap_or(Value::Null)
}

/// The files a call wrote, once each, in the walk's order: a redirect where a `cd` moved the shell, `sed -i`'s file, a copy's last
/// argument, a file written twice; not a directory it made, a `make` (a write where the shell stands, a directory), nor a program
/// that only reads. The line's form is pinned: the closing checks' reader looks for `"writes":` before it parses a line.
#[test]
fn a_bash_calls_post_line_names_the_files_it_wrote() {
    let d = clone("writes");
    let c = std::fs::canonicalize(&*d).unwrap();
    let c = c.to_string_lossy();
    std::fs::create_dir_all(d.join("sub")).unwrap();
    std::fs::create_dir_all(d.join("made")).unwrap();
    let cmd = "cd sub && echo x > out.txt; sed -i s/a/b/ ../f.txt; cp ../f.txt ../g.txt; echo y >> out.txt; mkdir -p ../made; \
               make quick; python3 -c 'print(1)'";
    assert_eq!(
        writes("PostToolUse", &c, cmd),
        json!([
            format!("{c}/sub/out.txt"),
            format!("{c}/f.txt"),
            format!("{c}/g.txt")
        ])
    );
    let row = Value::Object(line(
        &bash("PostToolUse", &c, "sed -i s/a/b/ docs/x.md"),
        "T",
    ));
    assert_eq!(
        row.to_string(),
        format!(
            r#"{{"t":"T","sid":"s","ev":"PostToolUse","tool":"Bash","id":"u","cat":"other tool","writes":["{c}/docs/x.md"]}}"#
        )
    );
}

/// Only a Bash call's end names its writes - its `PostToolUse`, or its `PostToolUseFailure` (a `sed -i F && make rust-test` red at its
/// test still wrote F) - never its start, another tool's end, or a call that wrote nothing: no field, never an empty list.
#[test]
fn only_a_bash_calls_end_names_its_writes() {
    let cmd = "echo x > /w/a.txt";
    assert_eq!(writes("PostToolUse", "/w", cmd), json!(["/w/a.txt"]));
    assert_eq!(writes("PostToolUseFailure", "/w", cmd), json!(["/w/a.txt"]));
    assert_eq!(writes("PreToolUse", "/w", cmd), Value::Null);
    assert_eq!(writes("PostToolUse", "/w", "ls -la"), Value::Null);
    assert_eq!(writes("PostToolUse", "/w", ""), Value::Null);
    let edit = json!({"hook_event_name": "PostToolUse", "tool_name": "Edit", "cwd": "/w", "tool_input": {"file_path": "/w/a.txt", "command": cmd}});
    assert_eq!(line(&edit, "T").get("writes"), None);
}

/// A target the walk cannot place names nothing - a relative write with no cwd, a word naming no place - while an absolute one
/// with no cwd is still named.
#[test]
fn a_target_the_walk_cannot_place_names_nothing() {
    let no_cwd = |command: &str| {
        let mut p = bash("PostToolUse", "", command);
        p.as_object_mut().unwrap().remove("cwd");
        line(&p, "T").remove("writes").unwrap_or(Value::Null)
    };
    assert_eq!(no_cwd("echo x > rel.txt"), Value::Null);
    assert_eq!(no_cwd("echo x > /abs/f.txt"), json!(["/abs/f.txt"]));
    assert_eq!(
        writes("PostToolUse", "/w", r#"echo x > "$(cat where)/f""#),
        Value::Null
    );
}

/// 451 T96: a Python program run from a heredoc or `-c` names the files its literals write, resolved where it runs - T84's
/// `p='...status.rs'; s=open(p).read() ... open(p,'w').write(s)`, a `cd` before a `-c` `write_text`, a `Path('a') / 'b'` join - each
/// an existing file at the call's end; not a literal it only reads (`open('read.rs').read()`), one naming no file (`'w'`, `'utf-8'`)
/// or a directory, one joined onto a base the program computes (`Path(sys.argv[1]) / 'plan.rs'`), nor any literal of a program
/// `py_c` judges a read. The walk's own writes keep their place: a redirect's file before the program's.
#[test]
fn a_python_programs_literal_writes_are_named() {
    let d = clone("writes-python");
    let c = std::fs::canonicalize(&*d).unwrap();
    let c = c.to_string_lossy();
    std::fs::create_dir_all(d.join("sub")).unwrap();
    for f in ["plan.rs", "read.rs", "sub/status.rs"] {
        std::fs::write(d.join(f), "x").unwrap();
    }
    let heredoc = "python3 -I - <<'EOF'\np='plan.rs'; s=open(p, encoding='utf-8').read()\nopen(p,'w').write(s.replace('a','b'))\nEOF";
    assert_eq!(
        writes("PostToolUse", &c, heredoc),
        json!([format!("{c}/plan.rs")])
    );
    let dash_c =
        r#"cd sub && python3 -c "from pathlib import Path; Path('status.rs').write_text('x')""#;
    assert_eq!(
        writes("PostToolUse", &c, dash_c),
        json!([format!("{c}/sub/status.rs")])
    );
    let joined = "python3 - <<'EOF'\nfrom pathlib import Path\n(Path('sub') / 'status.rs').write_text('y')\nEOF";
    assert_eq!(
        writes("PostToolUse", &c, joined),
        json!([format!("{c}/sub/status.rs")])
    );
    let read_one = "echo x > out.txt; python3 - <<'EOF'\ns = open('read.rs').read()\nopen('plan.rs', 'w').write(s)\nopen('sub', 'a')\nEOF";
    assert_eq!(
        writes("PostToolUse", &c, read_one),
        json!([format!("{c}/out.txt"), format!("{c}/plan.rs")])
    );
    let computed = "python3 - x <<'EOF'\nimport sys\nfrom pathlib import Path\n(Path(sys.argv[1]) / 'plan.rs').write_text('z')\nEOF";
    assert_eq!(writes("PostToolUse", &c, computed), Value::Null);
    let reads = r#"python3 -c "print(open('plan.rs').read())""#;
    assert_eq!(writes("PostToolUse", &c, reads), Value::Null);
}

/// The line `append` writes to the log carries the field.
#[test]
fn the_logged_line_carries_the_writes() {
    let d = clone("writes-log");
    let c = std::fs::canonicalize(&*d).unwrap();
    let c = c.to_string_lossy();
    let p = bash("PostToolUse", &c, "sed -i s/a/b/ rust/x.rs");
    let log = append(&p, "T", Path::new("/"), &none).unwrap();
    assert_eq!(last_line(&log)["writes"], json!([format!("{c}/rust/x.rs")]));
}
