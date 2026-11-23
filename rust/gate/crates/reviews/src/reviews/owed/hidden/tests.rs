//! The units a map not current hides, on scratch repositories (451 T164): the stale engine named, the last drawing's new elements named.

use std::path::PathBuf;

use super::super::super::tests::{commit, compound, hamlet, put, repo, sh};
use super::super::all_owed;
use super::*;

/// RED FIRST (451 T164): a Mode A binary older than its sources left every compound not current, and the problem said only "not current"
/// - the 449 T289 bundle's genkan units dropped with no word of the engine or of them. Now the line names the engine and the units.
#[test]
fn a_stale_engine_is_named_with_the_units_it_hides() {
    let r = repo("hidden-stale");
    compound(&r, "c", &["gate"]);
    commit(&r, "sheet");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    compound(&r, "c", &["gate", "genkan"]);
    put(&r, ".git/stale-mode-a", "");
    let (_, units, problems) = all_owed(&r);
    assert!(units.is_empty(), "{units:?}");
    assert_eq!(problems.len(), 1, "{problems:?}");
    let line = &problems[0];
    for want in [
        "the mode-a engine's binary is older than its sources",
        "glyph-check--genkan--c, size-audit--genkan",
    ] {
        assert!(line.contains(want), "{want} not in {line}");
    }
    // drawn as its base was: nothing shown, still hidden, and said so
    compound(&r, "c", &["gate"]);
    let line = &all_owed(&r).2[0];
    let said = "HIDDEN until it is drawn (its last drawing holds none its base lacks)";
    assert!(line.contains(said), "{line}");
}

/// A hamlet not current whose record keeps no census shows no units, and its unclassed ink is no element.
#[test]
fn a_hamlet_with_no_census_hides_what_it_cannot_show() {
    let r = repo("hidden-hamlet");
    hamlet(&r, "m", &["well"]);
    commit(&r, "map");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    hamlet(&r, "m", &["well", "-"]);
    put(&r, ".git/stale-hamlet", "");
    let line = &all_owed(&r).2[0];
    let stale = line.contains("the hamlet engine's binary is older");
    assert!(stale, "{line}");
    assert!(line.contains("holds none its base lacks"), "{line}");
    put(&r, "pool/hamlets/m/m.driver.json", "{}");
    let folder = l7r_gate_pool::walk(&r).folder("m").unwrap().clone();
    assert!(last_drawing(&Folder::from(folder)).is_empty());
}

/// Each engine is asked once a run; a folder no engine draws asks none.
#[test]
fn each_engine_is_asked_once() {
    struct Counted(std::rc::Rc<std::cell::Cell<u32>>);
    impl Binaries for Counted {
        fn binary(&mut self, _: Engine) -> Result<PathBuf, String> {
            self.0.set(self.0.get() + 1);
            Err("stale".to_owned())
        }
    }
    let n = std::rc::Rc::new(std::cell::Cell::new(0));
    let mut e = Engines::with(Box::new(Counted(n.clone())));
    assert_eq!(e.stale(Kind::Compound).as_deref(), Some("stale"));
    assert_eq!(e.stale(Kind::HandSheet).as_deref(), Some("stale"));
    assert_eq!(e.stale(Kind::Frozen), None);
    assert_eq!(n.get(), 1);
}
