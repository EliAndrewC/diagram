//! 451 T79: the walk keeps a word whole - a `\`-continued line, a `${VAR}` and a `$(...)` inside a word - reads a `$(mktemp ...)`
//! place where mktemp puts it, and settles an unresolved place one way for every tool. Found by T50 (2026-11-21): standing in
//! `/tmp`, `cp /tmp/a \` with the mirror's `b` on the next line and `D=<mirror>; cp /tmp/a ${D}/b` were let through by main-tree
//! while the one-line form and `$D/b` were refused, and `T=$(mktemp -d); cp /tmp/a $T/clone` standing in the mirror was refused.

use super::{mirror, walk};

type Place = (Option<String>, &'static str, &'static str);

/// (path, class, how) of each write of a walk standing in `at`, the home `/home/u`.
fn writes(cmd: &str, at: &str, m: &str) -> Vec<Place> {
    walk(cmd, Some(at), m, "/home/u")
        .targets
        .into_iter()
        .map(|t| (t.path, t.class, t.how))
        .collect()
}

fn at(path: &str, class: &'static str, how: &'static str) -> Place {
    (Some(path.to_owned()), class, how)
}

/// Bash drops a `\` and the newline after it, so the line goes on: one command, its words read as the one-line form's.
#[test]
fn a_continued_line_is_one_command() {
    let (_d, m, _c) = mirror("continued");
    let b = format!("{m}/b");
    for cmd in [
        format!("cp /tmp/a {b}"),
        format!("cp /tmp/a \\\n  {b}"),
        format!("cp \\\n /tmp/a \\\n {b}"),
    ] {
        assert_eq!(writes(&cmd, "/tmp", &m), [at(&b, "main", "named")], "{cmd}");
    }
    // a clone's or an init's operands go on past the line's end (T50 read them cut, and no write)
    for (cmd, place) in [
        ("git clone -q \\\n  https://h/o/r.git /tmp/c", "/tmp/c"),
        ("git clone -q /src/y \\\n  /tmp/c", "/tmp/c"),
        ("git init -q \\\n  /tmp/i", "/tmp/i"),
    ] {
        assert_eq!(
            writes(cmd, &m, &m),
            [at(place, "elsewhere", "named")],
            "{cmd}"
        );
    }
    // an escaped backslash before the newline is a backslash: the newline ends the command, as bash reads it
    assert_eq!(
        writes("echo a\\\\\ntouch f", "/tmp", &m),
        [at("/tmp/f", "elsewhere", "shell")]
    );
    // the assignment a continued line carries is read too
    assert_eq!(
        writes(&format!("D={m} \\\n  && cp /tmp/a $D/b"), "/tmp", &m),
        [at(&b, "main", "named")]
    );
}

/// `${VAR}` is a variable as `$VAR` is, its braces part of the word; a brace group's `{` and `}` still part its commands.
#[test]
fn a_braced_variable_is_a_variable() {
    let (_d, m, _c) = mirror("braced");
    let b = format!("{m}/b");
    for cmd in [
        format!("D={m}; cp /tmp/a $D/b"),
        format!("D={m}; cp /tmp/a ${{D}}/b"),
        format!("D={m}; cp /tmp/a \"${{D}}/b\""),
        format!("D={m}; echo x > ${{D}}/b"),
    ] {
        assert_eq!(writes(&cmd, "/tmp", &m), [at(&b, "main", "named")], "{cmd}");
    }
    // one word, unresolved, however its braces nest: never pieces of a command
    assert_eq!(
        writes("cp /tmp/a ${A:-${B}}/b /tmp/c", "/tmp", &m),
        [at("/tmp/c", "elsewhere", "named")]
    );
    // a brace group is no subshell: its `cd` holds after it
    assert_eq!(
        writes("{ cd /tmp && touch f; }; touch g", &m, &m),
        [
            at("/tmp/f", "elsewhere", "shell"),
            at("/tmp/g", "elsewhere", "shell")
        ]
    );
}

/// A `$(...)` inside a word is walked first, as a subshell of its own, and stays in its word, which the walk cannot resolve.
#[test]
fn a_substitution_stays_in_its_word() {
    let (_d, m, _c) = mirror("substitution");
    // spec 204's D6 case: `cd $(somewhere) && git commit` was read as a `cd` home, then a commit there
    assert_eq!(
        writes("cd $(somewhere) && git commit -q -m a", &m, &m),
        [(None, "main", "shell")]
    );
    // the destination is the word the substitution stands in, not the word before it
    let w = writes(&format!("cp /tmp/a $(echo {m})/b"), "/tmp", &m);
    assert_eq!((w.len(), w[0].0.as_deref()), (1, None));
    // the substitution's own writes are walked, its `cd` holding inside it alone
    assert_eq!(
        writes("echo $(cd /tmp && touch f) > g", &m, &m),
        [
            at("/tmp/f", "elsewhere", "shell"),
            at(&format!("{m}/g"), "main", "shell")
        ]
    );
    // a pipe into the word's command still feeds it, past the substitution's own commands
    let w = walk(
        "cat <<'PY' | python3 - $(echo x)\nopen('o', 'w').write('x')\nPY",
        Some(&m),
        &m,
        "/home/u",
    );
    assert!(w.targets.is_empty(), "{:?}", w.targets);
    let judged = super::walk_judged(
        "cat <<'PY' | python3 - $(echo x)\nopen('o', 'w').write('x')\nPY",
        Some(&m),
        &m,
        "/home/u",
    );
    assert_eq!(
        judged
            .targets
            .iter()
            .map(|t| (t.class, t.how))
            .collect::<Vec<_>>(),
        [("main", "shell")]
    );
}

/// `mktemp` makes its file or directory in the temp directory (`$TMPDIR`, else `/tmp`) unless a `-p` or a template with a `/` names
/// another; a relative template lands where the shell stands as mktemp runs, which the assignment's reading does not know.
/// Measured 2026-11-21 (coreutils `mktemp -u` per form, `TMPDIR` set and unset).
#[test]
fn a_mktemp_place_is_where_mktemp_puts_it() {
    let (_d, m, _c) = mirror("mktemp");
    let tmp = "/tmp/tmp.XXXXXXXXXX";
    for (cmd, place) in [
        // T50's tx#63 shape, standing in the mirror: a scratch clone
        (
            "T=$(mktemp -d); git clone -q . $T/clone",
            format!("{tmp}/clone"),
        ),
        ("T=$(mktemp -d); cp /tmp/a $T/clone", format!("{tmp}/clone")),
        ("T=\"$(mktemp -d)\"; touch \"$T/x\"", format!("{tmp}/x")),
        ("T=$(mktemp); echo x > $T", tmp.to_owned()),
        (
            "T=$(mktemp -d /tmp/t79/run.XXXX); touch $T/x",
            "/tmp/t79/run.XXXX/x".to_owned(),
        ),
        (
            "S=/s; T=$(mktemp -d -p $S/fresh); touch $T/x",
            "/s/fresh/tmp.XXXXXXXXXX/x".to_owned(),
        ),
        (
            "T=$(mktemp -u -t x.XXXX); touch $T",
            "/tmp/x.XXXX".to_owned(),
        ),
        (
            "T=$(mktemp --tmpdir=/q x.XXXX); touch $T",
            "/q/x.XXXX".to_owned(),
        ),
        (
            "T=$(mktemp -d --tmpdir x.XXXX); touch $T/y",
            "/tmp/x.XXXX/y".to_owned(),
        ),
        (
            "T=$(mktemp -p/s/g); touch $T",
            "/s/g/tmp.XXXXXXXXXX".to_owned(),
        ),
        ("cat > $(mktemp)", tmp.to_owned()),
    ] {
        assert_eq!(
            writes(cmd, &m, &m),
            [at(&place, "elsewhere", "named")],
            "{cmd}"
        );
    }
    // no bypass: a `-p` or a template in the mirror is the mirror, named
    for (cmd, place) in [
        (
            format!("T=$(mktemp -d -p {m}); touch $T/x"),
            format!("{m}/tmp.XXXXXXXXXX/x"),
        ),
        (
            format!("T=$(mktemp -d {m}/x.XXXX); touch $T/y"),
            format!("{m}/x.XXXX/y"),
        ),
    ] {
        assert_eq!(
            writes(&cmd, "/tmp", &m),
            [at(&place, "main", "named")],
            "{cmd}"
        );
    }
    // the temp directory is the process's `$TMPDIR` where it is set; `-t` prefers it to `-p`, `-p` to it otherwise
    crate::env::set("TMPDIR", "/td");
    assert_eq!(
        writes("T=$(mktemp -d); touch $T/x", &m, &m),
        [at("/td/tmp.XXXXXXXXXX/x", "elsewhere", "named")]
    );
    assert_eq!(
        writes("T=$(mktemp -t -p /pd x.XXXX); touch $T", &m, &m),
        [at("/td/x.XXXX", "elsewhere", "named")]
    );
    assert_eq!(
        writes("T=$(mktemp -p /pd x.XXXX); touch $T", &m, &m),
        [at("/pd/x.XXXX", "elsewhere", "named")]
    );
    // a relative template, or `-p .`, lands where the shell stands when mktemp runs: unresolved
    for cmd in [
        "T=$(mktemp -d -p .); touch $T/x",
        "T=$(mktemp x.XXXX); touch $T",
    ] {
        assert_eq!(writes(cmd, "/tmp", &m)[0].0, None, "{cmd}");
    }
}

/// THE ONE RULE for a place the walk cannot resolve, every tool alike (451 T79): what the walk knows of it decides - its known
/// directory in the mirror or a clone, there; elsewhere, elsewhere, unless the mirror could lie under it - and where nothing of it
/// is known it lands where the shell was last known (spec 204's D6). Before, a cp's unresolved target went where the shell was
/// last known whatever the walk knew of it, and a git form of T50's twelve was not placed at all.
#[test]
fn an_unresolved_place_is_settled_one_way_for_every_tool() {
    let (_d, m, c) = mirror("unresolved");
    let none = |class, how| (None, class, how);
    // a scratch place with a loop's name in it is scratch (bx#16705 and bx#16727 of T79's broad corpus, refused standing in the
    // mirror when D6 read them, measured 2026-11-21): its literal values resolve it (451 T79's second round) - and a name the walk
    // cannot know (`$RANDOM`, bash's own) under a known start is under it, for a redirect, a cp, a git form and the shell's own
    // place alike - under `/s`, since the test's mirror lies under `/tmp` and `/tmp/$X` could be it
    assert_eq!(
        writes(
            "R=/s/r; for pm in 4 8; do sed s/a/b/ $R/M > $R/M.P$pm; done",
            &m,
            &m
        ),
        [
            at("/s/r/M.P4", "elsewhere", "named"),
            at("/s/r/M.P8", "elsewhere", "named")
        ]
    );
    for (cmd, how) in [
        ("cp /tmp/a /s/$RANDOM/b", "named"),
        ("git clone -q /src/y /s/$RANDOM/c", "named"),
        ("git -C /s/$RANDOM commit -q -m a", "named"),
        ("cd /s/$RANDOM && touch f", "shell"),
        ("cd /s/$RANDOM && git worktree add --detach w", "shell"),
    ] {
        assert_eq!(writes(cmd, &m, &m), [none("elsewhere", how)], "{cmd}");
    }
    // a known directory in the mirror is the mirror, named - never a write moved and still landing there - and a clone's a clone
    assert_eq!(
        writes(&format!("D={m}; cp /tmp/a $D/out.$RANDOM"), "/tmp", &m),
        [none("main", "named")]
    );
    assert_eq!(
        writes(&format!("cp /tmp/a {c}/$RANDOM"), &m, &m),
        [none("clone", "named")]
    );
    let into = walk(
        &format!("cd {m}/$X && git commit -q -m a"),
        Some("/tmp"),
        &m,
        "/home/u",
    );
    assert!(into.cd_into_main);
    assert_eq!(into.targets[0].class, "main");
    // a name no one assigns is empty, as bash reads it (451 T79's second round): `$X/b` is `/b`, and `/$X/b` `//b` (`normpath`
    // keeps two leading slashes, as Python's does; Linux reads it as `/b`)
    for (cmd, place) in [("cp /tmp/a $X/b", "/b"), ("cp /tmp/a /$X/b", "//b")] {
        assert_eq!(
            writes(cmd, &m, &m),
            [at(place, "elsewhere", "named")],
            "{cmd}"
        );
    }
    // a write word of which nothing is known - led by what the walk cannot run, or under `/`, which the mirror lies under - lands
    // where the shell was last known (spec 204's D6; T79's first round read it as not the mirror's, its plan review's block)
    for cmd in [
        "cp /tmp/a $(cat f)/b",
        "cp /tmp/a /$RANDOM/b",
        "mkdir -p $(dirname $F)",
        "touch $(dirname -z /s/x) $(dirname)",
    ] {
        assert!(writes(cmd, &m, &m).iter().all(|w| w.1 == "main"), "{cmd}");
        assert!(
            writes(cmd, "/tmp", &m).iter().all(|w| w.1 == "elsewhere"),
            "{cmd}"
        );
    }
    // `$(pwd)` and `` `pwd` `` are where the shell stands, a word the walk knows: the mirror standing in it, scratch after a `cd`
    // into scratch (the probe of 2026-11-21: `` echo x > `pwd`/f `` read as nothing known passed a write of the mirror)
    for cmd in ["echo x > $(pwd)/f", "echo x > `pwd`/f", "cp /tmp/a $(pwd)"] {
        assert_eq!(writes(cmd, &m, &m)[0].1, "main", "{cmd}");
        assert_eq!(
            writes(&format!("cd /tmp && {cmd}"), &m, &m)[0].1,
            "elsewhere",
            "{cmd}"
        );
    }
    // a whole word unresolved only because a `cd` the walk cannot read moved the shell lands where the shell was last known
    // (spec 204's D6 itself)
    for cmd in [
        "cd \"$X\" && git switch other",
        "cd - && touch f",
        "cd $(somewhere) && git commit -q -m a",
        "read X; cd $X && cp /tmp/a out/$n",
        "read X; cd $X && cp /tmp/a out/$RANDOM",
    ] {
        assert_eq!(writes(cmd, &m, &m)[0].1, "main", "{cmd}");
        assert_eq!(writes(cmd, "/tmp", &m)[0].1, "elsewhere", "{cmd}");
    }
}

#[test]
fn a_brace_expansion_stays_in_its_word() {
    // 451 T79's probe of 2026-11-21: `cp /tmp/{a,b} <mirror>/x` from /tmp passed, its destination cut off at the braces; a brace
    // group's braces still split
    let (_d, m, _c) = mirror("braces");
    assert_eq!(
        writes(&format!("cp /tmp/{{a,b}} {m}/x"), "/tmp", &m),
        [(Some(format!("{m}/x")), "main", "named")]
    );
    assert_eq!(
        writes(&format!("mv /tmp/x{{1,2}} {m}/d/"), "/tmp", &m)
            .last()
            .map(|t| t.1),
        Some("main")
    );
    assert_eq!(
        writes(&format!("{{ cp /tmp/a {m}/x; }}"), "/tmp", &m),
        [(Some(format!("{m}/x")), "main", "named")]
    );
}

#[test]
fn an_unbalanced_parenthesis_ends_the_walk_cleanly() {
    // a `$(` with no `)` runs to the end of the command, and a `)` with no `(` closes nothing (451 T79's `closing`, `walk_in`)
    let (_d, m, _c) = mirror("unbalanced");
    assert_eq!(
        writes("touch /s/a $(true", &m, &m)[0].0.as_deref(),
        Some("/s/a")
    );
    assert_eq!(
        writes("echo a) ; touch /s/x", &m, &m)[0].0.as_deref(),
        Some("/s/x")
    );
}

/// 451 T83: a segment's redirect targets read by the pattern in the regex crate and its lookbehind by hand (`redirects`) are the
/// targets the one fancy pattern read, on every text of up to 5 pieces - a `<` or `>` before a match, a digit, `>>`, `>|`, a
/// blank, a separator and a character of two bytes.
#[test]
fn the_redirect_scan_reads_each_target_as_the_pattern_read_it() {
    let pattern = crate::regex::build(r"(?<![<>])\d?>{1,2}\|?\s*([^\s;&|()<>]+)").unwrap();
    let pieces = ["<", ">", "2", "|", " ", "f", ";", "é", "("];
    let (mut texts, mut longest) = (vec![String::new()], vec![String::new()]);
    for _ in 0..5 {
        longest = longest
            .iter()
            .flat_map(|t| pieces.map(|p| format!("{t}{p}")))
            .collect();
        texts.extend(longest.iter().cloned());
    }
    for text in &texts {
        let old: Vec<&str> = pattern
            .captures_iter(text)
            .map_while(Result::ok)
            .map(|c| c.get(1).map_or("", |m| m.as_str()))
            .collect();
        let scan = super::super::redirects(text);
        assert_eq!(scan, old, "{text:?}");
    }
}
