//! The decider on the suite's shapes (`tests/hooks/test-readme-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::{json, Value};

use super::{decide, hit};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

/// The tree the cases are judged against, and a clone of it.
const MAIN: &str = "/repo";
const CLONE: &str = "/repo/.clones/c";

fn event(tool: &str, input: &Value) -> Event {
    crate::shared::log::quiet();
    Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "tool_input": input}),
    }
}

/// A Bash call standing in `standing` ("" for an event with no `cwd`).
fn at(cmd: &str, standing: &str) -> Option<String> {
    let mut e = event("Bash", &json!({"command": cmd}));
    if !standing.is_empty() {
        e.input["cwd"] = json!(standing);
    }
    hit(&e, MAIN, "/home/u")
}

fn bash(cmd: &str) -> Option<String> {
    at(cmd, CLONE)
}

#[test]
fn a_write_of_a_readme_is_a_hit_and_a_read_or_mention_is_not() {
    let tool = |name: &str, path: &str| hit(&event(name, &json!({"file_path": path})), MAIN, "/");
    assert_eq!(tool("Write", "a/README.md").as_deref(), Some("a/README.md"));
    assert_eq!(tool("Edit", "readme").as_deref(), Some("readme"));
    assert_eq!(tool("Write", "a/READMEX.md"), None);
    assert_eq!(
        tool("Write", "/repo/.clones/c/x/../README.md").as_deref(),
        Some("/repo/.clones/c/x/../README.md")
    );
    // a file tool's README outside the tree, as a command's (451 T67)
    assert_eq!(tool("Write", "/tmp/scratch/README.md"), None);
    assert_eq!(
        bash("echo x > dev/README.md").as_deref(),
        Some("/repo/.clones/c/dev/README.md")
    );
    assert!(bash("sed -i s/a/b/ README.md").is_some());
    assert!(bash("printf x | tee -a docs/README").is_some());
    assert!(bash("cp a README.txt").is_some());
    assert!(
        bash("python3 -c \"import pathlib; pathlib.Path('x/README.md').write_text('y')\"")
            .is_some()
    );
    assert_eq!(bash("cat README.md"), None);
    assert_eq!(bash("grep -n x README.md"), None);
    assert_eq!(
        hit(
            &Event {
                name: "PreToolUse".to_owned(),
                input: json!({})
            },
            MAIN,
            "/"
        ),
        None
    );
}

#[test]
fn the_destination_in_the_tree_is_judged_never_a_name_the_command_holds() {
    // 451 T67's refusal (2026-11-21, T58's builder), its first segments verbatim: the destination a README by name, in /tmp
    assert_eq!(
        bash(
            "cd /tmp/t58/wt && cp rust/guard/src/guards/readme_hooks.rs /tmp/t58/readme.keep && printf '\\n#[allow(dead_code)]\\n' \
             >> rust/guard/src/guards/readme_hooks.rs && cp /tmp/t58/readme.keep rust/guard/src/guards/readme_hooks.rs"
        ),
        None
    );
    assert_eq!(bash("cp -p docs/README.md /tmp/x.md"), None);
    assert_eq!(
        bash("cp rust/guard/src/guards/readme_hooks.rs rust/guard/x.rs"),
        None
    );
    // 2026-11-17: the sed script names a README, the file it edits is a test's
    assert_eq!(
        bash("sed -i 's/(README 1, docs 2)/(README 1)/' rust/x/tests.rs"),
        None
    );
    // 2026-10-10: a scratch repository's README in /tmp; git's own writes
    assert_eq!(
        bash("d=/tmp/s && mkdir -p $d && cd $d && git init -q && printf 'x\\n' > README && git add README"),
        None
    );
    assert_eq!(bash("git add README.md"), None);
    assert_eq!(
        bash("cat > docs/notes.md <<'EOF'\ncat > docs/README.md\nEOF"),
        None
    );
    // 2026-10-30: a program whose triple-quoted text writes a fixture README; a program that only reads one
    assert_eq!(
        bash("python3 - <<'EOF'\nimport pathlib\npathlib.Path('t.py').write_text('''(tmp / \"README.md\").write_text(\"n\")''')\nEOF"),
        None
    );
    assert_eq!(bash("python3 -c \"print(open('README.md').read())\""), None);
    // 2026-11-07, its shape: a heredoc onto ../parked/README.md from rust/phases
    assert_eq!(
        at(
            "git rm -q tests/py_driver.py; cat > ../parked/README.md <<'EOF'\n# Parked\nEOF",
            "/repo/.clones/c/rust/phases"
        )
        .as_deref(),
        Some("/repo/.clones/c/rust/parked/README.md")
    );
    assert!(at("cp /tmp/x.md /repo/.clones/c/docs/README.md", "/tmp").is_some());
    assert!(at("cd /repo/.clones/c && cp /tmp/x.md docs/README.md", "/tmp").is_some());
    assert!(at("cp /tmp/x.md README.md", "/repo").is_some());
    // an event with no cwd stands in the tree
    assert!(at("cp a.md dev/README.md", "").is_some());
    // what the walk cannot resolve fails closed: a name read from input, a program standing where nothing is known; a variable
    // never set is empty, as bash reads it (451 T79), so its README is `/README.md`, not the tree's
    assert_eq!(
        bash("read NEVER_SET_T67; echo x > $NEVER_SET_T67/README.md").as_deref(),
        Some("> $NEVER_SET_T67/README.md")
    );
    assert_eq!(bash("echo x > $NEVER_SET_T67/README.md"), None);
    assert!(bash("read NEVER_SET_T67; cd $NEVER_SET_T67 && cat > README.md").is_some());
    assert!(bash(
        "read NEVER_SET_T67; cd $NEVER_SET_T67 && python3 -c \"open('README.md', 'w').write('x')\""
    )
    .is_some());
    // ...but a README the unresolved copy only reads is not its destination
    assert_eq!(bash("cp docs/README.md $NEVER_SET/x.md"), None);
    assert_eq!(bash("d=$(mktemp -d) && cp docs/README.md $d/x.md"), None);
    // a README's removal is a write of the GM's file
    assert!(bash("rm docs/README.md").is_some());
}

#[test]
fn a_git_redirect_a_shell_program_and_a_python_program_are_judged_by_where_they_write() {
    let py = |body: &str| {
        bash(&format!(
            "python3 - <<'EOF'\nimport pathlib, sys, os\n{body}\nEOF"
        ))
    };
    assert_eq!(
        bash("git show HEAD:a.md > docs/README.md").as_deref(),
        Some("/repo/.clones/c/docs/README.md")
    );
    assert_eq!(bash("git -C /tmp/s commit -qm x README"), None);
    assert_eq!(
        bash("bash -c 'echo x > docs/README.md'").as_deref(),
        Some("/repo/.clones/c/docs/README.md")
    );
    assert_eq!(bash("/bin/sh -c 'cat README.md'"), None);
    assert_eq!(bash("bash -c 'unclosed"), None);
    // a literal compared or read is no destination; a literal path, alone or joined onto a literal base, is resolved
    assert_eq!(
        py("if name == 'README.md':\n    open('out.txt', 'w').write('x')"),
        None
    );
    assert_eq!(py("print(os.path.exists('README.md'))"), None);
    assert_eq!(
        py("(pathlib.Path('docs') / 'README.md').write_text('x')").as_deref(),
        Some("/repo/.clones/c/docs/README.md")
    );
    assert_eq!(
        py("(pathlib.Path('/tmp/x') / 'README.md').write_text('x')"),
        None
    );
    // joined onto a base the program computes, it is written where nothing is known: the old rule, failing closed
    assert_eq!(
        py("(pathlib.Path(sys.argv[1]) / 'README.md').write_text('x')").as_deref(),
        Some("README.md').write_text")
    );
    // a literal passed on to a helper is no destination; a mktemp directory is scratch
    assert_eq!(
        py("def put(d, rel):\n    open(os.path.join(d, rel), 'w').write('x')\nput(sys.argv[1], 'questions/README.txt')"),
        None
    );
    assert_eq!(
        bash("d=$(mktemp -d -p /tmp/s) && cd $d; echo seed > README; git add README"),
        None
    );
    assert_eq!(bash("cd $(mktemp -d) && echo x > README.md"), None);
    // a README's write held as a one-line string's text is the program's text, as the triple-quoted one is, whichever quote
    // holds it; a string holding no quoted string of its own is still read (an f-string's base the program computes refused)
    assert_eq!(
        py("pathlib.Path('t.py').write_text('(tmp / \"README.md\").write_text(1)')"),
        None
    );
    assert_eq!(
        py("pathlib.Path('t.py').write_text(\"(tmp / \\\"README.md\\\").write_text(1)\")"),
        None
    );
    assert!(py("d = sys.argv[1]\npathlib.Path(f\"{d}/README.md\").write_text('x')").is_some());
    assert!(py("pathlib.Path(\"it's/README.md\").write_text('x')").is_some());
    // a comment's apostrophe opens no string; a string left open at its line's end is left as it is
    assert_eq!(
        py("open('out.txt', 'w').write('x')  # don't name README.md"),
        None
    );
    assert_eq!(
        py("s = 'unterminated README.md\nopen('out.txt', 'w').write(s)"),
        None
    );
}

/// The `.git` files and configs, by path under the fixture's root, as git writes them: a mirror whose origin is a neutral URL (the
/// rule reads the mirror's own), a clone in it, and outside both a builder's worktree of the clone, a clone of the clone and a
/// `file://` clone of that, a repository whose origin is the mirror's by another scheme, a `.git` file naming another's git dir
/// relatively - and, not copies, a repository whose origin only shares the mirror's prefix, a clone of a bare repository of its
/// own, a scratch repository, a malformed `.git` file, two clones of each other and a directory in no repository.
fn copies(root: &std::path::Path) {
    let p = |rel: &str| format!("{}/{rel}", root.display());
    let origin = |url: &str| {
        format!("[core]\n\tbare = false\n[remote \"origin\"]\n\turl = {url}\n[branch \"main\"]\n\tremote = origin\n")
    };
    let mirror = origin("https://example.invalid/owner/project");
    for (rel, text) in [
        ("main/.git/config", mirror.clone()),
        ("main/.clones/c/.git/config", mirror),
        (
            "main/.clones/c/.git/worktrees/wt/commondir",
            "../..\n".to_owned(),
        ),
        (
            "t58/wt/.git",
            format!("gitdir: {}\n", p("main/.clones/c/.git/worktrees/wt")),
        ),
        ("copy/.git/config", origin(&p("main/.clones/c"))),
        (
            "copy2/.git/config",
            origin(&format!("file://{}", p("copy"))),
        ),
        (
            "gh/.git/config",
            origin("git@example.invalid:owner/project.git"),
        ),
        ("sub/.git", "gitdir: ../gh/.git\n".to_owned()),
        (
            "sibling/.git/config",
            origin("https://example.invalid/owner/project-research"),
        ),
        ("bare.git/config", "[core]\n\tbare = true\n".to_owned()),
        ("bare.git/objects/info/packs", String::new()),
        ("frombare/.git/config", origin(&p("bare.git"))),
        ("scratch/.git/HEAD", "ref: refs/heads/main\n".to_owned()),
        ("odd/.git", "not a gitdir line\n".to_owned()),
        ("loop1/.git/config", origin(&p("loop2"))),
        ("loop2/.git/config", origin(&p("loop1"))),
        ("plain/x", String::new()),
    ] {
        let at = root.join(rel);
        std::fs::create_dir_all(at.parent().unwrap_or(root)).unwrap_or_default();
        std::fs::write(at, text).unwrap_or_default();
    }
}

/// A copy of this project anywhere is the tree, known by what its directory is (`copies`, the fixture), never by its path.
#[test]
fn a_copy_of_the_project_anywhere_is_the_tree_known_by_what_it_is() {
    let root = std::env::temp_dir().join(format!("l7r-readme-t67-{}", std::process::id()));
    copies(&root);
    let p = |rel: &str| format!("{}/{rel}", root.display());
    let main = p("main");
    let at = |cmd: &str, standing: &str| {
        let mut e = event("Bash", &json!({"command": cmd}));
        e.input["cwd"] = json!(standing);
        hit(&e, &main, "/home/u")
    };
    let file = |path: &str| hit(&event("Write", &json!({"file_path": path})), &main, "/");
    let clone = p("main/.clones/c");
    // a builder's worktree of the clone (T58's and T11's /tmp/t58/wt): after a cd, by its path, standing in it, by a file tool,
    // by a Python program, and in a directory the command has yet to make
    let wt = p("t58/wt");
    assert_eq!(
        at(
            &format!("cd {wt} && printf 'x\\n' > docs/README.md"),
            &clone
        ),
        Some(format!("{wt}/docs/README.md"))
    );
    assert!(at(&format!("cp /tmp/x.md {wt}/README.md"), "/tmp").is_some());
    assert!(at("echo x > README", &wt).is_some());
    assert!(file(&format!("{wt}/research/README.md")).is_some());
    assert!(at("python3 -c \"open('README.md', 'w').write('x')\"", &wt).is_some());
    assert!(at(
        &format!("mkdir -p {wt}/n/d && echo x > {wt}/n/d/README.md"),
        "/tmp"
    )
    .is_some());
    // the other copies, and the repositories that are not
    let copy = |rel: &str| {
        let got = at(&format!("echo x > {}/README.md", p(rel)), "/tmp");
        (rel.to_owned(), got.is_some())
    };
    let named = |rels: &[&str], is: bool| {
        rels.iter()
            .map(|r| ((*r).to_owned(), is))
            .collect::<Vec<_>>()
    };
    let yes = ["copy", "copy2", "gh", "sub"];
    let no = [
        "sibling", "frombare", "scratch", "odd", "loop1", "plain", "nowhere",
    ];
    assert_eq!(yes.map(copy).to_vec(), named(&yes, true));
    assert_eq!(no.map(copy).to_vec(), named(&no, false));
    assert_eq!(file(&p("scratch/README.md")), None);
    // 2026-10-10's whole command: a scratchpad `git init` repository, no copy
    let pad = p("scratchpad/livetest");
    assert_eq!(
        at(
            &format!("d={pad} && rm -rf $d && mkdir -p $d/specs/399-live-test && cd $d && git init -q && printf 'x\\n' > README && git add README"),
            &clone
        ),
        None
    );
    std::fs::remove_dir_all(&root).unwrap_or_default();
}

/// A work tree the command itself makes is not on disk when the guard reads: judged by what it is a work tree of.
#[test]
fn a_work_tree_the_command_makes_is_judged_by_what_it_copies() {
    let root = std::env::temp_dir().join(format!("l7r-readme-t67-made-{}", std::process::id()));
    copies(&root);
    let p = |rel: &str| format!("{}/{rel}", root.display());
    let (main, clone) = (p("main"), p("main/.clones/c"));
    let at = |cmd: &str, standing: &str| {
        let mut e = event("Bash", &json!({"command": cmd}));
        e.input["cwd"] = json!(standing);
        hit(&e, &main, "/home/u").is_some()
    };
    // a worktree of the tree, where git runs or by its `-C`; a clone of the mirror's origin by another scheme, of a clone by its
    // path past a valued option, of a copy by `file://`, under `-C`; a source the walk cannot resolve, failing closed
    assert!(at(
        "git worktree add --detach /tmp/t99/wt && cd /tmp/t99/wt && echo x > README.md",
        &clone
    ));
    assert!(at(
        &format!("git -C {clone} worktree add /tmp/t99/w2 && echo x > /tmp/t99/w2/README.md"),
        "/tmp"
    ));
    assert!(at("git clone -q git@example.invalid:owner/project.git /tmp/q/y && echo x > /tmp/q/y/README.md", "/tmp"));
    assert!(at(
        &format!("git clone -b main --depth=1 '{clone}' /tmp/q/c && echo x > /tmp/q/c/README.md"),
        "/tmp"
    ));
    assert!(at(
        &format!(
            "git clone file://{} /tmp/q/f && echo x > /tmp/q/f/README.md",
            p("copy")
        ),
        "/tmp"
    ));
    assert!(at(
        &format!(
            "git -C {} clone -q c /tmp/q/r && echo x > /tmp/q/r/README.md",
            p("main/.clones")
        ),
        "/tmp"
    ));
    assert!(at(
        "read NEVER_SET_T67; git clone $NEVER_SET_T67 /tmp/q/u && echo x > /tmp/q/u/README.md",
        "/tmp"
    ));
    // not this project's: a worktree of a scratch repository, a clone of another URL, a scratch clone of a bare repository of its own
    // (the corpus's `mktemp` shape), a clone with no source, and a command that makes no work tree
    assert!(!at(
        &format!(
            "git -C {} worktree add /tmp/q/s && echo x > /tmp/q/s/README.md",
            p("scratch")
        ),
        "/tmp"
    ));
    assert!(!at(
        "git clone -q https://example.invalid/other /tmp/q/o && echo x > /tmp/q/o/README.md",
        "/tmp"
    ));
    assert!(!at(
        "d=$(mktemp -d -p /tmp/q) && cd $d && git init -q --bare remote.git && git clone -q remote.git seed; cd seed; echo seed > README",
        &clone
    ));
    assert!(!at("git clone && echo x > /tmp/q/README.md", "/tmp"));
    assert!(!at(
        "git log --oneline && echo x > /tmp/q/README.md",
        "/tmp"
    ));
    // git's own subcommand only, opening its segment: a word after it, a commit message or a grep naming either is no such call
    let mentions = [
        "git commit -qm \"the clone step\"",
        "git grep -n clone docs",
        "git commit -m \"git clone the tree\"",
        "git log --grep 'worktree add'",
    ]
    .map(|m| at(&format!("{m} && cp a.rs /tmp/q/readme.keep"), &clone));
    assert_eq!(mentions, [false; 4]);
    assert!(at(
        &format!("cd /tmp && git -c user.name=t clone -q {clone} /tmp/q/n && echo x > /tmp/q/n/README.md"),
        "/tmp"
    ));
    std::fs::remove_dir_all(&root).unwrap_or_default();
}

/// A work tree the command makes holds the READMEs written under its place and no other (the plan review's (b)3c, round 2): T67's
/// own cp beside a `git worktree add` passes. The place is the walk's where the call runs - `worktree add`'s path past its valued
/// options, relative to its `-C`; a clone's directory, else the one git names from its source; a variable's as the walk expands it -
/// and one the walk cannot resolve fails closed, every README the command writes counted.
#[test]
fn a_work_tree_the_command_makes_holds_the_readmes_under_its_place() {
    let long = format!(
        "read NEVER_SET_T67; git worktree add $NEVER_SET_T67/{} && echo x > /tmp/q/README.md",
        "d".repeat(120)
    );
    let cases: [(&str, &str, Option<&str>); 27] = [
        // T67's own cp beside the worktree the command adds; a README in that worktree, by its path and after a cd
        ("git worktree add /tmp/t58/wt && cp rust/guard/src/guards/readme_hooks.rs /tmp/t58/readme.keep", CLONE, None),
        ("git worktree add /tmp/t58/wt && echo x > /tmp/t58/wt/README.md", CLONE, Some("/tmp/t58/wt/README.md")),
        ("git worktree add /tmp/t58/wt && cd /tmp/t58/wt && echo x > README.md", CLONE, Some("/tmp/t58/wt/README.md")),
        // a sibling sharing the place's prefix is outside it; a branch's name and a reason are no place; a relative place is its `-C`'s
        ("git worktree add /tmp/t58/wt && echo x > /tmp/t58/wt-notes/README.md", CLONE, None),
        ("git worktree add -b topic --reason=r /tmp/t58/wt && echo x > /tmp/t58/wt/README.md", CLONE, Some("/tmp/t58/wt/README.md")),
        ("git -C /repo/.clones/c worktree add ../../../tmp/q/w && echo x > /tmp/q/w/README.md", "/tmp/a/b/c/d", Some("/tmp/q/w/README.md")),
        // a clone of this repository: a README in its directory refused, one elsewhere outside it passing; with no directory, the one
        // git names from the source, a redirect no directory
        ("git clone -q /repo/.clones/c /tmp/x && echo x > /tmp/x/README.md", "/tmp", Some("/tmp/x/README.md")),
        ("git clone -q /repo/.clones/c /tmp/x && echo x > /tmp/y/README.md", "/tmp", None),
        ("git clone /repo/.clones/c/ && echo x > c/README.md", "/tmp/q", Some("/tmp/q/c/README.md")),
        ("git clone /repo/.clones/c/ && echo x > /tmp/q/README.md", "/tmp/q", None),
        ("git clone /repo/.clones/c >/dev/null && echo x > c/README.md", "/tmp/q", Some("/tmp/q/c/README.md")),
        // a worktree of the clone the command made before it, not yet on disk
        ("git clone -q /repo/.clones/c /tmp/x && git -C /tmp/x worktree add /tmp/y && echo x > /tmp/y/README.md", "/tmp", Some("/tmp/y/README.md")),
        // the corpus's scratch clone of a bare repository of its own, beside a worktree of the tree: its README is the scratch's
        ("git worktree add /tmp/t58/wt && d=$(mktemp -d -p /tmp/q) && cd $d && git init -q --bare remote.git && git clone -q remote.git seed; cd seed; echo seed > README", CLONE, None),
        // failing closed: a place the walk cannot resolve, a worktree with no place, and one past the walk's segment
        ("read NEVER_SET_T67; git worktree add $NEVER_SET_T67/wt && echo x > /tmp/q/README.md", CLONE, Some("/tmp/q/README.md")),
        ("git worktree add && echo x > /tmp/q/README.md", CLONE, Some("/tmp/q/README.md")),
        (&long, CLONE, Some("/tmp/q/README.md")),
        // a clone that is no copy holds nothing, beside one that is
        ("git clone -q /tmp/other /tmp/o && git clone -q /repo/.clones/c /tmp/x && echo x > /tmp/o/README.md", "/tmp", None),
        // a work tree a shell's `-c` program makes, its probe no longer in quoted text: its README refused, a scratch file passing
        ("bash -c \"git worktree add /tmp/w && echo x > /tmp/w/README.md\"", CLONE, Some("/tmp/w/README.md")),
        ("bash -c \"git worktree add /tmp/w && cp a.rs /tmp/readme.keep\"", CLONE, None),
        // ... and the write after the program, the outer command's
        ("bash -c \"git worktree add /tmp/w\" && echo x > /tmp/w/README.md", CLONE, Some("/tmp/w/README.md")),
        // a place or a source by a variable or home, as the walk expands it where the command stands, never under `.`
        ("d=/tmp/t58 && git worktree add $d/wt && echo x > $d/wt/README.md", CLONE, Some("/tmp/t58/wt/README.md")),
        ("WT=/tmp/t58/wt; git worktree add \"$WT\" && cd \"$WT\" && echo x > README.md", CLONE, Some("/tmp/t58/wt/README.md")),
        ("git worktree add ~/wt && echo x > ~/wt/README.md", CLONE, Some("/home/u/wt/README.md")),
        ("d=/tmp/t58 && git worktree add $d/wt && cp a.rs $d/readme.keep", CLONE, None),
        ("S=/repo/.clones/c && git clone $S /tmp/x && echo x > /tmp/x/README.md", "/tmp", Some("/tmp/x/README.md")),
        // a clone with no directory whose source is a variable: the name git gives it is not read before the walk, so failing closed
        ("S=/repo/.clones/c && git clone $S && echo x > c/README.md", "/tmp/q", Some("/tmp/q/c/README.md")),
        ("S=/repo/.clones/c && git clone \"$S\" && echo x > c/README.md", "/tmp/q", Some("/tmp/q/c/README.md")),
    ];
    let got = cases.map(|(cmd, standing, _)| (cmd, at(cmd, standing)));
    let want = cases.map(|(cmd, _, is)| (cmd, is.map(str::to_owned)));
    assert_eq!(got, want);
    // the mirror's origin by URL, with no directory: the one git names from it
    let root = std::env::temp_dir().join(format!("l7r-readme-t67-place-{}", std::process::id()));
    copies(&root);
    let main = format!("{}/main", root.display());
    let url = |write: &str| {
        let cmd = format!("git clone -q git@example.invalid:owner/project.git && echo x > {write}");
        let mut e = event("Bash", &json!({"command": cmd}));
        e.input["cwd"] = json!("/tmp/q");
        hit(&e, &main, "/home/u")
    };
    assert_eq!(
        [url("project/README.md"), url("/tmp/q/README.md")],
        [Some("/tmp/q/project/README.md".to_owned()), None]
    );
    std::fs::remove_dir_all(&root).unwrap_or_default();
}

#[test]
fn the_refusal_and_the_escape() {
    // the session's tree through its `CLONE_MAIN` seam
    let session =
        |e: &Event| Session::with_env(&e.input, |k| (k == "CLONE_MAIN").then(|| MAIN.to_owned()));
    let run = |cmd: &str| {
        let e = event("Bash", &json!({"command": cmd}));
        decide(&e, &session(&e))
    };
    let refused =
        |got: &[Answer], words: &str| matches!(got, [Answer::Refuse(t)] if t.contains(words));
    assert!(refused(
        &run("echo x > README.md"),
        "BLOCKED: writing a README (/repo/README.md)"
    ));
    assert!(run("echo x > README.md  # README_OK: the GM asked for this link table").is_empty());
    assert!(refused(
        &run("echo x > README.md  # README_OK"),
        "with no reason"
    ));
    assert!(run("cp README.md /tmp/x.md").is_empty());
    assert!(run("ls").is_empty());
    let file = event("Write", &json!({"file_path": "README.md"}));
    assert!(refused(&decide(&file, &session(&file)), "(README.md)"));
    let none = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Write"}),
    };
    assert!(decide(&none, &Session::from_input(&none.input)).is_empty());
}

/// 451 T113: a Python program's triple-quoted text nothing closes, forty escapes after its opening - `TRIPLE`, which
/// `program_writes` dropped the text with, took a backslash with the character after it or alone, so its backtracking search tried
/// 2^40 readings, and the guard gave no answer in 10 s (measured 2026-11-21, `/tmp/t113/probe-before.txt`); a lone quote closes the
/// single-quoted reading. Judged in a child under a deadline.
#[test]
fn a_triple_quote_nothing_closes_is_judged_in_time() {
    const CHILD: &str = "L7R_README_TRIPLE_IN_TIME";
    let cmd = format!(
        "python3 - <<'EOF'\nopen('README.md', 'w').write('x')\ns = '''it {} '\nEOF",
        "\\n".repeat(40)
    );
    if std::env::var_os(CHILD).is_some() {
        println!("T113 answered {:?}", bash(&cmd));
        return;
    }
    let (passed, said) = crate::guards::passes_in_time(
        "guards::readme_hooks::tests::a_triple_quote_nothing_closes_is_judged_in_time",
        CHILD,
        10,
    );
    assert!(passed, "the guard did not answer in 10 s: {said}");
    let hit = said.contains("T113 answered Some(\"/repo/.clones/c/README.md\")");
    assert!(hit, "{said}");
}

/// 451 T113: the program's text without its triple-quoted strings is what the pattern it replaced (`TRIPLE`, built here) left with
/// `replace_all`, on every text of up to 5 pieces of a double quote, three, a single quote, three, a backslash, a letter, a newline
/// and a character of two bytes (37,449 texts); the spans themselves are held to the pattern in `shared::shape`'s tests.
#[test]
fn the_text_without_its_triples_is_the_patterns() {
    let pattern =
        crate::shared::regex::build(r#"(?s)"""(?:\\.|(?!""").)*"""|'''(?:\\.|(?!''').)*'''"#)
            .unwrap();
    let pieces = ["\"", "\"\"\"", "'", "'''", "\\", "a", "\n", "é"];
    for text in crate::guards::texts_of(&pieces, 5) {
        let without = super::without_triples(&text);
        assert_eq!(without, pattern.replace_all(&text, "\"\""), "{text:?}");
    }
}
