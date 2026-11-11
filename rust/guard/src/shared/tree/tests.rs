use std::path::PathBuf;

use serde_json::json;

use super::{classify, context_line, explain, join, judge, normpath, relpath, walk};

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
    assert!(walk("python3 x.py", Some("/tmp"), &m, h).targets.is_empty());
    assert!(walk("cat <<EOF\ntouch /tmp/x\nEOF", None, &m, h)
        .targets
        .is_empty());
    assert!(walk("{ echo; }", None, &m, h).targets.is_empty());
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
