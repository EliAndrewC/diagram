//! The claims tools end to end on a scratch repository: each command through [`super::cli`], the Python half a stub runner answering
//! from files the test writes (`py-units.json` beside the engine), as the real runner answers from the `.py` files.

use std::path::{Path, PathBuf};

use crate::record::testkit::{git, put};

pub const RUNNER: &str = r#"import json, pathlib, sys
for line in sys.stdin:
    a = json.loads(line); v = a["verb"]; x = a.get("args", [])
    try:
        if v == "claims_py_units":
            f = pathlib.Path(x[0], "l7r", "py-units.json")
            ok = json.loads(f.read_text()) if f.is_file() else [[], []]
            if x[2] is False:
                for half in ok:
                    for u in half:
                        u["core"] = u["core"] + "-nostar"
        elif v == "claims_module_units":
            ok = json.loads(x[0]) if x[0].startswith("[") else []
        elif v == "claims_context_source":
            if x[1].endswith("NOPE"):
                raise ValueError("no `NOPE`")
            ok = "def " + x[1].split("::")[1] + "(): pass"
        elif v == "claims_callees":
            ok = ["l7r/diagram/m.py::helper", "l7r/diagram/m.py::GAP"]
        elif v == "claims_direct":
            ok = ["l7r/diagram/m.py::FAR"]
        elif v == "claims_chase":
            ok = [x[1] + "::" + n for n in x[2]]
        elif v == "claims_counter_only":
            ok = bool(x[2].get("counter_only"))
        elif v == "claims_stale":
            ok = ["stale figure: the stub's"]
        elif v == "claims_scope_units":
            ok = json.loads(x[0].split("\n")[0]) if x[0].startswith("{") else {}
        elif v == "claims_read_units":
            ok = ["l7r/diagram/m.py::read"]
        elif v == "tunables_unstated":
            ok = [["fn", 3, 4.5], ["big", 4, 1234567]] if "4.5" in x[0] else []
        else:
            raise KeyError(v)
        print(json.dumps({"ok": ok}), flush=True)
    except Exception as e:
        print(json.dumps({"error": "Traceback (most recent call last):\n" + type(e).__name__ + ": " + str(e)}), flush=True)
"#;

/// The stand-in `codeid.py`: a file's id the hash of its text with each line's comment and the spaces before it cut, as `re.sub(rb' *#.*',
/// b'', text)` cut them - without `re`, whose import was a third of the stand-in's 17 ms start (feature 449 T167, FR-008's tenth of a
/// second).
const CODEID: &str = "import hashlib, sys\nfor p in sys.argv[2:]:\n    d = b'\\n'.join(l.split(b'#', 1)[0].rstrip(b' ') if b'#' in l else l for l in open(p, 'rb').read().split(b'\\n'))\n    print(hashlib.sha256(d).hexdigest())\n";

pub const LIB: &str = "//! The probe.
//!
//! Research:
//!     plumbing - NONE

/// A gap.
///
/// Research:
///     gap - research/questions/0001-gap.html: kept 12 ft
pub const GAP: f64 = 12.0;

/// Research: reach - research/questions/0001-gap.html: within GAP
pub fn reach(x: f64) -> f64 {
    let y = 3.25; // a number
    x + GAP + y
}

impl Thing {
    /// Research: method guess - GUESS: wider than the page, 40 ft
    pub fn m(&self) -> u32 {
        let s = \"77\";
        let a = [0; 5];
        a[1] + 42
    }
}

pub fn helper() -> u32 {
    1
}

#[cfg(test)]
mod tests {
    fn t() -> f64 {
        8888.0
    }
}
";

pub const PAGE: &str = "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A second block.</p>\n";
pub const BUILDINGS: &str = "# Buildings\n\n## Walls\n<!-- Research: walls - CONVENTION -->\n<!-- Research: wall height - research/questions/0001-gap.html: 12 ft -->\n\nWalls stand.\n\n- a list item\n  continued\n| a | table |\n|---|---|\n\n### Deep\n\nNo claim here.\n\n##### Too deep\n";

/// A repository with the probe's Rust, procedures, questions and Python half, committed and set as origin/main; its root.
pub fn fixture(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    fixture_with(tag, &|_| {})
}

/// [`fixture`], `more` writing its own files into the tree before the one commit (feature 449 T166: a commit fewer a test).
pub fn fixture_with(tag: &str, more: &dyn Fn(&Path)) -> l7r_guard::shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    // the repository `git init -b main` makes, with its three settings, written as git writes them: four processes saved (feature 449
    // T166: each end-to-end test well within FR-008's tenth of a second)
    put(&root, ".git/HEAD", "ref: refs/heads/main\n");
    // `maintenance.auto` off: each commit started `git maintenance run --auto`, a process of 2 ms more (feature 449 T167)
    put(&root, ".git/config", "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n[user]\n\temail = t@example.org\n\tname = t\n[commit]\n\tgpgsign = false\n[maintenance]\n\tauto = false\n");
    for dir in ["objects", "refs/heads", "refs/tags"] {
        std::fs::create_dir_all(root.join(".git").join(dir)).unwrap();
    }
    put(&root, "scripts/bundle_door.py", RUNNER);
    put(&root, "scripts/gates/codeid.py", CODEID);
    put(&root, "rust/phases/src/lib.rs", LIB);
    put(
        &root,
        "rust/parked/src/lib.rs",
        "/// Research: parked - NONE\npub fn p() {}\n",
    );
    put(&root, "rust/gate/src/lib.rs", "pub fn g() {}\n");
    put(&root, "rust/phases/target/x.rs", "pub fn t() {}\n");
    put(&root, "docs/buildings.md", BUILDINGS);
    put(&root, "research/questions/0001-gap.html", PAGE);
    put(
        &root,
        "research/questions/0002-other.drawing.html",
        "<h2 id=\"other\">Other</h2>\n<p>It is 40 ft, drawn.</p>\n",
    );
    put(&root, "l7r/diagram/m.py", "GAP = 12\n");
    more(&root);
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    // origin/main set as `git update-ref` sets it, the new branch's loose ref copied: a process saved (feature 449 T166)
    let head = std::fs::read_to_string(root.join(".git/refs/heads/main")).unwrap();
    put(&root, ".git/refs/remotes/origin/main", &head);
    root
}

/// [`fixture`] with no Python module under `l7r/diagram/`, so no command starts the Python half: for a test whose Python half answers
/// nothing, its 16 ms start saved (feature 449 T167, FR-008's tenth of a second); the tests that read the Python half keep the module.
pub fn fixture_rust_only(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    fixture_with(tag, &|root| {
        std::fs::remove_file(root.join("l7r/diagram/m.py")).unwrap();
    })
}

/// Every change of the tree committed, and that commit made `origin/main` as the fixture makes it: the loose ref copied, where
/// `commit` and `git update-ref` took two processes more (feature 449 T167, as [`fixture_with`]).
pub fn commit_as_origin(root: &Path, msg: &str) {
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", msg, "--allow-empty"]);
    let head = std::fs::read_to_string(root.join(".git/refs/heads/main")).unwrap();
    put(root, ".git/refs/remotes/origin/main", &head);
}

/// The Python half's answer: units of `l7r/diagram/m.py`, each `(qualname, kind, claim lines, inherited)`.
pub fn py_units(
    root: &Path,
    inside: &[(&str, &str, &[&str], bool)],
    outside: &[(&str, &str, &[&str], bool)],
) {
    let unit = |(q, kind, claims, inherited): &(&str, &str, &[&str], bool)| {
        serde_json::json!({"path": "l7r/diagram/m.py", "qualname": q, "kind": kind, "lineno": 1, "end_lineno": 1, "claims": claims,
            "inherited": inherited, "core": format!("core-{q}"), "errors": [], "names": ["GAP=12"], "blocks": [], "module_errors": ["a module error"]})
    };
    let v = serde_json::json!([
        inside.iter().map(unit).collect::<Vec<_>>(),
        outside.iter().map(unit).collect::<Vec<_>>()
    ]);
    put(root, "l7r/py-units.json", &v.to_string());
}

/// `l7r-gate claims --root <root> args...`.
pub fn claims(root: &Path, args: &[&str]) -> crate::Reply {
    let mut all = vec!["--root".to_owned(), root.to_string_lossy().into_owned()];
    all.extend(args.iter().map(|a| (*a).to_owned()));
    super::cli(&all)
}

/// Every claim of the fixture recorded IN-STEP through a bundle and its reply; the bundle's directory.
pub fn record_all(root: &Path) -> PathBuf {
    let out = root.join("b-all");
    let got = claims(root, &["bundle", "--owed", "--out", &out.to_string_lossy()]);
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    let units: serde_json::Value =
        serde_json::from_str(&std::fs::read_to_string(out.join("units.json")).unwrap()).unwrap();
    let lines: Vec<String> = units
        .as_object()
        .unwrap()
        .keys()
        .map(|k| format!("VERDICT {k} IN-STEP - fine [§1]"))
        .collect();
    let reply = root.join("reply-all.txt");
    std::fs::write(&reply, lines.join("\n")).unwrap();
    let got = claims(
        root,
        &[
            "record",
            "--bundle",
            &out.to_string_lossy(),
            "--reply",
            &reply.to_string_lossy(),
        ],
    );
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    out
}

#[test]
fn the_command_line_is_read_as_argparse_reads_it() {
    let root = fixture("claims-cli");
    let r = root.to_string_lossy().into_owned();
    for (args, why) in [
        (vec![], "the following arguments are required: cmd"),
        (vec!["--root"], "argument --root: expected one argument"),
        (vec!["--bogus"], "unrecognized arguments: --bogus"),
        (vec!["nope"], "invalid choice: 'nope'"),
        (
            vec!["--ro", &r, "record", "--bundle", "x"],
            "the following arguments are required: --reply",
        ),
        (vec!["bundle", "--nope"], "unrecognized arguments: --nope"),
    ] {
        let got = super::cli(&args.iter().map(|a| (*a).to_owned()).collect::<Vec<_>>());
        assert_eq!((got.code, got.stdout.as_str()), (2, ""), "{args:?}");
        assert!(got.stderr.contains(why), "{}", got.stderr);
    }
    let got = super::cli(&["--root=".to_owned() + &r, "triage-owed".to_owned()]);
    assert_eq!((got.code, got.stdout.as_str()), (0, "0\n"));
    let got = super::tunables_cli(&["--bogus".to_owned()]);
    assert_eq!(got.code, 2);
    assert_eq!(super::read_paths().len(), 11);
}

#[test]
fn a_failure_is_the_traceback_with_its_exit() {
    let root = fixture("claims-fail");
    put(&root, "dev/claims-index.json", "[not json");
    let got = claims(&root, &["owed"]);
    assert_eq!(got.code, 1);
    assert!(got.stderr.starts_with("Traceback (most recent call last):"),);
    put(&root, "dev/claims-index.json", "[1]");
    assert!(claims(&root, &["owed"]).stderr.contains("not an object"));
    let got = super::tunables_cli(&["--root".to_owned(), root.to_string_lossy().into_owned()]);
    assert_eq!(got.code, 0);
    put(&root, "rust/phases/src/bad.rs", "");
    std::fs::write(root.join("rust/phases/src/bad.rs"), [0xffu8, 0xfe]).unwrap();
    let got = super::tunables_cli(&["--root".to_owned(), root.to_string_lossy().into_owned()]);
    assert_eq!(got.code, 1);
    assert!(got.stderr.starts_with("Traceback"));
}

#[test]
fn the_arbiter_reads_the_rows_and_the_index() {
    let root = fixture("claims-rows");
    py_units(
        &root,
        &[("helper", "function", &["help - GUESS: 3 households"], false)],
        &[],
    );
    put(
        &root,
        "dev/claims-index.json",
        "{\"l7r/diagram/m.py::helper#help\": {\"verdict\": \"IN-STEP\"}}\n",
    );
    let (rows, index) = super::rows_and_index(&root).unwrap();
    assert_eq!(rows["l7r/diagram/m.py::helper#help"]["backing"], "GUESS");
    assert_eq!(index["l7r/diagram/m.py::helper#help"]["verdict"], "IN-STEP");
    assert!(rows["rust/phases/src/lib.rs::GAP#gap"]["line"]
        .as_str()
        .unwrap()
        .starts_with("gap - "));
    put(&root, "dev/claims-index.json", "{");
    assert!(super::rows_and_index(&root).is_err());
    assert_eq!(
        super::stdin_git(&root, &["hash-object", "--stdin"], "x\n").map(|s| s.len()),
        Some(41)
    );
    assert!(super::stdin_git(&root, &["no-such-command"], "").is_none());
}

#[test]
fn the_inline_audit_runs_from_the_command_line() {
    let root = fixture("claims-cli-inline");
    let r = root.to_string_lossy().into_owned();
    let got = super::tunables_cli(&[
        "--root".to_owned(),
        r.clone(),
        "--inline".to_owned(),
        "--count".to_owned(),
    ]);
    assert!(got
        .stdout
        .starts_with("tunables --inline: 3 number(s) in 1 file(s)"));
    put(&root, "l7r/diagram/tools/pack_audit/x.py", "4.5\n");
    put(&root, "scripts/bundle_door.py", "import sys\nsys.exit(1)\n");
    assert_eq!(
        super::tunables_cli(&["--root".to_owned(), r, "--inline".to_owned()]).code,
        1
    );
}

/// What `land.py` and `replay_owing.py` asked through `claims-door` until feature 449 T121, asked in process since: the land's scope split
/// and live marks, the replay's migration and what is owed (their tests moved here from the door's when feature 449 T132 deleted it).
#[test]
fn the_land_and_the_replay_ask_in_process() {
    let root = fixture("claims-in-process");
    py_units(
        &root,
        &[],
        &[("helper", "function", &["help - GUESS: 3 households"], false)],
    );
    assert_eq!(
        super::scope_split(
            &root,
            "  DRIFTED        l7r/diagram/m.py::read#x - y\n",
            &["l7r/diagram/m.py".to_owned()],
            &["l7r/diagram/m.py".to_owned()]
        )
        .unwrap()
        .0,
        vec!["DRIFTED        l7r/diagram/m.py::read#x - y"]
    );
    assert_eq!(super::flight_live(&root), Ok(Vec::new()));
    let (mut index, mut store) = (serde_json::Map::new(), serde_json::Map::new());
    assert_eq!(super::backfill_at(&root, &mut index, &mut store), Ok(0));
    assert!(super::owed_at(&root, &index, &store)
        .unwrap()
        .iter()
        .any(|(_, why)| why == "new"));
}

/// The fixture's six Rust and procedure units as [`record_all`] records them (their `date` the day's): written by hand, so a test whose
/// subject comes after the recording starts no bundle, no record and no Python for it - those two commands were most of two tests'
/// time against FR-008's tenth of a second (feature 449 T167). [`the_recorded_state_is_what_record_all_writes`] holds them to a run.
pub const RECORDED: &str = r#"{
"docs/buildings.md::Walls#wall height": {"body": "ba7196821a227394", "claim": "wall height - gap: 12 ft", "code": "0fe5636fcc226192", "core": "5a446aed967da80f", "note": "fine", "pages": {"0001-gap.html": "d8de3199da52b188"}, "research": "b5b0435f6efbae7e", "rests": ["0001-gap.html:920c9aa4904322d0"], "section": "5a446aed967da80f", "verdict": "IN-STEP"},
"docs/buildings.md::Walls#walls": {"body": "ba7196821a227394", "claim": "walls - CONVENTION", "code": "2e2e47bc6b29892d", "core": "5a446aed967da80f", "note": "fine", "pages": {}, "research": "", "section": "5a446aed967da80f", "verdict": "IN-STEP"},
"rust/phases/src/lib.rs::GAP#gap": {"body": "2441d6182c5ac3fb", "claim": "gap - gap: kept 12 ft", "code": "c012c9b9e4cb01c3", "core": "2397112476f581b8", "note": "fine", "pages": {"0001-gap.html": "d8de3199da52b188"}, "research": "b5b0435f6efbae7e", "rests": ["0001-gap.html:920c9aa4904322d0"], "verdict": "IN-STEP"},
"rust/phases/src/lib.rs::Thing.m#method guess": {"body": "349fea7f929680fe", "claim": "method guess - GUESS: wider than the page, 40 ft", "code": "4b53c14ed8720f5e", "core": "08b04300c56f01ee", "note": "fine", "pages": {}, "research": "", "verdict": "IN-STEP"},
"rust/phases/src/lib.rs::helper#plumbing": {"body": "c652902763db3643", "claim": "plumbing - NONE", "code": "0e22ead8f7212067", "core": "88d9634f1ba5eae9", "note": "fine", "pages": {}, "research": "", "verdict": "IN-STEP"},
"rust/phases/src/lib.rs::reach#reach": {"body": "d55170eb8b81e067", "claim": "reach - gap: within GAP", "code": "0b7dd99fe7ba3f86", "core": "6a39a13cbbb5eb5a", "note": "fine", "pages": {"0001-gap.html": "d8de3199da52b188"}, "reads": "cda22d6495590d0e", "research": "b5b0435f6efbae7e", "rests": ["0001-gap.html:920c9aa4904322d0"], "verdict": "IN-STEP"}
}"#;

/// The page and section snapshots [`record_all`] keeps for [`RECORDED`] (`dev/claims-pages.json`).
pub const RECORDED_PAGES: &str = r#"{"5a446aed967da80f": ["7d5a07ee41496c5d", "25080c5fca325e96", "9769715ae09a3066"], "d8de3199da52b188": ["920c9aa4904322d0", "3c34bf75e966571a"]}"#;

/// The kept page blob [`record_all`] writes into the common git directory: the fixture's question page, committed with it.
pub const RECORDED_BLOBS: &str =
    r#"{"d8de3199da52b188": "3b949ddad95e20557cee0f406ee7ff635fd4b75d"}"#;

/// The `.py` units of the counter-only fixture as [`record_all`] records them.
pub const RECORDED_COUNTED: &str = r#"{
"l7r/diagram/m.py::Table#table": {"body": "e96d8f4fd032f055", "claim": "table - NONE", "code": "50586ae6d9c5d118", "core": "core-Table", "note": "fine", "pages": {}, "research": "", "verdict": "IN-STEP"},
"l7r/diagram/m.py::helper#help": {"body": "e96d8f4fd032f055", "claim": "help - NONE", "code": "4f70c4705b3c917b", "core": "core-helper", "note": "fine", "pages": {}, "research": "", "verdict": "IN-STEP"},
"l7r/diagram/m.py::modl#modl": {"body": "e96d8f4fd032f055", "claim": "modl - NONE", "code": "6d19a47dcd6308a5", "core": "core-modl", "note": "fine", "pages": {}, "research": "", "verdict": "IN-STEP"},
"l7r/diagram/m.py::other#other": {"body": "e96d8f4fd032f055", "claim": "other - NONE", "code": "9a8f943e04158d92", "core": "core-other", "note": "fine", "pages": {}, "research": "", "verdict": "IN-STEP"}
}"#;

/// The claimed dictionary of the triage fixture as [`record_all`] records it, and its snapshot.
pub const RECORDED_TABLE: &str = r#"{
"l7r/diagram/m.py::TABLE#table": {"body": "34d7a27d1912a68e", "claim": "table - NONE", "code": "16998eb84d3840b7", "core": "core-1", "note": "fine", "pages": {}, "research": "", "section": "core-1", "verdict": "IN-STEP"}
}"#;
pub const RECORDED_TABLE_PAGES: &str = r#"{"core-1": ["968cd8edf2fc4a0d", "8ac8985e6424ff5d"]}"#;

/// The Python half's units of the counter-only fixture: four of `l7r/diagram/m.py`, each claimed `- NONE`.
pub fn counted_units(root: &Path) {
    py_units(
        root,
        &[],
        &[
            ("helper", "function", &["help - NONE"], false),
            ("other", "function", &["other - NONE"], false),
            ("Table", "constant", &["table - NONE"], false),
            ("modl", "module", &["modl - NONE"], false),
        ],
    );
}

/// The triage fixture's claimed dictionary, `TABLE` of two entries, and the Python half's unit of it.
pub fn claimed_table(root: &Path) {
    let table = serde_json::json!([{"path": "l7r/diagram/m.py", "qualname": "TABLE", "kind": "constant", "lineno": 1, "end_lineno": 1,
        "claims": [], "inherited": false, "core": "c", "errors": [], "names": [], "blocks": ["'a': 1", "'gone': 2"], "module_errors": []}]);
    put(root, "l7r/diagram/m.py", &table.to_string());
    put(root, "l7r/py-units.json", &serde_json::json!([[], [{"path": "l7r/diagram/m.py", "qualname": "TABLE", "kind": "constant", "lineno": 1,
        "end_lineno": 1, "claims": ["table - NONE"], "inherited": false, "core": "core-1", "errors": [], "names": [], "blocks": ["'a': 1",
        "'gone': 2"], "module_errors": []}]]).to_string());
}

/// What [`record_all`] leaves, written by hand: [`RECORDED`] and `units`, each dated today as the record dates them, and the
/// snapshots - [`RECORDED_PAGES`] and `pages` - and the kept blob.
pub fn write_recorded(root: &Path, units: &str, pages: &str) {
    let today = crate::record::bundle::today();
    let mut index: serde_json::Map<String, serde_json::Value> =
        serde_json::from_str(RECORDED).unwrap();
    index
        .extend(serde_json::from_str::<serde_json::Map<String, serde_json::Value>>(units).unwrap());
    for unit in index.values_mut() {
        unit["date"] = serde_json::json!(today);
    }
    let mut store: serde_json::Map<String, serde_json::Value> =
        serde_json::from_str(RECORDED_PAGES).unwrap();
    store
        .extend(serde_json::from_str::<serde_json::Map<String, serde_json::Value>>(pages).unwrap());
    put(
        root,
        "dev/claims-index.json",
        &serde_json::Value::Object(index).to_string(),
    );
    put(
        root,
        "dev/claims-pages.json",
        &serde_json::Value::Object(store).to_string(),
    );
    put(root, ".git/claims-page-blobs.json", RECORDED_BLOBS);
}

/// The three files [`write_recorded`] writes, as parsed values.
fn recorded_files(root: &Path) -> Vec<serde_json::Value> {
    [
        "dev/claims-index.json",
        "dev/claims-pages.json",
        ".git/claims-page-blobs.json",
    ]
    .iter()
    .map(|f| serde_json::from_str(&std::fs::read_to_string(root.join(f)).unwrap()).unwrap())
    .collect()
}

/// [`write_recorded`] writes what a run of [`record_all`] writes, here on the counter-only fixture and below on the triage one: the hand-written state is pinned to the
/// commands, so a change to what they record fails here rather than leaving the two tests on a stale state (feature 449 T167).
#[test]
fn the_recorded_state_is_what_record_all_writes() {
    let counted = fixture("claims-recorded-counted");
    counted_units(&counted);
    record_all(&counted);
    let by_hand = fixture("claims-recorded-counted-hand");
    write_recorded(&by_hand, RECORDED_COUNTED, "{}");
    assert_eq!(recorded_files(&counted), recorded_files(&by_hand));
}

/// [`the_recorded_state_is_what_record_all_writes`] on the triage fixture's claimed dictionary, a test of its own to keep each under
/// FR-008's tenth of a second (feature 449 T167).
#[test]
fn the_recorded_table_is_what_record_all_writes() {
    let table = fixture_with("claims-recorded-table", &claimed_table);
    record_all(&table);
    let by_hand = fixture("claims-recorded-table-hand");
    write_recorded(&by_hand, RECORDED_TABLE, RECORDED_TABLE_PAGES);
    assert_eq!(recorded_files(&table), recorded_files(&by_hand));
}

/// The same on the fixture with no Python module, the carry tests': [`RECORDED`] alone (feature 449 T167).
#[test]
fn the_recorded_rust_units_are_what_record_all_writes() {
    let rust = fixture_rust_only("claims-recorded-rust");
    record_all(&rust);
    let by_hand = fixture("claims-recorded-rust-hand");
    write_recorded(&by_hand, "{}", "{}");
    assert_eq!(recorded_files(&rust), recorded_files(&by_hand));
}
