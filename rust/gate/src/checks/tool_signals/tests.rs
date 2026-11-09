//! No tool lands recording none of its runs; `tests/hooks/test-check-tool-signals.sh` is the end-to-end suite.

use std::path::Path;

use super::{cli, reached, recipe};
use crate::checks::scratch;

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn clean() -> std::path::PathBuf {
    let r = scratch("signals");
    put(&r, ".claude/settings.json", "{\"hooks\":{\"PreToolUse\":[{\"hooks\":[{\"command\":\"scripts/hooks/foo-hooks.sh pretool\"}]}]}}\n");
    put(&r, "Makefile", "done: lint\nlint:\n\t@python3 scripts/tools/lint.py\nquick:\n\t@true\ntick:\n\t@$(MAKE) sub\nsub:\n\t@true\n");
    put(
        &r,
        "scripts/hooks/foo-hooks.sh",
        "guard_log foo blocked x\n",
    );
    put(
        &r,
        "scripts/gates/gatey.py",
        "import usage_log\nif __name__ == \"__main__\":\n    usage_log.exited(\"gatey\", 0)\n",
    );
    put(&r, "scripts/gates/plain.txt", "not a check\n");
    put(&r, "scripts/tools/lint.py", "# TOOL_RECORD: its run\n");
    put(
        &r,
        "scripts/tool-registry.json",
        "{\"tools\":{\"gatey\":{\"kind\":\"check\",\"what\":\"x\"}}}\n",
    );
    r
}

fn ask(root: &Path) -> super::Outcome {
    cli(&[], root)
}

#[test]
fn a_clean_repository_passes_and_a_silent_tool_is_named_with_its_fix() {
    let r = clean();
    assert_eq!(ask(&r).code, 0);
    put(&r, "scripts/hooks/foo-hooks.sh", "exit 0\n");
    let got = ask(&r);
    assert!(
        got.code == 1
            && got
                .stderr
                .contains("scripts/hooks/foo-hooks.sh: records none of its runs")
            && got.stderr.contains("TOOL_RECORD")
    );
    let r = clean();
    put(&r, "scripts/tools/lint.py", "print(1)\n");
    assert!(ask(&r)
        .stderr
        .contains("scripts/tools/lint.py: records none"));
    let r = clean();
    put(&r, "scripts/tools/other.py", "print(1)\n");
    assert_eq!(ask(&r).code, 0);
}

#[test]
fn a_call_the_registry_lacks_and_an_entry_nothing_records_are_refused() {
    let r = clean();
    put(
        &r,
        "scripts/tools/step.py",
        "import usage_log\nusage_log.record(root, \"stray\", \"step\", \"changed\")\n",
    );
    assert!(ask(&r)
        .stderr
        .contains("records `stray`, which scripts/tool-registry.json lacks"));
    let r = clean();
    put(
        &r,
        "rust/gate/src/x.rs",
        "const USAGE_LOG_TOOL: &str = \"compiled\";\n",
    );
    assert!(ask(&r).stderr.contains("records `compiled`"));
    let r = clean();
    put(
        &r,
        "scripts/tool-registry.json",
        "{\"tools\":{\"gatey\":{},\"ghost\":{}}}\n",
    );
    assert!(ask(&r)
        .stderr
        .contains("`ghost` is registered but no code records it"));
    let elsewhere = clean();
    let arg = vec!["--root".to_owned(), elsewhere.display().to_string()];
    assert_eq!(cli(&arg, Path::new("/nonexistent")).code, 0);
}

#[test]
fn a_recipe_and_what_the_entry_targets_reach() {
    let make = "done: lint # note\n\t@true\nlint:\n\t@$(MAKE) --no-print-directory sub; x\nsub:\n\t@true\n";
    assert_eq!(
        recipe(make, "lint"),
        "lint:\n\t@$(MAKE) --no-print-directory sub; x\n"
    );
    assert_eq!(recipe(make, "nope"), "");
    let seen = reached(make);
    assert!(seen.contains("lint") && seen.contains("sub") && seen.contains("quick"));
}
