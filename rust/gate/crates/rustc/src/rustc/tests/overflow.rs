//! The lane's overflow (feature 451 T425): a build told alone that finds the small lane held takes a wide slot free at that
//! instant, never a place in the wide queue; with the lane and every wide slot held it waits for whichever frees first.

use std::collections::BTreeMap;
use std::path::Path;
use std::sync::mpsc::channel;
use std::time::Duration;

use super::alone::{fixture, since};
use super::phases::phases;
use super::runlock::Stepped;
use super::slot::{quick, quiet, telling};
use super::{world_with, World};
use crate::checks::scratch;
use crate::rustc::slot::{around_small, take, take_or, Slots, SMALL, USE};
use l7r_shared::tempdir::Held;

/// A world of two wide slots and a lane one wide under `dir`, the lane's waits looked at by `lane` (its ceiling `ceiling` s).
fn world(root: &Path, dir: &Path, lane: Slots, ceiling: u64) -> Held<World> {
    world_with(root, "exit 0").map(|w| World {
        slots: quick(dir, 2),
        small: Slots {
            ceiling: Duration::from_secs(ceiling),
            stem: "small",
            knob: SMALL,
            ..lane
        },
        ..w
    })
}

/// The lane's one place, held.
fn lane_held(dir: &Path) -> Option<crate::rustc::slot::Hold> {
    let lane = Slots {
        stem: "small",
        ..quick(dir, 1)
    };
    take(&lane, "lane\n", &mut quiet).hold
}

fn signed(dir: &Path, name: &str) -> String {
    std::fs::read_to_string(dir.join(name)).unwrap_or_default()
}

const ARGS: [&str; 2] = ["test", "--no-run"];

fn args() -> Vec<String> {
    ARGS.map(str::to_owned).to_vec()
}

#[test]
fn a_build_told_alone_that_finds_the_lane_held_takes_a_free_wide_slot_at_once() {
    let (root, a) = fixture();
    let dir = scratch("overflow-free");
    // a lane that waits 2 s at most: the old code's wait for it ends there, without a slot
    let world = world(&root, &dir, quick(&dir, 1), 2);
    let lane = lane_held(&dir);
    let one = take(&quick(&dir, 2), "one\n", &mut quiet).hold;
    assert!(lane.is_some() && one.is_some());
    let mut env = BTreeMap::new();
    let held = around_small(&world, &a, &args(), &mut env);
    assert!(held.is_some());
    // at once: no `slot-wait` line, and the lane's line says a wide slot was taken (code 2)
    assert_eq!(since(&root, 0), [format!("{USE} 2")]);
    let wide = [signed(&dir, "slot-0"), signed(&dir, "slot-1")];
    assert!(wide.contains(&"one\n".to_owned()));
    assert!(wide.iter().any(|w| w.ends_with("cargo test --no-run\n")));
    assert_eq!(signed(&dir, "small-0"), "lane\n");
    assert_eq!(
        env.get("L7R_BUILD_SLOT_HELD").map(String::as_str),
        Some("1")
    );
}

#[test]
fn with_the_lane_and_both_wide_slots_held_it_waits_and_takes_whichever_frees_first() {
    let (root, a) = fixture();
    let dir = scratch("overflow-wait");
    let one = take(&quick(&dir, 2), "one\n", &mut quiet).hold;
    let two = take(&quick(&dir, 2), "two\n", &mut quiet).hold;
    let lane = lane_held(&dir);
    assert!(one.is_some() && two.is_some() && lane.is_some());
    // a wide slot frees first: it is the waiter's, and its wait a `slot-wait 0` line before the lane's `slot-small 2`
    let (slots, waiting) = telling(&dir, 1);
    let patient = world(&root, &dir, slots, 10);
    let (tell, done) = channel();
    std::thread::scope(|s| {
        s.spawn(|| {
            let mut env = BTreeMap::new();
            let _ = tell.send(around_small(&patient, &a, &args(), &mut env).is_some());
        });
        waiting.recv_timeout(Duration::from_secs(30)).unwrap();
        assert!(done.try_recv().is_err());
        drop(one);
        assert!(done.recv_timeout(Duration::from_secs(30)).unwrap());
    });
    assert_eq!(
        since(&root, 0),
        ["slot-wait 0".to_owned(), format!("{USE} 2")]
    );
    assert_eq!(signed(&dir, "small-0"), "lane\n");
    // held again, all three: now the lane frees first, and the waiter takes the lane (`slot-small 0`)
    let one = take(&quick(&dir, 2), "one\n", &mut quiet).hold;
    assert!(one.is_some());
    let before = phases(&root).len();
    let (slots, waiting) = telling(&dir, 1);
    let patient = world(&root, &dir, slots, 10);
    let (tell, done) = channel();
    std::thread::scope(|s| {
        s.spawn(|| {
            let mut env = BTreeMap::new();
            let _ = tell.send(around_small(&patient, &a, &args(), &mut env).is_some());
        });
        waiting.recv_timeout(Duration::from_secs(30)).unwrap();
        assert!(done.try_recv().is_err());
        drop(lane);
        assert!(done.recv_timeout(Duration::from_secs(30)).unwrap());
    });
    assert_eq!(
        since(&root, before),
        ["slot-wait 0".to_owned(), format!("{USE} 0")]
    );
    assert!(signed(&dir, "small-0").ends_with("cargo test --no-run\n"));
    let mut wide = [signed(&dir, "slot-0"), signed(&dir, "slot-1")];
    wide.sort_unstable();
    assert_eq!(wide, ["one\n".to_owned(), "two\n".to_owned()]);
    drop((one, two));
}

#[test]
fn a_wait_on_the_lane_and_the_wide_slots_names_every_holder_and_ends_at_the_lane_s_ceiling() {
    let (root, a) = fixture();
    let dir = scratch("overflow-ceiling");
    let one = take(&quick(&dir, 2), "one\n", &mut quiet).hold;
    let two = take(&quick(&dir, 2), "two\n", &mut quiet).hold;
    let lane = lane_held(&dir);
    assert!(one.is_some() && two.is_some() && lane.is_some());
    let slow = Slots {
        poll: Duration::from_secs(30),
        clock: Box::new(Stepped::default()),
        ..quick(&dir, 1)
    };
    let world = world(&root, &dir, slow, 90);
    let mut env = BTreeMap::new();
    assert!(around_small(&world, &a, &args(), &mut env).is_none());
    assert!(env.is_empty());
    assert_eq!(
        since(&root, 0),
        ["slot-wait 1".to_owned(), format!("{USE} 1")]
    );
    drop((one, two, lane));
}

#[test]
fn a_wait_on_both_names_every_holder_of_each_and_the_lane_s_knob() {
    let dir = scratch("overflow-said");
    let held = [(); 2].map(|()| take(&quick(&dir, 2), "wide\n", &mut quiet).hold);
    let lane = lane_held(&dir);
    assert!(held.iter().all(Option::is_some) && lane.is_some());
    let slow = Slots {
        ceiling: Duration::from_secs(90),
        poll: Duration::from_secs(30),
        clock: Box::new(Stepped::default()),
        stem: "small",
        knob: SMALL,
        ..quick(&dir, 1)
    };
    let mut said = Vec::new();
    let (taken, wide) = take_or(&slow, Some(&quick(&dir, 2)), "me\n", &mut |l| {
        said.push(l.to_owned());
    });
    assert!(taken.hold.is_none() && taken.waited.is_some() && !wide);
    assert_eq!(said, [
        "rust-checks: waiting on a build slot, 60 s so far - 1 compiling cargo call(s) run at once on this machine (L7R_BUILD_SLOTS_SMALL, feature 451 T284); held by: lane; wide; wide\n",
        "rust-checks: waited 90 s on a build slot, the ceiling (L7R_BUILD_SLOT_CEILING seconds) - this cargo call runs without one; held by: lane; wide; wide\n",
    ]);
    // a wide set that cannot be asked is no slot of its own, never a run without: the wait goes on to the lane's ceiling
    let broken = Slots {
        flock: "/nonexistent/flock".to_owned(),
        ..quick(&dir, 2)
    };
    let slow = Slots {
        poll: Duration::from_secs(30),
        clock: Box::new(Stepped::default()),
        stem: "small",
        ..quick(&dir, 1)
    };
    let (taken, _) = take_or(&slow, Some(&broken), "me\n", &mut quiet);
    assert_eq!(taken.waited, Some(Duration::from_secs(900)));
    drop((held, lane));
}
