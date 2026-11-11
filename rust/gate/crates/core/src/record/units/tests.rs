//! The decision over plain text: what changed, what it owes, each unit's fingerprint.

use super::{
    claims_of, digest, fingerprint, owed, question, quotation_key, read_notes, reading, reading_of,
    stem_of, Keyed, Record, Unit,
};

fn files(pairs: &[(&str, &str)]) -> Keyed<String> {
    let mut k = Keyed::default();
    for (a, b) in pairs {
        k.insert((*a).to_owned(), (*b).to_owned());
    }
    k
}

const BASE_PAGE: &str = "<h2>Trade</h2><p class=\"intro\">Why.</p><p>Old claim.<sup class=\"fn\" data-note=\"k\"></sup></p><p>Plain.</p>";
const BASE_NOTES: &str = "<li data-note=\"k\">\"a passage\" <a href=\"https://e.org/a\"><code>key-a</code></a><a href=\"x\"> <code>key-a</code> </a></li><li data-note=\"s\">same</li><li data-note=\"l\">linked <a href=\"https://e.org/1\">p</a></li>";

fn base() -> Record {
    Record::of(
        &files(&[
            ("0094-trade.html", BASE_PAGE),
            ("0094-trade.notes.html", BASE_NOTES),
            (
                "0094-trade.drawing.html",
                "<h2>Drawn</h2><p class=\"intro\">Drawing intro.</p>",
            ),
            (
                "0095-gone.html",
                "<h2>Gone</h2><p class=\"intro\">An intro.</p>",
            ),
            (
                "0096-kept.html",
                "<h2>Kept</h2><p class=\"intro\">Kept intro.</p>",
            ),
            ("0097-noslug.notes.html", "<li data-note=\"q\">orphan</li>"),
            ("README.html", "<p>not a question</p>"),
            ("x.notes.html", "<li data-note=\"q\">not a question's</li>"),
        ]),
        &files(&[("key-a", "<p>A.</p>"), ("key-b", "<p>B.</p>")]),
    )
}

fn now() -> Record {
    Record::of(
        &files(&[
            ("0094-trade.html", "<h2>Trade routes</h2><p class=\"intro\">Why now.</p><p>New claim.<sup class=\"fn\" data-note=\"k\"></sup><sup class=\"fn\" data-note=\"m\"></sup></p><p>Plain, new.</p><p>Plain.</p>"),
            ("0094-trade.notes.html", "<li data-note=\"k\">\"a passage\" <a href=\"https://e.org/a\"><code>key-a</code></a><a href=\"x\"> <code>key-a</code> </a></li><li data-note=\"s\">same</li><li data-note=\"l\">linked <a href=\"https://e.org/2\">p</a></li><li data-note=\"m\">no publicly readable source</li><li data-note=\"o\">\u{201c}curly\u{201d}<span class=\"orig\" data-orig=\"o1\"></span></li>"),
            ("0094-trade.originals.html", "<li data-orig=\"o1\">\u{300c}orig\u{300d}</li>"),
            ("0094-trade.drawing.html", "<h2>Drawn</h2><p class=\"intro\">Drawing intro changed.</p>"),
            ("0096-kept.html", "<h2>Kept</h2><p>No intro now.</p>"),
            ("0098-new.html", "<h2>New</h2><p>Fresh.</p>"),
        ]),
        &files(&[("key-a", "<p>A, revised.</p>"), ("key-b", "<p>B.</p>")]),
    )
}

#[test]
fn every_change_owes_what_the_rules_say_and_nothing_else() {
    let rows = owed(&now(), &base());
    let slugs: Vec<&str> = rows.iter().map(|u| u.slug.as_str()).collect();
    for want in [
        "intro-check:0094",
        "intro-check:0096",
        "intro-check:0098",
        "quote-check:0094#k",
        "quote-check:0094#m",
        "quote-check:0094#unfootnoted",
        "quote-check:0094#l",
        "quote-check:0094#o",
        "source-reader:0094#o",
        "record-format:0094",
        "source-applicability:key-a",
    ] {
        assert!(slugs.contains(&want));
    }
    assert!(!slugs.contains(&"source-reader:0094#m"));
    assert!(!slugs.contains(&"quote-check:0094#s"));
    assert!(!slugs.contains(&"source-applicability:key-b"));
    let moved = rows
        .iter()
        .find(|u| u.slug == "quote-check:0094#l")
        .unwrap();
    assert!(moved.occasion.starts_with("the note's link changed") && moved.reading.is_empty());
    assert_eq!(
        rows.iter()
            .find(|u| u.slug == "intro-check:0096")
            .unwrap()
            .occasion,
        "the intro is removed or changed"
    );
    let mut sorted = slugs.clone();
    sorted.sort_unstable();
    assert_eq!(slugs, sorted);
    assert!(owed(&base(), &base()).is_empty());
    assert!(!owed(&base(), &Record::default()).is_empty());
}

#[test]
fn a_fingerprint_hashes_what_its_check_reads() {
    let rec = now();
    let fps: Vec<String> = [
        "intro-check:0094",
        "record-format:0094",
        "source-applicability:key-a",
        "source-reader:0094#k",
        "quote-check:0094#unfootnoted",
        "quote-check:0094#k",
        "intro-check:0099",
    ]
    .iter()
    .map(|s| fingerprint(&rec, s))
    .collect();
    assert!(fps.iter().all(|f| f.len() == 16));
    assert_eq!(
        fingerprint(&rec, "source-reader:0094#k"),
        digest(&[rec.notes.get("0094").unwrap().get("k").unwrap()])
    );
    assert_eq!(reading_of(&rec, "intro-check:0094"), "");
    assert_eq!(reading_of(&rec, "quote-check:0094#unfootnoted"), "");
    assert_eq!(reading_of(&rec, "source-reader:0094#o").len(), 16);
    assert_eq!(reading_of(&rec, "quote-check:0094#k").len(), 16);
    assert_eq!(reading_of(&rec, "source-reader:0099#x"), "");
    assert_eq!(quotation_key(&rec, "quote-check:0094#k").len(), 16);
    assert_eq!(quotation_key(&rec, "quote-check:0099#k").len(), 16);
    assert_eq!(quotation_key(&rec, "nocolon").len(), 16);
}

#[test]
fn notes_and_readings_read_their_originals() {
    let notes = read_notes("<li data-note=\"a\">x<span class=\"orig\" data-orig=\"o\"></span></li><li data-note=\"a\">again</li><li data-note=\"b\">y<span class=\"orig\" data-orig=\"gone\"></span></li>", "<li data-orig=\"o\">\u{300c}O\u{300d}</li>");
    assert_eq!(notes.get("a").unwrap(), "again");
    assert_eq!(notes.get("b").unwrap(), "y");
    assert!(notes.contains("a") && !notes.contains("c"));
    let table = std::collections::HashMap::from([("o".to_owned(), "\u{300c}O\u{300d}".to_owned())]);
    assert_eq!(reading("no quote here", &table), "");
    assert_eq!(
        reading("<a href=\"h\">x</a>&quot;q&quot;", &table).len(),
        16
    );
    assert_eq!(
        reading("x<span class=\"orig\" data-orig=\"o\"></span>", &table).len(),
        16
    );
}

#[test]
fn claims_are_the_sentences_carrying_the_mark() {
    let w =
        "First, p. 28 says so. [^a] Second one! [^b] [^a] Third \u{201c}quoted\u{201d}. Tail [^a]";
    assert_eq!(
        claims_of(w, "a"),
        [
            "First, p. 28 says so. [^a]",
            "Second one! [^b] [^a]",
            "Tail [^a]"
        ]
    );
    assert_eq!(claims_of(w, "b"), ["Second one! [^b] [^a]"]);
    assert!(claims_of("nothing.", "a").is_empty());
}

#[test]
fn small_readers() {
    assert_eq!(question("0094.drawing#k"), "0094");
    assert_eq!(question(""), "");
    assert_eq!(
        stem_of("0094-a.drawing.html"),
        Some(("0094.drawing".to_owned(), "a".to_owned()))
    );
    assert_eq!(stem_of("x.html"), None);
    let u = Unit {
        slug: "quote-check:0094#k".to_owned(),
        ..Unit::default()
    };
    assert_eq!((u.check(), u.subject()), ("quote-check", "0094#k"));
    let bare = Unit {
        slug: "bare".to_owned(),
        ..Unit::default()
    };
    assert_eq!((bare.check(), bare.subject()), ("bare", ""));
    assert_eq!(u.json()["subject"], "0094#k");
    assert!(bare.json().get("subject").is_none());
    assert_eq!(digest(&[]).len(), 16);
}

#[test]
fn many_notes_files_are_kept_and_the_table_starts_again() {
    let mut pairs = Vec::new();
    for i in 0..12 {
        pairs.push((
            format!("{:04}-n.notes.html", 100 + i),
            format!("<li data-note=\"a\">{i}</li>"),
        ));
    }
    let named: Vec<(&str, &str)> = pairs
        .iter()
        .map(|(a, b)| (a.as_str(), b.as_str()))
        .collect();
    assert_eq!(
        Record::of(&files(&named), &files(&[])).notes.iter().count(),
        12
    );
}
