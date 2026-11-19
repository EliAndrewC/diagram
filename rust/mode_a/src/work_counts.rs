//! The counted work of a run: basic operations by kind and by function (feature 449 T151, `l7r/diagram/work_counts.py`; feature 443,
//! D1-D3). The GM, 2026-10-27, `specs/443-work-budget-tooling/request.md`: the conversion is judged on "an algorithmically sensible number
//! of computations", so the work is counted in units that survive a port - a candidate tried, an index query - keyed `<kind>@<function>`.
//!
//! WHY PER THREAD: the Python's `OPS` was one module-level dict, filled under `if __debug__:` and so never in a deployed run; here each
//! thread counts its own, so the crate's tests, which run in parallel, never read one another's counts. `BY_STAGE` is not carried: its
//! one filler was the hamlet engine's driver, deleted with the Python hamlet engine (feature 444); the Rust stages count their own
//! (`rust/phases`).
//!
//! COMPILED OUT BY DEFAULT (feature 449 T198, as `rust/phases`' `counters` feature, 444 FR-012; the GM 2026-11-07: "We should probably run
//! with counters compiled out by default"): [`count`] counts only in a build with the crate's `counters` feature, the Rust form of the
//! Python's `if __debug__:`; every other build's counts are empty. The caption placer's counters are statements gated on the feature, so a
//! drawing build compiles none of them; `l7r-mode-a caption-counts`, a command of the counting build alone, reads them per caption
//! ([`scope`], [`by_scope`]).
//!
//! Research: plumbing - NONE: it counts, and decides nothing about the place

use std::cell::RefCell;
use std::collections::BTreeMap;

/// The kinds a key may open with: the Python's, and (T198) the caption placer's - a function's `call`, a `stage` of the search entered,
/// the seats `built` and those skipped (`skip`) or scored (`seat`), what an index holds when it is asked (`held`), the grid cells it reads
/// (`cell`), the entries it found measured exactly (`exact`), an index or ink `build`, a `leader` measured, and the greedy pass's `repair`.
pub const KINDS: [&str; 20] = [
    "pt_test",
    "seg_test",
    "dist",
    "index_query",
    "index_examined",
    "candidate",
    "placed",
    "dropped",
    "moved",
    "call",
    "stage",
    "built",
    "skip",
    "seat",
    "held",
    "build",
    "leader",
    "repair",
    "cell",
    "exact",
];

thread_local! {
    static OPS: RefCell<BTreeMap<String, u64>> = const { RefCell::new(BTreeMap::new()) };
}

/// Each scope's counts, in the order the scopes were opened, and the one counting now.
#[cfg(feature = "counters")]
type Scopes = (Vec<(String, BTreeMap<String, u64>)>, Option<usize>);

#[cfg(feature = "counters")]
thread_local! {
    static SCOPES: RefCell<Scopes> = const { RefCell::new((Vec::new(), None)) };
}

/// `OPS[key] += n` - and the open scope's too ([`scope`]) - in a build with the `counters` feature; nothing in any other (T198).
pub fn count(key: &str, n: u64) {
    #[cfg(feature = "counters")]
    {
        // the key is copied only the first time it is counted: a strict search counts every seat it refuses (`Obstacles.blocked`)
        fn add(ops: &mut BTreeMap<String, u64>, key: &str, n: u64) {
            match ops.get_mut(key) {
                Some(v) => *v += n,
                None => drop(ops.insert(key.to_owned(), n)),
            }
        }
        OPS.with(|ops| add(&mut ops.borrow_mut(), key, n));
        SCOPES.with(|s| {
            let mut s = s.borrow_mut();
            if let Some(at) = s.1 {
                add(&mut s.0[at].1, key, n);
            }
        });
    }
    #[cfg(not(feature = "counters"))]
    let _ = (key, n);
}

/// Count into the scope `name` from here on, as well as into the run's: a caption's search, keyed by what the caller names it. A name
/// opened again counts on where it left off.
#[cfg(feature = "counters")]
pub fn scope(name: &str) {
    SCOPES.with(|s| {
        let mut s = s.borrow_mut();
        let at = s.0.iter().position(|(n, _)| n == name).unwrap_or_else(|| {
            s.0.push((name.to_owned(), BTreeMap::new()));
            s.0.len() - 1
        });
        s.1 = Some(at);
    });
}

/// Every scope's counts on this thread so far, in the order the scopes were opened.
#[cfg(feature = "counters")]
#[must_use]
pub fn by_scope() -> Vec<(String, BTreeMap<String, u64>)> {
    SCOPES.with(|s| s.borrow().0.clone())
}

/// Every counted operation of this thread so far, keyed `<kind>@<function>`.
#[must_use]
pub fn ops() -> BTreeMap<String, u64> {
    OPS.with(|ops| ops.borrow().clone())
}

/// Clear the counts at the start of a run - the scopes too, none left open.
pub fn reset() {
    OPS.with(|ops| ops.borrow_mut().clear());
    #[cfg(feature = "counters")]
    SCOPES.with(|s| *s.borrow_mut() = (Vec::new(), None));
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
    use std::collections::BTreeMap;

    use super::{by_kind, count, ops, reset, KINDS};

    #[test]
    fn counts_sum_by_kind() {
        let counts = BTreeMap::from([
            ("candidate@a".to_owned(), 2),
            ("candidate@b".to_owned(), 1),
            ("dist@a".to_owned(), 4),
        ]);
        let got = by_kind(&counts);
        assert_eq!((got["candidate"], got["dist"]), (3, 4));
        assert!(KINDS.contains(&"candidate"));
    }

    /// Counted only in the counting build: a drawing build's counts stay empty (T198).
    #[test]
    fn a_thread_counts_its_own_work_in_the_counting_build_alone() {
        reset();
        count("candidate@a", 2);
        count("dist@a", 4);
        let got = ops();
        #[cfg(feature = "counters")]
        assert_eq!((got["candidate@a"], got["dist@a"]), (2, 4));
        #[cfg(not(feature = "counters"))]
        assert!(got.is_empty());
        std::thread::spawn(|| assert!(ops().is_empty()))
            .join()
            .unwrap();
        reset();
        assert!(ops().is_empty());
    }

    /// A scope counts what is counted while it is open, the run's counts all of it; a scope opened again counts on (T198).
    #[cfg(feature = "counters")]
    #[test]
    fn a_scope_counts_what_is_counted_while_it_is_open() {
        use super::{by_scope, scope};
        reset();
        count("seat@a", 1);
        scope("first");
        count("seat@a", 2);
        scope("second");
        count("seat@a", 3);
        scope("first");
        count("dist@b", 5);
        let got = by_scope();
        assert_eq!(got.len(), 2);
        assert_eq!(
            (got[0].0.as_str(), got[0].1["seat@a"], got[0].1["dist@b"]),
            ("first", 2, 5)
        );
        assert_eq!((got[1].0.as_str(), got[1].1["seat@a"]), ("second", 3));
        assert_eq!(ops()["seat@a"], 6);
        reset();
        assert!(by_scope().is_empty());
    }
}
