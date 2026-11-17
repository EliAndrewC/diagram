//! What an amount of money was worth (feature 449 T148): `expected.json` holds HEAD's `money.py` answers on the same inputs (the T148
//! scratch's `pymoney.py`); the box and the marks are pinned through the site's cases (`site/cases.json`, "money good" and "money bad").

use serde_json::{json, Value};

use super::{
    annotate, dollars, everyday, fmt, hover_box, load, rokugani, short_years, years, Table,
};
use crate::fixture::put;

fn expected() -> Value {
    serde_json::from_str(include_str!("expected.json")).unwrap()
}

fn f(v: &Value) -> f64 {
    v.as_f64().unwrap()
}

#[test]
fn every_figure_is_the_pythons() {
    let e = expected();
    for row in e["dollars"].as_array().unwrap() {
        assert_eq!(dollars(f(&row[0]), None), row[1].as_str().unwrap(), "{row}");
    }
    for row in e["dollars_scaled"].as_array().unwrap() {
        assert_eq!(
            dollars(f(&row[0]), Some(f(&row[1]))),
            row[2].as_str().unwrap()
        );
    }
    for row in e["everyday"].as_array().unwrap() {
        assert_eq!(everyday(row[0].as_i64().unwrap()), row[1].as_str().unwrap());
    }
    for row in e["rokugani"].as_array().unwrap() {
        assert_eq!(rokugani(f(&row[0])), row[1].as_str().unwrap(), "{row}");
    }
    for row in e["fmt"].as_array().unwrap() {
        assert_eq!(fmt(row[0].as_i64().unwrap()), row[1].as_str().unwrap());
    }
    for row in e["years"].as_array().unwrap() {
        let want = row[1]
            .as_array()
            .map(|p| (p[0].as_i64().unwrap(), p[1].as_i64().unwrap()));
        assert_eq!(years(row[0].as_str().unwrap()), want, "{row}");
    }
    for row in e["short_years"].as_array().unwrap() {
        assert_eq!(
            short_years(row[0].as_str().unwrap()),
            row[1].as_str().unwrap()
        );
    }
}

#[test]
fn the_table_is_read_as_the_python_read_it() {
    let dir = crate::fixture::record();
    assert_eq!(load(&dir).unwrap(), Table::default());
    put(&dir, "assets/money-conversions.json", "[1]");
    assert_eq!(load(&dir).unwrap(), Table::default());
    put(&dir, "assets/money-conversions.json", "{\"eras\": [1]}");
    assert_eq!(
        load(&dir).unwrap_err().message,
        "'list' object has no attribute 'get'"
    );
    put(&dir, "assets/money-conversions.json", "{not json");
    assert_eq!(load(&dir).unwrap_err().kind, "JSONDecodeError");
    std::fs::remove_file(dir.join("assets/money-conversions.json")).unwrap();
    std::fs::create_dir_all(dir.join("assets/money-conversions.json")).unwrap();
    assert_eq!(load(&dir).unwrap_err().kind, "OSError");
}

#[test]
fn a_box_and_its_marks() {
    let unit =
        json!({"goods_dollars": 1, "goods_dollars_high": 2, "wage_dollars": 1, "rokugan_sen": 1});
    let era =
        json!({"place": "Edo", "years": "1745-1754", "goods_left_out": "AB", "basket_coverage": 3});
    let (u, e) = (unit.as_object().unwrap(), era.as_object().unwrap());
    assert_eq!(
        hover_box(&[2.0], "2 ryo", u, e, true).unwrap(),
        "2 ryo: about $2.00-$4.00 in goods, $2.00 in wages, 2.0 sen in Rokugan\nat Edo 1745-54 prices\nEdo 1745-1754: 3; leaves out a, b"
    );
    let plain = json!({"place": "Edo", "years": "1766", "confidence": ""});
    assert_eq!(
        hover_box(&[1.0, 2.0], "1-2 ryo", u, plain.as_object().unwrap(), false).unwrap(),
        "1-2 ryo: about $1.00-$4.00 in goods, $1.00-$2.00 in wages, 1.0 sen to 2.0 sen in Rokugan\nEdo 1766: "
    );
    assert_eq!(dollars(-12345.0, Some(20000.0)), "$-12,300");
    // every digit below the place: `round(30, -2)` is 0, `round(51, -2)` 100
    assert_eq!(
        (dollars(30.0, Some(20000.0)), dollars(51.0, Some(20000.0))),
        ("$0".to_owned(), "$100".to_owned())
    );
    let twice = "<span class=\"money\" data-amount=\"9\" data-amount=\"1\" data-coin=\"ryo\" data-era=\"edo\">1</span>";
    let one = Table {
        eras: json!({"edo": {"place": "Edo", "years": "1766", "units": {"ryo": unit}}})
            .as_object()
            .unwrap()
            .clone(),
        awaiting: serde_json::Map::new(),
    };
    assert!(annotate(twice, "w", &one)
        .unwrap()
        .0
        .contains("data-def=\"1: about $1.00-$2.00 in goods"));
    let bad = json!({"goods_dollars": "x"});
    assert_eq!(
        hover_box(&[1.0], "x", bad.as_object().unwrap(), e, false)
            .unwrap_err()
            .kind,
        "TypeError"
    );
    assert_eq!(
        hover_box(&[1.0], "x", u, json!({}).as_object().unwrap(), false)
            .unwrap_err()
            .message,
        "'place'"
    );
    let table = Table {
        eras: json!({"edo": {"place": "Edo", "years": "1766", "units": {"ryo": [1]}}, "flat": 5})
            .as_object()
            .unwrap()
            .clone(),
        awaiting: serde_json::Map::new(),
    };
    let text = "<p data-era=\"edo\"><span class=\"money\" data-amount=\"1\" data-coin=\"ryo\">1</span></p>";
    assert_eq!(annotate(text, "w", &table).unwrap_err().kind, "TypeError");
    let text = "<p data-era=\"flat\"><span class=\"money\" data-amount=\"1\" data-coin=\"ryo\">1</span></p>";
    assert_eq!(
        annotate(text, "w", &table).unwrap_err().kind,
        "AttributeError"
    );
    let text =
        "<p data-era=\"edo\"></div><span class=\"money\" data-amount=\"1\" data-coin=\"mon\">1";
    assert_eq!(
        annotate(text, "w", &table).unwrap().1,
        ["w: the amount '1' names coin 'mon', which era 'edo' has no unit for (it has: ryo)"]
    );
    let empty = Table::default();
    let text = "<span class=\"money\" data-amount=\"1\" data-coin=\"mon\" data-era=\"x\">1</span>";
    assert_eq!(
        annotate(text, "w", &empty).unwrap().1,
        ["w: the amount '1' names era 'x', which the conversion table does not have and research/assets/money-eras-awaiting.json does not list (known: none)"]
    );
    assert_eq!(
        annotate("<p>no money</p>", "w", &empty).unwrap(),
        ("<p>no money</p>".to_owned(), Vec::new())
    );
}
