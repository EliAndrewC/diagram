//! The claims sheet over a scratch mirror and clone: what is live, a claim recorded or refused, a release, the sweep of closed features,
//! and every refusal and raise of the command.

use std::path::{Path, PathBuf};

use super::{
    asked, claim, cli, live, mirror, old_map, parse, query, settled_features, sheet, sweep, Ask,
    Env, SHEET,
};

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

fn put(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

/// A mirror with one clone `me` in git, its gate script, two features closed (one in the mirror, one in the clone) and one open, and
/// feature 303's move record naming an old page's section (the question's path built from parts: no research pointer in a fixture).
fn world(tag: &str) -> (l7r_guard::shared::tempdir::TempDir, PathBuf) {
    let d = l7r_gate_core::ci::fixtures::scratch(tag);
    let top = std::fs::canonicalize(&*d).unwrap().join(".clones/me");
    std::fs::create_dir_all(&top).unwrap();
    l7r_gate_core::record::testkit::git(&top, &["init", "-q"]);
    let mirror = top.parent().unwrap().parent().unwrap().to_path_buf();
    put(&mirror, "specs/376-done/tasks.md", "- [x] T1\n");
    put(&top, "specs/377-open/tasks.md", "- [ ] T1\n");
    put(&top, "specs/378-closed/tasks.md", "- [x] T1\n");
    put(&top, "specs/379-file", "");
    put(&top, "specs/notes.md", "");
    put(&top, "scripts/gates/l7r-gate.sh", "#!/bin/sh\n");
    {
        use std::os::unix::fs::PermissionsExt as _;
        std::fs::set_permissions(
            top.join("scripts/gates/l7r-gate.sh"),
            std::fs::Permissions::from_mode(0o755),
        )
        .unwrap();
    }
    let q = ["research", "questions", "0091-old.html"].join("/");
    put(
        &top,
        "research/moved-303.json",
        &format!("{{\"files\": {{\"buildings/240-a.html\": \"{q}\", \"buildings/250-b.html\": \"elsewhere\", \"x\": 1}}}}"),
    );
    (d, top)
}

// feature 449 T137: the old page-and-number item is built from parts, so the research-pointer check reads no retired pointer here
const SHEET_TEXT: &str = concat!(
    "# owner | feature | item\n\
other | 376 | Q=0060 | in progress | 2026-10-01\n\
other | 377 | build",
    "ings 240 and 250 | in progress | 2026-10-01\n\
me | 378 | Q=0070,0071 | in progress | 2026-10-02\n\
gone | 376 | Q=0080 | in progress | 2026-10-01\n\
gone | 376 | Q=0080 | done | 2026-10-03\n\
short | 376\n"
);

#[test]
fn a_line_reads_as_its_cells_and_the_live_claims_are_each_owners_latest() {
    assert_eq!(parse("# a | b | c"), None);
    assert_eq!(parse("a | b"), None);
    let row = parse(" a | 376 | Q=0060 ").unwrap();
    assert_eq!(
        (row.owner.as_str(), row.status.as_str(), row.date.as_str()),
        ("a", "", "")
    );
    let (_d, top) = world("claims-live");
    let lines: Vec<&str> = SHEET_TEXT.lines().collect();
    let held = live(&lines, &top);
    assert_eq!(
        held.keys().collect::<Vec<_>>(),
        ["0060", "0070", "0071", "0091"]
    );
    assert_eq!(held["0091"][0].feature, "377");
    assert_eq!(old_map(&top).len(), 1);
    assert!(old_map(Path::new("/no/such")).is_empty());
    assert_eq!(mirror(&top), top.parent().unwrap().parent().unwrap());
    assert_eq!(mirror(Path::new("/a/b")), Path::new("/a/b"));
    assert_eq!(sheet(None), Path::new(SHEET));
    assert_eq!(sheet(Some(String::new())), Path::new("."));
    assert_eq!(asked("0246, 0060 0060").unwrap(), ["0060", "0246"]);
    assert!(asked("none")
        .unwrap_err()
        .starts_with("research-claims: Q= names no question"));
}

#[test]
fn a_query_a_claim_a_refusal_and_a_release() {
    let (d, top) = world("claims-claim");
    let s = d.join("sheet/RESEARCH-CLAIMS.md");
    let q = |qs: &[&str]| query(&args(qs), &top, &s);
    assert_eq!(
        q(&["0060"]),
        (0, "research-claims: no live claim on 0060".to_owned())
    );
    put(&d, "sheet/RESEARCH-CLAIMS.md", SHEET_TEXT);
    assert_eq!(
        q(&["0060", "0070"]),
        (
            1,
            "research-claims: 2 live claim(s) on 0060 0070:\n  other | 376 | Q=0060 | in progress | 2026-10-01\n  me | 378 | Q=0070,0071 | in progress | 2026-10-02"
                .to_owned()
        )
    );
    assert_eq!(q(&["0070", "0071"]).1.lines().count(), 2);
    let qs = args(&["0060", "0099"]);
    let ask = |status: &'static str, release: &'static str, why: &'static str| Ask {
        qs: &qs,
        feature: "449",
        status,
        release,
        why,
    };
    let refused = claim(&ask("in progress", "", ""), &top, &s, "2026-11-14").unwrap();
    assert_eq!(refused.0, 1);
    assert!(refused.1.starts_with(
        "research-claim: REFUSED - another session holds 1 of these:\n  other | 376 | Q=0060"
    ));
    assert_eq!(
        claim(&ask("done", "", ""), &top, &s, "2026-11-14").unwrap(),
        (
            0,
            "research-claim: recorded - me | 449 | Q=0060,0099 | done | 2026-11-14".to_owned()
        )
    );
    assert_eq!(claim(&ask("x", "other", ""), &top, &s, "d").unwrap().0, 2);
    assert_eq!(
        claim(&ask("x", "other", "its session is gone"), &top, &s, "d").unwrap().1,
        "research-claim: recorded - other | 449 | Q=0060,0099 | released by me: its session is gone | d"
    );
    assert_eq!(q(&["0060"]).0, 0);
    let mine = args(&["0070"]);
    let ok = claim(
        &Ask {
            qs: &mine,
            feature: "449",
            status: "in progress",
            release: "",
            why: "",
        },
        &top,
        &s,
        "d",
    )
    .unwrap();
    assert_eq!(ok.0, 0);
}

#[test]
fn the_sweep_releases_each_live_claim_of_a_closed_feature() {
    let (d, top) = world("claims-sweep");
    let mut settled: Vec<String> = settled_features(&top).into_iter().collect();
    settled.sort();
    assert_eq!(settled, ["376", "378"]);
    let s = d.join("RESEARCH-CLAIMS.md");
    std::fs::write(&s, SHEET_TEXT).unwrap();
    assert_eq!(
        sweep(&top, &s, "2026-11-14").unwrap(),
        "research-claims sweep: 2 release line(s) for 3 claim(s) of closed features"
    );
    let text = std::fs::read_to_string(&s).unwrap();
    assert!(text.ends_with(
        "me | 378 | Q=0070,0071 | released by me: feature 378 is closed (make speckit-todo) | 2026-11-14\n\
         other | 376 | Q=0060 | released by me: feature 376 is closed (make speckit-todo) | 2026-11-14\n"
    ));
    assert_eq!(
        sweep(&top, &s, "d").unwrap(),
        "research-claims sweep: 0 release line(s) for 0 claim(s) of closed features"
    );
    // a broken vocabulary, no gate of its own, or no feature directories at all: nothing is closed
    put(&top, ".specify/affects.json", "{");
    assert!(settled_features(&top).is_empty());
    std::fs::remove_file(top.join(".specify/affects.json")).unwrap();
    std::fs::remove_file(top.join("scripts/gates/l7r-gate.sh")).unwrap();
    assert!(settled_features(&top).is_empty());
    assert!(settled_features(&d.join("nothing")).is_empty());
}

#[test]
fn a_lock_or_a_write_that_fails_is_the_python_s_raise() {
    let (d, top) = world("claims-raise");
    put(&d, "file", "");
    let under_file = d.join("file/RESEARCH-CLAIMS.md");
    let qs = args(&["0060"]);
    let ask = Ask {
        qs: &qs,
        feature: "449",
        status: "in progress",
        release: "",
        why: "",
    };
    assert!(claim(&ask, &top, &under_file, "d").is_err());
    assert!(sweep(&top, &under_file, "d").is_err());
    std::fs::create_dir_all(d.join("lockdir/s.md.lock")).unwrap();
    assert!(claim(&ask, &top, &d.join("lockdir/s.md"), "d").is_err());
    std::fs::create_dir_all(d.join("sheetdir/s.md")).unwrap();
    assert!(claim(&ask, &top, &d.join("sheetdir/s.md"), "d").is_err());
}

#[test]
fn the_command_answers_as_argparse_and_the_tool_did() {
    let (d, top) = world("claims-cli");
    let s = d.join("s.md");
    let env = Env {
        cwd: top.clone(),
        sheet: s.clone(),
        today: || "2026-11-14".to_owned(),
    };
    let run = |a: &[&str]| cli(&args(a), &env);
    for (bad, why) in [
        (vec![], "the following arguments are required: op"),
        (
            vec!["nope"],
            "argument op: invalid choice: 'nope' (choose from claim, query, sweep)",
        ),
        (
            vec!["claim", "0060", "extra"],
            "unrecognized arguments: extra",
        ),
    ] {
        let got = run(&bad);
        assert_eq!(got.code, 2);
        assert!(
            got.stderr.ends_with(&format!("error: {why}\n")),
            "{}",
            got.stderr
        );
    }
    assert_eq!(run(&["query", "x"]).code, 1);
    assert_eq!(
        run(&["query", "0060"]).stdout,
        "research-claims: no live claim on 0060\n"
    );
    assert_eq!(
        run(&["claim", "0060"]).stderr,
        "research-claim: FEATURE=<number> is required - the feature the work belongs to\n"
    );
    let ok = run(&["claim", "0060", "--feature", "449"]);
    assert_eq!(
        ok.stdout,
        "research-claim: recorded - me | 449 | Q=0060 | in progress | 2026-11-14\n"
    );
    assert_eq!(
        run(&["claim", "0060", "--feature=449", "--release", "x"]).code,
        2
    );
    assert!(run(&["sweep"])
        .stdout
        .starts_with("research-claims sweep: 0 release line(s)"));
    put(&d, "file", "");
    let broken = Env {
        cwd: top.clone(),
        sheet: d.join("file/s.md"),
        today: d_day,
    };
    assert_eq!(cli(&args(&["sweep"]), &broken).code, 1);
    assert_eq!(
        cli(&args(&["claim", "0060", "--feature", "449"]), &broken).code,
        1
    );
    // another session's claim, refused on stderr with exit 1
    std::fs::write(&s, "other | 376 | Q=0061 | in progress | d\n").unwrap();
    let refused = run(&["claim", "0061", "--feature", "449"]);
    assert_eq!((refused.code, refused.stdout.as_str()), (1, ""));
    let outside = Env {
        cwd: PathBuf::from("/"),
        sheet: s,
        today: d_day,
    };
    assert_eq!(cli(&args(&["query", "0061"]), &outside).code, 0);
}

fn d_day() -> String {
    "d".to_owned()
}
