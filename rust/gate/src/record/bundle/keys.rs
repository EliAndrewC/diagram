//! A source's bundles, the intro-check bundle and the parts a question bundle borrows (from `check_bundle.py`): a key's registry entry and its saved page (feature 250 D19), several keys for source-applicability (feature 312), the intro-check batch (feature 311 D4), the residue pages and the scoped quotation report (feature 288), the page images (feature 395) and what changed since a source-reader's last round.

use std::collections::{BTreeMap, HashSet};
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_guard::shared::checks::{load, state_path};
use l7r_guard::shared::pyjson;
use serde_json::{json, Value};

use super::check::{
    dumps, excerpt, flat, fresh, manifest, notes_subset, registry_entry, report_lines, untagged,
    url_of, with_earlier,
};
use super::earlier::dispatches;
use super::owed::{self as bo};
use super::{
    copy, default_root, head, py_path, py_str, relative, shown, slug, write, Run, MANIFEST,
};
use crate::difflib::unified_diff;
use crate::record::leaves::fragments_for;
use crate::record::owed::units as owed_units;
use crate::record::py_lines;
use crate::record::repo::{fail, git_out, read_text, Fail};
use crate::record::units::{re, read_notes, Unit, QUESTIONS};

type Rows = Vec<(String, String, String)>;

/// What a `source_pages.py` run printed before its manifest: the page's earlier reads on the ledger (feature 288).
fn ledger_part(saved: &str) -> &str {
    saved
        .split_once("pointer | file | state")
        .map_or(saved, |p| p.0)
        .trim_matches('\n')
}

/// Every passage the record quotes from `key` - the ORIGINAL where a quote is translated - across every notes file.
fn quoted_passages(run: &mut Run, root: &Path, key: &str) -> Result<Vec<String>, Fail> {
    let li = re(&format!(
        r#"(?s)<li data-note="{}(?:-\d+)?">(.*?)</li>"#,
        fancy_regex::escape(key)
    ));
    let comment = re(r"(?s)<!--.*?-->");
    let mut files: Vec<PathBuf> = Vec::new();
    walk(&root.join("research"), &mut files);
    files.retain(|p| {
        p.file_name()
            .is_some_and(|n| n.to_string_lossy().ends_with(".notes.html"))
    });
    super::sort_paths(&mut files);
    let mut out: Vec<String> = Vec::new();
    for notes in files {
        let text = read_text(&notes)?;
        for c in li.captures_iter(&text).flatten() {
            let body = comment
                .replace_all(c.get(1).map_or("", |g| g.as_str()), "")
                .into_owned();
            let got = run.door.ask("passages", &json!([body]))?;
            for p in got.as_array().into_iter().flatten() {
                let text = |k: &str| {
                    p.get(k)
                        .and_then(Value::as_str)
                        .unwrap_or_default()
                        .to_owned()
                };
                let original = text("original");
                out.push(if original.is_empty() {
                    text("quote")
                } else {
                    original
                });
            }
        }
    }
    let mut seen: Vec<String> = Vec::new();
    for q in out {
        if !seen.contains(&q)
            && !q.starts_with("http://")
            && !q.starts_with("https://")
            && q.chars().count() >= 20
        {
            seen.push(q);
        }
    }
    Ok(seen)
}

/// Every file under `dir`, recursively (`rglob("*")`'s files).
fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
    for e in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let p = e.path();
        if p.is_dir() {
            walk(&p, out);
        } else {
            out.push(p);
        }
    }
}

/// The cached text of every page a quotation was not found VERBATIM on, saved under `out/pages/` from the host's page cache only (feature 288 FR-010, FR-011); the count of pages named.
pub(crate) fn residue_pages(run: &mut Run, out: &Path) -> Result<usize, Fail> {
    let report = out.join("quote-verbatim.json");
    let data: Value = if report.is_file() {
        serde_json::from_str(&read_text(&report)?).map_err(fail)?
    } else {
        json!({})
    };
    let mut urls: Vec<String> = Vec::new();
    for e in data
        .get("footnotes")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
    {
        let residue = e
            .get("passages")
            .and_then(Value::as_array)
            .is_some_and(|ps| {
                ps.iter()
                    .any(|p| p.get("quotation").and_then(Value::as_str) != Some("VERBATIM"))
            });
        if !residue {
            continue;
        }
        for u in e
            .get("links")
            .and_then(Value::as_array)
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
        {
            if (u.starts_with("http://") || u.starts_with("https://"))
                && !urls.iter().any(|x| x == u)
            {
                urls.push(u.to_owned());
            }
        }
    }
    if urls.is_empty() {
        return Ok(0);
    }
    run.door
        .ask("save_cached", &json!([urls, shown(&out.join("pages"))]))?;
    Ok(urls.len())
}

/// The quote-verbatim report cut to the notes being re-checked: an entry kept when one of its passages is quoted in the cut notes, or its assertion stands in the excerpt.
pub(crate) fn scoped_verbatim(out: &Path, full_text: &str) -> Result<String, Fail> {
    let path = out.join("quote-verbatim.json");
    let mut data: Value = serde_json::from_str(&read_text(&path)?).map_err(fail)?;
    let mut joined = String::new();
    for e in std::fs::read_dir(out).map_err(fail)?.flatten() {
        let p = e.path();
        if p.extension().is_some_and(|x| x == "html") {
            joined += &read_text(&p)?;
        }
    }
    let kept_text = flat(&joined);
    let plain = flat(&untagged(&kept_text));
    let truthy = |v: Option<&Value>| v.is_some_and(|v| !l7r_guard::shared::checks::falsy(Some(v)));
    let footnotes: Vec<Value> = data
        .get("footnotes")
        .and_then(Value::as_array)
        .ok_or_else(|| "KeyError: 'footnotes'".to_owned())?
        .clone();
    let kept: Vec<Value> = footnotes
        .into_iter()
        .filter(|e| {
            let quoted = e
                .get("passages")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .any(|p| {
                    ["quote", "original"].iter().any(|k| {
                        truthy(p.get(*k))
                            && kept_text.contains(head(
                                &flat(&py_str(p.get(*k).unwrap_or(&Value::Null))),
                                40,
                            ))
                    })
                });
            quoted
                || (truthy(e.get("assertion"))
                    && plain.contains(head(&flat(&py_str(&e["assertion"])), 40)))
        })
        .collect();
    let n = kept.len();
    let mut lines = report_lines(full_text);
    lines.extend(kept.iter().map(|e| {
        let key = e
            .get("key")
            .filter(|v| truthy(Some(v)))
            .or_else(|| e.get("class"));
        format!(
            "  {} {} - {}",
            py_str(e.get("id").unwrap_or(&Value::Null)),
            py_str(key.unwrap_or(&Value::Null)),
            py_str(e.get("readability").unwrap_or(&Value::Null))
        )
    }));
    if let Some(obj) = data.as_object_mut() {
        obj.insert("footnotes".to_owned(), Value::Array(kept));
    }
    write(&path, &dumps(&data))?;
    Ok(lines.join("\n")
        + &format!("\n  (scoped to the {n} footnote(s) of the notes being re-checked)\n"))
}

/// The claims a WHOLE read is owed for: each owed note and the blocks carrying its mark, per question (feature 319).
fn claims_read(root: &Path, rows: &[Unit]) -> Result<String, Fail> {
    let mut wanted: BTreeMap<String, HashSet<String>> = BTreeMap::new();
    for u in rows.iter().filter(|u| u.check() == "source-reader") {
        let (stem, note) = u.subject().split_once('#').unwrap_or((u.subject(), ""));
        wanted
            .entry(stem.to_owned())
            .or_default()
            .insert(note.to_owned());
    }
    if wanted.is_empty() {
        return Ok(String::new());
    }
    let mut parts = vec![
        String::new(),
        "## The claims to read (the owed notes, and the sentences carrying them)".to_owned(),
        String::new(),
    ];
    for (stem, keys) in &wanted {
        let (q, page) = stem.split_once('.').unwrap_or((stem.as_str(), ""));
        for rel in fragments_for(q, root) {
            if rel.contains(".drawing.") != (page == "drawing") {
                continue;
            }
            let text = read_text(&root.join(&rel))?;
            let body = if rel.ends_with(".notes.html") {
                notes_subset(&text, keys)
            } else {
                excerpt(&text, keys, false)
            };
            if body.contains("data-note=\"") {
                parts.extend([
                    format!("### `{rel}`"),
                    String::new(),
                    "```".to_owned(),
                    body.trim_end_matches('\n').to_owned(),
                    "```".to_owned(),
                    String::new(),
                ]);
            }
        }
    }
    Ok(parts.join("\n") + "\n")
}

/// The page images a scanned source is read from, copied into `images/` and listed BY NAME (feature 395).
pub(crate) fn images_section(out: &Path, images: &[String]) -> Result<String, Fail> {
    let mut files: Vec<PathBuf> = Vec::new();
    for i in images {
        let p = py_path(i);
        if p.is_dir() {
            let mut inside: Vec<PathBuf> = std::fs::read_dir(&p)
                .map_err(fail)?
                .flatten()
                .map(|e| e.path())
                .collect();
            super::sort_paths(&mut inside);
            files.extend(inside);
        } else {
            files.push(p);
        }
    }
    files.retain(|f| f.is_file());
    if files.is_empty() {
        return Ok(String::new());
    }
    std::fs::create_dir_all(out.join("images")).map_err(fail)?;
    let mut listing = String::new();
    for f in &files {
        let name = f
            .file_name()
            .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
        std::fs::copy(f, out.join("images").join(&name)).map_err(fail)?;
        let _ = writeln!(listing, "- `images/{name}`");
    }
    Ok(format!(
        "\n## The page images (read these for a scanned page)\n\n{listing}"
    ))
}

/// Each owed source-reader note's words now against the last commit before its latest round (feature 395).
fn since_last_round(root: &Path, rows: &[Unit]) -> Result<String, Fail> {
    let state = state_path(&root.to_string_lossy())
        .filter(|p| p.is_file())
        .map_or_else(|| json!({}), |p| load(&p));
    let mut parts: Vec<String> = Vec::new();
    for u in rows.iter().filter(|u| u.check() == "source-reader") {
        let (stem, note) = u.subject().split_once('#').unwrap_or((u.subject(), ""));
        let q = stem.split_once('.').map_or(stem, |p| p.0);
        let subject = format!("q:{q}");
        let last = dispatches(&state)
            .into_iter()
            .filter(|v| {
                let notes: Vec<&str> = v
                    .get("notes")
                    .and_then(Value::as_array)
                    .map(|a| a.iter().filter_map(Value::as_str).collect())
                    .unwrap_or_default();
                v.get("check").and_then(Value::as_str) == Some("source-reader")
                    && v.get("subjects")
                        .and_then(Value::as_array)
                        .is_some_and(|s| s.iter().any(|x| x.as_str() == Some(subject.as_str())))
                    && !matches!(
                        v.get("state").and_then(Value::as_str),
                        Some("pending" | "running")
                    )
                    && (l7r_guard::shared::checks::falsy(v.get("notes")) || notes.contains(&note))
            })
            .map(|v| v.get("t").and_then(Value::as_f64).unwrap_or(0.0))
            .fold(0.0_f64, f64::max);
        if last == 0.0 {
            continue;
        }
        #[expect(clippy::cast_possible_truncation, reason = "`int(last)`, an epoch")]
        let before = git_out(
            root,
            &[
                "rev-list",
                "-1",
                &format!("--before=@{}", last.trunc() as i64),
                "HEAD",
            ],
        );
        let before = before.trim();
        for rel in fragments_for(q, root)
            .into_iter()
            .filter(|r| r.ends_with(".notes.html"))
        {
            let was = if before.is_empty() {
                String::new()
            } else {
                git_out(root, &["show", &format!("{before}:{rel}")])
            };
            let path = root.join(&rel);
            let current = read_text(&path)?;
            let (old_all, new_all) = (read_notes(&was, ""), read_notes(&current, ""));
            let (old, new) = (
                old_all.get(note).cloned().unwrap_or_default(),
                new_all.get(note).cloned().unwrap_or_default(),
            );
            if !new.is_empty() && old != new {
                let diff = unified_diff(
                    &py_lines(&old),
                    &py_lines(&new),
                    "at the last round",
                    "now",
                    1,
                );
                parts.extend([
                    format!("### `{rel}` | {note}"),
                    String::new(),
                    "```diff".to_owned(),
                ]);
                parts.extend(diff);
                parts.extend(["```".to_owned(), String::new()]);
            }
        }
    }
    if parts.is_empty() {
        return Ok(String::new());
    }
    Ok(format!("\n## What each owed note changed since its last source-reader round (read the added lines first)\n\n{}", parts.join("\n")))
}

/// One key's copies in `out` - its entry, and its page saved under `pages` - as a MANIFEST's rows.
fn key_rows(
    run: &mut Run,
    root: &Path,
    (key, entry): (&str, &Path),
    out: &Path,
    (whole, question): (bool, &str),
    pages: &str,
) -> Result<Rows, Fail> {
    let mut rows = vec![(
        copy(entry, out, Some(&format!("sources/{key}.html")))?,
        relative(entry, root),
        format!("the registry entry of `{key}`: its two write-ups"),
    )];
    let url = url_of(&read_text(entry)?);
    if url.is_empty() {
        return Ok(rows);
    }
    let saved = shown(&out.join(pages));
    let (code, text) = if whole {
        let args = [
            saved,
            url.clone(),
            "--question".to_owned(),
            if question.is_empty() {
                "none".to_owned()
            } else {
                question.to_owned()
            },
            "--sought".to_owned(),
            format!("source-reader: the passage behind a new claim on {key}"),
        ];
        let got = run.door.helper("source_pages", &args, root)?;
        let ledger = ledger_part(&got.1).to_owned();
        if !ledger.is_empty() {
            run.say(&ledger);
        }
        rows.push((format!("{pages}/"), url, "the page's whole visible text, saved - a long page in PARTS; grep them all, read the part a hit is in".to_owned()));
        got
    } else {
        let qfile = out.join(if pages == "pages" {
            "quotes.json".to_owned()
        } else {
            format!("{pages}.quotes.json")
        });
        let quoted = quoted_passages(run, root, key)?;
        write(&qfile, &pyjson::dumps(&json!(quoted), None, false))?;
        let args = [
            saved,
            url.clone(),
            "--quotes".to_owned(),
            shown(&qfile),
            "--no-ledger".to_owned(),
        ];
        let got = run.door.helper("source_pages", &args, root)?;
        rows.push((format!("{pages}/"), url, "the page's visible text, saved - a long page as an EXCERPT (its front and a window around each passage the record quotes); grep it; MANIFEST.txt says which".to_owned()));
        got
    };
    if code != 0 {
        run.warn(&text);
    }
    Ok(rows)
}

/// A source's bundle (`key_bundle`): its entry and its page, the claims a whole read is owed for.
#[expect(clippy::too_many_arguments, reason = "the Python's own parameters")]
pub(crate) fn key_bundle(
    run: &mut Run,
    root: &Path,
    key: &str,
    out: &Path,
    read: (bool, &str),
    owed: &str,
    rows_owed: &[Unit],
    images: &[String],
) -> Result<i32, Fail> {
    let Some(entry) = registry_entry(root, key) else {
        run.warn(&format!(
            "check-bundle: no registry entry for {}",
            super::py_repr(key)
        ));
        return Ok(2);
    };
    fresh(out)?;
    let rows = key_rows(run, root, (key, &entry), out, read, "pages")?;
    let extra = images_section(out, images)? + &since_last_round(root, rows_owed)?;
    let text = manifest(out, &format!("source {key}"), &rows)?
        + owed
        + &claims_read(root, rows_owed)?
        + &extra;
    write(&out.join(MANIFEST), &with_earlier(root, out, &text)?)?;
    run.say(&format!(
        "check-bundle: {} item(s) in {} - hand the agent {}",
        rows.len(),
        shown(out),
        shown(&out.join(MANIFEST))
    ));
    Ok(0)
}

/// A source-applicability bundle over several keys (feature 312), refused for a key nothing owes unless a reason is given.
pub(crate) fn keys_bundle(
    run: &mut Run,
    root: &Path,
    keys: &[String],
    out_arg: &str,
    not_owed_ok: &str,
) -> Result<i32, Fail> {
    let mut rows_owed: Vec<Unit> = Vec::new();
    let every = owed_units(root, None, None, &["record"], "")?;
    let mut entries = Vec::new();
    for key in keys {
        let Some(entry) = registry_entry(root, key) else {
            run.warn(&format!(
                "check-bundle: no registry entry for {}",
                super::py_repr(key)
            ));
            return Ok(2);
        };
        entries.push(entry);
        let (got, _, refusal) = bo::owed_for_key(root, key, false, not_owed_ok, "", Some(&every))?;
        if !refusal.is_empty() {
            run.warn(&format!("check-bundle: REFUSED - {key}: {refusal}"));
            return Ok(3);
        }
        rows_owed.extend(got);
    }
    let first = keys
        .first()
        .ok_or_else(|| "IndexError: list index out of range".to_owned())?;
    let out = if out_arg.is_empty() {
        default_root().join(format!("keys-{first}-{}", keys.len()))
    } else {
        py_path(out_arg)
    };
    fresh(&out)?;
    let mut rows = Vec::new();
    for (key, entry) in keys.iter().zip(&entries) {
        rows.extend(key_rows(
            run,
            root,
            (key, entry),
            &out,
            (false, ""),
            &format!("pages/{key}"),
        )?);
    }
    let text = manifest(
        &out,
        &format!("{} sources, for source-applicability", keys.len()),
        &rows,
    )? + &bo::manifest_lines(&rows_owed, "source-applicability", not_owed_ok);
    write(&out.join(MANIFEST), &text)?;
    run.say(&format!(
        "check-bundle: {} source(s) in {} - hand the agent {}",
        keys.len(),
        shown(&out),
        shown(&out.join(MANIFEST))
    ));
    Ok(0)
}

/// An intro-check bundle over one question or a batch (plan D4, D10), refused for a question nothing owes it on unless a reason is given.
pub(crate) fn intro_bundle(
    run: &mut Run,
    root: &Path,
    questions: &[String],
    out_arg: &str,
    not_owed_ok: &str,
) -> Result<i32, Fail> {
    let mut rows_owed: Vec<Unit> = Vec::new();
    let every = owed_units(root, None, None, &["record"], "")?;
    for q in questions {
        let (got, _, refusal) =
            bo::owed_for_question(root, q, "intro-check", not_owed_ok, Some(&every))?;
        if !refusal.is_empty() {
            run.warn(&format!("check-bundle: REFUSED - {refusal}"));
            return Ok(3);
        }
        rows_owed.extend(got);
    }
    let mut docs = None;
    let mut texts = Vec::new();
    for q in questions {
        texts.push((q, bo::intro_bundle_text(root, q, &mut docs)?));
    }
    let missing: Vec<&str> = texts
        .iter()
        .filter(|(_, t)| t.is_empty())
        .map(|(q, _)| q.as_str())
        .collect();
    if !missing.is_empty() {
        run.warn(&format!(
            "check-bundle: no research page for {}",
            missing.join(" ")
        ));
        return Ok(2);
    }
    let first = questions
        .first()
        .ok_or_else(|| "IndexError: list index out of range".to_owned())?;
    let out = if out_arg.is_empty() {
        let many = if questions.len() > 1 {
            format!("-{}", questions.len())
        } else {
            String::new()
        };
        default_root().join(format!("intro-{}{many}", slug(first)))
    } else {
        py_path(out_arg)
    };
    fresh(&out)?;
    let mut rows: Rows = Vec::new();
    for (q, text) in &texts {
        let name = format!("q-{}.txt", bo::question_of(q));
        write(&out.join(&name), text)?;
        rows.push((name, format!("{QUESTIONS}/{}-*.html", bo::question_of(q)), "for intro-check: the research page, its drawing page, the map elements written from it".to_owned()));
    }
    let title = if questions.len() == 1 {
        format!("question {first}, for intro-check")
    } else {
        format!("{} questions, for intro-check", questions.len())
    };
    let text = manifest(&out, &title, &rows)?
        + &bo::manifest_lines(&rows_owed, "intro-check", not_owed_ok);
    write(&out.join(MANIFEST), &with_earlier(root, &out, &text)?)?;
    run.say(&format!(
        "check-bundle: {} question(s) in {} - hand the agent {}",
        rows.len(),
        shown(&out),
        shown(&out.join(MANIFEST))
    ));
    Ok(0)
}

#[cfg(test)]
mod tests;
