//! Where a link in the record goes once the record is a site (feature 449 T148): each expected value `site_links.py`'s and `posixpath`'s on
//! the same input (`CPython` 3.14.4, observed 2026-11-16).

use super::{
    asset_href, dirname, ids_in, normpath, relpath, rewrite, single_href, site_file, site_href,
    Index, Loc, Target,
};

fn loc(kind: &'static str, page: Option<&str>, anchor: Option<&str>) -> Target {
    Target::Loc(Loc {
        kind,
        page: page.map(str::to_owned),
        anchor: anchor.map(str::to_owned),
    })
}

fn index() -> Index {
    let mut i = Index::new();
    i.add_page("a.html", "a", "<p id=\"x\">x</p><!-- <p id=\"hid\"> -->");
    i.add_registry(None, "<p id=\"intro\">");
    i.add_registry(Some("k"), "<p id=\"in-k\">");
    i.add_section("s", "research");
    i.add_section("s", "drawing");
    i
}

#[test]
fn every_link_resolves_as_the_pythons() {
    let i = index();
    let ok = |h: &str, own: Option<&str>| i.resolve(h, own).unwrap();
    assert_eq!(
        ok("a.html#x", Some("a.html")),
        loc("q", Some("a"), Some("x"))
    );
    assert_eq!(ok("#x", Some("a.html")), loc("q", Some("a"), Some("x")));
    assert_eq!(ok("#a", Some("a.html")), loc("q", Some("a"), None));
    assert_eq!(
        i.resolve("x.html", None).unwrap_err(),
        "`x.html` - no such page in the record"
    );
    assert_eq!(
        ok("../SOURCES.html#in-k", Some("a.html")),
        loc("source", Some("k"), Some("in-k"))
    );
    assert_eq!(ok("#intro", None), loc("source", None, Some("intro")));
    assert_eq!(ok("#k", None), loc("source", Some("k"), None));
    for out in ["", "mailto:x", "//h", "HTTPS://h"] {
        assert_eq!(ok(out, None), Target::Outside);
    }
    assert_eq!(
        ok("../contents.json#s", Some("a.html")),
        loc("section", Some("research-s"), None)
    );
    assert_eq!(
        ok("../assets/c.css#z", Some("a.html")),
        Target::Asset("assets/c.css#z".into())
    );
    assert_eq!(
        ok("../assets/c.css", Some("a.html")),
        Target::Asset("assets/c.css".into())
    );
    assert_eq!(
        ok("/abs.css", Some("a.html")),
        Target::Asset("/abs.css".into())
    );
    assert_eq!(
        i.resolve("a.html#hid", Some("a.html")).unwrap_err(),
        "`a.html#hid` - no id `hid` on a.html"
    );
}

#[test]
fn every_place_is_written_for_both_forms() {
    let cases = [
        (
            Loc {
                kind: "q",
                page: Some("a".into()),
                anchor: Some("x".into()),
            },
            "q/b.html",
            "q/a.html",
            "a.html#x",
            "#x",
        ),
        (
            Loc {
                kind: "q",
                page: Some("a".into()),
                anchor: Some("x".into()),
            },
            "q/a.html",
            "q/a.html",
            "#x",
            "#x",
        ),
        (
            Loc {
                kind: "section",
                page: Some("research-s".into()),
                anchor: None,
            },
            "index.html",
            "findings/s.html",
            "findings/s.html",
            "#research-s",
        ),
        (
            Loc {
                kind: "source",
                page: None,
                anchor: Some("y".into()),
            },
            "sources/index.html",
            "sources/index.html",
            "#y",
            "#y",
        ),
        (
            Loc {
                kind: "source",
                page: Some("k".into()),
                anchor: None,
            },
            "q/a.html",
            "sources/k.html",
            "../sources/k.html",
            "#k",
        ),
        (
            Loc {
                kind: "source",
                page: None,
                anchor: None,
            },
            "q/a.html",
            "sources/index.html",
            "../sources/index.html",
            "#reg",
        ),
    ];
    for (l, here, file, href, single) in cases {
        assert_eq!(
            (site_file(&l), site_href(&l, here), single_href(&l, "reg")),
            (file.to_owned(), href.to_owned(), single.to_owned())
        );
    }
    assert_eq!(
        asset_href("assets/c.css#z", "q/a.html"),
        "../../assets/c.css#z"
    );
    assert_eq!(asset_href("assets/c.css", "index.html"), "../assets/c.css");
    assert_eq!(
        ids_in("<p id=\"a\" data-id=\"b\" xid=\"c\" id=\"\"><!-- id=\"d\" -->"),
        ["a", "b"]
    );
}

#[test]
fn a_fragment_is_rewritten_for_each_form() {
    let i = index();
    assert_eq!(
        rewrite("<a href=\"#x\">a</a><img alt=\"y\" src=\"../assets/i.png\"><a href=\"nope.html\">n</a><a name=\"z\">", Some("a.html"), &i, "q/a.html", false, "W", ""),
        ("<a href=\"#x\">a</a><img alt=\"y\" src=\"../../assets/i.png\"><a href=\"nope.html\">n</a><a name=\"z\">".to_owned(), vec!["W: `nope.html` - no question page nope.html".to_owned()])
    );
    assert_eq!(
        rewrite("<a href=\"#x\">a</a><img src=\"../assets/i.png\"><a href=\"https://h\">h</a><a\thref=\"../SOURCES.html\">r</a><a href=\"x", Some("a.html"), &i, "q/a.html", true, "W", "reg").0,
        "<a href=\"#x\">a</a><img src=\"../assets/i.png\"><a href=\"https://h\">h</a><a\thref=\"#reg\">r</a><a href=\"x"
    );
    // a tag that never closes, and one whose name only begins with `a`
    assert_eq!(
        rewrite(
            "<abbr href=\"#x\"> <a title=\"t\" ",
            None,
            &i,
            "q/a.html",
            false,
            "W",
            ""
        )
        .0,
        "<abbr href=\"#x\"> <a title=\"t\" "
    );
}

#[test]
fn paths_are_read_as_posixpath_reads_them() {
    for (p, want) in [
        ("a/../../b", "../b"),
        ("/../a", "/a"),
        ("//a/b", "//a/b"),
        ("///a", "/a"),
        (".", "."),
        ("a/./b/", "a/b"),
    ] {
        assert_eq!(normpath(p), want, "{p}");
    }
    for (p, want) in [
        ("a/b", "a"),
        ("/", "/"),
        ("a", ""),
        ("a/", "a"),
        ("//x", "//"),
    ] {
        assert_eq!(dirname(p), want, "{p}");
    }
    assert_eq!(relpath("a/b", "a/b"), ".");
    assert_eq!(relpath("a", ""), "a");
    let depth = std::env::current_dir().unwrap().components().count() - 1;
    assert_eq!(relpath("/x", "q"), format!("{}x", "../".repeat(depth + 1)));
}
