//! A derivation's form, its totals' arithmetic and the reference's reasons, each refusal in the Python's words (feature 449 T134;
//! the same derivations its differential gave `work_budget_bundle.py`, 0 differing).
#![expect(
    clippy::float_cmp,
    reason = "figures Python computes exactly, compared as it compares them"
)]

use super::super::tests::BASE;
use super::{arith, fixed0, form_problems, int_commas, reference_problems, rounded, sizes};

fn problems(text: &str) -> Vec<String> {
    form_problems(text).unwrap()
}

fn with(from: &str, to: &str) -> Vec<String> {
    assert!(BASE.contains(from), "{from}");
    problems(&BASE.replace(from, to))
}

#[test]
fn the_totals_are_arithmetic_as_python_evaluates_it() {
    for (expr, want) in [
        ("10 + 5", 15.0),
        ("2*5 - -1", 11.0),
        ("(1 + 2) * 3", 9.0),
        ("1 / 4", 0.25),
        ("5. + .5", 5.5),
        ("00 + 1", 1.0),
        ("- (2)", -2.0),
    ] {
        assert_eq!(arith(expr).unwrap(), want, "{expr}");
    }
    for expr in [
        "10 ** 5",
        "10 // 5",
        "+10",
        "10 5",
        "10(5)",
        "(10)(5)",
        "()",
        "10 + 5.5.5",
        "10 +",
        "10 + 5 . 0",
        "1. 5",
        "007",
        "(1",
        "1)",
        "1/0",
        "",
        "1 2",
    ] {
        assert!(arith(expr).is_err(), "{expr}");
    }
    let huge_int = "9".repeat(400);
    // an integer past a float is float()'s OverflowError
    assert!(arith(&huge_int).is_err(),);
    assert_eq!(arith(&format!("{huge_int}.0")).unwrap(), f64::INFINITY);
    assert_eq!(arith(&format!("1/{huge_int}.0")).unwrap(), 0.0);
    assert!(rounded(f64::INFINITY).is_err());
    assert!(rounded(f64::NAN).is_err());
    assert_eq!(rounded(2.5).unwrap(), 2.0);
    assert_eq!(rounded(-0.4).unwrap(), 0.0);
    assert_eq!(int_commas(-1_234_567.0), "-1,234,567");
    assert_eq!(int_commas(-0.0), "0");
    assert_eq!(int_commas(1e21), "1,000,000,000,000,000,000,000");
    assert_eq!(fixed0(4_500.5), "4,500");
    assert_eq!(fixed0(-1_000.0), "-1,000");
}

#[test]
fn the_sizes_are_the_bounded_ns_or_the_standard_three() {
    assert_eq!(sizes("x"), [20, 40, 80]);
    assert_eq!(sizes("a bounded n: households 10-20"), [10, 20]);
    assert_eq!(sizes("A Bounded N, Households 20 to 80"), [20, 40, 80]);
    assert_eq!(sizes("a bounded n: households 30-50"), [20, 40, 80]);
    assert_eq!(
        sizes("a bounded n: households 10-99999999999999999999"),
        [10, 20, 40, 80]
    );
}

#[test]
fn a_whole_derivation_owes_nothing() {
    assert_eq!(problems(BASE), Vec::<String>::new());
    assert_eq!(
        problems(&BASE.replace('\n', "\r\n").replace("\r\n", "\n")),
        Vec::<String>::new()
    );
}

#[test]
fn each_part_of_the_form_is_owed() {
    assert_eq!(
        with(
            "- Reads: the field outline\n- Writes: the ink\n- Keeps: the rules of the record\n",
            ""
        ),
        [
            "`## Contract`: its `Reads:` line, filled",
            "`## Contract`: its `Writes:` line, filled",
            "`## Contract`: its `Keeps:` line, filled"
        ]
    );
    assert_eq!(with("| factor | scope |", "| factor | Scope2 |")[0], "the `## The count, factor by factor` table with the columns factor | scope | value | reason | worst case");
    assert_eq!(
        with(
            "| the grid's cells | over the run | 5 | each cell examined | 5 |",
            "| the grid's cells | over the run | 5 |"
        )[0],
        "`the grid's cells`: every column filled (scope, value, reason, worst case)"
    );
    assert_eq!(
        with("| each cell examined |", "| <why> |")[0],
        "`the grid's cells`: every column filled (scope, value, reason, worst case)"
    );
    assert_eq!(
        with(
            "| the grid's cells | over the run | 5 | each cell examined | 5 |",
            "|  | over the run | 5 | x | 5 |"
        )[0],
        "`a factor`: every column filled (scope, value, reason, worst case)"
    );
    assert_eq!(
        with("| over the run |", "| per run |"),
        ["`the grid's cells`: its scope is one of per item, over the run, once - not `per run`"]
    );
    assert!(with("| over the run |", "| Over The Run |").is_empty());
    let header_only = with("| items | per item | 10 at 20, 20 at 40, 40 at 80 | the things placed | the same |\n| the grid's cells | over the run | 5 | each cell examined | 5 |\n", "");
    assert!(header_only.contains(&"a row for each factor of the count".to_owned()),);
    assert_eq!(
        with("- priority queue: not used", "- priority queue:"),
        ["`## Cheaper algorithms considered`: a line for `priority queue` - used, or why not"]
    );
    assert!(with("- sweep:", "- Sweep :").is_empty());
    // every algorithm owed
    assert_eq!(
        with("## Cheaper algorithms considered", "## Others").len(),
        5,
    );
}

#[test]
fn every_index_is_its_own_row() {
    let indexes =
        "## Indexes\n- the grid: cells of 64 ft; densest 4, from a smallest side of 128 ft\n";
    assert_eq!(with(indexes, ""), ["an `## Indexes` section: one line per index the derivation uses - `- <name>: cells of <N> ft; densest <count>, from a smallest side of <S> ft`"]);
    assert_eq!(
        with("cells of 64 ft;", "cells of 64;"),
        ["`## Indexes` - the grid: its cell size in ft (`cells of <N> ft`)"]
    );
    assert_eq!(
        with("from a smallest side of 128 ft", "over 400 sq ft"),
        ["`## Indexes` - the grid: its densest case from a smallest side in ft, never an area"]
    );
    assert_eq!(with("| the grid's cells |", "| the grid's rows |"), [
        "`## The count, factor by factor`: a row counting the index cells examined - the derivation says a grid or spatial index is used",
        "`## The count, factor by factor`: a row counting the grid's cells - its factor naming `the grid` and its cells",
    ]);
    // an index listed but unused owes nothing more
    assert!(with(
        "- grid or spatial index: used - the grid",
        "- grid or spatial index: not used"
    )
    .is_empty(),);
    let px = "a 40 px gap.\n3px (2 ft) and 5 px, 6 ft.\na 4.5px gap that is very long, much longer than forty characters, before 12 ft\nx.5px and a5px.\n";
    assert_eq!(
        problems(&(BASE.to_owned() + px)),
        [
            "`40 px`: a px figure with no ft beside it - write its conversion, `40 px (<N> ft)`",
            "`4.5px`: a px figure with no ft beside it - write its conversion, `4.5px (<N> ft)`",
        ]
    );
}

#[test]
fn the_totals_hold_every_row_once_at_every_size() {
    assert_eq!(
        with("## Totals", "## Sums"),
        ["a `## Totals` section: one line per size, `- at <20|40|80>: <expression> = <value>`"]
    );
    assert_eq!(
        with("- at 80: 40 + 5 = 45\n", ""),
        ["`## Totals`: a line for 80 households"]
    );
    assert_eq!(
        with("10 + 5 = 15", "10 + 5 = 16"),
        ["`## Totals` at 20: `10 + 5` is 15, not 16"]
    );
    assert_eq!(with("10 + 5 = 15", "ten + 5 = 15"), ["`## Totals` at 20: `ten + 5` is not arithmetic on the table's figures (digits, + - x / and brackets)"]);
    assert_eq!(with("10 + 5 = 15", "15 = 15"), [
        "`## Totals` at 20: `items`'s figure 10 is not in the expression - every row of the count is a term of the total",
        "`## Totals` at 20: `the grid's cells`'s figure 5 is not in the expression - every row of the count is a term of the total",
    ]);
    assert_eq!(with("| over the run | 5 |", "| over the run | many |"), [
        "`the grid's cells`: no figure at 20 households - write its value as `N at <size>` for each of 20, 40, 80, or one number for every size",
        "`the grid's cells`: no figure at 40 households - write its value as `N at <size>` for each of 20, 40, 80, or one number for every size",
        "`the grid's cells`: no figure at 80 households - write its value as `N at <size>` for each of 20, 40, 80, or one number for every size",
    ]);
    assert!(with("| over the run | 5 |", "| over the run | about 5 cells |").is_empty());
    assert!(with("| over the run | 5 |", "| over the run | 5 at 20, 6 at 20, 5 at 40, 5 at 80 |").contains(&"`## Totals` at 20: `the grid's cells`'s figure 6 is not in the expression - every row of the count is a term of the total".to_owned()));
    assert_eq!(
        with("10 + 5 = 15", "10 + 5 + 1,000 = 1,015"),
        Vec::<String>::new()
    );
    // a total's value is a figure, never signed
    assert_eq!(
        with("10 + 5 = 15", "-10 + 5 = -5"),
        ["`## Totals`: a line for 20 households"],
    );
    assert_eq!(with("10 + 5 = 15", "10 + 5 = 15.4"), Vec::<String>::new());
    // a size past the four is owed nothing
    assert!(
        problems(&(BASE.to_owned() + "- at 99999999999999999999: 1 = 1\n- at 10: 1 = 1\n"))
            .is_empty(),
    );
    let twice = BASE.replace(
        "| the grid's cells | over the run | 5 |",
        "| the grid's cells | over the run | 10 at 20, 5 at 40, 5 at 80 |",
    );
    // two rows sharing a figure owe it twice
    assert_eq!(
        problems(&twice.replace("10 + 5 = 15", "10 + 10 = 20")),
        Vec::<String>::new(),
    );
    assert_eq!(
        problems(&twice.replace("10 + 5 = 15", "10 + 0 = 10")).len(),
        1
    );
    let dup = BASE.replace("| the grid's cells | over the run | 5 | each cell examined | 5 |", "| the grid's cells | over the run | 5 | each cell examined | 5 |\n| items | per item | 1 | again | 1 |");
    // a repeated factor's later figure in its first place
    assert_eq!(problems(&dup).len(), 3,);
    assert_eq!(with("10 + 5 = 15", "1, + 5 = 15"), ["`## Totals` at 20: `1, + 5` is 6, not 15", "`## Totals` at 20: `items`'s figure 10 is not in the expression - every row of the count is a term of the total"]);
    for bad in ["10 ** 5", "10 / 0", "9".repeat(400).as_str()] {
        assert!(form_problems(&BASE.replace("10 + 5 = 15", &format!("{bad} = 15"))).is_err(),);
    }
    // float('') is Python's ValueError
    assert!(form_problems(&BASE.replace("10 + 5 = 15", "10 + 5 = ,")).is_err(),);
    assert!(form_problems(&BASE.replace(
        "10 + 5 = 15",
        &format!("{0}.0 - {0}.0 = 15", "9".repeat(400))
    ))
    .is_err());
}

#[test]
fn a_bounded_n_owes_its_own_sizes() {
    let bounded = BASE
        .replace(
            "- Keeps: the rules of the record",
            "- Keeps: the rules\n- Bounds: a bounded n: households 10-20",
        )
        .replace(
            "## Totals\n- at 20: 10 + 5 = 15\n- at 40: 20 + 5 = 25\n- at 80: 40 + 5 = 45\n",
            "## Totals\n- at 10: 10 + 5 = 15\n- at 20: 10 + 5 = 15\n- at 80: 1 = 2\n",
        )
        .replace("10 at 20, 20 at 40, 40 at 80", "10 at 10, 10 at 20");
    assert_eq!(problems(&bounded), Vec::<String>::new());
    assert_eq!(
        problems(&bounded.replace("- at 10: 10 + 5 = 15\n", "")),
        ["`## Totals`: a line for 10 households"]
    );
}

#[test]
fn a_cost_past_the_reference_names_its_reason_and_its_bound() {
    let big = BASE
        .replace(
            "| items | per item | 10 at 20, 20 at 40, 40 at 80 |",
            "| items | per item | 1 at 20, 1 at 40, 1 at 80 |",
        )
        .replace(
            "| over the run | 5 |",
            "| over the run | 5000 at 20, 9000 at 40, 9000 at 80 |",
        )
        .replace("10 + 5 = 15", "1 + 5000 = 5001")
        .replace("20 + 5 = 25", "1 + 9000 = 9001")
        .replace("40 + 5 = 45", "1 + 9000 = 9001");
    assert_eq!(reference_problems(&big), [
        "the cost per thing at 40, 9,001 (9001 over 1 items), passes the reference's 4,000 (rubric S8) - count the typical case, or name why: `- reason above the reference: <why>`",
        "the cost per thing at 40, 9,001, passes the reference's 4,000 - name the bound that stops the search before it visits the whole set, or why none can (rubric S9): `- pruning: <the bound, or why none applies>`",
    ]);
    assert!(reference_problems(
        &(big.clone() + "\n- reason above the reference: big\n- pruning: none\n")
    )
    .is_empty());
    // no items: no cost per thing
    assert!(reference_problems(&big.replace("1 at 20, 1 at 40, 1 at 80", "0")).is_empty(),);
    assert!(reference_problems(&big.replace("## Totals", "## Sums")).is_empty());
    assert!(reference_problems(BASE).is_empty());
}
