//! THE POOL SWEEP (feature 449 T211; feature 254 FR-004/FR-005, feature 294 B15c and B24): every Mode A sheet in the live pool through
//! every registered check its declared tier owes, written fresh against the Rust audit when the pytest sweep and its stale-sheet helper
//! were deleted - the helper keyed a generated sheet's freshness on the Python engine's files alone, so a Rust generator edit left the
//! sheet it read stale (a defect retired with it). A hand sheet is read as tracked; a declared generated exception is composed in process
//! from its `<map>.compound.json` spec and its captions placed, as `l7r-mode-a compound` writes it, so no sheet on disk is ever read in
//! its place. A failure names the sheet, the check and the compliant fix, in that order; each rides in the compared
//! value, so a failure prints it and a pass reaches every line.
//!
//! The sweep also asks the census's pool checks (`census/pool_check.rs`, moved here from the parse's lockstep, which T212 deleted),
//! the notes' typed counts against the sheets held here, and every census block against its manifest; and the crate's end-to-end test,
//! from the same lockstep: the pool's pages and the country shrine drawn whole.
//!
//! Research:
//!     the Mode A pool sweep - NONE: the pool's sheets put through the registered checks, deciding nothing about a building

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

use l7r_gate_research::Error;

use crate::audit::onmap::read_on_map;
use crate::audit::registry::{checks_for, run_checks, Check, Context, CHECKS};
use crate::audit::report::read_form;
use crate::types::{by_tier, tiers};

fn tree() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

/// One pool sheet: its tier, its name, its path in the pool (its notes beside it), the text the checks read, and whether it was composed.
struct Pooled {
    tier: String,
    stem: String,
    svg: PathBuf,
    text: String,
    generated: bool,
}

const NO_SVG: &str =
    "no svg and not a declared generated exception - draw it, or declare it generated";

/// Every folder under each declared tier's pool folder, from the one pool walk (feature 449 T220), its sheet read or composed once for
/// every test here.
fn pool() -> &'static [Pooled] {
    static POOL: OnceLock<Vec<Pooled>> = OnceLock::new();
    POOL.get_or_init(|| {
        let tree = tree();
        let walked = l7r_gate_pool::walk(&tree);
        let mut out = Vec::new();
        for tier in tiers(&tree).unwrap() {
            let generated = by_tier(&tier, &tree)
                .unwrap()
                .map(|t| t.generated_exceptions)
                .unwrap_or_default();
            // a declared tier with no folder yet has no sheet
            for map in walked
                .in_tree(l7r_gate_pool::LIVE)
                .filter(|m| m.tier == tier)
            {
                let stem = map.name.clone();
                let svg = map.file(".svg");
                let composed = generated.contains(&stem);
                let spec = map.file(".compound.json");
                let text = if composed {
                    compose(&tree, &spec).unwrap()
                } else {
                    let read = l7r_gate_core::record::read_text(&svg).ok();
                    assert_eq!((&stem, read.is_some(), NO_SVG), (&stem, true, NO_SVG));
                    read.unwrap()
                };
                out.push(Pooled {
                    tier: tier.clone(),
                    stem,
                    svg,
                    text,
                    generated: composed,
                });
            }
        }
        out
    })
}

/// A generated exception's sheet as `l7r-mode-a compound` writes it: composed from its spec, its captions placed.
fn compose(tree: &Path, spec: &Path) -> Result<String, Error> {
    let (program, bands) = crate::compound::cli::load(tree, &spec.to_string_lossy())?;
    let (text, _) = crate::compound::cli::compose(&program, &bands)?;
    crate::caption_place::placed(&text)
}

/// A sheet's context: `text` read as the sheet at `svg` (its notes' form and map declaration beside it) under `tier`, handed to `f`.
fn with_context<T>(
    tree: &Path,
    tier: &str,
    svg: &Path,
    text: &str,
    f: impl FnOnce(&Context) -> Result<T, Error>,
) -> Result<T, Error> {
    let shown = svg.to_string_lossy();
    let plan = crate::parse::parse_svg(text)?;
    let btype = by_tier(tier, tree)?;
    let (form, on_map) = (read_form(&shown)?, read_on_map(&shown)?);
    let ctx = Context::new(
        &plan,
        text,
        btype.as_ref(),
        form.as_deref(),
        on_map.as_ref(),
        tree,
    );
    f(&ctx)
}

/// Every check `tier` owes, run on the sheet: each finding as `<check>: <finding> - fix: <fix>`. Empty is a pass.
fn judge(tree: &Path, tier: &str, svg: &Path, text: &str) -> Result<Vec<String>, Error> {
    with_context(tree, tier, svg, text, |ctx| {
        Ok(run_checks(ctx, Some(tier))?
            .into_iter()
            .flat_map(|(ch, found)| {
                found
                    .into_iter()
                    .map(move |f| format!("{}: {f} - fix: {}", ch.name, ch.fix))
            })
            .collect())
    })
}

#[test]
fn every_pool_sheet_passes_its_tiers_checks() {
    let tree = tree();
    let got: Vec<(&str, Result<Vec<String>, Error>)> = pool()
        .iter()
        .map(|s| (s.stem.as_str(), judge(&tree, &s.tier, &s.svg, &s.text)))
        .collect();
    let want: Vec<(&str, Result<Vec<String>, Error>)> = pool()
        .iter()
        .map(|s| (s.stem.as_str(), Ok(Vec::new())))
        .collect();
    assert_eq!(got, want);
    // non-vacuity: each tier swept runs checks of its own beyond the shared layer, and both generated sheets were composed
    let swept: BTreeSet<&str> = pool().iter().map(|s| s.tier.as_str()).collect();
    let own: Vec<bool> = swept
        .iter()
        .map(|t| {
            checks_for(Some(t), &tree)
                .unwrap()
                .iter()
                .any(|c| !c.shared)
        })
        .collect();
    assert_eq!(own, vec![true; swept.len()]);
    assert_eq!(pool().iter().filter(|s| s.generated).count(), 2);
}

/// The sweep's judge goes red on a broken sheet: a pool sheet with its scale note changed fails the check that reads it.
#[test]
fn a_pool_sheet_that_breaks_a_check_fails_the_sweep() {
    let tree = tree();
    let sheet = pool()
        .iter()
        .find(|s| s.stem == "ubame-magistracy")
        .unwrap();
    let broken = sheet.text.replace("3 px = 1 ft", "4 px = 1 ft");
    assert_ne!(broken, sheet.text);
    let found = judge(&tree, &sheet.tier, &sheet.svg, &broken).unwrap();
    let fired: Vec<bool> = found
        .iter()
        .map(|f| f.starts_with("scale_bar_present: "))
        .collect();
    assert!(fired.contains(&true), "{found:?}");
}

/// The tier a red fixture is read under: that of the pool sheet it was cut from, whose place its name opens with.
fn fixture_tier(fixture: &str) -> String {
    let place = fixture.split('-').next().unwrap_or_default();
    let found: BTreeSet<&str> = pool()
        .iter()
        .filter(|s| s.stem.starts_with(&format!("{place}-")))
        .map(|s| s.tier.as_str())
        .collect();
    assert_eq!((fixture, found.len()), (fixture, 1));
    found.into_iter().next().unwrap().to_owned()
}

/// Whether the tier of the red fixture `fixture` owes `ch`, and whether `ch` FIRES on it.
fn fires(tree: &Path, ch: &Check, fixture: &str) -> (bool, Result<bool, Error>) {
    let svg = tree.join("tests/fixtures").join(fixture);
    let text = l7r_gate_core::record::read_text(&svg).unwrap();
    let tier = fixture_tier(fixture);
    let owed = checks_for(Some(&tier), tree)
        .unwrap()
        .iter()
        .any(|c| c.name == ch.name);
    let fired = with_context(tree, &tier, &svg, &text, |ctx| {
        Ok(!(ch.run)(ctx)?.is_empty())
    });
    (owed, fired)
}

/// A check's name, its red fixture, whether that fixture's tier owes it and whether it fired there.
type Fired<'a> = (&'a str, &'a str, (bool, Result<bool, Error>));

/// Every check's red fixtures: its registry row's, then the registry's `MORE_FIXTURES`.
fn red_fixtures() -> Vec<(&'static Check, &'static str)> {
    let more = crate::audit::registry::MORE_FIXTURES
        .iter()
        .map(|(name, fixture)| {
            let ch = CHECKS.iter().find(|c| c.name == *name);
            assert!(ch.is_some(), "{name}: no registered check of that name");
            (ch.unwrap(), *fixture)
        });
    CHECKS
        .iter()
        .map(|ch| (ch, ch.fixture))
        .chain(more)
        .collect()
}

/// Every registered check FIRES on each of its red fixtures under `tests/fixtures/`, read under the tier of the pool sheet it was cut
/// from, and that tier owes the check.
#[test]
fn every_check_fires_on_its_red_fixture() {
    let tree = tree();
    let reds = red_fixtures();
    let got: Vec<Fired<'_>> = reds
        .iter()
        .map(|(ch, fixture)| (ch.name, *fixture, fires(&tree, ch, fixture)))
        .collect();
    let want: Vec<Fired<'_>> = reds
        .iter()
        .map(|(ch, fixture)| (ch.name, *fixture, (true, Ok(true))))
        .collect();
    assert_eq!(got, want);
}

/// Every `-red.svg` under `tests/fixtures/` is a red fixture of some check (T211 found three no row named; a fixture nothing runs proves
/// nothing).
#[test]
fn every_red_fixture_is_some_check_s() {
    const FIX: &str = "name it as a check's red fixture (its registry row, or the registry's `MORE_FIXTURES`), or delete it";
    let named: BTreeSet<&str> = red_fixtures().into_iter().map(|(_, f)| f).collect();
    let mut orphans: Vec<String> = std::fs::read_dir(tree().join("tests/fixtures"))
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().into_owned())
        .filter(|n| n.ends_with("-red.svg") && !named.contains(n.as_str()))
        .collect();
    orphans.sort();
    assert_eq!((orphans, FIX), (Vec::<String>::new(), FIX));
}

const UNTABLED: &str = "tagged kinds no size-table row carries (a kind on a caption alone) - tag the drawn element with the kind, or the caption with the kind it names";

/// Feature 294 B15c: every kind a pool sheet tags is sized by a size-table row, so `size-audit` enumerates every sized feature from it.
#[test]
fn every_tagged_kind_on_a_pool_sheet_has_a_size_row() {
    let got: Vec<(&str, Vec<String>, &str)> = pool()
        .iter()
        .map(|s| {
            let missing = crate::size_marks::untabled_kinds(&s.text).unwrap();
            (s.stem.as_str(), missing, UNTABLED)
        })
        .collect();
    let want: Vec<(&str, Vec<String>, &str)> = pool()
        .iter()
        .map(|s| (s.stem.as_str(), Vec::new(), UNTABLED))
        .collect();
    assert_eq!(got, want);
}

/// Feature 294 B24: where a map records a subject of the sheet's tier at its place, the notes carry the `**On map**:` declaration (so
/// the map check holds the sheet to the map) or opt out of it in so many words.
#[test]
fn a_sheet_whose_place_a_map_records_declares_it() {
    let tree = tree();
    let fix = format!(
        "declare it (`{}`) or opt out (`{}`)",
        crate::audit::onmap::GRAMMAR,
        crate::audit::onmap::OPT_OUT
    );
    let got: Vec<(&str, Vec<String>, bool, &str)> = pool()
        .iter()
        .map(|s| {
            let maps = crate::audit::mapmatch::maps_recording(&s.stem, &s.tier, &tree).unwrap();
            let notes = crate::audit::onmap::read_notes(&s.svg.to_string_lossy()).unwrap();
            let held = maps.is_empty() || crate::audit::onmap::declares(&notes.unwrap_or_default());
            (s.stem.as_str(), maps, held, fix.as_str())
        })
        .collect();
    let held: Vec<bool> = got.iter().map(|g| g.2).collect();
    assert_eq!(held, vec![true; got.len()], "{got:?}");
}

/// Non-vacuity of the rule above: the two sheets whose places a map records are found, the two no map records are not.
#[test]
fn the_map_record_rule_finds_the_sheets_it_is_for() {
    let tree = tree();
    let found =
        |stem: &str, tier: &str| crate::audit::mapmatch::maps_recording(stem, tier, &tree).unwrap();
    let shrine = found("hoshigaoka-shrine", "country-shrines");
    assert_eq!(
        shrine,
        ["legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json"]
    );
    let ubame = found("ubame-magistracy", "magistracies");
    assert_eq!(ubame, ["legacy-hand-authored-pool/towns/ubame/ubame.json"]);
    let none = [
        found("ochiba-magistracy", "magistracies"),
        found("hayakawa-magistracy", "magistracies"),
    ];
    assert_eq!(none, [Vec::<String>::new(), Vec::new()]);
}

/// A declared tier with a pool folder is swept; one with no folder yet is the exemplar's to fill. Both tiers declared today have sheets.
#[test]
fn the_sweep_covers_every_declared_tier_that_has_a_folder() {
    let tree = tree();
    let swept: BTreeSet<&str> = pool().iter().map(|s| s.tier.as_str()).collect();
    let walked = l7r_gate_pool::walk(&tree);
    let unswept: Vec<String> = tiers(&tree)
        .unwrap()
        .into_iter()
        .filter(|t| {
            walked.in_tree(l7r_gate_pool::LIVE).any(|m| &m.tier == t) && !swept.contains(t.as_str())
        })
        .collect();
    assert_eq!(unswept, Vec::<String>::new());
    assert!(swept.contains("magistracies") && swept.contains("country-shrines"));
}

/// The emitter, not only its ring tracer (`compound/gen_tests.rs`): the round-trip's three corridor pieces keep a fill each, tagged for
/// the checks, with no outline of their own; one dotted ring round them, one subpath; one caption.
#[test]
fn the_round_trips_corridor_is_drawn_as_one_passage() {
    let svg = &pool()
        .iter()
        .find(|s| s.stem == "ochiba-roundtrip-test")
        .unwrap()
        .text;
    let all = |re: &str| -> Vec<String> {
        l7r_shared::regex::build(re)
            .unwrap()
            .captures_iter(svg)
            .map_while(Result::ok)
            .map(|c| c.get(1).map_or("", |m| m.as_str()).to_owned())
            .collect()
    };
    let pieces = all(r#"(<rect [^>]*data-kind="residence corridor"[^>]*/>)"#);
    let unstroked = pieces
        .iter()
        .filter(|r| r.contains(r#"stroke="none""#))
        .count();
    assert_eq!((pieces.len(), unstroked), (3, 3), "{pieces:?}");
    assert_eq!(all(r#"<(\w+) [^>]*stroke-dasharray="1 2"[^>]*>"#), ["path"]);
    let ring = all(r#"<path d="([^"]*)"[^>]*stroke-dasharray="1 2""#);
    let subpaths: Vec<usize> = ring.iter().map(|d| d.matches('M').count()).collect();
    assert_eq!(subpaths, [1]);
    assert_eq!(svg.matches(">corridor</text>").count(), 1);
}

/// The census's pool checks (moved from the parse's lockstep): the notes' typed counts against the sheets held here, and every census
/// block the pool's notes carry against its manifest.
#[test]
fn the_pool_notes_type_what_their_sheets_draw_and_their_census_blocks_are_fresh() {
    let sheets: Vec<(&Path, &str)> = pool()
        .iter()
        .map(|s| (s.svg.as_path(), s.text.as_str()))
        .collect();
    crate::census::pool_check::every_pool_sheet_s_notes_type_the_counts_it_draws(&sheets);
    crate::census::pool_check::every_census_block_is_its_manifest_s(&tree());
}

/// FR-008's one end-to-end test (ask:449-T167-realtree): the page writer's cases that read the live tree, and each pool sheet on disk
/// with its page written, picture and id map drawn and census clean (`page::held::outcomes`, T150); and the country shrine drawn whole by
/// the command its generator runs (T151), a copy beside this test's world so the pool is untouched, the picture skipped - its census
/// clean, its placed text the placer's, the tracked sheet among the reads the generation cache is told of. The parse's lockstep held it
/// until T212 deleted that test with its Python.
#[test]
fn the_pages_and_the_country_shrine_are_drawn_end_to_end() {
    let tree = tree();
    let on_disk: Vec<PathBuf> = pool()
        .iter()
        .filter(|s| s.svg.is_file())
        .map(|s| s.svg.clone())
        .collect();
    assert!(on_disk.len() >= 4);
    let writer = crate::page::held::outcomes(&on_disk);
    let held = (writer.pages, writer.cases > 200, writer.refusals > 0);
    assert_eq!(held, (on_disk.len(), true, true));
    let dir = l7r_shared::tempdir::TempDir::new("mode-a-end-to-end");
    let shrine = dir.path().join("hoshigaoka-shrine.svg");
    let tracked = tree.join("pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg");
    std::fs::copy(&tracked, &shrine).unwrap();
    let skip = crate::raster::Host {
        vars: vec![("DIAGRAM_SKIP_RENDER".into(), "1".into())],
        ..Default::default()
    };
    let drawn_to = dir.path().join("shrine-placed.svg");
    let args = [&shrine, &drawn_to].map(|p| p.to_string_lossy().into_owned());
    let words = [args[0].clone(), "--placed".to_owned(), args[1].clone()];
    let r = {
        let _log = crate::reads::taker();
        crate::sheet::hand::main(&words, &tree, &skip)
    };
    assert_eq!((r.code, r.stderr.as_str()), (0, ""));
    assert!(r.stdout.contains(&format!("\"{}\"", args[0])));
    assert!(
        r.stdout.contains("/modals/sheet/torii.md\""),
        "{}",
        r.stdout
    );
    let drawn = std::fs::read_to_string(&drawn_to).unwrap();
    let text = std::fs::read_to_string(&tracked).unwrap();
    assert_eq!(drawn, crate::caption_place::placed(&text).unwrap());
    assert!(dir.path().join("hoshigaoka-shrine.html").is_file());
}
