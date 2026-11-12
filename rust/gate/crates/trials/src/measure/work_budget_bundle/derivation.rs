//! What a MODE BUDGET derivation must hold, and may not (feature 443 T05, T13; feature 444 T01, T07, FR-014, FR-015; ported by
//! feature 449 T134 from `work_budget_bundle.py`, the refusals and their words unchanged). Each refusal's why stays beside it.

use std::collections::BTreeMap;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_guard::shared::py_text::strip;
use l7r_guard::shared::speckit::splitlines;

use super::{py_re, read, R};

/// What a MODE BUDGET derivation may not hold, each with why (443 plan D10): each would put today's code or its numbers in front
/// of the judge.
static FORBIDDEN: LazyLock<[(Regex, &str); 3]> = LazyLock::new(|| {
    [
        (
            py_re(r"(?mi)^```\s*py(?:thon)?\b"),
            "a fenced block of Python - today's code",
        ),
        (
            py_re(r"(?<![\w/])l7r/[\w./-]+"),
            "a path under l7r/ - today's code",
        ),
        (
            py_re(r"(?i)\b\d[\d,.]*\s*(?:[kKmM]\s*)?(?:calls|ops)\b|\b(?:calls|ops)\s*[:=]?\s*\d"),
            "a figure tagged as a current count (calls or ops beside a number)",
        ),
    ]
});

/// A `## <title>` section to the next one.
fn section(title: &str) -> Regex {
    py_re(&format!(r"(?ms)^## {title}\b(.*?)(?=^## |\Z)"))
}

pub(super) static CONTRACT: LazyLock<Regex> = LazyLock::new(|| section("Contract"));
// THE DERIVATION'S FORM (feature 443 T13; the GM 2026-10-28: being careful means the checklist says what careful is) - each a field
// an error of T05's grid fixture would have been refused at: round 2's "per disc" bound that held only over the run (SCOPE), round
// 3's incremental update never considered (the ALTERNATIVES) and its "once" term with no bound (WORST CASE)
static COUNT: LazyLock<Regex> = LazyLock::new(|| section("The count, factor by factor"));
static ALTERNATIVES: LazyLock<Regex> = LazyLock::new(|| section("Cheaper algorithms considered"));
static TOTALS: LazyLock<Regex> = LazyLock::new(|| section("Totals"));
static INDEXES: LazyLock<Regex> = LazyLock::new(|| section("Indexes"));
static ANSWERS: LazyLock<Regex> = LazyLock::new(|| section("Earlier findings"));

const COLUMNS: [&str; 5] = ["factor", "scope", "value", "reason", "worst case"];
const SCOPES: [&str; 3] = ["per item", "over the run", "once"];
const STANDARD: [&str; 5] = [
    "sweep",
    "grid or spatial index",
    "priority queue",
    "incremental update",
    "memoizing what a scan does not change",
];
pub(super) const TEMPLATE: &str = ".specify/templates/derivation.md";

const TOTAL_SIZES: [i64; 3] = [20, 40, 80];
/// The sizes a derivation's totals may be given at: the standard three, or - for a stage whose form exists only over a BOUNDED n
/// (rubric S6), stated in its Contract's Bounds as `a bounded n: households 10-20` - those of these within it, at least two (the
/// round arbiter's ruling on ask:444-polder-sizes: a polder exists at 10-20 households alone, 0019).
const ANY_SIZES: [i64; 4] = [10, 20, 40, 80];

static BOUNDED: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?i)bounded n[^.;\n]*?households\s+(\d+)\s*(?:-|to)\s*(\d+)"));
static TOTAL: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?m)^-\s*at\s+(\d+)\s*:\s*(.+?)\s*=\s*([\d,]+(?:\.\d+)?)\s*$"));
static EXPR: LazyLock<Regex> = LazyLock::new(|| py_re(r"^[\d\s.,+\-*/x()]+$"));
static AT: LazyLock<Regex> = LazyLock::new(|| py_re(r"([\d,]+(?:\.\d+)?)\s+at\s+(\d+)"));
static NUM: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"^\s*(?:at most\s+|about\s+)?([\d,]+(?:\.\d+)?)\b"));
static FIGURE: LazyLock<Regex> = LazyLock::new(|| py_re(r"[\d,]+(?:\.\d+)?"));

/// The rubric's reference, a few thousand basic operations a house (request.md; a GUESS).
const REFERENCE_PER_THING: f64 = 4000.0;
static REASON: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?mi)^-\s*reason above the reference:\s*\S"));
// rubric S9 (the GM 2026-10-29, the notice board's 8,730 operations)
static PRUNING: LazyLock<Regex> = LazyLock::new(|| py_re(r"(?mi)^-\s*pruning:\s*\S"));

static INDEX: LazyLock<Regex> = LazyLock::new(|| py_re(r"(?m)^-\s*([^:\n]+):\s*(.*)$"));
static CELL_FT: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?i)\bcells?\s+(?:of\s+)?[\d,.]+\s*ft\b"));
static SIDE: LazyLock<Regex> = LazyLock::new(|| py_re(r"(?i)\bside\b[^.]*?[\d,.]+\s*ft\b"));
static PX: LazyLock<Regex> = LazyLock::new(|| py_re(r"(?<![\w.])[\d,.]+\s*px\b"));
static PX_FT: LazyLock<Regex> = LazyLock::new(|| py_re(r"^[^.;\n]{0,40}?[\d,.]+\s*ft\b"));
static USED: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?mi)^-\s*grid or spatial index:\s*used\b"));
static CONTRACT_LINE: LazyLock<Regex> =
    LazyLock::new(|| py_re(r"(?m)^-\s*(Reads|Writes|Keeps):[ \t]*(.*)$"));
static SAID: LazyLock<Regex> = LazyLock::new(|| py_re(r"(?m)^-\s*([^:\n]+):[ \t]*(.*)$"));
static ANSWER: LazyLock<Regex> = LazyLock::new(|| {
    py_re(r"(?mi)^-\s*verdict-(\d+),\s*finding\s+(\d+):\s*(fixed|disputed)\b\s*-\s*\S")
});
static ALSO: LazyLock<Regex> = LazyLock::new(|| py_re(r"(?s)\(Also:\s*(.*?)\)\s*$"));

/// The captures of `re` at its first match in `text`, each group's text ("" for none).
fn search(re: &Regex, text: &str) -> Option<Vec<String>> {
    let c = re.captures(text).ok().flatten()?;
    Some(
        (0..c.len())
            .map(|i| c.get(i).map_or_else(String::new, |m| m.as_str().to_owned()))
            .collect(),
    )
}

/// Every match's groups.
fn finditer(re: &Regex, text: &str) -> Vec<Vec<String>> {
    re.captures_iter(text)
        .filter_map(Result::ok)
        .map(|c| {
            (0..c.len())
                .map(|i| c.get(i).map_or_else(String::new, |m| m.as_str().to_owned()))
                .collect()
        })
        .collect()
}

/// A section's body (its group 1), "" when it is absent.
fn body(re: &Regex, text: &str) -> String {
    search(re, text).map(|g| g[1].clone()).unwrap_or_default()
}

/// `int(text)` of a run of digits `\d` matched: an ASCII one, else none (a non-ASCII digit Python reads, the divergence T127 met).
fn int(text: &str) -> Option<i64> {
    text.parse().ok()
}

/// `str.lower()`.
fn lower(text: &str) -> String {
    text.to_lowercase()
}

/// The household sizes this derivation's totals are owed at: its bounded n's, else the standard three.
#[must_use]
pub fn sizes(text: &str) -> Vec<i64> {
    let Some(g) = search(&BOUNDED, text) else {
        return TOTAL_SIZES.to_vec();
    };
    let (lo, hi) = (
        int(&g[1]).unwrap_or(i64::MAX),
        int(&g[2]).unwrap_or(i64::MAX),
    );
    let within: Vec<i64> = ANY_SIZES
        .iter()
        .copied()
        .filter(|h| lo <= *h && *h <= hi)
        .collect();
    if within.len() >= 2 {
        within
    } else {
        TOTAL_SIZES.to_vec()
    }
}

/// A table line's cells, as `ln.strip().strip("|").split("|")` with each cell stripped.
fn cells(line: &str) -> Vec<String> {
    strip(line)
        .trim_matches('|')
        .split('|')
        .map(|c| strip(c).to_owned())
        .collect()
}

/// The count section's table lines.
fn table_lines(text: &str) -> Vec<String> {
    let count = body(&COUNT, text);
    splitlines(&count)
        .into_iter()
        .filter(|ln| strip(ln).starts_with('|'))
        .map(str::to_owned)
        .collect()
}

/// Each count row's figure at each size: `N at S` pairs where the value cell gives them, else its one leading number at every
/// size; a row whose value is neither has no figure (and is refused by `total_problems`). Rows in first-seen order, a repeated
/// factor's later figures in its first place, as a Python dict keeps them.
fn row_values(text: &str) -> Vec<(String, BTreeMap<i64, String>)> {
    let mut out: Vec<(String, BTreeMap<i64, String>)> = Vec::new();
    let count = body(&COUNT, text);
    for ln in splitlines(&count) {
        let c = cells(ln);
        if !strip(ln).starts_with('|')
            || c.len() != COLUMNS.len()
            || lower(&c[0]) == "factor"
            || c[0].chars().all(|ch| ch == '-')
        {
            continue;
        }
        let pairs: Vec<(Option<i64>, String)> = finditer(&AT, &c[2])
            .into_iter()
            .map(|g| (int(&g[2]), g[1].clone()))
            .collect();
        let one = search(&NUM, &c[2]).map(|g| g[1].clone());
        let at: BTreeMap<i64, String> = sizes(text)
            .into_iter()
            .map(|h| {
                let pair = pairs
                    .iter()
                    .rev()
                    .find(|(sz, _)| *sz == Some(h))
                    .map(|(_, n)| n.clone());
                let fallback = if pairs.is_empty() {
                    one.clone().unwrap_or_default()
                } else {
                    String::new()
                };
                (h, pair.unwrap_or(fallback))
            })
            .collect();
        match out.iter_mut().find(|(k, _)| *k == c[0]) {
            Some(row) => row.1 = at,
            None => out.push((c[0].clone(), at)),
        }
    }
    out
}

/// An arithmetic expression's value: numbers, `+ - * /` and brackets, as `ast.parse` and `_arith` read it - anything else (a
/// `**`, a `//`, a unary plus, two numbers side by side, a number Python refuses such as `007`) is the failure they raised.
fn arith(expr: &str) -> R<f64> {
    let toks: Vec<char> = expr.chars().filter(|c| !super::is_py_space(*c)).collect();
    let spaced: Vec<char> = expr.chars().collect();
    // two numbers side by side (`1 2`) are no expression; the spaces are dropped only after that is ruled out
    let mut prev_digit = false;
    let mut gap = false;
    for c in &spaced {
        if super::is_py_space(*c) {
            gap = prev_digit;
        } else {
            if gap && (c.is_ascii_digit() || *c == '.') {
                return Err(format!("SyntaxError: invalid syntax: {expr}"));
            }
            prev_digit = c.is_ascii_digit() || *c == '.';
            gap = false;
        }
    }
    let mut p = Arith { s: toks, at: 0 };
    let v = p.sum()?;
    if p.at != p.s.len() {
        return Err(format!("SyntaxError: invalid syntax: {expr}"));
    }
    Ok(v)
}

struct Arith {
    s: Vec<char>,
    at: usize,
}

impl Arith {
    fn peek(&self) -> Option<char> {
        self.s.get(self.at).copied()
    }

    fn bad<T>(&self) -> R<T> {
        Err(format!(
            "SyntaxError or ValueError at {} of {}",
            self.at,
            self.s.iter().collect::<String>()
        ))
    }

    fn sum(&mut self) -> R<f64> {
        let mut v = self.term()?;
        while let Some(op @ ('+' | '-')) = self.peek() {
            self.at += 1;
            let r = self.term()?;
            v = if op == '+' { v + r } else { v - r };
        }
        Ok(v)
    }

    fn term(&mut self) -> R<f64> {
        let mut v = self.unary()?;
        while let Some(op @ ('*' | '/')) = self.peek() {
            self.at += 1;
            if matches!(self.peek(), Some('*' | '/')) {
                // `**` and `//`: Pow and FloorDiv, which `_arith` refuses
                return self.bad();
            }
            let r = self.unary()?;
            if op == '/' && r == 0.0 {
                return Err("ZeroDivisionError: float division by zero".to_owned());
            }
            v = if op == '*' { v * r } else { v / r };
        }
        Ok(v)
    }

    fn unary(&mut self) -> R<f64> {
        match self.peek() {
            Some('-') => {
                self.at += 1;
                Ok(-self.unary()?)
            }
            Some('+') => {
                // a unary plus parses, but `_arith` takes only `USub`
                self.at += 1;
                self.unary()?;
                self.bad()
            }
            Some('(') => {
                self.at += 1;
                if self.peek() == Some(')') {
                    return self.bad();
                }
                let v = self.sum()?;
                if self.peek() != Some(')') {
                    return self.bad();
                }
                self.at += 1;
                self.after_atom()?;
                Ok(v)
            }
            _ => {
                let start = self.at;
                while self.peek().is_some_and(|c| c.is_ascii_digit() || c == '.') {
                    self.at += 1;
                }
                let lit: String = self.s[start..self.at].iter().collect();
                if lit.is_empty() || !super::pyast_number(&lit) {
                    return self.bad();
                }
                self.after_atom()?;
                // a literal Python's tokenizer reads is one Rust's float reader reads
                let v: f64 = lit.parse().unwrap_or_default();
                // an integer literal past a float's range is `float(int)`'s OverflowError; a float literal past it is inf, as Python reads it
                if v.is_infinite() && !lit.contains('.') {
                    return self.bad();
                }
                Ok(v)
            }
        }
    }

    /// An atom followed by `(` is a call, which `_arith` refuses.
    fn after_atom(&self) -> R<()> {
        if self.peek() == Some('(') {
            return self.bad();
        }
        Ok(())
    }
}

/// `round(x)`, ties to even, as its exact integer's digits; the failure Python raised for an infinity or a NaN.
fn rounded(x: f64) -> R<f64> {
    if x.is_finite() {
        Ok(x.round_ties_even())
    } else {
        Err(format!(
            "OverflowError or ValueError: cannot convert float {x} to integer"
        ))
    }
}

/// An integral float's exact digits with thousands commas (`f"{n:,}"` of the int).
fn int_commas(x: f64) -> String {
    let digits = format!("{:.0}", x.abs());
    let grouped = commas_of(&digits);
    if x < 0.0 {
        format!("-{grouped}")
    } else {
        grouped
    }
}

/// A string of digits grouped by thousands.
pub(super) fn commas_of(digits: &str) -> String {
    let mut out = String::new();
    for (i, c) in digits.chars().enumerate() {
        if i > 0 && (digits.len() - i) % 3 == 0 {
            out.push(',');
        }
        out.push(c);
    }
    out
}

/// `f"{x:,.0f}"` of a finite figure.
pub(super) fn fixed0(x: f64) -> String {
    let s = format!("{x:.0}");
    match s.strip_prefix('-') {
        Some(digits) => format!("-{}", commas_of(digits)),
        None => commas_of(&s),
    }
}

/// The `## Totals` section's lines - `- at <size>: <expression> = <value>`, one per size - each evaluated EXACTLY, to the
/// integer (feature 444 T07: a sum written wrong refused before any dispatch), and each holding every count row's figure at that
/// size (a total leaving out a term refused); a row with no figure at a size is refused too, so nothing escapes the expression.
fn total_problems(text: &str) -> R<Vec<String>> {
    let sz = sizes(text);
    let Some(sec) = search(&TOTALS, text) else {
        let joined: Vec<String> = sz.iter().map(i64::to_string).collect();
        return Ok(vec![format!(
            "a `## Totals` section: one line per size, `- at <{}>: <expression> = <value>`",
            joined.join("|")
        )]);
    };
    let mut found: BTreeMap<i64, (String, String)> = BTreeMap::new();
    for g in finditer(&TOTAL, &sec[1]) {
        // a size Python's int() reads but past i64 is no size of the four; it is owed nothing
        if let Some(h) = int(&g[1]) {
            found.insert(h, (g[2].clone(), g[3].clone()));
        }
    }
    let mut out: Vec<String> = sz
        .iter()
        .filter(|h| !found.contains_key(h))
        .map(|h| format!("`## Totals`: a line for {h} households"))
        .collect();
    let rows = row_values(text);
    for (h, (expr, value)) in found.iter().filter(|(h, _)| sz.contains(h)) {
        if !EXPR.is_match(expr).unwrap_or(false) {
            out.push(format!("`## Totals` at {h}: `{expr}` is not arithmetic on the table's figures (digits, + - x / and brackets)"));
            continue;
        }
        let got = rounded(arith(&expr.replace(',', "").replace('x', "*"))?)?;
        let value_read = value
            .replace(',', "")
            .parse::<f64>()
            .map_err(|e| format!("ValueError: {e}"))?;
        let want = rounded(value_read)?;
        #[expect(
            clippy::float_cmp,
            reason = "two rounded integers, compared as Python compares the ints"
        )]
        let differ = got != want;
        if differ {
            out.push(format!(
                "`## Totals` at {h}: `{expr}` is {}, not {value}",
                int_commas(got)
            ));
        }
        // ...EACH ROW ITS OWN TERM (the round arbiter's note on ask:444-T07-plan-round-3): two rows sharing a figure owe it twice, so the
        // expression's numbers are counted, and each row takes one of its own
        let mut tokens: BTreeMap<String, i64> = BTreeMap::new();
        for g in finditer(&FIGURE, expr) {
            *tokens.entry(g[0].replace(',', "")).or_default() += 1;
        }
        let joined: Vec<String> = sz.iter().map(i64::to_string).collect();
        for (name, at) in &rows {
            let figure = &at[h];
            let key = figure.replace(',', "");
            if figure.is_empty() {
                out.push(format!(
                    "`{name}`: no figure at {h} households - write its value as `N at <size>` for each of {}, or one number for every size",
                    joined.join(", ")
                ));
            } else if tokens.get(&key).copied().unwrap_or(0) > 0 {
                *tokens.entry(key).or_default() -= 1;
            } else {
                out.push(format!("`## Totals` at {h}: `{name}`'s figure {figure} is not in the expression - every row of the count is a term of the total"));
            }
        }
    }
    Ok(out)
}

/// THE REFERENCE ASKS A REASON (feature 444 FR-014, rubric S8; the GM 2026-10-28: "I thought the idea was to REDUCE the number of
/// operations. Why would we be targeting something HIGHER?"): a derivation whose total at 40 over its items at 40 passes the
/// reference's 4,000 a thing names why, `- reason above the reference: <why>`, and the bound that stops its search early or why none
/// can, `- pruning: <why>` (rubric S9: the GM 2026-10-29, "Why do we think it should take 8,730-11,277 operations to place a single
/// notice board?!" - "the stage is one thing" had passed as the reason); under it, nothing is asked. The agent judges the words.
/// It refuses nothing a reason answers - the band is a GUESS worked for the homesteads.
fn reference_problems(text: &str) -> Vec<String> {
    let rows = row_values(text);
    let items = rows
        .iter()
        .find(|(k, _)| k == "items")
        .and_then(|(_, at)| at.get(&40))
        .cloned()
        .unwrap_or_default();
    let total = search(&TOTALS, text)
        .and_then(|sec| {
            finditer(&TOTAL, &sec[1])
                .into_iter()
                .find(|g| int(&g[1]) == Some(40))
                .map(|g| g[3].clone())
        })
        .unwrap_or_default();
    let (Ok(t), Ok(i)) = (
        total.replace(',', "").parse::<f64>(),
        items.replace(',', "").parse::<f64>(),
    ) else {
        return vec![];
    };
    if i == 0.0 {
        return vec![];
    }
    let per = t / i;
    if per <= REFERENCE_PER_THING {
        return vec![];
    }
    let mut out = Vec::new();
    if !REASON.is_match(text).unwrap_or(false) {
        out.push(format!(
            "the cost per thing at 40, {} ({total} over {items} items), passes the reference's 4,000 (rubric S8) - count the typical case, or name why: `- reason above the reference: <why>`",
            fixed0(per)
        ));
    }
    if !PRUNING.is_match(text).unwrap_or(false) {
        out.push(format!(
            "the cost per thing at 40, {}, passes the reference's 4,000 - name the bound that stops the search before it visits the whole set, or why none can (rubric S9): `- pruning: <the bound, or why none applies>`",
            fixed0(per)
        ));
    }
    out
}

/// Whether the derivation says a grid or spatial index is used.
fn index_used(text: &str) -> bool {
    search(&ALTERNATIVES, text).is_some_and(|alts| USED.is_match(&alts[1]).unwrap_or(false))
}

/// The count table's factors, lowered, the header and its rule left out.
fn factors(text: &str) -> Vec<String> {
    table_lines(text)
        .iter()
        .skip(2)
        .map(|ln| lower(&cells(ln)[0]))
        .collect()
}

/// EVERY INDEX ITS OWN ROW (the round arbiter's tooling fix on ask:444-T02-water-round-6: T07's check held once a derivation, so
/// one cells row passed while each index a rewrite added went unchecked - field round 5, `pond_bank` round 3): a derivation that uses a
/// grid or spatial index lists each in `## Indexes` - its cell size in ft and its densest case from a smallest SIDE in ft, never an
/// area - and counts each in a row of its own, the row's factor naming the index and its cells; and every px figure carries its ft.
fn index_problems(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    let entries: Vec<(String, String)> = search(&INDEXES, text)
        .map(|sec| {
            finditer(&INDEX, &sec[1])
                .into_iter()
                .map(|g| (strip(&g[1]).to_owned(), g[2].clone()))
                .collect()
        })
        .unwrap_or_default();
    if index_used(text) && entries.is_empty() {
        out.push("an `## Indexes` section: one line per index the derivation uses - `- <name>: cells of <N> ft; densest <count>, from a smallest side of <S> ft`".to_owned());
    }
    let rows = factors(text);
    for (name, line) in &entries {
        if !CELL_FT.is_match(line).unwrap_or(false) {
            out.push(format!(
                "`## Indexes` - {name}: its cell size in ft (`cells of <N> ft`)"
            ));
        }
        if !SIDE.is_match(line).unwrap_or(false) {
            out.push(format!(
                "`## Indexes` - {name}: its densest case from a smallest side in ft, never an area"
            ));
        }
        if !rows
            .iter()
            .any(|r| r.contains(&lower(name)) && r.contains("cell"))
        {
            out.push(format!("`## The count, factor by factor`: a row counting {name}'s cells - its factor naming `{name}` and its cells"));
        }
    }
    for m in PX.find_iter(text).filter_map(Result::ok) {
        let after = text[m.end()..].trim_start_matches([' ', '(']);
        if !PX_FT.is_match(after).unwrap_or(false) {
            out.push(format!(
                "`{}`: a px figure with no ft beside it - write its conversion, `{} (<N> ft)`",
                m.as_str(),
                m.as_str()
            ));
        }
    }
    out
}

/// A derivation that uses a grid or spatial index counts the cells it examines (the rubric: an index cell examined is a basic
/// operation; feature 444 T07).
fn cells_problems(text: &str) -> Vec<String> {
    if index_used(text) && !factors(text).iter().any(|r| r.contains("cell")) {
        return vec!["`## The count, factor by factor`: a row counting the index cells examined - the derivation says a grid or spatial index is used".to_owned()];
    }
    vec![]
}

/// Each field of the derivation template a derivation lacks (`TEMPLATE`): the count's table with every column filled and a
/// scope of its three, and a line for each standard cheaper algorithm saying whether it is used and why.
///
/// # Errors
///
/// Where a total's expression raised (`total_problems`).
pub(super) fn form_problems(text: &str) -> R<Vec<String>> {
    let mut out = Vec::new();
    let contract = search(&CONTRACT, text)
        .map(|g| g[0].clone())
        .unwrap_or_default();
    let mut lines: BTreeMap<String, String> = BTreeMap::new();
    for g in finditer(&CONTRACT_LINE, &contract) {
        lines.insert(lower(&g[1]), strip(&g[2]).to_owned());
    }
    // ...THE CONTRACT'S FOUR PARTS (feature 444 T01, the design's checklist box 1): what it reads, what it writes, and what it keeps -
    // the cohort properties and the research claims, each a rule asked of a candidate before it is placed, so each a check of the count
    for k in ["Reads", "Writes", "Keeps"] {
        if lines
            .get(&lower(k))
            .is_none_or(|v| v.is_empty() || v.starts_with('<'))
        {
            out.push(format!("`## Contract`: its `{k}:` line, filled"));
        }
    }
    let rows: Vec<Vec<String>> = table_lines(text).iter().map(|ln| cells(ln)).collect();
    if rows.is_empty()
        || rows[0]
            .iter()
            .map(|c| lower(c))
            .ne(COLUMNS.iter().map(|c| (*c).to_owned()))
    {
        out.push(format!(
            "the `## The count, factor by factor` table with the columns {}",
            COLUMNS.join(" | ")
        ));
    } else {
        for r in rows.iter().skip(2) {
            let name = if r[0].is_empty() { "a factor" } else { &r[0] };
            if r.len() != COLUMNS.len() || r.iter().any(|c| c.is_empty() || c.starts_with('<')) {
                out.push(format!(
                    "`{name}`: every column filled (scope, value, reason, worst case)"
                ));
            } else if !SCOPES.contains(&lower(&r[1]).as_str()) {
                out.push(format!(
                    "`{name}`: its scope is one of {} - not `{}`",
                    SCOPES.join(", "),
                    r[1]
                ));
            }
        }
        if rows.len() < 3 {
            out.push("a row for each factor of the count".to_owned());
        }
    }
    let alts = body(&ALTERNATIVES, text);
    let mut said: BTreeMap<String, String> = BTreeMap::new();
    for g in finditer(&SAID, &alts) {
        said.insert(lower(strip(&g[1])), strip(&g[2]).to_owned());
    }
    for a in STANDARD {
        if said.get(a).is_none_or(String::is_empty) {
            out.push(format!(
                "`## Cheaper algorithms considered`: a line for `{a}` - used, or why not"
            ));
        }
    }
    out.extend(cells_problems(text));
    out.extend(index_problems(text));
    out.extend(total_problems(text)?);
    out.extend(reference_problems(text));
    Ok(out)
}

/// Why a derivation may not go to MODE BUDGET: each forbidden thing it holds, with its first match.
pub(super) fn refusals(text: &str) -> Vec<String> {
    FORBIDDEN
        .iter()
        .filter_map(|(re, why)| {
            let m = re.find(text).ok().flatten()?;
            let shown: String = strip(m.as_str()).chars().take(60).collect();
            Some(format!("{why}: `{shown}`"))
        })
        .collect()
}

/// A recorded verdict's findings: its headline, then each `;`-separated item of its `(Also: ...)` note.
fn findings_of(text: &str) -> Vec<String> {
    let lines: Vec<&str> = splitlines(text)
        .into_iter()
        .map(strip)
        .filter(|l| !l.is_empty())
        .collect();
    let Some(first) = lines.first() else {
        return vec![];
    };
    let mut out = vec![(*first).to_owned()];
    if let Some(g) = search(&ALSO, text) {
        out.extend(
            g[1].split(';')
                .filter(|a| !strip(a).is_empty())
                .map(|a| strip(a).trim_end_matches('.').to_owned()),
        );
    }
    out
}

/// A verdict file's number: the digits after its last `-` (`<stage>.verdict-<N>.txt`), none where it holds no digit.
fn verdict_number(name: &str) -> Option<usize> {
    let tail = name.rsplit_once('-').map_or(name, |(_, t)| t);
    let digits: String = tail.chars().filter(char::is_ascii_digit).collect();
    digits.parse().ok()
}

/// The verdict files recorded beside a derivation (`<stage>.verdict-*.txt`), in the directory's own order.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "glob's pattern is case-sensitive, as the Python's was"
)]
pub(super) fn verdict_files(dir: &Path, stage: &str) -> Vec<std::path::PathBuf> {
    let prefix = format!("{stage}.verdict-");
    super::listing(dir)
        .into_iter()
        .filter(|p| {
            p.file_name().and_then(|n| n.to_str()).is_some_and(|n| {
                n.starts_with(&prefix) && n.ends_with(".txt") && n.len() >= prefix.len() + 4
            })
        })
        .collect()
}

/// EVERY EARLIER FINDING ANSWERED (the round arbiter's tooling fix on ask:444-T02-field-round-8: a finding left open under one
/// verdict's "Also" came back as the next verdict's headline): each finding of each earlier verdict recorded beside the derivation
/// (`<stage>.verdict-<N>.txt`) has a line in `## Earlier findings`, `- verdict-<N>, finding <K>: fixed - ...` or `disputed - ...`.
///
/// # Errors
///
/// A verdict file whose name holds no number, or one that does not read: where the Python raised.
pub(super) fn answer_problems(src: &Path, text: &str) -> R<Vec<String>> {
    let name = src.file_name().and_then(|n| n.to_str()).unwrap_or_default();
    let stage = name.strip_suffix(".derivation.md").unwrap_or(name);
    let have: Vec<(Option<usize>, Option<usize>)> = search(&ANSWERS, text)
        .map(|sec| {
            finditer(&ANSWER, &sec[1])
                .into_iter()
                .map(|g| (g[1].parse().ok(), g[2].parse().ok()))
                .collect()
        })
        .unwrap_or_default();
    let mut files = verdict_files(src.parent().unwrap_or(Path::new(".")), stage);
    files.sort_by_key(|p| {
        verdict_number(&p.file_name().unwrap_or_default().to_string_lossy()).unwrap_or(0)
    });
    let mut out = Vec::new();
    for v in files {
        let vname = v
            .file_name()
            .unwrap_or_default()
            .to_string_lossy()
            .into_owned();
        let n = verdict_number(&vname).ok_or_else(|| {
            format!("ValueError: invalid literal for int() with base 10: {vname}")
        })?;
        for (k, f) in (1..).zip(findings_of(&read(&v)?)) {
            if !have.contains(&(Some(n), Some(k))) {
                let shown: String = f.chars().take(80).collect();
                out.push(format!("`## Earlier findings`: verdict-{n}, finding {k} unanswered - `- verdict-{n}, finding {k}: fixed - <how>` or `disputed - <why>` ({shown})"));
            }
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests;
