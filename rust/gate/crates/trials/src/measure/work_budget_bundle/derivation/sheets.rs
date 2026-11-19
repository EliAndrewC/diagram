//! A Mode A stage's derivation (feature 449 T201): sized by the pool sheets rather than by households. The hamlet's form was the
//! only one (feature 443 T13, 444 T07), so T198's caption-placer derivation, judged SOUND, was refused for its form alone - Totals per
//! pool sheet, px on sheets drawn at 3 px to 1 ft, scopes per query. A derivation opts in with its `- Sizes: pool sheets: <sheet>, ...`
//! line; with none, or `- Sizes: households`, every check of `derivation.rs` holds exactly as before, and nothing here is asked.
//!
//! What changes under pool sheets, each with why:
//! - THE TOTALS: one line per named sheet, `- at <sheet>: <expression> = <value>`, each evaluated to the integer as a hamlet's is,
//!   and one for them all, `- all sheets: ... = <value>`, holding each sheet's value as a term and equal to their sum. A sheet is a
//!   fixed input, not a size of a growing n, so a count row's figure is per sheet in the derivation's own tables and is not matched
//!   term for term against each line (the agent judges that arithmetic; the all-sheets line is held mechanically).
//! - THE ITEMS: the `items` row gives each sheet's count in the `Sizes:` order, so the reference (rubric S8) is asked of the sum.
//! - THE SCOPES: also `per <step>`, where another row's factor names that step and resolves, row by row, to `per item`, `over the
//!   run` or `once` - a per-query factor is a per-item one once its queries are counted per item (T198: cells per query, entries
//!   per cell); and a standard scope with a qualifier (`per item, on the search kinds`).
//! - THE INDEXES: only a bullet naming a grid is read as one (T198's `Cells a query reads` and `Entries a cell holds` describe its
//!   grid's reads, not grids of their own). A grid states its cell size in ft, or in px at the stated scale; its density is the
//!   count's entries-per-cell row, measured per sheet, not bounded from a smallest side - a hamlet's grid saw every n of a range, a
//!   pool sheet is one drawn input whose density is read off it.
//! - THE PX: a sheet's own unit; a derivation that states its scale once (`- Scale: <N> px = <M> ft`) owes no ft beside each.

use std::collections::BTreeMap;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::strip;

use super::{
    arith, cells, finditer, fixed0, index_used, int_commas, lower, py_re, rounded, search,
    table_lines, EXPR, FIGURE, INDEX, INDEXES, PRUNING, PX, PX_FT, R, REASON, REFERENCE_PER_THING,
    SCOPES, TOTALS,
};

static SIZES_LINE: LazyLock<Regex> = LazyLock::new(|| py_re(r"(?m)^-\s*Sizes:[ \t]*(.*)$"));
static SCALE: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?mi)^-\s*Scale:\s*[\d.]+\s*px\s*=\s*[\d.]+\s*ft\b"));
static SHEET_TOTAL: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?m)^-\s*at\s+([\w-]+)\s*:\s*(.+?)\s*=\s*([\d,]+(?:\.\d+)?)\s*$"));
static ALL_TOTAL: LazyLock<Regex> = LazyLock::new(|| {
    py_re(
        r"(?mi)^-\s*(?:all(?:\s+the)?(?:\s+\w+)?\s+sheets|the\s+\w+\s+sheets)\s*:\s*(.+?)\s*=\s*([\d,]+(?:\.\d+)?)\s*$",
    )
});
static CELL_SIZE: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?i)\bcells?\s+of\s+(?:\w+\s*=\s*)?[\d,.]+\s*(?:px|ft)\b"));
static COUNT_FIG: LazyLock<Regex> = LazyLock::new(|| py_re(r"\d[\d,]*\d|\d"));
static WORD: LazyLock<Regex> = LazyLock::new(|| py_re(r"[a-z]+"));

/// The pool sheets a derivation's `Sizes:` line names: none for a hamlet derivation (no line, or `households`); the refusal for a
/// line that names neither, or pool sheets with no sheet.
pub(super) fn sizing(text: &str) -> Result<Option<Vec<String>>, String> {
    let Some(g) = search(&SIZES_LINE, text) else {
        return Ok(None);
    };
    let said = strip(&g[1]);
    let low = lower(said);
    if low.starts_with("households") {
        return Ok(None);
    }
    if !low.starts_with("pool sheets") {
        return Err(format!("`Sizes:` names households (a hamlet stage) or pool sheets (a Mode A stage) - not `{said}`"));
    }
    let rest = said.get("pool sheets".len()..).unwrap_or_default();
    let names: Vec<String> = rest
        .trim_start_matches([':', ' ', '\t'])
        .split(',')
        .map(|n| strip(n).trim_end_matches('.').to_owned())
        .filter(|n| !n.is_empty())
        .collect();
    if names.is_empty() {
        return Err(
            "`Sizes:` names each pool sheet: `- Sizes: pool sheets: <sheet>, <sheet>, ...`"
                .to_owned(),
        );
    }
    Ok(Some(names))
}

/// The pool sheets a derivation names, none for a hamlet derivation or a `Sizes:` line that does not read.
#[must_use]
pub fn pool_sheets(text: &str) -> Option<Vec<String>> {
    sizing(text).ok().flatten()
}

/// A word's stem, plurals folded (`queries` - `query`, `cells` - `cell`).
fn stem(word: &str) -> String {
    if let Some(head) = word.strip_suffix("ies") {
        format!("{head}y")
    } else if word.len() > 3 && word.ends_with('s') && !word.ends_with("ss") {
        word[..word.len() - 1].to_owned()
    } else {
        word.to_owned()
    }
}

fn stems(text: &str) -> Vec<String> {
    WORD.find_iter(&lower(text))
        .map_while(Result::ok)
        .map(|m| stem(m.as_str()))
        .collect()
}

/// Whether a count row's scope is one a pool-sheet derivation may write: a standard scope, one with a qualifier after a comma, or
/// `per <step>` where another row's factor names the step (its last word) and that row's own scope resolves the same way.
pub(super) fn scope_ok(rows: &[Vec<String>], me: usize) -> bool {
    fn resolves(rows: &[Vec<String>], me: usize, seen: &mut Vec<usize>) -> bool {
        let scope = lower(&rows[me][1]);
        if SCOPES
            .iter()
            .any(|s| scope == *s || scope.starts_with(&format!("{s},")))
        {
            return true;
        }
        let Some(step) = scope.strip_prefix("per ") else {
            return false;
        };
        let Some(noun) = stems(step).pop() else {
            return false;
        };
        seen.push(me);
        (0..rows.len()).any(|i| {
            !seen.contains(&i)
                && rows[i].len() > 1
                && stems(&rows[i][0]).contains(&noun)
                && resolves(rows, i, &mut seen.clone())
        })
    }
    resolves(rows, me, &mut Vec::new())
}

/// The scope refusal under pool sheets.
pub(super) fn scope_problem(name: &str, scope: &str) -> String {
    format!(
        "`{name}`: its scope is one of {}, or per <a step another row's factor names and counts per item> - not `{scope}`",
        SCOPES.join(", ")
    )
}

/// The grids a pool-sheet derivation lists, their cell sizes, the density row, and its px against its stated scale.
pub(super) fn index_problems(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    let grids: Vec<(String, String)> = search(&INDEXES, text)
        .map(|sec| {
            finditer(&INDEX, &sec[1])
                .into_iter()
                .map(|g| (strip(&g[1]).to_owned(), g[2].clone()))
                .filter(|(name, _)| lower(name).contains("grid"))
                .collect()
        })
        .unwrap_or_default();
    if index_used(text) && grids.is_empty() {
        out.push("an `## Indexes` section with a line for each grid the derivation uses - `- <name> grid: cells of <N> ft` (or px at the stated scale)".to_owned());
    }
    let factors: Vec<String> = table_lines(text)
        .iter()
        .skip(2)
        .map(|ln| lower(&cells(ln)[0]))
        .collect();
    for (name, line) in &grids {
        if !CELL_SIZE.is_match(line).unwrap_or(false) {
            out.push(format!(
                "`## Indexes` - {name}: its cell size (`cells of <N> ft`, or px at the stated scale)"
            ));
        }
        // ...ONE GRID, ITS CELLS ANY CELLS ROW (`cells_problems` asks one); more than one, each its own row, as a hamlet's
        if grids.len() > 1
            && !factors
                .iter()
                .any(|r| r.contains(&lower(name)) && r.contains("cell"))
        {
            out.push(format!("`## The count, factor by factor`: a row counting {name}'s cells - its factor naming `{name}` and its cells"));
        }
    }
    if !grids.is_empty()
        && !factors
            .iter()
            .any(|r| r.contains("entr") && r.contains("cell"))
    {
        out.push("`## The count, factor by factor`: a row counting the entries a grid cell holds - a pool sheet's density, measured on each sheet".to_owned());
    }
    if !SCALE.is_match(text).unwrap_or(false) {
        for m in PX.find_iter(text).map_while(Result::ok) {
            let after = text[m.end()..].trim_start_matches([' ', '(']);
            if !PX_FT.is_match(after).unwrap_or(false) {
                out.push(format!(
                    "`{}`: a px figure with no ft beside it and no `- Scale: <N> px = <M> ft` line - state the sheets' scale once, or write `{} (<N> ft)`",
                    m.as_str(),
                    m.as_str()
                ));
            }
        }
    }
    out
}

/// The `items` row's count on each sheet, in the `Sizes:` order: none where it gives fewer than one a sheet.
fn items(text: &str, sheets: usize) -> Option<Vec<f64>> {
    let rows: Vec<Vec<String>> = table_lines(text).iter().map(|ln| cells(ln)).collect();
    let row = rows
        .iter()
        .skip(2)
        .find(|r| lower(&r[0]) == "items" && r.len() > 2)?;
    let figs: Vec<f64> = COUNT_FIG
        .find_iter(&row[2])
        .map_while(Result::ok)
        .filter_map(|m| m.as_str().replace(',', "").parse().ok())
        .collect();
    (figs.len() >= sheets).then(|| figs[..sheets].to_vec())
}

/// One Totals line evaluated, as a hamlet's: its problem pushed, its value (rounded) where it is arithmetic.
fn line(label: &str, expr: &str, value: &str, out: &mut Vec<String>) -> R<Option<f64>> {
    if !EXPR.is_match(expr).unwrap_or(false) {
        out.push(format!("`## Totals` {label}: `{expr}` is not arithmetic on the table's figures (digits, + - x / and brackets)"));
        return Ok(None);
    }
    let got = rounded(arith(&expr.replace(',', "").replace('x', "*"))?)?;
    let want = rounded(
        value
            .replace(',', "")
            .parse::<f64>()
            .map_err(|e| format!("ValueError: {e}"))?,
    )?;
    #[expect(clippy::float_cmp, reason = "two rounded integers")]
    if got != want {
        out.push(format!(
            "`## Totals` {label}: `{expr}` is {}, not {value}",
            int_commas(got)
        ));
    }
    Ok(Some(want))
}

/// Each sheet's Totals line and the all-sheets line, as written: (sheet, expression, value) and (expression, value).
type Lines = (Vec<(String, String, String)>, Option<(String, String)>);

fn lines_of(text: &str) -> Option<Lines> {
    let sec = search(&TOTALS, text)?;
    let each = finditer(&SHEET_TOTAL, &sec[1])
        .into_iter()
        .map(|g| (g[1].clone(), g[2].clone(), g[3].clone()))
        .collect();
    let all = search(&ALL_TOTAL, &sec[1]).map(|g| (g[1].clone(), g[2].clone()));
    Some((each, all))
}

/// The `## Totals` of a pool-sheet derivation: a line per named sheet, each exact; the all-sheets line, exact, holding each sheet's
/// value once and equal to their sum; and the items row's count per sheet.
pub(super) fn total_problems(text: &str, names: &[String]) -> R<Vec<String>> {
    let mut out = Vec::new();
    if items(text, names.len()).is_none() {
        out.push(format!("`items`: its value gives each sheet's count, in the `Sizes:` line's order (`N = <n>, <n>, ...`, {} of them)", names.len()));
    }
    let Some((each, all)) = lines_of(text) else {
        out.push("a `## Totals` section: one line per pool sheet, `- at <sheet>: <expression> = <value>`, and one for them all, `- all sheets: <expression> = <value>`".to_owned());
        return Ok(out);
    };
    let mut values: BTreeMap<&str, (f64, String)> = BTreeMap::new();
    for (sheet, expr, value) in &each {
        if !names.contains(sheet) {
            out.push(format!(
                "`## Totals` at {sheet}: no sheet the `Sizes:` line names"
            ));
        } else if let Some(v) = line(&format!("at {sheet}"), expr, value, &mut out)? {
            values.insert(sheet, (v, value.replace(',', "")));
        }
    }
    for n in names
        .iter()
        .filter(|n| !each.iter().any(|(s, _, _)| s == *n))
    {
        out.push(format!("`## Totals`: a line for the sheet {n}"));
    }
    let Some((expr, value)) = all else {
        out.push(
            "`## Totals`: a line for the sheets together, `- all sheets: <expression> = <value>`"
                .to_owned(),
        );
        return Ok(out);
    };
    let Some(total) = line("for all sheets", &expr, &value, &mut out)? else {
        return Ok(out);
    };
    let mut tokens: BTreeMap<String, i64> = BTreeMap::new();
    for g in finditer(&FIGURE, &expr) {
        *tokens.entry(g[0].replace(',', "")).or_default() += 1;
    }
    for (sheet, (_, written)) in &values {
        if tokens.get(written).copied().unwrap_or(0) > 0 {
            *tokens.entry(written.clone()).or_default() -= 1;
        } else {
            out.push(format!("`## Totals` for all sheets: {sheet}'s total {written} is not in the expression - the sum holds every sheet's line"));
        }
    }
    let sum: f64 = values.values().map(|(v, _)| v).sum();
    #[expect(clippy::float_cmp, reason = "sums of rounded integers")]
    if values.len() == names.len() && sum != total {
        out.push(format!(
            "`## Totals` for all sheets: {value} is not the sheets' sum, {}",
            int_commas(sum)
        ));
    }
    Ok(out)
}

/// The reference's reasons (rubric S8, S9) over the sheets together: the all-sheets total over the items summed.
pub(super) fn reference_problems(text: &str, names: &[String]) -> Vec<String> {
    let (Some(n), Some((_, Some((_, total))))) = (items(text, names.len()), lines_of(text)) else {
        return vec![];
    };
    let (Ok(t), i) = (total.replace(',', "").parse::<f64>(), n.iter().sum::<f64>()) else {
        return vec![];
    };
    if i == 0.0 || t / i <= REFERENCE_PER_THING {
        return vec![];
    }
    let per = fixed0(t / i);
    let mut out = Vec::new();
    if !REASON.is_match(text).unwrap_or(false) {
        out.push(format!("the cost per thing over the sheets, {per} ({total} over {} items), passes the reference's 4,000 (rubric S8) - count the typical case, or name why: `- reason above the reference: <why>`", fixed0(i)));
    }
    if !PRUNING.is_match(text).unwrap_or(false) {
        out.push(format!("the cost per thing over the sheets, {per}, passes the reference's 4,000 - name the bound that stops the search before it visits the whole set, or why none can (rubric S9): `- pruning: <the bound, or why none applies>`"));
    }
    out
}

/// A pool-sheet derivation's budget as its Totals give it: each named sheet's value and the all-sheets value, with each sheet's items
/// - none for a hamlet derivation or one whose lines do not read (the bundle's checks refuse those first).
#[must_use]
pub fn sheet_budget(text: &str) -> Option<SheetBudget> {
    let names = pool_sheets(text)?;
    let n = items(text, names.len())?;
    let (each, all) = lines_of(text)?;
    let figure = |v: &str| v.replace(',', "").parse::<f64>().ok();
    let sheets = names
        .iter()
        .zip(n)
        .map(|(name, items)| {
            let (_, _, v) = each.iter().find(|(s, _, _)| s == name)?;
            Some((name.clone(), figure(v)?, items))
        })
        .collect::<Option<Vec<_>>>()?;
    Some(SheetBudget {
        sheets,
        all: figure(&all?.1)?,
    })
}

/// A pool-sheet stage's budget: (sheet, operations, items) per sheet, and the sheets together.
#[derive(Debug, PartialEq)]
pub struct SheetBudget {
    pub sheets: Vec<(String, f64, f64)>,
    pub all: f64,
}

#[cfg(test)]
mod tests;
