//! `record site`, `site-stale` and `check` (feature 449 T148): each answer `record_asset.py`'s, `record_build.py`'s and `memo_check.py`'s
//! on the same tree; the pages themselves are pinned in `record/site/tests.rs`.

use super::{check, run, stale};
use crate::fixture::{put, tree};

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_site_is_checked_and_written() {
    let t = tree();
    let r = check(&t).unwrap();
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (0, "record: builds cleanly (20 page(s))\n")
    );
    let r = run(&[], &t, &t).unwrap();
    assert_eq!(
        r.stdout,
        "record: wrote the site, 20 page(s), to research/site/ - open research/site/index.html\n"
    );
    let r = run(
        &args(&["--out", "elsewhere", "--research-dir", "research"]),
        &t,
        &t,
    )
    .unwrap();
    assert_eq!(
        r.stdout,
        "record: wrote the site, 20 page(s), to elsewhere/ - open elsewhere/index.html\n"
    );
    assert!(t.join("elsewhere/all.html").is_file());
    assert_eq!(run(&args(&["--bogus"]), &t, &t).unwrap().code, 2);
    // an original still written inline: the check refuses, the build moves it
    put(&t, &q("0001-paddies.notes.html"), "<li data-note=\"k\"><a href=\"https://e.org/a\"><code>src-a</code></a> - \"one\" (translated; original: \u{300c}\u{539f}\u{300d})</li>\n<li data-note=\"n\">no source is owed: physical necessity</li>\n");
    let r = check(&t).unwrap();
    assert_eq!((r.code, r.stderr.as_str()), (1, "record: an original is still inline - `make record` moves it:\n  questions/0001-paddies.notes.html\n"));
    let r = run(&[], &t, &t).unwrap();
    assert!(r.stdout.starts_with("record: moved the originals of 1 notes file(s) into their .originals.html (feature 292)\nrecord: wrote the site"), "{}", r.stdout);
    put(&t, &q("0002-coins.html"), "<h2 id=\"coins\">Coins</h2>\n<!-- tags: subject=money; setting=town; level=foundational -->\n<p><a href=\"nowhere.html\">x</a></p>\n");
    let r = check(&t).unwrap();
    assert_eq!((r.code, r.stderr.as_str()), (1, "record: the site does not build (2 refusal(s)):\n  questions/0002-coins.html: `nowhere.html` - no question page nowhere.html\n  questions/0002-coins.html: `nowhere.html` - no question page nowhere.html\n"));
    let t = tree();
    std::fs::remove_file(t.join("research/assets/site.js")).unwrap();
    assert_eq!(check(&t).unwrap_err().kind, "OSError");
}

#[test]
fn render_syncs_build_runs_when_its_stamp_moved() {
    let t = tree();
    let root = t.display().to_string();
    assert_eq!(
        stale(&args(&["--root", &root]), b"x").unwrap().stdout,
        "rebuilt\n"
    );
    assert_eq!(
        stale(&args(&["--root", &root]), b"x").unwrap().stdout,
        "fresh\n"
    );
    assert_eq!(stale(&[], b"x").unwrap().code, 2);
    assert_eq!(stale(&args(&["--bogus"]), b"x").unwrap().code, 2);
    put(&t, &q("0002-coins.html"), "<h2 id=\"coins\">Coins</h2>\n<!-- tags: subject=money; setting=town; level=foundational -->\n<p><a href=\"nowhere.html\">x</a></p>\n");
    assert_eq!(
        stale(&args(&["--root", &root]), b"x").unwrap_err().kind,
        "RecordError"
    );
}

/// A question file's path in the fixture tree, built from its parts.
fn q(name: &str) -> String {
    format!("research/{}/{name}", crate::record::questions::QUESTIONS)
}
