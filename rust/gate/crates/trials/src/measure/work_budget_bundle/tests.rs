//! The bundles on scratch trees: every refusal of a MODE BUDGET derivation, each reading of a MODE AUDIT, and the failures the
//! Python raised (feature 449 T134; the same shapes its differential ran against `work_budget_bundle.py`, 0 differing).

use std::path::Path;
use std::time::{Duration, SystemTime};

use l7r_gate_core::checks::scratch;

use super::{cli, dumps_py, glob, loads, nonfinite, num, py_re, rglob};

pub(super) const PH: &str = "specs/x/phases";

/// A derivation every check passes.
pub(super) const BASE: &str = "# Derivation - the grid stage

## Contract
- Reads: the field outline
- Writes: the ink
- Keeps: the rules of the record

## The count, factor by factor
| factor | scope | value | reason | worst case |
|---|---|---|---|---|
| items | per item | 10 at 20, 20 at 40, 40 at 80 | the things placed | the same |
| the grid's cells | over the run | 5 | each cell examined | 5 |

## Cheaper algorithms considered
- sweep: not used, nothing is ordered
- grid or spatial index: used - the grid
- priority queue: not used
- incremental update: not used
- memoizing what a scan does not change: not used

## Indexes
- the grid: cells of 64 ft; densest 4, from a smallest side of 128 ft

## Totals
- at 20: 10 + 5 = 15
- at 40: 20 + 5 = 25
- at 80: 40 + 5 = 45
";

pub(super) fn put(root: &Path, rel: &str, data: &[u8]) {
    let p = root.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, data).unwrap();
}

const RUN: &str = r#"{"meta": {}, "rows": [{"seed": 4, "households": 20, "stages": {"hem": {"total": 5, "ops": {"call@fill_out": 2, "write@field_ink": 1, "candidate@Obstacles.blocked": 3, "plain": 1}}, "sink": {"total": 1, "ops": {}}}}, {"seed": 4, "households": 40, "stages": {"hem": {"total": 9, "ops": {"call@fill_out": 4}}, "top": {"total": 1}, "water": {"total": 1, "ops": null}, "field": {"total": 1, "ops": {"call@broken": 1}}}}], "summary": {"stages": {"hem": {"per": {"40": {"ops": 1}}}, "sink": {"per": {}}}}}"#;

/// A tree with an engine of each kind: the Python hamlet stages, a seed module whose calls the audit follows, the Rust phases, runs,
/// a budget table, the pool's manifests and a call-chain report newer than every source.
pub(super) fn tree(root: &Path) {
    let files: &[(&str, &str)] = &[
        ("l7r/__init__.py", ""),
        ("l7r/diagram/__init__.py", "from .geom import area as area\n"),
        ("l7r/diagram/geom.py", "AREA_UNIT = 1\nclass Shape:\n    edge_count = 4\n    def area(self): pass\ndef area(x):\n    return x\ndef fill_out(): pass\nK = Knob(\"grid_size\", [\"small\", \"big_one\"])\n"),
        ("l7r/diagram/util.py", "def helper(): pass\nfrom .geom import fill_out as reexported\n"),
        ("l7r/diagram/shapes/__init__.py", "from .make import make\n"),
        ("l7r/diagram/shapes/make.py", "def make(): pass\n"),
        ("l7r/diagram/shapes/deep/__init__.py", ""),
        ("l7r/diagram/shapes/deep/inner.py", "def deep_fn(): pass\n"),
        ("l7r/diagram/labels/__init__.py", ""),
        (
            "l7r/diagram/labels/placer.py",
            "from l7r.diagram.geom import area, Shape\nfrom l7r.diagram import util as u2\nfrom .. import shapes\nimport l7r.diagram.util as u\nfrom l7r.diagram.util import reexported\nfrom l7r.diagram.shapes import deep_fn\nfrom ......x import y\nCOUNTER = \"write@field_ink\"\nclass Placer:\n    def run(self, s):\n        area(1)\n        u.helper()\n        u2.helper()\n        shapes.make()\n        self.mixin_method()\n        s.other_mixin()\n        self.run()\n        reexported()\n        deep_fn()\n        [].append(1)\n",
        ),
        (
            "l7r/diagram/labels/broken_seed.py",
            "COUNTER = \"call@broken\"\nfrom l7r.diagram.geom import nowhere\nimport l7r.diagram.util as uu\nimport l7r.diagram.util\nfrom l7r.diagram.missingmod import q\nfrom l7r.diagram.cyc_a import loop\nfrom l7r.diagram.shapes import absent\nnowhere()\nuu.gone()\nq()\nloop()\nabsent()\n",
        ),
        ("l7r/diagram/cyc_a.py", "from l7r.diagram.cyc_b import loop\n"),
        ("l7r/diagram/cyc_b.py", "from l7r.diagram.cyc_a import loop\n"),
        ("l7r/diagram/labels/bad.py", "def (:\n"),
        ("l7r/diagram/settlement/__init__.py", ""),
        ("l7r/diagram/settlement/mixins.py", "class M:\n    def mixin_method(self): pass\n    def other_mixin(self): pass\n"),
        ("l7r/diagram/hamletgen/__init__.py", ""),
        ("l7r/diagram/hamletgen/top.py", "def stage_top(s):\n    pass\n"),
        ("l7r/diagram/hamletgen/water/__init__.py", ""),
        ("l7r/diagram/hamletgen/water/plan.py", "def stage_water(s):\n    pass\n"),
        ("l7r/diagram/hamletgen/water/other.py", "x = 1\n"),
        ("rust/phases/src/lib.rs", "pub mod hem;\n"),
        ("rust/phases/src/hem.rs", "pub fn stage_hem() { crate::course::drawn(); crate::water::flow(); crate::nothing::x(); }\nfn blocked() {}\n"),
        ("rust/phases/src/course.rs", "pub fn drawn() {}\n"),
        ("rust/phases/src/water/mod.rs", "pub fn flow() {}\n"),
        ("rust/phases/src/sink.rs", "mod stage;\n"),
        ("rust/phases/src/sink/stage.rs", "pub(crate) fn stage_sink() { crate::course::drawn(); }\n"),
        ("rust/phases/src/sink/brook.rs", "fn brook() {}\n"),
        ("rust/phases/src/field/mod.rs", "    fn stage_field() {}\n"),
        ("rust/target/debug/gen.rs", "fn stage_target() {}\nfn fill_out() {}\n"),
        ("docs/work-budget-rubric.md", "# rubric\r\nS1-S11\n"),
        ("dev/work-budget.json", "{\"program\": {}, \"stages\": {\"hem\": {\"status\": \"budgeted\", \"per_thing\": 1.5, \"note\": \"caf\u{e9}\"}, \"grid\": {}}}"),
        ("dev/work-budget/20261101T000000Z-a.json", "{}"),
        ("dev/work-budget/20261102T000000Z-b.json", RUN),
        ("pool/hamlets/one/one.json", "{\"manifest_key\": {\"nested_key\": [{\"listed_key\": 1}]}}"),
        ("pool/hamlets/one/bad.json", "{"),
        ("pool/hamlets/stray.json", "{\"stray_key\": 1}"),
        ("tests/fixtures/budget.json", "{\"per_thing\": 3}"),
        ("dev/perf-log/20261102T000000Z-fanout-old.txt", "old\n"),
        ("dev/perf-log/notes.txt", "x\n"),
        ("dev/perf-log/20261103T000000Z-fanout-adhoc.txt", "hem: the chains\n  a -> b\nsink: other\nzz\n"),
    ];
    for (rel, text) in files {
        put(root, rel, text.as_bytes());
    }
    put(root, "pool/hamlets/one/bytes.json", b"\xff{}");
    let past = SystemTime::now() - Duration::from_secs(1000);
    for p in rglob(root, "") {
        if p.is_file() {
            let _ = std::fs::File::options()
                .append(true)
                .open(&p)
                .and_then(|f| f.set_modified(past));
        }
    }
    let report = std::fs::File::options()
        .append(true)
        .open(root.join("dev/perf-log/20261103T000000Z-fanout-adhoc.txt"))
        .unwrap();
    report.set_modified(SystemTime::now()).unwrap();
}

/// The stale report: the call-chain report older than every source.
fn stale(root: &Path) {
    let report = std::fs::File::options()
        .append(true)
        .open(root.join("dev/perf-log/20261103T000000Z-fanout-adhoc.txt"))
        .unwrap();
    report
        .set_modified(SystemTime::now() - Duration::from_secs(5000))
        .unwrap();
}

pub(super) fn run(root: &Path, args: &[&str]) -> crate::Reply {
    let mut all: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
    all.extend([
        "--root".to_owned(),
        root.to_string_lossy().into_owned(),
        "--out".to_owned(),
        root.join("out").to_string_lossy().into_owned(),
    ]);
    cli(&all, Path::new("/nowhere"))
}

fn budget(root: &Path, text: &str) -> crate::Reply {
    put(root, &format!("{PH}/grid.derivation.md"), text.as_bytes());
    run(
        root,
        &[
            "budget",
            "grid",
            "--derivation",
            &format!("{PH}/grid.derivation.md"),
        ],
    )
}

#[test]
fn a_python_pattern_matches_as_python_reads_it() {
    assert!(py_re(r"^a\sb$").is_match("a\x1cb").unwrap());
    assert!(!py_re(r"^a\Sb$").is_match("a\x1cb").unwrap());
    assert!(py_re(r"^[\s.]+$").is_match(" .\x1c").unwrap());
    assert!(py_re(r"^[]x]+$").is_match("]x").unwrap());
    assert!(py_re(r"^[^]x]+$").is_match("ab").unwrap());
    assert!(py_re(r"a\Z").is_match("ba").unwrap());
    assert!(!py_re(r"a\Z").is_match("a\n").unwrap());
    assert!(py_re(r"\d\.").is_match("1.").unwrap());
}

#[test]
fn the_listings_are_sorted_as_pathlib_sorts_them() {
    let d = scratch("wbb-glob");
    for f in ["b.json", "a.json", "x.txt", "sub/c.json", ".json"] {
        put(&d, f, b"");
    }
    std::os::unix::fs::symlink(d.join("sub"), d.join("link")).unwrap();
    let names = |v: Vec<std::path::PathBuf>| {
        v.iter()
            .map(|p| p.strip_prefix(&*d).unwrap().to_string_lossy().into_owned())
            .collect::<Vec<_>>()
    };
    assert_eq!(names(glob(&d, "", ".json")), [".json", "a.json", "b.json"]);
    assert_eq!(names(glob(&d, "b", ".json")), ["b.json"]);
    assert_eq!(
        names(rglob(&d, ".json")),
        [".json", "a.json", "b.json", "sub/c.json"]
    );
    assert!(glob(&d.join("none"), "", "").is_empty());
}

#[test]
fn the_command_line_is_argparses() {
    let d = scratch("wbb-args");
    tree(&d);
    let code = |args: &[&str]| run(&d, args).code;
    assert_eq!(cli(&[], Path::new(".")).code, 2);
    assert_eq!(code(&["budget"]), 2);
    assert_eq!(code(&["nope", "grid"]), 2);
    assert_eq!(code(&["budget", "grid", "x"]), 2);
    assert_eq!(code(&["audit", "hem", "--bogus"]), 2);
    let empty = run(&d, &["audit", ""]);
    assert_eq!(
        (empty.code, empty.stderr.as_str()),
        (2, "work-budget-bundle: PHASE= is required\n")
    );
    let none = run(&d, &["budget", "grid"]);
    assert_eq!(
        (none.code, none.stderr.as_str()),
        (
            2,
            "work-budget-bundle: MODE=budget needs DERIVATION=<file>\n"
        )
    );
    let missing = run(&d, &["budget", "grid", "--derivation", "nope.md"]);
    assert_eq!(
        (missing.code, missing.stderr.as_str()),
        (2, "work-budget-bundle: no derivation at nope.md\n")
    );
}

#[test]
fn a_sound_derivation_is_bundled_with_its_earlier_verdicts() {
    let d = scratch("wbb-budget");
    tree(&d);
    put(
        &d,
        &format!("{PH}/grid.verdict-2.txt"),
        b"LOOSE - short\n(Also: one; two.)\n",
    );
    put(&d, &format!("{PH}/grid.verdict-.txt"), b"x");
    put(&d, "out/stale.txt", b"x");
    let answers = "\n## Earlier findings\n- verdict-2, finding 1: fixed - x\n- verdict-2, finding 2: disputed - y\n- verdict-2, finding 3: fixed - z\n";
    let raised = budget(&d, &(BASE.to_owned() + answers));
    // a verdict with no number is Python's ValueError
    assert_eq!(raised.code, 1,);
    std::fs::remove_file(d.join(format!("{PH}/grid.verdict-.txt"))).unwrap();
    let got = budget(&d, &(BASE.to_owned() + answers));
    assert_eq!(
        (got.code, got.stdout.clone()),
        (0, format!("{}\n", d.join("out/MANIFEST.md").display()))
    );
    let out = d.join("out");
    assert!(!out.join("stale.txt").exists());
    assert_eq!(
        std::fs::read_to_string(out.join("rubric.md")).unwrap(),
        "# rubric\r\nS1-S11\n"
    );
    assert!(std::fs::read_to_string(out.join("contract.md"))
        .unwrap()
        .starts_with("## Contract\n- Reads"));
    assert!(out.join("grid.verdict-2.txt").is_file());
    assert!(std::fs::read_to_string(out.join("MANIFEST.md"))
        .unwrap()
        .starts_with("# work-budget MODE BUDGET - grid\n\nMODE BUDGET: judge"));
    // a CRLF derivation is read as Python reads text
    put(&d, &format!("{PH}/grid.verdict-2.txt"), b"");
    let crlf = budget(&d, &BASE.replace('\n', "\r\n"));
    assert_eq!(crlf.code, 0, "{crlf:?}");
    assert_eq!(
        std::fs::read_to_string(out.join("derivation.md")).unwrap(),
        BASE
    );
}

#[test]
fn a_derivation_holding_todays_code_is_refused() {
    let d = scratch("wbb-forbidden");
    tree(&d);
    let refused = |add: &str| budget(&d, &(BASE.to_owned() + add));
    let fence = refused("```python\nx = 1\n```\n12 ops\nsee l7r/diagram/x.py\n");
    assert_eq!(fence.code, 1);
    assert_eq!(
        fence.stderr,
        "work-budget-bundle: REFUSED - a MODE BUDGET bundle holds no code and no counts of today's code:\n  a fenced block of Python - today's code: ````python`\n  a path under l7r/ - today's code: `l7r/diagram/x.py`\n  a figure tagged as a current count (calls or ops beside a number): `12 ops`\n"
    );
    let names =
        refused("it calls `fill_out` and Shape.area, `labels/placer`, AREA_UNIT, edge_count\n");
    assert!(names.stderr.contains(
        "today's code's names (5): AREA_UNIT, edge_count, fill_out, labels, placer - write"
    ),);
    let many = refused("`fill_out` `area` `Shape` `helper` `make` `deep_fn` `mixin_method` `other_mixin` `stage_top` `stage_water` `Placer` `run` `geom` `util`\n");
    assert!(
        many.stderr.contains("today's code's names (14): ")
            && many.stderr.contains("run, stage_top ... - write"),
    );
    assert_eq!(refused("the `grid_size` knob, big_one, manifest_key, nested_key, listed_key, hem, stray_key, `placer.py.txt`\n").code, 0);
    put(&d, "dev/work-budget.json", b"{\"stages\": [\"fill_out\"]}");
    assert_eq!(refused("fill_out\n").code, 0);
    put(&d, "dev/work-budget.json", b"{\"stages\": \"fill_out\"}");
    assert_eq!(refused("fill_out\n").code, 1);
    for (table, code) in [
        ("{\"stages\": 5}", 1),
        ("[]", 1),
        ("{", 1),
        ("{\"program\": {}}", 0),
    ] {
        put(&d, "dev/work-budget.json", table.as_bytes());
        assert_eq!(refused("").code, code, "{table}");
    }
    std::fs::remove_file(d.join("dev/work-budget.json")).unwrap();
    assert_eq!(refused("fill_out\n").code, 1);
    put(&d, "pool/hamlets/one/dir.json/x", b"1");
    // a directory named .json is Python's IsADirectoryError
    assert_eq!(refused("").code, 1,);
    std::fs::remove_dir_all(d.join("pool/hamlets/one/dir.json")).unwrap();
    put(&d, "l7r/z.py", b"\xff");
    // a source that is no UTF-8 is Python's UnicodeDecodeError
    assert_eq!(refused("").code, 1,);
}

#[test]
fn a_derivation_short_of_its_form_is_refused() {
    let d = scratch("wbb-form");
    tree(&d);
    let no_contract = budget(&d, &BASE.replace("## Contract", "## Agreement"));
    assert_eq!(no_contract.stderr, "work-budget-bundle: REFUSED - the derivation has no `## Contract` section (what the stage reads and writes)\n");
    let short = budget(&d, &BASE.replace("- Writes: the ink", "- Writes: <what>"));
    assert_eq!(
        short.stderr,
        "work-budget-bundle: REFUSED - the derivation is short of the template's fields (.specify/templates/derivation.md):\n  `## Contract`: its `Writes:` line, filled\n"
    );
    let unanswered = {
        put(
            &d,
            &format!("{PH}/grid.verdict-1.txt"),
            b"LOOSE - the count is short\n",
        );
        budget(&d, BASE)
    };
    assert!(unanswered.stderr.contains("verdict-1, finding 1 unanswered - `- verdict-1, finding 1: fixed - <how>` or `disputed - <why>` (LOOSE - the count is short)"));
    put(&d, &format!("{PH}/grid.verdict-1.txt"), b"\xff");
    assert_eq!(budget(&d, BASE).code, 1);
    std::fs::remove_file(d.join(format!("{PH}/grid.verdict-1.txt"))).unwrap();
    // a Pow is `_arith`'s ValueError
    assert_eq!(
        budget(&d, &BASE.replace("10 + 5 = 15", "10 ** 5 = 15")).code,
        1,
    );
    put(&d, &format!("{PH}/grid.derivation.md"), b"\xff");
    assert_eq!(
        run(
            &d,
            &[
                "budget",
                "grid",
                "--derivation",
                &format!("{PH}/grid.derivation.md")
            ]
        )
        .code,
        1
    );
    std::fs::remove_file(d.join("docs/work-budget-rubric.md")).unwrap();
    // no rubric to copy is Python's FileNotFoundError
    assert_eq!(budget(&d, BASE).code, 1,);
}

#[test]
fn the_out_directory_is_replaced_and_a_file_there_fails() {
    let d = scratch("wbb-out");
    tree(&d);
    put(&d, "out", b"x");
    let got = budget(&d, BASE);
    assert_eq!(got.code, 1);
    assert!(got.stderr.starts_with("work-budget-bundle: OSError"));
    std::fs::remove_file(d.join("out")).unwrap();
    std::os::unix::fs::symlink(d.join("l7r"), d.join("out")).unwrap();
    assert_eq!(budget(&d, BASE).code, 1);
    // the default out directory, under /tmp/l7r-check
    put(&d, &format!("{PH}/grid.derivation.md"), BASE.as_bytes());
    let phase = format!("t134-{}", std::process::id());
    let all = [
        "budget".to_owned(),
        phase.clone(),
        "--derivation".to_owned(),
        format!("{PH}/grid.derivation.md"),
        "--root".to_owned(),
        d.to_string_lossy().into_owned(),
    ];
    let default = cli(&all, Path::new("."));
    assert_eq!(
        default.stdout,
        format!("/tmp/l7r-check/work-budget-budget-{phase}/MANIFEST.md\n")
    );
    std::fs::remove_dir_all(format!("/tmp/l7r-check/work-budget-budget-{phase}")).unwrap();
    // nothing left behind: the bundles' directory goes too, where it is empty
    let _ = std::fs::remove_dir("/tmp/l7r-check");
}

#[test]
fn an_audit_bundles_the_stage_its_counters_and_its_calls() {
    let d = scratch("wbb-audit");
    tree(&d);
    let got = run(&d, &["audit", "hem"]);
    assert_eq!(got.code, 0, "{got:?}");
    let out = d.join("out");
    let manifest = std::fs::read_to_string(out.join("MANIFEST.md")).unwrap();
    assert!(manifest.contains("(`/` as `__`): rust__phases__src__hem.rs, rust__phases__src__course.rs, rust__phases__src__water__mod.rs, "), "{manifest}");
    for name in [
        "l7r__diagram__labels__placer.py",
        "l7r__diagram__util.py",
        "l7r__diagram__shapes__make.py",
        "l7r__diagram__shapes__deep__inner.py",
        "l7r__diagram__settlement__mixins.py",
        "l7r__diagram__geom.py",
    ] {
        assert!(out.join("code").join(name).is_file(), "{name}: {manifest}");
    }
    // a build tree's source counts nothing
    assert!(!out.join("code/rust__target__debug__gen.rs").exists(),);
    let counts = std::fs::read_to_string(out.join("counts.json")).unwrap();
    assert!(counts.starts_with("{\n \"run\": \"20261102T000000Z-b.json\",\n \"summary\": {\n  \"per\": {\n   \"40\": {\n    \"ops\": 1"), "{counts}");
    assert_eq!(
        std::fs::read_to_string(out.join("chains.txt")).unwrap(),
        "from dev/perf-log/20261103T000000Z-fanout-adhoc.txt\n\nhem: the chains\n  a -> b\n"
    );
    assert_eq!(
        std::fs::read_to_string(out.join("budget.json")).unwrap(),
        "{\n \"status\": \"budgeted\",\n \"per_thing\": 1.5,\n \"note\": \"caf\\u00e9\"\n}"
    );
    let with_budget = run(
        &d,
        &["audit", "hem", "--budget", "tests/fixtures/budget.json"],
    );
    assert_eq!(with_budget.code, 0);
    assert_eq!(
        std::fs::read_to_string(out.join("budget.json")).unwrap(),
        "{\n \"per_thing\": 3\n}"
    );
    // a stage the report has no section for, the Python stages in the package root and a subpackage, the module directory, a build tree
    assert_eq!(run(&d, &["audit", "target"]).code, 0);
    assert!(std::fs::read_to_string(out.join("chains.txt"))
        .unwrap()
        .contains("(the report has no section for target)"));
    for (phase, code) in [
        ("water", 0),
        ("top", 0),
        ("sink", 0),
        ("nosuch", 2),
        ("field", 2),
    ] {
        assert_eq!(run(&d, &["audit", phase]).code, code, "{phase}");
    }
    assert_eq!(
        run(&d, &["audit", "field"]).stderr,
        "work-budget-bundle: the stage's code calls what no module under l7r/ defines - the audit could not read it:\n  absent (from l7r.diagram.shapes, called in l7r/diagram/labels/broken_seed.py)\n  l7r.diagram.util.gone (called in l7r/diagram/labels/broken_seed.py)\n  loop (from l7r.diagram.cyc_a, called in l7r/diagram/labels/broken_seed.py)\n  nowhere (from l7r.diagram.geom, called in l7r/diagram/labels/broken_seed.py)\n  q (from l7r.diagram.missingmod, called in l7r/diagram/labels/broken_seed.py)\n"
    );
    assert_eq!(
        run(&d, &["audit", "nosuch"]).stderr,
        "work-budget-bundle: no `stage_nosuch` under rust or l7r/diagram/hamletgen\n"
    );
    std::fs::remove_file(d.join("rust/phases/src/sink.rs")).unwrap();
    assert_eq!(run(&d, &["audit", "sink"]).code, 0);
    std::fs::remove_dir_all(d.join("l7r/diagram/hamletgen")).unwrap();
    // no hamlet package, no Python stage
    assert_eq!(run(&d, &["audit", "top"]).code, 2,);
}

#[test]
fn a_bundle_that_cannot_be_written_fails() {
    use std::os::unix::fs::PermissionsExt;
    let d = scratch("wbb-readonly");
    tree(&d);
    put(&d, &format!("{PH}/grid.derivation.md"), BASE.as_bytes());
    std::fs::create_dir(d.join("ro")).unwrap();
    std::fs::set_permissions(d.join("ro"), std::fs::Permissions::from_mode(0o555)).unwrap();
    let all: Vec<String> = [
        "budget",
        "grid",
        "--derivation",
        &format!("{PH}/grid.derivation.md"),
        "--root",
        &d.to_string_lossy(),
        "--out",
        &d.join("ro/out").to_string_lossy(),
    ]
    .iter()
    .map(|a| (*a).to_owned())
    .collect();
    let got = cli(&all, Path::new("."));
    std::fs::set_permissions(d.join("ro"), std::fs::Permissions::from_mode(0o755)).unwrap();
    assert_eq!(got.code, 1);
    assert!(got.stderr.contains("ro/out: Permission denied"), "{got:?}");
}

#[test]
fn an_audit_refuses_a_stale_report_and_a_missing_run() {
    let d = scratch("wbb-stale");
    tree(&d);
    stale(&d);
    assert_eq!(
        run(&d, &["audit", "hem"]).stderr,
        "work-budget-bundle: dev/perf-log/20261103T000000Z-fanout-adhoc.txt is older than the engine it would describe - run `make perf-fanout STAGES=hem` first\n"
    );
    std::fs::remove_dir_all(d.join("dev/perf-log")).unwrap();
    assert_eq!(run(&d, &["audit", "hem"]).code, 0);
    assert_eq!(
        std::fs::read_to_string(d.join("out/chains.txt")).unwrap(),
        "no `make perf-fanout` report is kept: run `make perf-fanout STAGES=hem`\n"
    );
    std::fs::remove_dir_all(d.join("dev/work-budget")).unwrap();
    assert_eq!(
        run(&d, &["audit", "hem"]).stderr,
        "work-budget-bundle: no `make work-budget` run is recorded - run it first\n"
    );
}

#[test]
fn an_audit_fails_where_the_python_raised() {
    let d = scratch("wbb-raise");
    let newest = "dev/work-budget/20261109T000000Z-z.json";
    for (rel, text, code) in [
        (newest, "{", 1),
        (newest, "{\"rows\": 5, \"summary\": {\"stages\": {}}}", 1),
        (newest, "{\"rows\": {}, \"summary\": {\"stages\": {}}}", 0),
        (newest, "{\"rows\": [{\"households\": 1, \"stages\": {\"hem\": {}}}], \"summary\": {\"stages\": {}}}", 1),
        (newest, "{\"rows\": [{\"seed\": 1, \"households\": 1, \"stages\": {\"hem\": [1]}}], \"summary\": {\"stages\": {}}}", 1),
        (newest, "{\"rows\": [{\"seed\": 1, \"households\": 1, \"stages\": [\"hem\"]}], \"summary\": {\"stages\": {}}}", 1),
        (newest, "{\"rows\": [{\"seed\": 1, \"households\": 2, \"stages\": {\"hem\": {\"seed\": 9, \"ops\": [\"call@make\", \"plain\"]}}}], \"summary\": {\"stages\": {\"hem\": null}}}", 0),
        (newest, "{\"rows\": [{\"seed\": 1, \"households\": 2, \"stages\": {\"hem\": {\"ops\": [5]}}}], \"summary\": {\"stages\": {}}}", 1),
        (newest, "{\"rows\": [{\"seed\": 1, \"households\": 2, \"stages\": {\"hem\": {\"ops\": 5}}}], \"summary\": {\"stages\": {}}}", 1),
        (newest, "{\"rows\": [{\"seed\": 1, \"households\": 2, \"stages\": {\"hem\": {\"ops\": 0}}}], \"summary\": {\"stages\": {}}}", 0),
        (newest, "{\"rows\": [{\"seed\": 1, \"households\": 2, \"stages\": {\"hem\": {\"ops\": \"\"}}}], \"summary\": {\"stages\": {}}}", 0),
        (newest, "{\"rows\": []}", 1),
        ("dev/work-budget.json", "{}", 1),
        ("dev/work-budget.json", "{", 1),
        ("rust/phases/src/z.rs", "\u{ff}", 0),
        ("l7r/diagram/labels/bad.py", "COUNTER = \"write@field_ink\"\ndef (:\n", 1),
        ("l7r/diagram/settlement/bad.py", "def (:\n", 1),
        ("rust/phases/src/sink/stage.rs", "pub(crate) fn stage_sink() { crate::field::x(); crate::course::y(); }\n", 0),
    ] {
        let _ = std::fs::remove_dir_all(&*d);
        tree(&d);
        put(&d, rel, text.as_bytes());
        assert_eq!(run(&d, &["audit", "hem"]).code, code, "{rel}: {text}");
    }
    let _ = std::fs::remove_dir_all(&*d);
    tree(&d);
    put(&d, "rust/phases/src/z.rs", b"\xff");
    // a Rust source that is no UTF-8
    assert_eq!(run(&d, &["audit", "hem"]).code, 1,);
    std::fs::remove_file(d.join("rust/phases/src/z.rs")).unwrap();
    put(&d, "l7r/diagram/hamletgen/z.py", b"\xff");
    // a hamlet source that is no UTF-8
    assert_eq!(run(&d, &["audit", "top"]).code, 1,);
    std::fs::remove_file(d.join("l7r/diagram/hamletgen/z.py")).unwrap();
    assert_eq!(run(&d, &["audit", "hem", "--budget", "nope.json"]).code, 1);
    std::fs::remove_file(d.join("docs/work-budget-rubric.md")).unwrap();
    assert_eq!(run(&d, &["audit", "hem"]).code, 1);
    std::fs::remove_dir_all(d.join("rust")).unwrap();
    std::fs::remove_dir_all(d.join("l7r/diagram/settlement")).unwrap();
    put(&d, "docs/work-budget-rubric.md", b"r");
    assert_eq!(run(&d, &["audit", "top"]).code, 0);
}

#[test]
fn the_old_code_is_the_python_the_stage_reads() {
    let d = scratch("wbb-old");
    tree(&d);
    let got = run(&d, &["--sources", "hem"]);
    // the modules defining what the stage's counters name, its Rust among them, as `phase_sources.sources` read them
    assert_eq!(
        got.stdout,
        "[\"l7r/diagram/geom.py\", \"rust/phases/src/hem.rs\", \"l7r/diagram/labels/placer.py\"]\n"
    );
    assert_eq!(run(&d, &["--sources", "water"]).stdout, "[\"l7r/diagram/hamletgen/water/__init__.py\", \"l7r/diagram/hamletgen/water/other.py\", \"l7r/diagram/hamletgen/water/plan.py\"]\n");
    put(
        &d,
        "dev/work-budget/20261109T000000Z-z.json",
        b"{\"rows\": [{\"x\": 1}]}",
    );
    assert_eq!(run(&d, &["--sources", "hem"]).code, 1);
    put(
        &d,
        "dev/work-budget/20261109T000000Z-z.json",
        b"{\"rows\": 5}",
    );
    assert_eq!(run(&d, &["--sources", "hem"]).code, 1);
    put(&d, "dev/work-budget/20261109T000000Z-z.json", b"{");
    assert_eq!(run(&d, &["--sources", "hem"]).code, 1);
    std::fs::remove_dir_all(d.join("dev/work-budget")).unwrap();
    assert_eq!(
        run(&d, &["--sources", "top"]).stdout,
        "[\"l7r/diagram/hamletgen/top.py\"]\n"
    );
}

#[test]
fn json_reads_and_writes_pythons_non_finite_numbers() {
    let v = loads(r#"{"a": Infinity, "b": [-Infinity, NaN], "s": "NaN \" Infinity", "n": 1.5}"#)
        .unwrap();
    assert_eq!(nonfinite(v["a"].as_str().unwrap()), Some(f64::INFINITY));
    assert_eq!(
        nonfinite(v["b"][0].as_str().unwrap()),
        Some(f64::NEG_INFINITY)
    );
    assert!(nonfinite(v["b"][1].as_str().unwrap()).unwrap().is_nan());
    assert_eq!(v["s"], "NaN \" Infinity");
    assert_eq!(nonfinite("plain"), None);
    assert_eq!(
        dumps_py(&v, None),
        r#"{"a": Infinity, "b": [-Infinity, NaN], "s": "NaN \" Infinity", "n": 1.5}"#
    );
    assert_eq!(dumps_py(&num(2.0), None), "2.0");
    assert_eq!(dumps_py(&num(f64::NAN), None), "NaN");
    assert_eq!(dumps_py(&num(f64::NEG_INFINITY), None), "-Infinity");
    assert!(loads("{\"a\": NaNx}").is_err());
    assert!(loads("{").is_err());
}
