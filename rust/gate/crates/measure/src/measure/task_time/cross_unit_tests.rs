//! The cross-blocking's pieces (451 T510): the builder places, a tree's free spans, the refusals' rules and the pool's `done` rows.

use std::collections::HashMap;

use serde_json::json;

use super::super::super::where_time::columns::{Run, Runs, Split};
use super::super::book::{Attempt, Batch};
use super::super::held::Hold;
use super::{cap_of, dones, measure, refusals, Records, CAP};

fn hold(tree: &str, from: f64, until: f64) -> Hold {
    Hold {
        from,
        until,
        tree: tree.to_owned(),
        feature: "451".to_owned(),
        tasks: vec!["T1".to_owned()],
    }
}

fn landing(t0: f64, t1: f64) -> Batch {
    Batch {
        feature: "451-x".to_owned(),
        tasks: vec!["T1".to_owned()],
        attempts: vec![Attempt {
            t0,
            t1,
            ..Attempt::default()
        }],
        carried: Vec::new(),
    }
}

#[test]
fn the_builder_places_are_l7r_builders_else_three() {
    assert_eq!(
        (cap_of(Some(" 2 ")), cap_of(Some("x")), cap_of(None)),
        (2, CAP, CAP)
    );
}

/// Free trees count only up to the places left open, and a tree handed on in the same second was never free.
#[test]
fn a_free_tree_counts_only_while_a_place_is_open() {
    let holds = [
        hold("a", 0.0, 10.0),
        hold("a", 50.0, f64::INFINITY),
        hold("b", 0.0, 10.0),
        hold("b", 60.0, f64::INFINITY),
        hold("c", 0.0, f64::INFINITY),
        // handed on at once: no gap
        hold("d", 0.0, 20.0),
        hold("d", 20.0, f64::INFINITY),
    ];
    // one place open (c and d held): of a and b free, one counts, 20 to 40
    let one = measure(&holds, &[landing(20.0, 40.0)], &[], (0.0, 100.0), 3);
    assert!((one.idle - 20.0).abs() < 1e-9 && (one.both - 20.0).abs() < 1e-9);
    // no place open: nothing
    let none = measure(&holds, &[landing(20.0, 40.0)], &[], (0.0, 100.0), 2);
    assert!(none.idle.abs() < 1e-9, "{none:?}");
    // a refusal beside it: the larger, each second once
    let both = measure(
        &holds,
        &[landing(20.0, 40.0)],
        &[(30.0, 50.0)],
        (0.0, 100.0),
        4,
    );
    assert_eq!(both.n_refused, 1);
    assert!((both.idle - 40.0).abs() < 1e-9 && (both.refused - 20.0).abs() < 1e-9);
    assert!((both.both - 50.0).abs() < 1e-9, "{both:?}");
}

/// A tree freed in the window and handed out only after it counts the same before that handout is logged as after (461 T33: the
/// night's figure grew from 32.3 to 53.7 min as later handouts reached the pool's log): its free span ends at the window's end.
#[test]
fn a_free_span_open_at_the_windows_end_counts_to_it_whatever_follows() {
    let before = [hold("a", 0.0, 30.0), hold("b", 0.0, f64::INFINITY)];
    let after = [
        before[0].clone(),
        before[1].clone(),
        hold("a", 150.0, f64::INFINITY),
    ];
    let at = |holds: &[Hold]| measure(holds, &[landing(20.0, 80.0)], &[], (0.0, 100.0), 3).idle;
    let (read_then, read_later) = (at(&before), at(&after));
    let both = (read_then - 50.0).abs() < 1e-9 && (read_later - 50.0).abs() < 1e-9;
    assert!(both, "{read_then} {read_later}");
}

fn run(id: &str, by: &str, make: &str) -> Run {
    Run {
        id: id.to_owned(),
        t0: 100.0,
        t1: 101.0,
        sid: "s".to_owned(),
        by: by.to_owned(),
        bg_id: String::new(),
        makes: vec![make.to_owned()],
        bucket: "other",
        task: "T9".to_owned(),
        bg: false,
        open: false,
        split: Split::default(),
    }
}

/// A refusal is a main session's failed handout of a task with an uncarried done commit, to its next handout or carry.
#[test]
fn a_refusal_waits_from_its_failure_to_the_task_s_next_handout_or_carry() {
    let runs = Runs {
        runs: vec![
            run("a", "", "builder-tree"),
            run("b", "", "builder-brief"),
            run("c", "", "builder-tree"),
            run("d", "", "builder-tree"),
            run("e", "B1", "builder-tree"),
            run("f", "", "quick"),
            run("g", "", "builder-tree"),
            run("h", "", "builder-tree"),
        ],
        ..Runs::default()
    };
    let stream: Vec<_> = ["a", "b", "c", "d", "e", "f", "h"]
        .iter()
        .map(|id| {
            let v = json!({"ev": "PostToolUseFailure", "id": id});
            serde_json::from_value(v).unwrap()
        })
        .collect();
    let commands: HashMap<String, String> = [
        ("a", "make builder-tree T=T1 F=451"),
        ("b", "make builder-brief T=\"T2\" F=451"),
        ("c", "make builder-tree F=451"),
        ("d", "make builder-tree T=T3 F=451"),
        ("e", "make builder-tree T=T1 F=451"),
        ("f", "make quick T=T1"),
        ("g", "make builder-tree T=T1 F=451"),
        ("h", "make builder-tree T=T4 F=451"),
    ]
    .map(|(k, v)| (k.to_owned(), v.to_owned()))
    .into();
    let dones = vec![
        (50.0, vec!["T1".to_owned()]),
        (40.0, vec!["T1".to_owned()]),
        (50.0, vec!["T2".to_owned()]),
        (50.0, vec!["T4".to_owned()]),
    ];
    // T1 handed out at 130; T2 carried at 120; T4 carried at 60, before its refusal
    let takes = vec![(130.0, "t".to_owned(), "451 T1".to_owned())];
    let carried = vec![
        ("x".to_owned(), 120.0, "451 T2".to_owned()),
        ("y".to_owned(), 60.0, "451 T4".to_owned()),
    ];
    let r = Records {
        runs: &runs,
        stream: &stream,
        commands: &commands,
        dones: &dones,
        takes: &takes,
        carried: &carried,
    };
    // a: to T1's handout; b: to T2's carry; c names no task; d has no done; e is a builder's; f no handout; g did not fail;
    // h's commit was carried before it
    assert_eq!(refusals(&r, 500.0), [(100.0, 130.0), (100.0, 120.0)]);
    // no handout or carry after: to the window's end
    let late = Records {
        takes: &[],
        carried: &[],
        ..r
    };
    assert_eq!(refusals(&late, 500.0)[0], (100.0, 500.0));
}

/// The pool's `done` rows, each log read once, other rows and an unreadable time left out.
#[test]
fn the_done_rows_are_read_once_a_log() {
    let d = crate::checks::scratch("task-time-cross-dones");
    let git = d.join("root/.git");
    std::fs::create_dir_all(&git).unwrap();
    std::fs::write(
        git.join("builder-pool.log"),
        format!(
            "{}\n{}\n{}\nnot a row\n",
            json!({"utc": "2026-11-26T10:00:00Z", "event": "done", "detail": "451 T1,T2"}),
            json!({"utc": "2026-11-26T10:00:00Z", "event": "release", "detail": "451 T1"}),
            json!({"utc": "x", "event": "done", "detail": "451 T3"}),
        ),
    )
    .unwrap();
    let root = d.join("root");
    let rows = dones(&[root.clone(), root]);
    assert_eq!(rows.len(), 1);
    assert_eq!(rows[0].1, ["T1", "T2"]);
}
