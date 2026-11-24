use std::path::Path;

use serde_json::{json, Map, Value};

use super::{hold, SEARCHED};

fn put(root: &Path, rel: &str, text: &str) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

const KITCHENS: &str = "0107-kitchens-daidokoro.html";
const GENKAN: &str = "0104-the-formal-entrance-genkan.html";
const HOUSES: &str = "0091-samurai-residences.html";
const GRAVES: &str = "0235-burial-grounds.drawing.html";

/// A record of four pages, one of them (0107) saying what 449's found row 210 said no page says; a notes file, which is no page.
fn record(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    let q = "research/questions";
    put(&root, &format!("{q}/{KITCHENS}"), "<h1>Kitchens (daidokoro)</h1>\n<ul><li>The kitchen door (katteguchi) is recorded, often at the rear of the house.</li></ul>\n");
    put(&root, &format!("{q}/{GENKAN}"), "<h1>The formal entrance (genkan)</h1>\n<p>The katteguchi leads from outside into the kitchen.</p>\n");
    put(&root, &format!("{q}/{HOUSES}"), "<h1>Samurai residences</h1>\n<p>At the Miwa house a back door stands by the kitchen.</p>\n");
    put(
        &root,
        &format!("{q}/{GRAVES}"),
        "<h1>Burial grounds</h1>\n<p>The rows of grave markers are a map drawing convention.</p>\n",
    );
    put(
        &root,
        &format!("{q}/0107-kitchens-daidokoro.notes.html"),
        "<p>kitchen door rear house frequency katteguchi</p>\n",
    );
    root
}

fn bundle(root: &Path, pages: &[&str]) -> std::path::PathBuf {
    let b = root.join("b");
    for p in pages {
        put(&b, &format!("questions/{p}.txt"), "the page\n");
    }
    b
}

fn units() -> Map<String, Value> {
    json!({
        "docs/buildings.md::Graves#the marker's size": {"claim": "the grave marker's size - GUESS: about 2 by 1 ft"},
        "a::b#c": {},
    })
    .as_object()
    .unwrap()
    .clone()
}

/// Feature 449's found row 210 (452 T22), as the check writes it under the effect form: the cited pages do not say the kitchen
/// door is often at the rear, and 0107, which the section did not cite, says it.
const ROW_210: &str = "- docs/building-programs.md | required-items table, `kitchen` row | the row says the kitchen door \"is recorded, often at the rear of the house\", but none of the pages this section cites says so: 0104 gives only that the katteguchi leads from outside into the kitchen | effect: map - the kitchen pop-up states as recorded a frequency these pages do not attest";

#[test]
fn a_silent_finding_waits_for_the_record_s_nearest_pages() {
    let root = record("claims-silent-held");
    let (q, store) = (root.join("research/questions"), root.join(SEARCHED));
    let b = bundle(&root, &[GENKAN, HOUSES]);
    let reply = format!("VERDICT a::b#c IN-STEP - fine [§1]\n\n## OUTSIDE THE CHANGE\n{ROW_210}\n");
    let (kept, held) = hold(&reply, &units(), &q, &b, &store).unwrap();
    // the row is neither recorded nor filed: it is out of the reply, and the page that says it is named
    assert!(!kept.contains("kitchen") && kept.contains("VERDICT a::b#c IN-STEP"));
    assert_eq!(held.len(), 2, "{held:?}");
    assert!(
        held[0].starts_with(&format!("HELD line - it says the pages are silent, and the record's nearest pages for its words are not in the bundle ({KITCHENS}): - docs/building-programs.md | required-items table")),
    );
    assert_eq!(
        held[1],
        format!("a held line is neither recorded nor filed (451 T218): judge the bundle again with those pages in it - make claims-bundle UNITS=\"docs/buildings.md::Graves#the marker's size,a::b#c\" PAGES=\"{HOUSES},{GENKAN},{KITCHENS}\" REASON=\"the record searched before a silent finding is filed\" - where a page says it, the finding is a citation fix or nothing; where none does, the line is recorded as written")
    );
    let was = std::fs::read_to_string(&store).unwrap();
    assert!(was.contains("docs/building-programs.md") && was.contains(KITCHENS));
    // judged again with the pages in the bundle, a line on that file is recorded as written whatever its words now are (one
    // hold a search: a reworded reply's own nearest page, the graves', is not asked for), and the search is forgotten
    let b = bundle(&root, &[KITCHENS]);
    let again = "## OUTSIDE THE CHANGE\n- `docs/building-programs.md` | the kitchen row | no page gives the grave markers their rows | effect: page - its reader is told a frequency no page gives\n";
    let (kept, held) = hold(again, &units(), &q, &b, &store).unwrap();
    assert!(held.is_empty() && kept == again);
    assert_eq!(std::fs::read_to_string(&store).unwrap().trim(), "{}");
    // the second reading dropped the finding (0107 says it): the search is forgotten all the same, so a later silent line on
    // that file is searched for its own words
    let fresh = record("claims-silent-dropped");
    let (q, store) = (fresh.join("research/questions"), fresh.join(SEARCHED));
    let lacking = bundle(&fresh, &[GENKAN, HOUSES]);
    assert_eq!(
        hold(&reply, &units(), &q, &lacking, &store)
            .unwrap()
            .1
            .len(),
        2
    );
    let full = bundle(&fresh, &[KITCHENS]);
    let (kept, held) = hold(
        "VERDICT a::b#c IN-STEP - fine [§1]",
        &units(),
        &q,
        &full,
        &store,
    )
    .unwrap();
    assert!(held.is_empty() && kept.starts_with("VERDICT"));
    assert_eq!(std::fs::read_to_string(&store).unwrap().trim(), "{}");
}

#[test]
fn a_truly_silent_finding_is_recorded_once_the_nearest_pages_were_read() {
    let root = record("claims-silent-true");
    let (q, store) = (root.join("research/questions"), root.join(SEARCHED));
    // 449 T411 (452 T011): no page gives the grave marker's 2 by 1 ft
    let reply = "VERDICT docs/buildings.md::Graves#the marker's size NEEDS-RESEARCH - 0235's drawing page calls the rows of markers a convention and gives no size [§]\n";
    let bare = bundle(&root, &[]);
    let (kept, held) = hold(reply, &units(), &q, &bare, &store).unwrap();
    assert!(kept.is_empty() && held[0].contains(GRAVES), "{held:?}");
    let b = bundle(&root, &[GRAVES, KITCHENS, GENKAN, HOUSES]);
    let (kept, held) = hold(reply, &units(), &q, &b, &store).unwrap();
    assert!(held.is_empty() && kept == reply, "{held:?}");
}

#[test]
fn only_a_finding_that_says_the_pages_are_silent_is_held() {
    let root = record("claims-silent-not");
    let (q, store) = (root.join("research/questions"), root.join(SEARCHED));
    let b = bundle(&root, &[]);
    let reply = [
        // a pass, a drift that names what a page says, a claim of another bundle (refused by the vet), and a silent drift
        "VERDICT a::b#c IN-STEP - the pages are silent on it, so GUESS is right [§]",
        "VERDICT a::b#c DRIFTED - the kitchen is drawn 9 ft deep where the page gives 12; fix: code; effect: a short kitchen [§2]",
        "VERDICT z::y#x NEEDS-RESEARCH - no page says [§]",
        "## OUTSIDE THE CHANGE",
        // an outside line naming no effect is dropped unfiled (451 T219), so nothing is searched for it
        "- docs/x.md | the kitchen | none of the pages says the kitchen door is at the rear",
        "- docs/x.md | the kitchen | the kitchen door is drawn at the front | effect: sheet - a door on the wrong wall",
        "- not a row",
        "plain words",
        "## NOTED, NOT FILED",
        "- docs/x.md | the kitchen | no page gives the kitchen door | effect: page - past the heading, no outside row",
    ]
    .join("\n");
    let (kept, held) = hold(&reply, &units(), &q, &b, &store).unwrap();
    assert!(held.is_empty() && kept == reply, "{held:?}");
    assert!(!store.exists());
    let silent = "VERDICT a::b#c MISLABELED - the cited page does not say how deep the kitchen ran; fix: claim [§3]";
    let (kept, held) = hold(silent, &units(), &q, &b, &store).unwrap();
    assert!(kept.is_empty() && held[0].contains(KITCHENS), "{held:?}");
}
