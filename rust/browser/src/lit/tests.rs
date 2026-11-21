//! The lit page (feature 449 T150), on the tests' Chromium: the steps run, the zoom key pressed until vector mode, each refusal.

use l7r_shared::tempdir::TempDir;
use serde_json::json;

use super::{lit, options, ZOOM_STEPS};
use crate::page::Browser;
use crate::testkit::{fake_chrome, var_for};

#[test]
fn a_page_is_lit_and_photographed_before_and_after() {
    let dir = TempDir::new("browser-lit");
    let fake = fake_chrome(dir.path());
    let mut b = Browser::open(&var_for(&fake), options()).unwrap();
    let got = lit(&mut b, &dir.path().join("map.html"), "well", false).unwrap();
    assert_eq!(
        (got.mode, got.zoom, got.ctm, got.viewbox),
        (
            json!("vector"),
            json!(1.5),
            json!([2, 0, 0, 2, 10.5, -4]),
            json!([0, 0, 10, 10])
        )
    );
    assert_eq!(
        (got.before.as_slice(), got.after.as_slice()),
        (&b"\x89PNG fake"[..], &b"\x89PNG fake"[..])
    );
    // the zoom key pressed until the page says vector: twice on `zoomy`, never more than ZOOM_STEPS on `stuck`
    let zoomed = lit(&mut b, &dir.path().join("zoomy-novb.html"), "well", true).unwrap();
    assert_eq!(
        (zoomed.mode, zoomed.viewbox),
        (json!("vector"), json!(null))
    );
    let stuck = lit(&mut b, &dir.path().join("stuck.html"), "well", true).unwrap();
    assert_eq!(stuck.mode, json!("raster"));
    assert_eq!(
        (options().width, options().height, ZOOM_STEPS),
        (1400, 1000, 24)
    );
}

#[test]
fn a_page_that_never_readies_or_throws_is_refused() {
    let dir = TempDir::new("browser-lit-fail");
    let fake = fake_chrome(dir.path());
    let mut b = Browser::open(&var_for(&fake), options()).unwrap();
    let err = lit(&mut b, &dir.path().join("notready.html"), "k", false).unwrap_err();
    assert!(err.starts_with("page.wait_for_function: Timeout "), "{err}");
    let err = lit(&mut b, &dir.path().join("readythrow.html"), "k", false).unwrap_err();
    assert_eq!(err, "page.evaluate: TypeError: no raster");
    let err = lit(&mut b, &dir.path().join("neterr.html"), "k", false).unwrap_err();
    assert!(err.starts_with("page.goto: net::ERR_ABORTED"));
}
