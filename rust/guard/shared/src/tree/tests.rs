use std::path::PathBuf;

use serde_json::json;

use super::{
    classify, context_line, explain, join, judge, normpath, realpath, relpath, walk, walk_judged,
};

/// A mirror with a clone under `.clones/` that has a `.git`.
fn mirror(tag: &str) -> (crate::tempdir::TempDir, String, String) {
    let d = crate::tempdir::TempDir::new(&format!("guard-tree-{tag}"));
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
    // a name no one assigns is empty, as bash reads it, so `$UNSET/f` is `/f` (451 T79's second round; what stays unknown keeps
    // spec 204's D6, in `tests/binds.rs`)
    assert_eq!(
        walk("touch $UNSET/f", Some(&m), &m, h).targets[0].class,
        "elsewhere"
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
fn a_git_c_place_the_walk_cannot_resolve_is_judged_by_what_it_knows() {
    // 451 T79's one rule: a `-C` whose start is in the mirror is the mirror, named; one whose start is outside the mirror's tree
    // is no write there
    let (_dir, m, c) = mirror("c-unresolved");
    let unnamed = judge(
        &input(&format!("git -C {m}/$U commit"), &m),
        &m,
        Some(&c),
        "/h",
        true,
    );
    assert_eq!((unnamed.verdict, unnamed.reason), ("refuse", "named-main"));
    let scratch = judge(&input("git -C /x/$U commit", &m), &m, Some(&c), "/h", true);
    assert_eq!(
        (scratch.verdict, scratch.reason),
        ("allow", "no-write-in-main")
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
                program: None,
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

/// 451 T33: git's writing OPTIONS - found as T44 found its screen, each read-only subcommand's `--git-completion-helper` searched for an
/// option naming an output file or directory - land where they name, relative to `-C` or the shell; a read without one writes nothing.
#[test]
fn a_git_option_that_writes_a_file_is_a_write_where_it_names() {
    let (_d, m, _c) = mirror("git-output");
    let h = "/home/u";
    let at = |cmd: &str| -> Vec<(Option<String>, &'static str)> {
        walk(cmd, Some(&m), &m, h)
            .targets
            .into_iter()
            .map(|t| (t.path, t.how))
            .collect()
    };
    let named = |p: &str| vec![(Some(p.to_owned()), "named")];
    let here = |p: &str| vec![(Some(format!("{m}{p}")), "shell")];
    assert_eq!(at("git diff --output=/tmp/x.patch"), named("/tmp/x.patch"));
    assert_eq!(at("git diff --output x.patch HEAD"), here("/x.patch"));
    assert_eq!(at("git -C /o log -p --output=l.txt"), named("/o/l.txt"));
    assert_eq!(at("git show --output=s.txt HEAD"), here("/s.txt"));
    assert_eq!(at("git diff-tree -p --output=/tmp/t HEAD"), named("/tmp/t"));
    assert_eq!(at("git range-diff --output=r a...b"), here("/r"));
    assert_eq!(at("git archive -o /tmp/a.tar HEAD"), named("/tmp/a.tar"));
    assert_eq!(at("git archive --output=a.tar HEAD"), here("/a.tar"));
    assert_eq!(at("git archive --output a.tar HEAD"), here("/a.tar"));
    assert_eq!(at("git format-patch -1"), here(""));
    assert_eq!(at("git format-patch -o /tmp/p -1"), named("/tmp/p"));
    assert_eq!(at("git format-patch --output-directory=p -1"), here("/p"));
    assert_eq!(
        at("git format-patch --output-directory /tmp/p -1"),
        named("/tmp/p")
    );
    assert_eq!(
        at("git format-patch --output=/tmp/one.patch -1"),
        named("/tmp/one.patch")
    );
    assert_eq!(at("git bundle create b.bundle HEAD"), here("/b.bundle"));
    assert_eq!(at("git bugreport"), here(""));
    assert_eq!(at("git diagnose -o /tmp/d"), named("/tmp/d"));
    // a stash still writes where git runs, save its `list` and `show`
    assert_eq!(at("git stash"), here(""));
    assert_eq!(at("git stash pop"), here(""));
    for read in [
        "git stash list",
        "git stash show -p stash@{0}",
        "git diff",
        "git diff --stat HEAD",
        "git diff --output-indicator-new=+ HEAD",
        "git log --oneline -3",
        "git show HEAD:x",
        "git archive HEAD",
        "git format-patch --stdout -1",
        "git bundle verify b.bundle",
        "git bundle list-heads b.bundle",
        "git ls-files -o",
        "git status --porcelain",
        "git diff --outpu=/tmp/x",
    ] {
        assert!(at(read).is_empty(), "{read}");
    }
}

/// A walk's writes as (path, how), standing in `m`, the home `/home/u`.
fn git_writes(cmd: &str, m: &str) -> Vec<(Option<String>, &'static str)> {
    walk(cmd, Some(m), m, "/home/u")
        .targets
        .into_iter()
        .map(|t| (t.path, t.how))
        .collect()
}

/// 451 T50: the twelve subcommands outside `GIT_WRITES`, each form's real write, measured 2026-11-21 (git 2.53.0, each form run in
/// a scratch repository and its work tree, `.git`, the directory beside it and the home compared before and after,
/// `/tmp/t50/scripts/writes.sh`): a form that changes a work tree writes where it lands - the new, removed or moved tree a
/// `worktree`, `clone` or `init <dir>` names, `config --file`'s file - or where git runs (`switch`, `bisect`, `sparse-checkout`,
/// `submodule`, a bare `init` of no directory); `config --global` writes the home's config; a form that writes only `.git` or
/// nothing is no write.
#[test]
fn a_git_subcommand_writes_where_a_tree_changes_and_not_for_git_alone() {
    let (_d, m, _c) = mirror("git-tree");
    let at = |cmd: &str| git_writes(cmd, &m);
    let named = |p: &str| vec![(Some(p.to_owned()), "named")];
    let here = |p: &str| vec![(Some(format!("{m}{p}")), "shell")];
    assert_eq!(at("git worktree add --detach -q /tmp/w"), named("/tmp/w"));
    assert_eq!(at("git worktree add -b nb -q wt main"), here("/wt"));
    assert_eq!(at("git -C /o worktree add --detach w"), named("/o/w"));
    assert_eq!(at("git worktree remove --force /tmp/w"), named("/tmp/w"));
    assert_eq!(
        at("git worktree move /tmp/w w2"),
        [named("/tmp/w"), here("/w2")].concat()
    );
    assert_eq!(at("git clone -q /src/y /tmp/c"), named("/tmp/c"));
    assert_eq!(at("git clone -q -b other --depth 1 /src/y c"), here("/c"));
    assert_eq!(at("git clone -q -- /src/y d"), here("/d"));
    assert_eq!(at("git clone -q /src/y/"), here("/y"));
    assert_eq!(at("git clone -q --shared /src/y/.git"), here("/y"));
    assert_eq!(at("git clone -q https://h/o/r.git"), here("/r"));
    assert_eq!(at("git clone -q --bare /src/y"), here("/y.git"));
    assert_eq!(at("git clone --mirror h:o/r.git"), here("/r.git"));
    // a name the walk cannot read: the clone lands where git runs (451 T79's second round: `$R` unassigned is empty, a `git clone`
    // with no repository, which git refuses, so a substitution stands for the name it cannot read)
    assert_eq!(at("git clone $(cat url)"), here(""));
    assert!(at("git clone $R").is_empty());
    assert_eq!(at("git init -q /tmp/i"), named("/tmp/i"));
    assert_eq!(at("git init -q -b main --template /t d"), here("/d"));
    assert_eq!(at("git init -q --bare /tmp/b.git"), named("/tmp/b.git"));
    assert_eq!(at("git init --bare"), here(""));
    assert_eq!(at("git -C /o switch main"), named("/o"));
    for cmd in [
        "git switch other",
        "git switch -",
        "git switch -c nb other",
        "git switch --detach other",
        "git switch --orphan nb",
        "git bisect start HEAD HEAD~7",
        "git bisect start --term-new fixed HEAD v1",
        "git bisect good",
        "git bisect skip",
        "git bisect reset",
        "git sparse-checkout set --cone d",
        "git sparse-checkout add e",
        "git sparse-checkout disable",
        "git submodule add /src/y sm",
        "git submodule --quiet update --init",
        "git submodule deinit -f sm",
        "git submodule foreach 'git pull'",
    ] {
        assert_eq!(at(cmd), here(""), "{cmd}");
    }
    assert_eq!(at("git config -f f.cfg a.b c"), here("/f.cfg"));
    assert_eq!(
        at("git config --file=/tmp/g.cfg --unset a.b"),
        named("/tmp/g.cfg")
    );
    assert_eq!(at("git config set --file x.cfg a.b c"), here("/x.cfg"));
    assert_eq!(at("git config -f x.cfg -e"), here("/x.cfg"));
    assert_eq!(
        at("git config --system --add a.b c"),
        named("/etc/gitconfig")
    );
}

/// 451 T50: the twelve's forms that write only `.git` or nothing (the same measurement as above) are no write.
#[test]
fn a_git_subcommand_that_writes_only_git_or_nothing_is_no_write() {
    let (_d, m, _c) = mirror("git-none");
    for none in [
        "git worktree list",
        "git worktree list --porcelain",
        "git worktree prune -n --expire 1.day",
        "git worktree lock --reason x /tmp/w",
        "git worktree unlock /tmp/w",
        "git worktree repair",
        "git worktree add",
        "git clone",
        "git init",
        "git init -q",
        "git init -q .",
        "git -C /tmp/x init -q -b main",
        "git switch",
        "git switch -c nb",
        "git switch -C nb",
        "git switch --detach",
        "git bisect",
        "git bisect start",
        "git bisect start HEAD",
        "git bisect start HEAD -- d",
        "git bisect start --no-checkout HEAD v1",
        "git bisect log",
        "git bisect view",
        "git bisect visualize",
        "git bisect terms",
        "git sparse-checkout list",
        "git sparse-checkout check-rules --rules-file r",
        "git submodule",
        "git submodule status",
        "git submodule --quiet init",
        "git submodule sync --recursive",
        "git submodule summary",
        "git submodule absorbgitdirs",
        "git config user.name x",
        "git config set user.name x",
        "git config --local a.b c",
        "git config --worktree a.b c",
        "git config user.name",
        "git config --get user.name",
        "git config get user.name",
        "git config --list --show-origin",
        "git config --global -l",
        "git config --system --list",
        "git config -f f.cfg --get a.b",
        "git config get --file f.cfg a.b",
        "git config --blob HEAD:f a.b c",
        "git config --global --get-regexp x",
        "git fetch -q origin",
        "git fetch --dry-run origin",
        "git -C /o fetch -q",
        "git fetch origin main:main",
        "git notes add -m x",
        "git notes show",
        "git update-ref refs/heads/x HEAD",
        "git -C /o update-ref -d refs/x",
        "git symbolic-ref HEAD",
        "git symbolic-ref --short HEAD",
        "git symbolic-ref HEAD refs/heads/other",
    ] {
        assert!(git_writes(none, &m).is_empty(), "{none}");
    }
}

/// 451 T50: the four misreadings a review found in T33's dropped addition (2026-11-20), pinned: `fetch -n` is `--no-tags`, not a
/// dry run - and no fetch writes the tree, `--dry-run` included (it writes `.git`, measured 2026-11-21); one value-option list
/// for all twelve - each subcommand's own, from its `-h` (`-f` is `config`'s `--file` and `worktree`'s `--force`, `-n` `clone`'s
/// `--no-checkout`, `-c` `clone`'s `--config` and `switch`'s `--create`); `config --global` writes the home's config, not where
/// git runs; and a running gate's `git stash list` read as a write where git runs (fixed by T33).
#[test]
fn the_reviews_four_misreadings_stay_read() {
    let (_d, m, _c) = mirror("git-review");
    let at = |cmd: &str| git_writes(cmd, &m);
    let named = |p: &str| vec![(Some(p.to_owned()), "named")];
    assert!(at("git fetch -n origin").is_empty() && at("git fetch -q -n").is_empty());
    assert_eq!(at("git worktree add -f /tmp/wt"), named("/tmp/wt"));
    assert_eq!(at("git worktree add -f /tmp/wt other"), named("/tmp/wt"));
    assert_eq!(at("git config -f /tmp/f.cfg a.b c"), named("/tmp/f.cfg"));
    assert_eq!(at("git clone -n /src/y /tmp/c"), named("/tmp/c"));
    assert_eq!(at("git clone -c a=b /src/y /tmp/c"), named("/tmp/c"));
    assert_eq!(at("git init -b main /tmp/i"), named("/tmp/i"));
    assert!(at("git switch -c nb").is_empty());
    assert_eq!(
        at("git config --global user.name x"),
        named("/home/u/.gitconfig")
    );
    assert!(at("git stash list").is_empty() && at("git stash show -p").is_empty());
}

/// 451 T50: the shapes T33's dropped addition misread, kept as cases - main-tree#10 and #11 (a clone into the scratchpad, its URL
/// holding `${PAT}`, read at its after5 build as a clone where the shell stood), a `\`-continued clone (its operands on a line the
/// walk reads as a command of its own: its write is not placed, failing open as an unresolvable path does), and a clone into the
/// session's clones from the mirror.
#[test]
fn a_clone_lands_where_its_operands_say() {
    let (_d, m, _c) = mirror("git-clone");
    let walked = |cmd: &str| walk(cmd, Some(&m), &m, "/home/u").targets;
    // the writes of a command's `git clone` segment: (path, class); and that no other write is the mirror's
    let clones = |cmd: &str| -> Vec<(Option<String>, &'static str)> {
        let t = walked(cmd);
        // every write but the clone's own lands elsewhere
        assert!(t.iter().all(|t| t.how == "read" || t.class == "elsewhere"));
        t.into_iter()
            .filter(|t| t.segment.contains("git clone"))
            .map(|t| (t.path, t.class))
            .collect()
    };
    let sp = "/tmp/claude-1000/-diagram/x/scratchpad";
    let pat = "PAT=$(python3 -c \"\nimport configparser;c=configparser.ConfigParser();c.read('/h/s.ini');print(c['g']['p'])\")";
    assert_eq!(
        clones(&format!(
            "SP={sp}; {pat}; rm -rf $SP/clonetest; time git clone -q --filter=blob:none \"https://x-access-token:$PAT@github.com/o/diagram\" $SP/clonetest 2>&1 | tail -3"
        )),
        vec![(Some(format!("{sp}/clonetest")), "elsewhere")]
    );
    // `${PAT}` is one word with the URL it stands in (451 T79; T50 read it cut at its braces, not placed): the clone lands where
    // its second operand says (the `\`-continued forms T50 read cut are T79's, in `tests/words.rs`)
    assert_eq!(
        clones(&format!(
            "SP={sp}; {pat}; rm -rf $SP/clonetest; time git clone -q --filter=blob:none \"https://x-access-token:${{PAT}}@github.com/o/diagram\" $SP/clonetest 2>&1 | tail -3"
        )),
        vec![(Some(format!("{sp}/clonetest")), "elsewhere")]
    );
    assert_eq!(
        clones(&format!(
            "SP={sp} && {pat} && git clone -q --filter=blob:none --no-checkout \"https://x:${{PAT}}@github.com/o/diagram\" $SP/repro2 && git -C $SP/repro2 checkout -q \"$SHA\" -- a"
        )),
        vec![(Some(format!("{sp}/repro2")), "elsewhere")]
    );
    // a place of these forms the walk cannot resolve is settled by the walk's one rule, as every tool's is (451 T79,
    // `tests/words.rs`; T50 left it unplaced, since D6 read tx#63's scratch clone toward the mirror - its `$(mktemp -d)` is
    // scratch since T79): a tree word nothing is known of, and one where the shell stands after a `cd` the walk cannot read,
    // land where the shell was last known (spec 204's D6; 451 T79's second round, its plan review: T79's first round read the
    // first as not the mirror's); `git worktree add --detach $W`, `$W` unassigned, names no tree, which git refuses
    assert!(walked("git worktree add --detach $W").is_empty());
    for (unknown, class) in [
        ("git worktree add --detach $(cat w)", "main"),
        ("cd $(somewhere) && git switch other", "main"),
        ("cd $(somewhere) && git init -q --bare", "main"),
    ] {
        let t = walked(unknown);
        let got: Vec<_> = t.iter().map(|t| (t.path.as_deref(), t.class)).collect();
        assert_eq!(got, [(None, class)], "{unknown}");
    }
    let into = walked(&format!("git clone -q {m} .clones/x"));
    assert_eq!(
        (into[0].path.clone(), into[0].class),
        (Some(format!("{m}/.clones/x")), "clone")
    );
}

/// 451 T33, its round-3 gate replay (measured 2026-11-20): `chmod`'s mode and `chown`'s owner are not files - `chmod +x
/// $C/scripts/a.sh` was refused as a write of `+x` where the shell stood (refusals#124, #125, #132, window#256).
#[test]
fn a_mode_or_an_owner_is_not_a_file_written() {
    let (_d, m, _c) = mirror("chmod-mode");
    let at = |cmd: &str| -> Vec<Option<String>> {
        walk(cmd, Some(&m), &m, "/home/u")
            .targets
            .into_iter()
            .map(|t| t.path)
            .collect()
    };
    let named =
        |ps: &[&str]| -> Vec<Option<String>> { ps.iter().map(|p| Some((*p).to_owned())).collect() };
    assert_eq!(at("chmod +x /tmp/a.sh"), named(&["/tmp/a.sh"]));
    assert_eq!(at("chmod 755 /tmp/a /tmp/b"), named(&["/tmp/a", "/tmp/b"]));
    assert_eq!(at("chmod -R u+rw,go-w /tmp/d"), named(&["/tmp/d"]));
    assert_eq!(at("chmod -x /tmp/a.sh"), named(&["/tmp/a.sh"]));
    assert_eq!(at("chmod --reference=/tmp/r /tmp/a"), named(&["/tmp/a"]));
    assert_eq!(at("chown -R u:g /tmp/d"), named(&["/tmp/d"]));
    assert_eq!(at("chown --reference=/tmp/r /tmp/a"), named(&["/tmp/a"]));
    assert_eq!(
        at("rm -f /tmp/a +x"),
        named(&["/tmp/a", &format!("{m}/+x")])
    );
}

/// 451 T33: a Python write carries the program it comes from, so a guard can read which files its body names; any other write
/// carries none.
#[test]
fn a_python_write_carries_its_program() {
    let (_d, m, _c) = mirror("program");
    let h = "/home/u";
    let programs = |cmd: &str| -> Vec<Option<String>> {
        walk_judged(cmd, Some(&m), &m, h)
            .targets
            .into_iter()
            .map(|t| t.program.map(|p| p.trim_end().to_owned()))
            .collect()
    };
    let body = "open('a.rs','w').write('x')";
    assert_eq!(
        programs(&format!("python3 - <<'EOF'\n{body}\nEOF")),
        [Some(body.to_owned())]
    );
    assert_eq!(
        programs(&format!("python3 -c \"{body}\" > /tmp/log")),
        [Some(body.to_owned()), None]
    );
    assert_eq!(
        programs(&format!("cat <<'EOF' | python3\n{body}\nEOF")),
        [Some(body.to_owned())]
    );
    assert_eq!(programs("echo x > /tmp/a; sed -i s/a/b/ f"), [None, None]);
    assert!(
        walk(&format!("python3 - <<'EOF'\n{body}\nEOF"), Some(&m), &m, h)
            .targets
            .is_empty()
    );
}

/// `os.path.realpath` of a path that need not exist, moved here from `finished_run_hooks` (451 T58).
#[test]
fn a_path_is_resolved_whether_or_not_it_exists() {
    use std::path::Path;
    assert_eq!(
        realpath(Path::new("./no-such-either")),
        Path::new("no-such-either")
    );
    let d = crate::tempdir::TempDir::new("guard-tree-realpath");
    let real = std::fs::canonicalize(&d).unwrap();
    assert_eq!(realpath(&d.join("a/../b/./c")), real.join("b/c"));
    assert_eq!(realpath(&real), real);
}

mod words;

mod binds;

mod builds;
