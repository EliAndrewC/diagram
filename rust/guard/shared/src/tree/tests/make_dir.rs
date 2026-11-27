//! 451 T409: a make runs where its own directory options put it, as GNU make 4.4.1 reads them (measured 2026-11-26 on a scratch
//! Makefile echoing `$(CURDIR)`, `t409-make` in the builders' scratchpad): `-C D`, `-CD`, `--directory=D`, `--directory D` and an
//! unambiguous prefix of it (`--di=D`), each relative to the one before (`-C a -C b` is `a/b`), an absolute one starting afresh,
//! anywhere among the goals (`x -C a`), inside a cluster (`-sC a`, `-sCa`), and none past `--`.

use super::super::{judge, walk};
use super::{input, mirror};

#[test]
fn a_make_runs_where_its_own_directory_options_say() {
    let (_dir, main, clone) = mirror("make-dir");
    let home = "/home/u";
    let at = |cmd: &str, start: Option<&str>| {
        let walked = walk(cmd, start, &main, home);
        let target = &walked.targets[0];
        (target.path.clone(), target.how)
    };
    let sub = Some(format!("{clone}/sub"));
    for cmd in [
        "make -C sub x",
        "make -Csub x",
        "make --directory=sub x",
        "make --directory sub x",
        "make --di=sub x",
        "make x -C sub",
        "make -sC sub x",
        "make -sCsub x",
        "make -j4 -C sub x",
        "make -j -C sub x",
        "make -f Makefile -C sub x",
        "make -fMakefile -C sub x",
        "make --file Makefile -C sub x",
        "make --no-print-directory - -C sub x",
        "make -C a/.. -C sub x",
        "make -C \"sub\" x",
    ] {
        assert_eq!(at(cmd, Some(&clone)), (sub.clone(), "shell"), "{cmd}");
    }
    // relative to the one before, an absolute one afresh and the rest relative to it
    assert_eq!(
        at("make -C a --directory=b x", Some(&clone)),
        (Some(format!("{clone}/a/b")), "shell")
    );
    assert_eq!(
        at("make -C a -C /abs -C b x", Some(&clone)),
        (Some("/abs/b".to_owned()), "named")
    );
    // no directory read: `-f`'s value, past `--`, a `-C` with nothing after it (make refuses it), a `-j` taking the rest
    for cmd in [
        "make -f -C sub x",
        "make -k -- -C sub x",
        "make x -C",
        "make -kj4C sub x",
    ] {
        assert_eq!(
            at(cmd, Some(&clone)),
            (Some(clone.clone()), "shell"),
            "{cmd}"
        );
    }
    // where the shell stands is unknown: a relative one with it, an absolute one named all the same
    assert_eq!(at("make -C sub x", None), (None, "shell"));
    assert_eq!(
        at("make -C /abs x", None),
        (Some("/abs".to_owned()), "named")
    );
    // a directory the walk cannot read is judged by what it knows, as git's `-C` is (451 T79's one rule)
    let unread = walk("make -C $(cat /tmp/d) tick", Some(&clone), &main, home);
    assert_eq!(
        (unread.targets[0].path.clone(), unread.targets[0].class),
        (None, "elsewhere")
    );
    // main-tree: a make sent into the mirror from a clone names it, and one sent from the mirror into a clone writes no mirror
    let named = judge(
        &input(&format!("make -C {main} quick"), &clone),
        &main,
        Some(&clone),
        home,
        true,
    );
    assert_eq!((named.verdict, named.reason), ("refuse", "named-main"));
    let away = judge(
        &input(&format!("make -C {clone} quick"), &main),
        &main,
        Some(&clone),
        home,
        true,
    );
    assert_eq!((away.verdict, away.reason), ("allow", "no-write-in-main"));
}
