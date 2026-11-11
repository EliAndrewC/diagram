//! The parts a question bundle is built of beyond its pages (from `check_bundle.py`'s `entry_bundle`): each helper's output in the bundle's order, the quote-verbatim report and its residue pages, the registry entries the notes cite, the style guide, the variant index and the dispatcher's extra files.

use std::path::Path;

use super::check::{helper_part, parts, registry_entry, run_script, Entry, Rows, STYLE, VARIANTS};
use super::{copy, py_path, relative, shown, write, Run};
use crate::record::repo::Fail;

const PREPASS: &str = "for record-format: the WORDS TO RULE ON and the pattern candidates";
const STYLE_PREPASS: &str = "for record-style: the metric figures with no conversion (each a FAIL) and every lead line to rule on";
const TRANSLATIONS: &str =
    "for translation-check: each owed translated quotation, its translation and its original";

/// The quote-verbatim report, scoped where notes are named, and the residue pages; Some(exit) where it failed.
fn quote_part(
    run: &mut Run,
    root: &Path,
    e: &Entry<'_>,
    rows: &mut Rows,
    args: Vec<String>,
) -> Result<Option<i32>, Fail> {
    let (out, q) = (&e.out, e.q);
    let mut args = args;
    args.extend(["--json".to_owned(), shown(&out.join("quote-verbatim.json"))]);
    let (code, mut text) = run_script(run, "quote_verbatim", &args, root)?;
    if !e.notes.is_empty() && code == 0 {
        text = super::keys::scoped_verbatim(out, &text)?;
    }
    write(&out.join("quote-verbatim.txt"), &text)?;
    rows.push((
        "quote-verbatim.txt".to_owned(),
        format!("make quote-verbatim Q={q}"),
        "for quote-check: which quotations are on their pages, character for character".to_owned(),
    ));
    if code != 0 {
        run.warn(&text);
        return Ok(Some(code));
    }
    if super::keys::residue_pages(run, out)? > 0 {
        rows.push(("pages/".to_owned(), "the host's page cache (feature 288)".to_owned(), "for quote-check: the saved text of each page a quotation was not found VERBATIM on - grep it before any WebFetch; its MANIFEST.txt names a page the cache did not hold".to_owned()));
    }
    Ok(None)
}

/// The style guide, the variant index and the dispatcher's extra files.
fn copied_parts(root: &Path, e: &Entry<'_>, rows: &mut Rows) -> Result<(), Fail> {
    let (want, out) = (parts(e.for_), &e.out);
    if want.contains(&"style") {
        rows.push((copy(&root.join(STYLE), out, None)?, STYLE.to_owned(), "for record-style: the style guide - every rule you judge, with the GM's words it comes from".to_owned()));
    }
    if want.contains(&"variants") {
        rows.push((
            copy(&root.join(VARIANTS), out, None)?,
            VARIANTS.to_owned(),
            "the glossary's variant index: one line per defined word - grep it".to_owned(),
        ));
    }
    for path in e.extra {
        let src = if Path::new(path).is_absolute() {
            py_path(path)
        } else {
            root.join(py_path(path))
        };
        let name = format!(
            "extra/{}",
            src.file_name()
                .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
        );
        rows.push((
            copy(&src, out, Some(&name))?,
            path.clone(),
            "named by the dispatcher".to_owned(),
        ));
    }
    Ok(())
}

/// The registry entries the notes cite, in first-cited order (the `registry` part).
fn registry_part(root: &Path, out: &Path, rows: &mut Rows, keys: &[String]) -> Result<(), Fail> {
    let mut seen: Vec<&String> = Vec::new();
    for key in keys {
        if seen.contains(&key) {
            continue;
        }
        seen.push(key);
        if let Some(src) = registry_entry(root, key) {
            rows.push((
                copy(&src, out, Some(&format!("sources/{key}.html")))?,
                relative(&src, root),
                format!("the registry entry of `{key}`"),
            ));
        }
    }
    Ok(())
}

/// Every helper's part in the bundle's order; Some(exit) where one failed.
pub(crate) fn helper_parts(
    run: &mut Run,
    root: &Path,
    e: &Entry<'_>,
    rows: &mut Rows,
    keys: &[String],
) -> Result<Option<i32>, Fail> {
    let (want, q, out) = (parts(e.for_), e.q, e.out.clone());
    let base_args = vec![q.to_owned(), "--root".to_owned(), shown(root)];
    let late = [
        (
            "styleprepass",
            "style_prepass",
            base_args.clone(),
            (
                "style-prepass.txt",
                format!("make style-prepass Q={q}"),
                STYLE_PREPASS,
            ),
        ),
        (
            "translations",
            "translation_owed",
            vec![
                "--root".to_owned(),
                shown(root),
                "--q".to_owned(),
                q.to_owned(),
            ],
            (
                "translations.txt",
                format!("make translation-owed Q={q}"),
                TRANSLATIONS,
            ),
        ),
    ];
    let prepass = (
        "prepass",
        "record_prepass",
        base_args.clone(),
        ("prepass.txt", format!("make record-prepass Q={q}"), PREPASS),
    );
    for (i, (part, name, args, row)) in std::iter::once(prepass).chain(late).enumerate() {
        if i == 1 {
            if e.quotes && want.contains(&"quote") {
                if let Some(code) = quote_part(run, root, e, rows, base_args.clone())? {
                    return Ok(Some(code));
                }
            }
            if want.contains(&"registry") {
                registry_part(root, &out, rows, keys)?;
            }
        }
        if want.contains(&part) {
            if let Some(code) = helper_part(run, root, &out, rows, (name, args), row)? {
                return Ok(Some(code));
            }
        }
    }
    copied_parts(root, e, rows)?;
    Ok(None)
}
