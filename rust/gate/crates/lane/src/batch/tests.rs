//! D5's batch (feature 461 T14): the oldest waiting and its feature's run after it, each cut - another feature, a hand-in held behind
//! an open batch, the cap - the no-pull-forward rule, and the id counting up per feature.

use std::collections::BTreeSet;

use serde_json::json;

use super::{form, next_id, LANE_MAX};
use crate::log::{self, HandIn, World};

fn h(feature: &str, tasks: &[&str], commit: &str) -> HandIn {
    HandIn {
        feature: feature.to_owned(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
        commit: commit.to_owned(),
        at: String::new(),
        repair_of: None,
    }
}

fn formed(hand_ins: &[HandIn], lane: &[serde_json::Value], max: usize) -> Vec<String> {
    let on_main = BTreeSet::new();
    let batches = log::batches(lane);
    let w = World {
        hand_ins,
        all: hand_ins,
        on_main: &on_main,
        log: lane,
        batches: &batches,
    };
    form(&w, max).iter().map(|h| h.commit.clone()).collect()
}

#[test]
fn a_batch_is_the_oldest_waiting_and_its_feature_s_run_after_it() {
    let all = [
        h("461", &["T1"], "aaaaaaa1"),
        h("461", &["T2"], "aaaaaaa2"),
        h("451", &["T9"], "bbbbbbb1"),
        h("461", &["T3"], "aaaaaaa3"),
    ];
    // cut at another feature's; the same feature's after it is not pulled forward
    assert_eq!(formed(&all, &[], LANE_MAX), ["aaaaaaa1", "aaaaaaa2"]);
    // cut at the cap
    assert_eq!(formed(&all, &[], 1), ["aaaaaaa1"]);
    // nothing waiting: no batch
    assert!(formed(&[], &[], LANE_MAX).is_empty());
    // a landed batch takes its changes off the waiting: the next is the other feature's
    let lane = [
        json!({"event": "batch", "batch": "461-1", "changes": ["aaaaaaa1", "aaaaaaa2"]}),
        json!({"event": "landed", "batch": "461-1", "landed": ["aaaaaaa1", "aaaaaaa2"]}),
    ];
    assert_eq!(formed(&all, &lane, LANE_MAX), ["bbbbbbb1"]);
}

#[test]
fn a_hand_in_of_a_task_an_open_batch_carries_waits_until_it_ends() {
    let all = [
        h("461", &["T1"], "aaaaaaa1"),
        h("461", &["T2"], "aaaaaaa2"),
        h("461", &["T3"], "aaaaaaa3"),
        h("461", &["T2"], "aaaaaaa4"),
    ];
    // T2's first hand-in is in an open batch: its second (which supersedes it) is held, and cuts the batch after T3
    let lane = [json!({"event": "batch", "batch": "461-1", "changes": ["aaaaaaa2"]})];
    assert_eq!(formed(&all, &lane, LANE_MAX), ["aaaaaaa1", "aaaaaaa3"]);
    // the oldest waiting held: no batch forms, since nothing lands ahead of it
    let lane = [json!({"event": "batch", "batch": "461-1", "changes": ["aaaaaaa1"]})];
    let later = [h("461", &["T1"], "aaaaaaa1"), h("461", &["T1"], "aaaaaaa5")];
    assert!(formed(&later, &lane, LANE_MAX).is_empty());
    // another feature's task of the same name is not held
    let other = [h("461", &["T1"], "aaaaaaa1"), h("451", &["T1"], "bbbbbbb1")];
    let lane = [json!({"event": "batch", "batch": "461-1", "changes": ["aaaaaaa1"]})];
    assert_eq!(formed(&other, &lane, LANE_MAX), ["bbbbbbb1"]);
}

#[test]
fn a_batch_s_id_counts_up_per_feature() {
    assert_eq!(next_id(&[], "461"), "461-1");
    let lane = [
        json!({"event": "batch", "batch": "461-2"}),
        json!({"event": "batch", "batch": "451-7"}),
        json!({"event": "run", "batch": "461-9"}),
        json!({"event": "batch", "batch": "461-x"}),
        json!({"event": "batch"}),
    ];
    assert_eq!(next_id(&lane, "461"), "461-3");
    assert_eq!(next_id(&lane, "451"), "451-8");
}

/// D14's end of an open batch (461 T26): a later hand-in of a task the open batch carries waits; the batch landing the earlier, the
/// later is the next batch (carried on top of it); the batch ejecting the earlier, the later supersedes it, is the next batch, and the
/// ejected one's repair entry reads as closed - though the later was handed in while the batch was still open, before the eject.
#[test]
fn an_open_batch_s_end_lands_a_later_hand_in_of_its_task_on_top_or_has_it_supersede_the_ejected() {
    const ONE: &str = "aaaaaaaaaa1111111111111111111111111111111";
    const TWO: &str = "aaaaaaaaaa2222222222222222222222222222222";
    let all = [h("461", &["T1"], ONE), h("461", &["T1"], TWO)];
    let state = |lane: &[serde_json::Value], commit: &str| {
        let on_main = BTreeSet::new();
        let batches = log::batches(lane);
        let w = World {
            hand_ins: &all,
            on_main: &on_main,
            log: lane,
            batches: &batches,
        };
        log::state(all.iter().find(|x| x.commit == commit).unwrap(), &w)
    };
    let formed_ = json!({"event": "batch", "batch": "461-1", "changes": [ONE]});
    // open: the later waits, and no batch forms ahead of it
    assert!(formed(&all, &[formed_.clone()], LANE_MAX).is_empty());
    // landed: the later is the next batch, on top of it
    let landed = [
        formed_.clone(),
        json!({"event": "landed", "batch": "461-1", "landed": [ONE], "ejected": []}),
    ];
    assert_eq!(state(&landed, ONE), log::HandInState::Landed);
    assert_eq!(formed(&all, &landed, LANE_MAX), [TWO]);
    // ejected: the later supersedes it and is the next batch
    let ejected = [
        formed_,
        json!({"event": "eject", "batch": "461-1", "change": ONE, "repair": "r1", "why": "red"}),
        json!({"event": "landed", "batch": "461-1", "landed": [], "ejected": [ONE]}),
    ];
    assert_eq!(state(&ejected, ONE), log::HandInState::Superseded);
    assert_eq!(formed(&all, &ejected, LANE_MAX), [TWO]);
    // ...and its repair entry is closed by the later hand-in, made at 03:02 while the batch ran, before the 03:05 eject
    let dir = l7r_gate_core::ci::fixtures::scratch("lane-batch-supersede");
    let common = dir.path();
    let entry = crate::repairs::Entry {
        feature: "461-landing-lane".into(),
        tasks: vec!["T1".into()],
        kind: "fix".into(),
        ejected: vec![ONE.into()],
        batch: "461-1".into(),
        why: "red".into(),
        units: Vec::new(),
        attempt: "a.log".into(),
    };
    let id = crate::repairs::file(common, "2026-11-28T03:05:00Z", &entry).unwrap();
    let eject = json!({"batch": "461-1", "change": ONE, "repair": id, "why": "red"});
    log::append(common, "2026-11-28T03:05:00Z", "eject", &eject).unwrap();
    let done = |utc: &str, commit: &str| json!({"utc": utc, "event": "done", "tree": "/t", "detail": "461 T1", "commit": commit, "handed_in": true});
    let pool = common.join(l7r_shared::builder_queue::LOG);
    std::fs::write(&pool, format!("{}\n", done("2026-11-28T03:00:00Z", ONE))).unwrap();
    assert_eq!(log::repairs_open(common), [id.clone()]);
    let both = format!(
        "{}\n{}\n",
        done("2026-11-28T03:00:00Z", ONE),
        done("2026-11-28T03:02:00Z", TWO)
    );
    std::fs::write(&pool, both).unwrap();
    assert!(log::repairs_open(common).is_empty());
}
