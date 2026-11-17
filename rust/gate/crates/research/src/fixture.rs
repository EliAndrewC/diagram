//! The crate's test record (feature 449 T144): a few questions, their notes and originals, a registry, the vocabularies and the lists,
//! written into a scratch directory a test owns. Its expectations are the Python's answers on the same files.

use std::path::Path;

use l7r_gate_core::checks::{scratch, TempDir};

/// Each file of the record and its text.
pub const FILES: &[(&str, &str)] = &[
    ("tags.json", "{\n \"subject\": {\n  \"farming\": {\n   \"name\": \"Farming\",\n   \"description\": \"growing\"\n  },\n  \"money\": {\n   \"name\": \"Money\"\n  }\n },\n \"setting\": {\n  \"countryside\": {\n   \"name\": \"Countryside\",\n   \"description\": \"fields\"\n  },\n  \"town\": {\n   \"name\": \"Town\",\n   \"description\": 3\n  }\n },\n \"level\": [\n  {\n   \"id\": \"foundational\",\n   \"name\": \"Foundational\"\n  },\n  {\n   \"id\": \"detail\",\n   \"name\": \"Detail\",\n   \"description\": \"fine\"\n  }\n ]\n}"),
    ("contents.json", "{\n \"opening\": \"<p>What it is for.</p>\",\n \"sections\": [\n  {\n   \"id\": \"land\",\n   \"title\": \"Land\",\n   \"description\": \"On land\",\n   \"drawing_description\": \"Drawn land\",\n   \"takes\": [\n    {\n     \"primary\": \"farming\"\n    }\n   ],\n   \"sections\": [\n    {\n     \"id\": \"fields\",\n     \"title\": \"Fields\",\n     \"takes\": [\n      {\n       \"subject\": [\n        \"farming\"\n       ],\n       \"level\": \"detail\"\n      }\n     ]\n    }\n   ]\n  },\n  {\n   \"id\": \"coin\",\n   \"title\": \"Coin\",\n   \"takes\": [\n    {\n     \"primary\": \"money\",\n     \"setting\": [\n      \"town\",\n      \"countryside\"\n     ]\n    }\n   ]\n  },\n  {\n   \"id\": \"later\",\n   \"title\": \"Later\",\n   \"awaiting\": \"the first request\",\n   \"takes\": [\n    {\n     \"level\": \"foundational\",\n     \"primary\": \"farming\"\n    }\n   ]\n  }\n ]\n}"),
    ("confusables.json", "[{\"a\": \"0001-paddies.html#paddies\", \"b\": \"0002-coins.html#coins\", \"why\": \"both round\"}]"),
    ("questions/0001-paddies.html", "<h2 id=\"paddies\">Paddies <em>wet</em> (researched 2026-08-27, feature 133)</h2>\n<!-- tags: subject=farming; setting=countryside; level=detail -->\n<p>Paddies are wet. They hold water.<sup class=\"fn\" data-note=\"k\"></sup> See https://e.org/b).</p>\n<p>Again.<sup class=\"fn\" data-note=\"k\"></sup><sup class=\"fn\" data-note=\"n\"></sup></p>\n"),
    ("questions/0001-paddies.notes.html", "<ol>\n<li data-note=\"k\"><a href=\"https://e.org/a\"><code>src-a</code></a> - \"one\" ; \"two\" <span class=\"orig\" data-orig=\"k#1\"></span></li>\n<li data-note=\"n\">no publicly readable source<!-- searched 2026-09-28 --> nothing</li>\n</ol>\n"),
    ("questions/0001-paddies.originals.html", "<li data-orig=\"k#1\">original: \u{300c}\u{539f}\u{300d}</li>\n"),
    ("questions/0001-paddies.drawing.html", "<h2 id=\"paddies-drawn\">How paddies are drawn</h2>\n<p>Drawn blue.</p>\n"),
    ("questions/0002-coins.html", "<h2 id=\"coins\">Coins</h2>\n<!-- tags: subject=money; setting=town; level=foundational -->\n<!-- a comment --><p>Coins are <b>round</b>&amp; flat! More.</p>\n"),
    ("questions/0003-more-drawn.drawing.html", "<h2 id=\"more-drawn\">More drawn</h2>\n<!-- about: 0001-paddies -->\n<p>x</p>\n"),
    ("sources/_front.html", "<html><body><main>\n"),
    ("sources/_tail.html", "\n</main>\n</body>\n</html>\n"),
    ("sources/010-works-cited.html", "<h2 id=\"works-cited\">Works cited</h2>\n"),
    ("sources/010-works-cited/0010-src-a.html", "<h3 id=\"work-src-a\"><code>src-a</code></h3>\n<p>Src A, https://e.org/a READ <!-- READ 2026-10-01 at https://e.org/a2 --></p>\n<p><em>What it is:</em> a book</p>\n<p><em>Used for:</em> paddies</p>\n<!-- tags: period=modern,premodern; region=japan; kind=book -->\n"),
    ("sources/010-works-cited/0020-l7r-notes.html", "<h3 id=\"l7r-notes\"><code>l7r-notes</code></h3>\n<p>The GM's l7r.md https://github.com/x/l7r.md</p>\n"),
    ("sources/010-works-cited/0030-grok.html", "<h3 id=\"work-grok\"><code>grok</code></h3>\n<p>https://grokipedia.com/page/X SUMMARY-ONLY</p>\n<!-- tags: period=modern; region=china; kind=web -->\n"),
    ("sources/020-other.html", "<h2 id=\"other\">Other</h2>\n<p>https://banned.example.org/p and https://e.org/a.</p>\n"),
    ("source-tags.json", "{\n \"period\": [\n  {\n   \"id\": \"modern\",\n   \"name\": \"Modern\",\n   \"description\": \"now & \\\"then\\\"\"\n  },\n  {\n   \"id\": \"premodern\",\n   \"name\": \"Premodern\",\n   \"description\": \"old\"\n  }\n ],\n \"region\": [\n  {\n   \"id\": \"japan\",\n   \"name\": \"Japan\",\n   \"description\": \"jp\"\n  },\n  {\n   \"id\": \"china\",\n   \"name\": \"China\",\n   \"description\": \"cn\"\n  }\n ],\n \"kind\": [\n  {\n   \"id\": \"book\",\n   \"name\": \"Book\",\n   \"description\": \"bound\"\n  },\n  {\n   \"id\": \"web\",\n   \"name\": \"Web <page>\",\n   \"description\": \"online\"\n  }\n ],\n \"canon\": {\n  \"id\": \"canon\",\n  \"name\": \"Canon\",\n  \"description\": \"the GM's\"\n }\n}"),
    ("source-sections.json", "{\n \"sections\": [\n  {\n   \"id\": \"works-japan\",\n   \"title\": \"Japan & more\",\n   \"description\": \"Japanese works\",\n   \"takes\": [\n    {\n     \"region\": \"japan\"\n    }\n   ]\n  },\n  {\n   \"id\": \"works-china\",\n   \"title\": \"China\",\n   \"takes\": [\n    {\n     \"region\": [\n      \"china\"\n     ],\n     \"kind\": \"web\"\n    }\n   ]\n  },\n  {\n   \"id\": \"works-canon\",\n   \"title\": \"Canon\",\n   \"canon\": true\n  }\n ]\n}"),
    ("blocked-domains.json", "{\"domains\": [{\"domain\": \"grokipedia.com\", \"reason\": \"machine text\", \"approved\": {\"date\": \"2026-10-02\", \"words\": \"block it\"}}]}"),
    ("banned-citations.json", "{\"patterns\": [{\"pattern\": \"banned\\\\.example\\\\.org/\", \"reason\": \"forbidden\", \"approved\": {\"date\": \"2026-10-03\", \"words\": \"ban it\"}}]}"),
    ("archive/a1/a1b2c3d4e5f6.json", "{\"outcome\": \"archived\", \"captured\": \"2026-10-01T00:00:00Z\", \"path\": \"a1/x\"}"),
];

/// The record, written into a new scratch directory.
pub fn record() -> TempDir {
    let dir = scratch("research-record");
    for (rel, text) in FILES {
        put(&dir, rel, text);
    }
    dir
}

/// One file written, its directory made.
///
/// # Panics
/// A file the test's temporary directory cannot hold.
pub fn put(dir: &Path, rel: &str, text: &str) {
    let path = dir.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// What the record's site is built from beside the record (feature 449 T148): the hand-written assets, the glossary and its term files, the
/// derived variant index, the source-applicability contract.
pub const TREE: &[(&str, &str)] = &[
    ("research/sources/_front.html", "<html><body><main>\n<h1 id=\"the-registry\">The <em>registry</em></h1>\n<p>Every work, and <a href=\"#works-cited\">the cited</a>.</p>\n<hr>\n"),
    ("research/sources/010-works-cited/0010-src-a.html", "<h3 id=\"src-a\"><code>src-a</code></h3>\n<p>Src A, https://e.org/a READ <!-- READ 2026-10-01 at https://e.org/a2 --></p>\n<p><em>What it is:</em> a book</p>\n<p><em>Why it applies, and its limits:</em> it does</p>\n<p><em>Used for:</em> paddies (<a href=\"contents.json#land\">Land</a>)</p>\n<!-- tags: period=modern,premodern; region=japan; kind=book -->\n"),
    ("research/sources/010-works-cited/0020-l7r-notes.html", "<h3 id=\"l7r-notes\"><code>l7r-notes</code></h3>\n<p>The GM's campaign notes, <code>l7r.md</code>, \"A\" (https://github.com/x/l7r.md#a) and \"B\" (https://github.com/x/l7r.md#b) (https://github.com/x/l7r.md)<!-- READ --></p>\n"),
    ("research/sources/010-works-cited/0040-bare.html", "<h3 id=\"bare\"><code>bare</code></h3>\n<!-- tags: period=modern; region=china; kind=web -->\n"),
    ("research/sources/040-uncited-works.html", "<h2 id=\"uncited-works\">Uncited works</h2>\n<p>Read and kept.</p>\n"),
    ("research/sources/040-uncited-works/0010-unc-a.html", "<h3 id=\"unc-a\"><code>unc-a</code></h3>\n<p>Unc A (https://e.org/u).</p>\n<p><em>What it is:</em> a page</p>\n<p><em>Why it applies, and its limits:</em> kept</p>\n<!-- tags: period=modern; region=japan; kind=book -->\n"),
    ("research/assets/money-conversions.json", "{\"eras\": {\"edo\": {\"place\": \"Edo\", \"years\": \"1745-1754\", \"basket_coverage\": \"rice\", \"goods_left_out\": [\"Fish\"], \"confidence\": \"good\", \"units\": {\"ryo\": {\"goods_dollars\": 100, \"goods_dollars_high\": 150, \"wage_dollars\": 50, \"rokugan_sen\": 1000}}}}}"),
    ("{Q}/0002-coins.html", "<h2 id=\"coins\">Coins <span class=\"xref\">(see too)</span></h2>\n<!-- tags: subject=money; setting=town; level=foundational -->\n<!-- a comment --><p>Coins are <b>round</b>&amp; flat! More. <span class=\"money\" data-amount=\"3\" data-coin=\"ryo\" data-era=\"edo\">3 ryo</span> <a href=\"../assets/record.css\">css</a> <a href=\"0001-paddies.html#paddies\">p</a> <a href=\"../SOURCES.html#src-a\">a</a></p>\n"),
    ("research/assets/record.css", "body {}\n"),
    ("research/assets/record.js", "// record\n"),
    ("research/assets/site.css", "nav {}\n"),
    ("research/assets/site.js", "// site\r\n"),
    ("research/assets/theme.js", "// theme\n"),
    ("research/assets/glossary-variants.txt", "bund\tbund\nembankment\tbund\nochiba\tochiba\n"),
    ("l7r/diagram/interactive/assets/glossary.json", "{\n \"bund\": {\n  \"def\": \"A low bank.\",\n  \"variants\": [\n   \"bund\",\n   \"embankment\"\n  ]\n },\n \"ochiba\": {\n  \"def\": \"Fallen leaves.\",\n  \"variants\": [\n   \"ochiba\"\n  ],\n  \"cased\": true\n }\n}\n"),
    ("l7r/diagram/interactive/assets/glossary/0010-bund.json", "{\n \"term\": \"bund\",\n \"def\": \"A low bank.\",\n \"variants\": [\n  \"bund\",\n  \"embankment\"\n ]\n}\n"),
    ("l7r/diagram/interactive/assets/glossary/0020-ochiba.json", "{\n \"term\": \"ochiba\",\n \"def\": \"Fallen leaves.\",\n \"variants\": [\n  \"ochiba\"\n ],\n \"cased\": true\n}\n"),
    (".claude/agents/source-applicability.md", "# contract\n<!-- source-tags: DERIVED by make source-tags-contract from research/source-tags.json - edit the vocabulary, never here -->\nold\n<!-- /source-tags -->\nend\n"),
];

/// The record under `research/` of a tree that builds its site cleanly: the crate's record less what its lists refuse (the blocked
/// entry, the banned section, the archive's uncovered rows), with [`TREE`] beside it.
///
/// # Panics
/// A record the crate's archive reader refuses, which the fixture never is.
pub fn tree() -> TempDir {
    let dir = scratch("research-tree");
    for (rel, text) in FILES {
        if rel.starts_with("archive/")
            || rel.ends_with("0030-grok.html")
            || rel.ends_with("020-other.html")
        {
            continue;
        }
        put(&dir, &format!("research/{rel}"), text);
    }
    for (rel, text) in TREE {
        // a question's path built from its parts, so no fixture names a question of the real record
        put(
            &dir,
            &rel.replace(
                "{Q}",
                &format!("research/{}", crate::record::questions::QUESTIONS),
            ),
            text,
        );
    }
    let research = dir.join("research");
    for (url, _) in crate::record::archive::cited(&research).unwrap() {
        let id = crate::record::archive::url_id(&url);
        put(&research, &format!("archive/{}/{id}.json", &id[..2]), "{\"outcome\": \"archived\", \"captured\": \"2026-10-01T00:00:00Z\", \"path\": \"aa/x\"}");
    }
    dir
}
