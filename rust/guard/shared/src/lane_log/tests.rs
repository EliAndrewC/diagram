//! The lane's computed states (feature 461 T11, moved here by T63): each state of data-model.md for a hand-in and a batch.

use std::collections::BTreeSet;

use serde_json::{json, Value};

use super::{
    batches, hand_ins, names, on_lane, state, state_of, waiting_unasked, Batch, BatchState, HandIn,
    HandInState, World,
};

const A: &str = "aaaaaaaaaa1111111111111111111111111111111";
const B: &str = "bbbbbbbbbb2222222222222222222222222222222";
const C: &str = "cccccccccc3333333333333333333333333333333";

fn done(utc: &str, detail: &str, commit: &str) -> Value {
    json!({"utc": utc, "event": "done", "tree": "/t", "detail": detail, "commit": commit, "handed_in": true})
}

#[test]
fn hand_ins_are_the_handed_in_done_lines_one_a_commit_and_only_those_still_the_lane_s() {
    let pool = vec![
        json!({"utc": "u0", "event": "take", "detail": "461 T01"}),
        json!({"utc": "u1", "event": "done", "detail": "461 T01", "commit": C}),
        done("u2", "461 T01,T02", A),
        done("u3", "461 T01,T02", A),
        done("u4", "no-tasks", B),
        json!({"utc": "u5", "event": "done", "detail": "461 T03", "handed_in": true}),
        {
            let mut l = done("u6", "451 T09", B);
            l["repair_of"] = json!("r3");
            l
        },
    ];
    let all = hand_ins(&pool);
    assert_eq!(
        all,
        vec![
            HandIn {
                feature: "461".into(),
                tasks: vec!["T01".into(), "T02".into()],
                commit: A.into(),
                at: "u2".into(),
                repair_of: None,
                build_half: false
            },
            HandIn {
                feature: "451".into(),
                tasks: vec!["T09".into()],
                commit: B.into(),
                at: "u6".into(),
                repair_of: Some("r3".into()),
                build_half: false
            },
        ]
    );
    // A's ref stands; B's is gone and only a log line by its short sha keeps it the lane's; with neither it is off the lane
    let refs: BTreeSet<String> = [A.to_owned()].into();
    let log = vec![json!({"event": "run", "batch": "451-1", "set": [&B[..10]]})];
    assert_eq!(on_lane(all.clone(), &refs, &log).len(), 2);
    assert_eq!(on_lane(all, &refs, &[]).len(), 1);
}

fn states(lines: &[Value]) -> BatchState {
    state_of(lines)
}

#[test]
fn a_batch_s_state_is_read_from_its_lines_in_order() {
    let ev = |e: &str, more: Value| {
        let mut l = json!({"event": e, "batch": "461-1"});
        for (k, v) in more.as_object().unwrap() {
            l[k] = v.clone();
        }
        l
    };
    let mut lines = vec![ev("batch", json!({"changes": [A, B]}))];
    assert_eq!(states(&lines), BatchState::Carrying);
    lines.push(ev("carry", json!({"code": 0})));
    assert_eq!(states(&lines), BatchState::Gating(1));
    lines.push(ev("run", json!({"code": 1})));
    assert_eq!(states(&lines), BatchState::Halving);
    lines.push(ev("attribute", json!({"how": "record"})));
    assert_eq!(states(&lines), BatchState::Halving);
    lines.push(ev(
        "eject",
        json!({"change": A, "repair": "r1", "why": "red"}),
    ));
    assert_eq!(states(&lines), BatchState::Gating(2));
    lines.push(ev("owed", json!({"line": "x"})));
    assert_eq!(states(&lines), BatchState::Gating(2));
    lines.push(ev("run", json!({"code": 0})));
    assert_eq!(states(&lines), BatchState::Pushing);
    lines.push(ev("push", json!({"code": 0})));
    assert_eq!(states(&lines), BatchState::Pushing);
    lines.push(ev("landed", json!({"landed": [B], "ejected": [A]})));
    assert_eq!(states(&lines), BatchState::Landed);
    assert_eq!(
        states(&[
            ev("batch", json!({})),
            ev("stop", json!({"why": "arbiter"}))
        ]),
        BatchState::Stopped
    );
    let shown: Vec<String> = [
        BatchState::Carrying,
        BatchState::Gating(3),
        BatchState::Halving,
        BatchState::Pushing,
        BatchState::Landed,
        BatchState::Stopped,
    ]
    .iter()
    .map(ToString::to_string)
    .collect();
    assert_eq!(
        shown,
        ["carrying", "gating 3", "halving", "pushing", "landed", "stopped"]
    );
}

#[test]
fn batches_gather_their_own_lines_from_their_batch_line_on() {
    let log = vec![
        json!({"event": "start", "pid": 1}),
        json!({"event": "carry", "batch": "461-0", "code": 0}),
        json!({"event": "batch", "batch": "461-1", "changes": [A]}),
        json!({"event": "batch", "batch": "451-1", "changes": [B, C]}),
        json!({"event": "carry", "batch": "461-1", "code": 0}),
        json!({"event": "stop", "batch": "451-1", "why": "arbiter"}),
    ];
    let all = batches(&log);
    assert_eq!(all.len(), 2);
    assert_eq!((all[0].id.as_str(), all[0].lines.len()), ("461-1", 2));
    assert_eq!(all[0].changes, [A]);
    assert_eq!(all[0].state, BatchState::Gating(1));
    assert!(all[0].open());
    assert_eq!(all[1].changes, [B, C]);
    assert_eq!(all[1].state, BatchState::Stopped);
    assert!(!all[1].open());
}

fn hand_in(feature: &str, tasks: &[&str], commit: &str) -> HandIn {
    HandIn {
        feature: feature.into(),
        tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
        commit: commit.into(),
        at: String::new(),
        repair_of: None,
        build_half: false,
    }
}

/// Each of data-model.md's five states of a hand-in, and the order they are asked in.
#[test]
fn a_hand_in_s_state_is_the_first_of_the_data_model_s_order_that_holds() {
    let ask = |h: &HandIn, all: &[HandIn], main: &[&str], log: &[Value]| {
        let on_main: BTreeSet<String> = main.iter().map(|s| (*s).to_owned()).collect();
        let b: Vec<Batch> = batches(log);
        state(
            h,
            &World {
                hand_ins: all,
                all,
                on_main: &on_main,
                log,
                batches: &b,
            },
        )
    };
    let a = hand_in("461", &["T01"], A);
    let b = hand_in("461", &["T02"], B);
    let all = vec![a.clone(), b.clone()];
    assert_eq!(ask(&a, &all, &[], &[]), HandInState::Waiting);
    // on origin/main by the carried rule, or listed by a landed line though its object is gone
    assert_eq!(ask(&a, &all, &[A], &[]), HandInState::Landed);
    let landed = json!({"event": "landed", "batch": "461-1", "landed": [&A[..10]], "ejected": []});
    assert_eq!(ask(&a, &all, &[], &[landed.clone()]), HandInState::Landed);
    assert_eq!(ask(&b, &all, &[], &[landed]), HandInState::Waiting);
    // a later hand-in of the same feature sharing a task; another feature's, or an earlier one, supersedes nothing
    let later = hand_in("461", &["T09", "T01"], C);
    let other = hand_in("451", &["T01"], C);
    assert_eq!(
        ask(&a, &[a.clone(), later.clone()], &[], &[]),
        HandInState::Superseded
    );
    assert_eq!(
        ask(&later, &[a.clone(), later.clone()], &[], &[]),
        HandInState::Waiting
    );
    assert_eq!(ask(&a, &[a.clone(), other], &[], &[]), HandInState::Waiting);
    // in an open batch; ejected once the last line naming it is its ejection
    let formed = json!({"event": "batch", "batch": "461-1", "changes": [A, B]});
    let eject =
        json!({"event": "eject", "batch": "461-1", "change": A, "repair": "r1", "why": "red"});
    assert_eq!(
        ask(&a, &all, &[], &[formed.clone()]),
        HandInState::InBatch("461-1".into())
    );
    let log = [formed.clone(), eject.clone()];
    assert_eq!(ask(&a, &all, &[], &log), HandInState::Ejected("r1".into()));
    // still ejected once its batch's `landed` line lists it among the ejected (461 T15); a landed line not listing it changes nothing
    let ended = json!({"event": "landed", "batch": "461-1", "landed": [], "ejected": [A]});
    let ended_log = [formed.clone(), eject.clone(), ended];
    assert_eq!(
        ask(&a, &all, &[], &ended_log),
        HandInState::Ejected("r1".into())
    );
    let mention =
        json!({"event": "landed", "batch": "461-1", "landed": [], "ejected": [], "set": [A]});
    assert_eq!(
        ask(&a, &all, &[], &[formed.clone(), mention]),
        HandInState::Waiting
    );
    assert_eq!(
        ask(&b, &all, &[], &log),
        HandInState::InBatch("461-1".into())
    );
    // an ejection with no repair named says so empty; a stopped batch holds none of its changes
    let bare = json!({"event": "eject", "batch": "461-1", "change": A});
    assert_eq!(
        ask(&a, &all, &[], &[formed.clone(), bare]),
        HandInState::Ejected(String::new())
    );
    let stop = json!({"event": "stop", "batch": "461-1", "why": "arbiter"});
    assert_eq!(
        ask(&b, &all, &[], &[formed.clone(), stop.clone()]),
        HandInState::Waiting
    );
    // held by the tripwire (461 T18): its ejection names no repair but the round arbiter's trigger, and the stop holds it no less
    let held = json!({"event": "eject", "batch": "461-1", "change": A, "repair": null, "why": "red", "arbiter": "ask:lane-T01"});
    assert_eq!(
        ask(&a, &all, &[], &[formed, held, stop]),
        HandInState::Ejected("ask:lane-T01".into())
    );
    let shown: Vec<String> = [
        HandInState::Landed,
        HandInState::Superseded,
        HandInState::Ejected("ask:lane-T01".into()),
        HandInState::Ejected("r2".into()),
        HandInState::InBatch("461-3".into()),
        HandInState::OnClosingHalf,
        HandInState::Waiting,
    ]
    .iter()
    .map(ToString::to_string)
    .collect();
    assert_eq!(
        shown,
        [
            "landed",
            "superseded",
            "ejected -> the round arbiter ask:lane-T01",
            "ejected -> repair r2",
            "in batch 461-3",
            "waiting on its closing half",
            "waiting"
        ]
    );
}

/// 461 T90: a hand-in is a build half's where its tree's last brief for its holder since the tree was held says `build-half` - a
/// brief of another holder, of another tree, or before the tree was taken again says nothing - and a build half's state is
/// `waiting on its closing half` until a later hand-in of its task supersedes it, an open batch or an ejection still read first.
#[test]
fn a_build_half_s_hand_in_waits_on_its_closing_half() {
    let line = |event: &str, tree: &str, detail: &str, kind: Option<&str>| {
        let mut l = json!({"utc": "u", "event": event, "tree": tree, "detail": detail});
        if let Some(k) = kind {
            l["kind"] = json!(k);
        }
        l
    };
    let d = |tree: &str, detail: &str, commit: &str| {
        let mut l = line("done", tree, detail, None);
        l["commit"] = json!(commit);
        l["handed_in"] = json!(true);
        l
    };
    let pool = vec![
        line("take", "/t1", "461 T01", None),
        line("brief", "/t1", "461 T01", Some("build-half")),
        line("brief", "/t2", "461 T02", Some("build-half")),
        line("brief", "/t1", "461 T09", None),
        d("/t1", "461 T01", A),
        line("take", "/t1", "461 T02", None),
        line("take", "/t2", "461 T02", None),
        line("brief", "/t2", "461 T02", Some("fix")),
        d("/t2", "461 T02", B),
        d("/t1", "461 T02", C),
    ];
    let all = hand_ins(&pool);
    let halves: Vec<bool> = all.iter().map(|h| h.build_half).collect();
    assert_eq!(halves, [true, false, false]);
    let ask = |h: &HandIn, all: &[HandIn], log: &[Value]| {
        let b = batches(log);
        let none = BTreeSet::new();
        let w = World {
            hand_ins: all,
            all,
            on_main: &none,
            log,
            batches: &b,
        };
        state(h, &w)
    };
    let half = &all[0];
    assert_eq!(ask(half, &all, &[]), HandInState::OnClosingHalf);
    // an open batch that formed before T90 still holds it; an ejection is still read as one
    let formed = json!({"event": "batch", "batch": "461-1", "changes": [A]});
    assert_eq!(
        ask(half, &all, &[formed.clone()]),
        HandInState::InBatch("461-1".into())
    );
    let eject = json!({"event": "eject", "batch": "461-1", "change": A, "repair": "r1"});
    assert_eq!(
        ask(half, &all, &[formed, eject]),
        HandInState::Ejected("r1".into())
    );
    // its closing half's hand-in supersedes it; the Stop rule's waiting reads neither the half nor what superseded it as waiting
    let close = d(
        "/t1",
        "461 T01",
        "ffffffffff6666666666666666666666666666666",
    );
    let mut both = pool.clone();
    both.extend([line("take", "/t1", "461 T01", None), close]);
    let all = hand_ins(&both);
    assert_eq!(ask(&all[0], &all, &[]), HandInState::Superseded);
    assert_eq!(ask(&all[3], &all, &[]), HandInState::Waiting);
    let refs: BTreeSet<String> = [A.to_owned()].into();
    assert!(waiting_unasked(&hand_ins(&pool), &refs, &[]).is_empty());
}

/// 461 T53: an earlier hand-in an open batch names stays `in batch` though a later hand-in of its task exists - the batch's line
/// carries the earlier sha and lands it (D14) - and the later one waits; once the batch ejects or stops it, the later one supersedes it.
#[test]
fn an_open_batch_s_change_is_in_batch_though_a_later_hand_in_of_its_task_exists() {
    let a = hand_in("461", &["T01"], A);
    let later = hand_in("461", &["T01"], C);
    let all = vec![a.clone(), later.clone()];
    let formed = json!({"event": "batch", "batch": "461-4", "changes": [A]});
    let ask = |h: &HandIn, log: &[Value]| {
        let b = batches(log);
        state(
            h,
            &World {
                hand_ins: &all,
                all: &all,
                on_main: &BTreeSet::new(),
                log,
                batches: &b,
            },
        )
    };
    assert_eq!(
        ask(&a, &[formed.clone()]),
        HandInState::InBatch("461-4".into())
    );
    assert_eq!(ask(&later, &[formed.clone()]), HandInState::Waiting);
    let eject = json!({"event": "eject", "batch": "461-4", "change": A, "repair": "r1"});
    assert_eq!(ask(&a, &[formed.clone(), eject]), HandInState::Superseded);
    let stop = json!({"event": "stop", "batch": "461-4"});
    assert_eq!(ask(&a, &[formed, stop]), HandInState::Superseded);
}

/// A sha is named by its whole or a prefix of seven characters or more, never a shorter one.
#[test]
fn a_commit_is_named_by_a_prefix_of_seven_or_more() {
    assert!(names(A, &A[..7]));
    assert!(names(&A[..10], A));
    assert!(!names(A, &A[..6]));
    assert!(!names(A, B));
}

/// 461 T63: a later hand-in of the task supersedes an earlier one though it has left the lane (its ref deleted by its carry), and
/// the waiting ones with `origin/main` not asked are the lane's, read through the one assembly the Stop rule and the wake share.
#[test]
fn a_later_hand_in_off_the_lane_supersedes_and_the_waiting_are_read_with_origin_main_not_asked() {
    let pool = [
        done("u1", "461 T01", A),
        done("u2", "461 T01", B),
        done("u3", "451 T02", C),
    ];
    let all = hand_ins(&pool);
    let stopped = [
        json!({"event": "batch", "batch": "461-1", "changes": [A]}),
        json!({"event": "stop", "batch": "461-1"}),
    ];
    let b = batches(&stopped);
    let lane = on_lane(all.clone(), &BTreeSet::new(), &stopped);
    assert_eq!(lane.len(), 1);
    let w = World {
        hand_ins: &lane,
        all: &all,
        on_main: &BTreeSet::new(),
        log: &stopped,
        batches: &b,
    };
    assert_eq!(state(&all[0], &w), HandInState::Superseded);
    assert!(waiting_unasked(&all, &BTreeSet::new(), &stopped).is_empty());
    // the later one's ref and C's stand: those two wait, in the pool's order
    let refs: BTreeSet<String> = [B.to_owned(), C.to_owned()].into();
    let waits: Vec<String> = waiting_unasked(&all, &refs, &stopped)
        .into_iter()
        .map(|h| h.commit)
        .collect();
    assert_eq!(waits, [B, C]);
}
