//! Feature 451 T522 (c): a landed task's counted lines listed, a pool tree's pre-warm booked by its own task.

use std::collections::HashMap;

use super::super::super::where_time::columns::ran::{Kind, Ran};
use super::super::super::where_time::columns::Runs;
use super::super::book::{book, World};
use super::listing;

fn ran(kind: Kind, step: &str, (t0, t1): (f64, f64), task: &str) -> Ran {
    Ran {
        kind,
        step: step.to_owned(),
        t0,
        t1,
        tree: "pool-a".to_owned(),
        make: "builder-checks".to_owned(),
        crates: "rust/guard".to_owned(),
        key: ("451-x".to_owned(), task.to_owned()),
        said: None,
    }
}

/// A pre-warm in the window is booked under its line's task, one outside it under none; the listing names each kind in start order.
#[test]
fn a_tasks_counted_lines_are_listed_by_start() {
    let runs = Runs {
        prewarm: vec![
            ran(Kind::Compile, "prewarm", (5.0, 5.5), "T1"),
            ran(Kind::Compile, "prewarm", (50.0, 60.0), "T1"),
        ],
        ..Runs::default()
    };
    let world = World {
        stream: &[],
        runs: &runs,
        commands: &HashMap::new(),
        agents: &[],
        pages: &[],
        window: (0.0, 20.0),
        batches: &[],
        carried: &HashMap::new(),
    };
    let mut l = book(&world).unwrap();
    let key = ("451-x".to_owned(), "T1".to_owned());
    let booked = l.ran.get_mut(&key).unwrap();
    assert_eq!(booked.len(), 1);
    booked.push(ran(Kind::Coverage, "cover-run", (2.0, 3.0), "T1"));
    booked.push(ran(Kind::UnitTest, "test", (1.0, 2.0), "T1"));
    let mut out = String::new();
    listing(&mut out, &l, &key);
    let rows: Vec<&str> = out.lines().filter(|r| r.starts_with("| 01-01")).collect();
    let want = [
        "| 01-01T00:00:01 | pool-a | builder-checks | test | rust/guard | 1.0 | unit-test run |",
        "| 01-01T00:00:02 | pool-a | builder-checks | cover-run | rust/guard | 1.0 | coverage run |",
        "| 01-01T00:00:05 | pool-a | builder-checks | prewarm | rust/guard | 0.5 | compile, under 1.0 s |",
    ];
    assert_eq!(rows, want);
    // a task with none lists nothing
    let mut none = String::new();
    listing(&mut none, &l, &("451-x".to_owned(), "T2".to_owned()));
    assert_eq!(none, "");
}
