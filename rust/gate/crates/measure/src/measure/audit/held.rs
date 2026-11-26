//! `make audit`'s count of the plan gate's escapes (`PLAN_REVIEW_OK`) by what the gate held, read from each record's `held` list -
//! the `{feature, rule, blocks}` rows the plan gate writes where it honors the escape (`bypass_record`, the plan crate) - and never
//! from its reason.
//!
//! WHY (feature 451 T270): the reason is the session's wording, a standing one carried from push to push. 451 T261's builder,
//! reading reasons, counted 60% of the escapes as unstarted tasks' template stubs; replayed at their commits (2026-11-26, 12
//! records) the gate held no such stub in any and nothing at all in 7, and T261 was withdrawn on it.
//!
//! The classes are the shapes the record has. It names the place (`plan-gate push`, `plan-gate tick <feature>`), not the task
//! asked for, so which task owns a held block is not in it: the place says what the gate judged there (451 T84) - at a push the
//! ticked tasks' sections, at a tick the asked task's and those ticked before it, at both the blocks outside every task's section.

use serde_json::Value;

/// What one honored escape's record says the gate held.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub(super) enum Class {
    /// No `held` list: a record written before 451 T262, or a push recorded with no range.
    NotRecorded,
    /// An empty list: the gate listed no feature.
    Nothing,
    /// Rows, none with a block: `plan-missing` or `plan-review-missing`, where the gate lists no block.
    NoBlock,
    /// A block held at a push.
    Push,
    /// A block held at a tick.
    Tick,
}

/// Every class, in the order the count prints them.
const ALL: [Class; 5] = [
    Class::NotRecorded,
    Class::Nothing,
    Class::NoBlock,
    Class::Push,
    Class::Tick,
];

impl Class {
    const fn label(self) -> &'static str {
        match self {
            Self::NotRecorded => "held not recorded (a record before 451 T262)",
            Self::Nothing => "nothing held",
            Self::NoBlock => "a plan or its review record missing, no block listed",
            Self::Push => "at a push: blocks held, of ticked tasks or outside every task",
            Self::Tick => "at a tick: blocks held, of the asked task, of tasks ticked before it or outside every task",
        }
    }
}

/// The class of a bypass record; None for a record of another escape (the plan gate's `decide-defer` among them, which is the
/// decide lint's `DEFER_FORM_OK` and carries no `held`).
pub(super) fn class(record: &Value) -> Option<Class> {
    let target = record.get("target").and_then(Value::as_str)?;
    let tick = target.starts_with("plan-gate tick ");
    if !tick && target != "plan-gate push" {
        return None;
    }
    let Some(rows) = record.get("held").and_then(Value::as_array) else {
        return Some(Class::NotRecorded);
    };
    if rows.is_empty() {
        return Some(Class::Nothing);
    }
    let block = rows.iter().any(|row| {
        row.get("blocks")
            .and_then(Value::as_array)
            .is_some_and(|blocks| !blocks.is_empty())
    });
    Some(match (block, tick) {
        (false, _) => Class::NoBlock,
        (true, false) => Class::Push,
        (true, true) => Class::Tick,
    })
}

/// The count's lines over every bypass record: none where no record is a plan-gate escape, else a heading and each class's count.
pub(super) fn lines(records: &[Value]) -> Vec<String> {
    let classes: Vec<Class> = records.iter().filter_map(class).collect();
    if classes.is_empty() {
        return Vec::new();
    }
    let mut out = vec![format!(
        "  PLAN_REVIEW_OK escapes by what the plan gate held (each record's `held` list, never its reason) - {} records",
        classes.len()
    )];
    for c in ALL {
        let n = classes.iter().filter(|k| **k == c).count();
        out.push(format!("  {n:>6}  {}", c.label()));
    }
    out
}
