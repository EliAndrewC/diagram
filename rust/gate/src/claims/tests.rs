//! The claims tools end to end on a scratch repository: each command through [`super::cli`], the Python half a stub runner answering
//! from files the test writes (`py-units.json` beside the engine), as the real runner answers from the `.py` files.

use std::path::{Path, PathBuf};

use crate::record::testkit::{commit, git, put};

pub(crate) const RUNNER: &str = r#"import json, pathlib, sys
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
        elif v == "gm_review_add_row":
            with open(pathlib.Path(x[0], "gm-review.jsonl"), "a") as fh:
                fh.write(json.dumps(x[1]) + "\n")
            ok = True
        else:
            raise KeyError(v)
        print(json.dumps({"ok": ok}), flush=True)
    except Exception as e:
        print(json.dumps({"error": "Traceback (most recent call last):\n" + type(e).__name__ + ": " + str(e)}), flush=True)
"#;

const APPLY_EDITS: &str = "def reply_of(path):\n    return path.read_text()\n";
const CODEID: &str = "import hashlib, re, sys\nfor p in sys.argv[2:]:\n    print(hashlib.sha256(re.sub(rb' *#.*', b'', open(p, 'rb').read())).hexdigest())\n";

pub(crate) const LIB: &str = "//! The probe.
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

pub(crate) const PAGE: &str = "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A second block.</p>\n";
pub(crate) const BUILDINGS: &str = "# Buildings\n\n## Walls\n<!-- Research: walls - CONVENTION -->\n<!-- Research: wall height - research/questions/0001-gap.html: 12 ft -->\n\nWalls stand.\n\n- a list item\n  continued\n| a | table |\n|---|---|\n\n### Deep\n\nNo claim here.\n\n##### Too deep\n";

/// A repository with the probe's Rust, procedures, questions and Python half, committed and set as origin/main; its root.
pub(crate) fn fixture(tag: &str) -> PathBuf {
    let root = crate::checks::scratch(tag);
    git(&root, &["init", "-q", "-b", "main"]);
    git(&root, &["config", "user.email", "t@example.org"]);
    git(&root, &["config", "user.name", "t"]);
    git(&root, &["config", "commit.gpgsign", "false"]);
    put(&root, "scripts/bundle_door.py", RUNNER);
    put(&root, "scripts/record/apply_edits.py", APPLY_EDITS);
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
    commit(&root, "base");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    root
}

/// The Python half's answer: units of `l7r/diagram/m.py`, each `(qualname, kind, claim lines, inherited)`.
pub(crate) fn py_units(
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
pub(crate) fn claims(root: &Path, args: &[&str]) -> crate::Reply {
    let mut all = vec!["--root".to_owned(), root.to_string_lossy().into_owned()];
    all.extend(args.iter().map(|a| (*a).to_owned()));
    super::cli(&all)
}

/// Every claim of the fixture recorded IN-STEP through a bundle and its reply; the bundle's directory.
pub(crate) fn record_all(root: &Path) -> PathBuf {
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
    assert_eq!(super::read_paths().len(), 8);
}

#[test]
fn a_failure_is_the_traceback_with_its_exit() {
    let root = fixture("claims-fail");
    put(&root, "dev/claims-index.json", "[not json");
    let got = claims(&root, &["owed"]);
    assert_eq!(got.code, 1);
    assert!(
        got.stderr.starts_with("Traceback (most recent call last):"),
        "{}",
        got.stderr
    );
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
