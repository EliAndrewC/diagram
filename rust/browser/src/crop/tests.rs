//! The glyph crop (feature 449 T146), on the tests' Chromium: the steps run, the PNG and the kinds written, each refusal.

use l7r_guard::shared::tempdir::TempDir;

use super::{crop, options};
use crate::page::Browser;
use crate::testkit::{fake_chrome, var_for};

#[test]
fn a_crop_writes_the_png_and_the_kinds_sorted() {
    let dir = TempDir::new("browser-crop");
    let fake = fake_chrome(dir.path());
    let mut b = Browser::open(&var_for(&fake), options()).unwrap();
    for name in ["grows.html", "big.html", "small.html"] {
        let out = dir.path().join(format!("{name}.png"));
        crop(&mut b, &dir.path().join(name), "k", &out).unwrap();
        assert_eq!(std::fs::read(&out).unwrap(), b"\x89PNG fake");
        assert_eq!(
            std::fs::read_to_string(format!("{}.kinds", out.display())).unwrap(),
            "alpha\nzeta"
        );
    }
}

#[test]
fn a_crop_fails_where_the_python_died() {
    let dir = TempDir::new("browser-crop-fail");
    let fake = fake_chrome(dir.path());
    let mut b = Browser::open(&var_for(&fake), options()).unwrap();
    let out = dir.path().join("x.png");
    let err = crop(&mut b, &dir.path().join("noglyph.html"), "k", &out).unwrap_err();
    assert!(err.starts_with("TypeError: cannot unpack non-iterable NoneType object"));
    assert!(crop(&mut b, &dir.path().join("neterr.html"), "k", &out)
        .unwrap_err()
        .starts_with("page.goto: net::ERR_ABORTED"));
    assert!(crop(
        &mut b,
        &dir.path().join("big.html"),
        "k",
        &dir.path().join("no/dir/x.png")
    )
    .is_err());
    // the PNG written and its kinds not: a directory stands where the kinds go
    std::fs::create_dir_all(dir.path().join("y.png.kinds")).unwrap();
    assert!(crop(
        &mut b,
        &dir.path().join("big.html"),
        "k",
        &dir.path().join("y.png")
    )
    .unwrap_err()
    .contains("y.png.kinds"));
    assert!(!out.exists());
    assert_eq!((options().width, options().height), (1200, 900));
}

/// FR-008's one end-to-end test (ask:449-T167-realtree): the browser's (`ask:449-T80-order`: the browser behind one seam, with one
/// end-to-end test): the pinned Chromium itself, a local page rendered and a glyph on it cropped - no network, a `file://` page; and
/// (feature 449 T150) a page lit and photographed before and after.
#[test]
fn the_real_chromium_renders_and_crops_a_local_page() {
    let dir = TempDir::new("browser-e2e");
    let page = dir.path().join("map.html");
    std::fs::write(
        &page,
        "<!DOCTYPE html><html><body><p>a map</p><svg width='800' height='600'>\
         <g class='f' data-k='well'><rect x='100' y='100' width='300' height='250' fill='#336'/></g>\
         <g class='f' data-k='far'><rect x='700' y='550' width='10' height='10'/></g></svg></body></html>",
    )
    .unwrap();
    let var = crate::chromium::env_var;
    let mut b = Browser::open(&var, options()).unwrap();
    let out = dir.path().join("crop.png");
    crop(&mut b, &page, "well", &out).unwrap();
    let png = std::fs::read(&out).unwrap();
    assert_eq!(&png[..8], b"\x89PNG\r\n\x1a\n");
    assert_eq!(
        std::fs::read_to_string(format!("{}.kinds", out.display())).unwrap(),
        "well"
    );
    let (mhtml, text) = crate::serve::render(
        &mut b,
        &format!("file://{}", page.display()),
        std::time::Duration::from_secs(30),
        std::time::Duration::from_secs(2),
    )
    .unwrap();
    assert!(mhtml.starts_with("From: <Saved by Blink>"));
    assert_eq!(text, "a map");
    // (feature 449 T150) the lit page, `page_lit`'s browser half, on a page whose map API lights its one class: the shots differ there
    let lit_page = dir.path().join("lit.html");
    std::fs::write(
        &lit_page,
        "<!DOCTYPE html><html><body style='margin:0'><svg id='map' viewBox='0 0 100 100' width='400' height='400'>\
         <rect id='w' x='10' y='10' width='50' height='50' fill='#336'/></svg><script>window.l7rMap = {rasterReady: () => true, \
         mode: () => 'vector', zoom: () => 1, highlight: (k) => { document.getElementById('w').setAttribute('fill', k ? '#fc0' : '#336'); }};\
         </script></body></html>",
    )
    .unwrap();
    let mut b = Browser::open(&var, crate::lit::options()).unwrap();
    let got = crate::lit::lit(&mut b, &lit_page, "well", true).unwrap();
    assert_eq!(
        (got.mode, got.ctm, got.viewbox),
        (
            serde_json::json!("vector"),
            serde_json::json!([4, 0, 0, 4, 0, 0]),
            serde_json::json!([0, 0, 100, 100])
        )
    );
    assert!(got.before.starts_with(b"\x89PNG") && got.before != got.after);
}
