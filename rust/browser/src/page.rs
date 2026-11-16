//! A browser context and its pages, set up as Playwright set them up (feature 449 T146): the same protocol commands in the same order
//! for a new page - the window and its metrics, the user agent and its metadata, the font families, the emulated media - read off
//! Playwright's own protocol log for `archive.py`'s render and `glyph_crop.py`'s crop (observed 2026-11-16 with `DEBUG=pw:protocol`),
//! so a page lays out and draws as it did. What Playwright did only for its own bookkeeping (its utility world, the network domain it
//! tracked requests by, its download folder) is not done.

use std::time::{Duration, Instant};

use serde_json::{json, Value};

use crate::chromium::Launched;

/// How a context's pages are made (Playwright's `new_context` and `new_page` options this repository passes).
#[derive(Debug, Clone)]
pub struct Options {
    pub width: u32,
    pub height: u32,
    pub user_agent: Option<String>,
    pub ignore_https_errors: bool,
}

/// A page of the context: its target, its protocol session and its main frame.
#[derive(Debug, Clone)]
pub struct Page {
    pub target: String,
    pub session: String,
    pub frame: String,
}

/// The browser, one context in it.
pub struct Browser {
    pub launched: Launched,
    pub context: String,
    pub options: Options,
}

fn text_of(v: &Value, key: &str) -> String {
    v.get(key)
        .and_then(Value::as_str)
        .unwrap_or_default()
        .to_owned()
}

impl Browser {
    /// Starts the browser and makes its context, downloads refused (a page that turns out to be a download fails to render, as it
    /// failed under Playwright, and no file lands anywhere).
    ///
    /// # Errors
    /// The browser cannot start or answer.
    pub fn open(var: &dyn Fn(&str) -> String, options: Options) -> Result<Self, String> {
        let mut launched = Launched::start(var)?;
        let made = launched.cdp.call(
            "Target.createBrowserContext",
            json!({"disposeOnDetach": true}),
            None,
        )?;
        let context = text_of(&made, "browserContextId");
        launched.cdp.call(
            "Browser.setDownloadBehavior",
            json!({"behavior": "deny", "browserContextId": context}),
            None,
        )?;
        Ok(Self {
            launched,
            context,
            options,
        })
    }

    fn page_call(&mut self, page: &Page, method: &str, params: Value) -> Result<Value, String> {
        self.launched.cdp.call(method, params, Some(&page.session))
    }

    /// A new blank page, its emulation set as Playwright set it.
    ///
    /// # Errors
    /// A protocol command failed.
    pub fn new_page(&mut self) -> Result<Page, String> {
        let cdp = &mut self.launched.cdp;
        let made = cdp.call(
            "Target.createTarget",
            json!({"url": "about:blank", "browserContextId": self.context}),
            None,
        )?;
        let target = text_of(&made, "targetId");
        let attached = cdp.call(
            "Target.attachToTarget",
            json!({"targetId": target, "flatten": true}),
            None,
        )?;
        let session = text_of(&attached, "sessionId");
        let s = Some(session.as_str());
        cdp.call("Page.enable", json!({}), s)?;
        let tree = cdp.call("Page.getFrameTree", json!({}), s)?;
        let frame = tree
            .pointer("/frameTree/frame/id")
            .and_then(Value::as_str)
            .unwrap_or_default()
            .to_owned();
        cdp.call(
            "Page.setLifecycleEventsEnabled",
            json!({"enabled": true}),
            s,
        )?;
        cdp.call("Runtime.enable", json!({}), s)?;
        cdp.call(
            "Emulation.setFocusEmulationEnabled",
            json!({"enabled": true}),
            s,
        )?;
        if self.options.ignore_https_errors {
            cdp.call(
                "Security.setIgnoreCertificateErrors",
                json!({"ignore": true}),
                s,
            )?;
        }
        let (w, h) = (self.options.width, self.options.height);
        let window = cdp.call(
            "Browser.getWindowForTarget",
            json!({"targetId": target}),
            None,
        )?;
        cdp.call(
            "Browser.setWindowBounds",
            json!({"windowId": window.get("windowId").cloned().unwrap_or(Value::Null),
                   "bounds": {"width": w, "height": h}}),
            None,
        )?;
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            json!({"mobile": false, "width": w, "height": h, "screenWidth": w, "screenHeight": h, "deviceScaleFactor": 1,
                   "screenOrientation": {"angle": 0, "type": "landscapePrimary"}}),
            s,
        )?;
        if let Some(ua) = &self.options.user_agent {
            cdp.call(
                "Emulation.setUserAgentOverride",
                json!({"userAgent": ua, "userAgentMetadata": {"mobile": false, "model": "", "architecture": "x86",
                       "platform": "Linux", "platformVersion": ""}}),
                s,
            )?;
        }
        cdp.call(
            "Page.setFontFamilies",
            json!({"fontFamilies": {"standard": "Times New Roman", "fixed": "Monospace", "serif": "Times New Roman",
                   "sansSerif": "Arial", "cursive": "Comic Sans MS", "fantasy": "Impact"}}),
            s,
        )?;
        cdp.call(
            "Emulation.setEmulatedMedia",
            json!({"media": "", "features": [{"name": "prefers-color-scheme", "value": "light"},
                   {"name": "prefers-reduced-motion", "value": "no-preference"}, {"name": "forced-colors", "value": "none"},
                   {"name": "prefers-contrast", "value": "no-preference"}]}),
            s,
        )?;
        Ok(Page {
            target,
            session,
            frame,
        })
    }

    /// `page.goto(url, wait_until="load", timeout=...)`: the navigation, then its document's load event. Returns the navigation's
    /// loader, which [`Browser::wait_idle`] waits on.
    ///
    /// # Errors
    /// Playwright's words: the network error the navigation met (`page.goto: net::ERR_... at <url>`), or the timeout.
    pub fn goto(&mut self, page: &Page, url: &str, timeout: Duration) -> Result<String, String> {
        let deadline = Instant::now() + timeout;
        let went = self.page_call(
            page,
            "Page.navigate",
            json!({"url": url, "frameId": page.frame, "referrerPolicy": "unsafeUrl"}),
        )?;
        let error = text_of(&went, "errorText");
        if !error.is_empty() {
            return Err(format!("page.goto: {error} at {url}"));
        }
        let loader = text_of(&went, "loaderId");
        if loader.is_empty() {
            return Ok(loader);
        }
        let (frame, session) = (page.frame.clone(), page.session.clone());
        let load_event = self.launched.cdp.wait_event(deadline, |e| {
            lifecycle(e, &session, &frame, &loader, "load")
        });
        if load_event.is_none() {
            return Err(format!(
                "page.goto: Timeout {}ms exceeded.",
                timeout.as_millis()
            ));
        }
        Ok(loader)
    }

    /// `page.wait_for_load_state("networkidle", timeout=...)`: true once the document's network has been idle (Chromium's own
    /// `networkIdle`: no request for 500 ms), false at the timeout.
    pub fn wait_idle(&mut self, page: &Page, loader: &str, timeout: Duration) -> bool {
        let (frame, session) = (page.frame.clone(), page.session.clone());
        self.launched
            .cdp
            .wait_event(Instant::now() + timeout, |e| {
                lifecycle(e, &session, &frame, loader, "networkIdle")
            })
            .is_some()
    }

    /// The page saved whole as MHTML (`Page.captureSnapshot`, as `archive.py` asked it through a CDP session).
    ///
    /// # Errors
    /// The protocol's.
    pub fn mhtml(&mut self, page: &Page) -> Result<String, String> {
        let got = self.page_call(page, "Page.captureSnapshot", json!({"format": "mhtml"}))?;
        Ok(text_of(&got, "data"))
    }

    /// `page.evaluate(function, arg)`: `function` (a JavaScript function's source) called with `arg`, its promise awaited, its value
    /// returned by value.
    ///
    /// # Errors
    /// The page's exception, or the protocol's.
    pub fn evaluate(&mut self, page: &Page, function: &str, arg: &Value) -> Result<Value, String> {
        let got = self.page_call(
            page,
            "Runtime.evaluate",
            json!({"expression": format!("({function})({arg})"), "returnByValue": true, "awaitPromise": true,
                   "userGesture": true}),
        )?;
        if let Some(ex) = got.get("exceptionDetails") {
            let said = ex
                .pointer("/exception/description")
                .and_then(Value::as_str)
                .unwrap_or_else(|| ex.get("text").and_then(Value::as_str).unwrap_or("error"));
            return Err(format!("page.evaluate: {said}"));
        }
        Ok(got.pointer("/result/value").cloned().unwrap_or(Value::Null))
    }

    /// `page.inner_text("body")`: the body's rendered text, once there is a body (Playwright waited up to its 30-second default).
    ///
    /// # Errors
    /// No body within the wait, or the protocol's.
    pub fn body_text(&mut self, page: &Page, wait: Duration) -> Result<String, String> {
        let deadline = Instant::now() + wait;
        loop {
            let got = self.evaluate(
                page,
                "() => document.body ? document.body.innerText : null",
                &Value::Null,
            )?;
            if let Some(text) = got.as_str() {
                return Ok(text.to_owned());
            }
            if Instant::now() >= deadline {
                return Err(format!(
                    "locator.innerText: Timeout {}ms exceeded.",
                    wait.as_millis()
                ));
            }
            std::thread::sleep(Duration::from_millis(100));
        }
    }

    /// `page.mouse.move(x, y)`, no modifier held (as Playwright sent it).
    ///
    /// # Errors
    /// The protocol's.
    pub fn mouse_move(&mut self, page: &Page, x: f64, y: f64) -> Result<(), String> {
        self.page_call(
            page,
            "Input.dispatchMouseEvent",
            json!({"type": "mouseMoved", "button": "none", "buttons": 0, "x": x, "y": y, "modifiers": 0, "force": 0}),
        )
        .map(drop)
    }

    /// `keyboard.down("Control")`, `mouse.wheel(0, dy)` at (x, y), `keyboard.up("Control")`: the events Playwright sent for them.
    ///
    /// # Errors
    /// The protocol's.
    pub fn control_wheel(&mut self, page: &Page, x: f64, y: f64, dy: f64) -> Result<(), String> {
        self.page_call(
            page,
            "Input.dispatchKeyEvent",
            json!({"type": "rawKeyDown", "modifiers": 2, "windowsVirtualKeyCode": 17, "code": "ControlLeft", "commands": [],
                   "key": "Control", "text": "", "unmodifiedText": "", "autoRepeat": false, "location": 1, "isKeypad": false}),
        )?;
        self.page_call(
            page,
            "Input.dispatchMouseEvent",
            json!({"type": "mouseWheel", "x": x, "y": y, "modifiers": 2, "deltaX": 0, "deltaY": dy}),
        )?;
        self.page_call(
            page,
            "Input.dispatchKeyEvent",
            json!({"type": "keyUp", "modifiers": 0, "key": "Control", "windowsVirtualKeyCode": 17, "code": "ControlLeft",
                   "location": 1}),
        )
        .map(drop)
    }

    /// `page.screenshot(clip=...)`: the PNG Chromium encodes for the clip, after the page's fonts are ready (as Playwright waited).
    ///
    /// # Errors
    /// The protocol's, or a reply that is not base64.
    pub fn screenshot(&mut self, page: &Page, clip: &Value) -> Result<Vec<u8>, String> {
        self.evaluate(
            page,
            "() => document.fonts.ready.then(() => null)",
            &Value::Null,
        )?;
        let mut clip = clip.clone();
        clip["scale"] = json!(1);
        let got = self.page_call(
            page,
            "Page.captureScreenshot",
            json!({"format": "png", "clip": clip, "captureBeyondViewport": false}),
        )?;
        crate::base64::decode(&text_of(&got, "data"))
    }

    /// The context's cookies (`Storage.getCookies`).
    ///
    /// # Errors
    /// The protocol's.
    pub fn cookies(&mut self) -> Result<Vec<Value>, String> {
        let got = self.launched.cdp.call(
            "Storage.getCookies",
            json!({"browserContextId": self.context}),
            None,
        )?;
        Ok(got
            .get("cookies")
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default())
    }

    /// Cookies stored in the context (`Storage.setCookies`), as Playwright stored a response's.
    ///
    /// # Errors
    /// The protocol's.
    pub fn set_cookies(&mut self, cookies: &[Value]) -> Result<(), String> {
        if cookies.is_empty() {
            return Ok(());
        }
        self.launched
            .cdp
            .call(
                "Storage.setCookies",
                json!({"cookies": cookies, "browserContextId": self.context}),
                None,
            )
            .map(drop)
    }

    /// `page.close()`.
    pub fn close_page(&mut self, page: &Page) {
        let _ =
            self.launched
                .cdp
                .call("Target.closeTarget", json!({"targetId": page.target}), None);
    }
}

/// Whether `e` is the lifecycle event `name` of the page's frame and loader.
fn lifecycle(e: &Value, session: &str, frame: &str, loader: &str, name: &str) -> bool {
    e.get("method").and_then(Value::as_str) == Some("Page.lifecycleEvent")
        && e.get("sessionId").and_then(Value::as_str) == Some(session)
        && e.pointer("/params/frameId").and_then(Value::as_str) == Some(frame)
        && e.pointer("/params/loaderId").and_then(Value::as_str) == Some(loader)
        && e.pointer("/params/name").and_then(Value::as_str) == Some(name)
}

#[cfg(test)]
mod tests;
