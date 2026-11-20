use std::path::PathBuf;

use serde_json::json;

use super::{classify, context_line, explain, join, judge, normpath, relpath, walk, walk_judged};

/// A mirror with a clone under `.clones/` that has a `.git`.
fn mirror(tag: &str) -> (crate::shared::tempdir::TempDir, String, String) {
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-tree-{tag}"));
    let clone = d.join("diagram/.clones/mine");
    std::fs::create_dir_all(clone.join(".git")).unwrap();
    let main = d.join("diagram").to_string_lossy().into_owned();
    (d, main, clone.to_string_lossy().into_owned())
}

fn input(cmd: &str, dir: &str) -> serde_json::Value {
    json!({"tool_input": {"command": cmd, "description": "d"}, "cwd": dir})
}

#[test]
fn paths_normalize_join_and_relate_as_posixpath_does() {
    assert_eq!(normpath(""), ".");
    assert_eq!(normpath("/a//b/./c/../d"), "/a/b/d");
    assert_eq!(normpath("//a"), "//a");
    assert_eq!(normpath("///a"), "/a");
    assert_eq!(normpath("../x/.."), "..");
    assert_eq!(normpath("a/../.."), "..");
    assert_eq!(normpath("/.."), "/");
    assert_eq!(normpath("."), ".");
    assert_eq!(
        (
            join("/a", "b"),
            join("/a/", "b"),
            join("/a", "/b"),
            join("", "b")
        ),
        ("/a/b".into(), "/a/b".into(), "/b".into(), "b".into())
    );
    assert_eq!(
        (
            relpath("/m/x/y", "/m"),
            relpath("/m", "/m"),
            relpath("/o", "/m/x")
        ),
        ("x/y".to_owned(), ".".to_owned(), "../../o".to_owned())
    );
}

#[test]
fn a_path_is_the_mirror_a_clone_elsewhere_or_unknown() {
    assert_eq!(
        [
            classify(Some("/m/.clones"), "/m"),
            classify(Some("/m/.clones/c/x"), "/m"),
            classify(Some("/m/x"), "/m"),
            classify(Some("/mx"), "/m"),
            classify(None, "/m")
        ],
        ["clone", "clone", "main", "elsewhere", "unknown"]
    );
}

#[test]
fn the_walk_follows_the_commands_own_cds_variables_and_subshells() {
    let (_dir, m, c) = mirror("walk");
    let h = "/home/u";
    let w = walk(
        &format!("cd {m} && git add x && git commit -q"),
        Some("/tmp"),
        &m,
        h,
    );
    assert!(
        w.cd_into_main
            && w.targets.len() == 2
            && w.targets
                .iter()
                .all(|t| t.class == "main" && t.how == "shell")
    );
    assert_eq!(
        walk("cat > /tmp/x", Some(&m), &m, h).targets[0].class,
        "elsewhere"
    );
    assert_eq!(
        walk(&format!("C={c}; git -C $C rm x"), Some(&m), &m, h).targets[0].class,
        "clone"
    );
    assert!(walk(
        &format!("( cd {c} && make quick ); git log"),
        Some("/tmp"),
        &m,
        h
    )
    .targets
    .iter()
    .all(|t| t.class == "clone"));
    assert!(walk(&format!("cd {m} && git log"), None, &m, h)
        .targets
        .is_empty());
    let named = walk(&format!("git -C {m} commit"), None, &m, h);
    assert_eq!(
        (named.targets[0].class, named.targets[0].how),
        ("main", "named")
    );
    let after = walk(
        "S=/tmp/x; ( cd $S && cat > m.py ); git commit",
        Some(&m),
        &m,
        h,
    );
    assert_eq!(
        after.targets.iter().map(|t| t.class).collect::<Vec<_>>(),
        ["elsewhere", "main"]
    );
    assert_eq!(
        walk("echo $(cd /tmp) > f", Some(&m), &m, h).targets[0].class,
        "main"
    );
    assert_eq!(
        walk("cd && touch f", Some(&m), &m, h).targets[0]
            .path
            .as_deref(),
        Some("/home/u/f")
    );
    assert_eq!(
        walk("cd - && touch f", Some(&m), &m, h).targets[0].class,
        "main"
    );
    assert_eq!(
        walk("pushd /tmp && touch f; popd; touch g", Some("/x"), &m, h)
            .targets
            .iter()
            .map(|t| t.class)
            .collect::<Vec<_>>(),
        ["elsewhere", "elsewhere"]
    );
    assert_eq!(
        walk("cd -- && mkdir d", None, &m, h).targets[0]
            .path
            .as_deref(),
        Some("/home/u/d")
    );
}

#[test]
fn the_walk_reads_each_tool_and_its_paths() {
    let (_dir, m, _c) = mirror("tools");
    let h = "/home/u";
    assert_eq!(
        walk("sudo env X=1 timeout 5 touch /tmp/a", None, &m, h).targets[0]
            .path
            .as_deref(),
        Some("/tmp/a")
    );
    assert!(walk("timeout", None, &m, h).targets.is_empty());
    assert_eq!(
        walk("sed -i -e s/a/b/ /tmp/f /tmp/g", None, &m, h)
            .targets
            .len(),
        2
    );
    assert_eq!(
        walk("sed -i --expression=x 's/a/b/' /tmp/f", None, &m, h)
            .targets
            .len(),
        1
    );
    assert_eq!(walk("sed -i -f prog /tmp/f", None, &m, h).targets.len(), 0);
    // T227: `perl -i` and `sed --in-place=SUFFIX` rewrite a file in place too
    for (cmd, n) in [
        ("perl -pi -e s/a/b/ /tmp/f", 1),
        ("perl -i.bak -pe s/a/b/ /tmp/f /tmp/g", 2),
        ("perl -Ilib -e 1 /tmp/f", 0),
        ("perl -Mstrict -pe s/a/b/ /tmp/f", 0),
        ("perl --version /tmp/f", 0),
        ("sed --in-place=.bak s/a/b/ /tmp/f", 1),
        // a script quoted around a space is blanked to '' and is still the script, or -e's argument
        ("sed -i 's/a b/c/' /tmp/f", 1),
        ("sed -i -e 's/a b/c/' /tmp/f", 1),
        ("perl -pi -e 's/a b/c/' /tmp/f", 1),
        // rsync's destination, dd's of= and truncate's files, its -s and -r values aside
        ("rsync -a /tmp/src /tmp/f", 1),
        ("dd if=/tmp/src of=/tmp/f bs=1M", 1),
        ("dd if=/tmp/src", 0),
        ("truncate -s 0 /tmp/f /tmp/g", 2),
        ("truncate -r /tmp/ref /tmp/f", 1),
        ("truncate --size=0 /tmp/f", 1),
    ] {
        assert_eq!(walk(cmd, None, &m, h).targets.len(), n, "{cmd}");
    }
    assert_eq!(
        walk("cp a b /tmp/dest -- ''", None, &m, h).targets[0]
            .path
            .as_deref(),
        Some("/tmp/dest")
    );
    assert_eq!(
        walk("echo x >| /tmp/o 2>&1 >/dev/null", None, &m, h)
            .targets
            .len(),
        1
    );
    assert_eq!(walk("touch \"/tmp/q\" 'a b'", None, &m, h).targets.len(), 1);
    assert_eq!(
        walk("touch ~/f", None, &m, h).targets[0].path.as_deref(),
        Some("/home/u/f")
    );
    assert_eq!(
        walk("touch $UNSET/f", Some(&m), &m, h).targets[0].class,
        "main"
    );
    assert_eq!(walk("touch /a/$UNSET", None, &m, h).targets[0].how, "named");
    assert_eq!(
        walk("X=$Y; touch $X", Some("/tmp"), &m, h).targets[0].class,
        "elsewhere"
    );
    assert_eq!(walk("touch rel", None, &m, h).targets[0].path, None);
    assert_eq!(
        walk("cd \"$NOPE\" && touch f", Some(&m), &m, h).targets[0].class,
        "main"
    );
    assert!(walk("git", None, &m, h).targets.is_empty());
    assert!(walk("git -c a=b -p log", None, &m, h).targets.is_empty());
    assert_eq!(
        walk("git -c a=b commit", Some("/tmp"), &m, h).targets.len(),
        1
    );
    assert_eq!(
        walk("git -C rel commit", Some("/tmp"), &m, h).targets[0].how,
        "shell"
    );
    assert_eq!(walk("python3 -c 'x'", Some("/tmp"), &m, h).targets.len(), 1);
    assert!(walk("cat <<EOF\ntouch /tmp/x\nEOF", None, &m, h)
        .targets
        .is_empty());
    assert!(walk("{ echo; }", None, &m, h).targets.is_empty());
}

#[test]
fn the_walk_judges_a_python_program_a_read_or_a_write() {
    let (_dir, m, _c) = mirror("python");
    let h = "/home/u";
    // 451 T31: a program that only reads stays a target MARKED "read" (its own `;` and `|` not splitting the walk), one that
    // can write and an unquoted one stay "shell"; the flags before `-c` and a minor version are read through
    let hows = |cmd: &str| -> Vec<&'static str> {
        walk_judged(cmd, Some("/tmp"), &m, h)
            .targets
            .iter()
            .map(|t| t.how)
            .collect()
    };
    assert_eq!(
        hows("python3 -c \"import sys; print(sys.argv | 1)\" a && python3 -c 'x'"),
        ["read", "read"]
    );
    assert_eq!(hows("python3 -c 'open(\"x\", \"w\")'"), ["shell"]);
    assert_eq!(hows("python3 -c x"), ["shell"]);
    assert_eq!(
        hows("python3 -I -c 'print(1)'; python3.12 -W ignore -Xdev -Ic 'open(\"x\", \"w\")'"),
        ["read", "shell"]
    );
    assert_eq!(
        hows("/usr/bin/python3 -B -c \"open('o', 'a')\"; python3 -W -c 'x'"),
        ["shell"]
    );
    assert!(hows("python3 -m json.tool x; python3 --version; python3 - <<<x").is_empty());
    assert!(walk("python3 x.py", Some("/tmp"), &m, h).targets.is_empty());
    // 451 T42 (T31's stdin rule retired): a stdin program is judged by its own body, and the `-c` read beside one the walk
    // reads is a read; beside one it cannot read (a missing file, any other upstream) the `-c` stays D5's write, as T31 had it
    let heredoc =
        "python3 - <<'PY'\nimport pathlib\np = pathlib.Path('x'); p.write_text('y')\nPY\n";
    assert_eq!(hows(heredoc), ["shell"]);
    assert_eq!(
        hows(&format!("{heredoc}python3 -c 'print(1)'")),
        ["shell", "read"]
    );
    assert_eq!(
        hows("python3 -c 'print(1)'; python3 <<EOF\nprint(2)\nEOF"),
        ["read"]
    );
    for cmd in [
        "python3 -c 'print(1)' && cat p.py | python3 -u",
        "python3 -c 'print(1)'; python3 -I - a < p.py",
    ] {
        assert_eq!(hows(cmd), ["shell"], "{cmd}");
    }
    assert_eq!(
        hows("python3 -c 'import sys; print(sys.stdin.read())' <<EOF\ndata\nEOF"),
        ["read"]
    );
    assert_eq!(
        hows("python3 -m json.tool <<EOF\n{}\nEOF\npython3 -c 'print(1)'; python3 --version"),
        ["read"]
    );
}

#[test]
fn a_branch_is_written_by_its_flags_or_a_new_name_alone() {
    let (_dir, m, _) = mirror("branch");
    let n = |cmd: &str| walk(cmd, Some("/tmp"), &m, "/h").targets.len();
    assert_eq!(
        [
            n("git branch -D x"),
            n("git branch --set-upstream-to=o/x"),
            n("git branch new"),
            n("git branch"),
            n("git branch --list x"),
            n("git branch --contains abc"),
            n("git branch --show-current x")
        ],
        [1, 1, 1, 0, 0, 0, 0]
    );
}

#[test]
fn each_verdict_and_its_words() {
    let (_dir, m, c) = mirror("judge");
    let h = "/h";
    let named = judge(
        &input(&format!("git -C {m} commit"), "/tmp"),
        &m,
        Some(&c),
        h,
        false,
    );
    assert_eq!(
        (named.verdict, named.reason, named.cause),
        ("refuse", "named-main", "named")
    );
    assert!(
        explain(&named, &m).contains(&format!("Named: {m}"))
            && explain(&named, &m).contains("Do it in your clone instead")
    );
    assert_eq!(judge(&input("ls", &m), &m, None, h, false).verdict, "allow");
    assert_eq!(
        judge(&input("git commit", &m), &m, None, h, false).verdict,
        "needs-clone"
    );
    let unresolved = judge(&input("git commit", &m), &m, None, h, true);
    assert!(
        unresolved.verdict == "refuse"
            && explain(&unresolved, &m).contains("cannot be resolved")
            && explain(&unresolved, &m).contains("standing in")
    );
    let missing = judge(&input("git commit", &m), &m, Some("/nowhere"), h, true);
    assert!(missing.reason == "clone-missing" && explain(&missing, &m).contains("git clone"));
    let shape = judge(&input("f() { git commit; }; f", &m), &m, Some(&c), h, true);
    assert!(
        shape.reason == "shape" && explain(&shape, &m).contains("could not be rewritten safely")
    );
}

#[test]
fn a_rewrite_moves_the_write_and_is_re_judged() {
    let (_dir, m, c) = mirror("rewrite");
    let h = "/h";
    let named = judge(
        &input(&format!("git -C {m} commit"), "/tmp"),
        &m,
        Some(&c),
        h,
        false,
    );
    let cd = judge(
        &input(&format!("cd {m} && git commit"), "/tmp"),
        &m,
        Some(&c),
        h,
        true,
    );
    assert_eq!(
        (cd.verdict, cd.cause, cd.command.as_deref()),
        (
            "rewrite",
            "cd",
            Some(format!("cd {c} && git commit").as_str())
        )
    );
    assert!(
        context_line(&cd, &m).contains("cd'd into")
            && cd.context()["context"]["prepended"] == false
    );
    let stand = judge(
        &input("git commit", &format!("{m}/sub")),
        &m,
        Some(&c),
        h,
        true,
    );
    assert_eq!(
        stand.command.as_deref(),
        Some(
            format!(
                "cd {} && git commit",
                PathBuf::from(&c).join("sub").display()
            )
            .as_str()
        )
    );
    assert!(
        context_line(&stand, &m).contains("standing in") && stand.context()["command"].is_string()
    );
    let top = judge(&input("git commit", &m), &m, Some(&c), h, true);
    assert_eq!(
        top.command.as_deref(),
        Some(format!("cd {c} && git commit").as_str())
    );
    let via = judge(
        &input(&format!("D={m}; cd $D && git commit"), "/tmp"),
        &m,
        Some(&c),
        h,
        true,
    );
    assert!(via.reason == "shape" && explain(&via, &m).contains("cds into"));
    let unnamed = judge(&input("git -C /x/$U commit", &m), &m, Some(&c), h, true);
    assert_eq!((unnamed.verdict, unnamed.reason), ("refuse", "named-main"));
    let none = super::Verdict {
        clone: None,
        ..named.clone()
    };
    assert!(explain(&none, &m).contains("<your clone under .clones/>"));
    let nopath = super::Verdict {
        walk: super::Walk {
            targets: vec![super::Target {
                path: None,
                class: "main",
                how: "named",
                segment: "seg".into(),
            }],
            ..named.walk.clone()
        },
        ..named
    };
    assert!(explain(&nopath, &m).contains("a target this cannot resolve, in `seg`"));
    let blank = judge(&json!({}), &m, None, h, false);
    assert!(
        blank.verdict == "allow"
            && blank.cwd.is_none()
            && context_line(
                &super::Verdict {
                    cause: "standing",
                    ..blank
                },
                &m
            )
            .contains("None")
    );
}

#[test]
fn the_walk_judges_a_python_program_run_from_stdin() {
    let (dir, m, _c) = mirror("stdin");
    let h = "/home/u";
    let hows = |cmd: &str| -> Vec<&'static str> {
        walk_judged(cmd, Some(&m), &m, h)
            .targets
            .iter()
            .map(|t| t.how)
            .collect()
    };
    // 451 T42: a heredoc's body is judged by T31's reader - a writer is a write where the shell stands, a read no target (as
    // every heredoc was before), and the `-c` read beside a read is a read: T31's stdin rule is retired for a judged program
    let writer = "python3 - <<'PY'\nimport pathlib\np = pathlib.Path('x'); p.write_text('y')\nPY\n";
    let reader =
        "python3 - a.html <<'PY'\nimport sys, re\nprint(len(open(sys.argv[1]).read()))\nPY\n";
    assert_eq!(hows(writer), ["shell"]);
    let w = walk_judged(writer, Some(&m), &m, h);
    assert_eq!(w.targets[0].segment, "python3 -  <<BODY");
    // the readers of a walk's paths (house style, make-only, the bench) see no stdin program, as before: house style's D11
    assert!(walk(writer, Some(&m), &m, h).targets.is_empty());
    assert!(hows(reader).is_empty());
    assert_eq!(hows(&format!("{reader}python3 -c 'print(1)'")), ["read"]);
    assert_eq!(
        hows(&format!("{writer}python3 -c 'print(1)'")),
        ["shell", "read"]
    );
    assert_eq!(
        hows(&format!("cat <<'PY' > n.py\nopen('o', 'w')\nPY\n{reader}")),
        ["shell"]
    );
    for (cmd, want) in [
        ("python3 <<EOF\nprint(1)\nEOF", &[][..]),
        ("python3 -I <<-EOF\n\tprint(1)\n\tEOF", &[]),
        // an unquoted delimiter: the shell expands the body first, a quoted one (`'EOF'`, `"EOF"`, `\EOF`) leaves it literal
        ("python3 <<EOF\nprint('$(rm f)')\nEOF", &["shell"]),
        ("python3 <<EOF\nprint(`rm f`)\nEOF", &["shell"]),
        ("python3 <<EOF\n$CODE\nEOF", &["shell"]),
        ("python3 <<EOF\nprint('$HOME')\nEOF", &[]),
        // in a heredoc `\"` is two characters, so this `$X` stands inside the literal
        ("python3 <<EOF\nprint(\"a\\\"$X\")\nEOF", &[]),
        ("python3 <<'EOF'\nprint('$(rm f)')\nEOF", &[]),
        ("python3 <<\"EOF\"\nprint(`x`)\nEOF", &[]),
        ("python3 <<\\EOF\n$CODE\nEOF", &[]),
        ("python3 - <<'PY' | tee out.txt\nprint(1)\nPY", &["shell"]),
        // a pipe from `cat` of a heredoc or a readable file is the program; any other source is not judged
        ("cat <<'PY' | python3\nopen('o', 'w')\nPY", &["shell"]),
        ("cat <<'PY' | python3 -u\nprint(1)\nPY", &[]),
        ("python3 < $D/w.py", &[]),
    ] {
        assert_eq!(hows(cmd), want, "{cmd}");
    }
    std::fs::create_dir_all(format!("{m}/l7r")).unwrap();
    std::fs::create_dir_all(format!("{m}/sub")).unwrap();
    for (f, body) in [
        ("w.py", "open('o', 'w')\n"),
        ("r.py", "print(1)\n"),
        ("sub/w.py", "import os; os.remove('f')\n"),
    ] {
        std::fs::write(format!("{m}/{f}"), body).unwrap();
    }
    for (cmd, want) in [
        ("python3 - <<'PY'\nimport l7r\nPY", &["shell"][..]),
        ("cat w.py | python3", &["shell"]),
        ("cat r.py | python3 -", &[]),
        ("cat -- r.py | python3", &[]),
        ("python3 < w.py", &["shell"]),
        ("python3 - x <r.py", &[]),
        ("D=sub; python3 < $D/w.py", &["shell"]),
        ("python3 < sub", &[]),
    ] {
        assert_eq!(hows(cmd), want, "{cmd}");
    }
    // a program the walk cannot read - a variable, a missing file, a directory, any other upstream - is judged as T31 left it:
    // no target of its own, and a `-c` read beside it D5's write
    for cmd in [
        "echo \"$CODE\" | python3",
        "python3 <<<\"$CODE\"",
        "python3 < missing.py",
        "python3 < sub",
        "cat a.py b.py | python3",
        "curl -s u | python3 -",
    ] {
        assert!(hows(cmd).is_empty(), "{cmd}");
        let beside = format!("{cmd}; python3 -c 'print(1)'");
        assert_eq!(hows(&beside), ["shell"], "{cmd}");
    }
    drop(dir);
}
