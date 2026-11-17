//! `l7r-gate registry dump | silent` (feature 449 T149): the library's reading of a tree, refusals named where the Python raised.

use serde_json::Value;

use super::cli;
use l7r_gate_core::checks::scratch;
use l7r_gate_core::record::testkit::put;

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_dump_reads_both_registries_and_each_map_s_knobs() {
    let root = scratch("registry-dump");
    let r = root.to_string_lossy().into_owned();
    // nothing there: every part names the refusal the Python raised
    let empty: Value = serde_json::from_str(&cli(&args(&["dump", "--root", &r])).stdout).unwrap();
    assert!(empty["classes"]["error"]
        .as_str()
        .unwrap()
        .starts_with("OSError: "));
    assert!(empty["knobs"]["error"].is_string() && empty["maps"].as_object().unwrap().is_empty());
    crate::testkit::modals(&root, "research/questions/x.html [form=row]");
    put(
        &root,
        crate::conditions::KNOBS_FILE,
        "{\"knobs\": {\"form\": {\"forms\": [\"row\", \"dot\"]}}}",
    );
    put(&root, crate::choices::TABLE, "{\"choices\": [{\"key\": \"form\", \"name\": \"How\", \"values\": {\"row\": \"in a row\"}}]}");
    put(
        &root,
        "l7r/diagram/interactive/assets/page-text.json",
        "{\"not_highlighted_rulings\": [], \"not_highlighted_overturned\": []}",
    );
    put(&root, crate::about::modal_rel(&crate::kinds::HAMLET_REGISTRY, "byre").as_str(), "About: [form=row] a\n\n[form=dot] b\nGuesses:\n- [form=row] g\nName: Byre\nCovers: c\nSources: s\nEntry: research/questions/x.html [form=row]\nDrawing: research/questions/x.drawing.html [form=dot]\n");
    put(
        &root,
        crate::about::modal_rel(&crate::kinds::HAMLET_REGISTRY, "garden").as_str(),
        "About: a\nGuesses:\n- [nope=x] g\nName: Garden\nCovers: c\nSources: s\nEntry: e\n",
    );
    put(&root, "maps/a.json", "{\"meta\": {\"form\": \"row\"}}");
    put(&root, "maps/b.json", "{\"form\": \"dot\"}");
    put(&root, "maps/c.json", "[1]");
    put(&root, "maps/d.json", "{bad");
    let said = cli(&args(&[
        "dump",
        "--root",
        &r,
        &format!("{r}/maps/a.json"),
        &format!("{r}/maps/b.json"),
        &format!("{r}/maps/c.json"),
        &format!("{r}/maps/d.json"),
        "/no/such.json",
    ]));
    assert_eq!(said.code, 0);
    let got: Value = serde_json::from_str(&said.stdout).unwrap();
    assert_eq!(
        (
            got["classes"].as_array().unwrap().len(),
            got["compound"].as_array().unwrap().len()
        ),
        (61, 99)
    );
    let a = &got["maps"][format!("{r}/maps/a.json")];
    assert_eq!(a["made"][0]["value"], "in a row");
    assert_eq!(a["hamlet"]["alder"]["entry"], "research/questions/x.html");
    assert_eq!(
        a["hamlet"]["alder"]["labels"][0],
        "(only where form is row)"
    );
    assert_eq!(a["hamlet"]["garden"]["error"], "ValueError: Garden: [nope=...] names no registered knob - one of ['form'] (dev/modals.md M22)");
    assert_eq!(
        (
            a["hamlet"]["byre"]["about"][0].as_str(),
            a["hamlet"]["byre"]["drawing"].as_str()
        ),
        (Some("a"), Some(""))
    );
    let b = &got["maps"][format!("{r}/maps/b.json")];
    assert_eq!(b["hamlet"]["alder"]["entry"], "");
    assert_eq!(
        b["hamlet"]["byre"]["drawing"],
        "research/questions/x.drawing.html"
    );
    // a recorded value the table does not know is listed by its raw value, with no modal
    assert_eq!(
        (b["made"][0]["value"].as_str(), b["made"][0]["k"].as_str()),
        (Some("dot"), Some(""))
    );
    assert_eq!(
        got["maps"][format!("{r}/maps/c.json")]["made"],
        Value::Array(vec![])
    );
    assert!(got["maps"][format!("{r}/maps/d.json")]["error"]
        .as_str()
        .unwrap()
        .starts_with("JSONDecodeError: "));
    assert!(got["maps"]["/no/such.json"]["error"]
        .as_str()
        .unwrap()
        .starts_with("OSError: "));
}

#[test]
fn the_silences_are_listed_and_a_registry_that_does_not_load_refused() {
    let root = scratch("registry-silent");
    let r = root.to_string_lossy().into_owned();
    crate::testkit::modals(&root, "research/questions/x.html");
    let silent = cli(&args(&["silent", "--root", &r]));
    assert_eq!((silent.code, silent.stdout.as_str()), (0, "  0 of 61 entries name no section; the other 61 must RESOLVE, checked at the gate and the push.\n"));
    std::fs::remove_file(root.join(crate::about::modal_rel(
        &crate::kinds::HAMLET_REGISTRY,
        "byre",
    )))
    .unwrap();
    assert_eq!(cli(&args(&["silent", "--root", &r])).code, 1);
    assert_eq!(cli(&args(&["nope"])).code, 2);
    assert_eq!(cli(&args(&["dump", "--root"])).code, 0);
}
