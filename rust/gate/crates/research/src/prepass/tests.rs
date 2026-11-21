//! What a pattern can find on a research page (feature 449 T145; each expected value `record_prepass.py`'s on the same record, 2026-11-16).

use std::collections::{HashMap, HashSet};
use std::os::unix::fs::PermissionsExt as _;

use serde_json::{json, Value};

use super::*;

const FILES: &str = r#"{"R/assets/glossary-variants.txt": "kiln\tkiln\nplain\n\n", "R/SOURCES.html": "<h3 id=\"key-one\">x</h3><h3 id=\"Bad\">y</h3><h3 id=\"ward-a\">z</h3>", "R/questions/0001-alpha.html": "<h2 id=\"alpha-heading\">Alpha &amp; omega</h2>\n<p>The wardens spoke of a kiln. Grounds: none. See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced. A <code>module_name.attr</code> and <a href=\"x\"><code>linked.one</code></a> <code>plain</code>.</p>\n<p><em>Pinus densiflora</em> and <i>hitoyado</i> and <em>a \"quoted\" one</em> and <em>far too many words here</em> 松の木 and 松の木 again. Another ward.</p>\n<h3>Second <span class=\"xref\">(x)</span></h3><p>wardens again rarely-seen</p><script>no</script>", "R/questions/0001-alpha.notes.html": "<li data-note=\"n\">the zoetrope <code>codeword</code> here</li>", "R/questions/0002-beta.html": "<h2 id=\"beta\">Beta</h2><p>wardens and kilns and rarely-seen things</p>", "R/questions/0002-beta.drawing.html": "<h2 id=\"beta-drawn\">Beta drawn</h2><p>drawn</p>", "R/questions/0002-beta.drawing.notes.html": "<li>drawing notes zoetrope</li>", "R/questions/0003-gamma.notes.html": "<li>orphan notes</li>", "R/questions/_private.html": "<p>wardens</p>", "R/questions/citations/0001-x.html": "<p>wardens</p>", "R/site/0001.html": "<p>wardens</p>", "R/assets/x.html": "<p>wardens</p>", "R/top.html": "<p>wardens</p>", "R/assets/glossary/a.html": "<p>glossed wardens</p>", "l7r/diagram/interactive/assets/glossary.json": "{\"Kiln\": {\"variants\": [\"kilns\", \"Wardens\"]}, \"Hitoyado\": {\"variants\": []}}"}"#;
const WANT: &str = r#"{"sections": [["Alpha & omega", "\n<p>The wardens spoke of a kiln. Grounds: none. See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced. A <code>module_name.attr</code> and <a href=\"x\"><code>linked.one</code></a> <code>plain</code>.</p>\n<p><em>Pinus densiflora</em> and <i>hitoyado</i> and <em>a \"quoted\" one</em> and <em>far too many words here</em> 松の木 and 松の木 again. Another ward.</p>\n"], ["Second", "<p>wardens again rarely-seen</p>"]], "text_of": "a & c", "sentence": "Three is it.", "sentence0": "no stops here", "known": ["hitoyado", "kiln", "kilns", "wardens"], "session": [{"class": "SESSION NOTE", "label": "field", "match": "Grounds:", "sentence": "Grounds: none."}, {"class": "SESSION NOTE", "label": "feature number", "match": "feature 251", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "task id", "match": "T45", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "spec path", "match": "specs/251-tiered-x", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "make target", "match": "make record-prepass", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "file path", "match": "scripts/x.py", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "file path", "match": "run.sh", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "UNFETCHABLE", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "leftover", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "not re-sourced", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "engine identifier", "match": "module_name.attr", "sentence": "A module_name.attr and linked.one plain ."}], "vocab": [{"class": "VOCABULARY", "label": "binomial", "match": "Pinus densiflora", "sentence": "Pinus densiflora and hitoyado and a \"quoted\" one and far too many words here 松の木 and 松の木 again."}, {"class": "VOCABULARY", "label": "CJK term", "match": "松の木", "sentence": "Pinus densiflora and hitoyado and a \"quoted\" one and far too many words here 松の木 and 松の木 again."}], "defined": ["kiln", "plain\n"], "keys": ["key-one", "ward-a"], "freq": {"glossed": 1, "wardens": 3, "again": 1, "alpha": 1, "and": 2, "another": 1, "attr": 1, "densiflora": 1, "far": 1, "feature": 1, "grounds": 1, "here": 2, "hitoyado": 1, "kiln": 1, "leftover": 1, "linked": 1, "make": 1, "many": 1, "module": 1, "name": 1, "no": 1, "none": 1, "not": 1, "of": 1, "omega": 1, "one": 1, "pinus": 1, "plain": 1, "py": 1, "quoted": 1, "rarely-seen": 2, "re-sourced": 1, "record-prepass": 1, "run": 1, "scripts": 1, "second": 1, "see": 1, "sh": 1, "specs": 1, "spoke": 1, "the": 2, "tiered-x": 1, "too": 1, "unfetchable": 1, "ward": 1, "words": 1, "beta": 2, "kilns": 1, "things": 1, "drawn": 1, "notes": 2, "orphan": 1, "codeword": 1, "zoetrope": 2, "drawing": 1}, "notes": {"gamma": "orphan notes", "alphaheading": "the zoetrope here", "betadrawn": "drawing notes zoetrope"}, "bare": "alphaomegass", "without": "a c", "prepass": [{"section": "Alpha & omega", "items": [{"class": "SESSION NOTE", "label": "field", "match": "Grounds:", "sentence": "Grounds: none."}, {"class": "SESSION NOTE", "label": "feature number", "match": "feature 251", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "task id", "match": "T45", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "spec path", "match": "specs/251-tiered-x", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "make target", "match": "make record-prepass", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "file path", "match": "scripts/x.py", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "file path", "match": "run.sh", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "UNFETCHABLE", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "leftover", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "not re-sourced", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "engine identifier", "match": "module_name.attr", "sentence": "A module_name.attr and linked.one plain ."}, {"class": "VOCABULARY", "label": "binomial", "match": "Pinus densiflora", "sentence": "Pinus densiflora and hitoyado and a \"quoted\" one and far too many words here 松の木 and 松の木 again."}, {"class": "VOCABULARY", "label": "CJK term", "match": "松の木", "sentence": "Pinus densiflora and hitoyado and a \"quoted\" one and far too many words here 松の木 and 松の木 again."}], "rare": [["again", 1], ["and", 2], ["another", 1], ["densiflora", 1], ["far", 1], ["feature", 1], ["grounds", 1], ["here", 2], ["hitoyado", 1], ["leftover", 1], ["make", 1], ["many", 1], ["none", 1], ["not", 1], ["of", 1], ["one", 1], ["pinus", 1], ["py", 1], ["quoted", 1], ["re-sourced", 1], ["record-prepass", 1], ["run", 1], ["scripts", 1], ["see", 1], ["sh", 1], ["specs", 1], ["spoke", 1], ["the", 2], ["tiered-x", 1], ["too", 1], ["unfetchable", 1], ["ward", 1], ["words", 1]]}, {"section": "Second", "items": [], "rare": [["again", 1], ["rarely-seen", 2]]}], "prepass_none": [{"section": "Alpha & omega", "items": [{"class": "SESSION NOTE", "label": "field", "match": "Grounds:", "sentence": "Grounds: none."}, {"class": "SESSION NOTE", "label": "feature number", "match": "feature 251", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "task id", "match": "T45", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "spec path", "match": "specs/251-tiered-x", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "make target", "match": "make record-prepass", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "file path", "match": "scripts/x.py", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "file path", "match": "run.sh", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "UNFETCHABLE", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "leftover", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "fetch verdict", "match": "not re-sourced", "sentence": "See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced."}, {"class": "SESSION NOTE", "label": "engine identifier", "match": "module_name.attr", "sentence": "A module_name.attr and linked.one plain ."}, {"class": "VOCABULARY", "label": "binomial", "match": "Pinus densiflora", "sentence": "Pinus densiflora and hitoyado and a \"quoted\" one and far too many words here 松の木 and 松の木 again."}, {"class": "VOCABULARY", "label": "CJK term", "match": "松の木", "sentence": "Pinus densiflora and hitoyado and a \"quoted\" one and far too many words here 松の木 and 松の木 again."}], "rare": []}, {"section": "Second", "items": [], "rare": []}], "render": "record-prepass: 0001 - 2 sections, 13 candidates (each is for record-format to confirm or dismiss)\n## Alpha & omega\n  SESSION NOTE [field] 'Grounds:' - Grounds: none.\n  SESSION NOTE [feature number] 'feature 251' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [task id] 'T45' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [spec path] 'specs/251-tiered-x' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [make target] 'make record-prepass' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [file path] 'scripts/x.py' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [file path] 'run.sh' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [fetch verdict] 'UNFETCHABLE' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [fetch verdict] 'leftover' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [fetch verdict] 'not re-sourced' - See feature 251 and T45, specs/251-tiered-x, make record-prepass, scripts/x.py, run.sh, UNFETCHABLE leftover not re-sourced.\n  SESSION NOTE [engine identifier] 'module_name.attr' - A module_name.attr and linked.one plain .\n  VOCABULARY [binomial] 'Pinus densiflora' - Pinus densiflora and hitoyado and a \"quoted\" one and far too many words here 松の木 and 松の木 again.\n  VOCABULARY [CJK term] '松の木' - Pinus densiflora and hitoyado and a \"quoted\" one and far too many words here 松の木 and 松の木 again.\n\n## WORDS TO RULE ON (35) - feature 260\n\nEvery word below is in this entry, is defined by no glossary term, and appears in at most\n2 of the record's question fragments (the count is beside each one). `record-format` rules\non EVERY one of them and says which verdict each got. The list is a floor, not the question:\nit cannot see a MULTI-WORD term, and it does not raise a word the record uses often though\nthe glossary does not define it - so anything else you notice is reported too.\n### Alpha & omega\n  again (1), and (2), another (1), densiflora (1), far (1), feature (1), grounds (1), here (2), hitoyado (1), leftover (1), make (1), many (1), none (1), not (1), of (1), one (1), pinus (1), py (1), quoted (1), re-sourced (1), record-prepass (1), run (1), scripts (1), see (1), sh (1), specs (1), spoke (1), the (2), tiered-x (1), too (1), unfetchable (1), ward (1), words (1)\n### Second\n  again (1), rarely-seen (2)", "render_empty": "record-prepass: x - 1 sections, 0 candidates (each is for record-format to confirm or dismiss)", "rare": [["zebra", 1]], "words": ["Grounds:", "Pinus densiflora", "T45", "UNFETCHABLE", "again", "and", "another", "densiflora", "far", "feature", "feature 251", "grounds", "here", "hitoyado", "leftover", "make", "make record-prepass", "many", "module_name.attr", "none", "not", "not re-sourced", "of", "one", "pinus", "py", "quoted", "rarely-seen", "re-sourced", "record-prepass", "run", "run.sh", "scripts", "scripts/x.py", "see", "sh", "specs", "specs/251-tiered-x", "spoke", "the", "tiered-x", "too", "unfetchable", "ward", "words", "松の木"]}"#;

fn sorted(set: HashSet<String>) -> Vec<String> {
    let mut v: Vec<String> = set.into_iter().collect();
    v.sort();
    v
}

#[test]
fn every_reader_is_the_pythons() {
    let d = l7r_shared::tempdir::TempDir::new("research-prepass");
    let files: serde_json::Map<String, Value> = serde_json::from_str(FILES).unwrap();
    for (rel, text) in &files {
        // `R/` is the record's directory, spelled so the pointer check does not read a scratch record's files as the real one's
        let p = d.join(rel.replace("R/", "research/"));
        std::fs::create_dir_all(p.parent().unwrap()).unwrap();
        std::fs::write(p, text.as_str().unwrap()).unwrap();
    }
    let want: Value = serde_json::from_str(WANT).unwrap();
    let rd = d.join("research");
    let page = files["R/questions/0001-alpha.html"].as_str().unwrap();
    let gloss = read_glossary(&d).unwrap();
    assert_eq!(json!(sections(page)), want["sections"]);
    assert_eq!(json!(text_of(" a <b>&amp;</b>\n c ")), want["text_of"]);
    let chars = |s: &str| s.chars().collect::<Vec<_>>();
    assert_eq!(
        json!(sentence_around(
            &chars("One. Two here? Three is it. Four."),
            16,
            21
        )),
        want["sentence"]
    );
    assert_eq!(
        json!(sentence_around(&chars("no stops here"), 0, 2)),
        want["sentence0"]
    );
    assert_eq!(sentence_around(&[], 0, 0), "");
    assert_eq!(json!(sorted(known_terms(&gloss).unwrap())), want["known"]);
    assert_eq!(json!(session_notes(page)), want["session"]);
    assert_eq!(
        json!(vocabulary(page, &known_terms(&gloss).unwrap())),
        want["vocab"]
    );
    assert_eq!(json!(sorted(defined_words(&rd).unwrap())), want["defined"]);
    assert_eq!(
        json!(sorted(registry_keys(&Reader::new(&rd)).unwrap())),
        want["keys"]
    );
    let freq: HashMap<String, usize> = corpus_frequency(&rd).unwrap();
    let want_freq: HashMap<String, usize> = serde_json::from_value(want["freq"].clone()).unwrap();
    assert_eq!(freq, want_freq);
    let notes = notes_index(&rd).unwrap();
    let want_notes: HashMap<String, String> =
        serde_json::from_value(want["notes"].clone()).unwrap();
    assert_eq!(notes, want_notes);
    assert_eq!(json!(bare("<b>Alpha</b> &amp; Omega-\u{df}")), want["bare"]);
    assert_eq!(
        json!(without_code("<p>a <code class='x'>b</code> c</p>")),
        want["without"]
    );
    let listing = prepass(page, &gloss, Some(&rd)).unwrap();
    assert_eq!(json!(listing), want["prepass"]);
    assert_eq!(
        json!(prepass(page, &gloss, None).unwrap()),
        want["prepass_none"]
    );
    assert_eq!(json!(render("0001", &listing)), want["render"]);
    assert_eq!(
        json!(render(
            "x",
            &[json!({"section": "s", "items": [], "rare": []})]
        )),
        want["render_empty"]
    );
    let defined: HashSet<String> = ["defined".to_owned()].into();
    let fq: HashMap<String, usize> = [
        ("zebra".to_owned(), 1),
        ("quokka".to_owned(), 3),
        ("kiln-x".to_owned(), 2),
    ]
    .into();
    let keys: HashSet<String> = ["kiln-x".to_owned()].into();
    assert_eq!(
        json!(rare_words(
            "Zebra zebra, quokka unknown kiln-x",
            &defined,
            &fq,
            &keys
        )),
        want["rare"]
    );
    assert_eq!(
        json!(sorted(prepass_words(&d, "0001").unwrap())),
        want["words"]
    );
}

#[test]
fn what_the_python_refused() {
    let d = l7r_shared::tempdir::TempDir::new("research-prepass-bad");
    let gloss = d.join(GLOSSARY);
    std::fs::create_dir_all(gloss.parent().unwrap()).unwrap();
    assert!(read_glossary(&d).unwrap().is_empty());
    for (text, kind) in [("{", "JSONDecodeError"), ("[]", "AttributeError")] {
        std::fs::write(&gloss, text).unwrap();
        assert_eq!(read_glossary(&d).unwrap_err().kind, kind);
    }
    std::fs::write(&gloss, [0xff]).unwrap();
    assert_eq!(read_glossary(&d).unwrap_err().kind, "UnicodeDecodeError");
    let entry = |v: Value| known_terms(v.as_object().unwrap());
    assert_eq!(entry(json!({"a": 1})).unwrap_err().kind, "AttributeError");
    assert_eq!(
        entry(json!({"a": {"variants": 5}})).unwrap_err().kind,
        "TypeError"
    );
    assert_eq!(
        sorted(entry(json!({"A": {"variants": "xY"}})).unwrap()),
        ["a", "x", "y"]
    );
    assert_eq!(
        sorted(entry(json!({"A": {"variants": {"K": 1}}})).unwrap()),
        ["a", "k"]
    );
    assert_eq!(sorted(entry(json!({"A": {"variants": 0}})).unwrap()), ["a"]);
    let rd = d.join("research");
    std::fs::create_dir_all(rd.join("assets")).unwrap();
    std::fs::write(rd.join("assets/glossary-variants.txt"), [0xff]).unwrap();
    assert!(defined_words(&rd).is_err());
    std::fs::create_dir_all(rd.join("questions")).unwrap();
    std::fs::write(rd.join("questions/0001-a.html"), [0xff]).unwrap();
    assert!(corpus_frequency(&rd).is_err());
    std::fs::write(rd.join("questions/0001-a.notes.html"), [0xff]).unwrap();
    assert!(notes_index(&rd).is_err());
    std::fs::write(rd.join("questions/0001-a.html"), "<h2 id=\"a\">A</h2>").unwrap();
    assert!(notes_index(&rd).is_err());
    std::fs::write(rd.join("questions/0001-a.notes.html"), "").unwrap();
    std::fs::create_dir_all(rd.join("questions/0002-b.notes.html")).unwrap();
    assert!(notes_index(&rd).is_ok());
    std::fs::write(rd.join("questions/0003-c.notes.html"), "x").unwrap();
    std::fs::create_dir_all(rd.join("questions/0003-c.html")).unwrap();
    assert!(notes_index(&rd).is_ok());
    assert!(prepass_words(&d, "0003").is_err());
    let nowhere = d.join("nowhere");
    assert!(
        defined_words(&nowhere).unwrap().is_empty()
            && corpus_frequency(&nowhere).unwrap().is_empty()
    );
    let locked = rd.join("questions/0005-e.notes.html");
    std::fs::write(&locked, "x").unwrap();
    std::fs::set_permissions(&locked, std::fs::Permissions::from_mode(0o000)).unwrap();
    assert!(notes_index(&rd).is_err());
    let html = rd.join("sub/0006-f.html");
    std::fs::create_dir_all(html.parent().unwrap()).unwrap();
    std::fs::write(&html, "x").unwrap();
    std::fs::set_permissions(&html, std::fs::Permissions::from_mode(0o000)).unwrap();
    assert!(corpus_frequency(&rd).is_err());
    let listing = [
        json!({"section": "a", "items": [], "rare": [["w", 1]]}),
        json!({"section": "b", "items": [], "rare": []}),
    ];
    assert!(render("x", &listing).ends_with("### a\n  w (1)"));
}
