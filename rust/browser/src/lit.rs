//! The page lit (feature 449 T150, the engine port's step 2; `l7r/diagram/tools/page_lit.py`'s browser half, which drove Playwright):
//! a map's page opened at 1400 x 1000, its raster awaited, zoomed past the raster switch with the page's own zoom key when asked, then
//! two screenshots - nothing lit, then the class lit - each after the browser has painted. The steps, scripts and waits are the
//! Python's, and the protocol commands Playwright sent for them (observed 2026-11-18 with `DEBUG=pw:protocol` on a pool sheet's page);
//! what the pixels mean is `l7r-mode-a page-lit`'s (`rust/mode_a/src/diagnostics/page_lit.rs`), which runs this as a program.
//!
//! Research: the lit page's browser half - NONE: a measurement's steps in the browser, no map decision

use std::path::Path;
use std::thread::sleep;
use std::time::Duration;

use serde_json::{json, Value};

use crate::page::{Browser, Options, Page};

/// The opening viewport: the browser tests' size, as the Python's `VIEWPORT`.
pub const WIDTH: u32 = 1400;
pub const HEIGHT: u32 = 1000;
/// How many presses of the zoom key `--vector` may take before giving up on reaching the vector page (the Python's `ZOOM_STEPS`).
pub const ZOOM_STEPS: usize = 24;

/// `page.wait_for_function(..., timeout=60000)`: polled on each animation frame in the page, as Playwright polls.
const READY: &str = "() => new Promise((r, j) => { const f = () => { try { if (window.l7rMap && window.l7rMap.rasterReady()) r(true); else requestAnimationFrame(f); } catch (e) { j(e); } }; f(); })";
const MODE: &str = "() => window.l7rMap.mode()";
const ZOOM: &str = "() => window.l7rMap.zoom()";
const CTM: &str = "() => { var m = document.getElementById('map').getScreenCTM(); return [m.a, m.b, m.c, m.d, m.e, m.f]; }";
const VIEWBOX: &str = "() => { var v = document.getElementById('map').getAttribute('viewBox'); return v ? v.trim().split(/[\\s,]+/).map(Number) : null; }";
const CLEAR: &str = "() => window.l7rMap.highlight(null)";
const LIGHT: &str = "k => window.l7rMap.highlight(k)";
/// Two animation frames: the browser telling us it painted, never a wall-clock wait (the Python's `_painted`: a fixed 300 ms gave a
/// before-shot of a map not yet drawn in one run and an after-shot the highlight had not reached in another).
const PAINTED: &str =
    "() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))";

/// The page's options for a lit measure: Playwright's `new_page(viewport=..., device_scale_factor=1)` on a fresh context.
#[must_use]
pub fn options() -> Options {
    Options {
        width: WIDTH,
        height: HEIGHT,
        user_agent: None,
        ignore_https_errors: false,
    }
}

/// What the page answered: its mode and zoom, the map's screen transform and viewBox, and the two screenshots (PNG).
#[derive(Debug)]
pub struct Lit {
    pub mode: Value,
    pub zoom: Value,
    pub ctm: Value,
    pub viewbox: Value,
    pub before: Vec<u8>,
    pub after: Vec<u8>,
}

/// The raster's wait, a minute as the Python's (`timeout=60000`), IN EVERY BUILD (451 T70): the wait is the page's own answer, so a
/// page that readies pays nothing for the ceiling. The test build's 40 ms failed the end-to-end test's real Chromium under load (1 of
/// 40 runs in the event log, under `make closing-checks`; 1 of 10 with 44 busy loops on 22 cpus), a ready page's answer that came late.
const READY_WAIT: Duration = Duration::from_secs(60);
/// The zoom key's settle (120 ms), as the Python's; the tests' fake browser answers at once.
#[cfg(not(test))]
const SETTLE: Duration = Duration::from_millis(120);
#[cfg(test)]
const SETTLE: Duration = Duration::from_millis(1);

#[cfg(not(test))]
fn ready_wait() -> Duration {
    READY_WAIT
}
#[cfg(test)]
fn ready_wait() -> Duration {
    READY_CEILING.get()
}

#[cfg(test)]
thread_local! {
    /// The test build's raster ceiling: the shipped minute, which the test of a page that never readies shortens on its own thread,
    /// so that refusal comes in 40 ms (451 T70).
    pub(crate) static READY_CEILING: std::cell::Cell<Duration> = const { std::cell::Cell::new(READY_WAIT) };
}

fn viewport() -> Value {
    json!({"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT})
}

/// `page_path` opened, `key` lit, and what changed photographed.
///
/// # Errors
/// The page would not load, its raster never readied, a script threw, or the browser failed.
pub fn lit(b: &mut Browser, page_path: &Path, key: &str, vector: bool) -> Result<Lit, String> {
    let page = b.new_page()?;
    let done = lit_on(b, &page, page_path, key, vector);
    b.close_page(&page);
    done
}

fn lit_on(
    b: &mut Browser,
    page: &Page,
    page_path: &Path,
    key: &str,
    vector: bool,
) -> Result<Lit, String> {
    b.goto(
        page,
        &format!("file://{}", page_path.display()),
        Duration::from_secs(30),
    )?;
    let ready_wait = ready_wait();
    b.evaluate_within(page, READY, &Value::Null, ready_wait)
        .map_err(|e| {
            if e.contains("no answer within") {
                format!(
                    "page.wait_for_function: Timeout {}ms exceeded.",
                    ready_wait.as_millis()
                )
            } else {
                e
            }
        })?;
    if vector {
        // THE PAGE'S OWN ZOOM KEY, NEVER THE WHEEL (feature 245): the page scrolls on a wheel turn by the GM's ruling (page.js `onWheel`,
        // 2026-08-28: "I don't want scrolling to zoom"), so the wheel never left raster mode on a real map
        let mut pressed = false;
        for _ in 0..ZOOM_STEPS {
            if b.evaluate(page, MODE, &Value::Null)? == json!("vector") {
                break;
            }
            b.control_equal(page)?;
            pressed = true;
            sleep(SETTLE);
        }
        // THE ZOOM'S HOVER LANDS BEFORE THE CLEAR (feature 449 T150): a zoom moves the map under the pointer, and the browser lights
        // what is now under it at the next frame it draws. With no frame drawn between the last press and the clear below, that hover
        // landed after the clear: on Ochiba's page lit by "inner court" the before-shot showed the family quarters lit and the measure
        // counted them as changed (2 of 2 runs after a 240 ms sleep, 1 of 3 with nothing; observed 2026-11-18, `data-hl` read before
        // the shot) where the Python's measure did not. Two frames drawn here first, the hover lands and the clear clears it (8 of 8).
        if pressed {
            b.evaluate(page, PAINTED, &Value::Null)?;
        }
    }
    let mode = b.evaluate(page, MODE, &Value::Null)?;
    let zoom = b.evaluate(page, ZOOM, &Value::Null)?;
    let ctm = b.evaluate(page, CTM, &Value::Null)?;
    let viewbox = b.evaluate(page, VIEWBOX, &Value::Null)?;
    // NOTHING IS LIT IN THE `before` SHOT: the pointer starts at (0, 0), on the map, and the page lights what lies there; the zoom moves
    // it too, so the clear comes last
    b.evaluate(page, CLEAR, &Value::Null)?;
    b.evaluate(page, PAINTED, &Value::Null)?;
    let before = b.screenshot(page, &viewport())?;
    b.evaluate(page, LIGHT, &json!(key))?;
    b.evaluate(page, PAINTED, &Value::Null)?;
    let after = b.screenshot(page, &viewport())?;
    Ok(Lit {
        mode,
        zoom,
        ctm,
        viewbox,
        before,
        after,
    })
}

#[cfg(test)]
mod tests;
