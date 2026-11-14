//! Feature 261's four measures over scratch maps, and Python's arithmetic they rest on (the expected floats are Python 3.14's).

use std::path::Path;

use l7r_gate_core::record::testkit::put;
use serde_json::{json, Value};

use super::{
    board_well, brook_turn, degrees, fixtures_and_board, frexp_exponent, groups, hypot, num, pow2,
    py_mod, row_spread, Num, MAPS, OLD_POOL,
};

fn words(w: &[&str]) -> Vec<String> {
    w.iter().map(|s| (*s).to_owned()).collect()
}

fn map(root: &Path, base: &str, name: &str, v: &Value) {
    put(root, &format!("{base}/{name}/{name}.json"), &v.to_string());
}

fn run(
    f: fn(&[String], &Path, &mut String) -> super::Ran,
    args: &[&str],
    root: &Path,
) -> (super::Ran, String) {
    let mut out = String::new();
    let ran = f(&words(args), root, &mut out);
    (ran, out)
}

#[test]
#[expect(
    clippy::float_cmp,
    reason = "Python's floats, which the port must give exactly"
)]
fn pythons_arithmetic() {
    assert_eq!(hypot(3.0, -4.0), 5.0);
    assert_eq!(
        hypot(2_539.333_333_333_333_5, -1_466.600_000_000_000_1),
        2_932.427_209_288_882
    );
    assert_eq!(hypot(0.1, 0.2), 0.223_606_797_749_979);
    assert_eq!(hypot(1e-310, 2e-310), 2.236_067_977_499_8e-310);
    assert_eq!(hypot(5e-324, 0.0), 5e-324);
    assert_eq!(hypot(3e-308, 4e-308), 5.000_000_000_000_001e-308);
    assert_eq!(hypot(1.7e308, 1.7e308), f64::INFINITY);
    assert_eq!(hypot(f64::INFINITY, 1.0), f64::INFINITY);
    assert_eq!(hypot(0.0, -0.0), 0.0);
    assert_eq!(frexp_exponent(1.0), 1);
    assert_eq!(frexp_exponent(5e-324), -1073);
    assert_eq!((pow2(-1024), pow2(3)), (2f64.powi(-1023) / 2.0, 8.0));
    assert_eq!(degrees(1.0), 57.295_779_513_082_32);
    assert_eq!(
        (
            py_mod(-370.5, 360.0),
            py_mod(-360.0, 360.0),
            py_mod(720.0, 360.0),
            py_mod(10.0, 360.0)
        ),
        (349.5, 0.0, 0.0, 10.0)
    );
    assert_eq!(num(&json!(true)), Ok(Num::Int(1)));
    assert_eq!(num(&json!(u64::MAX)), Ok(Num::Int(i128::from(u64::MAX))));
    assert_eq!(num(&json!(2.5)), Ok(Num::Float(2.5)));
    assert!(num(&json!("1")).is_err());
    let big = Num::Int(i128::MAX / 2);
    assert_eq!(big.mul(Num::Int(4)), Num::Float(big.f() * 4.0));
    assert_eq!(Num::Int(3).mul(Num::Float(0.5)), Num::Float(1.5));
    assert_eq!(
        (Num::Int(5).round1(), Num::Float(16.04).round1()),
        ("5".to_owned(), "16.0".to_owned())
    );
    assert_eq!(
        (
            Num::Float(2.5).round0(),
            Num::Float(3.5).round0(),
            Num::Int(-7).round0()
        ),
        (2, 4, -7)
    );
    assert!(Num::Float(-0.5).negative() && !Num::Int(0).negative());
}

#[test]
fn the_board_and_its_nearest_well() {
    let root = crate::checks::scratch("spec-board-well");
    map(
        &root,
        "pool/hamlets",
        "a",
        &json!({"kosatsuba": [{"x": 0, "y": 9}, {"x": 0, "y": 0}], "wells": [{"x": 30, "y": 40}, {"x": 3, "y": 4.0}], "meta": {"ftpx": "2", "kosatsuba_well_ft": [1, "a"]}}),
    );
    map(
        &root,
        "pool/hamlets",
        "b",
        &json!({"kosatsuba": [{"x": 0, "y": 0}], "wells": [{"x": 1, "y": 1}], "meta": {"ftpx": 0, "kosatsuba_well_ft": 1.5}}),
    );
    let (ran, out) = run(board_well, &["a", "b"], &root);
    assert_eq!(ran, Ok(0));
    assert_eq!(
        out,
        "a recorded [1, 'a'] drawn 10.0\nb recorded 1.5 drawn 1.4\n"
    );
    for (bad, why) in [
        (
            json!({"kosatsuba": [{"x": 0, "y": 0}], "wells": [], "meta": {}}),
            "ValueError: min()",
        ),
        (
            json!({"kosatsuba": [], "wells": [], "meta": {}}),
            "IndexError",
        ),
        (
            json!({"kosatsuba": {}, "wells": [], "meta": {}}),
            "TypeError",
        ),
        (
            json!({"kosatsuba": [{"x": 0, "y": 0}], "wells": [{"x": 1, "y": 1}], "meta": {"ftpx": "x"}}),
            "ValueError: could not convert",
        ),
        (
            json!({"kosatsuba": [{"x": 0, "y": 0}], "wells": [{"x": 1, "y": 1}], "meta": []}),
            "AttributeError",
        ),
        (json!([1]), "TypeError"),
    ] {
        map(&root, "pool/hamlets", "c", &bad);
        let raised = run(board_well, &["c"], &root).0.unwrap_err();
        assert!(raised.starts_with(why));
    }
    put(&root, "pool/hamlets/c/c.json", "{");
    assert!(run(board_well, &["c"], &root)
        .0
        .unwrap_err()
        .starts_with("JSONDecodeError"));
}

#[test]
fn the_sharpest_turn_of_each_brook() {
    let root = crate::checks::scratch("spec-brook-turn");
    map(
        &root,
        OLD_POOL,
        "a",
        &json!({"streams": [{"poly": [[0, 0], [10, 0], [0, 0.0], [0, -10]]}, {"poly": [[0, 0], [3, 4], [6, 8]]}]}),
    );
    map(&root, OLD_POOL, "b", &json!({}));
    map(&root, OLD_POOL, "c", &json!({"streams": {}}));
    let (ran, out) = run(brook_turn, &["a", "b", "c"], &root);
    assert_eq!(ran, Ok(0));
    assert_eq!(out, "a [180.0, 0.0]\nb []\nc []\n");
    for bad in [
        json!({"streams": [{"poly": [[0, 0], [1, 1]]}]}),
        json!({"streams": [{"poly": {}}]}),
        json!({"streams": [{"poly": [[0, 0], [1], [2, 2]]}]}),
        json!({"streams": "ab"}),
        json!({"streams": null}),
    ] {
        map(&root, OLD_POOL, "d", &bad);
        assert!(run(brook_turn, &["d"], &root).0.is_err());
    }
}

fn pool_map(extra: &Value) -> Value {
    let mut m = json!({
        "kosatsuba": [{"x": 2.5, "y": 3.5, "rot": -176.6}],
        "meta": {"farm_fixtures_unseated": ["a"], "roll_attempt": 3},
        "lanes": [{"pts": [[0, 0], [10, 10]]}, {"pts": "a"}, {"pts": {"k": 1}}, {"pts": [[5, -5]]}],
        "farm_fixtures": [{"x": 10, "y": 0, "of": [0, 10]}, {"x": 10, "y": 0, "of": [11, 10]}, {"of": []}, {"x": 1, "y": 1, "of": [0, 0]}],
        "persimmons": [{"x": 10, "y": 0, "of": [0, 10]}],
        "dry_plots": [{"homestead": true}, {"homestead": 0}, {}],
    });
    for (k, v) in extra.as_object().unwrap() {
        m[k] = v.clone();
    }
    m
}

#[test]
fn fixtures_across_a_lane_and_the_board() {
    let root = crate::checks::scratch("spec-fixtures");
    for m in MAPS {
        map(&root, "pool/hamlets", m, &pool_map(&json!({})));
    }
    map(
        &root,
        "pool/hamlets",
        "sawada",
        &pool_map(
            &json!({"lanes": {}, "dry_plots": {}, "persimmons": [{"x": 1, "y": 1, "of": "ab"}], "kosatsuba": [{"x": 4, "y": true}]}),
        ),
    );
    let mut out = String::new();
    assert_eq!(fixtures_and_board(&root, &mut out), Ok(0));
    let line = "homestead plots 1 fixtures 4 across lane 2 unseated ['a'] board 2 4 -176.6 caption None roll 3\n";
    assert!(out.starts_with(&format!("inashiro {line}kashikawa {line}")));
    assert!(out.ends_with("sawada homestead plots 0 fixtures 4 across lane 0 unseated ['a'] board 4 1 None caption None roll 3\n"));
    for bad in [
        json!({"lanes": [{"pts": "ab"}]}),
        json!({"lanes": [{"pts": [[0, 0], [1, 1]]}], "farm_fixtures": [{"x": 1, "y": 1, "of": 5}]}),
        json!({"lanes": [{"pts": [[0, 0], [1, 1]]}], "farm_fixtures": [{"y": 1, "of": [0, 0]}]}),
        json!({"lanes": null}),
        json!({"farm_fixtures": [[1]]}),
        json!({"dry_plots": [[1]]}),
        json!({"meta": [1]}),
    ] {
        map(&root, "pool/hamlets", "sawada", &pool_map(&bad));
        assert!(fixtures_and_board(&root, &mut String::new()).is_err());
    }
    let mut lacking = pool_map(&json!({}));
    lacking.as_object_mut().unwrap().remove("lanes");
    map(&root, "pool/hamlets", "sawada", &lacking);
    assert_eq!(
        fixtures_and_board(&root, &mut String::new()),
        Err("KeyError: 'lanes'".to_owned())
    );
}

#[test]
fn ranks_of_houses() {
    assert_eq!(
        groups(&[
            json!(0),
            json!(40),
            json!(80.5),
            json!(81),
            json!(200),
            json!(-0.0),
            json!(0.0)
        ])
        .unwrap(),
        "[(4, 40)]"
    );
    assert!(groups(&[]).unwrap_err().starts_with("IndexError"));
    assert!(groups(&[json!("a")]).is_err());
    let root = crate::checks::scratch("spec-row-spread");
    let git = |args: &[&str]| {
        let out = std::process::Command::new("git")
            .arg("-C")
            .arg(&*root)
            .args(["-c", "user.name=t", "-c", "user.email=t@t"])
            .args(args)
            .output()
            .unwrap();
        assert!(out.status.success());
    };
    let houses = json!({"houses": [{"x": 0, "y": 0}, {"x": 20, "y": 1}, {"x": 40, "y": 2.5}, {"x": 500, "y": 900}]});
    map(&root, "pool/hamlets", "a", &houses);
    assert!(run(row_spread, &["a"], &root)
        .0
        .unwrap_err()
        .starts_with("CalledProcessError"));
    git(&["init", "-q"]);
    let (ran, out) = run(row_spread, &["a"], &root);
    assert_eq!(ran, Ok(0));
    assert_eq!(out, "a rows [(3, 2.5)] columns [(3, 40)]\n");
    assert_eq!(run(row_spread, &["--rev", "", "a"], &root).1, out);
    map(&root, OLD_POOL, "a", &json!({"houses": [{"x": 1, "y": 1}]}));
    git(&["add", "-A"]);
    git(&["commit", "-qm", "c"]);
    let (ran, out) = run(row_spread, &["--rev", "HEAD", "a"], &root);
    assert_eq!((ran, out.as_str()), (Ok(0), "a rows [] columns []\n"));
    assert!(run(row_spread, &["--rev", "HEAD", "b"], &root)
        .0
        .unwrap_err()
        .starts_with("CalledProcessError"));
    assert!(run(row_spread, &["--rev"], &root)
        .0
        .unwrap_err()
        .starts_with("IndexError"));
    put(&root, &format!("{OLD_POOL}/c/c.json"), "{");
    git(&["add", "-A"]);
    git(&["commit", "-qm", "c"]);
    assert!(run(row_spread, &["--rev", "HEAD", "c"], &root)
        .0
        .unwrap_err()
        .starts_with("JSONDecodeError"));
    map(&root, "pool/hamlets", "d", &json!({"houses": [{"y": 1}]}));
    assert!(run(row_spread, &["d"], &root)
        .0
        .unwrap_err()
        .starts_with("KeyError"));
}
