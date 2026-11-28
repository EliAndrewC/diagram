//! The halving's rules on indices alone (461 T24): D6's table, every single bad change of n = 1 to 8 within US4's bound, two bad
//! changes, the retry knob.

use super::{Halving, Next, Why, LANE_RETRY};

/// The sets a halving ran and its ejections, each with the run its red rests on.
type Driven = (Vec<Vec<usize>>, Vec<(usize, Why, usize)>);

/// The halving of `n` changes run to its end, a set red where it holds one of `bad` (or where `flaky` says so, once a set): the sets
/// run and the ejections, each with the run its red rests on.
fn drive(n: usize, bad: &[usize], retry: usize, flaky: &mut dyn FnMut(&[usize]) -> bool) -> Driven {
    let mut h = Halving::new((0..n).collect(), 1, retry);
    let (mut runs, mut out) = (Vec::new(), Vec::new());
    loop {
        match h.advance() {
            Next::Run(set) => {
                let green = !set.iter().any(|c| bad.contains(c)) && !flaky(&set);
                runs.push(set);
                h.record(green, runs.len() + 1);
            }
            Next::Eject { change, why, at } => out.push((change, why, at)),
            Next::Done => return (runs, out),
        }
    }
}

fn never(_: &[usize]) -> bool {
    false
}

#[test]
fn d6_s_table_row_by_row() {
    let (runs, out) = drive(4, &[1], 0, &mut never);
    assert_eq!(runs, [vec![0, 1], vec![0], vec![2, 3]]);
    assert_eq!(out, [(1, Why::Inferred, 2)]);
    let (runs, out) = drive(4, &[3], 0, &mut never);
    assert_eq!(runs, [vec![0, 1], vec![2]]);
    assert_eq!(out, [(3, Why::Inferred, 1)]);
    let (runs, out) = drive(4, &[2], 0, &mut never);
    assert_eq!(runs, [vec![0, 1], vec![2], vec![3]]);
    assert_eq!(out, [(2, Why::Red, 3)]);
    let (runs, out) = drive(6, &[2], 0, &mut never);
    assert_eq!(runs, [vec![0, 1, 2], vec![0], vec![1], vec![3, 4, 5]]);
    assert_eq!(out, [(2, Why::Inferred, 2)]);
    let (runs, out) = drive(6, &[5], 0, &mut never);
    assert_eq!(runs, [vec![0, 1, 2], vec![3], vec![4]]);
    assert_eq!(out, [(5, Why::Inferred, 1)]);
    let (runs, out) = drive(6, &[4], 0, &mut never);
    assert_eq!(runs, [vec![0, 1, 2], vec![3], vec![4], vec![5]]);
    assert_eq!(out, [(4, Why::Red, 4)]);
}

#[test]
fn every_single_bad_change_of_n_1_to_8_is_found_within_the_bound() {
    for n in 1..=8_usize {
        let bound = n.next_power_of_two().trailing_zeros() as usize + 1;
        for b in 0..n {
            let (runs, out) = drive(n, &[b], 0, &mut never);
            assert!(runs.len() <= bound, "n {n} bad {b}: {runs:?}");
            assert_eq!(out.len(), 1, "n {n} bad {b}");
            assert_eq!(out[0].0, b);
            // every good change ran green exactly once in a set of its own landing
            let last: Vec<usize> = runs
                .iter()
                .filter(|s| !s.contains(&b))
                .flatten()
                .copied()
                .collect();
            assert_eq!(last.len(), n - 1, "n {n} bad {b}: {runs:?}");
        }
    }
}

#[test]
fn a_one_change_batch_red_on_its_own_run_is_ejected_red_with_no_run() {
    let (runs, out) = drive(1, &[0], 0, &mut never);
    assert!(runs.is_empty());
    assert_eq!(out, [(0, Why::Red, 1)]);
}

#[test]
fn two_bad_changes_left_alone_by_inference_are_each_ejected_inferred_at_the_end() {
    // [0 1 2] red, [0] green, [1 2] inferred red: [1] red, ejected; [2 3 4 5] red, halved again
    let (runs, out) = drive(6, &[1, 4], 0, &mut never);
    assert!(out.iter().any(|&(c, _, _)| c == 1));
    assert!(out.iter().any(|&(c, _, _)| c == 4));
    assert_eq!(out.len(), 2, "{runs:?}");
    let (_, out) = drive(4, &[1, 3], 0, &mut never);
    assert_eq!(out, [(1, Why::Inferred, 2), (3, Why::Inferred, 4)]);
}

#[test]
fn a_flake_is_run_again_only_as_often_as_the_retry_knob_says() {
    assert_eq!(LANE_RETRY, 0);
    // the first run of [0 1] flakes: with no retry, it is halved and 1 is ejected by inference, the cost the knob accepts; with one,
    // it runs again green and lands whole
    let mut once = true;
    let mut flake = |s: &[usize]| s.len() == 2 && std::mem::take(&mut once);
    let (runs, out) = drive(4, &[3], 0, &mut flake);
    assert_eq!(runs, [vec![0, 1], vec![0], vec![2, 3], vec![2]]);
    assert_eq!(out, [(1, Why::Inferred, 2), (3, Why::Inferred, 4)]);
    let mut once = true;
    let mut flake = |s: &[usize]| s.len() == 2 && std::mem::take(&mut once);
    let (runs, out) = drive(4, &[3], 1, &mut flake);
    assert_eq!(runs, [vec![0, 1], vec![0, 1], vec![2]]);
    assert_eq!(out, [(3, Why::Inferred, 1)]);
}

#[test]
fn a_result_recorded_with_nothing_run_changes_nothing() {
    let mut h = Halving::new(vec![0], 1, 0);
    assert_eq!(
        h.advance(),
        Next::Eject {
            change: 0,
            why: Why::Red,
            at: 1
        }
    );
    h.record(true, 2);
    assert_eq!(h.advance(), Next::Done);
    assert_eq!(
        (Why::Red.as_str(), Why::Inferred.as_str()),
        ("red", "inferred")
    );
}

/// Every set of bad changes of n = 1 to 6 (each non-empty subset: a halving starts from a batch already red, so at least one is bad):
/// each ends with exactly its bad changes ejected, each once - the sets beside a finished run in every state they can be in, not only
/// a halving's sibling.
#[test]
fn every_set_of_bad_changes_of_n_1_to_6_ejects_exactly_those() {
    for n in 1..=6_usize {
        for mask in 1..(1_u32 << n) {
            let bad: Vec<usize> = (0..n).filter(|&c| mask & (1 << c) != 0).collect();
            let (_, out) = drive(n, &bad, 0, &mut never);
            let mut ejected: Vec<usize> = out.iter().map(|&(c, _, _)| c).collect();
            ejected.sort_unstable();
            assert_eq!(ejected, bad);
        }
    }
}
