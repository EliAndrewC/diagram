//! The tests' Chromium in Rust (feature 449 T273, where a Python program stood since T146): this test binary started again with
//! [`MARKER`] set and run as [`ENTRY`] alone, reading the protocol on fd 3 and answering on fd 4 as Chromium does, each command from
//! the table below, so every path of the crate runs without a browser, a network or a Python interpreter. Its stdout and stderr are
//! the launch's `/dev/null`, so the test harness's own lines go nowhere. What a page does is read from its URL: `neterr` fails the
//! navigation, `samedoc` has no loader, `noload` never loads, `busy` never goes idle, `nobody` has no body, `noglyph` has no glyph to
//! measure, `throw` throws in the page, `big` measures large at once, `small` never grows; and (feature 449 T150, the lit page)
//! `notready` never readies its raster, `readythrow` throws asking, `zoomy` reaches vector mode at the second press of the zoom key,
//! `stuck` never does, `novb` has no viewBox; and (451 T70) `lateready` readies its raster 50 ms after it is asked, past the 40 ms the
//! test build once gave a real Chromium that missed it under load.

use std::io::{Read, Write};

use serde_json::{json, Value};

/// Set in the started copy's environment: the copy is the fake.
pub const MARKER: &str = "L7R_TEST_FAKE_CHROMIUM";

/// The test the started copy runs, by its path in this crate's test binary.
pub const ENTRY: &str = "testkit::fake::the_fake_chromium";

/// The fake's whole run: nothing in a plain test run, the browser in the copy [`super::fake_chrome`] starts.
#[test]
fn the_fake_chromium() {
    if std::env::var_os(MARKER).is_none() {
        return;
    }
    let mut inp = std::fs::File::open("/dev/fd/3").unwrap();
    let mut out = std::fs::OpenOptions::new()
        .write(true)
        .open("/dev/fd/4")
        .unwrap();
    let mut fake = Fake::default();
    let mut buf: Vec<u8> = Vec::new();
    let mut chunk = vec![0u8; 65536];
    while let Ok(n @ 1..) = inp.read(&mut chunk) {
        buf.extend_from_slice(&chunk[..n]);
        while let Some(at) = buf.iter().position(|b| *b == 0) {
            let raw: Vec<u8> = buf.drain(..=at).collect();
            let m: Value = serde_json::from_slice(&raw[..at]).unwrap();
            let mut send = |v: Value| {
                let mut bytes = v.to_string().into_bytes();
                bytes.push(0);
                let _ = out.write_all(&bytes);
            };
            if fake.answer(&m, &mut send) {
                std::process::exit(0);
            }
        }
    }
}

/// What the fake remembers across commands: the page's URL, the cookie jar, how often a glyph was measured and the zoom key pressed.
#[derive(Default)]
struct Fake {
    url: String,
    cookies: Vec<Value>,
    measured: i64,
    presses: u32,
}

impl Fake {
    /// Answers one command through `send`; true once the browser is to exit.
    fn answer(&mut self, command: &Value, send: &mut dyn FnMut(Value)) -> bool {
        let id = command["id"].clone();
        let meth = command["method"].as_str().unwrap_or_default();
        let params = command["params"].clone();
        let session = command.get("sessionId").cloned().unwrap_or(Value::Null);
        let result = match meth {
            "Browser.getVersion" => json!({"product": "FakeChrome/1", "userAgent": "FakeUA/1"}),
            "Target.createBrowserContext" => json!({"browserContextId": "C1"}),
            "Target.createTarget" => json!({"targetId": "T1"}),
            "Target.attachToTarget" => json!({"sessionId": "S1"}),
            "Page.getFrameTree" => json!({"frameTree": {"frame": {"id": "F1"}}}),
            "Browser.getWindowForTarget" => json!({"windowId": 1}),
            "Page.navigate" => {
                self.navigate(&id, &params, &session, send);
                return false;
            }
            "Page.captureSnapshot" => json!({"data": format!("MHTML of {}", self.url)}),
            "Runtime.evaluate" => {
                let Some(got) = self.evaluate(params["expression"].as_str().unwrap_or_default())
                else {
                    return false;
                };
                got
            }
            "Input.dispatchKeyEvent" => {
                if params["key"] == "=" && params["type"] == "rawKeyDown" {
                    self.presses += 1;
                }
                json!({})
            }
            // base64 of the bytes `\x89PNG fake`
            "Page.captureScreenshot" => json!({"data": "iVBORyBmYWtl"}),
            "Storage.getCookies" => json!({"cookies": self.cookies}),
            "Storage.setCookies" => {
                self.set_cookies(&params);
                json!({})
            }
            "Fail.me" => {
                send(json!({"id": id, "error": {"message": "no such method"}}));
                return false;
            }
            "Silent.me" => return false,
            "Browser.close" => {
                send(json!({"id": id, "result": {}}));
                return true;
            }
            _ => json!({}),
        };
        let mut reply = json!({"id": id, "result": result});
        if !session.is_null() {
            reply["sessionId"] = session;
        }
        send(reply);
        false
    }

    /// A navigation: its reply, then the frame's event, a message with no method, and the loads and idle the URL allows.
    fn navigate(
        &mut self,
        id: &Value,
        params: &Value,
        session: &Value,
        send: &mut dyn FnMut(Value),
    ) {
        self.url = params["url"].as_str().unwrap_or_default().to_owned();
        let url = self.url.as_str();
        let result = if url.contains("neterr") {
            json!({"frameId": "F1", "errorText": "net::ERR_ABORTED"})
        } else if url.contains("samedoc") {
            json!({"frameId": "F1"})
        } else {
            json!({"frameId": "F1", "loaderId": "L1"})
        };
        send(json!({"id": id, "result": result, "sessionId": session}));
        send(json!({"method": "Page.frameNavigated", "params": {}, "sessionId": session}));
        send(json!({"no": "method"}));
        if ["noload", "neterr", "samedoc"]
            .iter()
            .any(|k| url.contains(k))
        {
            return;
        }
        let idle = !url.contains("busy");
        for (loader, name, sent) in [
            ("L0", "load", true),
            ("L1", "load", true),
            ("L1", "networkIdle", idle),
        ] {
            if sent {
                let params = json!({"frameId": "F1", "loaderId": loader, "name": name});
                send(
                    json!({"method": "Page.lifecycleEvent", "params": params, "sessionId": session}),
                );
            }
        }
    }

    /// A page script's result by what it asks and the page's URL; none where the page never answers.
    fn evaluate(&mut self, e: &str) -> Option<Value> {
        let url = self.url.as_str();
        let raster = e.contains("rasterReady");
        if raster && url.contains("notready") {
            return None;
        }
        if raster && url.contains("lateready") {
            std::thread::sleep(std::time::Duration::from_millis(50));
        }
        Some(if raster && url.contains("readythrow") {
            thrown("Uncaught", Some("TypeError: no raster"), &json!({}))
        } else if raster {
            json!({"result": {"type": "boolean", "value": true}})
        } else if e.contains("l7rMap.mode()") {
            let vector = !url.contains("stuck") && (!url.contains("zoomy") || self.presses >= 2);
            json!({"result": {"value": if vector { "vector" } else { "raster" }}})
        } else if e.contains("l7rMap.zoom()") {
            json!({"result": {"value": 1.5}})
        } else if e.contains("getScreenCTM") {
            json!({"result": {"value": [2, 0, 0, 2, 10.5, -4]}})
        } else if e.contains("getAttribute('viewBox')") {
            let viewbox = (!url.contains("novb")).then(|| json!([0, 0, 10, 10]));
            json!({"result": {"value": viewbox}})
        } else if url.contains("throw") && e.contains("document.body") {
            thrown(
                "Uncaught",
                Some("Error: thrown"),
                &json!({"type": "object"}),
            )
        } else if e.contains("throwplain") {
            thrown("Uncaught plain", None, &json!({}))
        } else if e.contains("throwbare") {
            json!({"result": {}, "exceptionDetails": {}})
        } else if e.contains("document.body") {
            let text = (!url.contains("nobody")).then(|| format!("the text of {url}"));
            json!({"result": {"type": "string", "value": text}})
        } else if e.contains("getBoundingClientRect().width > 0); const r") {
            self.measured += 1;
            self.glyph()
        } else if e.contains("out.add(g.dataset.k)") {
            json!({"result": {"value": ["zeta", "alpha"]}})
        } else {
            json!({"result": {"type": "undefined"}})
        })
    }

    /// The glyph's box: none on `noglyph`, wide at once on `big`, never growing on `small`, else wider at each measure.
    fn glyph(&self) -> Value {
        let url = self.url.as_str();
        if url.contains("noglyph") {
            return json!({"result": {"value": null}});
        }
        let w = if url.contains("big") {
            300
        } else if url.contains("small") {
            50
        } else {
            50 * self.measured
        };
        json!({"result": {"value": [10.5, 20, w, 40]}})
    }

    /// Each cookie set replaces the jar's of its domain, path and name, and stays only while it has not expired.
    fn set_cookies(&mut self, p: &Value) {
        let key = |c: &Value| (c["domain"].clone(), c["path"].clone(), c["name"].clone());
        for c in p["cookies"].as_array().into_iter().flatten() {
            self.cookies.retain(|x| key(x) != key(c));
            let expires = c.get("expires").and_then(Value::as_f64).unwrap_or(-1.0);
            if (expires + 1.0).abs() < f64::EPSILON || expires > 1000.0 {
                self.cookies.push(c.clone());
            }
        }
    }
}

/// A script's reply that threw: `result` beside the exception's text and, where it has one, its description.
fn thrown(text: &str, description: Option<&str>, result: &Value) -> Value {
    let mut details = json!({ "text": text });
    if let Some(d) = description {
        details["exception"] = json!({ "description": d });
    }
    json!({"result": result, "exceptionDetails": details})
}
