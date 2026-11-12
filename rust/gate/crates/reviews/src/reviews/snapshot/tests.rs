//! The reviewer's snapshot on scratch clones: every check's prompt, each side copied or lacking, the stale renders, every refusal and
//! raise (feature 449 T132). The same outputs as `scripts/reviews/review_snapshot.py` are the differential's (`scratchpad/t132/`);
//! these pin the branches.

use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

use super::super::owed::Unit;
use super::super::tests::{dir, map, put, repo, sheet};
use super::{cli, copy2, flag_like, map_dir, mtime, parse, snapshot, stale_renders};

fn unit(check: &str, subject: &str, on: &str) -> Unit {
    Unit {
        check: check.to_owned(),
        subject: subject.to_owned(),
        on: on.to_owned(),
        occasion: "an occasion".to_owned(),
    }
}

fn words(w: &[&str]) -> Vec<String> {
    w.iter().map(|s| (*s).to_owned()).collect()
}

/// Set `rel`'s modification time `ago` seconds before now.
fn aged(root: &Path, rel: &str, ago: u64) {
    let at = SystemTime::now() - Duration::from_secs(ago);
    std::fs::File::open(root.join(rel))
        .unwrap()
        .set_times(std::fs::FileTimes::new().set_modified(at))
        .unwrap();
}

#[test]
fn an_owed_map_is_snapshot_from_the_clone_and_the_mirror() {
    let main = dir("snapshot-main");
    let clone = main.join(".clones/c");
    std::fs::create_dir_all(&clone).unwrap();
    let held = repo("snapshot-clone");
    // the clone is a repository under main's `.clones/`, so main is read as its mirror
    std::fs::rename(&*held, &clone).unwrap();
    std::fs::create_dir_all(&*held).unwrap();
    map(&clone, "pool", "m", &["house"]);
    put(&clone, "pool/hamlets/m/m.png", "png");
    map(&main, "pool", "m", &["house"]);
    put(&main, "pool/hamlets/m/m.html", "html");
    let r = clone.to_string_lossy().into_owned();
    // a stale render named first: the clone's map has no .html
    let stale = cli(&words(&[
        "--root",
        &r,
        "--stale-renders",
        "settlement-review--m",
    ]));
    assert_eq!(
        (stale.code, stale.stdout.as_str()),
        (0, "pool/hamlets/m/m.gen.py\n")
    );
    let got = cli(&words(&[
        "--ro",
        &r,
        "--key=k1",
        "settlement-review--m",
        "settlement-review--m",
    ]));
    assert_eq!(got.code, 0, "{}", got.stderr);
    let snap = clone.join(".git/review-snapshot/settlement-review--m");
    let line = format!(
        "snapshot settlement-review--m (on m): clone {}/clone (missing in the clone: .svg .html .notes.md - regenerate it with make map) | main {}/main | prompt {}/dispatch.md\n",
        snap.display(),
        snap.display(),
        snap.display()
    );
    assert_eq!(got.stdout, format!("{line}{line}"));
    assert_eq!(
        std::fs::read_to_string(snap.join("clone/m.png")).unwrap(),
        "png"
    );
    assert_eq!(
        std::fs::read_to_string(snap.join("main/m.html")).unwrap(),
        "html"
    );
    let prompt = std::fs::read_to_string(snap.join("dispatch.md")).unwrap();
    assert!(prompt.starts_with("UNIT: settlement-review--m\nsettlement-review - the WHOLE-MAP review of m: a map new to the pool."));
    assert!(prompt.contains("Engine key: k1."));
    assert!(prompt.contains("/clone  (missing in the clone: .svg .html .notes.md - regenerate it with make map)\n  before (main):     "));
    // a named mirror with no such map, and no key
    let other = dir("snapshot-other");
    let got = cli(&words(&[
        "--root",
        &r,
        "--mirror",
        &other.to_string_lossy(),
        "--",
        "settlement-review--m",
    ]));
    assert!(got
        .stdout
        .contains("| main unavailable (no mirror, or main has no such map) |"));
    assert!(std::fs::read_to_string(snap.join("dispatch.md"))
        .unwrap()
        .contains("Engine key: not computed."));
    assert!(!snap.join("main").exists());
    // a slug not owed is refused by name, the snapshot untouched
    let refused = cli(&words(&["--root", &r, "settlement-review--m", "nope", "x"]));
    assert_eq!(
        (refused.code, refused.stderr.as_str()),
        (2, "_review_snapshot: not owed by this delta: nope x\n")
    );
}

#[test]
fn each_check_is_asked_its_own_question() {
    let root = dir("snapshot-checks");
    sheet(&root, "pool", "s", &["bench"]);
    put(&root, "pool/compounds/s/s.png", "png");
    std::fs::create_dir_all(root.join(".git")).unwrap();
    let units = [
        unit("building-review", "s", "s"),
        unit("glyph-check", "it's", "s"),
        unit("size-audit", "bench", "s"),
        unit("fix-check", "s", "s"),
        unit("glyph-check", "well", ""),
    ];
    let refs: Vec<&Unit> = units.iter().collect();
    let lines = snapshot(&root, None, &refs, "").unwrap();
    // a sheet lacks no manifest; the render it has is copied
    assert!(
        lines[0].contains("(missing in the clone: .html .notes.md - regenerate it with make map)")
    );
    assert!(lines[4].starts_with(
        "snapshot glyph-check--well (on ?): clone not in the clone's pool | main unavailable"
    ));
    let prompt = |slug: &str| {
        std::fs::read_to_string(
            root.join(".git/review-snapshot")
                .join(slug)
                .join("dispatch.md"),
        )
        .unwrap()
    };
    assert!(prompt("building-review--s")
        .contains("give it severity `outside` and judge the verdict on the change alone.\n"));
    assert!(prompt("glyph-check--it-s--s")
        .contains("the glyph check of the element \"it's\", on s: an occasion."));
    assert!(prompt("size-audit--bench").contains("the size audit of 'bench' on s"));
    assert!(prompt("fix-check--s").contains("the fix check on s: an occasion. Answer"));
    let well = prompt("glyph-check--well");
    assert!(well.contains("on no map draws it"));
    assert!(well.contains("after (the clone): not in the clone's pool\n"));
    // a check with no prompt raises after its copies, as the Python's KeyError did
    let odd = unit("odd-check", "s", "s");
    let raised = snapshot(&root, None, &[&odd], "").unwrap_err();
    assert_eq!(raised, "KeyError: 'odd-check'");
    assert!(root
        .join(".git/review-snapshot/odd-check--s/clone/s.svg")
        .is_file());
    // a snapshot that cannot be cleared or written raises
    std::fs::remove_dir_all(root.join(".git")).unwrap();
    std::fs::write(root.join(".git"), "gitdir: x\n").unwrap();
    assert!(snapshot(&root, None, &refs, "")
        .unwrap_err()
        .starts_with("OSError"));
}

#[test]
fn the_stale_renders_are_the_generators_whose_render_is_older() {
    let root = dir("snapshot-stale");
    map(&root, "pool", "a", &[]);
    for rel in ["pool/hamlets/a/a.png", "pool/hamlets/a/a.html"] {
        put(&root, rel, "r");
    }
    aged(&root, "pool/hamlets/a/a.gen.py", 100);
    aged(&root, "pool/hamlets/a/a.json", 100);
    sheet(&root, "legacy-hand-authored-pool", "s", &[]);
    sheet(&root, "pool", "t", &[]);
    put(&root, "pool/compounds/t/t.png", "png");
    let (a, s, t, none) = (
        unit("x", "a", "a"),
        unit("x", "s", "s"),
        unit("x", "t", "t"),
        unit("x", "n", ""),
    );
    let gone = unit("x", "g", "g");
    assert!(
        stale_renders(&root, &[&a, &s, &t, &none, &gone]).unwrap()
            == ["sheet:legacy-hand-authored-pool/compounds/s/s.svg"]
    );
    // a render older than the manifest, listed once however often it is asked
    aged(&root, "pool/hamlets/a/a.html", 200);
    assert_eq!(
        stale_renders(&root, &[&a, &a]).unwrap(),
        ["pool/hamlets/a/a.gen.py"]
    );
    std::fs::remove_file(root.join("pool/hamlets/a/a.json")).unwrap();
    assert_eq!(stale_renders(&root, &[&a]).unwrap().len(), 1);
    assert!(mtime(&root.join("none"))
        .unwrap_err()
        .starts_with("FileNotFoundError"));
    // a time before the epoch is a negative float, as `st_mtime` is
    std::fs::File::open(root.join("pool/hamlets/a/a.gen.py"))
        .unwrap()
        .set_times(
            std::fs::FileTimes::new()
                .set_modified(std::time::UNIX_EPOCH - Duration::from_millis(1500)),
        )
        .unwrap();
    assert!((mtime(&root.join("pool/hamlets/a/a.gen.py")).unwrap() + 1.5).abs() < 1e-9);
    assert!(copy2(&root.join("none"), &root.join("x"))
        .unwrap_err()
        .starts_with("OSError"));
    // `*` matches a dot folder, and the first in sorted order wins
    put(&root, "pool/.h/a/x", "");
    assert_eq!(map_dir(&root, "a"), Some(root.join("pool/.h/a")));
    assert_eq!(map_dir(&root, "zz"), None::<PathBuf>);
}

#[test]
fn the_command_line_is_read_as_argparse_reads_it() {
    let ok = parse(&words(&[
        "--root",
        "r",
        "--mirror=m",
        "--k",
        "-5",
        "--stale",
        "a",
        "b",
    ]))
    .unwrap();
    assert_eq!(
        (
            ok.root.as_deref(),
            ok.mirror.as_deref(),
            ok.key.as_str(),
            ok.stale,
            ok.units
        ),
        (Some("r"), Some("m"), "-5", true, words(&["a", "b"]))
    );
    for (w, why) in [
        (&["a"][..], "the following arguments are required: --root"),
        (
            &["--root", "r"],
            "the following arguments are required: units",
        ),
        (&[], "the following arguments are required: --root, units"),
        (&["--root"], "argument --root: expected one argument"),
        (
            &["--root", "--key"],
            "argument --root: expected one argument",
        ),
        (
            &["--root", "r", "a", "--key", "k", "b"],
            "unrecognized arguments: b",
        ),
        (&["--root", "r", "-x", "a"], "unrecognized arguments: -x"),
        (
            &["--root", "r", "--stale-renders=1", "a"],
            "argument --stale-renders: ignored explicit argument",
        ),
        (
            &["--", "--root", "r"],
            "the following arguments are required: --root",
        ),
    ] {
        assert_eq!(parse(&words(w)).err().as_deref(), Some(why), "{w:?}");
    }
    assert!(parse(&words(&["--root", "r", "--", "-a"])).is_ok());
    assert!(parse(&words(&["--root", "r", "-1.5", "- a"])).is_ok());
    assert!(
        !flag_like("--root x")
            && flag_like("--root")
            && !flag_like("-x y")
            && !flag_like("-.5")
            && flag_like("-5.")
            && flag_like("-1e5")
    );
    let help = cli(&words(&["-h"]));
    assert_eq!((help.code, help.stderr.as_str()), (0, ""));
    assert_eq!(cli(&words(&["--help=x"])).code, 2);
    let bad = cli(&words(&["--root", "r"]));
    assert_eq!((bad.code, bad.stdout.as_str()), (2, ""));
    assert!(bad.stderr.starts_with("l7r-gate reviews snapshot: "));
}

#[test]
fn a_raise_is_a_trace_and_exit_one() {
    let held = repo("snapshot-raise");
    let root: &Path = &held;
    map(root, "pool", "m", &[]);
    std::fs::create_dir_all(root.join(".git/review-snapshot/settlement-review--m")).unwrap();
    std::fs::write(root.join(".git/review-snapshot/settlement-review--m/x"), "").unwrap();
    let r = root.to_string_lossy().into_owned();
    // the clone's `.git` read-only: the old snapshot cannot be cleared
    let snaps = root.join(".git/review-snapshot");
    std::fs::set_permissions(&snaps, std::os::unix::fs::PermissionsExt::from_mode(0o555)).unwrap();
    let got = cli(&words(&["--root", &r, "settlement-review--m"]));
    std::fs::set_permissions(&snaps, std::os::unix::fs::PermissionsExt::from_mode(0o755)).unwrap();
    assert_eq!((got.code, got.stdout.as_str()), (1, ""));
    assert!(got
        .stderr
        .starts_with("Traceback (most recent call last):\n  l7r-gate reviews snapshot\nOSError"));
    // renders newer than the map: nothing stale, one empty line as `print("")` wrote
    put(root, "pool/hamlets/m/m.png", "p");
    put(root, "pool/hamlets/m/m.html", "h");
    let fine = cli(&words(&[
        "--root",
        &r,
        "--stale-renders",
        "settlement-review--m",
    ]));
    assert_eq!(fine.stdout, "\n");
}
