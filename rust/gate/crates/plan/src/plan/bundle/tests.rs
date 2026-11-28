//! What a plan review reads.

use std::path::Path;

use fancy_regex::Captures;
use serde_json::{json, Value};

use super::super::tests::{git, repo};
use super::{
    answered, build, delta_prompt, expand_ranges, measured, paragraphs, request_sections,
    requirements, spec_amendments, task_prompt, trimmed_request, DECISION, IDS, QUALIFIED,
};
use crate::checks::scratch;

const REQUEST: &str = "# Feature 900 - the GM's request\n\n> the original words\n\n## Amendment 1 (2026-10-01)\n\nThe first change.\n\n> one\n\n### Amendment 1, extended\n\n> one more\n\n## Amendment 2 (2026-10-02)\n\nThe second change.\n\n> two\n\n## Amendment 3 (2026-10-03)\n\n> three\n";
const SPEC: &str = "## Requirements\n\n- **FR-001 The original.** x\n\n### Amendment 1 - first (`request.md`, Amendment 1)\n\n- **FR-002 One.** y\n\n### Amendment 2 - second\n\n- **FR-003 Two.** z\n- **SC-009** (FR-003) measured\n\n## Success criteria\n";

fn under(pairs: &[(&str, &str)]) -> Vec<(String, String)> {
    pairs
        .iter()
        .map(|(k, b)| ((*k).to_owned(), (*b).to_owned()))
        .collect()
}

#[test]
fn the_newest_amendment_carries_the_original_and_itself() {
    let n = answered(
        &under(&[(
            "## Amendment 3 (FR-004)",
            "## Amendment 3 (FR-004)\n\n**D9 - x.**",
        )]),
        SPEC,
    );
    let (req, index) = trimmed_request(REQUEST, n);
    assert_eq!(n, Some(3));
    assert!(
        req.contains("> the original words")
            && req.contains("> three")
            && !req.contains("> one")
            && !req.contains("> two")
    );
    assert!(
        index.contains("## Amendment 1 (2026-10-01) - The first change.")
            && index.contains("## Amendment 2 (2026-10-02) - The second change.")
    );
}

#[test]
fn an_earlier_amendment_carries_every_later_one() {
    let n = answered(
        &under(&[("plan block", "**D4 - the wave (FR-003, SC-009).** text")]),
        SPEC,
    );
    let (req, index) = trimmed_request(REQUEST, n);
    assert_eq!(n, Some(2));
    assert!(req.contains("> two") && req.contains("> three") && !req.contains("> one"));
    assert!(!req.contains("### Amendment 1, extended"));
    assert_eq!(index.matches("## Amendment").count(), 1);
}

#[test]
fn a_later_amendment_correcting_an_earlier_requirement_carries_the_earlier_words() {
    let n = answered(
        &under(&[(
            "## Amendment 3, reopened (FR-002 corrected)",
            "## Amendment 3, reopened (FR-002 corrected)\n\n**D9 - x.**",
        )]),
        SPEC,
    );
    let (req, index) = trimmed_request(REQUEST, n);
    assert_eq!(n, Some(1));
    assert!(req.contains("> one") && req.contains("> three") && index.is_empty());
}

#[test]
fn the_earliest_of_several_blocks_wins_and_an_original_block_gets_it_whole() {
    let n = answered(
        &under(&[("## Amendment 3", "x"), ("## Amendment 1, reopened", "y")]),
        SPEC,
    );
    assert_eq!(n, Some(1));
    assert!(trimmed_request(REQUEST, n).0.contains("> one more"));
    assert_eq!(
        answered(
            &under(&[("## Decisions", "**D1 - the original (FR-001).**")]),
            SPEC
        ),
        None
    );
    assert_eq!(
        answered(
            &under(&[("## Amendment 2", "x"), ("## Phases", "nothing cited")]),
            SPEC
        ),
        None
    );
    assert_eq!(
        answered(&under(&[("key", "## Amendment 2\n")]), SPEC),
        Some(2)
    );
    assert_eq!(answered(&[], SPEC), None);
    assert_eq!(
        trimmed_request(REQUEST, None),
        (REQUEST.to_owned(), String::new())
    );
    let plain = "# Feature 901\n\n> just the words\n";
    assert_eq!(
        trimmed_request(plain, Some(2)),
        (plain.to_owned(), String::new())
    );
    assert_eq!(request_sections(plain), (plain, Vec::new()));
}

#[test]
fn spec_amendments_map_each_id_to_its_section() {
    let got = spec_amendments(SPEC);
    assert_eq!(
        got.into_iter().collect::<Vec<_>>(),
        [
            ("FR-002".to_owned(), 1),
            ("FR-003".to_owned(), 2),
            ("SC-009".to_owned(), 2)
        ]
    );
}

#[test]
fn a_requirement_written_as_a_heading_is_cited_whole() {
    let spec = "## Requirements\n\n### FR-006 - the reason outside the file\n\nThe body.\n\n- (c) a clause\n\n### FR-007 - next\n\nx\n\n- **SC-008** (FR-006): done.\n";
    let got = requirements(spec);
    assert_eq!(
        got["FR-006"],
        "### FR-006 - the reason outside the file\n\nThe body.\n\n- (c) a clause\n"
    );
    assert_eq!(got["SC-008"], "- **SC-008** (FR-006): done.\n");
    assert_eq!(got.len(), 3);
}

/// A requirement written with no list dash (`**FR-007** ...`, `**FR-004 - title.** ...`: 24 specs of features 129 to 271 write some
/// so, measured 2026-11-21) is carried with its text, to the next requirement or heading (451 T82: it was NOT FOUND, 449's
/// "FR-007 of feature 239" among them). A dashed item or a heading of the same id still wins: 170's `### FR-006` restated in bold
/// under it, and 177's dashed FR-006a beside a later bold "FR-006a, PROVEN" commentary. An indented sub-item with its own id (184's and
/// 295's FR-005a to FR-005d) is read too, found by this task's own bundle naming them NOT FOUND.
#[test]
fn a_requirement_with_no_list_dash_is_cited_with_its_text() {
    let spec = "## Requirements\n\n**FR-001** The bench MUST refuse a guard,\nnaming FR-002.\n\nIts own paragraph.\n\n**FR-002 - what a failed proof does.** The field.\n**FR-009a** lettered.\n\n**SC-003a** (`done`) the median.\n\n- **FR-010** dashed beside them.\n\n**FR-010, PROVEN rather than assured** commentary.\n\n- **FR-012** parent.\n  - **FR-012a** its sub-item.\n    continued.\n\nA paragraph of the section.\n\n### FR-006 - a guard file's reason\n\n**FR-006 - restated in bold.** under it.\n\n### FR-007 - next\n\nx\n\n## After\n\n**FR-011** last.\n";
    let got = requirements(spec);
    assert_eq!(
        got["FR-001"],
        "**FR-001** The bench MUST refuse a guard,\nnaming FR-002.\n\nIts own paragraph.\n"
    );
    assert_eq!(
        got["FR-002"],
        "**FR-002 - what a failed proof does.** The field.\n"
    );
    assert_eq!(got["FR-009a"], "**FR-009a** lettered.\n");
    assert_eq!(got["SC-003a"], "**SC-003a** (`done`) the median.\n");
    assert_eq!(got["FR-010"], "- **FR-010** dashed beside them.\n");
    // an indented sub-item with its own id (184's FR-005a, 295's FR-005a) is carried as a list item, its parent keeping it too
    assert_eq!(
        got["FR-012"],
        "- **FR-012** parent.\n  - **FR-012a** its sub-item.\n    continued.\n"
    );
    assert_eq!(
        got["FR-012a"],
        "  - **FR-012a** its sub-item.\n    continued.\n"
    );
    assert_eq!(
        got["FR-006"],
        "### FR-006 - a guard file's reason\n\n**FR-006 - restated in bold.** under it.\n"
    );
    assert_eq!(got["FR-011"], "**FR-011** last.\n");
    assert_eq!(got.len(), 10);
}

/// Another feature's dashless requirement arrives under its feature's line, never as NOT FOUND (451 T82: 449's plan-done.md line 967,
/// "FR-007 of feature 239", and 383's plan.md line 503, "256's FR-004", each got a NOT FOUND line on the plan crate unedited, measured
/// 2026-11-21).
#[test]
fn another_feature_s_dashless_requirement_is_carried_from_it() {
    let (root, dir) = feature();
    let other = root.join("specs/239-x");
    std::fs::create_dir_all(&other).unwrap();
    std::fs::write(other.join("spec.md"), "## Requirements\n\n**FR-006** Before.\n\n**FR-007** The bench MUST refuse a guard whose decision it cannot import.\n\n**FR-008** After.\n").unwrap();
    let out = scratch("out");
    let body = "## T15 - x\n\n`bench` TAKES ANY GUARD: FR-007 of feature 239 refused a guard; 239's FR-004 is not there.\n";
    let m = build(&dir, &out, "T15", &under(&[("## T15 - x", body)]), &[], "h").unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    assert!(cited.contains("<!-- feature 239 -->\n**FR-007** The bench MUST refuse a guard whose decision it cannot import.\n"));
    assert!(!cited.contains("FR-007**: NOT FOUND") && !cited.contains("**FR-008** After."));
    assert!(cited
        .contains("<!-- feature 239 -->\n- **FR-004**: NOT FOUND - specs/239-x holds no FR-004"));
}

#[test]
fn a_list_of_this_feature_s_ids_is_not_read_as_another_feature_s() {
    let body = "## D1 - the rule (FR-001, FR-002)\n\nfeature 383 FR-043 is another feature's; feature 407 FR-007 is ours.\n";
    let kept = QUALIFIED.replace_all(body, |q: &Captures<'_>| {
        if &q[1] == "407" {
            q[2].to_owned()
        } else {
            String::new()
        }
    });
    let ids: Vec<String> = IDS
        .captures_iter(&kept)
        .map_while(Result::ok)
        .map(|c| c[1].to_owned())
        .collect();
    assert_eq!(ids, ["D1", "FR-001", "FR-002", "FR-007"]);
}

#[test]
fn a_task_s_own_decision_label_is_not_the_spec_s_decision() {
    // 451 T257's review (2026-11-25): T256's section labeled its decisions T256-D1 to D5, and its bundle carried the spec's D1 to D5
    let n = super::named(
        "- T256-D1 THE ROUTE: as D3 says, and FR-002; T12a-D2b beside it.\n",
        "999",
        &[],
    );
    assert_eq!(super::ids_in(&n.bare), ["D3", "FR-002"]);
    assert_eq!(expand_ranges("T256-D1 and D1-D2"), " and D1, D2");
}

#[test]
fn every_written_form_of_a_decision_is_read() {
    let plan = "**D83 - a knot gathered.** body\n\n- **D96 - the tread off a wall.** body\n\n- **D121** The rows released.\n\n- **D7 The placed-house index**: body\n\n**D8.** `make hooks-test` body\n\n**Dx** not one\n- D9 - THE BINARY FROM ITS OWN TREE: body\n  its second line\n- D10 - NEXT: body\n- D11 is not a decision\n";
    let got = paragraphs(plan, &DECISION);
    let mut keys: Vec<&String> = got.keys().collect();
    keys.sort();
    assert_eq!(keys, ["D10", "D121", "D7", "D8", "D83", "D9", "D96"]);
    assert_eq!(
        got["D9"],
        "- D9 - THE BINARY FROM ITS OWN TREE: body\n  its second line\n"
    );
    assert_eq!(got["D121"], "- **D121** The rows released.\n");
}

#[test]
fn a_cited_range_is_written_out_id_by_id() {
    assert_eq!(
        expand_ranges("D5 (FR-005-FR-007)"),
        "D5 (FR-005, FR-006, FR-007)"
    );
    assert_eq!(
        expand_ranges("FR-001 to FR-003; SC-002 to 004"),
        "FR-001, FR-002, FR-003; SC-002, SC-003, SC-004"
    );
    assert_eq!(
        expand_ranges("FR-007-FR-005 and FR-001 to FR-099"),
        "FR-007-FR-005 and FR-001 to FR-099"
    );
    assert_eq!(
        expand_ranges("(D1-D4; FR-001 to FR-002)"),
        "(D1, D2, D3, D4; FR-001, FR-002)"
    );
    assert_eq!(expand_ranges("D5 to D3"), "D5 to D3");
}

#[test]
fn a_cited_measurement_is_carried_whole() {
    let dir = scratch("measured");
    std::fs::write(dir.join("measurements.json"), r#"{"hooks-bash": {"value": "26 guards", "method": "bash -x", "n": 3}, "other": {"value": "x"}, "not": 3}"#).unwrap();
    let got = measured(
        &dir,
        &["per `m:hooks-bash`, and `m:hooks-bash` again, and `m:missing` and `m:not`"],
    );
    assert!(
        got.contains("### m:hooks-bash")
            && got.contains("- **method**: bash -x")
            && got.contains("- **n**: 3")
            && !got.contains("other")
    );
    assert_eq!(got.matches("### m:").count(), 1);
    assert_eq!(measured(&dir, &["no figure"]), "");
    std::fs::write(dir.join("measurements.json"), "not json").unwrap();
    assert_eq!(measured(&dir, &["`m:hooks-bash`"]), "");
}

const PLAN: &str = "# Plan\n\n**D1 - shared.** Every gate is checked once.\n\n## Batch 2\n\n### Wave 2 (T02)\n\n**D3 - the well.** The well stands by the lane (FR-002).\n\n## Notes\n\nA note.\n";
const SPEC2: &str = "# Spec\n\n## Requirements\n\n- **FR-001 The sty.** A sty stands against the house.\n- **FR-002 The well.** A well stands by its lane.\n- **FR-003 Unrelated.** Something else entirely.\n\n## Success criteria\n\n- **SC-001** (FR-001) The sty is drawn.\n";

fn feature() -> (l7r_shared::tempdir::TempDir, std::path::PathBuf) {
    let root = repo();
    let dir = root.join("specs/999-x");
    std::fs::create_dir_all(&dir).unwrap();
    for (name, text) in [
        ("plan.md", PLAN),
        ("spec.md", SPEC2),
        ("request.md", "> the GM's words\n"),
    ] {
        std::fs::write(dir.join(name), text).unwrap();
    }
    (root, dir)
}

fn read(dir: &Path, name: &str) -> String {
    std::fs::read_to_string(dir.join(name)).unwrap()
}

#[test]
fn a_requirement_cited_as_another_feature_s_is_bundled_from_that_feature() {
    let (root, dir) = feature();
    let other = root.join("specs/375-enforced");
    std::fs::create_dir_all(&other).unwrap();
    std::fs::write(other.join("spec.md"), "## Requirements\n\n- **FR-002 The archive.** Archiving voids nothing.\n- **FR-044 The plan.** Finished sections move.\n").unwrap();
    let out = scratch("out");
    let body = "## T05 - x\n\nAs feature 375's FR-002 has it, and 375 FR-044, and feature 375, FR-099 (no such id); FR-001 is ours; feature 999 FR-003 too; feature 123 FR-001 nowhere.\n";
    let m = build(&dir, &out, "t", &under(&[("## T05 - x", body)]), &[], "how").unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    assert!(
        cited.contains("<!-- feature 375 -->\n- **FR-002 The archive.**")
            && cited.contains("FR-044 The plan.")
    );
    assert!(
        cited.contains("FR-001 The sty.")
            && cited.contains("FR-003 Unrelated")
            && !cited.contains("FR-002 The well.")
    );
    // an id not where it is named is named as not found, never dropped without a word (451 T46)
    assert!(cited.contains(
        "<!-- feature 375 -->\n- **FR-099**: NOT FOUND - specs/375-enforced holds no FR-099"
    ));
    assert!(cited.contains(
        "<!-- feature 123 -->\n- **FR-001**: NOT FOUND - feature 123 has no directory under specs/"
    ));
    std::fs::write(
        other.join("plan.md"),
        "# Plan\n\n**D18 - lands open.** An open box holds the landing unless the line names it.\n",
    )
    .unwrap();
    std::fs::write(
        dir.join("plan.md"),
        format!("{PLAN}\n**D18 - the sty.** One predicate.\n"),
    )
    .unwrap();
    for body in [
        "## T05 - x\n\nFeature 375 plan D18 says so.\n",
        "## T05 - x\n\nFeature 375 amendment 11 (D18) holds; 375 amendment 6, FR-002 too.\n",
    ] {
        let m = build(
            &dir,
            &out,
            "t2",
            &under(&[("## T05 - x", body)]),
            &[],
            "how",
        )
        .unwrap();
        let cited = read(m.parent().unwrap(), "spec-cited.md");
        assert!(cited.contains("D18 - lands open.") && !cited.contains("D18 - the sty."));
    }
}

#[test]
fn the_bundle_is_lean_and_shows_each_earlier_verdict() {
    let (_dir, dir) = feature();
    let out = scratch("out");
    let earlier = [
        ("T05".to_owned(), "then".to_owned(), "BLOCKED".to_owned()),
        ("T06".to_owned(), "before".to_owned(), String::new()),
    ];
    let m = build(
        &dir,
        &out,
        "T05",
        &under(&[("the section of T05", "now D3 and FR-002")]),
        &earlier,
        "how to record",
    )
    .unwrap();
    let b = m.parent().unwrap();
    let text = read(b, "earlier.md");
    assert!(text.starts_with("# Each changed block's text when last judged, with that verdict"));
    assert!(
        text.contains("<!-- block \"T05\" verdict BLOCKED -->\nthen")
            && text.contains("\"T06\" verdict no verdict recorded")
            && !text.contains("CLEAR")
    );
    assert!(
        read(b, "MANIFEST.md").contains("and the verdict it got")
            && read(b, "MANIFEST.md").contains("how to record")
    );
    assert_eq!(read(b, "request.md"), "> the GM's words\n");
    assert!(read(b, "request-index.md").contains("(none - the whole request"));
    assert!(read(b, "spec-cited.md").contains("FR-002 The well."));
    assert!(read(b, "spec-index.md").contains("FR-003 Unrelated"));
    assert!(read(b, "blocks.md").contains("<!-- block \"the section of T05\" sha256 "));
    // the rulings the blocks cite ride in their own file, which the MANIFEST names (feature 449 T169)
    assert!(read(b, "rulings.md").ends_with("(none - the blocks cite no `ask:` ruling)\n"));
    assert!(read(b, "MANIFEST.md")
        .contains("`rulings.md` the round arbiter's ruling, why, what and tooling fix"));
    let none = build(&dir, &out, "T06", &under(&[("T06", "x")]), &[], "h").unwrap();
    assert!(read(none.parent().unwrap(), "earlier.md").contains("every block here is new"));
}

/// 461 T70: a reviewer copies a block's key from its comment into `make plan-verdict BLOCKS=1`, so the comment carries the heading
/// as plan.md holds it - a double quote and a non-ASCII letter unescaped (T32,T33's first record was refused on a `\"`).
#[test]
fn a_block_s_key_comment_is_the_heading_as_plan_md_holds_it() {
    let (_dir, dir) = feature();
    let out = scratch("out-key");
    let key = "### T32 (`make rust-test CRATE=\"<several>\"` failed, caf\u{e9})";
    let earlier = [(key.to_owned(), "then".to_owned(), "BLOCKED".to_owned())];
    let m = build(&dir, &out, "k", &under(&[(key, "body")]), &earlier, "h").unwrap();
    let b = m.parent().unwrap();
    let blocks = read(b, "blocks.md");
    let copied = blocks
        .strip_prefix("<!-- block \"")
        .and_then(|rest| rest.split_once("\" sha256 "))
        .map(|(k, _)| k);
    assert_eq!(copied, Some(key));
    let (was, want) = (
        read(b, "earlier.md"),
        format!("<!-- block \"{key}\" verdict BLOCKED -->\nthen"),
    );
    assert!(was.contains(&want));
}

#[test]
fn a_feature_with_no_request_gets_no_bundle_and_a_long_name_is_cut() {
    let root = scratch("no-request");
    let dir = root.join("specs/905-x");
    std::fs::create_dir_all(&dir).unwrap();
    let out = scratch("out");
    let why = build(&dir, &out, "T01", &under(&[("T01", "x")]), &[], "h").unwrap_err();
    assert!(why.contains("specs/905-x/request.md is missing") && why.contains("verbatim"));
    assert_eq!(std::fs::read_dir(&out).unwrap().count(), 0);
    let (_dir, dir) = feature();
    let long = "x".repeat(200);
    let m = build(&dir, &out, &long, &under(&[("T01", "y")]), &[], "h").unwrap();
    assert!(m.parent().unwrap().file_name().unwrap().len() < 150);
}

#[test]
fn a_block_key_in_a_comment_is_escaped_as_json_escapes_it() {
    assert_eq!(
        super::ascii_json("a é \"b\" 𝄞"),
        "\"a \\u00e9 \\\"b\\\" \\ud834\\udd1e\""
    );
}

fn record_review(dir: &Path, review: &Value) {
    std::fs::write(dir.join("plan-review.json"), review.to_string()).unwrap();
}

#[test]
fn a_task_prompt_shows_the_section_s_earlier_text() {
    let (root, dir) = feature();
    let out = scratch("out");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "c"]);
    let sec = super::super::sections::task_sections(PLAN)["T02"].clone();
    let sha = super::super::sections::digest(sec.as_bytes());
    record_review(
        &dir,
        &json!({"tasks": {"T02": {"section_sha256": sha, "verdict": "BLOCKED"}}}),
    );
    std::fs::write(dir.join("plan.md"), PLAN.replace("the lane", "the road")).unwrap();
    let prompt = task_prompt(&dir, &out, "T02").unwrap();
    assert!(prompt.contains("feature 999-x, task T02"));
    let b = bundle_of(&prompt);
    assert!(
        read(&b, "earlier.md").contains("verdict BLOCKED")
            && read(&b, "MANIFEST.md").contains("TASK=T02")
    );
    // THE TREE IT WAS BUILT FROM (451 T257): named, and the recording command run there
    let tree = std::fs::canonicalize(&root).unwrap().display().to_string();
    let manifest = read(&b, "MANIFEST.md");
    assert!(manifest.contains(&format!("Built from the tree `{tree}`")));
    assert!(manifest.contains(&format!("make -C {tree} plan-verdict F=999 TASK=T02 FILE=")));
}

#[test]
fn a_delta_prompt_carries_earlier_text_and_removed_blocks_and_each_block_set_its_own_directory() {
    let (root, dir) = feature();
    let out = scratch("out");
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "c"]);
    let notes = "## Notes\n\nA note.\n";
    let gone = "## Gone\n\nold text\n";
    let review = json!({"blocks": {"### Wave 2 (T02)": {"sha256": "x", "verdict": "CLEAR", "text": "was"}, "## Notes": {"sha256": super::block_digest(notes), "verdict": "BLOCKED"}, "## Gone": {"sha256": super::block_digest(gone), "verdict": "CLEAR", "text": gone}}});
    record_review(&dir, &review);
    let keys = [
        "### Wave 2 (T02)".to_owned(),
        "## Notes".to_owned(),
        "(removed) ## Gone".to_owned(),
        "(removed) ## Never".to_owned(),
    ];
    let prompt = delta_prompt(&dir, &out, &keys).unwrap();
    assert!(prompt.contains("MODE 4: PLAN REVIEW of 4 changed block(s)"));
    let manifest = prompt
        .split("read ")
        .nth(1)
        .unwrap()
        .split(" and the files")
        .next()
        .unwrap()
        .to_owned();
    let b = Path::new(&manifest).parent().unwrap().to_owned();
    assert!(b
        .file_name()
        .unwrap()
        .to_string_lossy()
        .starts_with("plan-999-x-blocks-plan-"));
    let earlier = read(&b, "earlier.md");
    assert!(
        earlier.contains("verdict CLEAR -->\nwas")
            && earlier.contains("(removed) ## Gone")
            && earlier.contains("verdict BLOCKED -->\n## Notes")
    );
    assert!(
        read(&b, "MANIFEST.md").contains("BLOCKS=1")
            && read(&b, "MANIFEST.md").contains("\"(removed) ## Gone\": \"removed\"")
    );
    let tree = std::fs::canonicalize(&root).unwrap().display().to_string();
    assert!(read(&b, "MANIFEST.md")
        .contains(&format!("make -C {tree} plan-verdict F=999 BLOCKS=1 FILE=")));
    let plain = delta_prompt(&dir, &out, &["## Notes".to_owned()]).unwrap();
    assert!(plain.contains("blocks-plan-"));
    std::fs::write(dir.join("plan.md"), format!("{PLAN}\n### T02 extra\n\nz\n")).unwrap();
    assert!(delta_prompt(&dir, &out, &["### T02 extra".to_owned()])
        .unwrap()
        .contains("blocks-T02-"));
}

#[test]
fn the_request_is_trimmed_to_the_amendment_the_blocks_answer() {
    let (_dir, dir) = feature();
    std::fs::write(dir.join("request.md"), REQUEST).unwrap();
    let out = scratch("out");
    let m = build(
        &dir,
        &out,
        "t",
        &under(&[("## Amendment 3", "x")]),
        &[],
        "h",
    )
    .unwrap();
    let b = m.parent().unwrap();
    assert!(read(b, "request-index.md").contains("## Amendment 1 (2026-10-01) - The first change."));
    assert!(!read(b, "request.md").contains("> one"));
}

#[test]
fn the_bundle_is_lean_and_each_block_set_has_its_own_directory() {
    let (root, dir) = feature();
    let out = scratch("out");
    let reviewed = json!({"blocks": {"### Wave 2 (T02)": {"sha256": super::block_digest("### Wave 2 (T02)\n\n**D3 - the well.** The well stands by the lane (FR-002).\n\n"), "verdict": "CLEAR"}}});
    record_review(&dir, &reviewed);
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "reviewed"]);
    std::fs::write(
        dir.join("plan.md"),
        PLAN.replace(
            "by the lane (FR-002)",
            "by the lane, two to a lane (FR-002)",
        ),
    )
    .unwrap();
    let key = ["### Wave 2 (T02)".to_owned()];
    let prompt = delta_prompt(&dir, &out, &key).unwrap();
    let first = Path::new(
        prompt
            .split("read ")
            .nth(1)
            .unwrap()
            .split(" and the files")
            .next()
            .unwrap(),
    )
    .parent()
    .unwrap()
    .to_owned();
    assert_eq!(read(&first, "request.md"), "> the GM's words\n");
    let cited = read(&first, "spec-cited.md");
    assert!(
        cited.contains("FR-002 The well.** A well stands by its lane.")
            && !cited.contains("FR-003")
    );
    assert!(read(&first, "spec-index.md").contains("FR-003 Unrelated"));
    assert!(
        read(&first, "blocks.md").contains("two to a lane")
            && !read(&first, "blocks.md").contains("Notes")
    );
    assert!(
        read(&first, "earlier.md").contains("by the lane (FR-002)")
            && read(&first, "earlier.md").contains("verdict CLEAR -->")
    );
    let size: u64 = std::fs::read_dir(&first)
        .unwrap()
        .flatten()
        .map(|e| e.metadata().unwrap().len())
        .sum();
    // the MANIFEST names its tree twice, the line and the recording command (451 T257)
    let tree = std::fs::canonicalize(dir.parent().unwrap().parent().unwrap())
        .unwrap()
        .display()
        .to_string()
        .len();
    assert!(size < (SPEC2.len() + PLAN.len() + 2000 + 2 * tree) as u64);
    std::fs::write(
        dir.join("plan.md"),
        PLAN.replace(
            "by the lane (FR-002)",
            "by the lane, three to a lane (FR-002)",
        ),
    )
    .unwrap();
    let again = delta_prompt(&dir, &out, &key).unwrap();
    let second = Path::new(
        again
            .split("read ")
            .nth(1)
            .unwrap()
            .split(" and the files")
            .next()
            .unwrap(),
    )
    .parent()
    .unwrap()
    .to_owned();
    assert_ne!(first, second);
    assert!(read(&first, "blocks.md").contains("two to a lane"));
}

/// A decision past a megabyte of plan (feature 449, found 2026-11-18): the decisions are read from plan.md and plan-done.md together, and
/// once 449's two passed 1,000,000 bytes `fancy_regex` gave up `DECISION`'s search (a lookahead runs it in the backtracking VM, about
/// one step a character) with an error the `.flatten()` here repeated without advancing - `make decide F=449 T=T194` spun without end in
/// `task_prompt` (measured 2026-11-18 on a scratch copy, probes around `decide`'s three calls, 10 KB of prose added to plan-done.md). The
/// scan reads to the end, bounded here so that the test cannot spin.
#[test]
fn a_decision_past_a_megabyte_of_plan_is_read() {
    let text = format!(
        "- **D1** - the first.\n\n{}- **D2** - the last.\n",
        "plain words of a finished section\n".repeat(40_000)
    );
    let (tx, rx) = std::sync::mpsc::channel();
    let _scan = std::thread::spawn(move || tx.send(paragraphs(&text, &DECISION)));
    let found = rx
        .recv_timeout(std::time::Duration::from_secs(20))
        .expect("the decisions' scan spun past its bound");
    assert_eq!(
        found.keys().map(String::as_str).collect::<Vec<_>>(),
        ["D1", "D2"]
    );
}

/// A decision is carried whole, its lists included, to the next decision or heading (feature 451 T37, found by T19's plan review
/// 2026-11-20): the fixture is 451's plan.md D14 to D17 verbatim as of 07cc8f2cd1, where `spec-cited.md` stopped D15 at its colon and
/// D16 at "Two things make the comparison real:", the first blank line, and a reviewer judged each without its bullets.
#[test]
fn a_decision_is_carried_whole_with_its_lists() {
    let plan = include_str!("fixtures/451-d14-d17.md");
    let got = paragraphs(plan, &DECISION);
    let d15 = got["D15"].as_str().unwrap();
    assert!(d15.starts_with("**D15 - The deferral's form**"));
    assert!(
        d15.contains("- **Both ids name an OPEN task**")
            && d15.contains("- **Judged once, at the decision.**")
    );
    assert!(d15.ends_with("No\nopen section of any plan is refused by it today (R9).\n"));
    let d16 = got["D16"].as_str().unwrap();
    assert!(d16.contains("Two things make the comparison real:\n\n- **Every check runs to its own end in both runs.**"));
    assert!(d16.contains("- **Findings are compared, not checks.**"));
    assert!(d16.ends_with("`QUICK_OK` on `make task-add` escapes, through `$(LOGESCAPE)`.\n"));
    // the last decision stops at the next heading, and each stops at the next decision
    assert!(got["D17"].as_str().unwrap().ends_with("never a gate).\n"));
    assert!(!got["D14"].as_str().unwrap().contains("D15 - "));
}

/// A list item - an FR or SC, a decision written as a bullet - runs on across a blank line only into its own indented lines, and
/// stops at a heading with no blank line before it (feature 451 T37: 383's FR-041 carried the `### Amendment 7` heading under it).
#[test]
fn a_list_item_runs_on_into_its_indented_lines_only() {
    let spec = "- **FR-004**: What owes what:\n\n  | a | b |\n  |---|---|\n\n- **FR-005** next\n  its line\n\nA paragraph of the section, not the item's.\n\n- **FR-041** The sweep.\n  classed\n### Amendment 7\n\n- **FR-042** x";
    let got = requirements(spec);
    assert_eq!(
        got["FR-004"],
        "- **FR-004**: What owes what:\n\n  | a | b |\n  |---|---|\n"
    );
    assert_eq!(got["FR-005"], "- **FR-005** next\n  its line\n");
    assert_eq!(got["FR-041"], "- **FR-041** The sweep.\n  classed\n");
    assert_eq!(got["FR-042"], "- **FR-042** x\n");
    let plan = "- D9 - THE RULE: body\n\n\n  - its own clause\n\n- not D9's\n";
    assert_eq!(
        paragraphs(plan, &DECISION)["D9"],
        "- D9 - THE RULE: body\n\n\n  - its own clause\n"
    );
}

/// A decision named as another feature's is carried from that feature and never from the reviewed one (feature 451 T46, found by T42's
/// plan review 2026-11-20): the fixture is T42's section verbatim from 451's plan-done.md at 212266c482, which names "feature 204 D5",
/// "feature 204 spec D5, D6", a bare "D5's form" and "; D6 (unknown resolves toward main)", and "house style's D11" - and
/// `spec-cited.md` carried 451's own D5, D6 and D11 for all three. Feature 204 keeps its decisions in its spec (no plan.md).
#[test]
fn another_feature_s_decisions_are_carried_from_it_never_from_this_one() {
    let root = repo();
    let dir = root.join("specs/451-x");
    let other = root.join("specs/204-guards");
    for d in [&dir, &other] {
        std::fs::create_dir_all(d).unwrap();
    }
    let ours = "# Plan\n\n**D5 - OURS FIVE.** x\n\n**D6 - OURS SIX.** x\n\n**D11 - OURS ELEVEN.** x\n\n**D3 - OURS THREE.** x\n";
    std::fs::write(dir.join("plan.md"), ours).unwrap();
    for d in ["specs/777-a", "specs/777-b"] {
        std::fs::create_dir_all(root.join(d)).unwrap();
    }
    std::fs::write(
        dir.join("spec.md"),
        "## Requirements\n\n- **FR-013**: Performance work goes first.\n- **FR-002**: Ours.\n",
    )
    .unwrap();
    std::fs::write(dir.join("request.md"), "> words\n").unwrap();
    std::fs::write(
        other.join("spec.md"),
        format!("## Decisions\n\n{}", include_str!("fixtures/204-d5-d6.md")),
    )
    .unwrap();
    let out = scratch("out");
    let section = include_str!("fixtures/451-t42.md");
    let m = build(
        &dir,
        &out,
        "T42",
        &under(&[("the section of T42", section)]),
        &[],
        "h",
    )
    .unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    assert!(
        !cited.contains("OURS ELEVEN")
            && cited.matches("OURS FIVE").count() == 1
            && cited.matches("OURS SIX").count() == 1
    );
    // the bare "D5's form" and "; D6 (unknown resolves toward main)" carry 451's text only under the line saying they may mean either
    assert!(cited.contains("<!-- feature 451's D5, cited bare; the blocks also name feature 204's D5, so a bare D5 may mean either -->\n**D5 - OURS FIVE.**"));
    assert!(cited.contains("<!-- feature 451's D6, cited bare; the blocks also name feature 204's D6, so a bare D6 may mean either -->\n**D6 - OURS SIX.**"));
    assert!(cited.contains("<!-- feature 204 -->\n- **D5 - `python3 -c` remains a write.**"));
    assert!(cited.contains("<!-- feature 204 -->\n- **D6 - unknown resolves toward main.**"));
    assert!(cited.contains("- **D11**: NOT FOUND - named as house style's"));
    assert!(cited.contains("FR-013**: Performance work goes first."));
    // every other form: a bare number, a requirement of a feature with no such id, a feature with no directory, a list after "and";
    // and the possessives that name this feature's own documents still carry its own decisions
    let body = "## T05\n\n204 D5 holds, and feature 204's D5 and D6; 449 FR-023 and 123 D1 are named; the claims gate's FR-010 too. The plan's D3 and this feature's FR-002 are ours, the reviewed feature's FR-013 too, T31's D11 too; a gate's FR-020 is not; 777 D1 is twice.\n";
    let m = build(&dir, &out, "T05", &under(&[("T05", body)]), &[], "h").unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    assert!(!cited.contains("OURS FIVE") && !cited.contains("OURS SIX"));
    assert_eq!(cited.matches("<!-- feature 204 -->").count(), 2);
    assert!(cited.contains("- **FR-023**: NOT FOUND - feature 449 has no directory under specs/"));
    assert!(cited.contains("- **D1**: NOT FOUND - feature 123 has no directory under specs/"));
    assert!(cited.contains("- **FR-010**: NOT FOUND - named as claims gate's"));
    assert!(cited.contains("OURS THREE") && cited.contains("- **FR-002**: Ours."));
    // a task's decision is read from that task's section, never the plan's (461 T68)
    let t31 = "<!-- feature 451 T31 -->\n- **D11**: NOT FOUND - specs/451-x has no T31 section";
    assert!(cited.contains(t31) && !cited.contains("OURS ELEVEN"));
    assert!(cited.contains("- **FR-020**: NOT FOUND - named as gate's"));
    assert!(
        cited.contains("- **FR-013**: Performance work goes first.")
            && !cited.contains("reviewed feature's")
    );
    assert!(cited.contains("- **D1**: NOT FOUND - feature 777 has 2 directories under specs/"));
    std::fs::create_dir_all(root.join("specs/449-a")).unwrap();
    std::fs::write(root.join("specs/449-a/spec.md"), "- **FR-001**: x\n").unwrap();
    let m = build(
        &dir,
        &out,
        "T06",
        &under(&[(
            "T06",
            "449 FR-023 is cited; the style's FR-013; FR-013 bare.\n",
        )]),
        &[],
        "h",
    )
    .unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    assert!(cited.contains("- **FR-023**: NOT FOUND - specs/449-a holds no FR-023 in its spec.md, plan.md or plan-done.md"));
    assert!(cited.contains("<!-- feature 451's FR-013, cited bare; the blocks also name style's FR-013, so a bare FR-013 may mean either -->\n- **FR-013**: Performance"));
}

/// A block citing another feature's requirement does not answer this feature's amendment holding the same id (451 T46).
#[test]
fn another_feature_s_id_answers_no_amendment_of_this_one() {
    let (_root, dir) = feature();
    let spec = "## Requirements\n\n- **FR-001** x\n\n### Amendment 2 - second\n\n- **FR-023** the amended one\n";
    std::fs::write(dir.join("spec.md"), spec).unwrap();
    std::fs::write(
        dir.join("request.md"),
        "> original\n\n## Amendment 1 (a)\n\n> one\n\n## Amendment 2 (b)\n\n> two\n",
    )
    .unwrap();
    let out = scratch("out");
    let m = build(
        &dir,
        &out,
        "T07",
        &under(&[("T07", "449 FR-023 and FR-001.\n")]),
        &[],
        "h",
    )
    .unwrap();
    assert!(read(m.parent().unwrap(), "request.md").contains("> one"));
}

/// An index line is the requirement's first sentence whole, its wrapped lines joined (feature 451 T46: FR-009's line stopped at "unless
/// it states why the defect is not"); a sentence past `INDEX_CAP` is cut at a word and marked, never cut silently.
#[test]
fn an_index_line_is_carried_whole() {
    let (_root, dir) = feature();
    let spec = "## Requirements\n\n- **FR-009**: `make decide` refuses a plan section whose found-and-left item defers a defect unless it states why the defect is not\n  fixed in this task, its filed task id and its order (\"lands before ...\"); and refuses a section whose fix names a class of defect\n  (every writer, every form, every file of a kind) without a line saying how every instance of the class was found, labeled as an\n  observation with its method.\n- **FR-010**: The three slowest hook suites are split.\n  1. a numbered clause\n- **FR-013**: Performance work goes first:\n  - its first clause\n- **FR-014**: The `a. b` span is code. Its second sentence.\n- **FR-016**: Each kind (e.g. a well) is drawn, cf. the sty. Then more.\n- **FR-017**: A list ... of things is kept, vs. none. More.\n- **FR-018**: A plain word ends here. then the sentence runs on. Then a new one.\n- **FR-030**: Kinds (e.g. `well`) are drawn. More.\n- **FR-031**: A thing (it runs. Here it ends) and more.\n- **FR-015**: word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word.\n\n### FR-020 A heading one\n\nits body\n";
    std::fs::write(dir.join("spec.md"), spec).unwrap();
    let out = scratch("out");
    let m = build(
        &dir,
        &out,
        "T08",
        &under(&[("T08", "nothing cited")]),
        &[],
        "h",
    )
    .unwrap();
    let index = read(m.parent().unwrap(), "spec-index.md");
    assert!(index.starts_with("# Every other requirement, its first sentence on one line (past 420 characters cut at a word and marked [...])\n\n"));
    assert!(index.contains("\n- **FR-009**: `make decide` refuses a plan section whose found-and-left item defers a defect unless it states why the defect is not fixed in this task, its filed task id and its order (\"lands before ...\"); and refuses a section whose fix names a class of defect (every writer, every form, every file of a kind) without a line saying how every instance of the class was found, labeled as an observation with its method.\n"));
    assert!(index.contains("\n- **FR-010**: The three slowest hook suites are split.\n- **FR-013**: Performance work goes first:\n- **FR-014**: The `a. b` span is code. [...]\n"));
    // a `.` before a lowercase word ends no sentence, whatever came before it (451 T46: no cut is left unmarked)
    assert!(index
        .contains("\n- **FR-018**: A plain word ends here. then the sentence runs on. [...]\n"));
    // an abbreviation or an ellipsis before a lowercase word ends no sentence (451 T46's review)
    assert!(index.contains("\n- **FR-016**: Each kind (e.g. a well) is drawn, cf. the sty. [...]\n- **FR-017**: A list ... of things is kept, vs. none. [...]\n"));
    let marked = index
        .lines()
        .find(|l| l.starts_with("- **FR-015**"))
        .unwrap();
    assert!(marked.ends_with(" word [...]") && marked.chars().count() <= 420 + 6);
    assert!(index.contains("\n### FR-020 A heading one\n"));
    // by construction: every line shorter than its requirement's lead paragraph ends marked
    for text in requirements(spec).values().filter_map(Value::as_str) {
        let (line, whole) = (super::lead(text), super::paragraph(text));
        assert!(line == whole || line.ends_with(" [...]"), "{line}");
    }
    // a line shorter than its lead paragraph always ends marked, whatever ended it (451 T46 round 2: 132 FR-023 at "e.g." before a
    // backtick, 246 FR-002 inside an open parenthesis)
    assert!(index
        .contains("\n- **FR-030**: Kinds (e.g. [...]\n- **FR-031**: A thing (it runs. [...]\n"));
}

/// A number then a task's possessive names that feature's id ("444 T20's FR-043", "433 T01's D3b"; 451 T46's plan review): it is
/// carried from that feature or named NOT FOUND, never dropped as this feature's.
#[test]
fn a_number_then_a_task_s_possessive_names_that_feature_s_id() {
    let (root, dir) = feature();
    let other = root.join("specs/444-x");
    std::fs::create_dir_all(&other).unwrap();
    std::fs::write(other.join("spec.md"), "- **FR-043**: THEIRS.\n").unwrap();
    let out = scratch("out");
    let body = "As 444 T20's FR-043 says; 449 T233's FR-005, and D1 and D3 in 999's sections; 204 D5, and FR-002 of feature 999; 123 D9 and FR-003 of feature 999; 123 D8 of the plan's; 433 T01's D3b too; 449 T233's FR-023 and FR-024; 999 T02's FR-001 is ours.\n";
    let m = build(&dir, &out, "T09", &under(&[("T09", body)]), &[], "h").unwrap();
    let cited = read(m.parent().unwrap(), "spec-cited.md");
    // T46's own sentence: the run stops at ", and D1 and D3 in 999's sections"
    let own = "449 T233's FR-023 and FR-024, and D1 and D3 in 999's sections of T42 and T44.\n";
    let k = build(&dir, &out, "T10", &under(&[("T10", own)]), &[], "h").unwrap();
    let mine = read(k.parent().unwrap(), "spec-cited.md");
    assert!(
        mine.contains("D1 - shared.")
            && mine.contains("D3 - the well.")
            && mine.contains("- **FR-024**: NOT FOUND")
            && !mine.contains("- **D1**: NOT FOUND")
    );
    assert!(cited.contains("<!-- feature 444 -->\n- **FR-043**: THEIRS."));
    // a task's decision is that task's section's (461 T68)
    assert!(cited.contains("<!-- feature 433 T01 -->\n- **D3b**: NOT FOUND"));
    assert!(cited.contains("<!-- feature 449 -->\n- **FR-024**: NOT FOUND"));
    assert!(cited.contains("FR-001 The sty."));
    // a feature number's run stops at a clause naming another source (451 T46 round 2: "449 T233's FR-023 and FR-024, and D5 and D11 in
    // 451's sections" carried 449's D5)
    assert!(
        !cited.contains("- **D1**: NOT FOUND")
            && !cited.contains("- **D3**: NOT FOUND")
            && !cited.contains("- **FR-002**: NOT FOUND")
    );
    assert!(
        cited.contains("D1 - shared.")
            && cited.contains("D3 - the well.")
            && cited.contains("FR-002 The well.")
    );
    assert!(
        cited.contains("FR-003 Unrelated")
            && cited.contains("- **D9**: NOT FOUND")
            && cited.contains("- **D8**: NOT FOUND")
    );
}

/// Ids inside a clause naming another feature by its number ("FR-010 of feature 134", "spec D1 of feature 207", "FR-025 of 132") are
/// that feature's: carried from it or named NOT FOUND, never this feature's same-named id (451 T48, measured 2026-11-21 over every
/// plan: 4 of the 5 real clauses carried the reviewed feature's own text unmarked, 319's FR-010 among them).
#[test]
fn ids_in_a_clause_naming_another_feature_are_that_feature_s() {
    let (root, dir) = feature();
    let other = root.join("specs/134-x");
    std::fs::create_dir_all(&other).unwrap();
    std::fs::write(other.join("spec.md"), "- **FR-001**: THEIRS.\n").unwrap();
    std::fs::write(
        other.join("plan.md"),
        "**D1 - their baseline.** The last full run.\n",
    )
    .unwrap();
    let out = scratch("out");
    let cited_of = |task: &str, body: &str| {
        let m = build(&dir, &out, task, &under(&[(task, body)]), &[], "h").unwrap();
        read(m.parent().unwrap(), "spec-cited.md")
    };
    // the shapes of 319, 415 and 133: a bare id, then the clause
    let bare = cited_of("T11", "A second serialization (FR-001 of feature 134); the baseline (spec D1 of feature 134); FR-002 of 132.\n");
    assert!(bare.contains("<!-- feature 134 -->\n- **FR-001**: THEIRS."));
    assert!(bare.contains("<!-- feature 134 -->\n**D1 - their baseline.**"));
    assert!(bare.contains(
        "<!-- feature 132 -->\n- **FR-002**: NOT FOUND - feature 132 has no directory under specs/"
    ));
    assert!(
        !bare.contains("The sty.") && !bare.contains("D1 - shared.") && !bare.contains("its lane")
    );
    // a number's run cut at a clause naming another feature: the part after the cut is the clause's
    let cut = cited_of("T12", "449 T233's FR-003, and D3 in 134's sections.\n");
    assert!(cut.contains("<!-- feature 449 -->\n- **FR-003**: NOT FOUND"));
    assert!(cut.contains("<!-- feature 134 -->\n- **D3**: NOT FOUND - specs/134-x holds no D3"));
    assert!(!cut.contains("Something else") && !cut.contains("the well."));
    // this feature's run cut so: its own ids carried, the clause's taken from the clause's feature
    let own = cited_of("T13", "999's FR-001, FR-003, and D1 in 134's sections.\n");
    assert!(own.contains("The sty.") && own.contains("Something else"));
    assert!(
        own.contains("<!-- feature 134 -->\n**D1 - their baseline.**")
            && !own.contains("D1 - shared.")
    );
    // a clause naming this feature is its own: carried, unmarked
    let mine = cited_of("T14", "D3 and FR-002 of feature 999.\n");
    assert!(mine.contains("D3 - the well.") && mine.contains("its lane") && !mine.contains("<!--"));
}

/// The bundle directory a dispatch prompt names.
fn bundle_of(prompt: &str) -> std::path::PathBuf {
    let manifest = prompt.split("read ").nth(1).unwrap();
    let manifest = manifest.split(" and the files").next().unwrap();
    Path::new(manifest).parent().unwrap().to_owned()
}

/// TWO TREES, ONE BUNDLES DIRECTORY (451 T271): two worktrees of one feature owe the same changed blocks whenever their plans
/// agree, and the second `make plan-delta` rewrote the first's bundle - its tree line and recording command the other tree's - under
/// the first's reviewer. The changed-blocks bundle is the tree's, and so is a task's own bundle (451 T288).
#[test]
fn two_trees_owing_the_same_blocks_get_a_bundle_each_and_one_tree_keeps_its_own() {
    let ((one, dir_one), (two, dir_two)) = (feature(), feature());
    let out = scratch("out");
    let keys = ["## Notes".to_owned()];
    let first = bundle_of(&delta_prompt(&dir_one, &out, &keys).unwrap());
    let second = bundle_of(&delta_prompt(&dir_two, &out, &keys).unwrap());
    assert_ne!(first, second);
    // the first tree's bundle still names the first tree, the second's the second
    for (root, bundle) in [(&one, &first), (&two, &second)] {
        let tree = std::fs::canonicalize(root).unwrap().display().to_string();
        assert!(read(bundle, "MANIFEST.md").contains(&format!("Built from the tree `{tree}`")));
    }
    // one tree's rebuild is the same directory, its name the shape every reader of it matches: `-blocks-<tasks>-<8 hex>`
    assert_eq!(
        bundle_of(&delta_prompt(&dir_one, &out, &keys).unwrap()),
        first
    );
    let name = first.file_name().unwrap().to_string_lossy().into_owned();
    let hex = name.strip_prefix("plan-999-x-blocks-plan-").unwrap();
    let shaped = hex.len() == 8 && hex.chars().all(|c| c.is_ascii_hexdigit());
    assert!(shaped, "{name}");
    // ONE TASK DECIDED IN TWO TREES (451 T288): since 451 T369 a task is started in a pool tree and the clone both, and the second
    // `make decide` rewrote the first's bundle under the first's reviewer - so a task's bundle is its tree's too, two bundles here
    let task_one = bundle_of(&task_prompt(&dir_one, &out, "T02").unwrap());
    let task_two = bundle_of(&task_prompt(&dir_two, &out, "T02").unwrap());
    assert_ne!(task_one, task_two);
    for (root, bundle) in [(&one, &task_one), (&two, &task_two)] {
        let tree = std::fs::canonicalize(root).unwrap().display().to_string();
        assert!(read(bundle, "MANIFEST.md").contains(&format!("Built from the tree `{tree}`")));
    }
    // one tree's re-decide is the same directory, named `plan-<feature>-<task>-<8 hex>` - the shape the plan hold matches
    assert_eq!(
        bundle_of(&task_prompt(&dir_one, &out, "T02").unwrap()),
        task_one
    );
    let name = task_one.file_name().unwrap().to_string_lossy().into_owned();
    let hex = name.strip_prefix("plan-999-x-T02-").unwrap();
    assert!(hex.len() == 8 && hex.chars().all(|c| c.is_ascii_hexdigit()));
}
