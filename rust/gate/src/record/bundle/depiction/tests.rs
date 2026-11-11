//! What a modal-depiction bundle reads: drawing pages and candidates, the knobs, the claims, the pool page and its crop.

use std::path::Path;

use serde_json::json;

use super::*;
use crate::record::bundle::modal::{bundle, Ask};
use crate::record::bundle::tests::scratch;
use crate::record::testkit::{commit, git, put, WELL};

const POOL_PAGE: &str = "<svg viewBox=\"0 0 9 9\"><g class=\"f k\" data-k=\"well\"><rect x=\"1\" y=\"2\" width=\"3\" stroke-width=\"9\"/><circle cx=\"4\" cy=\"5\" r=\"6\"/></g><g class=\"f o\" data-k=\"o\"><rect x=\"9\"/></g></svg>";

fn depiction(root: &Path, out: &str) -> (i32, Run) {
    let mut run = Run::new(root);
    let code = bundle(
        &mut run,
        root,
        "hamlet/well",
        &Ask {
            for_: "modal-depiction",
            out,
            reason: "a backfill asked",
            order_ok: "an audit asked",
        },
    )
    .unwrap_or_else(|e| {
        run.err.push_str(&e);
        -1
    });
    (code, run)
}

#[test]
fn a_depiction_bundle_with_its_crop() {
    let root = scratch("modal-depiction");
    put(&root, WELL, "Name: Well\nAbout: [winter_crop=wheat] A well.\n[role=x] and [empty=y]\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(&root, "research/questions/0094-trade.drawing.html", "<h2>How drawn</h2>\n<p>See <a href=\"0098-more.drawing.html\">more</a> and <a href=\"x/0099-gone.drawing.html\">gone</a>.</p>\n");
    put(
        &root,
        "research/questions/0098-more.drawing.html",
        "<h2>More</h2>\n",
    );
    put(
        &root,
        "research/questions/0095-other.drawing.html",
        "<h2>Other drawn</h2>\n",
    );
    put(
        &root,
        "rust/phases/src/a.rs",
        "let k = \"winter_crop\";\n// \"winter_crop\" - a comment\n",
    );
    put(&root, "dev/claims-index.json", &json!({"l7r/diagram/x.py::A#a": {"verdict": "DRIFTED", "pages": ["research/questions/0094-trade.drawing.html"], "note": "n"}, "l7r/diagram/y.py::B#b": {"pages": "0098-more.drawing.html"}, "z::C#c": {"pages": ["0001-unrelated.html"]}}).to_string());
    put(&root, "pool/hamlets/h1/h1.html", POOL_PAGE);
    put(&root, "pool/hamlets/h1-test/h1.html", POOL_PAGE);
    put(&root, "pool/sheets/s1/s1.html", "<g>none</g>");
    put(&root, "pool/notes.txt", "a file among the trees");
    let o = root.join("out").to_string_lossy().into_owned();
    let (code, _) = depiction(&root, &o);
    assert_eq!(code, 0);
    let glyph = std::fs::read_to_string(root.join("out/glyph.txt")).unwrap();
    assert!(
        glyph.contains("- `well` opens `hamlet/well`\n- `other` opens the `other` pop-up")
            && glyph.contains(
                "- <rect> x=\"1\" y=\"2\" width=\"3\"\n- <circle> cx=\"4\" cy=\"5\" r=\"6\"\n"
            )
    );
    let knobs = std::fs::read_to_string(root.join("out/knobs.md")).unwrap();
    assert!(
        knobs.contains("## winter_crop\n\nforms: none, wheat; default none\n")
            && knobs.contains("```python\ndef rule():\n    pass\n```")
            && knobs.contains("- `rust/phases/src/a.rs:1: let k = \"winter_crop\";`")
            && knobs.contains("## role\n\nforms: (not registered)")
            && knobs.contains("## empty\n\nforms: (not registered)\n")
    );
    let claims = std::fs::read_to_string(root.join("out/claims.md")).unwrap();
    assert!(claims.contains("- DRIFTED | `x.py::A#a` | n\n- ? | `y.py::B#b` | \n"));
    let text = std::fs::read_to_string(root.join("out/MANIFEST.md")).unwrap();
    assert!(
        text.contains("| `drawing/0098-more.drawing.html` |") && !text.contains("drawing/0099")
    );
    assert!(!root.join("out/glyph.png.kinds").exists());
}

#[test]
fn no_crop_a_stale_page_and_the_failures() {
    let root = scratch("modal-depiction-none");
    let o = root.join("out").to_string_lossy().into_owned();
    let (code, _) = depiction(&root, &o);
    assert_eq!(code, 0);
    assert!(std::fs::read_to_string(root.join("out/glyph.txt"))
        .unwrap()
        .starts_with("no crop: the kind `well` is drawn on no pool page"));
    put(&root, "pool/hamlets/nocrop/nocrop.html", POOL_PAGE);
    let (code, _) = depiction(&root, &o);
    assert_eq!(code, 0);
    assert!(std::fs::read_to_string(root.join("out/glyph.txt"))
        .unwrap()
        .contains("the browser could not crop it from `pool/hamlets/nocrop/nocrop.html`"));
    put(&root, "pool/hamlets/nocrop/nocrop.svg", "<svg/>");
    let page = root.join("pool/hamlets/nocrop/nocrop.html");
    let old = std::time::SystemTime::now() - std::time::Duration::from_secs(60);
    std::fs::File::options()
        .write(true)
        .open(&page)
        .unwrap()
        .set_modified(old)
        .unwrap();
    let (code, run) = depiction(&root, &o);
    assert_eq!(code, -1);
    assert!(run.err.contains("nocrop.html is older than nocrop.svg - its crop would show the drawing before the edit; regenerate it first: make map GEN=pool/hamlets/nocrop/nocrop.gen.py"));
    std::fs::remove_dir_all(root.join("pool/hamlets/nocrop")).unwrap();
    put(&root, "pool/hamlets/slow/slow.html", POOL_PAGE);
    let (code, run) = depiction(&root, &format!("{o}1"));
    assert_eq!(code, -1);
    assert!(run.err.contains("TimeoutExpired"));
    std::fs::remove_dir_all(root.join("pool/hamlets/slow")).unwrap();
    put(&root, "dev/claims-index.json", "not json");
    assert_eq!(depiction(&root, &format!("{o}2")).0, -1);
    std::fs::remove_file(root.join("dev/claims-index.json")).unwrap();
    put(&root, WELL, "Name: Well\nAbout: [winter_crop=wheat] A well.\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(&root, "rust/phases/src/b.rs", "x");
    std::fs::write(root.join("rust/phases/src/b.rs"), [0xff]).unwrap();
    assert_eq!(depiction(&root, &format!("{o}3")).0, -1);
    std::fs::remove_file(root.join("rust/phases/src/b.rs")).unwrap();
    std::fs::write(
        root.join("research/questions/0094-trade.drawing.html"),
        [0xff],
    )
    .unwrap();
    assert_eq!(depiction(&root, &format!("{o}4")).0, -1);
}

#[test]
fn the_candidates_at_the_merge_base_and_the_geometry() {
    let root = scratch("modal-depiction-base");
    put(&root, WELL, "Name: Well\nAbout: A well.\nEntry: research/questions/0095-other.drawing.html research/questions/0094-trade.html\n");
    put(
        &root,
        "research/questions/0095-other.drawing.html",
        "<h2>o</h2>",
    );
    commit(&root, "base form");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    put(
        &root,
        WELL,
        "Name: Well\nAbout: A well.\nEntry: research/questions/0094-trade.html\n",
    );
    let m = modals::find(&modals::modals_now(&root, true).unwrap(), "hamlet/well")
        .cloned()
        .unwrap();
    let got = drawing_candidates(&root, &m).unwrap();
    assert_eq!(
        got,
        vec![
            "research/questions/0094-trade.drawing.html",
            "research/questions/0095-other.drawing.html"
        ]
    );
    assert_eq!(drawn_geometry(Path::new("/no/such"), "well"), "");
    put(
        &root,
        "g.html",
        "<g data-k=\"well\"><g class=\"f x\"></g></g>",
    );
    assert_eq!(drawn_geometry(&root.join("g.html"), "well"), "");
    put(
        &root,
        "g2.html",
        "<g data-k=\"it&#x27;s\"><rect x=\"1\"/></g>",
    );
    assert!(drawn_geometry(&root.join("g2.html"), "it's").contains("viewBox ?"));
    assert_eq!(html_escape("a&<>\"'"), "a&amp;&lt;&gt;&quot;&#x27;");
    assert_eq!(stale_page(&root.join("g.html"), &root), "");
    put(&root, "g.svg", "<svg/>");
    assert_eq!(stale_page(&root.join("g.html"), &root), "");
}

#[test]
fn the_rare_paths_of_a_depiction_bundle() {
    let root = scratch("modal-depiction-rare");
    let hits: String = (0..16)
        .map(|i| format!("let k{i} = \"winter_crop\";\n"))
        .collect::<Vec<_>>()
        .concat();
    put(&root, "rust/phases/src/deep/a.rs", &hits);
    put(&root, WELL, "Name: Well\nAbout: [winter_crop=wheat] A well.\nEntry: research/questions/0095-other.html research/questions/0094-trade.drawing.html\nDrawing: research/questions/0779-gone.drawing.html\n");
    put(&root, "pool/hamlets/a/a.html", "<g data-k=\"other\"></g>");
    put(&root, "pool/hamlets/b-example/b.html", POOL_PAGE);
    put(&root, "pool/hamlets/c/nokinds.html", POOL_PAGE);
    put(&root, "pool/hamlets/d/locked.html", POOL_PAGE);
    let locked = root.join("pool/hamlets/d/locked.html");
    std::fs::set_permissions(&locked, std::os::unix::fs::PermissionsExt::from_mode(0o000)).unwrap();
    let o = root.join("out").to_string_lossy().into_owned();
    let (code, _) = depiction(&root, &o);
    std::fs::set_permissions(&locked, std::os::unix::fs::PermissionsExt::from_mode(0o644)).unwrap();
    assert_eq!(code, 0);
    let knobs = std::fs::read_to_string(root.join("out/knobs.md")).unwrap();
    assert_eq!(knobs.matches("let k").count(), 15);
    let glyph = std::fs::read_to_string(root.join("out/glyph.txt")).unwrap();
    assert!(glyph.contains("pool/hamlets/c/nokinds.html") && !glyph.contains("opens"));
    let fresh = Modal {
        cls: "x.Fresh".to_owned(),
        key: "fresh".to_owned(),
        origin: "l7r/diagram/interactive/assets/modals/hamlet/fresh.md".to_owned(),
        tags: Vec::new(),
        doc: String::new(),
    };
    assert!(drawing_candidates(&root, &fresh).unwrap().is_empty());
    let bare = crate::checks::scratch("depiction-nocommit");
    git(&bare, &["init", "-q"]);
    assert!(drawing_candidates(&bare, &fresh).unwrap().is_empty());
}
