//! The claims tools end to end on a scratch repository: each command through [`super::cli`], over the Rust units and the procedure
//! sections (the stub runner of the `.py` half left with the engine's Python, feature 449 T158).

use std::path::{Path, PathBuf};

use crate::record::testkit::{git, put};

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

/// A repository with the probe's Rust, procedures and questions, committed and set as origin/main; its root.
pub fn fixture(tag: &str) -> l7r_shared::tempdir::TempDir {
    fixture_with(tag, &|_| {})
}

/// [`fixture`], `more` writing its own files into the tree before the one commit (feature 449 T166: a commit fewer a test).
pub fn fixture_with(tag: &str, more: &dyn Fn(&Path)) -> l7r_shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    // the repository `git init -b main` makes, with its three settings, written as git writes them: four processes saved (feature 449
    // T166: each end-to-end test well within FR-008's tenth of a second)
    put(&root, ".git/HEAD", "ref: refs/heads/main\n");
    // `maintenance.auto` off: each commit started `git maintenance run --auto`, a process of 2 ms more (feature 449 T167)
    put(&root, ".git/config", "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n[user]\n\temail = t@example.org\n\tname = t\n[commit]\n\tgpgsign = false\n[maintenance]\n\tauto = false\n");
    for dir in ["objects", "refs/heads", "refs/tags"] {
        std::fs::create_dir_all(root.join(".git").join(dir)).unwrap();
    }
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
    more(&root);
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "base"]);
    // origin/main set as `git update-ref` sets it, the new branch's loose ref copied: a process saved (feature 449 T166)
    let head = std::fs::read_to_string(root.join(".git/refs/heads/main")).unwrap();
    put(&root, ".git/refs/remotes/origin/main", &head);
    root
}

/// Every change of the tree committed, and that commit made `origin/main` as the fixture makes it: the loose ref copied, where
/// `commit` and `git update-ref` took two processes more (feature 449 T167, as [`fixture_with`]).
pub fn commit_as_origin(root: &Path, msg: &str) {
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", msg, "--allow-empty"]);
    let head = std::fs::read_to_string(root.join(".git/refs/heads/main")).unwrap();
    put(root, ".git/refs/remotes/origin/main", &head);
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
    put(
        &root,
        "dev/claims-index.json",
        "{\"rust/phases/src/lib.rs::Thing.m#method guess\": {\"verdict\": \"IN-STEP\"}}\n",
    );
    let (rows, index) = super::rows_and_index(&root).unwrap();
    assert_eq!(
        rows["rust/phases/src/lib.rs::Thing.m#method guess"]["backing"],
        "GUESS"
    );
    assert_eq!(
        index["rust/phases/src/lib.rs::Thing.m#method guess"]["verdict"],
        "IN-STEP"
    );
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
    // a `.py` file under the map code is read no more (feature 449 T158): no Python starts, and its numbers are not counted
    put(&root, "l7r/diagram/tools/pack_audit/x.py", "4.5\n");
    let got = super::tunables_cli(&["--root".to_owned(), r, "--inline".to_owned()]);
    assert_eq!(got.code, 0);
    assert!(!got.stdout.contains("x.py"));
}

/// What `land.py` asked through `claims-door` until feature 449 T121, asked in process since: the land's scope split and live marks
/// (their tests moved here from the door's when feature 449 T132 deleted it; the replay's migration and owing left with `make
/// replay-owing`, feature 449 T247).
#[test]
fn the_land_asks_in_process() {
    let root = fixture("claims-in-process");
    assert_eq!(
        super::scope_split(
            &root,
            "  DRIFTED        rust/phases/src/lib.rs::GAP#x - y\n",
            &["rust/phases/src/lib.rs".to_owned()],
            &[]
        )
        .unwrap()
        .0,
        vec!["DRIFTED        rust/phases/src/lib.rs::GAP#x - y"]
    );
    assert_eq!(super::flight_live(&root), Ok(Vec::new()));
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

/// The kept blobs [`record_all`] writes into the common git directory: the fixture's question page, committed with it, and the Walls
/// section's words (feature 451 T210), [`RECORDED_SECTION`].
pub const RECORDED_BLOBS: &str = r#"{"d8de3199da52b188": "3b949ddad95e20557cee0f406ee7ff635fd4b75d", "section:5a446aed967da80f": "1a2fb38bc38f10a694c6a907725d5341582d9478"}"#;

/// The Walls section's words as [`record_all`] keeps them (feature 451 T210), written as the blob [`RECORDED_BLOBS`] names.
const RECORDED_SECTION: &str = r#"["Walls stand.", "- a list item continued", "| a | table |"]"#;

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
    assert!(super::stdin_git(root, &["hash-object", "-w", "--stdin"], RECORDED_SECTION).is_some());
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

/// [`write_recorded`] writes what a run of [`record_all`] writes: the hand-written state is pinned to the commands, so a change to what
/// they record fails here rather than leaving the tests that start from it on a stale state (feature 449 T167).
#[test]
fn the_recorded_rust_units_are_what_record_all_writes() {
    let rust = fixture("claims-recorded-rust");
    record_all(&rust);
    let by_hand = fixture("claims-recorded-rust-hand");
    write_recorded(&by_hand, "{}", "{}");
    assert_eq!(recorded_files(&rust), recorded_files(&by_hand));
}
