//! The decider's parts (`tests/hooks/test-make-only-hooks.sh`, replayed through the shim, and `tests/tooling/test_guard_corpus.py`'s rows are the verdict).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{
    classify, decide, judge, lay, makefile_for, recipes, split_segment, words, wrapped,
    wrapped_modules, Ctx, Token,
};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;

const MAKEFILE: &str = "pack-audit: ## x\n\t@$(RUN).tools.pack_audit $(ARGS)\n# note\nci-status:\n\t$(RUN).ci status $(if $(ROUTE),--route,)\nengine-key:\n\t$(RUN).ci engine-key $(or $(REF),HEAD)\nswitches:\n\t$(SWITCH) show\nmulti:\n\t$(RUN).x a\n\t$(RUN).x b\nnot-run:\n\t@echo hi\nexp: export X=1\n\tignored\nVAR = 1\n\tstray\nci-status:\n\t\n";

fn v(cmd: &str) -> String {
    classify(cmd)
}

#[test]
fn each_verdict_has_its_shape() {
    for (cmd, want) in [
        ("", "ok"),
        ("make quick", "ok"),
        ("make -f /tmp/x y", "foreign-makefile"),
        ("python3 -m l7r.diagram.tools.x", "engine-entry-point"),
        ("cargo test", "bare-cargo"),
        ("~/.cargo/bin/cargo clippy", "bare-cargo"),
        ("make done FULL=1 REF_WHY=x", "inline-override"),
        ("REF_OK=1 make maps", "inline-override"),
        ("echo REF_OK=1", "ok"),
        ("make x Q=1 Q=2", "make-dup-var:Q"),
        ("make x Q=1 R=2", "ok"),
        ("sed -i s/a/b/ scripts/hooks/a-hooks.sh", "guard-write"),
        ("cat > .claude/settings.json", "guard-write"),
        ("tee Makefile", "guard-write"),
        ("sed -i s/a/b/ tests/hooks/test-a-hooks.sh", "ok"),
        ("x = Path('Makefile').write_text(y)", "guard-write"),
        (
            "open('scripts/hooks/a-hooks.sh', 'a').write(x)",
            "guard-write",
        ),
        ("p = Path('Makefile')\np.write_text(x)", "guard-write"),
        ("p = 'Makefile'\nopen(p, 'w')", "guard-write"),
        ("p = 'Makefile'\nopen(p)", "ok"),
        ("make done 2> /tmp/log", "ok"),
        ("ls # GUARD_EDIT_OK: a reason here", "guard-edit-ok"),
    ] {
        assert_eq!(v(cmd), want, "{cmd}");
    }
}

/// PYTEST IS NO LONGER THE GUARD'S (feature 449 T213): its targets left with it, so a run has nothing to be routed to and the branch that
/// refused or rewrote one is gone - and with it T214's defect, a read-only `python3 -I -c` whose string held the word refused as a run.
#[test]
fn a_pytest_command_or_mention_is_left_alone() {
    for cmd in [
        "pytest -q",
        "python3 -m pytest tests/a/test_b.py -k x",
        "x | pytest -q",
        "grep -c \"a|pytest\" f.txt",
        "python3 -I -c 'print(\"pytest\")'",
    ] {
        assert_eq!(v(cmd), "ok", "{cmd}");
    }
}

#[test]
fn a_replacements_binary_is_refused_and_its_wrapper_is_not() {
    assert_eq!(
        v("~/.cache/x/release/l7r-guard --only y PreToolUse"),
        "bare-binary"
    );
    // the tools' own profile (T95)
    assert_eq!(v("~/.cache/x/tool/l7r-gate --version"), "bare-binary");
    assert_eq!(v("target/release/hamlet pool/x.spec.json"), "bare-binary");
    // the checks' and the browser's own programs (feature 449 T93, T146; FR-005)
    assert_eq!(v("~/.cache/x/tool/l7r-rust test --crate y"), "bare-binary");
    assert_eq!(v("~/.cache/x/tool/l7r-browser serve"), "bare-binary");
    assert_eq!(v("scripts/gates/l7r-gate.sh browser crop x"), "ok");
    assert_eq!(v("ls rust/browser/src/l7r-browser-notes"), "ok");
    // the embedder's program (feature 449 T138; FR-005)
    assert_eq!(
        v("~/.cache/x/tool/l7r-embed serve --cache c"),
        "bare-binary"
    );
    assert_eq!(v("l7r-embed serve"), "bare-binary");
    assert_eq!(v("scripts/gates/l7r-gate.sh embed serve --cache c"), "ok");
    assert_eq!(v("ls rust/embed/src/l7r-embed.md"), "ok");
    // the Mode A engine's program (feature 449 T168; FR-005), which `l7r-gate.sh mode-a` builds and runs
    assert_eq!(
        v("~/.cache/x/tool/l7r-mode-a building-programs --check"),
        "bare-binary"
    );
    assert_eq!(v("l7r-mode-a --version"), "bare-binary");
    assert_eq!(
        v("scripts/gates/l7r-gate.sh mode-a building-programs"),
        "ok"
    );
    assert_eq!(v("ls rust/mode_a/src/l7r-mode-a.md"), "ok");
    assert_eq!(v("hamlet x"), "bare-binary");
    assert_eq!(v("scripts/hooks/l7r-guard.sh --version"), "ok");
    assert_eq!(v("git log --grep hamlet"), "ok");
    assert_eq!(v("make hamlet SPEC=x"), "ok");
}

#[test]
fn the_segment_ends_at_an_unquoted_separator() {
    assert_eq!(
        split_segment(" a 'b;c' \"d\\\"e\" ; f"),
        (" a 'b;c' \"d\\\"e\" ", "; f")
    );
    assert_eq!(split_segment("a\\;b"), ("a\\;b", ""));
    assert_eq!(split_segment("&x"), ("", "&x"));
    assert_eq!(split_segment("a 2>&1"), ("a 2>&1", ""));
    assert_eq!(
        words(" a 'b c'\t\"d\"  "),
        [
            ("a".to_owned(), "a".to_owned()),
            ("'b c'".to_owned(), "b c".to_owned()),
            ("\"d\"".to_owned(), "d".to_owned())
        ]
    );
}

#[test]
fn an_entry_point_a_target_wraps_is_rewritten() {
    let ok = |c: &str| wrapped(c, MAKEFILE).unwrap();
    assert_eq!(
        ok("python3 -m l7r.diagram.ci status --route"),
        "make ci-status ROUTE=1"
    );
    assert_eq!(
        ok("python3 -m l7r.diagram.ci status 2>&1 | grep x"),
        "make ci-status 2>&1 | grep x"
    );
    assert_eq!(
        ok("( cd s && python3 -m l7r.diagram.ci engine-key w 2>&1 | head )"),
        "( cd s && make engine-key REF=w 2>&1 | head )"
    );
    assert_eq!(
        ok("python3 -m l7r.diagram.ci engine-key"),
        "make engine-key"
    );
    assert_eq!(
        ok("python3 -m l7r.diagram.tools.pack_audit wip/x.svg"),
        "make pack-audit ARGS=\"wip/x.svg\""
    );
    assert_eq!(
        ok("python3 -m l7r.diagram.tools.pack_audit"),
        "make pack-audit"
    );
    assert_eq!(ok("python3 -m l7r.diagram.switches show"), "make switches");
    let why = |c: &str| wrapped(c, MAKEFILE).unwrap_err();
    assert_eq!(why("ls"), "no engine entry point");
    assert!(why("python3 -m l7r.diagram.none x").contains("`ci` -> `make ci-status`"));
    assert_eq!(
        why("python3 -m l7r.diagram.ci state"),
        "`make ci-status` cannot carry these arguments"
    );
    assert_eq!(
        why("python3 -m l7r.diagram.ci status 'a b'"),
        "the quoted argument 'a b'"
    );
    let quoted = "python3 -m l7r.diagram.tools.pack_audit a$b";
    assert_eq!(
        why(quoted),
        "`make pack-audit` cannot carry these arguments"
    );
    assert_eq!(lay(&["--x".to_owned()], &[Token::Or("V".to_owned())]), None);
}

#[test]
fn the_recipes_are_read_as_make_writes_them() {
    let all = recipes(MAKEFILE);
    assert!(all.iter().any(|(t, l)| t == "multi" && l.len() == 2));
    assert!(!all.iter().any(|(t, _)| t == "exp"));
    let table = wrapped_modules(MAKEFILE);
    assert!(table.contains_key("switches") && !table.contains_key("x"));
}

fn world(tag: &str) -> crate::shared::tempdir::Held<PathBuf> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-makeonly-{tag}"));
    std::fs::write(d.join("a.py"), "x").unwrap();
    std::fs::write(d.join("Makefile"), MAKEFILE).unwrap();
    let held = d.canonicalize().unwrap();
    // the world stands for a project tree (451 T87: under the temp directory a guard file's name is scratch, held only in one)
    crate::shared::env::set("CLONE_MAIN", &held);
    d.hold(held)
}

fn run(cmd: &str, d: &Path) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "cwd": d, "tool_input": {"command": cmd, "description": "kept"}}),
    };
    judge(
        &e,
        &Session::from_input(&e.input),
        &Ctx {
            tree: d.to_path_buf(),
            here: d.to_path_buf(),
        },
    )
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn each_refusal_names_what_to_run() {
    let d = world("refuse");
    for (cmd, words) in [
        ("make x Q=1 Q=2", "sets Q twice"),
        ("cargo test", "make rust-test"),
        ("hamlet x", "make hamlet SPEC="),
        ("make -f x y", "from the repository root"),
        ("python3 -m l7r.diagram.none", "no make target wraps"),
        ("REF_OK=1 make x", "answer the prompt"),
        ("sed -i s/a/b/ Makefile", "a marker INSIDE the text written"),
        ("cd dev && cp /tmp/x switches.json", "make guard-edit FILE="),
    ] {
        assert!(refused(&run(cmd, &d), words), "{cmd}");
    }
    assert!(run("ls", &d).is_empty());
}

/// A write is resolved from where the command starts: the event's `cwd`, else the guard's own directory (T227).
#[test]
fn a_relative_write_is_resolved_from_where_the_command_starts() {
    let d = world("here");
    let at = |cwd: &str, here: &Path| {
        let e = Event {
            name: "PreToolUse".to_owned(),
            input: json!({"tool_name": "Bash", "cwd": cwd, "tool_input": {"command": "cat > settings.json < /tmp/x"}}),
        };
        let ctx = Ctx {
            tree: d.to_path_buf(),
            here: here.to_path_buf(),
        };
        refused(
            &judge(&e, &Session::from_input(&e.input), &ctx),
            "GUARD FILE",
        )
    };
    let claude = d.join(".claude");
    assert!(at(&claude.to_string_lossy(), &d));
    assert!(at("", &claude));
    assert!(!at("", &d));
}

#[test]
fn the_rewrites_and_the_escape() {
    let d = world("rewrite");
    assert!(run("pytest tests/a/test_b.py -q", &d).is_empty());
    let got = run("python3 -m l7r.diagram.ci status", &d);
    assert!(
        matches!(&got[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["command"] == "make ci-status" && n.contains("`python3 -m l7r.diagram.ci` was rewritten to `make ci-status`"))
    );
    assert!(run(
        "sed -i s/a/b/ Makefile # GUARD_EDIT_OK: it fired on correct work",
        &d
    )
    .is_empty());
    assert!(refused(
        &run("sed -i s/a/b/ Makefile # GUARD_EDIT_OK", &d),
        "with no reason"
    ));
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
    let none = Event {
        name: "PreToolUse".to_owned(),
        input: json!({}),
    };
    assert!(decide(&none, &Session::from_input(&none.input)).is_empty());
}

#[test]
fn the_makefile_is_the_trees_the_command_runs_in() {
    let d = world("makefile");
    std::fs::create_dir_all(d.join("sub")).unwrap();
    let tree = world("makefile-tree");
    std::fs::write(tree.join("Makefile"), "from the tree").unwrap();
    assert_eq!(
        makefile_for(&d.join("sub").to_string_lossy(), &tree),
        MAKEFILE
    );
    assert_eq!(makefile_for("", &tree), "from the tree");
    assert_eq!(makefile_for("/", &tree), "from the tree");
}

#[test]
fn an_escape_is_recorded_with_its_reason() {
    let d = world("recorded");
    let why = "it fired on correct work, unique to this firing record test";
    assert!(run(
        &format!("sed -i s/a/b/ Makefile # GUARD_EDIT_OK: {why}"),
        &d
    )
    .is_empty());
    let dir = std::env::var("GUARD_LOG_DIR").unwrap();
    let recorded = std::fs::read_dir(dir).unwrap().flatten().any(|f| {
        let text = std::fs::read_to_string(f.path()).unwrap_or_default();
        text.contains(why) && text.contains("guard-edit-ok")
    });
    assert!(recorded);
}

#[test]
fn text_being_stored_names_a_guard_without_writing_one() {
    assert_eq!(
        v("cat >> /tmp/p.py <<'EOF'\n(root / 'scripts' / 'x-hooks.sh').write_text('y')\nEOF"),
        "ok"
    );
    assert_eq!(v("tee /tmp/p.py <<'EOF'\nopen('Makefile', 'w')\nEOF"), "ok");
    assert_eq!(
        v("cat > /tmp/p <<\"EOF\"\nopen('Makefile', 'w')\nEOF"),
        "ok"
    );
    assert_eq!(v("cat > /tmp/p <<\\EOF\nopen('Makefile', 'w')\nEOF"), "ok");
    assert_eq!(
        v("cat > /tmp/p <<EOF\nopen('Makefile', 'w')\nEOF"),
        "guard-write"
    );
    assert_eq!(
        v("python3 - <<'EOF'\n(root / 'x-hooks.sh').write_text('y')\nEOF"),
        "guard-write"
    );
    assert_eq!(v("cat >> Makefile <<'EOF'\nx\nEOF"), "guard-write");
    assert_eq!(
        v("cat <<'EOF' | python3\nopen('Makefile', 'w')\nEOF"),
        "guard-write"
    );
    assert_eq!(
        v("cat > /tmp/x.py <<'EOF'\nopen('Makefile', 'w')\nEOF\npython3 /tmp/x.py"),
        "guard-write"
    );
    assert_eq!(v("cat <<'EOF'\nopen('Makefile', 'w')\nEOF"), "ok");
    assert_eq!(
        v("S=/tmp/a; cat >> $S/p.py <<'EOF'\n('x-hooks.sh').write_text('y')\nEOF"),
        "ok"
    );
    assert_eq!(
        v("cat > /tmp/x.py <<'EOF' && python3 /tmp/x.py\nopen('Makefile', 'w')\nEOF"),
        "guard-write"
    );
    assert_eq!(
        v("cat > /tmp/g_1.py <<'EOF'\nopen('Makefile', 'w')\nEOF\npython3 /tmp/g_*.py"),
        "guard-write"
    );
}

#[test]
fn the_storing_target_is_a_plain_word_and_the_terminator_is_as_bash_reads_it() {
    let body = "open('Makefile', 'w')";
    assert_eq!(
        v(&format!("cat > >(bash) <<'EOF'\n{body}\nEOF")),
        "guard-write"
    );
    assert_eq!(
        v(&format!("tee >(bash) >/dev/null <<'EOF'\n{body}\nEOF")),
        "guard-write"
    );
    assert_eq!(
        v(&format!("cat > $(mktemp) <<'EOF'\n{body}\nEOF")),
        "guard-write"
    );
    assert_eq!(
        v(&format!("S=$(pwn); cat > $S/x <<'EOF'\n{body}\nEOF")),
        "guard-write"
    );
    assert_eq!(v(&format!("tee -a /tmp/a $S/b <<'EOF'\n{body}\nEOF")), "ok");
    assert_eq!(
        v(&format!("PATH=/x; cat > /tmp/f <<'EOF'\n{body}\nEOF")),
        "guard-write"
    );
    assert_eq!(
        v(&format!("LD_PRELOAD=/x; cat > /tmp/f <<'EOF'\n{body}\nEOF")),
        "guard-write"
    );
    assert_eq!(
        v(&format!(
            "work_dir=/x; S=/y; cat > $S/f <<'EOF'\n{body}\nEOF"
        )),
        "ok"
    );
    assert_eq!(v(&format!("cat <<'EOF' > ${{S}}/x\n{body}\nEOF\n")), "ok");
    assert_eq!(v(&format!("cat > /tmp/x <<-'EOF'\n{body}\n\tEOF")), "ok");
    assert_eq!(
        v(&format!("cat > /tmp/x <<'EOF'\n{body}\n\tEOF")),
        "guard-write"
    );
    assert_eq!(
        v(&format!("cat > /tmp/x <<'EOF'\na\nEOF\n{body}\nEOF")),
        "guard-write"
    );
    assert_eq!(
        v(&format!("cat > /tmp/x <<-'EOF'\na\n\tEOF\n{body}\nEOF")),
        "guard-write"
    );
}

/// The guard files `guard_file_hooks::held` names, each as (path, a directory a session `cd`s into, the name it then writes).
const HELD: [(&str, &str, &str); 11] = [
    ("Makefile", "/diagram/.clones/s", "Makefile"),
    ("scripts/hooks/a-hooks.sh", "scripts/hooks", "a-hooks.sh"),
    (".claude/settings.json", ".claude", "settings.json"),
    ("tests/rolls.py", "tests", "rolls.py"),
    ("dev/switches.json", "dev", "switches.json"),
    ("dev/work-budget.json", "dev", "work-budget.json"),
    // T229: the guards' own sources
    (
        "rust/guard/src/guards/make_only_hooks.rs",
        "rust/guard/src/guards",
        "make_only_hooks.rs",
    ),
    ("rust/guard/Cargo.toml", "rust/guard", "Cargo.toml"),
    (
        "rust/guard/src/guards/house_style_words.tsv",
        "rust/guard/src/guards",
        "house_style_words.tsv",
    ),
    (
        "scripts/hooks/l7r-guard.sh",
        "scripts/hooks",
        "l7r-guard.sh",
    ),
    // the hook entries' launcher (451 T169), which chooses the dispatcher the settings' commands chose before
    ("scripts/hooks/l7r-hook", "scripts/hooks", "l7r-hook"),
];

/// Every form a session writes a file with from the shell (T227, measured on 2026-11-19), `{F}` the guard file, `{D}` and `{B}`
/// its directory and name; the seventh is T220's own, which rewrote two files through a `python3 -` heredoc.
const WRITE_FORMS: [&str; 50] = [
    "cat > {F} <<'EOF'\nx\nEOF",
    "cat <<'EOF' > {F}\nx\nEOF",
    "cat <<EOF >{F}\nx\nEOF",
    "tee {F} <<'EOF'\nx\nEOF",
    "tee {F} >/dev/null <<'EOF'\nx\nEOF",
    "tee -a {F} < /tmp/x",
    "cd /x && python3 - <<'EOF'\np='{F}'; s=open(p).read()\nopen(p,'w').write(s)\nEOF",
    "python3 - <<'EOF'\nfrom pathlib import Path\nPath('{F}').write_text('x')\nEOF",
    "python3 -c \"open('{F}','w').write('x')\"",
    "sed -i 's/a/b/' {F}",
    "sed -i.bak -e 's/a/b/' {F}",
    "sed -E -i 's/a/b/' {F}",
    "sed --in-place 's/a/b/' {F}",
    "perl -pi -e 's/a/b/' {F}",
    "cp /tmp/x {F}",
    "mv /tmp/x {F}",
    "install -m 755 /tmp/x {F}",
    "echo x >> {F}",
    "printf x >{F}",
    "echo x >| {F}",
    "echo x &> {F}",
    "cd {D} && cat > {B} <<'EOF'\nx\nEOF",
    "cd {D} && echo x > {B}",
    "cd {D}; sed -i s/a/b/ {B}",
    "cd {D} && cp /tmp/x {B}",
    "cat > /diagram/.clones/s/{F} <<'EOF'\nx\nEOF",
    "sed -i 's/old text/new/' {F}",
    "sed -i -e 's|a b|c|' {F}",
    "perl -pi -e 's/a b/c/' {F}",
    "for f in x; do sed -i s/a/b/ {F}; done",
    "find . -name x -exec sed -i s/a/b/ {F} \\;",
    "rsync -a /tmp/x {F}",
    "dd if=/tmp/x of={F} bs=1M",
    "truncate -s 0 {F}",
    "cd {D} && truncate --size=0 {B}",
    // 451 T33: through an interpreter - a Python program naming the file by a loop, a join or where the shell stands (T14's
    // own shape first: `cd` into the directory, then a heredoc writing the bare name), a shell or Perl body, a loop's variable
    "cd {D} && python3 - <<'EOF'\nimport re\np='{B}'\ns=open(p).read()\nopen(p,'w').write(s)\nEOF",
    "cd {D} && python3 -c \"open('{B}','w').write('x')\"",
    "python3 - <<'EOF'\nimport pathlib\nfor f in ['{F}']:\n    p = pathlib.Path(f)\n    p.write_text(p.read_text())\nEOF",
    "python3 - <<'EOF'\nfrom pathlib import Path\n(Path('{D}') / '{B}').write_text('y')\nEOF",
    "python3 -c \"import os; open(os.path.join('{D}','{B}'),'w').write('x')\"",
    "python3 <<'EOF'\nopen('{F}','w').write('x')\nEOF",
    "cat <<'EOF' | python3\nopen('{F}','w').write('x')\nEOF",
    "bash <<'EOF'\nsed -i s/a/b/ {F}\nEOF",
    "bash -c 'sed -i s/a/b/ {F}'",
    "sh -c \"echo x > {F}\"",
    "cat <<'EOF' | bash\necho x >> {F}\nEOF",
    "perl - <<'EOF'\nopen(F, '>', '{F}'); print F 'x';\nEOF",
    "for f in {F} /tmp/x; do echo x | tee $f; done",
    "for f in {F}; do sed -i s/a/b/ \"$f\"; done",
    // window#79's shape: a helper handed the file
    "python3 - <<'EOF'\nimport pathlib\ndef patch(path):\n    p = pathlib.Path(path); p.write_text(p.read_text())\npatch('{F}')\nEOF",
];

/// A guard file WRITTEN from the shell is refused in every form a session uses, and every miss is listed at once (T227).
#[test]
fn every_shell_write_of_a_guard_file_is_refused() {
    let verdicts: Vec<(String, String)> = HELD
        .iter()
        .flat_map(|(file, dir, base)| {
            WRITE_FORMS.iter().map(move |f| {
                f.replace("{F}", file)
                    .replace("{D}", dir)
                    .replace("{B}", base)
            })
        })
        .map(|cmd| (v(&cmd), cmd))
        .collect();
    let missed: Vec<&(String, String)> = verdicts
        .iter()
        .filter(|(got, _)| got != "guard-write")
        .collect();
    assert_eq!(missed, Vec::<&(String, String)>::new());
}

/// A guard file READ, named in stored text, or a file that is not a guard written, is left alone - review-gate.sh and its suite
/// among them: neither is on the guard list (`guard_file_hooks::held`), so T220's heredoc writing them was correctly let through.
#[test]
fn a_guard_file_read_or_mentioned_and_a_non_guard_written_are_left_alone() {
    for cmd in [
        "cp Makefile /tmp/x",
        "cp scripts/hooks/a-hooks.sh /tmp/x",
        "grep -n x Makefile > /tmp/out",
        "sed -n 1,5p Makefile",
        "cat .claude/settings.json | head",
        "diff dev/switches.json /tmp/x > /tmp/d",
        "cat > /tmp/notes <<'EOF'\nMakefile dev/switches.json\nEOF",
        "sed -i s/a/b/ tests/hooks/test-a-hooks.sh",
        "python3 - <<'EOF'\nprint(open('Makefile').read())\nEOF",
        "cd dev && cat switches.json > /tmp/x",
        "chmod +x scripts/hooks/a-hooks.sh",
        "echo 'sed -i s/a/b/ Makefile'",
        "make guard-edit FILE=Makefile WHY=\"a reason here\"",
        "python3 - <<'EOF'\np='rust/guard/src/guards/make_only_hooks/tests.rs'; s=open(p).read()\nopen(p,'w').write(s)\nEOF",
        "python3 -c \"open('rust/guard/src/shared/tests/tree.rs','w').write('x')\"",
        "python3 -c \"open('rust/guard/src/guards/tests.rs','w').write('x')\"",
        "cd /x && python3 - <<'EOF'\np='scripts/gates/review-gate.sh'; s=open(p).read()\nopen(p,'w').write(s)\nEOF",
        "cd /x && python3 - <<'EOF'\np='tests/hooks/test-review-gate.sh'; s=open(p).read()\nopen(p,'w').write(s)\nEOF",
        "cat > scripts/gates/review-gate.sh <<'EOF'\nx\nEOF",
        "cd .claude && cat > settings.local.json <<'EOF'\nx\nEOF",
        "cd tests/hooks && cat > test-a-hooks.sh <<'EOF'\nx\nEOF",
        // 451 T169, observed 2026-11-23 (refused on this task's own suite edit): the dispatcher's suite is no dispatcher, nor is a
        // hooks suite's scratch directory the launcher
        "python3 - <<'EOF'\np='tests/hooks/test-l7r-guard.sh'; s=open(p).read()\nopen(p,'w').write(s)\nEOF",
        "sed -i s/a/b/ tests/hooks/test-l7r-guard.sh",
        "echo x > /tmp/l7r-hooks-suite-pair-hooks.sh-1/x",
    ] {
        assert_eq!(v(cmd), "ok", "{cmd}");
    }
}

#[test]
fn the_guards_own_sources_are_guard_writes_from_the_shell_but_their_tests_are_not() {
    // T229 (ask:449-guard-sources-held): the walk judges by guard_file_hooks::held
    for cmd in [
        "sed -i s/a/b/ rust/guard/src/guards/make_only_hooks.rs",
        "cat > scripts/hooks/l7r-guard.sh <<'EOF'\nx\nEOF",
        "cat > scripts/hooks/l7r-hook <<'EOF'\nx\nEOF",
        "python3 - <<'EOF'\np='scripts/hooks/l7r-hook'; s=open(p).read()\nopen(p,'w').write(s)\nEOF",
        "cd rust/guard && cat >> Cargo.toml <<'EOF'\nx\nEOF",
        "cd rust/guard/src/shared && tee tree.rs",
        "cd rust/guard/shared/src && tee tree.rs",
        "sed -i s/a/b/ rust/guard/shared/src/env.rs",
        "cd rust/guard/shared && cat >> Cargo.toml <<'EOF'\nx\nEOF",
    ] {
        assert_eq!(v(cmd), "guard-write", "{cmd}");
    }
    for cmd in [
        "cat >> rust/guard/src/guards/make_only_hooks/tests.rs <<'EOF'\nx\nEOF",
        "cd rust/guard/src/shared/tests && tee tree.rs",
        "cd rust/guard/shared/src/context && tee tests.rs",
        "grep -n held rust/guard/src/guards/guard_file_hooks.rs",
    ] {
        assert_eq!(v(cmd), "ok", "{cmd}");
    }
}

/// 451 T33: what T33's readers must leave alone - a tee or a copy outside the guard files, a Python program that reads a guard
/// file (where the shell stands in a guard directory too: a `-c` read there was refused before T33), one that reads a guard file
/// and writes elsewhere, a shell or Perl body that only reads, a loop writing scratch.
#[test]
fn reads_and_writes_elsewhere_through_an_interpreter_are_left_alone() {
    for cmd in [
        "echo x | tee /tmp/t33/out.txt",
        "cp rust/guard/src/guards/make_only_hooks.rs /tmp/x",
        "cd rust/guard/src/guards && python3 -c \"print(open('make_only_hooks.rs').read()[:5])\"",
        "cd rust/guard/src/guards && python3 - <<'EOF'\nprint(open('make_only_hooks.rs').read())\nEOF",
        "python3 - <<'EOF'\nimport json\nd = json.load(open('.claude/settings.json'))\nprint(d)\nEOF",
        "python3 - <<'EOF'\ns = open('rust/guard/src/guards/make_only_hooks.rs').read()\nopen('/tmp/x', 'w').write(s)\nEOF",
        "python3 - <<'EOF'\nfrom pathlib import Path\nt = Path('Makefile').read_text()\nPath('/tmp/targets').write_text(t)\nEOF",
        "bash -c 'grep -n x Makefile'",
        "bash <<'EOF'\ncat Makefile > /tmp/x\nEOF",
        "for f in a b; do echo $f > /tmp/$f; done",
        "for f in Makefile dev/switches.json; do wc -l $f; done",
        "perl -ne 'print' Makefile",
        "sh -c 'echo hi'",
        // the replay's corrections: a hook RUN by subprocess (window#56, #299, #312), a hook payload's file (window#267)
        "python3 - <<'EOF'\nimport subprocess\nsubprocess.run(['scripts/hooks/a-hooks.sh', 'pretool'], input='{}', text=True)\nEOF",
        "cd /tmp && python3 -c \"import json; print(json.dumps({'file_path': '/x/scripts/hooks/gate-hooks.sh'}))\"",
    ] {
        assert_eq!(v(cmd), "ok", "{cmd}");
    }
}

/// 451 T33 (T34's found-and-left): a bare `rustfmt` formats outside make, and both refusals name `make format FILE=` / `CRATE=`,
/// never a bare `make format`, which rewrites every crate.
#[test]
fn a_bare_rustfmt_is_refused_naming_the_scoped_format() {
    for cmd in [
        "rustfmt rust/guard/src/guards/x.rs",
        "rustfmt --check rust/guard/src/lib.rs",
        "~/.cargo/bin/rustfmt --edition 2021 a.rs",
        "cd rust && rustfmt guard/src/lib.rs",
        "git diff --name-only | xargs rustfmt",
        "find rust -name '*.rs' -exec rustfmt {} +",
    ] {
        assert_eq!(v(cmd), "bare-rustfmt", "{cmd}");
    }
    for cmd in [
        "grep -rn rustfmt Makefile",
        "which rustfmt",
        "rustup component add rustfmt",
        "echo 'rustfmt a.rs'",
        "make format FILE=rust/guard/src/lib.rs",
        "rustfmt --version",
        "cat <<'EOF' > /tmp/n\nrustfmt a.rs\nEOF",
    ] {
        assert_eq!(v(cmd), "ok", "{cmd}");
    }
    let d = std::env::temp_dir();
    for (cmd, rule) in [
        ("rustfmt a.rs", "bare-rustfmt"),
        ("cargo fmt", "bare-cargo"),
    ] {
        let got = run(cmd, &d);
        let named =
            refused(&got, "make format FILE=<path>") && refused(&got, "make format CRATE=<dir>");
        assert!(named, "{rule}: {got:?}");
        assert!(!refused(&got, "make format (rustfmt)"), "{rule}: {got:?}");
    }
}

/// 451 T113: a quote nothing closes before forty escapes, after an engine entry point - `MASK_QUOTE`, the pattern `masked` blanked
/// quoted strings with, took a backslash with the character after it or alone, so its backtracking search tried 2^40 readings, and
/// the guard gave no answer in 10 s (measured 2026-11-21, `/tmp/t113/probe-before.txt`). Judged in a child under a deadline.
#[test]
fn an_unclosed_quote_after_an_entry_point_is_judged_in_time() {
    const CHILD: &str = "L7R_MAKE_ONLY_QUOTE_IN_TIME";
    let cmd = format!(
        "python3 -m l7r.diagram.tools.x; echo it's {}",
        "\\n".repeat(40)
    );
    if std::env::var_os(CHILD).is_some() {
        let d = world("in-time");
        println!("T113 answered {:?}", run(&cmd, &d));
        return;
    }
    let (passed, said) = crate::guards::passes_in_time(
        "guards::make_only_hooks::tests::an_unclosed_quote_after_an_entry_point_is_judged_in_time",
        CHILD,
        10,
    );
    assert!(passed, "the guard did not answer in 10 s: {said}");
    let refused = said.contains("no make target wraps `l7r.diagram.tools.x`");
    assert!(refused, "{said}");
}

/// 451 T113: the scan finds the strings the pattern it replaced (`MASK_QUOTE`, built here) found, on every text of up to 5 pieces of a
/// double and a single quote, a backslash, a letter, `-c `, `-c` and a tab, a dash, a `c`, a space, a newline and a character of two
/// bytes (177,156 texts).
#[test]
fn the_mask_finds_the_quoted_strings_the_pattern_found() {
    let pattern =
        crate::shared::regex::build(r#"(?s)(?<!-c )(?<!-c\t)(["'])(?:\\.|(?!\1).)*\1"#).unwrap();
    let pieces = [
        "\"", "'", "\\", "a", "-c ", "-c\t", "-", "c", " ", "\n", "é",
    ];
    for text in crate::guards::texts_of(&pieces, 5) {
        let found: Vec<(usize, usize)> = pattern
            .find_iter(&text)
            .map_while(Result::ok)
            .map(|m| (m.start(), m.end() - 1))
            .collect();
        assert_eq!(super::mask_quotes(&text), found, "{text:?}");
    }
}

/// 451 T87 (found by T79): a guard file's name written in scratch is no guard write - a literal `/tmp` place, a `$(mktemp -d)` one
/// (tx#953, ux#2204's shape), a copy of `dev/work-budget.json` into a `$(mktemp -d ...)` preview (ux#1106's), a scratch copy of a guard
/// source, quoted or not, and a Python program's write standing in scratch (the guard log's 2026-11-20 t232 row); the same write in a
/// project tree, one whose prefix nothing places (`$CLAUDE_PROJECT_DIR`, read as unassigned), and a scratch write beside a write the
/// walk cannot place or cannot see (an `xargs`'s) keep HEAD's reading.
#[test]
fn a_guard_files_name_written_in_scratch_is_no_guard_write() {
    for cmd in [
        "printf x > /tmp/q/Makefile",
        "T=$(mktemp -d); git init -q $T; printf 'all:\\n' > $T/Makefile",
        "S=$(mktemp -d /tmp/t226/preview.XXXX); mkdir -p $S/dev; cp dev/work-budget.json $S/dev/work-budget.json",
        "cd /tmp/q && sed -i s/a/b/ Makefile",
        "cp /tmp/x /tmp/t42/src/rust/guard/src/guards/a.rs",
        "printf 'all:\\n' > /tmp/q/Makefile",
        "sed -i 's/a/b/' /tmp/q/Makefile",
        "echo \"x\" > /tmp/q/Makefile 2>&1",
        "if true; then printf 'x' > /tmp/q/Makefile 2>/dev/null; fi",
        "echo x &>/tmp/q/Makefile",
        "cd /tmp/q && sed -i '491s|a = 0;|b|' rust/guard/src/guards/a_hooks.rs && sed -n 489,493p rust/guard/src/guards/a_hooks.rs",
        "cd /tmp/q && python3 -c \"import json;d=json.load(open('dev/switches.json'));json.dump(d,open('dev/switches.json','w'))\"",
    ] {
        let got = v(cmd);
        assert_eq!(got, "ok", "{cmd}");
    }
    for cmd in [
        "printf x > /diagram/.clones/s/Makefile",
        "echo x > $CLAUDE_PROJECT_DIR/Makefile",
        "F=$(ls); sed -i s/a/b/ $F/Makefile",
        "printf x > /tmp/q/Makefile; F=$(ls); sed -i s/a/b/ $F/Makefile",
        "cp Makefile /tmp/q/Makefile; ls | xargs sed -i s/a/b/ Makefile",
        "cp Makefile /tmp/q/Makefile; ls | xargs sed -i 's/a/b/' Makefile",
        "sed -i 's/a/b/' /tmp/q/Makefile; F=$(ls); sed -i 's/a/b/' $F/Makefile",
        "sed -i s/a/b/ /tmp/q/Makefile; cd $X && sed -i s/a/b/ Makefile",
        "cd /tmp/q && python3 -c \"open('Makefile','w')\"; ls | xargs python3 -c \"open('Makefile','w')\"",
        "python3 -c \"open('Makefile','w').write('x')\"",
        "cd /tmp/q && python3 -c \"import os; os.chdir('/diagram/.clones/s'); open('Makefile','w')\"",
        "cd /tmp/q && python3 - <<'EOF'\nimport os; os.chdir('/diagram/.clones/s'); open('Makefile','w')\nEOF",
        "cd /tmp/q && CDPATH=/diagram/.clones cd s && printf x > Makefile",
        "cd /tmp/q && CDPATH=/diagram/.clones cd s && cp /tmp/x Makefile",
        "cd /tmp/q && CDPATH=/diagram/.clones cd s && python3 -c \"open('Makefile','w')\"",
    ] {
        let got = v(cmd);
        assert_eq!(got, "guard-write", "{cmd}");
    }
}

/// 451 T87 (review round 2): a write into a git worktree in scratch of a project repository is a guard write, its commits reaching
/// that repository - the worktree on disk, its `.git` pointer read, and one the command itself makes, which no pointer shows yet, so
/// a command naming a `worktree add` keeps HEAD's reading by name. Scratch beside it stays scratch.
#[test]
fn a_write_into_a_project_repositorys_worktree_in_scratch_is_a_guard_write() {
    let d = world("worktree");
    let place = crate::shared::tempdir::TempDir::new("guard-makeonly-worktree-place");
    let s = place.canonicalize().unwrap();
    crate::shared::env::set("TMPDIR", std::env::temp_dir());
    std::fs::create_dir_all(d.join(".git/worktrees/w")).unwrap();
    std::fs::write(d.join(".git/worktrees/w/commondir"), "../..").unwrap();
    std::fs::create_dir_all(s.join("wt")).unwrap();
    std::fs::write(
        s.join("wt/.git"),
        format!("gitdir: {}/.git/worktrees/w\n", d.display()),
    )
    .unwrap();
    let w = s.join("wt").display().to_string();
    for cmd in [
        format!("printf x > {w}/Makefile"),
        format!("cp /tmp/x {w}/rust/guard/src/guards/a.rs"),
        format!("cd {w} && sed -i s/a/b/ Makefile"),
        format!("cd {w} && python3 -c \"open('Makefile','w')\""),
        "git -C /diagram/.clones/s worktree add --detach /tmp/q HEAD && printf x > /tmp/q/Makefile"
            .to_owned(),
    ] {
        let got = v(&cmd);
        assert_eq!(got, "guard-write", "{cmd}");
    }
    let beside = v(&format!("printf x > {}/Makefile", s.display()));
    assert_eq!(beside, "ok");
}
