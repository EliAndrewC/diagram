//! The vocabulary and the table of contents (feature 449 T144; each expected value `contents.py`'s on the same files, 2026-11-16).

use std::path::Path;

use super::{
    home, idle_rules, load_contents, load_opening, load_vocabulary, matches, parse_tags, path,
    takes, walk, Tags,
};
use crate::fixture::{put, record};

/// Each broken file and what (the vocabulary, the contents, the opening) the Python answered; a "not JSON (" refusal quotes the parser.
const CASES: &[(&str, Option<&str>, [&str; 3])] = &[
    ("contents.json", None, ["ok", "ContentsError: contents.json: missing - the record's table of contents is a file, and the build will not invent it", "ContentsError: contents.json: missing - the record's table of contents is a file, and the build will not invent it"]),
    ("contents.json", Some("{nope"), ["ok", "ContentsError: contents.json: not JSON (", "ContentsError: contents.json: not JSON ("]),
    ("contents.json", Some("[]"), ["ok", "ContentsError: contents.json: an object with a `sections` list", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\", \"takes\": [{\"level\": \"detail\"}]}, {\"id\": \"a\", \"title\": \"T\", \"takes\": [{\"level\": \"detail\"}]}]}"), ["ok", "ContentsError: contents.json section `a`: the id is used twice", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"takes\": [{\"level\": \"detail\"}]}]}"), ["ok", "ContentsError: contents.json section `a`: no `title`", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"A\", \"title\": \"T\"}]}"), ["ok", "ContentsError: contents.json: a section is an object with a lower-case `id`", "ok:"]),
    ("contents.json", Some("{\"sections\": [\"x\"]}"), ["ok", "ContentsError: contents.json: a section is an object with a lower-case `id`", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\"}]}"), ["ok", "ContentsError: contents.json section `a`: takes nothing and holds nothing", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\", \"takes\": [{\"hue\": \"x\"}]}]}"), ["ok", "ContentsError: contents.json section `a`: `hue` - a clause tests only primary, subject, setting, level", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\", \"takes\": [{}]}]}"), ["ok", "ContentsError: contents.json section `a`: a clause is an object of primary, subject, setting, level", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\", \"takes\": [{\"subject\": [\"nope\"]}]}]}"), ["ok", "ContentsError: contents.json section `a`: `subject: nope` - no subject tag `nope` in tags.json", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\", \"takes\": [{\"subject\": [3]}]}]}"), ["ok", "ContentsError: contents.json section `a`: `subject: 3` - no subject tag `3` in tags.json", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\", \"takes\": 5}]}"), ["ok", "TypeError: 'int' object is not iterable", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\", \"takes\": \"ab\"}]}"), ["ok", "ContentsError: contents.json section `a`: a clause is an object of primary, subject, setting, level", "ok:"]),
    ("contents.json", Some("{\"sections\": [{\"id\": \"a\", \"title\": \"T\", \"takes\": {\"k\": 1}}]}"), ["ok", "ContentsError: contents.json section `a`: a clause is an object of primary, subject, setting, level", "ok:"]),
    ("contents.json", Some("{\"opening\": 3, \"sections\": []}"), ["ok", "ok", "ContentsError: contents.json: `opening` is the home page's opening, as HTML text"]),
    ("tags.json", None, ["ContentsError: tags.json: missing - the record's vocabulary is a file, and the build will not invent it", "ContentsError: tags.json: missing - the record's vocabulary is a file, and the build will not invent it", "ok:<p>What it is for.</p>"]),
    ("tags.json", Some("nope"), ["ContentsError: tags.json: not JSON (", "ContentsError: tags.json: not JSON (", "ok:<p>What it is for.</p>"]),
    ("tags.json", Some("{\"subject\": {}}"), ["ContentsError: tags.json: holds exactly the facets subject, setting, level", "ContentsError: tags.json: holds exactly the facets subject, setting, level", "ok:<p>What it is for.</p>"]),
    ("tags.json", Some("{\"subject\": {}, \"setting\": {}, \"level\": []}"), ["ContentsError: tags.json: `level` is a list, in presentation order", "ContentsError: tags.json: `level` is a list, in presentation order", "ok:<p>What it is for.</p>"]),
    ("tags.json", Some("{\"subject\": {\"Bad\": {\"name\": \"x\"}}, \"setting\": {}, \"level\": [{\"id\": \"a\", \"name\": \"A\"}]}"), ["ContentsError: tags.json: subject `Bad` - a tag is a lower-case id with a `name` and a `description`", "ContentsError: tags.json: subject `Bad` - a tag is a lower-case id with a `name` and a `description`", "ok:<p>What it is for.</p>"]),
    ("tags.json", Some("{\"subject\": [], \"setting\": {}, \"level\": [{\"id\": \"a\", \"name\": \"A\"}]}"), ["AttributeError: 'list' object has no attribute 'items'", "AttributeError: 'list' object has no attribute 'items'", "ok:<p>What it is for.</p>"]),
    ("tags.json", Some("{\"subject\": {}, \"setting\": {}, \"level\": [{\"id\": \"a\"}]}"), ["ContentsError: tags.json: level `a` - a tag is a lower-case id with a `name` and a `description`", "ContentsError: tags.json: level `a` - a tag is a lower-case id with a `name` and a `description`", "ok:<p>What it is for.</p>"]),
    ("tags.json", Some("{\"subject\": {}, \"setting\": {}, \"level\": [\"a\"]}"), ["ContentsError: tags.json: level `` - a tag is a lower-case id with a `name` and a `description`", "ContentsError: tags.json: level `` - a tag is a lower-case id with a `name` and a `description`", "ok:<p>What it is for.</p>"]),
];

fn said<T>(r: crate::Result<T>, ok: impl Fn(T) -> String) -> String {
    match r {
        Ok(v) => ok(v),
        Err(e) => {
            let m = format!("{}: {}", e.kind, e.message);
            m.find("not JSON (")
                .map_or(m.clone(), |at| m[..at + 10].to_owned())
        }
    }
}

fn answers(dir: &Path) -> [String; 3] {
    [
        said(load_vocabulary(dir), |_| "ok".into()),
        said(
            load_vocabulary(dir).and_then(|v| load_contents(dir, &v)),
            |_| "ok".into(),
        ),
        said(load_opening(dir), |o| format!("ok:{o}")),
    ]
}

#[test]
fn every_broken_file_is_refused_as_the_python_refused_it() {
    for (rel, text, want) in CASES {
        let dir = record();
        match text {
            Some(t) => put(&dir, rel, t),
            None => std::fs::remove_file(dir.join(rel)).unwrap(),
        }
        assert_eq!(answers(&dir), *want, "{rel} {text:?}");
    }
}

#[test]
fn the_fixture_contents_and_their_rules() {
    let dir = record();
    let vocab = load_vocabulary(&dir).unwrap();
    assert_eq!(vocab.setting[1].1.description, "3");
    assert_eq!(vocab.facet("level")[1].0, "detail");
    assert_eq!(vocab.facet("setting").len(), 2);
    assert_eq!(vocab.facet("subject").len(), 2);
    assert_eq!(vocab.level_rank("detail").unwrap(), 1);
    assert_eq!(
        vocab.level_rank("x").unwrap_err().message,
        "list.index(x): x not in list"
    );
    let sections = load_contents(&dir, &vocab).unwrap();
    let ids: Vec<&str> = walk(&sections).iter().map(|s| s.id.as_str()).collect();
    assert_eq!(ids, ["land", "fields", "coin", "later"]);
    let up: Vec<&str> = path(&sections, "fields")
        .iter()
        .map(|s| s.id.as_str())
        .collect();
    assert_eq!(up, ["land", "fields"]);
    assert!(path(&sections, "none").is_empty());
    let farm = Tags {
        subjects: vec!["farming".into()],
        settings: vec!["town".into()],
        level: "foundational".into(),
    };
    assert_eq!(home(&sections, &farm).unwrap().id, "land");
    assert!(takes(&sections[2], &farm));
    assert!(!matches(&sections[1].takes[0], &farm));
    assert_eq!(farm.all().len(), 3);
    // an awaiting section whose clause now matches is stale; an idle clause of a plain section is a typo
    assert_eq!(
        idle_rules(&sections, std::slice::from_ref(&farm)),
        [
            "contents.json section `fields`: the clause {\"level\": [\"detail\"], \"subject\": [\"farming\"]} matches no question",
            "contents.json section `coin`: the clause {\"primary\": [\"money\"], \"setting\": [\"town\", \"countryside\"]} matches no question",
            "contents.json section `later`: it holds a question now - delete its `awaiting`",
        ]
    );
}

#[test]
fn a_marker_is_read_and_refused_as_the_python_reads_it() {
    let dir = record();
    let vocab = load_vocabulary(&dir).unwrap();
    let got = parse_tags(
        "<!-- tags: subject=farming, money; setting=town; level=detail -->",
        "w",
        &vocab,
    )
    .unwrap()
    .unwrap();
    assert_eq!(
        got.marker(),
        "<!-- tags: subject=farming,money; setting=town; level=detail -->"
    );
    assert_eq!(got.primary(), "farming");
    assert!(parse_tags("none", "w", &vocab).unwrap().is_none());
    for (text, want) in [
        ("<!-- tags: a --><!-- tags: b -->", "w: two tags markers"),
        (
            "<!-- tags: subject=farming -->",
            "w: no setting in its tags",
        ),
        (
            "<!-- tags: subject=farming; subject=money -->",
            "w: `subject=money` - the marker is `subject=a,b; setting=x; level=y`, each facet once",
        ),
        (
            "<!-- tags: hue=red -->",
            "w: `hue=red` - the marker is `subject=a,b; setting=x; level=y`, each facet once",
        ),
        (
            "<!-- tags: nothing -->",
            "w: `nothing` - the marker is `subject=a,b; setting=x; level=y`, each facet once",
        ),
        (
            "<!-- tags: subject=nope; setting=town; level=detail -->",
            "w: `subject=nope` - no such tag in tags.json",
        ),
        (
            "<!-- tags: subject=money,money; setting=town; level=detail -->",
            "w: a subject tag is stated twice",
        ),
        (
            "<!-- tags: subject=money; setting=town; level=detail,foundational -->",
            "w: 2 levels - a question has exactly one",
        ),
    ] {
        assert_eq!(parse_tags(text, "w", &vocab).unwrap_err().message, want);
    }
}
