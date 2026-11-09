//! The room table (405 T113; feature 449 T068, from `room_table.py`): one row per spacing or size knob, printed when what failed is a FIT failure.
//!
//! WHY (the GM, 2026-10-21; the round arbiter's tooling fix on `ask:set-down-T26`): two room probes widened `grow_gap` while the seating band
//! stayed the same size, so they dealt the same seats into the same band - tighter packing, not more room - and were read as "room fails".

use std::fmt::Write as _;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::Value;

/// The cohort failures that are a fit failure: something did not fit where it stands.
const FIT: [&str; 4] = [
    "refused",
    "lane_knots",
    "groves_crossed_by_lanes",
    "fixtures_on_groves",
];
static FIT_WORDS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)\b(?:knots?|lane_knots|refused|unreached|room)\b")
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// Is any of a cohort seed's `failures` a fit failure (a refusal is `refused:<kind>`)?
pub(crate) fn is_fit(failures: &[Value]) -> bool {
    failures.iter().any(|f| {
        FIT.contains(
            &f.as_str()
                .unwrap_or_default()
                .split(':')
                .next()
                .unwrap_or_default(),
        )
    })
}

/// Does a question put to the arbiter name a fit failure?
pub(crate) fn names_fit(text: &str) -> bool {
    FIT_WORDS.is_match(text).unwrap_or(false)
}

/// The table as Markdown, headed with what to do with it.
pub(crate) fn table(root: &Path) -> String {
    let data: Value = serde_json::from_str(
        &std::fs::read_to_string(root.join("scripts/gates/room_table.json")).unwrap_or_default(),
    )
    .unwrap_or_default();
    let mut out = "## The room table (405 T113) - a fit failure: weigh more room within these ceilings before packing (B6)\n\nA room probe grows the BAND with the gap: a knob marked DOES NOT GROW, widened alone, deals the same seats into the same band - packing, not room.\n\n| knob | value | label | measures | research ceiling | the seating band |\n|---|---|---|---|---|---|\n".to_owned();
    let field = |r: &Value, k: &str| {
        r[k].as_str()
            .map_or_else(|| r[k].to_string(), str::to_owned)
    };
    for r in data["rows"].as_array().map_or(&[][..], Vec::as_slice) {
        let _ = writeln!(
            out,
            "| `{}` ({}) | {} | {} | {} | {} | {} |",
            field(r, "knob"),
            field(r, "where"),
            field(r, "value"),
            field(r, "label"),
            field(r, "measures"),
            field(r, "ceiling"),
            field(r, "band")
        );
    }
    out
}

pub(crate) fn render(root: &Path) -> crate::Reply {
    crate::Reply {
        stdout: table(root),
        stderr: String::new(),
        code: 0,
    }
}
