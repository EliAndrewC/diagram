//! THE HALVING (feature 461 T24, plan D6 steps 3 and 5, its table; US4, FR-004): which set a red batch runs next where the gate's
//! record cannot place its red, and what each result means. Pure, over the changes' indices in hand-in order; `runner/run.rs` carries,
//! gates and pushes each set as any attempt, and ejects what this names.
//!
//! THE RULES, each labeled:
//! - The changes in hand-in order; the FIRST HALF is the first `len / 2` of a set (D6's table: `[A B C]` runs `[A]`, then `[B]`) and
//!   runs as a batch of its own. A green half is pushed at once (it was gated exactly as it lands, Zuul's rule). D6, literal.
//! - A red half is halved again; its second half waits on the first's run. Where the first is green, the second is red WITHOUT a run
//!   of its own (its parent was red on the main the first now lands on) and is halved in turn; where the first is red, the second is
//!   untested and runs. D6's table, literal.
//! - A change left alone in a set known red by inference is ejected without a run (`why` `inferred`) once every other change has
//!   landed or been ejected: D6's "the one left after every other change landed green", the table's `[D E F]` run before C is
//!   ejected. Where two bad changes leave two such singles (the plan is silent), each is ejected `inferred`, in hand-in order, at
//!   the end: the easier route.
//! - A change whose own one-change run is red is ejected at once (`why` `red`: that red is its alone), and so is a one-change set
//!   whose first red run was its own (a one-change batch).
//! - THE REST RUNS AS ONE: untested sets that stand next to each other at the front run together (after a `red` ejection, the
//!   ejected change's untested sibling and the untested other half). D6 step 2's "it is ejected and the rest runs again"; without it
//!   n = 4 with A bad took 4 runs and n = 6 with B bad took 5, past US4's ceil(log2 n) + 1 (counted by
//!   `tests::every_single_bad_change_of_n_1_to_8_is_found_within_the_bound`).
//! - NO RETRY OF A FLAKE: a red set is run again [`LANE_RETRY`] times before it is read red (D6 step 5).
//!
//! Each `Ran`, `Inferred` and `Sibling` carries the run the knowledge rests on (`n`): an `inferred` ejection's repair names that
//! attempt's file, so the tripwire's ask (`crate::tripwire::files`) gets the attempt its red rests on.

use std::collections::VecDeque;

/// How often a red set is run again before it is read red: none (GUESS knob, D6 step 5; Gas Town's `retry_flaky_tests` priced: a
/// flake costs one halving step, a retry a whole run on every true red).
pub const LANE_RETRY: usize = 0;

/// What is known of a set.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Known {
    /// Run as a set of its own and red, at run `n`.
    Ran(usize),
    /// Red without a run of its own: its parent red at run `n`, the first half beside it green.
    Inferred(usize),
    /// The second half of a set red at run `n`, waiting on the first half's run.
    Sibling(usize),
    Unknown,
}

/// Why a change leaves the batch, as its `eject` line writes it.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Why {
    Red,
    Inferred,
}

impl Why {
    #[must_use]
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Red => "red",
            Self::Inferred => "inferred",
        }
    }
}

/// The halving's next step.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Next {
    /// Run these changes as an attempt, then [`Halving::record`] its result.
    Run(Vec<usize>),
    /// Eject this change, its red resting on run `at`.
    Eject { change: usize, why: Why, at: usize },
    /// Every change landed or ejected.
    Done,
}

/// A halving in progress (the module's doc).
#[derive(Debug, Clone)]
pub struct Halving {
    sets: VecDeque<(Vec<usize>, Known)>,
    /// The singles known red by inference, ejected at the end.
    left: VecDeque<(usize, usize)>,
    retry: usize,
    tries: usize,
}

impl Halving {
    /// The halving of `changes`, which ran together red at run `n`, with `retry` runs again of a red set.
    #[must_use]
    pub fn new(changes: Vec<usize>, n: usize, retry: usize) -> Self {
        Self {
            sets: VecDeque::from([(changes, Known::Ran(n))]),
            left: VecDeque::new(),
            retry,
            tries: 0,
        }
    }

    /// The next step; a [`Next::Run`] is answered again, unchanged, until its result is recorded.
    pub fn advance(&mut self) -> Next {
        while let Some((set, known)) = self.sets.pop_front() {
            match known {
                Known::Unknown | Known::Sibling(_) => {
                    let mut run = set;
                    while let Some((more, Known::Unknown)) = self.sets.front() {
                        run.extend(more);
                        self.sets.pop_front();
                    }
                    self.sets.push_front((run.clone(), Known::Unknown));
                    return Next::Run(run);
                }
                Known::Ran(at) if set.len() == 1 => {
                    return Next::Eject {
                        change: set[0],
                        why: Why::Red,
                        at,
                    }
                }
                Known::Inferred(at) if set.len() == 1 => self.left.push_back((set[0], at)),
                Known::Ran(at) | Known::Inferred(at) => {
                    let (first, second) = set.split_at(set.len() / 2);
                    self.sets.push_front((second.to_vec(), Known::Sibling(at)));
                    self.sets.push_front((first.to_vec(), Known::Unknown));
                }
            }
        }
        self.left
            .pop_front()
            .map_or(Next::Done, |(change, at)| Next::Eject {
                change,
                why: Why::Inferred,
                at,
            })
    }

    /// The last [`Next::Run`]'s result: green (pushed), or red at run `n` - read red only past its retries.
    pub fn record(&mut self, green: bool, n: usize) {
        if !green && self.tries < self.retry {
            self.tries += 1;
            return;
        }
        self.tries = 0;
        let Some((set, _)) = self.sets.pop_front() else {
            return;
        };
        if !green {
            self.sets.push_front((set, Known::Ran(n)));
        }
        let at = usize::from(!green);
        // the set beside a finished run is its sibling or none (every bad subset of n = 1 to 6 driven, 2026-11-28): one test of both
        if let Some((_, Known::Sibling(m))) = self.sets.get(at) {
            let m = *m;
            self.sets[at].1 = if green {
                Known::Inferred(m)
            } else {
                Known::Unknown
            };
        }
    }
}

#[cfg(test)]
mod tests;
