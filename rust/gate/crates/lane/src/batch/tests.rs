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
