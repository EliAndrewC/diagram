//! The decider's parts (`tests/hooks/test-make-only-hooks.sh`, replayed through the shim, and `tests/tooling/test_guard_corpus.py`'s rows are the verdict).

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{
    classify, decide, judge, landing_lint, lay, makefile_for, recipes, split_segment, words,
    wrapped, wrapped_modules, Ctx, Token,
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
        (
            "python3 l7r/diagram/hamletgen/__main__.py a",
            "engine-entry-point",
        ),
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
    d.hold(held)
}

/// A stand-in for `python3 -m ruff`: `sh -m ruff ...` fails, so the tests put a script on the command by the python field.
fn fake(d: &Path, body: &str) -> String {
    let path = d.join("fake-python");
    crate::guards::write_executable(&path, &format!("#!/bin/sh\n{body}\n"));
    path.to_string_lossy().into_owned()
}

#[test]
fn a_landing_is_linted_before_it_runs() {
    let d = world("lint");
    let bad = fake(&d, "echo a.py:1 bad; exit 1");
    assert!(landing_lint("make land-tooling FILES=a.py", &d, &bad)
        .contains("the landing's lint fails on a.py"));
    assert!(
        landing_lint("make arbiter-fix-done ID=x LAND=\"a.py\"", &d, &bad).contains("a.py:1 bad")
    );
    assert_eq!(
        landing_lint("make land-tooling FILES=a.py", &d, &fake(&d, "exit 0")),
        ""
    );
    assert_eq!(
        landing_lint(
            "make land-tooling FILES=a.py",
            &d,
            &fake(&d, "echo No module named ruff >&2; exit 1")
        ),
        ""
    );
    assert_eq!(
        landing_lint("make land-tooling FILES=none.py", &d, &bad),
        ""
    );
    assert_eq!(landing_lint("make land-tooling FILES=a.sh", &d, &bad), "");
    assert_eq!(landing_lint("ls", &d, &bad), "");
}

fn run(cmd: &str, d: &Path, python: &str) -> Vec<Answer> {
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
            python,
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
        assert!(refused(&run(cmd, &d, "sh"), words), "{cmd}");
    }
    assert!(refused(
        &run(
            "make land-tooling FILES=a.py",
            &d,
            &fake(&d, "echo bad; exit 1")
        ),
        "the landing's lint fails"
    ));
    assert!(run("make land-tooling FILES=a.py", &d, &fake(&d, "exit 0")).is_empty());
    assert!(run("ls", &d, "sh").is_empty());
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
            python: "sh",
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
    assert!(run("pytest tests/a/test_b.py -q", &d, "sh").is_empty());
    let got = run("python3 -m l7r.diagram.ci status", &d, "sh");
    assert!(
        matches!(&got[..], [Answer::Rewrite(v), Answer::Notice(n)] if v["command"] == "make ci-status" && n.contains("`python3 -m l7r.diagram.ci` was rewritten to `make ci-status`"))
    );
    assert!(run(
        "sed -i s/a/b/ Makefile # GUARD_EDIT_OK: it fired on correct work",
        &d,
        "sh"
    )
    .is_empty());
    assert!(refused(
        &run("sed -i s/a/b/ Makefile # GUARD_EDIT_OK", &d, "sh"),
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
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "make land-tooling FILES=a.py"}}),
    };
    let got = judge(
        &e,
        &Session::from_input(&e.input),
        &Ctx {
            tree: d.clone(),
            here: d.clone(),
            python: &fake(&d, "echo bad; exit 1"),
        },
    );
    assert!(refused(&got, "the landing's lint fails"));
}

#[test]
fn an_escape_is_recorded_with_its_reason() {
    let d = world("recorded");
    let why = "it fired on correct work, unique to this firing record test";
    assert!(run(
        &format!("sed -i s/a/b/ Makefile # GUARD_EDIT_OK: {why}"),
        &d,
        "sh"
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
const HELD: [(&str, &str, &str); 10] = [
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
];

/// Every form a session writes a file with from the shell (T227, measured on 2026-11-19), `{F}` the guard file, `{D}` and `{B}`
/// its directory and name; the seventh is T220's own, which rewrote two files through a `python3 -` heredoc.
const WRITE_FORMS: [&str; 35] = [
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
        "cd rust/guard && cat >> Cargo.toml <<'EOF'\nx\nEOF",
        "cd rust/guard/src/shared && tee tree.rs",
    ] {
        assert_eq!(v(cmd), "guard-write", "{cmd}");
    }
    for cmd in [
        "cat >> rust/guard/src/guards/make_only_hooks/tests.rs <<'EOF'\nx\nEOF",
        "cd rust/guard/src/shared/tests && tee tree.rs",
        "grep -n held rust/guard/src/guards/guard_file_hooks.rs",
    ] {
        assert_eq!(v(cmd), "ok", "{cmd}");
    }
}
