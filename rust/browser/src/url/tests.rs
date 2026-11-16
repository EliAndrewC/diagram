//! A URL as Playwright's request read it (feature 449 T146): each expected value the one Playwright 1.62 reported as `response.url`
//! for the same input (observed 2026-11-16, method: the T146 differential's `url_probe.py` against its loopback server).

use super::{parse, punycode};

fn href(u: &str) -> String {
    parse(u).unwrap().href
}

#[test]
fn it_serializes_as_node_did() {
    assert_eq!(
        href("http://WWW.Site-A.test:80/p/p5.html"),
        "http://www.site-a.test/p/p5.html"
    );
    assert_eq!(href("http://www.site-a.test"), "http://www.site-a.test/");
    assert_eq!(
        href("http://www.site-a.test/a/../p/./p5.html"),
        "http://www.site-a.test/p/p5.html"
    );
    assert_eq!(
        href("http://www.site-a.test/p/p5.html#section-2"),
        "http://www.site-a.test/p/p5.html#section-2"
    );
    assert_eq!(
        href("http://www.site-a.test/日本 語?q=日本 x&y='z'#frag"),
        "http://www.site-a.test/%E6%97%A5%E6%9C%AC%20%E8%AA%9E?q=%E6%97%A5%E6%9C%AC%20x&y=%27z%27#frag"
    );
    assert_eq!(
        href("http://www.site-a.test/%7Euser/%41?x=%20"),
        "http://www.site-a.test/%7Euser/%41?x=%20"
    );
    assert_eq!(
        href("http://www.site-a.test/path with\"quote<>`{}|\\^"),
        "http://www.site-a.test/path%20with%22quote%3C%3E%60%7B%7D|/%5E"
    );
    assert_eq!(
        href("https://www.site-a.test:443/p/p6.html?"),
        "https://www.site-a.test/p/p6.html?"
    );
    assert_eq!(
        href("http://www.site-a.test/wiki/A_(b)"),
        "http://www.site-a.test/wiki/A_(b)"
    );
    assert_eq!(
        href("http://user:pa ss@www.site-a.test/x"),
        "http://user:pa%20ss@www.site-a.test/x"
    );
    assert_eq!(
        href("http://user:@www.site-a.test/x"),
        "http://user@www.site-a.test/x"
    );
    assert_eq!(
        href("http://@www.site-a.test/x"),
        "http://www.site-a.test/x"
    );
    assert_eq!(href("http://h.test:8080/a/b/.."), "http://h.test:8080/a/");
    assert_eq!(href("http://h.test/a/%2E%2e/b/%2e"), "http://h.test/b/");
    assert_eq!(href(" \thttp://h.test/a\n/b "), "http://h.test/a/b");
    assert_eq!(href("http://h.test/x#a b"), "http://h.test/x#a%20b");
    let u = parse("https://h.test:8443/x#f").unwrap();
    assert_eq!(
        (
            u.scheme.as_str(),
            u.host.as_str(),
            u.port,
            u.target.as_str()
        ),
        ("https", "h.test", Some(8443), "https://h.test:8443/x")
    );
    assert_eq!(
        href("http://bücher.example/"),
        "http://xn--bcher-kva.example/"
    );
    assert_eq!(href("http://日本語.jp/"), "http://xn--wgv71a119e.jp/");
}

#[test]
fn it_refuses_what_playwright_would_not_request() {
    assert_eq!(
        parse("ftp://h.test/x").unwrap_err(),
        "Protocol \"ftp:\" not supported. Expected \"http:\""
    );
    assert_eq!(parse("no scheme").unwrap_err(), "Invalid URL: no scheme");
    assert_eq!(parse("http://").unwrap_err(), "Invalid URL: http://");
    // a special scheme's extra slashes are skipped, as WHATWG skips them
    assert_eq!(href("http:///x"), "http://x/");
    assert_eq!(
        parse("http://h.test:port/").unwrap_err(),
        "Invalid URL: http://h.test:port/"
    );
}

#[test]
fn punycode_matches_rfc_3492() {
    assert_eq!(punycode("bücher"), "bcher-kva");
    assert_eq!(punycode("日本語"), "wgv71a119e");
    assert_eq!(punycode("ñandú"), "and-6ma2c");
    assert_eq!(punycode("münchen-ost"), "mnchen-ost-9db");
}
