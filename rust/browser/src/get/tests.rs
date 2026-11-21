//! The context's plain request (feature 449 T146): curl against a loopback server of the test's own, the cookies passed through the
//! tests' Chromium; no network beyond 127.0.0.1.

use std::io::{BufRead, BufReader, Write};
use std::net::TcpListener;
use std::time::Duration;

use l7r_shared::tempdir::TempDir;
use serde_json::json;

use super::{get, identity, jar_cookies, jar_line, why, Ask};
use crate::page::{Browser, Options};
use crate::testkit::{fake_chrome, var_for};
use crate::url::parse;

/// A server answering `n` requests by path, each on its own connection; its port.
fn serve(n: usize) -> u16 {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let port = listener.local_addr().unwrap().port();
    std::thread::spawn(move || {
        for stream in listener.incoming().take(n) {
            let Ok(mut s) = stream else { continue };
            let mut line = String::new();
            let mut r = BufReader::new(s.try_clone().unwrap());
            r.read_line(&mut line).unwrap();
            let mut cookie = String::new();
            loop {
                let mut h = String::new();
                r.read_line(&mut h).unwrap();
                if h.to_lowercase().starts_with("cookie:") {
                    cookie = h.trim().to_owned();
                }
                if h.trim().is_empty() {
                    break;
                }
            }
            let path = line.split(' ').nth(1).unwrap_or("/").to_owned();
            let (head, body) = match path.as_str() {
                "/ok" => ("200 OK\r\nContent-Type: text/html\r\nSet-Cookie: a=1; Path=/\r\nSet-Cookie: s=2; Path=/; HttpOnly; Max-Age=999".to_owned(), cookie),
                "/redir" => ("302 Found\r\nLocation: /ok".to_owned(), String::new()),
                "/forget" => ("200 OK\r\nSet-Cookie: a=; Path=/; Max-Age=0".to_owned(), "gone".to_owned()),
                _ => ("404 Not Found\r\nContent-Type: text/plain".to_owned(), String::new()),
            };
            let _ = write!(
                s,
                "HTTP/1.1 {head}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
                body.len()
            );
        }
    });
    port
}

fn ask<'a>(url: &'a str, headers: &'a [(String, String)]) -> Ask<'a> {
    Ask {
        url,
        headers,
        timeout: Duration::from_secs(10),
        max_redirects: 10,
        user_agent: "UA/1",
        program: "curl",
    }
}

#[test]
fn a_request_follows_redirects_and_carries_the_contexts_cookies_both_ways() {
    let dir = TempDir::new("browser-get");
    let fake = fake_chrome(dir.path());
    let options = Options {
        width: 1,
        height: 1,
        user_agent: None,
        ignore_https_errors: false,
    };
    let mut b = Browser::open(&var_for(&fake), options).unwrap();
    let port = serve(5);
    let out = dir.path().join("body");
    let headers = [("Accept".to_owned(), "*/*".to_owned())];
    let url = format!("http://127.0.0.1:{port}/redir#frag");
    let got = get(&mut b, &ask(&url, &headers), &out).unwrap();
    assert_eq!(got.status, 200);
    assert_eq!(got.url, format!("http://127.0.0.1:{port}/ok"));
    assert_eq!(got.content_type, "text/html");
    assert_eq!(std::fs::read(&out).unwrap(), b"");
    // the cookies the response set are the context's now, and go out with the next request
    assert_eq!(b.cookies().unwrap().len(), 2);
    let again = format!("http://127.0.0.1:{port}/ok#keep");
    let got = get(&mut b, &ask(&again, &headers), &out).unwrap();
    assert_eq!(got.url, again);
    assert_eq!(std::fs::read_to_string(&out).unwrap(), "Cookie: a=1; s=2");
    // a cookie the server removes is removed from the context
    get(
        &mut b,
        &ask(&format!("http://127.0.0.1:{port}/forget"), &headers),
        &out,
    )
    .unwrap();
    assert_eq!(b.cookies().unwrap().len(), 1);
    let got = get(
        &mut b,
        &ask(&format!("http://127.0.0.1:{port}/missing"), &headers),
        &out,
    )
    .unwrap();
    assert_eq!((got.status, got.content_type.as_str()), (404, "text/plain"));
    // the port is closed now: a refused connection, in Node's words (10 ms, where 100 ms was most of FR-008's bar, feature 449 T160)
    std::thread::sleep(Duration::from_millis(10));
    let refused = TcpListener::bind("127.0.0.1:0")
        .unwrap()
        .local_addr()
        .unwrap()
        .port();
    let err = get(
        &mut b,
        &ask(&format!("http://127.0.0.1:{refused}/x"), &headers),
        &out,
    )
    .unwrap_err();
    assert_eq!(
        err,
        format!("APIRequestContext.get: connect ECONNREFUSED 127.0.0.1:{refused}")
    );
    assert!(!out.exists());
    assert_eq!(
        get(&mut b, &ask("ftp://h/x", &headers), &out).unwrap_err(),
        "APIRequestContext.get: Protocol \"ftp:\" not supported. Expected \"http:\""
    );
    assert!(get(
        &mut b,
        &ask(&url, &headers),
        &dir.path().join("no/such/dir/body")
    )
    .is_err());
    let mut missing = ask(&url, &headers);
    missing.program = "/no/such/curl";
    assert!(get(&mut b, &missing, &out)
        .unwrap_err()
        .starts_with("APIRequestContext.get: curl: "));
    b.launched.cdp.close();
    assert!(get(&mut b, &ask(&url, &headers), &out).is_err());
}

#[test]
fn a_failure_reads_as_node_wrote_it() {
    let u = parse("http://h.invalid/x").unwrap();
    let t = Duration::from_secs(60);
    let nxdomain = |_: &str, _: u16| {
        Err("failed to lookup address information: Name or service not known".to_owned())
    };
    let offline = |_: &str, _: u16| {
        Err("failed to lookup address information: Temporary failure in name resolution".to_owned())
    };
    let found = |_: &str, _: u16| Ok("10.0.0.7".to_owned());
    assert_eq!(
        why(Some(6), "", &u, t, &nxdomain),
        "getaddrinfo ENOTFOUND h.invalid"
    );
    assert_eq!(
        why(Some(6), "", &u, t, &offline),
        "getaddrinfo EAI_AGAIN h.invalid"
    );
    assert_eq!(
        why(Some(7), "", &u, t, &found),
        "connect ECONNREFUSED 10.0.0.7:80"
    );
    assert_eq!(
        why(
            Some(7),
            "",
            &parse("https://h.invalid/").unwrap(),
            t,
            &nxdomain
        ),
        "connect ECONNREFUSED h.invalid:443"
    );
    assert_eq!(
        why(Some(28), "", &u, t, &found),
        "Timeout 60000ms exceeded."
    );
    assert_eq!(
        why(Some(47), "", &u, t, &found),
        "Max redirect count exceeded"
    );
    assert_eq!(why(Some(52), "", &u, t, &found), "socket hang up");
    assert_eq!(why(Some(56), "", &u, t, &found), "read ECONNRESET");
    assert_eq!(
        why(
            Some(35),
            "curl: (35) TLS connect error: x\nmore",
            &u,
            t,
            &found
        ),
        "TLS connect error: x"
    );
    assert_eq!(why(None, "killed", &u, t, &found), "killed");
    // the system's resolver, asked only of an address that needs no lookup
    assert_eq!(super::system_resolve("127.0.0.1", 80).unwrap(), "127.0.0.1");
    assert!(super::system_resolve("", 80).is_err());
}

#[test]
fn a_jar_line_and_back() {
    let c = json!({"name": "n", "value": "v", "domain": ".h.test", "path": "/", "expires": 2_000_000_000.5, "httpOnly": true, "secure": true});
    let line = jar_line(&c);
    assert_eq!(line, "#HttpOnly_.h.test\tTRUE\t/\tTRUE\t2000000000\tn\tv\n");
    let session =
        json!({"name": "s", "value": "", "domain": "h.test", "path": "/p", "expires": -1});
    assert_eq!(jar_line(&session), "h.test\tFALSE\t/p\tFALSE\t0\ts\t\n");
    let back = jar_cookies(&format!(
        "# Netscape\n\nshort\tline\n{line}{}",
        jar_line(&session)
    ));
    assert_eq!(back.len(), 2);
    assert_eq!(back[0]["httpOnly"], true);
    assert_eq!(back[0]["expires"], 2_000_000_000.0);
    assert_eq!(back[1]["expires"], -1.0);
    assert_eq!(back[1]["sameSite"], "Lax");
    assert_eq!(
        identity(&back[1]),
        ("h.test".to_owned(), "/p".to_owned(), "s".to_owned())
    );
}
