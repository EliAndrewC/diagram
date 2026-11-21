//! A context's pages (feature 449 T146), on the tests' Chromium.

use std::time::Duration;

use l7r_shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::{lifecycle, Browser, Options};
use crate::testkit::{fake_chrome, var_for};

fn options(ua: bool) -> Options {
    Options {
        width: 1280,
        height: 720,
        user_agent: ua.then(|| "UA/1".to_owned()),
        ignore_https_errors: ua,
    }
}

#[test]
fn a_page_loads_goes_idle_and_reads_back() {
    let dir = TempDir::new("browser-page");
    let fake = fake_chrome(dir.path());
    let mut b = Browser::open(&var_for(&fake), options(true)).unwrap();
    assert_eq!(b.context, "C1");
    let page = b.new_page().unwrap();
    assert_eq!(
        (
            page.target.as_str(),
            page.session.as_str(),
            page.frame.as_str()
        ),
        ("T1", "S1", "F1")
    );
    let loader = b.goto(&page, "http://x/a", Duration::from_secs(5)).unwrap();
    assert_eq!(loader, "L1");
    assert!(b.wait_idle(&page, &loader, Duration::from_secs(5)));
    assert_eq!(b.mhtml(&page).unwrap(), "MHTML of http://x/a");
    assert_eq!(
        b.body_text(&page, Duration::from_secs(1)).unwrap(),
        "the text of http://x/a"
    );
    assert_eq!(
        b.evaluate(&page, "() => 1", &Value::Null).unwrap(),
        Value::Null
    );
    b.mouse_move(&page, 1.5, 2.0).unwrap();
    b.control_wheel(&page, 1.5, 2.0, -240.0).unwrap();
    assert_eq!(
        b.screenshot(&page, &json!({"x": 0, "y": 0, "width": 10, "height": 10}))
            .unwrap(),
        b"\x89PNG fake"
    );
    assert!(b.cookies().unwrap().is_empty());
    b.set_cookies(&[]).unwrap();
    b.set_cookies(&[json!({"name": "a", "value": "1", "domain": "x", "path": "/", "expires": -1})])
        .unwrap();
    assert_eq!(b.cookies().unwrap().len(), 1);
    b.close_page(&page);
}

#[test]
fn a_navigation_that_fails_or_never_loads_and_a_page_with_no_body() {
    let dir = TempDir::new("browser-page-fail");
    let fake = fake_chrome(dir.path());
    let mut b = Browser::open(&var_for(&fake), options(false)).unwrap();
    let page = b.new_page().unwrap();
    assert_eq!(
        b.goto(&page, "http://x/neterr", Duration::from_secs(5))
            .unwrap_err(),
        "page.goto: net::ERR_ABORTED at http://x/neterr"
    );
    assert_eq!(
        b.goto(&page, "http://x/samedoc", Duration::from_secs(5))
            .unwrap(),
        ""
    );
    assert_eq!(
        b.goto(&page, "http://x/noload", Duration::from_millis(20))
            .unwrap_err(),
        "page.goto: Timeout 20ms exceeded."
    );
    let loader = b
        .goto(&page, "http://x/busy/nobody", Duration::from_secs(5))
        .unwrap();
    assert!(!b.wait_idle(&page, &loader, Duration::from_millis(10)));
    assert_eq!(
        b.body_text(&page, Duration::from_millis(15)).unwrap_err(),
        "locator.innerText: Timeout 15ms exceeded."
    );
    b.goto(&page, "http://x/throw", Duration::from_secs(5))
        .unwrap();
    assert_eq!(
        b.body_text(&page, Duration::from_secs(1)).unwrap_err(),
        "page.evaluate: Error: thrown"
    );
    assert_eq!(
        b.evaluate(&page, "() => throwplain", &Value::Null)
            .unwrap_err(),
        "page.evaluate: Uncaught plain"
    );
    assert_eq!(
        b.evaluate(&page, "() => throwbare", &Value::Null)
            .unwrap_err(),
        "page.evaluate: error"
    );
    b.launched.cdp.close();
    assert!(b.new_page().is_err());
    assert!(b.cookies().is_err());
    let none = dir.path().join("none");
    assert!(Browser::open(&var_for(&none), options(false)).is_err());
}

#[test]
fn only_the_pages_own_lifecycle_event_counts() {
    let e = json!({"method": "Page.lifecycleEvent", "sessionId": "S", "params": {"frameId": "F", "loaderId": "L", "name": "load"}});
    assert!(lifecycle(&e, "S", "F", "L", "load"));
    assert!(!lifecycle(&e, "S", "F", "L", "networkIdle"));
    assert!(!lifecycle(&e, "S", "F", "M", "load"));
    assert!(!lifecycle(&e, "S", "G", "L", "load"));
    assert!(!lifecycle(&e, "T", "F", "L", "load"));
    assert!(!lifecycle(
        &json!({"method": "Other"}),
        "S",
        "F",
        "L",
        "load"
    ));
}
