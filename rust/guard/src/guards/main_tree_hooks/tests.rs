//! The decider on the suite's shapes (`tests/hooks/test-main-tree-hooks.sh`, replayed through the shim, is the verdict).

use std::path::Path;

use serde_json::json;

use super::{decide, judge, mirror};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

fn tree(
    tag: &str,
) -> (
    crate::shared::tempdir::Held<std::path::PathBuf>,
    std::path::PathBuf,
) {
    crate::shared::log::quiet();
    let root = crate::shared::tempdir::TempDir::new(&format!("guard-mt-{tag}"));
    let d = root.join("diagram");
    let clone = d.join(".clones/mine");
    std::fs::create_dir_all(d.join(".git")).unwrap();
    std::fs::create_dir_all(clone.join(".git")).unwrap();
    std::fs::create_dir_all(d.join(".clones/.session-clones")).unwrap();
    std::fs::write(
        d.join(".clones/.session-clones/sid"),
        clone.to_string_lossy().as_bytes(),
    )
    .unwrap();
    (root.hold(d), clone)
}

fn run(cmd: &str, dir: &Path, main: &Path, sid: &str) -> Vec<Answer> {
    let input = json!({"session_id": sid, "cwd": dir.to_string_lossy(), "tool_name": "Bash", "tool_input": {"command": cmd}});
    let mut s = Session::from_input(&input);
    s.main_seam = Some(main.to_string_lossy().into_owned());
    judge(
        &Event {
            name: "PreToolUse".to_owned(),
            input,
        },
        &s,
        Some(dir),
        "/h",
    )
}

#[test]
fn a_write_standing_in_the_mirror_is_moved_to_the_clone() {
    let (m, c) = tree("move");
    let got = run("git commit -q", &m, &m, "sid");
    assert!(
        matches!(&got[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["command"] == format!("cd {} && git commit -q", c.display()) && n.contains("standing in"))
    );
    assert!(run("ls", &m, &m, "sid").is_empty());
    assert!(run("", &m, &m, "sid").is_empty());
}

#[test]
fn naming_the_mirror_and_an_unresolvable_clone_are_refused() {
    let (m, _c) = tree("refuse");
    let named = run(&format!("git -C {} commit", m.display()), &m, &m, "sid");
    assert!(
        matches!(&named[..], [Answer::Refuse(w)] if w.contains("names a path inside the mirror"))
    );
    let unclaimed = run("git commit", &m, &m, "nobody");
    assert!(matches!(&unclaimed[..], [Answer::Refuse(w)] if w.contains("cannot be resolved")));
}

#[test]
fn main_tree_ok_stands_aside_with_a_reason_and_refuses_without() {
    let (m, _c) = tree("escape");
    assert!(run(
        "git commit  # MAIN_TREE_OK: render-sync by hand",
        &m,
        &m,
        "sid"
    )
    .is_empty());
    assert!(
        matches!(&run("git commit  # MAIN_TREE_OK", &m, &m, "sid")[..], [Answer::Refuse(w)] if w.contains("MAIN_TREE_OK with no reason"))
    );
}

#[test]
fn the_mirror_is_the_work_trees_top_cut_at_its_clones() {
    let (m, c) = tree("mirror");
    assert_eq!(mirror(&c.join("x")), Some(m.to_path_buf()));
    assert_eq!(mirror(&m), Some(m.to_path_buf()));
    assert_eq!(mirror(Path::new("/")), None);
    let none = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "git commit"}}),
    };
    assert!(judge(
        &none,
        &Session::from_input(&json!({})),
        Some(Path::new("/")),
        "/h"
    )
    .is_empty());
    assert!(decide(&none, &Session::from_input(&json!({}))).len() <= 1);
}

/// 451 T31: a `python3 -c` that only reads is not a write where the shell stands - the T15 replay's
/// `python3 -c "data = open('$SP/x.html','rb').read() ..."` was refused with no clone to move it to - while a program that
/// writes, a redirect, a `tee`, and a program that runs the tree's own code are still writes.
#[test]
fn a_python_read_standing_in_the_mirror_is_not_a_write_and_a_python_write_still_is() {
    let (m, _c) = tree("pyread");
    let read = "SP=/tmp/sp; python3 -c \"\ndata = open('$SP/x.html','rb').read()\nfor enc in ['utf-8','cp932']:\n    print(enc, len(data.decode(enc, 'replace')))\n\"";
    assert!(run(read, &m, &m, "nobody").is_empty(), "a read refused");
    for read in [
        "python3 -c 'import json; print(json.load(open(\"a.json\", encoding=\"utf-8\"))[\"k\"])'",
        "python3 -c \"import sys,json; print(json.load(sys.stdin).get('x'))\"",
        "python3 -c 'print(1)'",
    ] {
        assert!(run(read, &m, &m, "nobody").is_empty(), "{read}");
    }
    std::fs::create_dir_all(m.join("l7r")).unwrap();
    let refused = |c: &str| matches!(&run(c, &m, &m, "nobody")[..], [Answer::Refuse(w)] if w.contains("cannot be resolved"));
    for write in [
        "python3 -c \"open('o.txt','w').write('x')\"",
        "python3 -c \"open('o.txt', mode='a')\"",
        "python3 -c \"m = 'w'; open('o.txt', m)\"",
        "python3 -c \"import pathlib; pathlib.Path('o').write_text('x')\"",
        "python3 -c \"import os; os.remove('f')\"",
        "python3 -c \"print('$(rm f)')\"",
        "python3 -c 'print(1)' > out.txt",
        "python3 -c 'print(1)' | tee out.txt",
        "python3 -c 'import l7r'",
        "python3 -c 'from . import x'",
        "cd $UNSET && python3 -c 'import json'",
        "python3 -c print",
        // window#61's shape: the heredoc writes, judged by no one, so the command's `-c` read stays D5's write
        "python3 - <<'PY'\nimport pathlib\np = pathlib.Path('hm.py'); p.write_text('x')\nPY\npython3 -c 'print(1)'",
        // parse#72's: a heredoc rewrites a module, a `-c` checks it parses
        "python3 - <<'PYEOF'\nimport pathlib\np=pathlib.Path('f.py')\np.write_text(p.read_text())\nPYEOF\npython3 -c \"import ast,sys; ast.parse(open('f.py').read()); print('parses ok')\"",
    ] {
        assert!(refused(write), "{write}");
    }
}
