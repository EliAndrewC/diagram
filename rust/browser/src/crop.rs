//! The glyph crop (feature 449 T146, `ask:449-phase4-slices` Q4; `scripts/record/glyph_crop.py`'s port, which `l7r-gate record
//! modal-bundle` ran by `python3 -c` for a modal-depiction bundle, `ask:449-T88-bundles` Q3): a pool page opened at 1200 x 900, the
//! kind's first glyph zoomed into with the page's own Ctrl+wheel until it is over 200 px, a clip around it saved as a PNG and every
//! kind with a part inside the clip listed beside it (`<out>.kinds`). The page's scripts below are the Python's, word for word, and
//! the steps, waits and protocol events are the ones Playwright sent for it (observed 2026-11-16 with `DEBUG=pw:protocol`), so the
//! crop's pixels are the Python's on the same Chromium.

use std::path::Path;
use std::thread::sleep;
use std::time::Duration;

use serde_json::{json, Value};

use crate::page::{Browser, Options};

/// The first leaf shape with a box on screen, not the class group: the group spans every instance on the map (a hamlet's gardens run
/// its whole width), so measuring it never zoomed - the garden's crop came out as the whole hamlet (feature 319, the garden pilot).
/// The group is the fallback.
const MEASURE: &str = "(s) => { const g = document.querySelector(s); if (!g) return null; const leaf = [...g.querySelectorAll('polygon,rect,path,ellipse,circle,line')].find(e => e.getBoundingClientRect().width > 0); const r = (leaf || g).getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }";
/// ...AND MEASURED WHILE SHOWN: below the raster scale the page hides every class group (0 x 0), so a measure there found nothing and
/// the zoom never centered on a glyph. The kind is shown for the measure alone and hidden again for the shot.
const SHOW: &str = "(s) => { const st = document.createElement('style'); st.id = 'crop-probe'; st.textContent = s + ', ' + s + ' * { display: inline !important; }'; document.head.appendChild(st); }";
const HIDE: &str =
    "() => { const st = document.getElementById('crop-probe'); if (st) st.remove(); }";
/// ...AND NEVER LIT: zoomed in, a large glyph (a Mode A kitchen, an archive) fills the viewport, so the corner the mouse leaves for is
/// ON it and the shot showed the page's highlight, not the drawn fill (feature 372 wave 105; fixed feature 374 wave 113, FR-007).
const UNLIGHT: &str =
    "() => document.querySelectorAll('g.f.on').forEach(g => g.classList.remove('on'))";
/// Every kind with a part inside the crop: a click on it opens that kind's pop-up (343's office-hall ruling - the check could not tell
/// whether the hall's front band opens office-hall or magistrate's dais).
const KINDS: &str = "(c) => { const st = document.createElement('style'); st.textContent = 'g.f, g.f * { display: inline !important; }'; document.head.appendChild(st); const out = new Set(); document.querySelectorAll('g.f[data-k]').forEach(g => { for (const e of g.querySelectorAll('polygon,rect,path,ellipse,circle,line')) { const r = e.getBoundingClientRect(); if (r.width > 0 && r.x < c.x + c.width && r.x + r.width > c.x && r.y < c.y + c.height && r.y + r.height > c.y) { out.add(g.dataset.k); break; } } }); st.remove(); return [...out]; }";

/// The viewport, as the Python opened it.
pub const WIDTH: f64 = 1200.0;
pub const HEIGHT: f64 = 900.0;

/// The page's options for a crop: Playwright's `new_page(viewport=...)` on a fresh context.
#[must_use]
pub fn options() -> Options {
    Options {
        width: 1200,
        height: 900,
        user_agent: None,
        ignore_https_errors: false,
    }
}

/// A wait of the Python's, in milliseconds (a hundredth of it in the tests, whose browser draws nothing).
#[cfg(not(test))]
fn ms(n: u64) -> Duration {
    Duration::from_millis(n)
}
#[cfg(test)]
fn ms(n: u64) -> Duration {
    Duration::from_millis(n / 100)
}

/// The kind's first glyph measured while shown: `[x, y, width, height]`.
fn rect(browser: &mut Browser, page: &crate::page::Page, sel: &Value) -> Result<[f64; 4], String> {
    browser.evaluate(page, SHOW, sel)?;
    let got = browser.evaluate(page, MEASURE, sel)?;
    browser.evaluate(page, HIDE, &Value::Null)?;
    let nums: Vec<f64> = got
        .as_array()
        .map(|a| a.iter().filter_map(Value::as_f64).collect())
        .unwrap_or_default();
    match nums.as_slice() {
        [x, y, w, h] => Ok([*x, *y, *w, *h]),
        // the Python unpacked the `None` a missing glyph gave and died there
        _ => Err(format!(
            "TypeError: cannot unpack non-iterable NoneType object (no glyph matches {sel})"
        )),
    }
}

/// The crop of `key`'s first glyph on `page_path` into `out` (a PNG) and `<out>.kinds`.
///
/// # Errors
/// The page would not load, the glyph is not on it, or the browser failed.
pub fn crop(b: &mut Browser, page_path: &Path, key: &str, out: &Path) -> Result<(), String> {
    let page = b.new_page()?;
    let done = crop_on(b, &page, page_path, key, out);
    b.close_page(&page);
    done
}

fn crop_on(
    browser: &mut Browser,
    page: &crate::page::Page,
    page_path: &Path,
    key: &str,
    out: &Path,
) -> Result<(), String> {
    browser.goto(
        page,
        &format!("file://{}", page_path.display()),
        Duration::from_secs(30),
    )?;
    sleep(ms(2500));
    let sel = json!(format!("g.f[data-k=\"{key}\"]"));
    for _ in 0..14 {
        let [x, y, w, h] = rect(browser, page, &sel)?;
        if w > 200.0 || h > 200.0 {
            break;
        }
        browser.mouse_move(page, x + w / 2.0, y + h / 2.0)?;
        browser.control_wheel(page, x + w / 2.0, y + h / 2.0, -240.0)?;
        sleep(ms(200));
    }
    let [x, y, w, h] = rect(browser, page, &sel)?;
    browser.mouse_move(page, 2.0, 2.0)?;
    sleep(ms(150)); // off the glyph, so it is not drawn lit
    browser.evaluate(page, UNLIGHT, &Value::Null)?;
    sleep(ms(100));
    let (cx, cy) = (x + w / 2.0, y + h / 2.0);
    let cw = WIDTH.min((w + 60.0).max(600.0));
    let ch = HEIGHT.min((h + 60.0).max(500.0));
    let clip = json!({"x": (cx - cw / 2.0).min(WIDTH - cw).max(0.0), "y": (cy - ch / 2.0).min(HEIGHT - ch).max(0.0),
                      "width": cw, "height": ch});
    let png = browser.screenshot(page, &clip)?;
    std::fs::write(out, png).map_err(|e| format!("{}: {e}", out.display()))?;
    let mut kinds: Vec<String> = browser
        .evaluate(page, KINDS, &clip)?
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(Value::as_str)
                .map(str::to_owned)
                .collect()
        })
        .unwrap_or_default();
    kinds.sort();
    let kinds_file = format!("{}.kinds", out.display());
    std::fs::write(&kinds_file, kinds.join("\n")).map_err(|e| format!("{kinds_file}: {e}"))
}

#[cfg(test)]
mod tests;
