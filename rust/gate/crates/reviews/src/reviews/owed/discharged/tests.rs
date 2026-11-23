//! A glyph unit the round arbiter's accept discharged (449 T377): recorded bound to its kind's marks, and read so by the owed lookup
//! until they move.

use std::path::{Path, PathBuf};

use l7r_shared::tempdir::Held;

use super::super::super::tests::{commit, compound, drawn, hamlet, put, redraw, repo, sh};
use super::super::{all_owed, cli as owed_cli};
use super::*;

/// Compound `c` at the base: a hall. Now: a kiln new to it, a glyph check owed.
const NOW: &str = r#"<svg><g data-kind="hall"/><g data-kind="kiln"/></svg>"#;
const KILN: &str = "glyph-check--kiln--c";
const WEIR: &str = "glyph-check--weir--h";

/// The compound `c` and the hamlet `h`, each drawn now with an element new to it, and a feature's log holding an accept and a
/// continue.
fn world(name: &str) -> Held<PathBuf> {
    let r = repo(name);
    compound(&r, "c", &["hall"]);
    hamlet(&r, "h", &["paddy"]);
    commit(&r, "the maps");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    redraw(&r, "c", NOW);
    drawn(&r, "h", &["paddy", "weir"]);
    put(
        &r,
        "specs/451-x/arbiter.jsonl",
        "{\"trigger\": \"ask:t\", \"ruling\": \"accept\"}\n{\"trigger\": \"ask:c\", \"ruling\": \"continue\"}\nnot json\n",
    );
    r
}

fn run(root: &Path, args: &[&str]) -> Reply {
    let mut all = vec!["--root".to_owned(), root.display().to_string()];
    all.extend(args.iter().map(|a| (*a).to_owned()));
    cli(&all)
}

fn glyphs(root: &Path) -> Vec<String> {
    all_owed(root)
        .1
        .iter()
        .filter(|u| u.check == "glyph-check")
        .map(Unit::slug)
        .collect()
}

/// RED FIRST (449 T377): an accept named only a unit's discharge in its words, so the unit stayed owed and the push refused it with
/// no verdict record; recorded, it is owed by nothing - the push, `make verify`, the glyph hour - until its kind's marks move.
#[test]
fn an_accept_discharges_a_glyph_unit_until_its_marks_move() {
    let r = world("discharge");
    assert_eq!(glyphs(&r), [KILN, WEIR]);
    let got = run(&r, &["--ruling", "ask:t", KILN]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.starts_with(
        "glyph-check--kiln--c: discharged by ask:t (its marks on c as they read now, "
    ));
    assert_eq!(glyphs(&r), [WEIR]);
    assert_eq!(
        owed_discharged(&r).3,
        [(KILN.to_owned(), "ask:t".to_owned())]
    );
    let why = owed_cli(&[
        "--root".to_owned(),
        r.display().to_string(),
        "--why".to_owned(),
        "--landing".to_owned(),
    ]);
    assert!(why.stdout.contains(
        "glyph checks discharged by the round arbiter's accept, their marks as it bound them (449 T377): glyph-check--kiln--c (ask:t)"
    ));
    let again = run(&r, &["--ruling", "ask:t", KILN]);
    assert_eq!(
        (again.code, again.stdout.as_str()),
        (0, "glyph-check--kiln--c: already discharged by ask:t\n")
    );
    // the kiln redrawn: owed again under the rule
    redraw(&r, "c", &NOW.replace(r#""kiln""#, r#""kiln" fill="x""#));
    assert_eq!(glyphs(&r), [KILN, WEIR]);
}

/// Nothing is recorded unless the ruling is an accept and each unit is a glyph check owed now whose kind's marks bind it.
#[test]
fn a_discharge_is_refused_unless_an_accept_binds_an_owed_glyph_units_marks() {
    let r = world("refused");
    for args in [&[][..], &["--ruling", "ask:t"][..], &["--nonsense"][..]] {
        assert_eq!(run(&r, args).code, 2, "{args:?}");
    }
    let lost = cli(&[
        "--root".to_owned(),
        "/nonexistent/t377".to_owned(),
        "--ruling".to_owned(),
        "ask:t".to_owned(),
        KILN.to_owned(),
    ]);
    assert_eq!(lost.code, 1);
    let why = |args: &[&str]| {
        let got = run(&r, args);
        assert_eq!(got.code, 1, "{args:?}");
        got.stderr
    };
    assert!(
        why(&["--ruling", "ask:none", KILN]).contains("no feature's arbiter.jsonl holds ask:none")
    );
    assert!(why(&["--ruling", "ask:c", KILN])
        .contains("ask:c ruled continue: only an accept discharges"));
    let other = all_owed(&r)
        .1
        .into_iter()
        .find(|u| u.check != "glyph-check")
        .unwrap()
        .slug();
    let all = why(&[
        "--ruling",
        "ask:t",
        KILN,
        "glyph-check--well--c",
        WEIR,
        &other,
    ]);
    assert!(all.contains("glyph-check--well--c is not owed now"));
    assert!(all.contains("glyph-check--weir--h: h draws no mark of weir read by kind"));
    assert!(all.contains(&format!("{other} is a ")));
    // one refused, none recorded
    assert_eq!(glyphs(&r), [KILN, WEIR]);
}

/// A record whose ruling is no accept, whose feature holds no such ruling, or that cannot be read discharges nothing.
#[test]
fn a_record_that_does_not_stand_discharges_nothing() {
    let r = world("unstanding");
    let marks = marks::digest(&marks::read(NOW), "kiln").unwrap();
    let at = format!(".git/review-verdicts/{KILN}{SUFFIX}");
    for (ruling, feature) in [("ask:c", "specs/451-x"), ("ask:t", "specs/452-gone")] {
        let rec = json!({"ruling": ruling, "feature": feature, "marks": marks});
        put(&r, &at, &rec.to_string());
        assert_eq!(glyphs(&r), [KILN, WEIR], "{ruling} {feature}");
    }
    put(&r, &at, "not json");
    assert_eq!(glyphs(&r), [KILN, WEIR]);
    // the same record with its accept: it stands
    let rec = json!({"ruling": "ask:t", "feature": "specs/451-x", "marks": marks});
    put(&r, &at, &rec.to_string());
    assert_eq!(glyphs(&r), [WEIR]);
}
