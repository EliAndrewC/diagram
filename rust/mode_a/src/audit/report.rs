//! The printed report and the command (feature 449 T175, `pack_audit/report.py` whole): the packing figures - coverage, the vacant
//! rectangles, the per-region density, the aligned gaps, the tubs and the gate openings - and then every registered check in registry
//! order, its findings or OK ([`check_lines`]); [`main`] prints it for each sheet named, as `make pack-audit` runs it.
//!
//! Research:
//!     the audit's report - NONE: the measures and the checks' findings printed in order, deciding nothing about a building

use std::fmt::Write as _;
use std::path::{Component, Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_core::Reply;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_shared::py_text::strip;

use super::checks::{
    aligned_gaps, fire_water_adrift, gap_tag, main_gate_passage_ft, tubs_in_buildings,
    wall_openings, TUB_BLDG_MIN_PX,
};
use super::onmap::{read_notes, read_on_map, OnMap};
use super::registry::{run_checks, Context};
use crate::compound::TUB_MAX_GAP_FT;
use crate::grids::{
    grids, perimeter_hugging_pct, region_density, top_vacant_rects, DENSITY_TILES, FTPX,
    HUG_DEPTH_FT, VACANT_DEPTH_FT, VACANT_MIN_SQFT,
};
use crate::parse::{parse_svg, ParsedPlan};
use crate::py::{fixed, grouped};
use crate::types::{by_tier, tiers, BuildingType};

/// How many vacant rectangles the report lists (its call's `n=4`).
pub const REPORT_VACANT_N: usize = 4;

/// Python's `a / b` of two counts, a `ZeroDivisionError` where `b` is 0.
#[expect(
    clippy::cast_precision_loss,
    reason = "a grid's cell counts, far inside f64's integers"
)]
fn share(a: usize, b: usize) -> Result<f64, Error> {
    if b == 0 {
        return Err(Error::new("ZeroDivisionError", "division by zero"));
    }
    Ok(a as f64 / b as f64)
}

/// The human-readable packing report (pure, as the CLI prints it): `text` is the sheet's source, `tier` its declared type (None: the shared
/// layer only), `btype` and `form` what the program checks read (feature 254), `tree` where the declaration and a manifest are read.
///
/// # Errors
/// A measure or a check raised, as the Python's did.
#[expect(
    clippy::too_many_arguments,
    reason = "the Python's keyword arguments, and the tree the Python found by its package's place"
)]
pub fn format_report(
    plan: &ParsedPlan,
    cell: usize,
    text: &str,
    tier: Option<&str>,
    btype: Option<&BuildingType>,
    form: Option<&str>,
    on_map: Option<&OnMap>,
    tree: &Path,
) -> Result<String, Error> {
    let g = grids(plan, cell)?;
    let (mut inside, mut built, mut openc, mut empty) = (0_usize, 0_usize, 0_usize, 0_usize);
    for gy in 0..g.h {
        for gx in 0..g.w {
            if !g.inside[gy][gx] {
                continue;
            }
            inside += 1;
            if g.building[gy][gx] {
                built += 1;
            } else if g.occ[gy][gx] {
                openc += 1;
            } else {
                empty += 1;
            }
        }
    }
    let (left, top, right, bottom) = plan.bounds()?;
    let hug = perimeter_hugging_pct(plan, HUG_DEPTH_FT, cell)?;
    #[expect(
        clippy::cast_precision_loss,
        reason = "a grid's cell count, far inside f64's integers"
    )]
    let sqft = (inside * cell * cell) as f64 / (FTPX * FTPX);
    let mut lines = vec![
        format!(
            "walled interior: {} x {} ft = {} sqft",
            fixed((right - left) / FTPX, 0),
            fixed((bottom - top) / FTPX, 0),
            grouped(sqft)
        ),
        format!(
            "building coverage: {}%  (a jin'ya runs ~30-42% built: Takayama's ~31% floor to the record's band, 0116)",
            fixed(share(100 * built, inside)?, 0)
        ),
        format!("purposeful open (garden/court/glyphs): {}%  (features)", fixed(share(100 * openc, inside)?, 0)),
        format!("bare open ground: {}%  (courts are open - not a defect alone)", fixed(share(100 * empty, inside)?, 0)),
        format!(
            "perimeter-hugging: {}% of building footprint within 25 ft of a wall  (high = buildings ring the courts)",
            fixed(100.0 * hug, 0)
        ),
        "top vacant rectangles (largest first - CENTRAL=courtyard/feature, PERIMETER=ring gap/slack):".to_owned(),
    ];
    let tv = top_vacant_rects(
        plan,
        REPORT_VACANT_N,
        cell,
        VACANT_MIN_SQFT,
        VACANT_DEPTH_FT,
    )?;
    if tv.is_empty() {
        lines.push("    (none above the floor area)".to_owned());
    }
    #[expect(
        clippy::cast_precision_loss,
        reason = "a rounded area, far inside f64's integers"
    )]
    lines.extend(tv.iter().map(|v| {
        format!(
            "    {} x {} ft = {} sqft [{}, {}] at svg({},{})",
            fixed(v.w_ft, 0),
            fixed(v.h_ft, 0),
            grouped(v.area_sqft as f64),
            v.orient(),
            v.zone,
            fixed(v.x, 0),
            fixed(v.y, 0)
        )
    }));
    lines.push(
        "per-region density (a large low-coverage tile = consolidation candidate):".to_owned(),
    );
    #[expect(
        clippy::cast_precision_loss,
        reason = "a rounded area, far inside f64's integers"
    )]
    lines.extend(
        region_density(plan, DENSITY_TILES.0, DENSITY_TILES.1, cell)?
            .iter()
            .map(|t| {
                format!(
                    "    tile[r{}c{}]: {}% built  ({} sqft interior)",
                    t.row,
                    t.col,
                    fixed(100.0 * t.coverage_pct, 0),
                    grouped(t.interior_sqft as f64)
                )
            }),
    );
    lines.extend(gaps_tubs_and_gates(plan));
    let ctx = Context::new(plan, text, btype, form, on_map, tree);
    lines.extend(check_lines(&ctx, tier)?);
    Ok(lines.join("\n"))
}

/// The report's gaps, tubs and gate openings, after its measures.
fn gaps_tubs_and_gates(plan: &ParsedPlan) -> Vec<String> {
    let mut lines = Vec::new();
    lines.push(
        "aligned building gaps 5-30 ft (kura fire-gap OK 6-10 ft; wooden >8 ft loose):".to_owned(),
    );
    let gaps = aligned_gaps(plan);
    if gaps.is_empty() {
        lines.push("    (none in the 5-30 ft range)".to_owned());
    }
    lines.extend(gaps.iter().take(12).map(|gp| {
        format!(
            "    {} ft  {}  at svg({},{})   {}",
            fixed(gp.ft, 1),
            gp.orient,
            fixed(gp.mx, 0),
            fixed(gp.my, 0),
            gap_tag(gp)
        )
    }));
    lines.push(format!(
        "fire-water tubs adrift (a gutter-fed tub must sit <={} ft from a building):",
        fixed(TUB_MAX_GAP_FT, 0)
    ));
    if plan.tubs.is_empty() {
        lines.push("    (no fire-water tubs in this plan)".to_owned());
    } else {
        let adrift = fire_water_adrift(plan);
        let intruding = tubs_in_buildings(plan, TUB_BLDG_MIN_PX);
        if adrift.is_empty() && intruding.is_empty() {
            lines.push(format!(
                "    (all {} tubs sit outside, clear of every building)",
                plan.tubs.len()
            ));
        }
        lines.extend(adrift.iter().map(|t| {
            format!(
                "    tub at svg({},{}) is {} ft from the nearest building - move it to a wall/eaves",
                fixed(t.x, 0),
                fixed(t.y, 0),
                fixed(t.gap_ft, 1)
            )
        }));
        lines.extend(intruding.iter().map(|t| {
            format!(
                "    TUB IN BUILDING: a fire-water tub at svg({},{}) reaches {} ft INTO a building - a tensuioke is gutter-fed and bucket-served, so move it OUT clear of the wall",
                fixed(t.x, 0),
                fixed(t.y, 0),
                fixed(t.into_ft, 1)
            )
        }));
    }
    lines.push(
        "GATE OPENINGS (compound wall, measured from the INK - a square cap eats 1.5 ft per end):"
            .to_owned(),
    );
    let openings = wall_openings(plan);
    if openings.is_empty() {
        lines.push("    (no openings found in the compound wall)".to_owned());
    }
    lines.extend(openings.iter().map(|o| {
        format!(
            "    {:>5} ft  at svg({},{})   compare with the width this opening's comment claims",
            fixed(o.ft, 1),
            fixed(o.x, 0),
            fixed(o.y, 0)
        )
    }));
    if let Some(passage) = main_gate_passage_ft(plan) {
        lines.push(format!(
            "    {:>5} ft  the MAIN GATE's passage, between its posts - the widest opening of all (docs/buildings.md checklist)",
            fixed(passage, 1)
        ));
    }
    lines
}

// `re.M`'s `$` is the end of any line (`pyre::py` reads `$` as the end of the text)
static FORM: LazyLock<Regex> = LazyLock::new(|| py(r"(?m)^\*\*Form\*\*:\s*([^\n]+?)\s*(?=\n|\z)"));

/// The `**Form**: ...` line of the sheet's notes file (`<stem>.notes.md` beside it), or None.
///
/// # Errors
/// The notes cannot be read.
pub fn read_form(svg_path: &str) -> Result<Option<String>, Error> {
    let Some(notes) = read_notes(svg_path)? else {
        return Ok(None);
    };
    Ok(FORM
        .captures(&notes)
        .ok()
        .flatten()
        .map(|m| strip(&m[1]).to_owned()))
}

/// The REGISTERED checks (feature 254): each applicable check in registry order, its findings or OK - the registry is the one list, so a
/// check the sweep runs is a check the report prints, with the same fix sentence.
///
/// # Errors
/// The declaration cannot be read, or a check raised.
pub fn check_lines(ctx: &Context, tier: Option<&str>) -> Result<Vec<String>, Error> {
    let layer = tier.map_or_else(
        || "shared layer only".to_owned(),
        |t| format!("shared layer + {t}"),
    );
    let mut lines = vec![format!("CHECKS ({layer}):")];
    for (ch, found) in run_checks(ctx, tier)? {
        if found.is_empty() {
            let why = (ch.skipped)(ctx);
            lines.push(format!(
                "    {}: {}",
                ch.name,
                why.map_or_else(|| "OK".to_owned(), |w| format!("skipped - {w}"))
            ));
            continue;
        }
        lines.extend(
            found
                .iter()
                .map(|f| format!("    {}: {f} - {}", ch.name.to_uppercase(), ch.fix)),
        );
    }
    Ok(lines)
}

/// `os.path.abspath`: joined to the working directory and normalized (`.` dropped, `..` climbing), links not followed.
fn abspath(path: &str) -> PathBuf {
    let joined = std::env::current_dir().unwrap_or_default().join(path);
    let mut out = PathBuf::new();
    for c in joined.components() {
        match c {
            Component::ParentDir => {
                if out.parent().is_some() {
                    out.pop();
                }
            }
            // `components()` has already dropped every `.` past the first, and the working directory leaves none first
            other => out.push(other),
        }
    }
    out
}

/// The sheet's type: its pool tier when the folder above its own is a declared one (feature 254).
fn tier_of(path: &str, tree: &Path) -> Result<Option<String>, Error> {
    let abs = abspath(path);
    let tier = abs
        .parent()
        .and_then(Path::parent)
        .and_then(Path::file_name)
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    Ok(tiers(tree)?.contains(&tier).then_some(tier))
}

/// One sheet's block of the command's output.
fn sheet(path: &str, tree: &Path, out: &mut String) -> Result<(), Error> {
    let text = l7r_gate_core::record::read_text(Path::new(path))
        .map_err(|e| crate::py::os_error(&e, path))?;
    let plan = parse_svg(&text)?;
    let tier = tier_of(path, tree)?;
    let _ = writeln!(out, "=== {} ===", path.rsplit('/').next().unwrap_or(path));
    // the report's arguments, read after the header as the Python's call read them
    let btype = match &tier {
        Some(t) => by_tier(t, tree)?,
        None => None,
    };
    let form = read_form(path)?;
    let on_map = read_on_map(path)?;
    let report = format_report(
        &plan,
        crate::grids::CELL,
        &text,
        tier.as_deref(),
        btype.as_ref(),
        form.as_deref(),
        on_map.as_ref(),
        tree,
    )?;
    let _ = writeln!(out, "{report}\n");
    Ok(())
}

/// The command: the report of each sheet named, a blank line after each; no sheet is the usage line and exit 2; an uncaught error ends
/// the run with its traceback's last line and exit 1, what was printed before it kept.
#[must_use]
pub fn main(args: &[String], tree: &Path) -> Reply {
    if args.is_empty() {
        return Reply {
            stdout: String::new(),
            stderr: "usage: make pack-audit ARGS=<compound.svg>\n".to_owned(),
            code: 2,
        };
    }
    let mut out = String::new();
    for path in args {
        if let Err(e) = sheet(path, tree, &mut out) {
            return Reply {
                stdout: out,
                stderr: crate::py::uncaught(&e),
                code: 1,
            };
        }
    }
    Reply {
        stdout: out,
        stderr: String::new(),
        code: 0,
    }
}
