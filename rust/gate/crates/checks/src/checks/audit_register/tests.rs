//! The audit register's check (451 T259): red first on a delta that adds a guard without an entry, then each kind, the entry's form,
//! the list and the replay.

use std::path::Path;
use std::process::Command;

use super::super::tests::{commit, put, repo};
use super::{cli, delta, list, parse, problems, Outcome};

fn owned(args: &[&str]) -> Vec<String> {
    args.iter().map(|s| (*s).to_owned()).collect()
}

const MAKE: &str = "# the chain\n.PHONY: done\nX := 1\ninclude other.mk\n\ndone: export X := 1\ndone: static ## the gate\n\t$(MAKE) --no-print-directory _quick || exit 1\n_quick:\n\t@true\nstatic:\n\t@x\nother:\n\t@y\n";

const ENTRY: &str = "---\nkind: adopted\ntitle: the x guard\nfor: x\nmeasured: 2026-11-25\nmeasurement: m\ncommand: make x\nfalsifier: f\nthreshold: t\ncost: c\nlast-audited: 2026-11-25\ncadence-days: 30\ncovers: rust/guard/src/guards/new_hooks.rs\n---\nwhy\n";

/// A repository at its base: a Makefile, a guard, a constant, an agent.
fn base(tag: &str) -> l7r_shared::tempdir::TempDir {
    let dir = repo(tag);
    put(&dir, "Makefile", MAKE);
    put(
        &dir,
        "rust/guard/src/guards/old_hooks.rs",
        "pub const OLD_CAP: u64 = 3;\n",
    );
    put(&dir, ".claude/agents/a.md", "a\n");
    commit(&dir);
    dir
}

fn judged(dir: &Path) -> Outcome {
    delta(dir, None, &dir.join(".git/log"))
}

#[test]
fn a_guard_added_without_its_entry_is_refused_and_with_it_passes() {
    let dir = base("guard");
    put(&dir, "rust/guard/src/guards/new_hooks.rs", "//! new\n");
    let said = judged(&dir);
    assert_eq!(said.code, 1, "{said:?}");
    assert!(
        said.stderr
            .contains("guard module `rust/guard/src/guards/new_hooks.rs`"),
        "{}",
        said.stderr
    );
    assert!(
        said.stderr
            .contains("covers: rust/guard/src/guards/new_hooks.rs"),
        "{}",
        said.stderr
    );
    put(&dir, "dev/audits/x.md", ENTRY);
    let said = judged(&dir);
    assert_eq!(said.code, 0, "{said:?}");
    assert!(said.stdout.contains("1 mechanism"), "{}", said.stdout);
}

#[test]
fn a_renamed_guard_and_a_guards_own_part_add_nothing() {
    let dir = base("rename");
    let git = |args: &[&str]| {
        assert!(Command::new("git")
            .arg("-C")
            .arg(&*dir)
            .args(args)
            .status()
            .unwrap()
            .success());
    };
    git(&[
        "mv",
        "rust/guard/src/guards/old_hooks.rs",
        "rust/guard/src/guards/renamed_hooks.rs",
    ]);
    put(
        &dir,
        "rust/guard/src/guards/old_hooks/part.rs",
        "//! part\n",
    );
    assert_eq!(judged(&dir).code, 0, "{:?}", judged(&dir));
}

#[test]
fn a_new_constant_name_is_refused_a_moved_or_local_one_is_not() {
    let dir = base("consts");
    // moved to another file of the scope; a local and a string constant; a test file's
    put(
        &dir,
        "rust/guard/src/guards/old_hooks.rs",
        "fn f() {\n    const LOCAL_CAP: u64 = 1;\n}\nconst NAME: &str = \"x\";\n",
    );
    put(
        &dir,
        "rust/guard/src/split.rs",
        "pub(crate) const OLD_CAP: u64 = 3;\n",
    );
    put(
        &dir,
        "rust/guard/src/x/tests.rs",
        "const TEST_CAP: u64 = 9;\n",
    );
    put(
        &dir,
        "rust/mode_a/src/a.rs",
        "const ENGINE_MAX_FT: u64 = 9;\n",
    );
    assert_eq!(judged(&dir).code, 0, "{:?}", judged(&dir));
    put(
        &dir,
        "rust/gate/crates/checks/src/checks/y.rs",
        "pub(super) const NEW_LIMIT: f64 = 2.5;\n",
    );
    let said = judged(&dir);
    assert_eq!(said.code, 1);
    assert!(
        said.stderr.contains("numeric constant `NEW_LIMIT`"),
        "{}",
        said.stderr
    );
    assert!(
        !said.stderr.contains("OLD_CAP")
            && !said.stderr.contains("TEST_CAP")
            && !said.stderr.contains("ENGINE_MAX_FT"),
        "{}",
        said.stderr
    );
}

#[test]
fn a_target_wired_into_the_chain_is_refused_one_beside_it_is_not() {
    let dir = base("make");
    put(&dir, "Makefile", &format!("{MAKE}lonely:\n\t@z\n"));
    assert_eq!(judged(&dir).code, 0, "{:?}", judged(&dir));
    put(
        &dir,
        "Makefile",
        &MAKE.replace("\t@x\n", "\t@x\n\t$(MAKE) other\n"),
    );
    let said = judged(&dir);
    assert_eq!(said.code, 1);
    assert!(said.stderr.contains("`make other`"), "{}", said.stderr);
}

#[test]
fn an_agent_file_added_is_refused() {
    let dir = base("agent");
    put(&dir, ".claude/agents/new-check.md", "x\n");
    let said = judged(&dir);
    assert!(
        said.stderr
            .contains("agent file `.claude/agents/new-check.md`"),
        "{}",
        said.stderr
    );
}

#[test]
fn an_entry_must_be_whole_and_its_dates_and_cadence_read() {
    assert!(problems(&parse("e.md", ENTRY)).is_empty());
    let stub = parse("e.md", "---\ntitle: t\ncovers: X\n---\n");
    assert_eq!(problems(&stub).len(), 10, "{:?}", problems(&stub));
    assert_eq!(problems(&parse("e.md", "no front matter\n")).len(), 11);
    let bad = ENTRY
        .replace("measured: 2026-11-25", "measured: unmeasured")
        .replace("last-audited: 2026-11-25", "last-audited: soon")
        .replace("cadence-days: 30", "cadence-days: 0");
    let found = problems(&parse("e.md", &bad));
    assert_eq!(found.len(), 3, "{found:?}");
    assert!(found[0].contains("first-audit"));
    let wrong = ENTRY.replace("measured: 2026-11-25", "measured: 2026-13-01");
    assert!(problems(&parse("e.md", &wrong))[0].contains("YYYY-MM-DD"));
    // a malformed entry refuses the delta even with nothing added
    let dir = base("stub");
    put(&dir, "dev/audits/stub.md", "---\ntitle: t\n---\n");
    let said = judged(&dir);
    assert_eq!(said.code, 1);
    assert!(
        said.stderr
            .contains("dev/audits/stub.md: `for:` is missing"),
        "{}",
        said.stderr
    );
}

#[test]
fn the_escape_passes_with_a_reason_and_is_recorded() {
    let dir = base("escape");
    put(&dir, ".claude/agents/new-check.md", "x\n");
    let log = dir.join("log");
    let said = delta(&dir, Some("a fixture agent, not a mechanism"), &log);
    assert_eq!(said.code, 0);
    assert!(said.stdout.contains("ESCAPED"), "{}", said.stdout);
    let short = delta(&dir, Some("x"), &log);
    assert_eq!(short.code, 1);
    assert!(short.stderr.contains("needs a reason"), "{}", short.stderr);
    let mut text = String::new();
    for e in std::fs::read_dir(&log).unwrap().map_while(Result::ok) {
        text.push_str(&std::fs::read_to_string(e.path()).unwrap_or_default());
    }
    assert!(text.contains("escaped") && text.contains("blocked"));
}

#[test]
fn the_list_puts_the_overdue_first() {
    let late = parse(
        "dev/audits/late.md",
        &ENTRY
            .replace("the x guard", "late one")
            .replace("last-audited: 2026-11-25", "last-audited: 2026-10-01"),
    );
    let soon = parse("dev/audits/soon.md", ENTRY);
    let never = parse(
        "dev/audits/never.md",
        &ENTRY
            .replace("the x guard", "never one")
            .replace("last-audited: 2026-11-25", "last-audited: never"),
    );
    let bad = parse("dev/audits/bad.md", "---\ntitle: bad one\n---\n");
    let out = list(&[soon, late, never, bad], "2026-11-26", &[]);
    let at = |s: &str| out.find(s).expect("listed");
    assert!(out.starts_with("audits: 4 entries in dev/audits/, 3 overdue (today 2026-11-26)"));
    assert!(at("NEVER AUDITED  [adopted] never one") < at("OVERDUE by 26 d  [adopted] late one"));
    assert!(at("late one") < at("due in 29 d  [adopted] the x guard"));
    assert!(out.contains("falsifier: f") && out.contains("MALFORMED"));
}

#[test]
fn the_command_line_and_the_replay() {
    let dir = base("cli");
    let root = dir.display().to_string();
    assert_eq!(cli(&owned(&["--selftest"]), &dir).code, 0);
    assert_eq!(cli(&owned(&["--delta"]), &dir).code, 2);
    assert_eq!(cli(&owned(&["--range", "HEAD"]), &dir).code, 2);
    assert_eq!(cli(&owned(&[]), &dir).code, 2);
    put(&dir, "dev/audits/x.md", ENTRY);
    put(&dir, "rust/guard/src/guards/new_hooks.rs", "//! new\n");
    commit(&dir);
    let listed = cli(
        &owned(&["--list", "--root", &root, "--today", "2026-11-26"]),
        Path::new("/"),
    );
    assert!(listed.stdout.contains("the x guard"), "{listed:?}");
    assert!(
        listed.stdout.contains("BACKFILL")
            && listed
                .stdout
                .contains("guard module: rust/guard/src/guards/old_hooks.rs")
    );
    assert!(cli(&owned(&["--list", "--root", &root]), &dir)
        .stdout
        .starts_with("audits: 1 entries"));
    let replay = cli(
        &owned(&["--range", "HEAD~1", "HEAD", "--root", &root]),
        Path::new("/"),
    );
    assert_eq!(replay.code, 0, "{replay:?}");
    assert!(
        replay
            .stdout
            .contains("guard module: rust/guard/src/guards/new_hooks.rs"),
        "{}",
        replay.stdout
    );
    let raw = cli(
        &owned(&[
            "--range",
            "HEAD~1",
            "HEAD",
            "--root",
            &root,
            "--empty-register",
        ]),
        Path::new("/"),
    );
    assert_eq!(raw.code, 1, "{raw:?}");
    // the delta's form through the command line: committed, nothing past the base (no origin/main: the base is HEAD)
    assert_eq!(cli(&owned(&["--delta", &root]), &dir).code, 0);
}

#[test]
fn a_threshold_is_read_by_its_names_words_a_unit_or_a_display_size_is_not() {
    for name in [
        "CAP_TOKENS",
        "POLL_CHECK_S",
        "STATIC_RUNS_A_TASK",
        "SNAPSHOT_DAYS",
        "FREE_PCT",
        "PLAN_ROUND_CAP",
    ] {
        assert!(super::detect::is_threshold(name), "{name}");
    }
    for name in [
        "GB",
        "DAY_MICROS",
        "SECONDS_A_DAY",
        "LARGEST",
        "SHOWN",
        "SIGTERM",
    ] {
        assert!(!super::detect::is_threshold(name), "{name}");
    }
    assert_eq!(super::detect::const_name("const LARGEST: usize = 4;"), None);
}

#[test]
fn the_base_is_origin_mains_and_an_empty_scope_holds_no_constant() {
    let dir = repo("origin");
    put(&dir, "Makefile", MAKE);
    put(
        &dir,
        "dev/audits/x.md",
        "---\ntitle: t\nno colon here\ncovers:\n---\n",
    );
    commit(&dir);
    let at = Command::new("git")
        .arg("-C")
        .arg(&*dir)
        .args(["rev-parse", "HEAD"])
        .output()
        .unwrap();
    let head = String::from_utf8_lossy(&at.stdout).trim().to_owned();
    assert!(Command::new("git")
        .arg("-C")
        .arg(&*dir)
        .args(["update-ref", "refs/remotes/origin/main", &head])
        .status()
        .unwrap()
        .success());
    assert_eq!(super::base(&dir), head);
    put(&dir, "rust/guard/src/guards/new_hooks.rs", "//! new\n");
    let said = judged(&dir);
    assert!(said.stderr.contains("dev/audits/x.md: `for:` is missing"));
    assert!(said.stderr.contains("new_hooks.rs"));
}

#[test]
fn a_landing_step_newly_named_is_refused() {
    let dir = base("steps");
    put(
        &dir,
        "rust/gate/crates/cohort/src/push.rs",
        "// the table\n    Row(\"old\", Tool::Gate),\n",
    );
    put(
        &dir,
        "rust/gate/crates/land/src/land/cheap.rs",
        "const GATES: [&str; 1] = [\"a-gate.sh\"];\n",
    );
    commit(&dir);
    assert_eq!(judged(&dir).code, 0);
    put(
        &dir,
        "rust/gate/crates/cohort/src/push.rs",
        "    Row(\"old\", Tool::Gate),\n    Row(\"new-row\", Tool::Gate),\n",
    );
    put(
        &dir,
        "rust/gate/crates/land/src/land.rs",
        "        self.phase(\"after\", || {\n",
    );
    put(
        &dir,
        "rust/gate/crates/land/src/land/cheap.rs",
        "const GATES: [&str; 2] = [\"a-gate.sh\", \"b-gate.sh\"];\n",
    );
    let said = judged(&dir);
    for name in [
        "push check new-row",
        "landing phase after",
        "landing gate b-gate.sh",
    ] {
        assert!(said.stderr.contains(&format!("`{name}`")), "{name}");
    }
    assert!(!said.stderr.contains("push check old"));
}

#[test]
fn a_landing_refusal_added_is_refused_by_its_number() {
    let dir = base("refusals");
    let cheap = "rust/gate/crates/land/src/land/cheap.rs";
    put(&dir, cheap, "stops.push(a);\n");
    commit(&dir);
    assert_eq!(judged(&dir).code, 0);
    put(&dir, cheap, "stops.push(a);\nstops.push(b);\n");
    let said = judged(&dir);
    assert_eq!(said.code, 1);
    assert!(
        said.stderr.contains("`landing refusal land/cheap.rs #2`"),
        "{}",
        said.stderr
    );
    assert!(!said.stderr.contains("#1"), "{}", said.stderr);
    assert!(super::detect::refusal_items("stops.push(a);", "").is_empty());
}

/// T258's case (451 T269): `make land`'s rule as it stood, to which T258 added one recipe line calling a script no entry names.
const LAND: &str = "LAND_RUN = \"$$(git rev-parse --show-toplevel)/scripts/gates/l7r-gate.sh\" land\nland: export LAND_NOTE = $(NOTE)\nland:           ## [project] land one task\n\t@$(LAND_RUN) \"$(F)\" \"$(T)\"; rc=$$?; \\\n";
const LAND_END: &str = "\t  $(SCRATCH_TREES); exit $$rc\n";
const T258: &str = "\t  if [ $$rc = 0 ] || [ $$rc = 3 ]; then \"$$(git rev-parse --show-toplevel)/scripts/state-sync.sh\" push --detach || :; fi; \\\n";

#[test]
fn a_script_newly_called_from_make_lands_recipe_is_refused_until_an_entry_covers_it() {
    let dir = base("callee");
    put(&dir, "Makefile", &format!("{MAKE}{LAND}{LAND_END}"));
    commit(&dir);
    assert_eq!(judged(&dir).code, 0);
    put(&dir, "Makefile", &format!("{MAKE}{LAND}{T258}{LAND_END}"));
    let said = judged(&dir);
    assert_eq!(said.code, 1, "{said:?}");
    assert!(
        said.stderr
            .contains("adds a landing script `landing script scripts/state-sync.sh`"),
        "{}",
        said.stderr
    );
    assert!(
        said.stderr
            .contains("covers: landing script scripts/state-sync.sh"),
        "{}",
        said.stderr
    );
    assert!(!said.stderr.contains("l7r-gate.sh"), "{}", said.stderr);
    put(
        &dir,
        "dev/audits/x.md",
        &ENTRY.replace(
            "rust/guard/src/guards/new_hooks.rs",
            "landing script scripts/state-sync.sh",
        ),
    );
    assert_eq!(judged(&dir).code, 0);
}

#[test]
fn a_landing_script_is_read_through_a_variable_and_the_push_scripts_by_name_over_them_all() {
    let dir = base("callee-forms");
    // another target's roster names a script no landing calls, and no landing recipe expands UNUSED
    let other =
        "roster:\n\t@for h in scripts/roster-only.sh; do :; done\n\nUNUSED := scripts/unused.sh\n";
    put(
        &dir,
        "Makefile",
        &format!("{MAKE}{LAND}{LAND_END}{other}land-tooling:\n\t@scripts/moved.sh\n"),
    );
    put(
        &dir,
        "scripts/land-tooling.sh",
        "# calls scripts/commented.sh\n",
    );
    commit(&dir);
    assert_eq!(judged(&dir).code, 0);
    // a call moved from a recipe into the push's script adds nothing; a variable's value held over two lines, a variable that one
    // expands, a recipe after a blank line and the push scripts' own lines are each read; a recipe after a comment, a glob, a
    // directory, a path with a variable in it and a comment name no script
    let vars = "SCRATCH_TREES = \"$$root/scripts/sweep.sh\" \\\n  $(DEEP) $(DEEP) $(NONE)\nDEEP ?= scripts/deep.sh.\n";
    put(
        &dir,
        "Makefile",
        &format!("{MAKE}{LAND}{LAND_END}{other}{vars}land-tooling:\n\n\t@scripts/land-tooling.sh\n# after\n\t@scripts/after-a-comment.sh\n"),
    );
    put(
        &dir,
        "scripts/land-tooling.sh",
        "# calls scripts/commented.sh\nscripts/moved.sh\ncase x in scripts/*|scripts/gates/) \"$ROOT/scripts/gates/$g.sh\";; esac\n",
    );
    put(
        &dir,
        "scripts/sync-with-main.sh",
        "\"$ROOT/scripts/hooks/new-push.sh\" --go\n",
    );
    let said = judged(&dir);
    assert_eq!(said.code, 1, "{said:?}");
    let named: Vec<&str> = said
        .stderr
        .lines()
        .filter_map(|l| l.strip_prefix("covers: landing script "))
        .collect();
    let want = "scripts/deep.sh scripts/hooks/new-push.sh scripts/land-tooling.sh scripts/sweep.sh";
    assert_eq!(named.join(" "), want, "{}", said.stderr);
}

#[test]
fn a_tooling_crates_threshold_is_read() {
    let dir = base("tooling-const");
    put(
        &dir,
        "rust/gate/crates/pages/src/x.rs",
        "const BUNDLE_TOKENS: usize = 9;\n",
    );
    assert!(judged(&dir).stderr.contains("`BUNDLE_TOKENS`"));
}

#[test]
fn a_duration_threshold_in_the_landing_crates_is_read() {
    assert_eq!(
        super::detect::const_name("const CLAIMS_WAIT: Duration = Duration::from_secs(5);"),
        Some("CLAIMS_WAIT")
    );
    let dir = base("land-const");
    put(
        &dir,
        "rust/gate/crates/land/src/land/x.rs",
        "pub(super) const COMMIT_TRIES: u32 = 3;\n",
    );
    assert!(judged(&dir).stderr.contains("`COMMIT_TRIES`"));
}

#[test]
fn a_declined_option_is_an_entry_and_a_third_kind_is_malformed() {
    let declined = parse(
        "dev/audits/no.md",
        &ENTRY.replace("kind: adopted", "kind: declined"),
    );
    assert!(problems(&declined).is_empty());
    assert!(list(&[declined], "2026-11-26", &[]).contains("[declined] the x guard"));
    let odd = problems(&parse(
        "e.md",
        &ENTRY.replace("kind: adopted", "kind: maybe"),
    ));
    assert_eq!(odd.len(), 1);
    assert!(odd[0].contains("`kind:` is `adopted`"));
}
