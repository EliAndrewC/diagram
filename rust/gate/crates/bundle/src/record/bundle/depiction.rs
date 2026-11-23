//! What `modal-depiction` reads beyond the modal and the rules (from `modal_bundle.py`, plan D13): each drawing page its `Drawing:` lists and each candidate its kind has, the knobs its conditions name (feature 374), the engine's claims citing those pages, and the glyph's crop - the one browser crate's `l7r-browser crop`, run as a program, only for this check (`ask:449-T88-bundles`; Playwright's `glyph_crop.py` until feature 449 T146).

use std::collections::HashSet;
use std::fmt::Write as _;
use std::io::Read as _;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::LazyLock;
use std::time::{Duration, Instant};

use fancy_regex::Regex;
use serde_json::{json, Map, Value};

use super::modal::Put;
use super::{findall, py_str, pyre, relative, shown};
use crate::record::modals::{self, Modal};
use crate::record::owed::merge_base;
use crate::record::py_lines;
use crate::record::repo::{fail, read_text, tree_of, Fail};
use l7r_gate_registry::conditions::{knob_table, knobs};

const CLAIMS_INDEX: &str = "dev/claims-index.json";
/// Where the pool pages a glyph is cropped from live; the hamlets are searched first.
const POOL: &str = l7r_gate_pool::LIVE;
const HAMLETS: &str = "hamlets";
/// How long the crop may take before the Python's `subprocess.TimeoutExpired`.
#[cfg(not(test))]
const CROP_TIMEOUT: Duration = Duration::from_secs(180);
/// The tests' own, under the fake crop's 5 s sleep: 300 ms was outlasted by a Python start alone with the coverage runs five crates at
/// a time, at a load of 13.8 (feature 449 T108, 2026-11-11), failing the crop of a page that was not slow, so it was a second - which the
/// slow page's test waited out whole, 1.3 s against FR-008's tenth of a second. The fake crop is a `sh` script now, which starts in a
/// few milliseconds where Python took tens, so 150 ms is still many times a start under that load (feature 449 T160).
#[cfg(test)]
const CROP_TIMEOUT: Duration = Duration::from_millis(150);
/// How often the crop is asked whether it has finished: a twentieth of a second, against its three minutes.
#[cfg(not(test))]
const CROP_POLL: Duration = Duration::from_millis(50);
/// ...and every millisecond in the tests, whose fake crop is done in a few: the 50 ms step was waited out once a crop, most of five
/// tests' time against FR-008's tenth of a second (feature 449 T167).
#[cfg(test)]
const CROP_POLL: Duration = Duration::from_millis(1);

/// How long the crop of `page` may take.
#[cfg(not(test))]
fn crop_timeout(_page: &Path) -> Duration {
    CROP_TIMEOUT
}
/// ...and in the tests, a page named `slow` 20 ms - the fake crop sleeps 5 s on it, so the timeout is all its test waits, and 150 ms of
/// it alone was past FR-008's tenth of a second; every other page keeps the 150 ms a crop under load needs (feature 449 T167).
#[cfg(test)]
fn crop_timeout(page: &Path) -> Duration {
    if page.to_string_lossy().contains("slow") {
        Duration::from_millis(20)
    } else {
        CROP_TIMEOUT
    }
}

static KNOB: LazyLock<Regex> = LazyLock::new(|| pyre(r"\[([a-z_]+)=[a-z_0-9|-]+\]"));
static DRAWING_HREF: LazyLock<Regex> =
    LazyLock::new(|| pyre(r#"href="(?:[^"]*/)?(\d{4}-[^"/#]+\.drawing\.html)"#));
static NEXT_GROUP: LazyLock<Regex> = LazyLock::new(|| pyre(r#"<g[^>]*\bclass="f "#));
static SHAPE: LazyLock<Regex> =
    LazyLock::new(|| pyre(r"<(rect|polygon|path|ellipse|circle|line)\b([^>]*)>"));
static KEEP: LazyLock<Regex> = LazyLock::new(|| {
    pyre(
        r#"(?<![\w-])(x|y|width|height|points|d|cx|cy|r|rx|ry|x1|y1|x2|y2|transform)="([^"]{0,200})""#,
    )
});
static VIEWBOX: LazyLock<Regex> = LazyLock::new(|| pyre(r#"viewBox="([^"]*)""#));

const LISTED: &str = "LISTED - a page the modal's Drawing: names - how our maps draw it";

/// The crop: the one browser crate's `crop` (feature 449 T146, `ask:449-phase4-slices` Q4), run as a program through the tree's launcher
/// (`scripts/gates/l7r-gate.sh browser crop <page> <key> <out>`), so the gate never compiles a browser; it ran `glyph_crop.py` by
/// `python3 -c` until then (`ask:449-T88-bundles` Q3).
#[cfg(not(test))]
fn crop_command(root: &Path) -> Command {
    let mut cmd = Command::new(tree_of(root).join("scripts/gates/l7r-gate.sh"));
    cmd.args(["browser", "crop"]);
    cmd
}
/// The tests' crop: no browser - a page named `nocrop` fails, one named `slow` outlasts the timeout, any other gets an image and two kinds.
#[cfg(test)]
fn crop_command(_root: &Path) -> Command {
    let mut cmd = Command::new("sh");
    cmd.args(["-c", "case \"$1\" in *slow*) exec sleep 5;; *nocrop*) exit 1;; esac\nprintf png > \"$3\"\ncase \"$1\" in *nokinds*) ;; *) printf 'well\\nother\\n' > \"$3.kinds\";; esac\n", "crop"]);
    cmd
}

/// The claims-index rows whose cited pages include any of `files`, each with its verdict (plan D13).
fn claims_citing(root: &Path, files: &[String]) -> Result<Vec<String>, Fail> {
    let path = root.join(CLAIMS_INDEX);
    if !path.is_file() || files.is_empty() {
        return Ok(Vec::new());
    }
    let names: HashSet<String> = files
        .iter()
        .map(|f| {
            Path::new(f)
                .file_name()
                .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
        })
        .collect();
    let index: Map<String, Value> = serde_json::from_str(&read_text(&path)?).map_err(fail)?;
    let mut keys: Vec<&String> = index.keys().collect();
    keys.sort();
    let mut out = Vec::new();
    for key in keys {
        let row = &index[key];
        let pages = py_str(row.get("pages").unwrap_or(&json!("")));
        if names.iter().any(|n| pages.contains(n.as_str())) {
            let field = |k: &str, d: &str| row.get(k).map_or_else(|| d.to_owned(), py_str);
            let unit = key.split_once("l7r/diagram/").map_or(key.as_str(), |p| p.1);
            out.push(format!(
                "- {} | `{unit}` | {}",
                field("verdict", "?"),
                field("note", "")
            ));
        }
    }
    Ok(out)
}

/// The first pool page that draws the kind `key`, hamlets first and a hand sheet before a placer's draft; a SHEET kind on the sheets alone.
fn pool_page_with(root: &Path, key: &str, sheet: bool) -> Option<PathBuf> {
    let marks = [
        format!("data-k=\"{key}\""),
        format!("data-k=\"{}\"", html_escape(key)),
    ];
    // the live pool's folders from the one pool walk (feature 449 T220), each folder's pages asked of its listing
    let pool = l7r_gate_pool::walk(root);
    let mut tiers: Vec<&str> = pool.in_tree(POOL).map(|m| m.tier.as_str()).collect();
    tiers.dedup();
    tiers.sort_by_key(|t| (*t != HAMLETS, *t));
    let name = |p: &Path| {
        p.file_name()
            .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
    };
    for tier in tiers.into_iter().filter(|t| !(sheet && *t == HAMLETS)) {
        let mut pages: Vec<PathBuf> = pool
            .in_tree(POOL)
            .filter(|m| m.tier == tier && !m.name.ends_with("-test"))
            .flat_map(|m| {
                m.files
                    .iter()
                    .filter(|f| Path::new(f).extension().is_some_and(|x| x == "html"))
                    .map(|f| m.dir.join(f))
            })
            .collect();
        let parent = |p: &Path| p.parent().map(name).unwrap_or_default();
        pages.sort_by(|a, b| {
            (parent(a).ends_with("-example"), name(a))
                .cmp(&(parent(b).ends_with("-example"), name(b)))
        });
        for page in pages {
            let mut bytes = Vec::new();
            if std::fs::File::open(&page)
                .and_then(|mut f| f.read_to_end(&mut bytes))
                .is_err()
            {
                continue;
            }
            let text = String::from_utf8_lossy(&bytes);
            if marks.iter().any(|mk| text.contains(mk.as_str())) {
                return Some(page);
            }
        }
    }
    None
}

/// `html.escape(text, quote=True)`: the guard's, one implementation (feature 449 T144).
fn html_escape(text: &str) -> String {
    l7r_shared::html_text::escape(text, true)
}

/// The first `n` characters of `text` from character `at`.
fn chars_from(text: &str, at: usize, n: usize) -> String {
    text.chars().skip(at).take(n).collect()
}

/// The kind's first glyph's drawn parts as the sheet's markup gives them (343's clerks--seats ruling, 2026-10-11).
fn drawn_geometry(page: &Path, key: &str) -> String {
    let bytes = std::fs::read(page).unwrap_or_default();
    let text = crate::record::repo::universal(&String::from_utf8_lossy(&bytes));
    let find = |mark: String| text.find(&mark).map(|b| text[..b].chars().count());
    let at = [
        find(format!("data-k=\"{key}\"")),
        find(format!("data-k=\"{}\"", html_escape(key))),
    ]
    .into_iter()
    .flatten()
    .max();
    let Some(at) = at else {
        return String::new();
    };
    let mut chunk = chars_from(&text, at, 4000);
    let skip = chunk.chars().next().map_or(0, char::len_utf8);
    if let Some(m) = NEXT_GROUP.find(&chunk[skip..]).ok().flatten() {
        let cut = chunk[skip..skip + m.start()].chars().count();
        chunk = chunk.chars().take(cut).collect();
    }
    let lines: Vec<String> = SHAPE
        .captures_iter(&chunk)
        .map_while(Result::ok)
        .take(8)
        .map(|c| {
            let attrs: Vec<String> = KEEP
                .captures_iter(&c[2])
                .map_while(Result::ok)
                .map(|a| format!("{}=\"{}\"", &a[1], &a[2]))
                .collect();
            format!("- <{}> {}", &c[1], attrs.join(" "))
        })
        .collect();
    if lines.is_empty() {
        return String::new();
    }
    let vb = VIEWBOX
        .captures(&text)
        .ok()
        .flatten()
        .map_or_else(|| "?".to_owned(), |c| c[1].to_owned());
    let page_name = page
        .file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned());
    format!("\nThe first glyph's drawn parts on `{page_name}` (the page's units; viewBox {vb}; its scale bar names the feet):\n{}\n", lines.join("\n"))
}

/// The pop-up a click on kind `key` opens: the About-form modal of that key in the same registry as `m`, or the key.
fn click_target(found: &[Modal], key: &str, m: &Modal) -> String {
    let uid = m.uid();
    let registry = uid.split('/').next().unwrap_or("");
    found
        .iter()
        .find(|x| x.key == key && x.uid().starts_with(&format!("{registry}/")))
        .map_or_else(
            || format!("the `{key}` pop-up"),
            |hit| format!("`{}`", hit.uid()),
        )
}

/// A crop of the kind's first glyph on a pool page (plan D13): false when the browser is not there or the glyph cannot be found.
fn glyph_crop(root: &Path, page: &Path, key: &str, out: &Path) -> Result<bool, Fail> {
    let mut child = crop_command(root)
        .arg(page)
        .arg(key)
        .arg(out)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(fail)?;
    let (start, timeout) = (Instant::now(), crop_timeout(page));
    loop {
        if let Some(status) = child.try_wait().map_err(fail)? {
            return Ok(status.success() && out.is_file());
        }
        if start.elapsed() > timeout {
            let _ = child.kill();
            let _ = child.wait();
            return Err(format!(
                "subprocess.TimeoutExpired: the crop of {key} timed out after 180 seconds"
            ));
        }
        std::thread::sleep(CROP_POLL);
    }
}

#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the record's page names, as `str.endswith` read them"
)]
/// The drawing pages the modal's KIND may rest on beyond its own `Drawing:` list (the plan review of D13, rounds 2 and 3).
fn drawing_candidates(root: &Path, m: &Modal) -> Result<Vec<String>, Fail> {
    let mut out: Vec<String> = Vec::new();
    for f in m.entry_files() {
        if f.ends_with(".html") && !f.ends_with(".drawing.html") {
            let sibling = format!("{}.drawing.html", &f[..f.len() - ".html".len()]);
            if root.join(&sibling).is_file() {
                out.push(sibling);
            }
        }
    }
    let base = merge_base(root);
    if !base.is_empty() {
        let at = modals::modals_at(root, &base, false)?;
        if let Some(was) = at.get(&m.uid()) {
            out.extend(
                was.entry_files()
                    .into_iter()
                    .chain(was.drawing_files())
                    .filter(|f| f.ends_with(".drawing.html")),
            );
        }
    }
    for f in m.drawing_files() {
        let p = root.join(&f);
        if p.is_file() {
            out.extend(
                findall(&DRAWING_HREF, &read_text(&p)?, 1)
                    .into_iter()
                    .map(|h| format!("research/questions/{h}")),
            );
        }
    }
    let listed = m.drawing_files();
    let mut seen: Vec<String> = Vec::new();
    for f in out {
        if !seen.contains(&f) && !listed.contains(&f) && root.join(&f).is_file() {
            seen.push(f);
        }
    }
    Ok(seen)
}

/// Every `.rs` file under `dir`, sorted as Python sorts paths.
fn rust_files(dir: &Path) -> Vec<PathBuf> {
    fn walk(dir: &Path, out: &mut Vec<PathBuf>) {
        for e in std::fs::read_dir(dir).into_iter().flatten().flatten() {
            let p = e.path();
            if p.is_dir() {
                walk(&p, out);
            } else if p.extension().is_some_and(|x| x == "rs") {
                out.push(p);
            }
        }
    }
    let mut out = Vec::new();
    walk(dir, &mut out);
    super::sort_paths(&mut out);
    out
}

/// Where the kind is drawn, for each knob the modal's conditions name (feature 374, the round arbiter's tooling fix); "" when it names none.
fn knobs_note(tree: &Path, doc: &str) -> Result<String, Fail> {
    let mut names: Vec<String> = Vec::new();
    for n in findall(&KNOB, doc, 1) {
        if !names.contains(&n) {
            names.push(n);
        }
    }
    if names.is_empty() {
        return Ok(String::new());
    }
    // the knob registry read in process (feature 449 T149): `conditions.knobs()` and `knob_table()` were the Python door's two verbs
    let fault = |e: l7r_gate_research::Error| format!("{}: {}", e.kind, e.message);
    let forms = Value::Object(
        knobs(tree)
            .map_err(fault)?
            .into_iter()
            .map(|(name, f)| (name, Value::Array(f)))
            .collect(),
    );
    let table = Value::Object(knob_table(tree).map_err(fault)?);
    let engine = rust_files(&tree.join("rust").join("phases").join("src"));
    let mut parts = vec![
        "# The knobs this modal's conditions name - which maps draw what it conditions\n"
            .to_owned(),
    ];
    for name in &names {
        let k = table
            .get(name)
            .filter(|k| !l7r_shared::checks::falsy(Some(k)));
        let listed: Vec<String> = forms
            .get(name)
            .and_then(Value::as_array)
            .map(|a| a.iter().map(py_str).collect())
            .unwrap_or_default();
        let listed = if listed.is_empty() {
            "(not registered)".to_owned()
        } else {
            listed.join(", ")
        };
        let default = k.map_or_else(String::new, |k| {
            format!(
                "; default {}",
                py_str(k.get("default").unwrap_or(&Value::Null))
            )
        });
        parts.push(format!("## {name}\n\nforms: {listed}{default}\n"));
        if let Some(rule) = table
            .get(name)
            .and_then(|k| k.get("typing_rule"))
            .filter(|r| !l7r_shared::checks::falsy(Some(r)))
        {
            parts.push(format!(
                "The typing rule (which settlements may take each form):\n\n```python\n{}```\n",
                py_str(rule)
            ));
        }
        let quoted = format!("\"{name}\"");
        let mut hits = Vec::new();
        'files: for f in &engine {
            for (i, line) in py_lines(&read_text(f)?).iter().enumerate() {
                if line.contains(&quoted) && !line.contains(" - ") {
                    hits.push(format!(
                        "- `{}:{}: {}`",
                        relative(f, tree),
                        i + 1,
                        l7r_shared::py_text::strip(line)
                    ));
                    if hits.len() == 15 {
                        break 'files;
                    }
                }
            }
        }
        let body = if hits.is_empty() {
            "- (no line names it)".to_owned()
        } else {
            hits.join("\n")
        };
        parts.push(format!("Where the engine sets or reads it:\n\n{body}\n"));
    }
    Ok(parts.join("\n"))
}

/// Why a pool page is older than the drawing it was written from, or "" (feature 374 wave 126).
fn stale_page(page: &Path, root: &Path) -> String {
    let svg = page.with_extension("svg");
    let mtime = |p: &Path| std::fs::metadata(p).and_then(|m| m.modified()).ok();
    let (Some(s), Some(h)) = (mtime(&svg), mtime(page)) else {
        return String::new();
    };
    if svg.is_file() && s > h + Duration::from_secs(1) {
        let folder = page.parent().unwrap_or(page);
        return format!(
            "{} is older than {} - its crop would show the drawing before the edit; regenerate it first: make map MAP={}",
            page.file_name().unwrap_or_default().to_string_lossy(),
            svg.file_name().unwrap_or_default().to_string_lossy(),
            relative(folder, root)
        );
    }
    String::new()
}

fn file_name(p: &Path) -> String {
    p.file_name()
        .map_or_else(String::new, |n| n.to_string_lossy().into_owned())
}

/// The pool page that draws the kind, its crop and the kinds a click in it opens, or why there is no crop (plan D13).
fn glyph_part(
    root: &Path,
    m: &Modal,
    now: &[Modal],
    put: &mut Put,
    grep_targets: &mut Vec<String>,
) -> Result<(), Fail> {
    let page = pool_page_with(root, &m.key, m.uid().starts_with("sheet/"));
    if let Some(p) = &page {
        let why = stale_page(p, root);
        if !why.is_empty() {
            return Err(format!("modal-bundle: {why}"));
        }
    }
    let crop = put.out.join("glyph.png");
    let shape = page
        .as_ref()
        .map_or_else(String::new, |p| drawn_geometry(p, &m.key));
    let cropped = match &page {
        Some(p) => glyph_crop(root, p, &m.key, &crop)?,
        None => false,
    };
    if let (Some(p), true) = (&page, cropped) {
        grep_targets.push("glyph.png".to_owned());
        let kinds_file = PathBuf::from(format!("{}.kinds", shown(&crop)));
        let kinds: Vec<String> = if kinds_file.is_file() {
            py_lines(&read_text(&kinds_file)?)
                .into_iter()
                .filter(|k| !k.is_empty())
                .map(str::to_owned)
                .collect()
        } else {
            Vec::new()
        };
        let _ = std::fs::remove_file(&kinds_file);
        let clicks = kinds.iter().fold(String::new(), |mut acc, k| {
            let _ = write!(
                acc,
                "
- `{k}` opens {}",
                click_target(now, k, m)
            );
            acc
        });
        let listing = if clicks.is_empty() {
            String::new()
        } else {
            format!("\nThe kinds with a part in the crop - a click on each opens its own pop-up:{clicks}\n")
        };
        let origin = relative(p, root);
        put.put("glyph.txt", &format!("glyph.png beside this MANIFEST: the kind `{}` as drawn on `{origin}`, zoomed until its first glyph is about 200 px across; Read it as an image.\n{listing}{shape}", m.key), &origin, "where the crop came from - Read glyph.png")?;
    } else {
        let why = page.as_ref().map_or_else(
            || format!("the kind `{}` is drawn on no pool page", m.key),
            |p| {
                format!(
                    "the browser could not crop it from `{}` (the kind IS drawn there)",
                    relative(p, root)
                )
            },
        );
        put.put("glyph.txt", &format!("no crop: {why} - judge from the drawing pages, the claims and the geometry below, and say so.\n{shape}"), "scripts/record/modal_bundle.py", "why there is no crop, and the drawn geometry")?;
    }
    Ok(())
}

/// What `modal-depiction` reads (plan D13), put beside the MANIFEST. `now` is the bundle's own reading of the pop-ups, which a click in
/// the crop is told to: read again here it cost the bundle a merge base, a listing and a batch read, twice the work for the same pop-ups
/// (feature 449 T167).
///
/// # Errors
///
/// Where what it reads, writes or runs fails: the error says which and why.
pub fn parts(
    root: &Path,
    m: &Modal,
    now: &[Modal],
    put: &mut Put,
    grep_targets: &mut Vec<String>,
) -> Result<(), Fail> {
    for f in modals::followed(root, &m.drawing_files()) {
        let p = root.join(&f);
        if p.is_file() {
            let text = read_text(&p)?;
            put.put(&format!("drawing/{}", file_name(&p)), &text, &f, LISTED)?;
        }
    }
    let cands = drawing_candidates(root, m)?;
    for f in &cands {
        let p = root.join(f);
        put.put(&format!("drawing/{}", file_name(&p)), &read_text(&p)?, f, "CANDIDATE - NOT on the modal's Drawing: list, but its kind's (beside an Entry question, or listed before this change): is it owed a link?")?;
    }
    let note = knobs_note(&tree_of(root), &m.doc)?;
    if !note.is_empty() {
        put.put("knobs.md", &note, "l7r/diagram/knobs.json", "which maps draw what the modal's conditions name: each knob's forms, typing rule and engine lines - read it before ruling on a conditional link")?;
    }
    let rows = claims_citing(root, &[m.drawing_files(), cands].concat())?;
    let body = if rows.is_empty() {
        "(none)".to_owned()
    } else {
        rows.join("\n")
    };
    put.put("claims.md", &format!("# The engine's research claims citing these drawing pages (verdict | unit | note)\n\n{body}\n"), CLAIMS_INDEX, "the code's own account of how it draws the kind - a DRIFTED row is a variety the record names and the code does not draw")?;
    glyph_part(root, m, now, put, grep_targets)
}

#[cfg(test)]
mod tests;
