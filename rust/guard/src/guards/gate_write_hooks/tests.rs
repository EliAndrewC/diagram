//! The guard on a stand-in `/proc` and an `sh` stand-in for the gate's tree check, which says "unseen" while `unseen` exists
//! (`tests/hooks/test-gate-write-hooks.sh`, replayed through the shim, is the verdict).

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{decide, file_named, judge, own_args, top_of, Ctx};
use crate::guards::finished_run_hooks::runs::Procs;
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

struct World {
    top: PathBuf,
    proc: PathBuf,
    _root: crate::shared::tempdir::TempDir,
}

fn world(tag: &str) -> World {
    crate::shared::log::quiet();
    let root = crate::shared::tempdir::TempDir::new(&format!("guard-gate-write-{tag}"));
    let top = root.join("tree");
    std::fs::create_dir_all(top.join("scripts/gates")).unwrap();
    std::fs::create_dir_all(top.join("l7r/x")).unwrap();
    std::fs::create_dir_all(root.join("proc")).unwrap();
    let t = top.canonicalize().unwrap();
    assert!(ask(
        Path::new("/"),
        "git",
        &["init", "-q", &t.to_string_lossy()],
        ""
    )
    .ok());
    crate::guards::write_executable(
        &t.join("scripts/gates/l7r-gate.sh"),
        &format!("#!/bin/sh\n[ -f {}/unseen ]\n", t.display()),
    );
    World {
        top: t,
        proc: root.join("proc"),
        _root: root,
    }
}

impl World {
    fn make(&self, pid: u32, program: &str, target: &str, cwd: &Path) {
        let d = self.proc.join(pid.to_string());
        std::fs::create_dir_all(&d).unwrap();
        std::fs::write(d.join("cmdline"), format!("{program}\0{target}\0")).unwrap();
        std::os::unix::fs::symlink(cwd, d.join("cwd")).unwrap();
    }

    fn run(&self, tool: &str, input: &Value) -> Vec<Answer> {
        self.run_at(tool, input, "")
    }

    fn run_at(&self, tool: &str, input: &Value, cwd: &str) -> Vec<Answer> {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: json!({"tool_name": tool, "tool_input": input, "cwd": cwd}),
        };
        let s = Session::from_input(&e.input);
        judge(
            &e,
            &s,
            &Ctx {
                procs: Procs {
                    root: self.proc.clone(),
                    mine: 99_999,
                },
                top: self.top.clone(),
            },
        )
    }

    fn bash(&self, cmd: &str) -> Vec<Answer> {
        self.run("Bash", &json!({"command": cmd}))
    }

    fn file(&self, rel: &str) -> String {
        self.top.join(rel).to_string_lossy().into_owned()
    }
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn nothing_is_refused_with_no_gate_running_here() {
    let w = world("idle");
    assert_eq!(top_of(Path::new("/proc/self")), Path::new("/proc/self"));
    assert_eq!(top_of(&w.top.join("l7r/x")), w.top);
    assert!(w.bash("git commit -qm x").is_empty());
    w.make(50, "make", "done", Path::new("/elsewhere"));
    w.make(51, "/usr/bin/python3", "make done", &w.top);
    assert!(w.bash("git commit -qm x").is_empty());
}

#[test]
fn a_running_gate_refuses_a_change_it_would_see() {
    let w = world("gate");
    w.make(60, "/usr/bin/make", "done", &w.top);
    let refusal = w.bash("git add -A");
    assert!(
        refused(&refusal, "while this tree's `make done` runs")
            && refused(&refusal, "make verify-wait")
    );
    assert!(refused(
        &w.bash("make tick F=1 T=T1"),
        "make tick (it writes a tracked record)"
    ));
    assert!(refused(
        &w.bash("make record-checked X=1"),
        "make record-checked"
    ));
    // feature 451 T02: the target the one make detector reads, never a word of an argument
    assert!(refused(
        &w.bash("timeout 60 make accept X=1"),
        "make accept (it writes a tracked record)"
    ));
    assert!(w.bash("make land T=T1 NOTE=tick").is_empty());
    assert!(w.bash("tail -3 log").is_empty() && w.bash("make append LINE=x").is_empty());
    assert!(w.run("Read", &json!({"file_path": "/x"})).is_empty());
    assert!(w
        .run(
            "Edit",
            &json!({"file_path": "/outside/a.txt", "old_string": "a", "new_string": "b"})
        )
        .is_empty());
}

#[test]
fn what_the_gate_does_not_see_passes() {
    let w = world("unseen");
    w.make(60, "gmake", "--no-print-directory done", &w.top);
    std::fs::write(w.top.join("l7r/x/m.py"), "a a\n").unwrap();
    let edit = json!({"file_path": w.file("l7r/x/m.py"), "old_string": "a", "new_string": "b"});
    assert!(refused(&w.run("Edit", &edit), "an Edit of l7r/x/m.py"));
    assert!(refused(
        &w.bash("git commit -qm x"),
        "a change the gate sees"
    ));
    std::fs::write(w.top.join("unseen"), "").unwrap();
    assert!(w.run("Edit", &edit).is_empty());
    let all = json!({"file_path": w.file("l7r/x/m.py"), "old_string": "a", "new_string": "b", "replace_all": true});
    assert!(w.run("Edit", &all).is_empty());
    assert!(w
        .run(
            "Write",
            &json!({"file_path": w.file("dev/r.json"), "content": "{}"})
        )
        .is_empty());
    assert!(w.bash("git commit -qm x").is_empty());
    assert!(refused(
        &w.run("NotebookEdit", &json!({"notebook_path": w.file("n.ipynb")})),
        "an NotebookEdit of n.ipynb"
    ));
    assert!(refused(
        &w.run(
            "Edit",
            &json!({"file_path": w.file("gone.py"), "old_string": "a", "new_string": "b"})
        ),
        "an Edit of gone.py"
    ));
}

#[test]
fn the_escape_needs_a_reason() {
    let g = world("escape-gate");
    g.make(60, "make", "done", &g.top);
    assert!(g
        .bash("GATE_WRITE_OK=\"a deliberate fix for the gate\" git commit -qm x")
        .is_empty());
    assert!(refused(
        &g.bash("git commit -qm x  # GATE_WRITE_OK"),
        "with no reason"
    ));
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}

/// `f`'s answer, or a failure once it runs past 20 s (feature 449 T185: a quadratic search, or a scan over an error it repeats, must
/// fail the test rather than hang it).
fn within<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    let _run = std::thread::spawn(move || tx.send(f()));
    rx.recv_timeout(std::time::Duration::from_secs(20))
        .expect("the search ran past its bound")
}

/// A `git commit` or a `make tick` after many `git` or `make` words (feature 449 T185): unlimited, each pattern tried every trigger to its
/// segment's end, its time the square of their count (24 s on 100 KB, measured 2026-11-18, scratchpad t185/sizecurve.log), and at `fancy_regex`'s old limit it erred and
/// read as no write; each now starts at its segment's first trigger.
#[test]
fn a_write_after_many_triggers_is_seen_in_linear_time() {
    let git = format!("{}; git commit -m x", "git x ".repeat(40_000));
    let make = format!("{}; make tick F=1", "make x ".repeat(40_000));
    let found = within(move || {
        (
            super::GIT_WRITE.is_match(&git).ok(),
            crate::shared::make::invoked(&make)
                .into_iter()
                .find(|t| super::MAKE_WRITE.contains(&t.as_str())),
        )
    });
    assert_eq!(found, (Some(true), Some("tick".to_owned())));
}

/// 451 T33: a SHELL write into the tree is refused while its gate runs, as an Edit and a commit are - on 2026-11-20 a builder's
/// `git apply` and `cp` of guard files under T34's `make land` put unfinished code under its gate - asked of the same tree check;
/// a write outside the tree, into `.git` or a path git ignores, and every read, pass.
#[test]
fn a_running_gate_refuses_a_shell_write_into_the_tree() {
    let w = world("shell");
    w.make(
        60,
        "/usr/bin/make",
        "--no-print-directory done NO_CUTOFF=1",
        &w.top,
    );
    std::fs::write(w.top.join(".gitignore"), "build/\n").unwrap();
    std::fs::write(w.top.join("l7r/x/a.py"), "a\n").unwrap();
    let run_git = |args: &[&str]| {
        let mut all = vec![
            "-C",
            w.top.to_str().unwrap(),
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
        ];
        all.extend_from_slice(args);
        assert!(ask(Path::new("/"), "git", &all, "").ok());
    };
    run_git(&["add", "-A"]);
    run_git(&["commit", "-qm", "a"]);
    let top = w.top.display().to_string();
    for (cmd, rel) in [
        ("git apply /tmp/p.patch".to_owned(), "."),
        (format!("git -C {top} apply /tmp/p.patch"), "."),
        ("cp /tmp/x l7r/x/a.py".to_owned(), "l7r/x/a.py"),
        ("cp /tmp/x l7r/x/new.py".to_owned(), "l7r/x/new.py"),
        ("mv l7r/x/a.py /tmp/a.py".to_owned(), "l7r/x/a.py"),
        ("echo x | tee l7r/x/a.py".to_owned(), "l7r/x/a.py"),
        (
            "echo x | tee -a /tmp/log l7r/x/a.py".to_owned(),
            "l7r/x/a.py",
        ),
        ("echo x > l7r/x/a.py".to_owned(), "l7r/x/a.py"),
        (
            "cd l7r && cat >> x/a.py <<'EOF'\nx\nEOF".to_owned(),
            "l7r/x/a.py",
        ),
        ("sed -i s/a/b/ l7r/x/a.py".to_owned(), "l7r/x/a.py"),
        // a real write behind more than 120 characters of prefixes is still refused (451 T90)
        (
            format!("A={} cp /tmp/x l7r/x/a.py", "a".repeat(130)),
            "l7r/x/a.py",
        ),
        (format!("A={} git apply /tmp/p.patch", "a".repeat(130)), "."),
        // a loop's body writes as its command does (451 T79)
        (
            "for f in l7r/x/a.py; do sed -i s/a/b/ $f; done".to_owned(),
            "l7r/x/a.py",
        ),
        (format!("cp /tmp/x {top}/l7r/x/a.py"), "l7r/x/a.py"),
        // a Python program that writes, judged by the files it names
        (
            "python3 - <<'EOF'\nopen('l7r/x/a.py', 'w').write('x')\nEOF".to_owned(),
            "l7r/x/a.py",
        ),
        (
            "cd l7r && python3 -c \"open('x/a.py','w').write('x')\"".to_owned(),
            "l7r/x/a.py",
        ),
    ] {
        let got = w.bash(&cmd);
        let named = refused(&got, &format!("a shell write of {rel}"));
        assert!(named && refused(&got, "make verify-wait"), "{cmd}: {got:?}");
    }
    for cmd in [
        "echo x | tee /tmp/t33-gate-a".to_owned(),
        "cp l7r/x/a.py /tmp/b".to_owned(),
        "python3 -c \"print(open('l7r/x/a.py').read())\"".to_owned(),
        "make verify-wait".to_owned(),
        // a make or a touch led by a keyword or `timeout N` is still the make or the touch (451 T79's third round: 38 of the ux
        // replay's commands, and `timeout 60 make task-add` at HEAD, were refused as a shell write of `.`, measured 2026-11-21)
        "for F in a.md; do make append FILE=$F LINE=b; done".to_owned(),
        "if true; then touch l7r/x/a.py; fi".to_owned(),
        "timeout 60 make append LINE=x".to_owned(),
        // a make behind more than the segment's 120 kept characters of prefixes is still the make (451 T90: T79's
        // `L7R_FEATURE_DIRECTORY=... make rust-test` was refused as a shell write of `.`, measured 2026-11-21)
        format!("A={} B={} make append LINE=x", "a".repeat(80), "b".repeat(80)),
        format!("env A={} timeout 60 make append LINE=x", "a".repeat(130)),
        "git status --porcelain".to_owned(),
        "git log --oneline | head -3".to_owned(),
        "git push".to_owned(),
        "git diff --output=/tmp/d.patch".to_owned(),
        "ls l7r > /dev/null 2>&1".to_owned(),
        "echo x > build/out.log".to_owned(),
        "echo x > .git/t33-scratch".to_owned(),
        format!("cd /tmp && cp {top}/l7r/x/a.py b.py"),
        "python3 - <<'EOF'\ns = open('l7r/x/a.py').read()\nopen('/tmp/t33-gate-b', 'w').write(s)\nEOF".to_owned(),
        "python3 - <<'EOF'\nopen('build/x.log', 'w').write('x')\nEOF".to_owned(),
    ] {
        assert!(w.bash(&cmd).is_empty(), "{cmd}");
    }
    let elsewhere = w.run_at("Bash", &json!({"command": "cp a.py b.py"}), "/tmp");
    assert!(elsewhere.is_empty());
    std::fs::write(w.top.join("unseen"), "").unwrap();
    assert!(w.bash("cp /tmp/x l7r/x/a.py").is_empty());
}

/// 451 T33's round-3 gate replay (1,134 rows under a stand-in `make done` in the replay mirror, measured 2026-11-20): of the 104
/// rows the shell-write check newly refused, these shapes write OUTSIDE the tree and were refused for a word that is not where
/// they write - a mode read as a file, the text between two string literals, an f-string's placeholder, a URL, an anchor, and a
/// literal joined onto a base the guard cannot resolve (`sys.argv[1]`, a temporary directory, a constant imported).
#[test]
fn a_running_gate_lets_through_what_writes_outside_the_tree() {
    let w = world("outside");
    w.make(
        60,
        "/usr/bin/make",
        "--no-print-directory done NO_CUTOFF=1",
        &w.top,
    );
    let py = |body: &str| format!("python3 - <<'EOF'\n{body}\nEOF");
    for cmd in [
        // refusals#124, #132, window#256
        "chmod +x /tmp/t33-gate-x.sh".to_owned(),
        "chmod 755 /tmp/t33-gate-x.sh".to_owned(),
        // main-tree#169, window#71, #275: the placeholder's base is a shell variable naming another tree
        py("C = '/tmp/c'\nopen(f\"{C}/l7r/x/a.py\", 'w').write('x')"),
        py("import glob\nfor f in glob.glob(f\"{SK}/pool/*/*.json\"):\n    open(f, 'w').write('x')"),
        // refusals#144, window#29, #280, #299: the text between two literals
        py("a = s.split(\",\")[0].split(\".\")\nopen('/tmp/t33-o', 'w').write(a)"),
        py("t = re.sub(r'<b>', \"\", s).replace(\".join(u[\", \"\")\nopen('/tmp/t33-o', 'w').write(t)"),
        // window#170, main-tree#43: a URL and an anchor
        py("u = 'https://doi.org/10.1002/x.html'\nopen('/tmp/t33-o', 'w').write(u)"),
        py("a = 'vegetation.md#fn-3'\nopen('/tmp/t33-o', 'w').write(a)"),
        // window#175, #176, #298: joined onto argv
        "python3 - /tmp/d <<'EOF'\nimport pathlib, sys\np = pathlib.Path(sys.argv[1]) / \"spec.md\"\np.write_text('x')\nEOF"
            .to_owned(),
        "python3 - /tmp/d <<'EOF'\nimport pathlib, sys\npathlib.Path(sys.argv[1], 'scripts', 'a.sh').write_text('x')\nEOF"
            .to_owned(),
        // window#68, #69: joined onto a temporary directory
        py("import pathlib, tempfile\nd = pathlib.Path(tempfile.mkdtemp())\n(d / \"a.py\").write_text('x')"),
        // ... past 200 characters of program before it (the context `joined_on` reads)
        py(&format!(
            "import pathlib, tempfile\n# {}\nd = pathlib.Path(tempfile.mkdtemp())\n(d / \"a.py\").write_text('x')",
            "x".repeat(250)
        )),
        // window#358: joined onto a constant imported
        py("import pathlib\nfrom m import RESEARCH_DIR\nsrc = pathlib.Path(RESEARCH_DIR, \"SOURCES.html\").read_text()\nopen('/tmp/t33-o', 'w').write(src)"),
        // window#280, #358 (round 4): a regex's or a string method's text
        py("import re\nn = len(re.findall(r\"summary.only\", s))\nopen('/tmp/t33-o', 'w').write(str(n))"),
        py("for f in fs:\n    if f.endswith(\".html\"):\n        open('/tmp/t33-o', 'a').write(f)"),
        py("t = s.replace('l7r/x/a.py', 'l7r/x/b.py')\nopen('/tmp/t33-o', 'w').write(t)"),
        // window#358 (after5): a literal compared
        py("for f in fs:\n    if f == \"SOURCES.html\" or f != 'a.py':\n        open('/tmp/t33-o', 'a').write(f)"),
        // window#53: a module loaded from a file is read; the program writes its stdout elsewhere
        "python3 - > /tmp/t33-ctx.txt <<'EOF'\nimport importlib.util\ns = importlib.util.spec_from_file_location('m', 'l7r/x/a.py')\nprint(s)\nEOF"
            .to_owned(),
        // parse#171, #173, refusals#88: the commit-or-add rule reads git's subcommand, not the word `add` anywhere in the segment
        "git notes add -m x".to_owned(),
        "git worktree add --detach /tmp/t33-gate-wt".to_owned(),
        "git remote add t33 /tmp/t33-src".to_owned(),
        "python3 -c 'moved = set(); moved.add(1)'; git status".to_owned(),
        // a stash's read forms write nothing (`stash` is in the walk's GIT_WRITES)
        "git stash list".to_owned(),
        "git stash show -p".to_owned(),
        // a ref's write past git's own options, as push, tag and branch are let through
        "git --no-pager push origin main".to_owned(),
        // window#72: a literal handed to a function of the program's own is placed where the function puts it, which the gate
        // does not read - here onto a base of its own, outside the tree - so it fails open (round 2's NOT LEGITIMATE ruling)
        py("R = \"/tmp/t33-r\"\ndef edit(rel, old, new, regex=False):\n    p = f\"{R}/{rel}\"; s = open(p, encoding=\"utf-8\").read()\n    open(p, \"w\", encoding=\"utf-8\").write(s.replace(old, new, 1))\nedit(\"vegetation.html\", 'a (b) \\'c\\'', \"d\")\nedit(\"citations/buildings.html\",\n     '<a href=\"x\">', f'<a href=\"{R}\">')"),
        // window#172's shape: the function writes the literal where the shell stands, INTO the tree - unread, so it fails open
        // with the rest (Found and left, T49)
        py("def edit(p):\n    open(p, 'w').write('x')\nedit('l7r/x/b.py')"),
    ] {
        let got = w.bash(&cmd);
        assert!(got.is_empty(), "{cmd}: {got:?}");
    }
    // the rule still refuses git's own commit and add, past its options
    for cmd in ["git -C . commit -m x", "git --no-pager add -A"] {
        let got = w.bash(cmd);
        assert!(!got.is_empty(), "{cmd}: {got:?}");
    }
    // still refused: a literal the program writes where it stands, joined or bare, one handed to a library's function, one
    // outside the call of a function the program defines, and one after a `def` or a call named only in a string or a comment
    // (window#220's `s.index("def brook_skirt(")`, a heredoc patching Python source)
    for cmd in [
        py("s = open('/tmp/a').read()\ni = s.index(\"def f(\")\nopen('l7r/x/b.py', 'w').write(s)"),
        py("def f(p):\n    pass\n# f(\nopen('l7r/x/b.py', 'w').write('x')"),
        py("import pathlib\n(pathlib.Path('l7r') / 'x.py').write_text('x')"),
        py("open('l7r/x/b.py', 'w').write('x')"),
        py("import shutil\nshutil.copy('/tmp/a', 'l7r/x/b.py')"),
        py("def edit(p):\n    pass\nedit('/tmp/a')\nopen('l7r/x/b.py', 'w').write('x')"),
        py("def edit(p):\n    pass\nx.edit('l7r/x/b.py')\nopen(x, 'w')"),
        "chmod +x l7r/x/a.py".to_owned(),
    ] {
        let got = w.bash(&cmd);
        assert!(refused(&got, "a shell write of l7r"), "{cmd}: {got:?}");
    }
}

/// 451 T118 (T51's probes, `/tmp/t51/probe-stdin.jsonl`, refused here on 2026-11-21): a running gate lets through a program that
/// reads through a join (window#306), runs a hook's argv list bound to a name (t67's `corpus.py`), tests a dotted word (window#305,
/// t46's `resid.py`) or names a directory (t79's `stream.py`) - and still refuses one that writes through a join, writes a new
/// file it names by its extension, or writes each literal a `for` iterates.
#[test]
fn a_running_gate_lets_through_a_read_a_run_a_test_and_a_directory() {
    let w = world("t118");
    std::fs::create_dir_all(w.top.join("tests/hooks/fixtures")).unwrap();
    std::fs::create_dir_all(w.top.join("scripts/hooks")).unwrap();
    w.make(61, "make", "done", &w.top);
    let py = |body: &str| format!("python3 - <<'EOF'\n{body}\nEOF");
    let fx = w.file("tests/hooks/fixtures");
    for cmd in [
        py("import pathlib\nroot = pathlib.Path('.')\nhook = (root / \"scripts\" / \"house-style-hooks.sh\").read_text()\nopen('/tmp/t118-o', 'w').write(hook)"),
        py("import subprocess\nold = ['scripts/gates/l7r-gate.sh', '--only', 'x']\nnew = ['scripts/hooks/l7r-guard.sh']\na = subprocess.run(old, input=d)\nv = [subprocess.run(g) for g in (old, new)]\nopen('/tmp/t118-o', 'w').write(a)"),
        py("if 'plan.md' in cmd and 'static.log' not in t and s.endswith(('.log', '.out')): pass\nAB = {\"e.g\", \"i.e\"}\nif w in {\"e.g\", \"i.e\"}: pass\nopen('/tmp/t118-o', 'w')"),
        py(&format!("import json\nFX = '{fx}'\nd = json.load(open(f\"{{FX}}/a.json\"))\nopen('/tmp/t118-o', 'w').write(d)")),
        py("import os\nd = 'tests/hooks/fixtures'\nn = len(os.listdir(d))\nopen('/tmp/t118-o', 'w').write(str(n))"),
        // window#63: a directory beside no write the program computes
        py("import sys\nsys.path.insert(0, 'scripts')\nopen('/tmp/t118-o', 'w').write('x')"),
    ] {
        let got = w.bash(&cmd);
        assert!(got.is_empty(), "{cmd}: {got:?}");
    }
    for (cmd, file) in [
        (
            py("import pathlib\nroot = pathlib.Path('.')\n(root / 'l7r' / 'x.py').write_text('x')"),
            "l7r/x.py",
        ),
        (py("open('l7r/x/new.py', 'w').write('x')"), "l7r/x/new.py"),
        (
            py("for f in ['l7r/x/a.md', 'l7r/x/b.md']:\n    open(f, 'w')"),
            "l7r/x/a.md",
        ),
        // window#170 and refusals#144: a directory beside a write the program computes, which can land under it
        (
            py("import pathlib\nR = pathlib.Path('l7r')\ndef put(path):\n    p = R / path\n    p.write_text('x')\nput('x/a.py')"),
            "l7r ",
        ),
        (
            py("import pathlib\nfor p in pathlib.Path('l7r').rglob('*.py'):\n    p.write_text('x')"),
            "l7r ",
        ),
    ] {
        let got = w.bash(&cmd);
        let words = format!("a shell write of {file}");
        assert!(refused(&got, &words), "{cmd}: {got:?}");
    }
}

/// 451 T118: gate-write's file test takes a file - one there, or a name with an extension it would make - and a directory only
/// beside a write the program computes; never a word with no extension that is not there.
#[test]
fn the_file_test_takes_a_file_not_a_directory() {
    let w = world("t118-file");
    std::fs::write(w.top.join("Makefile"), "x").unwrap();
    std::fs::create_dir_all(w.top.join("tests/hooks.d")).unwrap();
    let cases = [
        ("Makefile", true),
        ("l7r/x/new.py", true),
        ("l7r/x", false),
        ("tests/hooks.d", false),
        ("tests", false),
        ("utf8", false),
    ];
    for (rel, want) in cases {
        let got = file_named(&w.file(rel), &|| false);
        assert_eq!(got, want, "{rel}");
    }
    let computed = [("l7r/x", true), ("tests/hooks.d", true), ("utf8", false)];
    for (rel, want) in computed {
        let got = file_named(&w.file(rel), &|| true);
        assert_eq!(got, want, "{rel}");
    }
}

/// 451 T33 (window#72): `own_args` blanks the strings of a call to a function the program defines, to its closing parenthesis
/// past nested calls, comments, escapes and triple quotes, and leaves every other literal - a method of the same name, a string
/// outside the call - as it was; with no `def` the program is untouched.
#[test]
fn a_literal_handed_to_the_programs_own_function_is_blanked() {
    let body = "def f(a, b='w'):\n    pass\nf(g('ab'), # it's\n  '''x\"y''', \"c\\\"d\", '\u{3010}')\nx.f('k')\nopen('z')";
    let want = "def f(a, b='$'):\n    pass\nf(g('$$'), # it's\n  '''$$$''', \"$$$$\", '$$$')\nx.f('k')\nopen('z')";
    assert_eq!(own_args(body), want);
    // a string the line ends before it closes, and a call that never closes, fail open to the end
    assert_eq!(
        own_args("def f(a): pass\nf('ab\n'c"),
        "def f(a): pass\nf('$$\n'$"
    );
    assert_eq!(own_args("open('a.py', 'w')"), "open('a.py', 'w')");
    // a `def` or a call inside a string or a comment is neither
    let named = "s.index(\"def f(\")\nt = 'f(' # f(\nopen('a.py')";
    assert_eq!(own_args(named), named);
}

/// 451 T295: a head's command is read past its wrappers and their options, by its name however spelled.
#[test]
fn a_head_is_read_past_its_wrappers_and_their_options() {
    use super::head_of;
    assert_eq!(head_of("timeout -k 5 60 make quick"), ("make", ""));
    assert_eq!(head_of("env -i /usr/bin/make x"), ("make", ""));
    assert_eq!(
        head_of("sudo -u x \\git -C /x -c a=b commit -m y"),
        ("git", "commit")
    );
    assert_eq!(head_of("/usr/bin/git status"), ("git", "status"));
    assert_eq!(head_of("/tmp/mygit commit"), ("mygit", ""));
    assert_eq!(head_of("env"), ("", ""));
}
