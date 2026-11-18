//! The counted work of a run: basic operations by kind and by function (feature 449 T151, `l7r/diagram/work_counts.py`; feature 443,
//! D1-D3). The GM, 2026-10-27, `specs/443-work-budget-tooling/request.md`: the conversion is judged on "an algorithmically sensible number
//! of computations", so the work is counted in units that survive a port - a candidate tried, an index query - keyed `<kind>@<function>`.
//!
//! WHY PER THREAD: the Python's `OPS` was one module-level dict, filled under `if __debug__:` and so never in a deployed run; here each
//! thread counts its own, so the crate's tests, which run in parallel, never read one another's counts. `BY_STAGE` is not carried: its
//! one filler was the hamlet engine's driver, deleted with the Python hamlet engine (feature 444); the Rust stages count their own
//! (`rust/phases`).
//!
//! Research: plumbing - NONE: it counts, and decides nothing about the place

use std::cell::RefCell;
use std::collections::BTreeMap;

/// The kinds a key may open with.
pub const KINDS: [&str; 9] = [
    "pt_test",
    "seg_test",
    "dist",
    "index_query",
    "index_examined",
    "candidate",
    "placed",
    "dropped",
    "moved",
];

thread_local! {
    static OPS: RefCell<BTreeMap<String, u64>> = const { RefCell::new(BTreeMap::new()) };
}

/// `OPS[key] += n`.
pub fn count(key: &str, n: u64) {
    // the key is copied only the first time it is counted: a strict search counts every seat it refuses (`Obstacles.blocked`)
    OPS.with(|ops| {
        let mut ops = ops.borrow_mut();
        match ops.get_mut(key) {
            Some(v) => *v += n,
            None => drop(ops.insert(key.to_owned(), n)),
        }
    });
}

/// Every counted operation of this thread so far, keyed `<kind>@<function>`.
#[must_use]
pub fn ops() -> BTreeMap<String, u64> {
    OPS.with(|ops| ops.borrow().clone())
}

/// Clear the counts at the start of a run.
pub fn reset() {
    OPS.with(|ops| ops.borrow_mut().clear());
}

/// `counts` summed over functions, by kind.
#[must_use]
pub fn by_kind(counts: &BTreeMap<String, u64>) -> BTreeMap<String, u64> {
    let mut out = BTreeMap::new();
    for (key, n) in counts {
        let kind = key.split('@').next().unwrap_or_default();
        *out.entry(kind.to_owned()).or_insert(0) += n;
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{by_kind, count, ops, reset, KINDS};

    #[test]
    fn a_thread_counts_its_own_work_by_kind() {
        reset();
        count("candidate@a", 2);
        count("candidate@b", 1);
        count("dist@a", 4);
        let got = by_kind(&ops());
        assert_eq!((got["candidate"], got["dist"]), (3, 4));
        assert!(KINDS.contains(&"candidate"));
        std::thread::spawn(|| assert!(ops().is_empty()))
            .join()
            .unwrap();
        reset();
        assert!(ops().is_empty());
    }
}
