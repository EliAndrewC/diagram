//! The lean bundle a plan review reads (feature 375 amendment 11, FR-046, plan D64; feature 449 T066, from `plan_bundle.py`). The GM,
//! 2026-10-13: *"Is feature 374 growing too large in a way that eats tokens"*. A section's decisions answer to the requirements they
//! cite, so the bundle carries those in full, a one-line index of the rest, the GM's own words whole, the blocks under review and their
//! earlier text - built out of the repository, where no `CLAUDE.md` rides along.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::{Captures, Regex};
use serde_json::{json, Map, Value};

use super::history::History;
use super::sections::{block_digest, blocks, digest, re, task_sections};
use super::status::{reviewed_blocks, text_of, RECORD, REMOVED};

static IDS: LazyLock<Regex> = LazyLock::new(|| re(r"\b((?:FR|SC)-\d{3}[a-z]?|D\d+[a-z]?)\b"));
/// Another feature's requirement or decision, named as its own (feature 385 T66, T71, T123).
static QUALIFIED: LazyLock<Regex> = LazyLock::new(|| {
    re(
        r"(?<![-\w])(?:[Ff]eature\s+)?(\d{3})(?:'s|,)?\s+(?:amendment\s+\d+,?\s+)?\(?(?:plan\s+)?((?:FR|SC)-\d{3}[a-z]?|D\d+[a-z]?)\b",
    )
});
static ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^- \*\*((?:FR|SC)-\d{3}[a-z]?)\b"));
static RANGE: LazyLock<Regex> =
    LazyLock::new(|| re(r"\b(FR|SC)-(\d{3})\s*(?:-|to|through)\s*(?:(?:FR|SC)-)?(\d{3})\b"));
static DRANGE: LazyLock<Regex> = LazyLock::new(|| re(r"\bD(\d+)\s*(?:-|to|through)\s*D(\d+)\b"));
/// Every form the plans write a decision in (405 T133, D123; feature 449's plan's unbolded list item).
static DECISION: LazyLock<Regex> =
    LazyLock::new(|| re(r"(?m)^(?:- \*\*|\*\*|- (?=D\d+[a-z]? - ))(D\d+[a-z]?)(?: - |\*\*|\.| )"));
static HEAD_ITEM: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{2,4} ((?:FR|SC)-\d{3}[a-z]?)\b"));
static AMEND: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^## Amendment (\d+)\b"));
static SPEC_AMEND: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^### Amendment (\d+)\b"));
static KEY_AMEND: LazyLock<Regex> = LazyLock::new(|| re(r"\bAmendment (\d+)\b"));
static BODY_AMEND: LazyLock<Regex> = LazyLock::new(|| re(r"^\s*#+ Amendment (\d+)\b"));
static NEXT_TOP: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^#{1,4} "));
static NEXT_TWO: LazyLock<Regex> = LazyLock::new(|| re(r"(?m)^##"));
static MKEY: LazyLock<Regex> = LazyLock::new(|| re(r"\bm:([a-z0-9][a-z0-9-]*)"));
static BLOCK_TASK: LazyLock<Regex> = LazyLock::new(|| re(r"^#+ (T\d+)\b"));

const TOO_LONG: usize = 40;

/// `text` with each cited requirement or decision range written out id by id (at most 40 ids a range; a longer one is left as it is).
fn expand_ranges(text: &str) -> String {
    let first = RANGE.replace_all(text, |c: &Captures<'_>| {
        let (a, b): (usize, usize) = (c[2].parse().unwrap_or(0), c[3].parse().unwrap_or(0));
        if b > a && b - a <= TOO_LONG {
            (a..=b)
                .map(|n| format!("{}-{n:03}", &c[1]))
                .collect::<Vec<_>>()
                .join(", ")
        } else {
            c[0].to_owned()
        }
    });
    DRANGE
        .replace_all(&first, |c: &Captures<'_>| {
            let (a, b): (usize, usize) = (c[1].parse().unwrap_or(0), c[2].parse().unwrap_or(0));
            if b > a && b - a <= TOO_LONG {
                (a..=b)
                    .map(|n| format!("D{n}"))
                    .collect::<Vec<_>>()
                    .join(", ")
            } else {
                c[0].to_owned()
            }
        })
        .into_owned()
}

/// `{id: its paragraph}`: each match to the next blank line or the next item.
fn paragraphs(text: &str, pattern: &Regex) -> Map<String, Value> {
    let starts: Vec<(usize, String)> = pattern
        .captures_iter(text)
        .flatten()
        .map(|c| (c.get(0).map_or(0, |g| g.start()), c[1].to_owned()))
        .collect();
    let mut out = Map::new();
    for (i, (at, id)) in starts.iter().enumerate() {
        let blank = text[*at..].find("\n\n").map(|p| at + p);
        let next = starts.get(i + 1).map(|(a, _)| *a);
        let end = blank
            .into_iter()
            .chain(next)
            .filter(|x| *x > 0)
            .min()
            .unwrap_or(text.len());
        out.entry(id.clone())
            .or_insert_with(|| Value::from(format!("{}\n", text[*at..end].trim_end())));
    }
    out
}

/// `{FR or SC id: its text}`: a `- **FR-NNN**` item to its paragraph's end, a `### FR-NNN` heading to the next heading.
fn requirements(spec: &str) -> Map<String, Value> {
    let mut out = paragraphs(spec, &ITEM);
    for c in HEAD_ITEM.captures_iter(spec).flatten() {
        let whole = c.get(0).map_or((0, 0), |g| (g.start(), g.end()));
        let rest = &spec[whole.1..];
        let end = NEXT_TOP
            .find(rest)
            .ok()
            .flatten()
            .map_or(spec.len(), |n| whole.1 + n.start());
        out.entry(c[1].to_owned())
            .or_insert_with(|| Value::from(format!("{}\n", spec[whole.0..end].trim_end())));
    }
    out
}

/// `request.md` as (the original request, [(amendment number, its section)]).
fn request_sections(text: &str) -> (&str, Vec<(u32, &str)>) {
    let starts: Vec<(usize, u32)> = AMEND
        .captures_iter(text)
        .flatten()
        .map(|c| (c.get(0).map_or(0, |g| g.start()), c[1].parse().unwrap_or(0)))
        .collect();
    let Some(first) = starts.first() else {
        return (text, Vec::new());
    };
    let parts = starts
        .iter()
        .enumerate()
        .map(|(i, (at, n))| {
            (
                *n,
                &text[*at..starts.get(i + 1).map_or(text.len(), |s| s.0)],
            )
        })
        .collect();
    (&text[..first.0], parts)
}

/// `{FR or SC id: the amendment whose spec section holds it}`.
fn spec_amendments(spec: &str) -> BTreeMap<String, u32> {
    let mut out = BTreeMap::new();
    for c in SPEC_AMEND.captures_iter(spec).flatten() {
        let start = c.get(0).map_or(0, |g| g.end());
        let rest = &spec[start..];
        let body = NEXT_TWO
            .find(rest)
            .ok()
            .flatten()
            .map_or(rest, |n| &rest[..n.start()]);
        for item in ITEM.captures_iter(body).flatten() {
            out.entry(item[1].to_owned())
                .or_insert(c[1].parse().unwrap_or(0));
        }
    }
    out
}

/// The earliest amendment the blocks answer; None when any block answers none (the original plan, judged against the whole request).
fn answered(under: &[(String, String)], spec: &str) -> Option<u32> {
    let of = spec_amendments(spec);
    let mut found = Vec::new();
    for (key, body) in under {
        let named = KEY_AMEND
            .captures(key)
            .ok()
            .flatten()
            .or(BODY_AMEND.captures(body).ok().flatten())
            .map(|c| c[1].parse().unwrap_or(0));
        let joined = format!("{key}\n{body}");
        let ns: Vec<u32> = named
            .into_iter()
            .chain(
                IDS.captures_iter(&joined)
                    .flatten()
                    .filter_map(|i| of.get(&i[1]).copied()),
            )
            .collect();
        found.push(*ns.iter().min()?);
    }
    found.into_iter().min()
}

/// (the request a review of amendment `n` reads, the index of what it leaves out). Every amendment from `n` on is kept.
fn trimmed_request(text: &str, n: Option<u32>) -> (String, String) {
    let (head, parts) = request_sections(text);
    let Some(n) = n.filter(|_| !parts.is_empty()) else {
        return (text.to_owned(), String::new());
    };
    let kept: String = parts
        .iter()
        .filter(|(k, _)| *k >= n)
        .map(|(_, b)| *b)
        .collect();
    let index: String = parts
        .iter()
        .filter(|(k, _)| *k < n)
        .map(|(_, body)| {
            let mut lines = body.lines();
            let first = lines.next().unwrap_or("");
            let next: String = lines
                .find(|l| !l.trim().is_empty())
                .unwrap_or("")
                .trim()
                .chars()
                .take(160)
                .collect();
            format!("{first} - {next}\n")
        })
        .collect();
    (format!("{head}{kept}"), index)
}

fn read(path: &Path) -> String {
    std::fs::read_to_string(path).unwrap_or_default()
}

fn plans_of(dir: &Path) -> String {
    read(&dir.join("plan.md")) + &read(&dir.join("plan-done.md"))
}

/// Each (feature, id) another feature's requirement, from that feature's one directory, under a line naming it.
fn foreign(spec_dir: &Path, others: &[(String, String)]) -> Vec<String> {
    let parent = spec_dir.parent().unwrap_or(Path::new("."));
    let mut out = Vec::new();
    for (no, rid) in others {
        let prefix = format!("{no}-");
        let hits: Vec<PathBuf> = std::fs::read_dir(parent)
            .into_iter()
            .flatten()
            .flatten()
            .filter(|e| e.file_name().to_string_lossy().starts_with(&prefix) && e.path().is_dir())
            .map(|e| e.path())
            .collect();
        let [hit] = hits.as_slice() else {
            continue;
        };
        let found = if rid.starts_with('D') {
            paragraphs(&plans_of(hit), &DECISION)
        } else {
            requirements(&read(&hit.join("spec.md")))
        };
        if let Some(text) = found.get(rid).and_then(Value::as_str) {
            out.push(format!("<!-- feature {no} -->\n{text}"));
        }
    }
    out
}

/// Each `m:` figure the blocks cite, in full from the feature's `measurements.json`.
fn measured(spec_dir: &Path, bodies: &[&str]) -> String {
    let mut keys: Vec<String> = Vec::new();
    for body in bodies {
        for c in MKEY.captures_iter(body).flatten() {
            if !keys.iter().any(|k| *k == c[1]) {
                keys.push(c[1].to_owned());
            }
        }
    }
    let figures: Value =
        serde_json::from_str(&read(&spec_dir.join("measurements.json"))).unwrap_or(json!({}));
    let found: Vec<String> = keys
        .iter()
        .filter_map(|k| {
            let entry = figures.get(k)?.as_object()?;
            let lines: String = entry
                .iter()
                .map(|(f, v)| {
                    format!(
                        "- **{f}**: {}\n",
                        v.as_str()
                            .map_or_else(|| crate::checks::py_repr(v), str::to_owned)
                    )
                })
                .collect();
            Some(format!("### m:{k}\n\n{lines}"))
        })
        .collect();
    if found.is_empty() {
        String::new()
    } else {
        format!(
            "\n\n## The measurements the blocks cite (`measurements.json`)\n\n{}",
            found.join("\n")
        )
    }
}

fn json_str(text: &str) -> String {
    serde_json::to_string(text).unwrap_or_default()
}

/// A Python `json.dumps` of a text: non-ASCII escaped.
fn ascii_json(text: &str) -> String {
    json_str(text)
        .chars()
        .flat_map(|c| {
            if c.is_ascii() {
                vec![c.to_string()]
            } else {
                c.encode_utf16(&mut [0; 2])
                    .iter()
                    .map(|u| format!("\\u{u:04x}"))
                    .collect()
            }
        })
        .collect()
}

/// Write the bundle for the blocks `under` and return its MANIFEST; `earlier` is `{key: (its text when last judged, the verdict it got)}`.
pub(super) fn build(
    spec_dir: &Path,
    out_root: &Path,
    name: &str,
    under: &[(String, String)],
    earlier: &[(String, String, String)],
    how: &str,
) -> Result<PathBuf, String> {
    let feature = spec_dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    // NO REQUEST, NO BUNDLE (feature 405 T30, D2): a review against the spec alone tests the plan for self-consistency only.
    if !spec_dir.join("request.md").is_file() {
        return Err(format!("plan bundle: specs/{feature}/request.md is missing - write the GM's words there verbatim (the request and every amendment, as the spec's 'The request' quotes them), commit it, and build again"));
    }
    // ...A NAME THAT FITS THE FILE SYSTEM (feature 449, 2026-11-07): past 120 characters it is cut, the rest kept as a hash.
    let name = if name.chars().count() > 120 {
        format!(
            "{}-{}",
            name.chars().take(80).collect::<String>(),
            &digest(name.as_bytes())[..12]
        )
    } else {
        name.to_owned()
    };
    let out = out_root.join(format!("plan-{feature}-{name}"));
    let _ = std::fs::remove_dir_all(&out);
    let _ = std::fs::create_dir_all(&out);
    let spec = read(&spec_dir.join("spec.md"));
    let (items, decisions) = (
        requirements(&spec),
        paragraphs(&plans_of(spec_dir), &DECISION),
    );
    let own_no: String = feature.chars().take(3).collect();
    let mut others: Vec<(String, String)> = Vec::new();
    let mut cited: Vec<String> = Vec::new();
    let mut own: BTreeSet<String> = BTreeSet::new();
    for (_, body) in under {
        for c in QUALIFIED.captures_iter(body).flatten() {
            let pair = (c[1].to_owned(), c[2].to_owned());
            if pair.0 != own_no && !others.contains(&pair) {
                others.push(pair);
            }
        }
        let bare = QUALIFIED.replace_all(body, |c: &Captures<'_>| {
            if c[1] == *own_no {
                c[2].to_owned()
            } else {
                String::new()
            }
        });
        let expanded = expand_ranges(&bare);
        for c in IDS.captures_iter(&expanded).flatten() {
            if !cited.iter().any(|x| *x == c[1]) {
                cited.push(c[1].to_owned());
            }
        }
        own.extend(
            DECISION
                .captures_iter(body)
                .flatten()
                .map(|c| c[1].to_owned()),
        );
    }
    let text_at =
        |map: &Map<String, Value>, id: &str| map.get(id).and_then(Value::as_str).map(str::to_owned);
    let mut parts: Vec<String> = cited
        .iter()
        .filter(|i| !own.contains(*i))
        .filter_map(|i| {
            text_at(&items, i)
                .filter(|t| !t.is_empty())
                .or_else(|| text_at(&decisions, i))
        })
        .collect();
    parts.extend(foreign(spec_dir, &others));
    let bodies: Vec<&str> = under.iter().map(|(_, b)| b.as_str()).collect();
    let write = |file: &str, text: String| {
        let _ = std::fs::write(out.join(file), text);
    };
    write(
        "spec-cited.md",
        format!(
            "# The requirements and decisions the blocks name, in full\n\n{}{}",
            parts.join("\n"),
            measured(spec_dir, &bodies)
        ),
    );
    let index: String = items
        .iter()
        .filter(|(i, _)| !cited.contains(*i))
        .map(|(_, p)| {
            format!(
                "{}\n",
                p.as_str().unwrap_or("").lines().next().unwrap_or("")
            )
        })
        .collect();
    write(
        "spec-index.md",
        format!("# Every other requirement, its first line\n\n{index}"),
    );
    let (req, left) = trimmed_request(&read(&spec_dir.join("request.md")), answered(under, &spec));
    write("request.md", req);
    let shown = if left.is_empty() {
        "(none - the whole request is in request.md)\n".to_owned()
    } else {
        left
    };
    write("request-index.md", format!("# The request's sections left out - each earlier amendment, its heading and first line\n\n{shown}"));
    write(
        "blocks.md",
        under
            .iter()
            .map(|(k, b)| {
                format!(
                    "<!-- block {} sha256 {} -->\n{b}\n",
                    ascii_json(k),
                    block_digest(b)
                )
            })
            .collect(),
    );
    let before: String = earlier
        .iter()
        .map(|(k, t, v)| {
            format!(
                "<!-- block {} verdict {} -->\n{t}\n",
                ascii_json(k),
                if v.is_empty() {
                    "no verdict recorded"
                } else {
                    v
                }
            )
        })
        .collect();
    let before = if before.is_empty() {
        "(none - every block here is new)\n".to_owned()
    } else {
        before
    };
    write(
        "earlier.md",
        format!("# Each changed block's text when last judged, with that verdict\n\n{before}"),
    );
    let manifest = out.join("MANIFEST.md");
    let _ = std::fs::write(&manifest, format!("# Plan review bundle - {feature}, {name}\n\nA MODE 4 plan review of the blocks in `blocks.md` and nothing else of the plan (feature 375 amendment 11). Read the files beside\nthis MANIFEST and nothing in the repository: `request.md` is the GM's words verbatim - the original request and every amendment\nfrom the one these blocks answer on, the earlier ones indexed in `request-index.md`; `spec-cited.md` holds every requirement,\ndecision and `m:` measurement the blocks name, in full; `spec-index.md` the first line of every other requirement - grep it for one the blocks\nshould have named; `earlier.md` what a changed block said when last judged, and the verdict it got.\n\nFind each decision in the blocks, class it `within` or `narrowing`, and rule on each narrowing (LEGITIMATE / NOT LEGITIMATE).\n\n{how}\n"));
    Ok(manifest)
}

fn review_of(spec_dir: &Path) -> Value {
    serde_json::from_str(&read(&spec_dir.join(RECORD))).unwrap_or(json!({}))
}

fn number_of(spec_dir: &Path) -> String {
    spec_dir
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .split('-')
        .next()
        .unwrap_or("")
        .to_owned()
}

/// `make decide`'s dispatch (FR-003(a)) on the bundle of one task's section.
pub(super) fn task_prompt(spec_dir: &Path, out_root: &Path, task: &str) -> Result<String, String> {
    let plan = spec_dir.join("plan.md");
    let section = task_sections(&read(&plan)).remove(task).unwrap_or_default();
    let review = review_of(spec_dir);
    let entry = review
        .get("tasks")
        .and_then(|t| t.get(task))
        .cloned()
        .unwrap_or(json!({}));
    let was = text_of(&entry, "section_sha256")
        .filter(|s| !s.is_empty())
        .and_then(|s| History::new(&plan, "HEAD").section(task, s));
    let n = number_of(spec_dir);
    let how = format!("Record it: the JSON is `{{\"section_sha256\": \"{}\", \"decisions\": [...]}}`, written under /tmp, then `make plan-verdict F={n} TASK={task} FILE=<it> AS=spec-fidelity`.", digest(section.as_bytes()));
    let earlier: Vec<(String, String, String)> = was
        .into_iter()
        .map(|t| {
            (
                task.to_owned(),
                t,
                text_of(&entry, "verdict").unwrap_or("").to_owned(),
            )
        })
        .collect();
    let manifest = build(
        spec_dir,
        out_root,
        task,
        &[(format!("the section of {task}"), section)],
        &earlier,
        &how,
    )?;
    let feature = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    Ok(format!("MODE 4: PLAN REVIEW of one task's section - feature {feature}, task {task} (a decision preflight, feature 375 FR-003a), on its bundle: read {} and the files beside it, and nothing in the repository.", manifest.display()))
}

/// `make plan-delta`'s dispatch (FR-043) on the bundle of the plan's changed blocks.
pub(super) fn delta_prompt(
    spec_dir: &Path,
    out_root: &Path,
    keys: &[String],
) -> Result<String, String> {
    let plan = spec_dir.join("plan.md");
    let text = read(&plan);
    let under: Vec<(String, String)> = blocks(&text)
        .into_iter()
        .filter(|(k, ..)| keys.contains(k))
        .map(|(k, b, _)| (k, b))
        .collect();
    let have = reviewed_blocks(&review_of(spec_dir));
    let history = History::new(&plan, "HEAD");
    let removed: Vec<&str> = keys
        .iter()
        .filter_map(|k| k.strip_prefix(REMOVED))
        .collect();
    let text_at = |k: &str| -> String {
        let entry = &have[k];
        text_of(entry, "text")
            .filter(|t| !t.is_empty())
            .map(str::to_owned)
            .or_else(|| history.block(k, text_of(entry, "sha256").unwrap_or("None")))
            .unwrap_or_default()
    };
    let verdict_at = |k: &str| text_of(&have[k], "verdict").unwrap_or("").to_owned();
    let mut earlier: Vec<(String, String, String)> = Vec::new();
    for (k, _) in under.iter().filter(|(k, _)| have.contains_key(k)) {
        earlier.push((k.clone(), text_at(k), verdict_at(k)));
    }
    for k in removed.iter().filter(|k| have.contains_key(**k)) {
        earlier.push((format!("{REMOVED}{k}"), text_at(k), verdict_at(k)));
    }
    let n = number_of(spec_dir);
    let mut shas: Vec<String> = under
        .iter()
        .map(|(k, b)| format!("{}: \"{}\"", ascii_json(k), block_digest(b)))
        .collect();
    shas.extend(
        removed
            .iter()
            .map(|k| format!("{}: \"removed\"", ascii_json(&format!("{REMOVED}{k}")))),
    );
    let shas = format!("{{{}}}", shas.join(", "));
    let how = format!("Record it: the JSON is `{{\"blocks\": {shas}, \"decisions\": [...]}}`, written under /tmp, then `make plan-verdict F={n} BLOCKS=1 FILE=<it> AS=spec-fidelity`.");
    let tasks: BTreeSet<String> = under
        .iter()
        .filter_map(|(k, _)| {
            BLOCK_TASK
                .captures(k)
                .ok()
                .flatten()
                .map(|c| c[1].to_owned())
        })
        .collect();
    let label = if tasks.is_empty() {
        "plan".to_owned()
    } else {
        tasks.into_iter().collect::<Vec<_>>().join("-")
    };
    let name = format!("blocks-{label}-{}", &digest(shas.as_bytes())[..8]);
    let kept: Vec<(String, String, String)> = earlier
        .into_iter()
        .filter(|(_, t, _)| !t.is_empty())
        .collect();
    let manifest = build(spec_dir, out_root, &name, &under, &kept, &how)?;
    let feature = spec_dir.file_name().unwrap_or_default().to_string_lossy();
    Ok(format!("MODE 4: PLAN REVIEW of {} changed block(s) of feature {feature}'s plan (feature 375 FR-043), on their bundle: read {} and the files beside it, and nothing in the repository.", under.len() + removed.len(), manifest.display()))
}

#[cfg(test)]
mod tests;
