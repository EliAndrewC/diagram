//! Each verb of the door, on a scratch record.

use serde_json::{json, Value};

use super::{answer, serve};
use crate::record::testkit::{edit_everything, git, record, DRAWING, PAGE};

fn ok(verb: &str, args: &[Value]) -> Value {
    answer(verb, args).unwrap()
}

#[test]
fn the_pure_verbs_and_the_constants() {
    assert_eq!(ok("ru.question", &[json!("0094.drawing#k")]), "0094");
    assert_eq!(ok("ru.digest", &[json!(["a"])]).as_str().unwrap().len(), 16);
    assert_eq!(
        ok(
            "ru.read_page",
            &[json!("<h2>H</h2><p class=\"intro\">I.</p>")]
        )["intro"],
        "I."
    );
    assert_eq!(
        ok(
            "ru.read_notes",
            &[json!("<li data-note=\"a\">x</li>"), json!("")]
        )["a"],
        "x"
    );
    assert_eq!(ok("ru.stem_matches", &[json!("0001-a.html")]), true);
    assert_eq!(
        ok(
            "ru.unit",
            &[json!("a:b"), json!("w"), json!("f"), json!("")]
        )["subject"],
        "b"
    );
    for c in [
        "QUESTIONS",
        "FORM_CHECK",
        "RESEARCH_CHECKS",
        "DEPICTION_CHECK",
        "RESEARCH_AGENT",
        "ORDER",
        "MODAL_DIRS",
        "MODALS",
        "FIXED",
        "AGENT_UNITS",
    ] {
        assert!(!ok(&format!("const.{c}"), &[]).is_null());
    }
    assert_eq!(
        ok("mo.kinds_in", &[json!("class A:\n    key = 'a'\n")])[0][1],
        "a"
    );
    assert!(answer("mo.kinds_in", &[json!("x = (\n")]).is_err());
    assert!(
        ok("mo.modal_file", &[json!("x/classes/a.py"), json!("Well")])
            .as_str()
            .unwrap()
            .ends_with("hamlet/well.md")
    );
    let m = ok(
        "mo.choice_modal",
        &[
            json!("x/modals/choice/a.md"),
            json!("About: a\n"),
            json!(true),
        ],
    );
    assert_eq!(m["uid"], "choice/a");
    assert!(ok("mo.choice_modal", &[json!("a.md"), json!(""), json!(false)]).is_null());
    assert_eq!(ok("mo.depiction_owed_by", &[Value::Null, m.clone()]), true);
    assert_eq!(ok("mo.depiction_owed_by", &[m.clone(), m.clone()]), false);
    assert_eq!(
        ok("mo.earlier_units", &[json!(["modal-gaps"])]),
        json!(["modal-form"])
    );
    assert_eq!(ok("mt.triage_only", &[json!("a page its Entry")]), true);
    assert_eq!(
        ok("ro.reply_checks", &[json!("record-format: 1")]),
        json!(["record-format"])
    );
    assert!(answer("no.such", &[]).is_err());
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one scratch record walked through every verb in order, so a read follows its own write"
)]
fn the_verbs_that_read_and_write_the_repository() {
    let root = record("owed-door");
    edit_everything(&root);
    let r = json!(root.to_string_lossy());
    let store = json!(root.join(".git/record-checks").to_string_lossy());
    let base = git(&root, &["rev-parse", "HEAD"]);
    assert!(!ok(
        "ro.units",
        &[r.clone(), Value::Null, Value::Null, Value::Null, json!("")]
    )
    .as_array()
    .unwrap()
    .is_empty());
    assert!(
        ok(
            "ro.units",
            &[
                r.clone(),
                Value::Null,
                Value::Null,
                json!(["modal"]),
                json!("sheet/well")
            ]
        )
        .as_array()
        .unwrap()
        .len()
            >= 4
    );
    assert!(!ok("ro.unanswered", &[r.clone()])
        .as_array()
        .unwrap()
        .is_empty());
    assert_eq!(ok("ro.merge_base", &[r.clone()]), json!(base));
    assert_eq!(
        ok("ro.git", &[r.clone(), json!(["rev-parse", "HEAD"])]),
        json!(format!("{base}\n"))
    );
    assert!(ok("ro.store", &[r.clone()])
        .as_str()
        .unwrap()
        .ends_with("record-checks"));
    let rec = ok(
        "ro.read_at",
        &[r.clone(), Value::Null, json!(["0001-key-a.html"])],
    );
    assert!(rec["notes"]["0094"]["n"].is_string() && rec["cites"]["0094"]["k"].is_array());
    let pair = ok(
        "ru.fingerprint_and_keys",
        &[
            r.clone(),
            json!(base),
            Value::Null,
            json!(["quote-check:0094#k"]),
        ],
    );
    assert_eq!(pair["quote-check:0094#k"].as_array().unwrap().len(), 2);
    assert!(ok(
        "ru.fingerprints_of",
        &[
            r.clone(),
            Value::Null,
            json!([]),
            json!(["intro-check:0094"])
        ]
    )["intro-check:0094"]
        .is_string());
    let _ = answer(
        "ru.fingerprints_of",
        &[json!("/nonexistent/x"), Value::Null, Value::Null, json!([])],
    )
    .is_err();
    ok(
        "ro.write_answer",
        &[
            store.clone(),
            json!("a:b"),
            json!("f"),
            json!("r"),
            json!({"p": "b"}),
        ],
    );
    assert_eq!(
        ok(
            "ro.answered",
            &[store.clone(), json!("a:b"), json!("f"), json!("")]
        ),
        true
    );
    assert_eq!(
        ok("ro._read", &[store.clone(), json!("a:b")])["result"],
        "r"
    );
    assert_eq!(
        ok(
            "ro.settle",
            &[store.clone(), json!("a:b"), json!("f"), json!("g")]
        ),
        "answered"
    );
    ok(
        "ro.keep_reading",
        &[store.clone(), json!("a:b"), json!("rd"), json!("readings")],
    );
    assert!(
        ok("ro.fingerprints", &[r.clone(), json!(["record-format"])])
            .as_object()
            .unwrap()
            .contains_key("record-format:0094")
    );
    assert_eq!(
        ok(
            "ro.file_outside",
            &[
                r.clone(),
                json!("c"),
                json!("## OUTSIDE THE CHANGE\n- `f` | b | x\n")
            ]
        )
        .as_array()
        .unwrap()
        .len(),
        1
    );
    assert_eq!(
        ok(
            "ro.answer",
            &[
                r.clone(),
                json!("record-format"),
                json!("x"),
                json!(""),
                json!("94"),
                json!(""),
                json!(""),
                json!(""),
                json!("")
            ]
        ),
        json!(["record-format:0094"])
    );
    let modals = ok("mo.modals_now", &[r.clone(), json!(true)]);
    let well = modals[0].clone();
    assert_eq!(
        ok("mo.modals_now", &[r.clone(), json!(false)])
            .as_array()
            .unwrap()
            .len(),
        5
    );
    assert!(ok("mo.modals_at", &[r.clone(), json!(base), json!(true)])
        .as_object()
        .unwrap()
        .contains_key("hamlet/well"));
    assert_eq!(
        ok("mo.find", &[r.clone(), json!("well")])["uid"],
        "hamlet/well"
    );
    assert!(ok("mo.find", &[r.clone(), json!("nope")]).is_null());
    assert_eq!(
        ok("mo.fingerprints", &[r.clone(), well.clone()])
            .as_array()
            .unwrap()
            .len(),
        2
    );
    assert!(ok("mo.depiction_fingerprint", &[r.clone(), well.clone()]).is_string());
    assert!(!ok("mo.owed", &[r.clone(), json!(base), json!("")])
        .as_array()
        .unwrap()
        .is_empty());
    assert!(
        ok("mt.keep", &[r.clone(), json!(PAGE)])
            .as_str()
            .unwrap()
            .len()
            == 40
    );
    assert_eq!(
        ok(
            "mt.refusal",
            &[
                r.clone(),
                well.clone(),
                json!("modal-form"),
                json!([["a", "b", "c"]])
            ]
        ),
        ""
    );
    assert!(ok(
        "mt.refusal",
        &[r.clone(), well, json!("modal-research"), Value::Null]
    )
    .as_str()
    .unwrap()
    .contains("TRIAGE"));
    let fresh = record("owed-door-none");
    let none = ok(
        "mt.bundle",
        &[
            json!(fresh.to_string_lossy()),
            json!(fresh.join("tri").to_string_lossy()),
            json!(""),
        ],
    );
    assert_eq!(none, json!([Value::Null, 0]));
    std::fs::write(root.join(DRAWING), "<p>moved</p>").unwrap();
    let made = ok(
        "mt.bundle",
        &[
            r.clone(),
            json!(root.join("tri").to_string_lossy()),
            json!(""),
        ],
    );
    assert!(made[1].as_u64().unwrap() > 0);
    assert!(ok("to.owed", &[r.clone()]).as_array().unwrap().len() >= 2);
    assert!(answer(
        "ro.settle",
        &[
            json!("/proc/nonexistent"),
            json!("a:b"),
            json!("x"),
            json!("y")
        ]
    )
    .is_err());
}

#[test]
fn the_loop_answers_in_order() {
    let mut out = Vec::new();
    let mut input: &[u8] = b"{\"verb\": \"ru.question\", \"args\": [\"0001#a\"]}\n";
    assert_eq!(serve(&mut input, &mut out).code, 0);
    assert_eq!(String::from_utf8(out).unwrap(), "{\"ok\": \"0001\"}\n");
}
