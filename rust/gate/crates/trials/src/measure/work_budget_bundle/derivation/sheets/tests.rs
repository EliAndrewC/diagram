//! A Mode A derivation's form (feature 449 T201): sized by the pool sheets, its px at a stated scale, its scopes per query - and a
//! hamlet derivation held to exactly its own form.

use super::super::form_problems;
use super::{pool_sheets, reference_problems, sheet_budget, sizing, SheetBudget};

/// T198's caption-placer derivation, judged SOUND by the work-budget agent, with its form lines (`Sizes:`, `Scale:`, `Keeps:`).
const T198: &str = include_str!("T198-placer.md");

/// A pool-sheet derivation every check passes.
const POOL: &str = "# Derivation - a Mode A stage

## Contract
- Sizes: pool sheets: alpha-sheet, beta-sheet.
- Scale: 3 px = 1 ft
- Reads: the sheet
- Writes: the seats
- Keeps: the rules of the record

## The count, factor by factor
| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | N = 10, 20 (30) | the captions | 10 to 20 |
| queries | per item | 2 | the seats | 2 |
| cells per query | per query | 3 | a 48 px cell | 3 |
| entries per cell | per cell | 4 | the density | 4 |
| slack | per item, on the search | 1.5 | caption order | 1.5 |

## Cheaper algorithms considered
- sweep: not used
- grid or spatial index: used - the grid
- priority queue: not used
- incremental update: not used
- memoizing what a scan does not change: not used

## Indexes
- Grid: cells of c = 48 px over the sheet
- Cells a query reads: (1 + w / c)(1 + h / c)

## Totals
- at alpha-sheet: 10 x 2 x 3 x 4 = 240
- at beta-sheet: 20 x 2 x 3 x 4 = 480
- all sheets: 240 + 480 = 720
";

fn problems(text: &str) -> Vec<String> {
    form_problems(text).unwrap()
}

fn with(from: &str, to: &str) -> Vec<String> {
    assert!(POOL.contains(from), "{from}");
    problems(&POOL.replace(from, to))
}

#[test]
fn the_t198_placer_derivation_owes_nothing_of_its_form() {
    // red on the hamlet-only form: its `Keeps:` line, its per-query scopes, its Indexes read as grids in ft, its px, its Totals
    assert_eq!(problems(T198), Vec::<String>::new());
    assert_eq!(problems(POOL), Vec::<String>::new());
}

#[test]
fn the_sizes_line_switches_the_form() {
    assert_eq!(sizing("no line"), Ok(None));
    assert_eq!(sizing("- Sizes: households"), Ok(None));
    assert_eq!(
        sizing("- Sizes: pool sheets: a, b."),
        Ok(Some(vec!["a".to_owned(), "b".to_owned()]))
    );
    assert_eq!(
        pool_sheets(T198).unwrap(),
        [
            "county-magistracy-example",
            "hayakawa-magistracy",
            "ochiba-magistracy",
            "ochiba-roundtrip-test",
            "ubame-magistracy",
            "hoshigaoka-shrine"
        ]
    );
    assert_eq!(pool_sheets("- Sizes: acres"), None);
    // no sheet named: refused, and held to the hamlet's form
    assert_eq!(
        with(
            "- Sizes: pool sheets: alpha-sheet, beta-sheet.",
            "- Sizes: pool sheets"
        )[0],
        "`Sizes:` names each pool sheet: `- Sizes: pool sheets: <sheet>, <sheet>, ...`"
    );
    // a line that reads as neither is refused, and the derivation is then held to the hamlet's form
    let neither = with(
        "- Sizes: pool sheets: alpha-sheet, beta-sheet.",
        "- Sizes: acres",
    );
    assert_eq!(
        neither[0],
        "`Sizes:` names households (a hamlet stage) or pool sheets (a Mode A stage) - not `acres`"
    );
    assert!(neither.len() > 1);
}

#[test]
fn a_hamlet_derivation_keeps_its_own_form() {
    // T198's figures under households - no `Sizes:` line, or `Sizes: households` - are refused for every gap the hamlet form owes
    for sizes in ["", "- Sizes: households\n"] {
        let hamlet = T198.replace(
            "- Sizes: pool sheets: county-magistracy-example, hayakawa-magistracy, ochiba-magistracy, ochiba-roundtrip-test, ubame-magistracy, hoshigaoka-shrine\n",
            sizes,
        );
        let got = problems(&hamlet);
        for owed in [
            "`## Totals`: a line for 20 households",
            "`## Totals`: a line for 40 households",
            "`## Totals`: a line for 80 households",
            "`cells per query (S1)`: its scope is one of per item, over the run, once - not `per query`",
            "`slack`: its scope is one of per item, over the run, once - not `per item, on the search kinds`",
            "`## Indexes` - Cells a query reads: its cell size in ft (`cells of <N> ft`)",
            "`14 px`: a px figure with no ft beside it - write its conversion, `14 px (<N> ft)`",
        ] {
            assert!(got.contains(&owed.to_owned()), "{sizes:?} {owed}\n{got:#?}");
        }
    }
    // a hamlet's `Scale:` line excuses no px
    let base = super::super::super::tests::BASE.to_owned();
    assert_eq!(
        problems(&(base + "- Scale: 3 px = 1 ft\na 40 px gap\n")),
        ["`40 px`: a px figure with no ft beside it - write its conversion, `40 px (<N> ft)`"]
    );
}

#[test]
fn a_scope_per_step_names_a_step_counted_per_item() {
    assert_eq!(
        with("| per query |", "| per run |"),
        [
            "`cells per query`: its scope is one of per item, over the run, once, or per <a step another row's factor names and counts per item> - not `per run`",
            // counted per cell, and its cells now per nothing
            "`entries per cell`: its scope is one of per item, over the run, once, or per <a step another row's factor names and counts per item> - not `per cell`",
        ]
    );
    // a step no other row counts, or a scope with no step (and the row counted per its cells after it)
    assert_eq!(with("| per query |", "| per strip |").len(), 2);
    assert_eq!(with("| per query |", "| per 12 |").len(), 2);
    assert_eq!(with("| per query |", "| each |").len(), 2);
    // two rows naming each other resolve to nothing
    assert_eq!(
        with("| queries | per item |", "| queries | per cell |").len(),
        3
    );
    // a scope qualified by a comma
    assert!(with("| per item, on the search |", "| once, at the build |").is_empty());
    assert!(with("| per item, on the search |", "| per items |").is_empty());
    // plurals fold: `per entry` is counted by `entries per cell`; a word in `ss` keeps its s
    assert!(with(
        "| slack | per item, on the search |",
        "| slack | per entry |"
    )
    .is_empty());
    assert_eq!(
        with(
            "| slack | per item, on the search |",
            "| slack | per class |"
        )
        .len(),
        1
    );
}

#[test]
fn a_grid_states_its_cell_and_its_density_and_px_its_scale() {
    assert_eq!(
        with("- Grid: cells of c = 48 px over the sheet\n", ""),
        ["an `## Indexes` section with a line for each grid the derivation uses - `- <name> grid: cells of <N> ft` (or px at the stated scale)"]
    );
    assert_eq!(
        with("cells of c = 48 px", "cells everywhere"),
        ["`## Indexes` - Grid: its cell size (`cells of <N> ft`, or px at the stated scale)"]
    );
    assert!(with("cells of c = 48 px", "cells of 16 ft").is_empty());
    assert_eq!(
        with("| entries per cell | per cell |", "| reads per cell | per cell |"),
        ["`## The count, factor by factor`: a row counting the entries a grid cell holds - a pool sheet's density, measured on each sheet"]
    );
    // two grids: each its own cells row
    assert_eq!(
        with("- Cells a query reads:", "- Second grid: cells of 9 ft\n- Cells a query reads:"),
        [
            "`## The count, factor by factor`: a row counting Grid's cells - its factor naming `Grid` and its cells",
            "`## The count, factor by factor`: a row counting Second grid's cells - its factor naming `Second grid` and its cells",
        ]
    );
    // px with no scale owe their ft; with ft beside them they pass
    assert_eq!(
        with("- Scale: 3 px = 1 ft\n", ""),
        [
            "`48 px`: a px figure with no ft beside it and no `- Scale: <N> px = <M> ft` line - state the sheets' scale once, or write `48 px (<N> ft)`",
            "`48 px`: a px figure with no ft beside it and no `- Scale: <N> px = <M> ft` line - state the sheets' scale once, or write `48 px (<N> ft)`",
        ]
    );
    assert!(problems(
        &POOL
            .replace("- Scale: 3 px = 1 ft\n", "")
            .replace("48 px", "48 px (16 ft)")
    )
    .is_empty());
}

#[test]
fn the_totals_are_one_line_a_sheet_and_their_sum() {
    assert_eq!(
        with("## Totals", "## Sums"),
        ["a `## Totals` section: one line per pool sheet, `- at <sheet>: <expression> = <value>`, and one for them all, `- all sheets: <expression> = <value>`"]
    );
    assert_eq!(
        with("- at beta-sheet: 20 x 2 x 3 x 4 = 480\n", ""),
        ["`## Totals`: a line for the sheet beta-sheet"]
    );
    assert_eq!(
        with("- at beta-sheet:", "- at gamma-sheet:"),
        [
            "`## Totals` at gamma-sheet: no sheet the `Sizes:` line names",
            "`## Totals`: a line for the sheet beta-sheet",
        ]
    );
    assert_eq!(
        with("= 240\n", "= 241\n"),
        [
            "`## Totals` at alpha-sheet: `10 x 2 x 3 x 4` is 240, not 241",
            "`## Totals` for all sheets: alpha-sheet's total 241 is not in the expression - the sum holds every sheet's line",
            "`## Totals` for all sheets: 720 is not the sheets' sum, 721",
        ]
    );
    assert_eq!(
        with("10 x 2 x 3 x 4 = 240", "ten = 240"),
        ["`## Totals` at alpha-sheet: `ten` is not arithmetic on the table's figures (digits, + - x / and brackets)"]
    );
    assert_eq!(
        with("- all sheets: 240 + 480 = 720\n", ""),
        ["`## Totals`: a line for the sheets together, `- all sheets: <expression> = <value>`"]
    );
    assert_eq!(
        with("- all sheets: 240 + 480 = 720", "- all sheets: all = 720"),
        ["`## Totals` for all sheets: `all` is not arithmetic on the table's figures (digits, + - x / and brackets)"]
    );
    assert_eq!(
        with("240 + 480 = 720", "240 + 480 + 1 = 721"),
        ["`## Totals` for all sheets: 721 is not the sheets' sum, 720"]
    );
    assert_eq!(
        with("240 + 480 = 720", "240 + 240 + 240 = 720"),
        ["`## Totals` for all sheets: beta-sheet's total 480 is not in the expression - the sum holds every sheet's line"]
    );
    // the other ways to name the sum
    assert!(with("- all sheets:", "- the two sheets:").is_empty());
    assert!(with("- all sheets:", "- all the sheets:").is_empty());
    assert_eq!(
        with("N = 10, 20 (30)", "N = 10"),
        ["`items`: its value gives each sheet's count, in the `Sizes:` line's order (`N = <n>, <n>, ...`, 2 of them)"]
    );
    // what Python's arithmetic raised, raised
    for bad in ["1 / 0 = 240", "10 x 2 x 3 x 4 = ,"] {
        assert!(form_problems(&POOL.replace("10 x 2 x 3 x 4 = 240", bad)).is_err());
    }
    // a value that is no figure is float()'s ValueError
    assert_eq!(
        super::line("at x", "1", ",", &mut Vec::new()),
        Err("ValueError: cannot parse float from empty string".to_owned())
    );
    // a value past a float is round()'s OverflowError
    assert!(super::line("at x", "1", &"9".repeat(400), &mut Vec::new()).is_err());
}

#[test]
fn the_reference_is_asked_of_the_sheets_together() {
    let big = POOL
        .replace("N = 10, 20 (30)", "N = 1, 1")
        .replace("= 720", "= 9000")
        .replace("240 + 480", "240 + 480 + 8280");
    assert_eq!(reference_problems(&big, &["alpha-sheet".to_owned(), "beta-sheet".to_owned()]), [
        "the cost per thing over the sheets, 4,500 (9000 over 2 items), passes the reference's 4,000 (rubric S8) - count the typical case, or name why: `- reason above the reference: <why>`",
        "the cost per thing over the sheets, 4,500, passes the reference's 4,000 - name the bound that stops the search before it visits the whole set, or why none can (rubric S9): `- pruning: <the bound, or why none applies>`",
    ]);
    let names = ["alpha-sheet".to_owned(), "beta-sheet".to_owned()];
    assert!(reference_problems(
        &(big.clone() + "- reason above the reference: x\n- pruning: y\n"),
        &names
    )
    .is_empty());
    assert!(reference_problems(&big.replace("N = 1, 1", "N = 0, 0"), &names).is_empty());
    assert!(reference_problems(&big.replace("- all sheets", "- sum"), &names).is_empty());
    assert!(reference_problems(&big.replace("= 9000", "= ,"), &names).is_empty());
    assert!(reference_problems(POOL, &names).is_empty());
}

#[test]
fn a_budget_is_read_off_the_totals_per_sheet() {
    assert_eq!(
        sheet_budget(POOL),
        Some(SheetBudget {
            sheets: vec![
                ("alpha-sheet".to_owned(), 240.0, 10.0),
                ("beta-sheet".to_owned(), 480.0, 20.0)
            ],
            all: 720.0
        })
    );
    let t198 = sheet_budget(T198).unwrap();
    assert!((t198.all - 97983.0).abs() < 0.5);
    assert_eq!(
        t198.sheets[5],
        ("hoshigaoka-shrine".to_owned(), 1271.0, 9.0)
    );
    assert_eq!(sheet_budget(super::super::super::tests::BASE), None);
    assert_eq!(
        sheet_budget(&POOL.replace("- at beta-sheet:", "- at gamma:")),
        None
    );
    assert_eq!(sheet_budget(&POOL.replace("- all sheets:", "- sum:")), None);
    assert_eq!(sheet_budget(&POOL.replace("= 480", "= ,")), None);
    assert_eq!(sheet_budget(&POOL.replace("= 720", "= ,")), None);
    assert_eq!(
        sheet_budget(&POOL.replace("N = 10, 20 (30)", "N = 10")),
        None
    );
    assert_eq!(sheet_budget(&POOL.replace("## Totals", "## Sums")), None);
}
