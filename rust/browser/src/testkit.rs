//! The tests' Chromium (feature 449 T146): a small Python program that speaks the protocol on fds 3 and 4 as Chromium does, answering
//! each command the crate sends from a table, so every path of the crate runs without a browser or a network. What a page does is read
//! from its URL: `neterr` fails the navigation, `samedoc` has no loader, `noload` never loads, `busy` never goes idle, `nobody` has no
//! body, `noglyph` has no glyph to measure, `throw` throws in the page, `big` measures large at once, `small` never grows.

use std::path::{Path, PathBuf};

const FAKE: &str = r#"#!/usr/bin/env python3
import base64, json, os, sys
inp = os.fdopen(3, "rb", buffering=0)
out = os.fdopen(4, "wb", buffering=0)
url = ""
cookies = []
measured = 0
def send(m):
    out.write(json.dumps(m).encode() + b"\0")
buf = b""
while True:
    chunk = inp.read(65536)
    if not chunk:
        break
    buf += chunk
    while b"\0" in buf:
        raw, _, buf = buf.partition(b"\0")
        m = json.loads(raw)
        i, meth, p, s = m["id"], m["method"], m.get("params", {}), m.get("sessionId")
        r = {}
        if meth == "Browser.getVersion":
            r = {"product": "FakeChrome/1", "userAgent": "FakeUA/1"}
        elif meth == "Target.createBrowserContext":
            r = {"browserContextId": "C1"}
        elif meth == "Target.createTarget":
            r = {"targetId": "T1"}
        elif meth == "Target.attachToTarget":
            r = {"sessionId": "S1"}
        elif meth == "Page.getFrameTree":
            r = {"frameTree": {"frame": {"id": "F1"}}}
        elif meth == "Browser.getWindowForTarget":
            r = {"windowId": 1}
        elif meth == "Page.navigate":
            url = p["url"]
            if "neterr" in url:
                r = {"frameId": "F1", "errorText": "net::ERR_ABORTED"}
            elif "samedoc" in url:
                r = {"frameId": "F1"}
            else:
                r = {"frameId": "F1", "loaderId": "L1"}
            send({"id": i, "result": r, "sessionId": s})
            send({"method": "Page.frameNavigated", "params": {}, "sessionId": s})
            send({"no": "method"})
            if "noload" not in url and "neterr" not in url and "samedoc" not in url:
                send({"method": "Page.lifecycleEvent", "params": {"frameId": "F1", "loaderId": "L0", "name": "load"}, "sessionId": s})
                send({"method": "Page.lifecycleEvent", "params": {"frameId": "F1", "loaderId": "L1", "name": "load"}, "sessionId": s})
                if "busy" not in url:
                    send({"method": "Page.lifecycleEvent", "params": {"frameId": "F1", "loaderId": "L1", "name": "networkIdle"}, "sessionId": s})
            continue
        elif meth == "Page.captureSnapshot":
            r = {"data": "MHTML of " + url}
        elif meth == "Runtime.evaluate":
            e = p["expression"]
            if "throw" in url and "document.body" in e:
                r = {"result": {"type": "object"}, "exceptionDetails": {"text": "Uncaught", "exception": {"description": "Error: thrown"}}}
            elif "throwplain" in e:
                r = {"result": {}, "exceptionDetails": {"text": "Uncaught plain"}}
            elif "throwbare" in e:
                r = {"result": {}, "exceptionDetails": {}}
            elif "document.body" in e:
                r = {"result": {"type": "string", "value": None if "nobody" in url else "the text of " + url}}
            elif "getBoundingClientRect().width > 0); const r" in e:
                measured += 1
                if "noglyph" in url:
                    r = {"result": {"value": None}}
                else:
                    w = 300 if "big" in url else 50 if "small" in url else 50 * measured
                    r = {"result": {"value": [10.5, 20, w, 40]}}
            elif "out.add(g.dataset.k)" in e:
                r = {"result": {"value": ["zeta", "alpha"]}}
            else:
                r = {"result": {"type": "undefined"}}
        elif meth == "Page.captureScreenshot":
            r = {"data": base64.b64encode(b"\x89PNG fake").decode()}
        elif meth == "Storage.getCookies":
            r = {"cookies": cookies}
        elif meth == "Storage.setCookies":
            for c in p["cookies"]:
                cookies[:] = [x for x in cookies if (x["domain"], x["path"], x["name"]) != (c["domain"], c["path"], c["name"])]
                if c.get("expires", -1) == -1 or c["expires"] > 1000:
                    cookies.append(c)
        elif meth == "Fail.me":
            send({"id": i, "error": {"message": "no such method"}})
            continue
        elif meth == "Silent.me":
            continue
        elif meth == "Browser.close":
            send({"id": i, "result": {}})
            sys.exit(0)
        send({"id": i, "result": r, **({"sessionId": s} if s else {})})
"#;

/// The fake browser written into `dir`, executable; its path.
#[must_use]
pub fn fake_chrome(dir: &Path) -> PathBuf {
    let at = dir.join("fake-chrome");
    executable(&at, FAKE);
    at
}

/// `text` written to `at` as a program by `install`, as the gate's `core::write_executable` writes one: a file this process wrote
/// itself stays open for writing in any child another test thread forks meanwhile, until that child's `exec`, and running it then can
/// fail with "Text file busy". The fake browser closed before its first answer once in 12 runs with the crates' tests side by side, the
/// shape that race leaves (feature 449 T160, observed 2026-11-17; the error itself was not seen).
pub fn executable(at: &Path, text: &str) {
    let draft = at.with_extension("draft");
    std::fs::write(&draft, text).unwrap();
    let done = std::process::Command::new("install")
        .args(["-m", "755"])
        .arg(&draft)
        .arg(at)
        .status();
    assert!(done.unwrap().success());
    std::fs::remove_file(&draft).unwrap();
}

/// A program at `dir/name` running `body` as a shell script.
#[must_use]
pub fn script(dir: &Path, name: &str, body: &str) -> PathBuf {
    let at = dir.join(name);
    executable(&at, &format!("#!/bin/sh\n{body}\n"));
    at
}

/// The environment a test hands the crate: `L7R_CHROMIUM` the fake, every other name empty.
pub fn var_for(exe: &Path) -> impl Fn(&str) -> String + '_ {
    move |k: &str| {
        (k == "L7R_CHROMIUM")
            .then(|| exe.to_string_lossy().into_owned())
            .unwrap_or_default()
    }
}
