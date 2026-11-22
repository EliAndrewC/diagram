//! 451 T79's second round (its plan review, BLOCKED 2026-11-21): the walk RESOLVES what the command's own text resolves - a loop's
//! literal values, a variable no one assigns (empty, as bash reads it), a variable assigned in a loop's or a function's body, a name
//! assigned twice (judged by every value; in straight-line code, by the value it holds at each read, 451 T91), `$(dirname X)` and
//! `$(basename X)` of a known X - and what stays truly unknown keeps
//! spec 204's D6: it lands where the shell was last known, so standing in the mirror it is the mirror's. Before, a write word of
//! which nothing was known was read as not the mirror's, which let the review's five probes write the mirror.

use super::{mirror, walk};

type Place = (Option<String>, &'static str, &'static str);

fn writes(cmd: &str, at: &str, m: &str) -> Vec<Place> {
    walk(cmd, Some(at), m, "/home/u")
        .targets
        .into_iter()
        .map(|t| (t.path, t.class, t.how))
        .collect()
}

fn classes(cmd: &str, at: &str, m: &str) -> Vec<&'static str> {
    writes(cmd, at, m).into_iter().map(|w| w.1).collect()
}

fn at(path: &str, class: &'static str, how: &'static str) -> Place {
    (Some(path.to_owned()), class, how)
}

/// The review's five probes, each a write of the mirror standing in it: a relative word led by a variable no one assigns, a loop
/// over literal values (twice), and a word whose value is a substitution the walk cannot run - the last spec 204 D6's own bypass
/// moved from a `cd` to a write word.
#[test]
fn the_reviews_five_probes_write_the_mirror() {
    let (_d, m, _c) = mirror("probes");
    let here = |f: &str| at(&format!("{m}/{f}"), "main", "shell");
    assert_eq!(writes("echo x > $n.txt", &m, &m), [here(".txt")]);
    assert_eq!(
        writes("for i in 1 2; do echo x > $i.txt; done", &m, &m),
        [here("1.txt"), here("2.txt")]
    );
    assert_eq!(
        writes("for f in a.txt b.txt; do echo x > $f; done", &m, &m),
        [here("a.txt"), here("b.txt")]
    );
    for cmd in [
        "F=$(ls | head -1); sed -i s/a/b/ $F",
        "R=$(git rev-parse --show-toplevel); echo x > $R/f",
        "cp /tmp/a $(git rev-parse --show-toplevel)/f",
        "echo x > $(echo /diagram)/f",
    ] {
        assert_eq!(writes(cmd, &m, &m), [(None, "main", "shell")], "{cmd}");
        assert_eq!(classes(cmd, "/tmp", &m), ["elsewhere"], "{cmd}");
    }
    // a basename of a known word is a name where the shell stands
    assert_eq!(writes("touch $(basename /tmp/q/x)", &m, &m), [here("x")]);
}

/// The scratch writes the old catch-all was chosen to rescue (T79's 13, bx#22598 to bx#55610), resolved from the text instead:
/// each lands under `/s`, elsewhere, standing in the mirror.
#[test]
fn a_scratch_write_resolves_from_the_text() {
    let (_d, m, _c) = mirror("rescues");
    let s = |p: &str| at(p, "elsewhere", "named");
    for (cmd, want) in [
        (
            "for b in p q; do d=/s/k/$b/i; mkdir -p $d; rm -f \"${d:?}\"/*; done",
            vec![
                s("/s/k/p/i"),
                s("/s/k/p/i/*"),
                s("/s/k/q/i"),
                s("/s/k/q/i/*"),
            ],
        ),
        ("F=/s/p/plan.json; mkdir -p $(dirname $F)", vec![s("/s/p")]),
        (
            "F=/s/p/plan.json; D=$(dirname \"$F\"); B=$(basename $F); touch $D/x $D/$B",
            vec![s("/s/p/x"), s("/s/p/plan.json")],
        ),
        (
            "for d in /s/a /s/b; do mkdir -p $d/extra; done",
            vec![s("/s/a/extra"), s("/s/b/extra")],
        ),
        (
            "for t in \"sweet potato\" tobacco; do echo x > /s/h-$t.txt; done",
            vec![s("/s/h-sweet_potato.txt"), s("/s/h-tobacco.txt")],
        ),
        ("echo x > ${X:-/s/d}/f", vec![s("/s/d/f")]),
        ("X=/s/e; echo x > ${X:-/s/d}/f", vec![s("/s/e/f")]),
        ("cp /tmp/a $X/b", vec![s("/b")]),
        // a `NAME=` after a command's first word is its argument (bx#31033's `make plan-verdict F=413`), not the shell's
        (
            "F=/s/p.json; grep F=1 x; mkdir -p $(dirname $F)",
            vec![s("/s")],
        ),
        // a literal suffix cut keeps its word's directory (bx#31289's `"${f%.xls}.txt"`), a glob's or a name's
        (
            "for f in /s/x/*.xls; do echo x > \"${f%.xls}.txt\"; done",
            vec![(None, "elsewhere", "named")],
        ),
        (
            "F=/s/x/a.json; echo x > ${F%.json}.txt",
            vec![(None, "elsewhere", "named")],
        ),
        (
            "mkdir -p $(dirname /) $(dirname /s/) $(basename /s/a.txt .txt)",
            vec![s("/"), s("/"), at(&format!("{m}/a"), "main", "shell")],
        ),
        ("echo x > $OLDPWD/f", vec![s("/f")]),
    ] {
        assert_eq!(writes(cmd, &m, &m), want, "{cmd}");
    }
    // a function's body and a loop's: a known start, whatever its parameter
    for cmd in [
        "add(){ D=/s/k-$1-w; mkdir -p $D/pages; }; add x",
        "for q in 1 2; do D=/s/q-$q; mkdir -p $D/pages; done",
        "for f in /s/x/*; do echo x > $f.bak; done",
        "cd $X && touch f",
        "F=/s/a; F=/s/b; echo x > ${F%x}/y",
    ] {
        assert!(
            classes(cmd, &m, &m).iter().all(|c| *c == "elsewhere"),
            "{cmd}"
        );
    }
}

/// A write in a loop's or an `if`'s body, and a name the command assigns twice, which HEAD let through from `/tmp` (probed
/// 2026-11-21): the body's first word is its command, and a name is judged by every value it takes.
#[test]
fn a_body_and_a_second_value_are_read() {
    let (_d, m, _c) = mirror("bodies");
    for cmd in [
        format!("for f in a; do cp /tmp/a {m}/x; done"),
        format!("if true; then touch {m}/y; fi"),
        format!("while false; do touch {m}/y; done"),
        format!("F={m}/a; echo x > $F; F=/s/b"),
        format!("for f in /s/a {m}/b; do touch $f; done"),
        format!("if true; then D={m}; fi; echo x > $D/f"),
        format!("cd {m} && cd /tmp && echo x > $OLDPWD/f"),
        format!("cd {m} && echo x > $PWD/f"),
    ] {
        assert!(classes(&cmd, "/tmp", &m).contains(&"main"), "{cmd}");
    }
}

/// What the text cannot resolve - a name read from input, a loop over a substitution, a function's parameter, a sourced file's
/// names, a parameter expansion the walk does not read, a glob, more values than the walk tries, a cd to a name it cannot place -
/// is read where the shell was last known (spec 204's D6): the mirror standing in it, elsewhere standing in `/tmp`.
#[test]
fn what_stays_unknown_lands_where_the_shell_was_last_known() {
    let (_d, m, _c) = mirror("unknown");
    // nine values a loop, two loops: 81 bindings, past the 64 the walk tries for a product of names (451 T91 left it so: walked at one
    // value of `a` while `b`'s are tried, a pair that writes the mirror would be missed)
    let nine: Vec<String> = (0..9).map(|i| format!("v{i}")).collect();
    let wide = format!(
        "for a in {0}; do for b in {0}; do echo x > $a$b; done; done",
        nine.join(" ")
    );
    for cmd in [
        "read F; echo x > $F/f".to_owned(),
        "for i in $(seq 3); do echo x > $i.txt; done".to_owned(),
        "f() { echo x > $1; }; f a".to_owned(),
        "source e.sh; echo x > $X/f".to_owned(),
        "echo x > ${X%/*}/f".to_owned(),
        "for f in *; do echo x > $f.bak; done".to_owned(),
        "for f; do echo x > $f; done".to_owned(),
        "mapfile -t L < f; echo x > $L".to_owned(),
        "A=1 B=2; echo x > $B/f".to_owned(),
        "echo x > ${X#a}/f".to_owned(),
        "F=/s/a.b/c; echo x > ${F%%.*}".to_owned(),
        "for f in a b; do echo x > ${f%a}.t; done".to_owned(),
        "echo x > ${X%a}f".to_owned(),
        "F+=/s; echo x > $F".to_owned(),
        "printf -v F %s a; echo x > $F".to_owned(),
        "echo x > $RANDOM".to_owned(),
        "cd \"$X\" && touch f".to_owned(),
        "cd $(somewhere) && echo x > $OLDPWD/f".to_owned(),
        wide,
    ] {
        assert!(classes(&cmd, &m, &m).iter().all(|c| *c == "main"), "{cmd}");
        assert!(
            classes(&cmd, "/tmp", &m).iter().all(|c| *c == "elsewhere"),
            "{cmd}"
        );
    }
    // a literal name in single quotes, or after a backslash, is not a variable: the file is named `$X/f`, where the shell stands
    for cmd in ["echo x > '$X/f'", "echo x > \\$X/f", "echo x > $$.f"] {
        assert_eq!(classes(cmd, &m, &m), ["main"], "{cmd}");
    }
}

/// A name the environment sets is its value there, word-safe; the walk's bindings that end in different places leave its final
/// place unknown; `dirname /` is `/`, a word with no slash is in `.` (bash's `dirname a`).
#[test]
fn the_environment_and_the_bindings_places() {
    let (_d, m, _c) = mirror("environ");
    crate::env::set("T79_SCRATCH", "/s/e f");
    assert_eq!(
        writes("echo x > $T79_SCRATCH/g", &m, &m),
        [at("/s/e_f/g", "elsewhere", "named")]
    );
    crate::env::unset("T79_SCRATCH");
    let w = walk(
        "for d in /s/a /s/b; do cd $d; done",
        Some(&m),
        &m,
        "/home/u",
    );
    assert_eq!(w.final_dir, None);
    let env = super::super::Env::new();
    assert_eq!(
        super::super::bind::dir_base("dirname /", &env, "/h").as_deref(),
        Some("/")
    );
    assert_eq!(
        super::super::bind::dir_base("dirname a", &env, "/h").as_deref(),
        Some(".")
    );
    assert_eq!(
        super::super::bind::dir_base("basename a.txt .txt", &env, "/h").as_deref(),
        Some("a")
    );
}

/// A target's segment starts at its command: a loop's, an `if`'s or a `while`'s keyword the walk reads past is not shown as its
/// head, so a guard that reads the segment's first word reads the command (451 T79's third round: `for F in a; do make append
/// FILE=$F LINE=b; done` in a gated tree read `do` as the command, and gate-write refused a make it leaves to its target rule, 38
/// of the ux replay's commands, measured 2026-11-21).
#[test]
fn a_targets_segment_starts_at_its_command() {
    let (_d, m, _c) = mirror("keywords");
    let heads = |cmd: &str| -> Vec<String> {
        walk(cmd, Some(&m), &m, "/home/u")
            .targets
            .into_iter()
            .map(|t| t.segment)
            .collect()
    };
    assert_eq!(heads("for f in a; do touch $f; done"), ["touch $f"]);
    assert_eq!(heads("if true; then  touch b; fi"), ["touch b"]);
    assert_eq!(heads("while ! cp x y; do :; done"), ["cp x y"]);
    assert_eq!(heads("touch done"), ["touch done"]);
}

/// A name assigned from `$PWD` takes where the shell stands at the assignment, not at the command's start (451 T79's third round:
/// `cd <clone> && WT=$PWD; touch $WT/f` standing in the mirror was refused at HEAD, and bx#51888, which reassigns WT to a scratch
/// path before it writes, newly refused under the every-value binding, measured 2026-11-21).
#[test]
fn a_name_assigned_from_pwd_is_where_the_shell_stands_then() {
    let (_d, m, c) = mirror("pwd");
    let wt = format!("cd {c} && WT=$PWD; touch $WT/f");
    assert_eq!(
        writes(&wt, &m, &m),
        [at(&format!("{c}/f"), "clone", "named")]
    );
    // reassigned in straight-line code, the read takes the value it holds there, as bash does (451 T91: T79 judged both)
    let twice = format!("cd {c} && WT=$PWD; echo; WT=/tmp/q/wt; touch $WT/x.py");
    assert_eq!(classes(&twice, &m, &m), ["elsewhere"]);
    let both = format!("cd {c}; WT=$PWD; touch $WT/a; WT=/tmp/q/wt; touch $WT/x.py");
    assert_eq!(classes(&both, &m, &m), ["clone", "elsewhere"]);
}

/// A name reassigned from its own value (`S=$S/sub`, `S=${S}/a`, a prefix `S=$S cmd`) gives it no value of its own: it follows the
/// one before (451 T79's third round: the every-value binding that picked such an assignment read the name from itself, unknown, so
/// a scratch write standing in the mirror was the mirror's - window#302's `S=$S python3 $S/walk.py`, measured 2026-11-21).
#[test]
fn a_name_reassigned_from_itself_follows_its_value() {
    let (_d, m, _c) = mirror("itself");
    for (cmd, path) in [
        ("S=/tmp/q; S=$S/sub; touch $S/f", "/tmp/q/sub/f"),
        ("S=/tmp/q; S=$S true; touch $S/f", "/tmp/q/f"),
        ("S=/tmp/q; S=${S}/a; echo x > $S/f", "/tmp/q/a/f"),
    ] {
        let got: Vec<_> = writes(cmd, &m, &m)
            .into_iter()
            .map(|w| (w.0, w.1))
            .collect();
        assert_eq!(got, [(Some(path.to_owned()), "elsewhere")], "{cmd}");
    }
}

/// A loop's variable also assigned is judged at each of its loop's values and each literal value it is assigned (451 T79's third
/// round: ux#752 assigned `f` a page, wrote it with `sed -i`, then looped `f` over other pages, and its write of a gated tree went
/// unseen, measured 2026-11-21); an assignment the walk cannot read leaves it unknown.
#[test]
fn a_loop_variable_also_assigned_takes_both() {
    let (_d, m, _c) = mirror("loopset");
    let here = |f: &str| at(&format!("{m}/{f}"), "main", "shell");
    let mut got = writes(
        "f=a.txt; echo x > $f; for f in b.txt; do echo y > $f; done",
        &m,
        &m,
    );
    got.sort();
    got.dedup();
    assert_eq!(got, [here("a.txt"), here("b.txt")]);
    let mut quoted = writes("f='c.txt'; echo x > $f; for f in d.txt; do :; done", &m, &m);
    quoted.sort();
    assert_eq!(quoted, [here("c.txt"), here("d.txt")]);
    assert_eq!(
        classes(
            "f=$(cat x); echo x > /tmp/q/$f; for f in b; do :; done",
            &m,
            &m
        ),
        ["elsewhere"]
    );
}

/// 451 T91: a name reassigned in straight-line code - no branch, loop, function, subshell or `&&` between its assignment and the
/// read - reads the value it holds there, so `D=<mirror>/x; D=/s/y; touch $D/f` standing in the mirror writes scratch, as bash does
/// (T79 judged it at each value and refused it).
#[test]
fn a_straight_reassignment_reads_its_last_value() {
    let (_d, m, _c) = mirror("straight");
    for (cmd, path) in [
        (format!("D={m}/x; D=/s/y; touch $D/f"), "/s/y/f"),
        (format!("cd /s && D={m}/x; D=/s/y; touch $D/f"), "/s/y/f"),
        (format!("D={m}/x\nexport D=/s/y\necho x > $D/f"), "/s/y/f"),
        (
            format!("D={m}/x; D=/s/a; D=$D/b; echo x > $D/f"),
            "/s/a/b/f",
        ),
        (format!("D={m}/x; D=/s/y && touch $D/f"), "/s/y/f"),
        (format!("D={m}/x; D=/s/y; (touch $D/f)"), "/s/y/f"),
        (format!("D={m}/x; D=/s/y; (true); touch $D/f"), "/s/y/f"),
        (format!("D={m}/x; D=/s/y; touch \"$D/f\" 2>&1"), "/s/y/f"),
        (
            format!("for f in a; do D={m}/x; D=/s/$f; touch $D/g; done"),
            "/s/a/g",
        ),
        (
            format!("X=$(cat a | wc -l); D={m}/x; D=/s/y; touch $D/f"),
            "/s/y/f",
        ),
        (
            format!("D={m}/x; D=/s/y; echo \"a\\\"b\" ${{X}} \"${{X}}\" ${{#X}}; touch $D/f"),
            "/s/y/f",
        ),
        ("D=/s/a; D=$D/b; D=/s/c; echo x > $D/f".to_owned(), "/s/c/f"),
    ] {
        let got = writes(&cmd, &m, &m);
        assert_eq!(got, [at(path, "elsewhere", "named")], "{cmd}");
    }
    // an `a=` inside quotes is no assignment bash makes, and stays as written (bx#50157's `python3 -c "...; a=Image.open(...)"`)
    let texts = super::super::bind::bound_texts("a=/s/x; a=/s/y; touch $a/f; echo \"; a=1\"");
    assert_eq!(
        texts,
        ["__s0_a=/s/x; __s1_a=/s/y; touch ${__s1_a}/f; echo \"; a=1\""]
    );
    // a read before any assignment reads the environment or nothing, as bash does: `${D}f` is `f` where the shell stands
    let early = writes("echo x > ${D}f; D=/s/a/; D=/s/b/", &m, &m);
    assert_eq!(early, [at(&format!("{m}/f"), "main", "shell")]);
    crate::env::set("D", "/s/e/");
    let from_env = writes("echo x > ${D}f; D=/s/a/; D=/s/b/", &m, &m);
    crate::env::unset("D");
    let want = [at("/s/e/f", "elsewhere", "named")];
    assert_eq!(from_env, want);
}

/// 451 T91: a mirror value at either end is still read: the first where it is read before the reassignment, the last where it is
/// the last, and each value wherever the reassignment may not hold for the read - a prefix, a subshell, a pipe, a background, a
/// condition, a substitution, a function, a loop's next pass, a branch, a quoted or escaped or commented `D=`, `readonly`, `local`,
/// a read that assigns, and a read whose default word turns on the value (`${D:-W}`, `${D-W}`).
#[test]
fn a_mirror_value_at_either_end_is_still_read() {
    let (_d, m, _c) = mirror("either-end");
    for cmd in [
        format!("F={m}/a; echo x > $F; F=/s/b"),
        format!("D=/s/y; D={m}/x; touch $D/f"),
        format!("D={m}/x; D=/s/y true; touch $D/f"),
        format!("D={m}/x; (D=/s/y); touch $D/f"),
        format!("D={m}/x; (D=/s/y; touch $D/g); touch $D/f"),
        format!("D={m}/x; D=/s/y | cat; touch $D/f"),
        format!("D={m}/x; D=/s/y & touch $D/f"),
        format!("D={m}/x; false && D=/s/y; touch $D/f"),
        format!("D={m}/x; true || D=/s/y; touch $D/f"),
        format!("D={m}/x; X=$(D=/s/y); touch $D/f"),
        format!("D={m}/x; X=\"$(D=/s/y)\"; touch $D/f"),
        format!("D={m}/x; X=$(D=/s/y; echo); touch $D/f"),
        format!("D={m}/x; D=/s/y; X=`date`; touch $D/f"),
        format!("D={m}/x; D=/s/y; X=\"$(date)\"; touch $D/f"),
        format!("D={m}/x; D=/s/y; echo ${{X:-$(pwd)}}; touch $D/f"),
        format!("D={m}/x; D=/s/y\n# a note\ntouch $D/f"),
        format!("D={m}/x; D=/s/y; . e.sh; touch $D/f"),
        format!("f() {{ D={m}/x; }}; D=/s/y; f; touch $D/f"),
        format!("function f {{ touch $D/f; }}; D=/s/y; D={m}/x; f"),
        format!("D={m}/x; echo \"; D=/s/y\"; touch $D/f"),
        format!("D={m}/x; echo '; D=/s/y'; touch $D/f"),
        format!("D={m}/x; echo \\;D=/s/y; touch $D/f"),
        format!("D={m}/x # ; D=/s/y\ntouch $D/f"),
        format!("for i in 1 2; do touch $D/f; D=/s/a; D={m}/x; done"),
        format!("D=/s/a; for i in 1 2; do touch $D/f; D={m}/x; done"),
        format!("D=/s/a; if true; then D={m}/x; fi; touch $D/f"),
        format!("D={m}/x; readonly D; D=/s/y; touch $D/f"),
        format!("D={m}/x; local D=/s/y; touch $D/f"),
        format!("D={m}/x; D=/s/y; echo x > ${{D:=/s/z}}/f"),
        format!("D={m}/x; D=; touch ${{D:-{m}/z}}/f"),
        format!("D={m}/x; D=; touch ${{D-/s/z}}/f"),
        format!("D={m}/x; D=/s/y; {{ touch $D/f; }}"),
    ] {
        let from_tmp = classes(&cmd, "/tmp", &m);
        assert!(from_tmp.contains(&"main"), "{cmd}");
    }
}

/// 451 T91: a loop past the 64 bindings, its variable the command's only many-valued name, is judged at each of its values, so 65
/// scratch values written standing in the mirror pass (T79 read the 65th as unknown, D6's mirror), and one mirror value among them,
/// first, middle or last, is refused standing in the mirror and in `/tmp`; repeated values are one binding; past `MAX_VALUES`, and
/// past 64 for a cross product of names, a name is unknown as before (D6), since a product walked at one value of the other names
/// would miss the pair that writes the mirror.
#[test]
fn a_loop_past_the_cap_is_judged_value_by_value() {
    let (_d, m, _c) = mirror("past-cap");
    let values = |n: usize| -> Vec<String> { (0..n).map(|i| format!("/s/v{i}")).collect() };
    let looped = |v: &[String]| format!("for f in {}; do touch $f; done", v.join(" "));
    for n in [64, 65, super::super::bind::MAX_VALUES] {
        let got = classes(&looped(&values(n)), &m, &m);
        assert!(got.iter().all(|c| *c == "elsewhere"), "{n} values");
    }
    for at_k in [0, 40, 79] {
        let mut v = values(80);
        v[at_k] = format!("{m}/x");
        let cmd = looped(&v);
        let (inside, from_tmp) = (classes(&cmd, &m, &m), classes(&cmd, "/tmp", &m));
        assert!(
            inside.contains(&"main") && from_tmp.contains(&"main"),
            "mirror at {at_k}"
        );
    }
    let twice: Vec<String> = values(2).into_iter().cycle().take(70).collect();
    let texts = super::super::bind::bound_texts(&looped(&twice)).len();
    assert_eq!(texts, 2);
    let past = classes(&looped(&values(super::super::bind::MAX_VALUES + 1)), &m, &m);
    assert!(past.iter().all(|c| *c == "main"));
    let pair = format!(
        "for a in /s {m}; do for b in {}; do touch $a/$b; done; done",
        values(65).join(" ")
    );
    let from_tmp = classes(&pair, "/tmp", &m);
    assert!(from_tmp.contains(&"main"));
}
