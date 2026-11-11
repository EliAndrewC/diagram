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
        .flatten()
        .map(|c| c[1].to_owned())
        .collect();
    assert_eq!(ids, ["D1", "FR-001", "FR-002", "FR-007"]);
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

fn feature() -> (l7r_guard::shared::tempdir::TempDir, std::path::PathBuf) {
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
    let none = build(&dir, &out, "T06", &under(&[("T06", "x")]), &[], "h").unwrap();
    assert!(read(none.parent().unwrap(), "earlier.md").contains("every block here is new"));
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
    let b = out.join("plan-999-x-T02");
    assert!(
        read(&b, "earlier.md").contains("verdict BLOCKED")
            && read(&b, "MANIFEST.md").contains("TASK=T02")
    );
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
    assert!(size < (SPEC2.len() + PLAN.len() + 2000) as u64);
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
