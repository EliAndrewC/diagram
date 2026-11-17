//! Fetching a page (feature 449 T145; each URL's expected parts and quoting `urllib.parse`'s and `quote_verbatim.quoted_url`'s, 2026-11-16).

use std::io::{BufRead, BufReader, Write};
use std::net::TcpListener;

use super::{
    charset_of, idna, is_pdf, last_status, name_for, quote, quoted_url, urlsplit, Curl, Got, Pages,
    Response, Transport,
};

#[test]
fn a_url_is_split_as_urllib_splits_it() {
    let ok =
        |u: &str, want: [&str; 5]| assert_eq!(urlsplit(u).unwrap(), want.map(str::to_owned), "{u}");
    ok(
        "https://ja.wikipedia.org/wiki/\u{30a2}?q=x#frag",
        ["https", "ja.wikipedia.org", "/wiki/\u{30a2}", "q=x", "frag"],
    );
    ok("  http://a.b/c?d#e", ["http", "a.b", "/c", "d", "e"]);
    ok("HTTP://X.org", ["http", "X.org", "", "", ""]);
    ok("mailto:x@y", ["mailto", "", "x@y", "", ""]);
    ok("//host/p", ["", "host", "/p", "", ""]);
    ok("1http://a", ["", "", "1http://a", "", ""]);
    ok("http://[::1]:80/p", ["http", "[::1]:80", "/p", "", ""]);
    ok("http://u@[v1.x]/p", ["http", "u@[v1.x]", "/p", "", ""]);
    ok("http://h/p\t\n x", ["http", "h", "/p x", "", ""]);
    ok(
        "http://m\u{fc}nchen.de/",
        ["http", "m\u{fc}nchen.de", "/", "", ""],
    );
    for (bad, why) in [
        ("http://[bad/p", "Invalid IPv6 URL"),
        ("http://bad]/p", "Invalid IPv6 URL"),
        ("http://[vz]/p", "IPvFuture address is invalid"),
        ("http://[1.2.3.4]/", "An IPv4 address cannot be in brackets"),
        ("http://[::1]x/", "Invalid IPv6 URL"),
        ("http://a[::1]/", "Invalid IPv6 URL"),
        (
            "http://ex\u{2100}ample.org/",
            "netloc 'ex\u{2100}ample.org' contains invalid characters under NFKC normalization",
        ),
    ] {
        assert_eq!(urlsplit(bad).unwrap_err(), why, "{bad}");
    }
    assert!(urlsplit("http://[zz]/")
        .unwrap_err()
        .contains("does not appear"));
    assert!(urlsplit("http://[x@y]@z/")
        .unwrap_err()
        .contains("does not appear"));
}

#[test]
fn a_url_is_quoted_as_the_python_quoted_it() {
    let q = |u: &str| quoted_url(u).unwrap();
    assert_eq!(
        q("https://ja.wikipedia.org/wiki/\u{30a2}\u{30d6}\u{30e9}\u{30ca}?q=\u{6771} \u{4eac}#frag"),
        "https://ja.wikipedia.org/wiki/%E3%82%A2%E3%83%96%E3%83%A9%E3%83%8A?q=%E6%9D%B1%20%E4%BA%AC"
    );
    assert_eq!(
        q("http://m\u{fc}nchen.de/stra\u{df}e"),
        "http://xn--mnchen-3ya.de/stra%C3%9Fe"
    );
    assert_eq!(q("http:"), "http://");
    assert_eq!(q("http:///path"), "http:///path");
    assert_eq!(q("mailto:x@y"), "mailto:x@y");
    assert_eq!(q("relative/path"), "relative/path");
    assert_eq!(q("//host/p"), "//host/p");
    assert_eq!(q("x:a"), "x:a");
    assert_eq!(q("file:x"), "file:x");
    assert_eq!(q("ftp:////p"), "ftp:////p");
    assert_eq!(q("x:////p"), "x:////p");
    assert!(quoted_url("http://a..b/")
        .unwrap_err()
        .starts_with("UnicodeEncodeError"));
    assert!(quoted_url(&format!("http://{}.org/", "a".repeat(64))).is_err());
    assert!(quoted_url("http://[bad/").is_err());
    assert_eq!(idna("a.b.").unwrap(), "a.b.");
    assert_eq!(idna("\u{4f8b}\u{3002}jp").unwrap(), "xn--fsq.jp");
    assert_eq!(idna("\u{ff21}b.c").unwrap(), "ab.c");
    assert_eq!(
        idna("\u{30c9}\u{30e1}\u{30a4}\u{30f3}\u{540d}\u{4f8b}").unwrap(),
        "xn--eckwd4c7cu47r2wf"
    );
    assert_eq!(
        idna("\u{4f8b}\u{3048}\u{3070}\u{3053}\u{308c}\u{306f}\u{3068}\u{3066}\u{3082}\u{9577}\u{3044}\u{30e9}\u{30d9}\u{30eb}\u{3067}\u{3059}").unwrap(),
        "xn--n8jh7aza7dhe9ch8p2d07b6f3a2078id27k"
    );
    assert_eq!(quote("", "/"), "");
    assert_eq!(quote("a b/~", "/"), "a%20b/~");
}

#[test]
fn a_pdf_and_a_name_and_a_charset() {
    assert!(
        is_pdf("http://a/B.PDF", "")
            && is_pdf("http://a/x/_pdf?q", "")
            && is_pdf("http://a/x", "application/PDF")
    );
    assert!(!is_pdf("http://a/x.pdf.html", "") && !is_pdf("http://[bad/x", ""));
    assert_eq!(name_for("https://e.org/a"), "870874689b298a27.html");
    assert_eq!(charset_of("text/html; Charset=\"Shift_JIS\""), "shift_jis");
    assert_eq!(charset_of("text/html;x=1"), "");
    assert_eq!(charset_of("text/html"), "");
    let heads = "HTTP/1.1 302 Found\r\nLocation: x\r\n\r\nHTTP/1.1 404 Not Here\r\nContent-Type: text/plain\r\n\r\n";
    assert_eq!(
        last_status(heads),
        (404, "Not Here".to_owned(), "text/plain".to_owned())
    );
    assert_eq!(
        last_status("HTTP/1.0 200\r\n"),
        (200, String::new(), String::new())
    );
    assert_eq!(Got::fetched("t".into()).state, "FETCHED");
}

/// One canned answer: the content type and body, or the failure.
type Answer = Result<(String, Vec<u8>), String>;

/// A transport that answers from a list, counting what it was asked.
struct Canned(Vec<(String, Answer)>, std::rc::Rc<std::cell::Cell<usize>>);

impl Transport for Canned {
    fn open(&mut self, url: &str) -> Result<Response, String> {
        self.1.set(self.1.get() + 1);
        let (_, got) = self
            .0
            .iter()
            .find(|(u, _)| u == url)
            .cloned()
            .unwrap_or_else(|| (url.to_owned(), Err("URLError: x".into())));
        got.map(|(ctype, body)| Response {
            charset: charset_of(&ctype),
            content_type: ctype,
            body,
        })
    }
}

#[test]
fn each_page_once_and_each_refusing_host_once() {
    let asked = std::rc::Rc::new(std::cell::Cell::new(0));
    let canned = Canned(
        vec![
            (
                "http://a.org/p".into(),
                Ok((
                    "text/html; charset=utf-8".into(),
                    b"<p>Hi &amp; bye</p>".to_vec(),
                )),
            ),
            (
                "http://a.org/d.pdf".into(),
                Ok(("text/html".into(), b"x".to_vec())),
            ),
            (
                "http://a.org/doc".into(),
                Ok(("application/pdf".into(), Vec::new())),
            ),
            (
                "http://a.org/bin".into(),
                Ok(("text/html".into(), b"\x81".to_vec())),
            ),
        ],
        asked.clone(),
    );
    let mut pages = Pages::new(None, Box::new(canned));
    assert_eq!(pages.get("http://a.org/p").unwrap().text, "Hi & bye");
    assert_eq!(pages.get("http://a.org/p").unwrap().text, "Hi & bye");
    assert_eq!(asked.get(), 1);
    assert!(pages.get("http://a.org/d.pdf").unwrap().live);
    assert_eq!(pages.get("http://a.org/doc").unwrap().state, "NOT-CHECKED");
    assert_eq!(
        pages.get("http://a.org/bin").unwrap().why,
        "the page would not decode in any charset tried"
    );
    assert_eq!(pages.get("http://b.org/x").unwrap().why, "URLError: x");
    assert_eq!(
        pages.get("http://b.org/y").unwrap().why,
        "b.org already refused this run: URLError: x"
    );
    assert_eq!(
        pages.refused,
        vec![("b.org".to_owned(), "URLError: x".to_owned())]
    );
    assert_eq!(pages.get("notes/x.html").unwrap().state, "OWN");
    assert!(pages.get("http://[bad/x").is_err());
    let d = l7r_guard::shared::tempdir::TempDir::new("research-offline");
    std::fs::write(d.join(name_for("http://a.org/p")), "<p>saved</p>").unwrap();
    let mut off = Pages::new(Some(&d), Box::new(Curl::default()));
    assert_eq!(off.get("http://a.org/p").unwrap().text, "saved");
    assert_eq!(off.get("http://a.org/q").unwrap().why, "no offline copy");
    assert_eq!(off.get("http://a.org/q.pdf").unwrap().state, "NOT-CHECKED");
}

/// One response from a listener on the loopback, its request's first line kept.
fn serve_once(reply: &'static [u8]) -> (String, std::thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let url = format!(
        "http://127.0.0.1:{}/page",
        listener.local_addr().unwrap().port()
    );
    let handle = std::thread::spawn(move || {
        let (mut stream, _) = listener.accept().unwrap();
        let mut first = String::new();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        reader.read_line(&mut first).unwrap();
        let mut line = String::new();
        while reader.read_line(&mut line).unwrap_or(0) > 2 {
            line.clear();
        }
        stream.write_all(reply).unwrap();
        first
    });
    (url, handle)
}

/// FR-008's one end-to-end test (ask:449-T167-realtree): the seam's, `curl` run against a loopback listener, a page and a refusal.
#[test]
fn curl_fetches_and_names_a_status() {
    let (url, served) = serve_once(b"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: 5\r\nConnection: close\r\n\r\nhello");
    let got = Curl::default().open(&url).unwrap();
    assert_eq!(
        (got.body.as_slice(), got.charset.as_str()),
        (b"hello".as_slice(), "utf-8")
    );
    assert!(served.join().unwrap().starts_with("GET /page HTTP/1.1"));
    let (url, served) =
        serve_once(b"HTTP/1.1 404 Gone Away\r\nContent-Length: 0\r\nConnection: close\r\n\r\n");
    assert_eq!(
        Curl::default().open(&url).unwrap_err(),
        "HTTPError: HTTP Error 404: Gone Away"
    );
    served.join().unwrap();
    assert!(Curl::default()
        .open("http://127.0.0.1:9/x")
        .unwrap_err()
        .starts_with("URLError: <urlopen error"));
    assert!(Curl {
        program: "/no/such/curl".into()
    }
    .open("http://x")
    .unwrap_err()
    .starts_with("OSError"));
    // a redirect without end: refused as `urlopen` refused it, after the ten it allows
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let url = format!(
        "http://127.0.0.1:{}/loop",
        listener.local_addr().unwrap().port()
    );
    let looping = std::thread::spawn(move || {
        for _ in 0..11 {
            let (mut stream, _) = listener.accept().unwrap();
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let mut line = String::new();
            while reader.read_line(&mut line).unwrap_or(0) > 2 {
                line.clear();
            }
            stream.write_all(b"HTTP/1.1 302 Found\r\nLocation: /loop\r\nContent-Length: 0\r\nConnection: close\r\n\r\n").unwrap();
        }
    });
    assert_eq!(
        Curl::default().open(&url).unwrap_err(),
        "HTTPError: HTTP Error 302: The HTTP server returned a redirect error that would lead to an infinite loop.\nThe last 30x error message was:\nFound"
    );
    looping.join().unwrap();
}
