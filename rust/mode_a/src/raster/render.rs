//! THE RENDERER AS A LIBRARY (feature 449 T150; FR-001's phase-4 paragraph, `ask:449-phase4-slices` Q7 as amended by
//! `ask:449-engine-order`): a document drawn by the `resvg` crate in process, pinned to the version of the binary the Python ran (0.46.0),
//! and each step of that binary's `main.rs` followed - the arguments the page hands it (`--zoom`, `--width`, `--shape-rendering`,
//! `--text-rendering`, `--serif-family`), its defaults (96 dpi, Times New Roman at 12, English, a 100 x 100 default size, its width when
//! one is given), the XML read with DTDs allowed, the system's fonts loaded with its family defaults and the serif family named, the
//! pixmap sized and scaled as its `FitTo` does, and the PNG written by tiny-skia's encoder as its `save_png` writes it. So with the same
//! fonts the PNG is the binary's (measured on the six pool pages and part A's cases, 2026-11-18: see the task's report).
//!
//! Research: the renderer - NONE: drawing a document as the binary drew it, no map decision

use std::sync::{Arc, LazyLock, Mutex, PoisonError};

use l7r_gate_research::Error;

/// How the pixmap is sized from the document's (the binary's `FitTo`): as it is, to a width, or by a factor.
#[derive(Debug, Clone, Copy, PartialEq)]
enum Fit {
    Original,
    Width(u32),
    Zoom(f32),
}

/// What a render was asked: the fit, the shape and text rendering, and the serif family.
#[derive(Debug, Clone, PartialEq)]
struct Asked {
    fit: Fit,
    shape: resvg::usvg::ShapeRendering,
    text: resvg::usvg::TextRendering,
    serif: String,
}

fn refused(what: &str) -> Error {
    Error::new("RuntimeError", format!("resvg: {what}"))
}

/// A library's own refusal, in its words.
fn said(e: &dyn std::fmt::Display) -> Error {
    refused(&e.to_string())
}

/// The arguments as the binary reads them, the ones the page and the diagnostics hand it; any other refused by name.
fn asked(args: &[String]) -> Result<Asked, Error> {
    let mut a = Asked {
        fit: Fit::Original,
        shape: resvg::usvg::ShapeRendering::default(),
        text: resvg::usvg::TextRendering::default(),
        serif: "Times New Roman".to_owned(),
    };
    let (mut width, mut zoom) = (None, None);
    let mut it = args.iter();
    while let Some(flag) = it.next() {
        let value = it
            .next()
            .ok_or_else(|| refused(&format!("{flag} wants a value")))?;
        let bad = || refused(&format!("{flag} {value:?}"));
        match flag.as_str() {
            "--width" | "-w" => {
                width = Some(
                    value
                        .parse::<u32>()
                        .ok()
                        .filter(|w| *w > 0)
                        .ok_or_else(bad)?,
                );
            }
            "--zoom" | "-z" => {
                zoom = Some(
                    value
                        .parse::<f32>()
                        .ok()
                        .filter(|z| *z > 0.0)
                        .ok_or_else(bad)?,
                );
            }
            "--shape-rendering" => a.shape = value.parse().map_err(|_| bad())?,
            "--text-rendering" => a.text = value.parse().map_err(|_| bad())?,
            "--serif-family" => value.clone_into(&mut a.serif),
            _ => return Err(refused(&format!("no argument {flag}"))),
        }
    }
    a.fit = match (width, zoom) {
        (Some(w), _) => Fit::Width(w),
        (None, Some(z)) => Fit::Zoom(z),
        (None, None) => Fit::Original,
    };
    Ok(a)
}

/// The system's fonts, loaded once a process for each serif family (the binary's `load_fonts`: its family defaults, the serif named).
/// A font database for each serif family asked.
type Fonts = Vec<(String, Arc<resvg::usvg::fontdb::Database>)>;

static FONTS: LazyLock<Mutex<Fonts>> = LazyLock::new(|| Mutex::new(Vec::new()));

fn fonts(serif: &str) -> Arc<resvg::usvg::fontdb::Database> {
    let mut held = FONTS.lock().unwrap_or_else(PoisonError::into_inner);
    if let Some((_, db)) = held.iter().find(|(s, _)| s == serif) {
        return Arc::clone(db);
    }
    let mut db = resvg::usvg::fontdb::Database::new();
    db.load_system_fonts();
    db.set_serif_family(serif);
    db.set_sans_serif_family("Arial");
    db.set_cursive_family("Comic Sans MS");
    db.set_fantasy_family("Impact");
    db.set_monospace_family("Courier New");
    let db = Arc::new(db);
    held.push((serif.to_owned(), Arc::clone(&db)));
    db
}

/// `doc` drawn with `args` as the `resvg` binary of the same version draws it, as PNG bytes.
///
/// # Errors
/// An argument the binary would refuse, a document it cannot read, a size it cannot make, or the PNG's encoding.
pub fn png(doc: &str, args: &[String]) -> Result<Vec<u8>, Error> {
    let a = asked(args)?;
    let mut opt = resvg::usvg::Options {
        shape_rendering: a.shape,
        text_rendering: a.text,
        fontdb: fonts(&a.serif),
        ..resvg::usvg::Options::default()
    };
    if let Fit::Width(w) = a.fit {
        #[expect(clippy::cast_precision_loss, reason = "the binary's own `w as f32`")]
        let w = w as f32;
        opt.default_size = resvg::usvg::Size::from_wh(w, 100.0).unwrap_or(opt.default_size);
    }
    let xml = resvg::usvg::roxmltree::ParsingOptions {
        allow_dtd: true,
        ..Default::default()
    };
    let parsed =
        resvg::usvg::roxmltree::Document::parse_with_options(doc, xml).map_err(|e| said(&e))?;
    let tree = resvg::usvg::Tree::from_xmltree(&parsed, &opt).map_err(|e| said(&e))?;
    let size = tree.size().to_int_size();
    let target = match a.fit {
        Fit::Original => Some(size),
        Fit::Width(w) => size.scale_to_width(w),
        Fit::Zoom(z) => size.scale_by(z),
    }
    .ok_or_else(|| refused("target size is zero"))?;
    let mut pixmap = resvg::tiny_skia::Pixmap::new(target.width(), target.height())
        .ok_or_else(|| refused("cannot create pixmap"))?;
    let (from, to) = (size.to_size(), target.to_size());
    let ts = resvg::tiny_skia::Transform::from_scale(
        to.width() / from.width(),
        to.height() / from.height(),
    );
    resvg::render(&tree, ts, &mut pixmap.as_mut());
    // tiny-skia's encoder fails only on a pixmap it made itself; were it to, the empty bytes are refused where the PNG is read ("a tile
    // is no PNG"), so the failure still surfaces
    Ok(pixmap.encode_png().unwrap_or_default())
}

#[cfg(test)]
mod tests {
    use super::{asked, png, Fit};

    fn words(w: &[&str]) -> Vec<String> {
        w.iter().map(|s| (*s).to_owned()).collect()
    }

    #[test]
    fn the_arguments_are_the_binary_s() {
        let a = asked(&words(&[
            "--zoom",
            "2",
            "--serif-family",
            "DejaVu Serif",
            "--shape-rendering",
            "crispEdges",
        ]))
        .unwrap();
        assert_eq!((a.fit, a.serif.as_str()), (Fit::Zoom(2.0), "DejaVu Serif"));
        assert_eq!(
            asked(&words(&["-w", "30", "-z", "2"])).unwrap().fit,
            Fit::Width(30)
        );
        assert_eq!(asked(&[]).unwrap().fit, Fit::Original);
        assert!(asked(&words(&["--text-rendering", "optimizeSpeed"])).is_ok());
        for bad in [
            &["--zoom"][..],
            &["--zoom", "0"],
            &["--width", "x"],
            &["--dpi", "3"],
            &["--shape-rendering", "x"],
            &["--text-rendering", "x"],
        ] {
            assert_eq!(asked(&words(bad)).unwrap_err().kind, "RuntimeError");
        }
    }

    #[test]
    fn a_document_is_drawn_as_a_png() {
        let doc = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"4\" height=\"2\"><rect width=\"4\" height=\"2\" fill=\"#f00\"/></svg>";
        let out = png(doc, &words(&["--zoom", "2"])).unwrap();
        assert_eq!(&out[..8], b"\x89PNG\r\n\x1a\n");
        assert_eq!(crate::raster::encode::png_size(&out).unwrap(), (8, 4));
        assert_eq!(
            crate::raster::encode::png_size(&png(doc, &words(&["--width", "2"])).unwrap()).unwrap(),
            (2, 1)
        );
        assert_eq!(
            crate::raster::encode::png_size(&png(doc, &[]).unwrap()).unwrap(),
            (4, 2)
        );
        assert!(png("<svg", &[]).is_err());
        // a zoom that leaves no pixel
        assert!(png(doc, &words(&["--zoom", "0.0001"])).is_err());
        assert!(png("<html/>", &[]).is_err());
        // a pixmap too wide for tiny-skia (past i32::MAX / 4)
        let huge = doc.replace("width=\"4\"", "width=\"999999999\"");
        assert!(png(&huge, &[]).is_err());
    }
}
