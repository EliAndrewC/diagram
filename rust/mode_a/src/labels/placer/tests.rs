//! The placer held to the Python's answers (feature 449 T151): sixty seeded scenes - discs and turned roofs of every weight, group and
//! flag, ways soft and hard, a point, an area or a line subject, frames wide and tight, fixed lines and their sizes, strict and not, the
//! ring capped and not, a strict caller refusing the first rank - each seated by the Python's `place` and its index asked four questions
//! (`score`, `blocked`, `nearer_than`, `stands_nearest`, `caption_clears_ways`), its answers captured in `held.json` (generated
//! 2026-11-18 by a revision of `held_cases.py` beside it that was not kept, seed 449, `CPython` 3.14.4; its answers re-taken from the same
//! scenes by that script's `--reanswer` after feature 449 T184's fixes to the Python). Every answer here is the Python's to the bit.
//!
//! Research:
//!     its tests - NONE: the port held to the Python's answers, deciding nothing about a building

use l7r_guard::shared::pyjson::py_float;
use serde_json::Value;

use super::{
    caption_clears_ways, hug_gap, leader_of, moved_inward, nudge_reach, place, record_box,
    referent_box, Ask, Kind, Placement, Subject,
};
use crate::labels::geom::{rect, Pt};
use crate::labels::obstacles::{
    circle_obstacle, stands_nearest, Asker, Obstacle, ObstacleIndex, Way,
};

const HELD: &str = include_str!("held.json");

fn num(v: &Value) -> f64 {
    v.as_str().map_or_else(
        || v.as_f64().unwrap(),
        |s| crate::py::float(&s[2..]).unwrap(),
    )
}

fn pt(v: &Value) -> Pt {
    (num(&v[0]), num(&v[1]))
}

fn rect_of(v: &Value) -> Vec<Pt> {
    rect(num(&v[0]), num(&v[1]), num(&v[2]), num(&v[3]), num(&v[4]))
}

/// `[shape, ..., weight, group, flags, keep]`: a disc `"c" x y r` or a rect `"r" cx cy hw hh angle`.
fn obstacle(v: &Value) -> Obstacle {
    let a = v.as_array().unwrap();
    let at = if a[0] == "c" { 4 } else { 6 };
    let (weight, group, flags) = (num(&a[at]), a[at + 1].as_str(), a[at + 2].as_str().unwrap());
    let base = if a[0] == "c" {
        circle_obstacle(num(&a[1]), num(&a[2]), num(&a[3]), weight, group)
    } else {
        Obstacle {
            group: group.map(str::to_owned),
            ..Obstacle::new(
                rect(num(&a[1]), num(&a[2]), num(&a[3]), num(&a[4]), num(&a[5])),
                weight,
            )
        }
    };
    Obstacle {
        named: flags.contains('n'),
        inner: flags.contains('i'),
        soft: flags.contains('s'),
        keep: num(&a[at + 3]),
        ..base
    }
}

fn index(obstacles: &Value, ways: &Value) -> ObstacleIndex {
    let ways = ways
        .as_array()
        .into_iter()
        .flatten()
        .map(|w| Way {
            pts: w[0].as_array().unwrap().iter().map(pt).collect(),
            half_width: num(&w[1]),
            soft: w[2].as_bool().unwrap(),
        })
        .collect();
    ObstacleIndex::new(
        obstacles.as_array().unwrap().iter().map(obstacle).collect(),
        ways,
    )
}

fn subject(v: &Value) -> Subject {
    let kind = match v["kind"].as_str().unwrap() {
        "point" => Kind::Point,
        "area" => Kind::Area,
        _ => Kind::Line,
    };
    let poly = if v["rect"].is_array() {
        rect_of(&v["rect"])
    } else {
        v["poly"].as_array().unwrap().iter().map(pt).collect()
    };
    Subject {
        half_width: num(&v["half_width"]),
        hint: v["hint"].as_array().map(|h| (num(&h[0]), num(&h[1]))),
        civic: v["civic"].as_bool().unwrap(),
        ..Subject::new(kind, poly, num(&v["angle"]))
    }
}

/// A placement as the probe wrote it, every float by its `repr`.
fn written(p: &Placement) -> Value {
    let f = |x: f64| Value::from(format!("f:{}", py_float(x)));
    let pts = |v: &[Pt]| {
        Value::from(
            v.iter()
                .map(|q| Value::from(vec![f(q.0), f(q.1)]))
                .collect::<Vec<_>>(),
        )
    };
    serde_json::json!({"x": f(p.x), "y": f(p.y), "angle": f(p.angle), "lines": p.lines, "block": pts(&p.block), "ring": p.ring,
        "rank": p.rank, "position": p.position, "cost": f(p.cost), "leader": p.leader.map(|(a, b)| pts(&[a, b]))})
}

#[test]
fn every_held_scene_is_seated_as_the_python_seated_it() {
    let held: Value = serde_json::from_str(HELD).unwrap();
    let (mut strict_none, mut leaders) = (0, 0);
    for (k, c) in held["cases"].as_array().unwrap().iter().enumerate() {
        let idx = index(&c["obstacles"], &c["ways"]);
        let lead = c["leader_obstacles"]
            .as_array()
            .map(|_| index(&c["leader_obstacles"], &Value::Null));
        let lines: Option<Vec<String>> = c["lines"]
            .as_array()
            .map(|l| l.iter().map(|s| s.as_str().unwrap().to_owned()).collect());
        let sizes: Option<Vec<f64>> = c["line_sizes"]
            .as_array()
            .map(|l| l.iter().map(num).collect());
        let frame = c["frame"]
            .as_array()
            .map(|f| (num(&f[0]), num(&f[1]), num(&f[2]), num(&f[3])));
        let refuse = |p: &Placement| p.rank != 0;
        let ask = Ask {
            frame,
            lines: lines.as_deref(),
            char_w: num(&c["char_w"]),
            leader_index: lead.as_ref(),
            line_sizes: sizes.as_deref(),
            extended: c["extended"].as_bool().unwrap(),
            strict: c["strict"].as_bool().unwrap(),
            max_ring: c["max_ring"].as_u64().map(|r| usize::try_from(r).unwrap()),
            accept: c["refuse_rank0"]
                .as_bool()
                .unwrap()
                .then_some(&refuse as &dyn Fn(&Placement) -> bool),
        };
        let got = place(
            c["text"].as_str().unwrap(),
            num(&c["size"]),
            &subject(&c["subject"]),
            &idx,
            &ask,
        );
        // none is refused since feature 449 T184: case 15's leader seat on its own bent line was the Python's division by zero, and is
        // now seated
        let p = got.expect("no held scene is refused");
        assert!(c["raises"].is_null(), "{k}");
        strict_none += usize::from(p.is_none());
        leaders += usize::from(p.as_ref().is_some_and(|p| p.leader.is_some()));
        let got = p.as_ref().map_or(Value::Null, written);
        assert_eq!(got, c["answer"], "{k}");
    }
    // the scenes reach every answer: a strict search's none and a leader
    assert!(strict_none > 5 && leaders > 3);
}

#[test]
#[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
fn every_held_query_is_answered_as_the_python_answered_it() {
    let held: Value = serde_json::from_str(HELD).unwrap();
    let cases = held["cases"].as_array().unwrap();
    let (mut blocked, mut nearer) = (0, 0);
    for (k, q) in held["queries"].as_array().unwrap().iter().enumerate() {
        let c = &cases[usize::try_from(q["case"].as_u64().unwrap()).unwrap()];
        let idx = index(&c["obstacles"], &c["ways"]);
        let sub = subject(&c["subject"]);
        let block = rect_of(&q["block"]);
        let own = q["own"].as_bool().unwrap().then_some(sub.poly.as_slice());
        let who = Asker {
            subject: own,
            text: q["text"].as_str().unwrap(),
            civic: q["civic"].as_bool().unwrap(),
        };
        let gap = q["own_gap"].as_f64();
        let clear = num(&q["clear"]);
        let (cost, hard) = idx.score(&block, clear, who, gap);
        let want = (num(&q["score"][0]), q["score"][1].as_bool().unwrap());
        assert_eq!((cost, hard), want, "{k}");
        assert_eq!(idx.cost(&block, clear, who, gap), cost);
        let b = idx.blocked(&block, clear, nudge_reach(), who);
        assert_eq!(b, q["blocked"].as_bool().unwrap(), "{k}");
        let n = idx.nearer_than(&block, 4.0, &sub.poly);
        assert_eq!(n, q["nearer"].as_bool().unwrap(), "{k}");
        let stands = stands_nearest(&block, &sub.poly, &idx);
        assert_eq!(stands, q["stands"].as_bool().unwrap(), "{k}");
        let clears = caption_clears_ways(&block, &idx.ways);
        assert_eq!(clears, q["clears"].as_bool().unwrap(), "{k}");
        (blocked, nearer) = (blocked + usize::from(b), nearer + usize::from(n));
    }
    assert!(blocked > 50 && nearer > 50);
}

#[test]
#[expect(clippy::float_cmp, reason = "each figure is Python's to the bit")]
fn the_hug_and_the_inward_move_measure_as_the_python_s() {
    // Python: referent_box(Subject("line", ((0, 0), (10, 0), (10, 10)), half_width=2.0), rect(12, 5, 1, 1)) == (8.0, 3.0, 12.0, 7.0)
    let line = Subject {
        half_width: 2.0,
        ..Subject::new(Kind::Line, vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)], 0.0)
    };
    assert_eq!(
        referent_box(&line, &rect(12.0, 5.0, 1.0, 1.0, 0.0)),
        (8.0, 3.0, 12.0, 7.0)
    );
    let area = Subject::new(Kind::Area, rect(5.0, 5.0, 5.0, 5.0, 0.0), 0.0);
    assert_eq!(referent_box(&area, &[]), (0.0, 0.0, 10.0, 10.0));
    // a turned block's record box is its unturned extent; the hug the box gap
    let block = rect(20.0, 5.0, 4.0, 2.0, 30.0);
    let r = record_box(&block);
    assert!((r.2 - r.0 - 8.0).abs() < 1e-12 && (r.3 - r.1 - 4.0).abs() < 1e-12);
    assert_eq!(
        hug_gap(&rect(20.0, 5.0, 4.0, 2.0, 0.0), (0.0, 0.0, 10.0, 10.0)),
        6.0
    );
    // moved inward: by the least on an axis it fits, centered where the frame is narrower; no frame, no move
    let cand = super::Cand {
        ring: 0,
        rank: 0,
        position: "above",
        center: (5.0, 50.0),
        angle: 0.0,
        lines: vec!["x".to_owned()],
        half: (10.0, 2.0),
        size: 8.0,
    };
    let block = rect(5.0, 50.0, 10.0, 2.0, 0.0);
    let (moved, b) = moved_inward(&cand, &block, Some((0.0, 49.0, 100.0, 51.0)));
    assert_eq!((moved.center, b[0]), ((10.0, 50.0), (0.0, 48.0)));
    assert_eq!(moved_inward(&cand, &block, None).0, cand);
    // within twice the usual gap, or for an area, no leader
    assert_eq!(leader_of(1, &block, &line), None);
    assert_eq!(leader_of(5, &block, &area), None);
}

#[test]
fn a_line_of_one_point_and_a_caption_of_no_size_are_refused_by_name() {
    // feature 449 T184: the Python raised its own walk's AssertionError, or `min()`'s ValueError with a hint, on a line of one point, and
    // looped forever on a caption of no size (its leader rings never passed the hug); both sides now refuse each by name
    let one = Subject::new(Kind::Line, vec![(0.0, 0.0)], 0.0);
    let hinted = Subject {
        hint: Some((1.0, 1.0)),
        ..one.clone()
    };
    let none = Subject::new(Kind::Line, Vec::new(), 0.0);
    for sub in [&one, &hinted, &none] {
        let e = place("x", 8.0, sub, &ObstacleIndex::default(), &Ask::default()).unwrap_err();
        assert_eq!(
            (e.kind, e.message.as_str()),
            ("ValueError", super::ONE_POINT_LINE)
        );
    }
    let point = Subject::new(Kind::Point, rect(10.0, 10.0, 2.0, 2.0, 0.0), 0.0);
    for size in [0.0, -1.0, f64::NAN] {
        let e = place(
            "x",
            size,
            &point,
            &ObstacleIndex::default(),
            &Ask::default(),
        )
        .unwrap_err();
        assert_eq!((e.kind, e.message.as_str()), ("ValueError", super::NO_SIZE));
    }
}

#[test]
fn a_leader_s_block_touching_its_line_draws_no_leader() {
    // feature 449 T184: a line that bends back can hold a leader ring's block across another of its segments; the block touches what it
    // names, so no leader ties it back (the Python divided by the zero distance)
    let line = Subject::new(Kind::Line, vec![(0.0, 0.0), (40.0, 0.0), (0.0, 1.0)], 0.0);
    let block = rect(20.0, 0.0, 4.0, 2.0, 0.0);
    assert_eq!(leader_of(5, &block, &line), None);
}

#[test]
fn a_leader_of_no_length_crosses_nothing() {
    // Python: leader_score(_Cand(2, ...), a block 1e-7 off its subject, ...) == (0.0, False) - a leader too short to cross anything
    let sub = Subject::new(
        Kind::Point,
        vec![(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)],
        0.0,
    );
    let block = [
        (10.0 + 1e-7, 3.0),
        (20.0, 3.0),
        (20.0, 7.0),
        (10.0 + 1e-7, 7.0),
    ];
    let c = super::Cand {
        ring: 2,
        rank: 0,
        position: "right",
        center: (15.0, 5.0),
        angle: 0.0,
        lines: vec!["a".to_owned()],
        half: (5.0, 2.0),
        size: 8.0,
    };
    let who = Asker {
        subject: None,
        text: "",
        civic: false,
    };
    assert_eq!(
        super::leader_score(&c, &block, &sub, &ObstacleIndex::default(), 4.0, who),
        (0.0, false)
    );
}

#[test]
fn a_caller_that_refuses_a_free_seat_is_given_the_next() {
    // Python: place("well", 8, Subject("point", rect(100, 100, 10, 5)), ObstacleIndex(), accept=lambda p: p.rank != 0) - rank 1, below,
    // at (100.0, 115.4)
    let sub = Subject::new(Kind::Point, rect(100.0, 100.0, 10.0, 5.0, 0.0), 0.0);
    let refuse = |p: &Placement| p.rank != 0;
    let ask = Ask {
        accept: Some(&refuse),
        ..Ask::default()
    };
    let p = place("well", 8.0, &sub, &ObstacleIndex::default(), &ask)
        .unwrap()
        .unwrap();
    assert_eq!((p.rank, p.position, p.x, p.y), (1, "below", 100.0, 115.4));
}
