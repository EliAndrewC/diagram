//! The decider over a real checkout (`tests/hooks/test-phase-source-hooks.sh`, replayed through the shim, is the verdict).

use serde_json::{json, Value};

use super::{any_match, decide, judge, parent_of, stamp};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::ask;

const OLD: &str = "l7r/diagram/old/stage.py";

/// A checkout holding phase task T9's old module, its box open.
fn world(tag: &str, allow: &Value) -> crate::shared::tempdir::Held<String> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-phase-{tag}"));
    std::fs::create_dir_all(d.join("l7r/diagram/old")).unwrap();
    std::fs::create_dir_all(d.join("l7r/diagram/new")).unwrap();
    std::fs::create_dir_all(d.join("specs/444-x")).unwrap();
    let at = d.canonicalize().unwrap().to_string_lossy().into_owned();
    assert!(ask(std::path::Path::new("/"), "git", &["init", "-q", &at], "").ok());
    std::fs::write(format!("{at}/{OLD}"), "x\n").unwrap();
    std::fs::write(format!("{at}/l7r/diagram/new/fresh.py"), "x\n").unwrap();
    std::fs::write(
        format!("{at}/specs/444-x/tasks.md"),
        "- [ ] T9 rebuild\n- [x] T90 other\n",
    )
    .unwrap();
    let state =
        json!({"feature": "444-x", "task": "T9", "phase": "water", "files": [OLD], "allow": allow});
    std::fs::write(format!("{at}/.git/phase-sources.json"), state.to_string()).unwrap();
    let held = at;
    d.hold(held)
}

fn run(tool: &str, input: &Value, at: &str) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "cwd": at, "tool_input": input}),
    };
    judge(
        &e,
        &Session::from_input(&e.input),
        at,
        &format!("{at}/.git/phase-sources.json"),
        "2026-11-08T00:00:00Z",
    )
}

fn bash(cmd: &str, at: &str) -> Vec<Answer> {
    run("Bash", &json!({"command": cmd}), at)
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(t)] if t.contains(words))
}

#[test]
fn a_read_of_a_held_file_is_refused_and_says_where_to_write_from() {
    let at = world("read", &json!([]));
    let got = run("Read", &json!({"file_path": format!("{at}/{OLD}")}), &at);
    assert!(refused(&got, "is the old code of `water`"));
    assert!(refused(
        &run("Read", &json!({"file_path": OLD}), &at),
        "old code"
    ));
    assert!(run("Read", &json!({"file_path": "other.py"}), &at).is_empty());
    assert!(refused(
        &run("Grep", &json!({"path": "l7r/diagram/old"}), &at),
        "old code"
    ));
    assert!(refused(
        &run("Glob", &json!({"path": OLD}), &at),
        "old code"
    ));
    assert!(run("Grep", &json!({"path": "l7r/diagram/new"}), &at).is_empty());
    assert!(run("Read", &json!({"file_path": "/outside/x"}), &at).is_empty());
}

#[test]
fn a_shell_read_is_refused_and_a_mention_is_not() {
    let at = world("shell", &json!([]));
    assert!(refused(&bash(&format!("cat {OLD}"), &at), "old code"));
    assert!(refused(
        &bash("grep -n x l7r/diagram/old/", &at),
        "old code"
    ));
    assert!(refused(
        &bash(&format!("git show HEAD:{OLD}"), &at),
        "old code"
    ));
    assert!(bash(&format!("git rm {OLD}"), &at).is_empty());
    assert!(bash(&format!("make test-file FILE={OLD}"), &at).is_empty());
    assert!(bash("cat other.py", &at).is_empty());
}

#[test]
fn an_allowance_and_a_closed_task_release_the_file() {
    let at = world(
        "allow",
        &json!([{"file": OLD, "until": "2026-11-08T00:10:00Z"}, {"file": "z", "until": "2030"}]),
    );
    assert!(run("Read", &json!({"file_path": OLD}), &at).is_empty());
    let late = world(
        "late",
        &json!([{"file": OLD, "until": "2026-01-01T00:00:00Z"}]),
    );
    assert!(refused(
        &run("Read", &json!({"file_path": OLD}), &late),
        "old code"
    ));
    let closed = world("closed", &json!([]));
    std::fs::write(
        format!("{closed}/specs/444-x/tasks.md"),
        "- [x] T9 rebuild\n- [ ] T90 other\n",
    )
    .unwrap();
    assert!(run("Read", &json!({"file_path": OLD}), &closed).is_empty());
    std::fs::remove_file(format!("{closed}/specs/444-x/tasks.md")).unwrap();
    assert!(run("Read", &json!({"file_path": OLD}), &closed).is_empty());
}

#[test]
fn the_escape_needs_a_reason() {
    let at = world("escape", &json!([]));
    assert!(bash(
        &format!("cat {OLD}  # PHASE_SOURCE_OK: replacing its thin wrapper"),
        &at
    )
    .is_empty());
    assert!(refused(
        &bash(&format!("cat {OLD}  # PHASE_SOURCE_OK"), &at),
        "with no reason"
    ));
}

#[test]
fn nothing_held_or_nowhere_to_look_passes() {
    let at = world("none", &json!([]));
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Read", "tool_input": {"file_path": OLD}}),
    };
    let s = Session::from_input(&e.input);
    assert!(judge(&e, &s, &at, "/no/such/file", "now").is_empty());
    assert!(judge(
        &e,
        &s,
        "/tmp",
        &format!("{at}/.git/phase-sources.json"),
        "now"
    )
    .is_empty());
    std::fs::write(format!("{at}/.git/phase-sources.json"), "{").unwrap();
    assert!(run("Read", &json!({"file_path": OLD}), &at).is_empty());
    let nokey = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Read", "cwd": at}),
    };
    assert!(judge(
        &nokey,
        &Session::from_input(&nokey.input),
        &at,
        &format!("{at}/.git/phase-sources.json"),
        "now"
    )
    .is_empty());
    assert!(
        any_match(&format!("/no/such {at}/.git/HEAD"))
            && any_match(&format!("{at}/*/HEAD"))
            && !any_match(&format!("{at}/*/nothing"))
            && !any_match("/no/such/*/x")
    );
    assert_eq!((parent_of("a/b.py"), parent_of("b.py")), ("a", "."));
    assert_eq!(stamp().len(), 20);
    // The default glob names this host's checkouts, so what it answers is the host's; the seam's cases above are the verdict.
    let _host_answer = decide(&e, &s);
}

/// The state's `derivation` set to `path` (`make task-start` records it from the block's `derivation:` line, T204).
fn with_derivation(at: &str, path: &str) {
    let state = json!({"feature": "444-x", "task": "T9", "phase": "water", "derivation": path, "files": [OLD], "allow": []});
    std::fs::write(format!("{at}/.git/phase-sources.json"), state.to_string()).unwrap();
}

/// The compliant form a search refusal names (the text after `Search without them:`, up to the line's end).
fn fix_of(got: &[Answer]) -> String {
    let [Answer::Refuse(text)] = got else {
        return String::new();
    };
    let line = text
        .lines()
        .find_map(|l| l.strip_prefix("Search without them:  "));
    line.unwrap_or_default().to_owned()
}

#[test]
fn a_search_over_a_parent_of_the_held_code_is_refused_unless_it_leaves_it_out() {
    // T204: during T202 `grep -rn X rust/mode_a/src` printed lines of the held labels/placer.rs - the guard looked for the held
    // file or its directory, never a recursive search of a parent
    let at = world("search", &json!([]));
    for input in [
        json!({"pattern": "x", "path": "l7r"}),
        json!({"pattern": "x"}),
        json!({"pattern": "x", "path": format!("{at}/l7r/diagram"), "output_mode": "content"}),
        json!({"pattern": "x", "path": "l7r", "glob": "!**/new/*"}),
        json!({"pattern": "x", "path": "l7r", "type": "nosuchtype"}),
    ] {
        let got = run("Grep", &input, &at);
        assert!(refused(&got, "Search without them"), "{input}");
    }
    for input in [
        json!({"pattern": "x", "path": "l7r", "glob": "!**/old/stage.py"}),
        json!({"pattern": "x", "path": "l7r", "glob": "!old"}),
        json!({"pattern": "x", "path": "l7r", "glob": "*.md"}),
        json!({"pattern": "x", "path": "l7r", "type": "rust"}),
        json!({"pattern": "x", "path": "l7r/diagram/new"}),
    ] {
        assert!(run("Grep", &input, &at).is_empty(), "{input}");
    }
    for cmd in [
        "grep -rn x l7r".to_owned(),
        "grep -rnE \"a|b\" l7r/diagram".to_owned(),
        "cd l7r && grep -rn x .".to_owned(),
        "grep -rn x".to_owned(),
        "grep -r -e x l7r/diagram/old/stage.py".to_owned(),
        "egrep -R x ./l7r/ 2>/dev/null | head".to_owned(),
        format!("grep -rn x {at}/l7r"),
        "grep -n x l7r/diagram/*/stage.py".to_owned(),
        "grep -rn x l7r/*".to_owned(),
        "grep -rn x l7r --exclude-dir=new".to_owned(),
        "grep -rn x l7r --include='*.py'".to_owned(),
        "rg x".to_owned(),
        "rg -n x l7r/".to_owned(),
        "rg x l7r -g '!old/stage.py'".to_owned(),
        "rg x l7r -g '!stage.py' -g '*.py'".to_owned(),
        "rg x l7r/diagram/old/stage.py -g '!stage.py'".to_owned(),
        "rg x -t md -t py".to_owned(),
        "ag x l7r".to_owned(),
        "ag x l7r --ignore '**/stage.py'".to_owned(),
        "git grep -n x".to_owned(),
        "git grep x -- l7r".to_owned(),
        "git -C l7r grep x".to_owned(),
        "git grep x -- l7r ':!l7r/diagram/new'".to_owned(),
        "find l7r -name '*.py' -exec grep -n x {} +".to_owned(),
        "find l7r -not -path '*/new/*' -exec grep -n x {} \\;".to_owned(),
        "find l7r -name '*.py' -o -name '*.md' -exec grep x {} +".to_owned(),
        "find l7r -type f | xargs grep -n x".to_owned(),
        "find l7r -type f -print0 | xargs -0 -n 4 egrep -n x".to_owned(),
    ] {
        let got = bash(&cmd, &at);
        assert!(refused(&got, "Search without them"), "{cmd}: {got:?}");
    }
    for cmd in [
        "grep -rn x l7r --exclude=stage.py",
        "grep -rn x l7r --exclude-dir=old",
        "grep -rn x l7r --include='*.md'",
        "grep -n x l7r/diagram/old/stage.py --exclude=stage.py",
        "grep -rn x l7r/diagram/new",
        "grep x l7r",
        "ls l7r | grep x",
        "grep -rn x l7r --include=stage.py --exclude=stage.py",
        "rg x l7r -g '!**/old/stage.py'",
        "rg x l7r -g '!old'",
        "rg x l7r -g '*.py' -g '!stage.py'",
        "rg x l7r -g 'l7r/diagram/new/**'",
        "rg x -t rust",
        "rg x l7r -T py",
        "rg --files l7r",
        "cat list | rg x",
        "ag x l7r --ignore stage.py",
        "ag x l7r --ignore old/stage.py",
        "ag x l7r -G 'new/'",
        "ag -g stage l7r",
        "git grep x -- l7r ':!l7r/diagram/old'",
        "git grep x ':(top,exclude)l7r/diagram/old/stage.py'",
        "git grep x ':/l7r/diagram/new'",
        "find l7r -not -path '*/old/*' -exec grep x {} +",
        "find l7r ! -name stage.py -exec grep x {} +",
        "find l7r -path '*/old' -prune -o -name '*.py' -exec grep x {} +",
        "find l7r -name '*.md' -exec grep x {} +",
        "find l7r -exec grep --exclude=stage.py x {} +",
        "find l7r -type f",
        "find l7r -not -path '*/old/*' | xargs grep x",
        "echo l7r | xargs grep x",
    ] {
        assert!(bash(cmd, &at).is_empty(), "{cmd}: {:?}", bash(cmd, &at));
    }
    // an allowance lets its file be searched too
    let open = world(
        "search-allow",
        &json!([{"file": OLD, "until": "2026-11-08T00:10:00Z"}]),
    );
    assert!(bash("grep -rn x l7r", &open).is_empty());
}

#[test]
fn the_form_a_search_refusal_names_passes() {
    let at = world("search-fix", &json!([]));
    let grep_tool = run("Grep", &json!({"pattern": "x", "path": "l7r"}), &at);
    let glob = fix_of(&grep_tool);
    let value = glob
        .strip_prefix("glob: \"")
        .and_then(|g| g.strip_suffix('"'));
    let value = value.unwrap_or_default();
    assert!(run(
        "Grep",
        &json!({"pattern": "x", "path": "l7r", "glob": value}),
        &at
    )
    .is_empty());
    for cmd in [
        "grep -rn x l7r",
        "rg -n x l7r",
        "ag x l7r",
        "git grep -n x -- l7r",
        "git grep -n x",
    ] {
        let fix = fix_of(&bash(cmd, &at));
        let fixed = format!("{cmd} {fix}");
        assert!(bash(&fixed, &at).is_empty(), "{fixed}");
    }
    let fix = fix_of(&bash("find l7r -name '*.py' -exec grep -n x {} +", &at));
    let fixed = format!("find l7r {fix} -name '*.py' -exec grep -n x {{}} +");
    assert!(bash(&fixed, &at).is_empty(), "{fixed}");
    let refusal = bash("grep -rn x l7r", &at);
    assert!(
        refused(&refusal, "l7r/diagram/old/stage.py") && refused(&refusal, "--exclude=stage.py")
    );
}

#[test]
fn the_prescribed_command_and_a_listing_are_not_reads() {
    // T204: T202's deletion step was refused the `make phase-read` the refusal prescribes, piped into tail, and a `git diff --stat`
    let at = world("listing", &json!([]));
    for cmd in [
        format!("make phase-read FILE={OLD} WHY=\"to grep its callers\""),
        format!("make phase-read FILE={OLD} WHY=\"the thin wrapper\" 2>&1 | tail -3"),
        "git diff --stat l7r/diagram/old/".to_owned(),
        "git diff --name-only l7r/diagram/old | head".to_owned(),
        "git diff --name-status HEAD -- l7r/diagram/old/stage.py | tail -2".to_owned(),
        "git log --stat --oneline -3 -- l7r/diagram/old/ | head".to_owned(),
        "git status --short l7r/diagram/old/ | tail -5".to_owned(),
    ] {
        assert!(bash(&cmd, &at).is_empty(), "{cmd}: {:?}", bash(&cmd, &at));
    }
    for cmd in [
        format!("make phase-read FILE={OLD} WHY=\"a b\" && cat {OLD}"),
        "git diff --stat l7r/diagram/old/ && git diff l7r/diagram/old/".to_owned(),
        "git diff --stat -p l7r/diagram/old/".to_owned(),
        "git log -p l7r/diagram/old/ | head".to_owned(),
        "find l7r/diagram/old | xargs cat".to_owned(),
    ] {
        assert!(refused(&bash(&cmd, &at), "old code"), "{cmd}");
    }
}

#[test]
fn the_refusal_names_the_derivation_the_task_recorded_or_none() {
    // T204: during T202 it named specs/449-rust-codebase/phases/placer_greenfield.derivation.md, which does not exist
    let at = world("derivation", &json!([]));
    let read = || run("Read", &json!({"file_path": OLD}), &at);
    let none = read();
    assert!(!refused(&none, "water_greenfield.derivation.md"));
    assert!(refused(&none, "names no derivation") && refused(&none, "specs/444-x/tasks.md"));
    assert!(refused(&none, "specs/444-x/plan.md"));
    std::fs::create_dir_all(format!("{at}/specs/444-x/derivations")).unwrap();
    std::fs::write(format!("{at}/specs/444-x/derivations/T9-water.md"), "d\n").unwrap();
    with_derivation(&at, "specs/444-x/derivations/T9-water.md");
    assert!(refused(
        &read(),
        "Write it from:  specs/444-x/derivations/T9-water.md"
    ));
    assert!(refused(
        &bash("grep -rn x l7r", &at),
        "Write it from:  specs/444-x/derivations/T9-water.md"
    ));
    with_derivation(&at, "specs/444-x/derivations/gone.md");
    let gone = read();
    let missing = "specs/444-x/derivations/gone.md, which is not in the checkout";
    assert!(refused(&gone, missing) && !refused(&gone, "Write it from:  "));
    // feature 444's form, where the stage's derivation is there
    std::fs::create_dir_all(format!("{at}/specs/444-x/phases")).unwrap();
    std::fs::write(
        format!("{at}/specs/444-x/phases/water_greenfield.derivation.md"),
        "d\n",
    )
    .unwrap();
    with_derivation(&at, "");
    assert!(refused(
        &read(),
        "Write it from:  specs/444-x/phases/water_greenfield.derivation.md"
    ));
}

#[test]
fn each_form_of_a_search_is_read() {
    // the shell's words as bash reads them, each tool's flags, the globs and the paths - the forms the cases above do not reach
    let at = world("forms", &json!([]));
    assert_eq!(fix_of(&[]), "");
    for cmd in [
        "grep -rn \"a\\\"b\" l7r",
        "LC_ALL=C grep -rn x l7r",
        "sudo env grep -rn x l7r",
        "grep -rn x l7r 2> /dev/null",
        "grep -rn x l7r l7r/diagram",
        "grep -rn x l7*",
        "grep -n x l7r/diagram/old/stag?.py",
        "grep -rnA3 x l7r",
        "grep -d recurse x l7r",
        "cd l7r && git grep x diagram",
        "git -c core.x=1 grep x",
        "git --no-pager grep x",
        "grep -rn -- x l7r",
        "cd l7r && git grep x HEAD:./diagram/old",
        "find -L l7r -exec grep x {} +",
        "cd l7r && find -name '*.py' -exec grep x {} +",
        "rg x l7r -g '!**/{new,zzz}/[!a]tage.py'",
        "rg x l7r -g '!**/{old'",
        "rg x l7r -g '!**/[old'",
    ] {
        let got = bash(cmd, &at);
        assert!(refused(&got, "Search without them"), "{cmd}: {got:?}");
    }
    for cmd in [
        "grep -rn x scripts/*",
        "rg x l7r -g '!**/{old,zzz}/[st]tage.py'",
        "rg x l7r -g '!**/[!a]ld/stage.py'",
        "ag x l7r --ignore old",
        "bash scripts/run.sh l7r",
        "git log --stat -U3 l7r/diagram/old/ | head",
    ] {
        let got = bash(cmd, &at);
        assert!(!refused(&got, "Search without them"), "{cmd}: {got:?}");
    }
    // two held files: the Grep tool's fix names both in one glob, and passes
    let two = world("forms-two", &json!([]));
    std::fs::write(format!("{two}/l7r/diagram/old/more.py"), "x\n").unwrap();
    let state = json!({"feature": "444-x", "task": "T9", "phase": "water", "files": [OLD, "l7r/diagram/old/more.py"], "allow": []});
    std::fs::write(format!("{two}/.git/phase-sources.json"), state.to_string()).unwrap();
    let glob = fix_of(&run("Grep", &json!({"pattern": "x", "path": "l7r"}), &two));
    assert_eq!(
        glob,
        "glob: \"!**/{diagram/old/stage.py,diagram/old/more.py}\""
    );
    let value = "!**/{diagram/old/stage.py,diagram/old/more.py}";
    let input = json!({"pattern": "x", "path": "l7r", "glob": value});
    assert!(run("Grep", &input, &two).is_empty());
}

#[test]
fn what_a_search_or_listing_hides_is_still_judged() {
    // the T204 review's cases: a listing that prints content, a search the parser cannot place, a glob a tool reads literally or
    // without case, and a search inside quotes - each passed by the first fix
    let at = world("hidden", &json!([]));
    for cmd in [
        "git show --stat HEAD:l7r/diagram/old/stage.py",
        "git status -v l7r/diagram/old/ | head",
        "git log --stat --cc l7r/diagram/old/ | head",
        "git grep x HEAD:l7r/diagram/old",
        "git grep -n x HEAD",
        "git grep -n x HEAD -- l7r",
        "grep -rn x l7r --exclude='*.{py,md}'",
        "find l7r -not -name '*.{py,md}' -exec grep x {} +",
        "ag x l7r --ignore '*.{py,md}'",
        "git grep x -- l7r ':(exclude)*.{py,md}'",
        "rg x l7r --iglob '*.PY'",
        "echo \"$(grep -rn x l7r)\"",
        "bash -c 'grep -rn x l7r'",
        "grep -n l7r/diagram/old/stage.py l7r/diagram/old/",
    ] {
        assert!(refused(&bash(cmd, &at), "old code"), "{cmd}");
    }
    for input in [
        json!({"pattern": "x", "path": "l7r", "glob": "*.md *.py"}),
        json!({"pattern": "x", "path": "l7r", "glob": "*.md,*.py"}),
    ] {
        assert!(refused(&run("Grep", &input, &at), "old code"), "{input}");
    }
    for cmd in [
        "rg x l7r -g '!**/{old,zzz}/stage.py'",
        "rg x l7r --iglob '!**/OLD/stage.py'",
        "git grep -n x HEAD -- l7r ':!l7r/diagram/old'",
        "bash -c 'grep -rn x l7r --exclude=stage.py'",
        "echo \"$(grep -rn x l7r/diagram/new)\"",
    ] {
        assert!(bash(cmd, &at).is_empty(), "{cmd}: {:?}", bash(cmd, &at));
    }
}

#[test]
fn a_find_whose_results_feed_a_reader_is_a_read() {
    // T204, the plan review's condition: a find feeding a reader through xargs (whatever sits between), through `$(...)` or
    // backticks, or by -exec printed the held code past the whole-command rule, which never saw the held file's name
    let at = world("find-feeds", &json!([]));
    for cmd in [
        "find l7r -name '*.py' | sort | xargs grep -n x",
        "cat $(find l7r -name '*.py')",
        "find l7r -type f | xargs cat",
        "find l7r -name '*.py' -exec cat {} +",
        "head -5 `find l7r -type f`",
        "less \"$(find l7r -type f)\"",
        "find l7r -type f | grep py | xargs -n 1 sed -n 1,9p",
    ] {
        let got = bash(cmd, &at);
        let fix = "Search without them:  -not -path '*/diagram/old/stage.py'";
        assert!(refused(&got, fix), "{cmd}: {got:?}");
    }
    for cmd in [
        "find l7r -name '*.py'",
        "find l7r -name '*.py' | wc -l",
        "find l7r -type f | sort",
        "find l7r -type f | xargs wc -l",
        "find l7r -not -path '*/diagram/old/stage.py' | sort | xargs grep -n x",
        "cat $(find l7r -not -path '*/old/*' -type f)",
        "find l7r ! -path '*/old/*' -type f | xargs cat",
        "find l7r -path '*/old' -prune -o -name '*.py' -exec cat {} +",
        "wc -l $(find l7r -type f)",
    ] {
        let got = bash(cmd, &at);
        assert!(got.is_empty(), "{cmd}: {got:?}");
    }
}

#[test]
fn a_reader_fed_by_any_producer_or_a_glob_is_a_read() {
    // T204, the plan review's second round: a reader fed by a lister other than find, by a list nobody can read here, or by a
    // shell glob into the held directory printed the held code
    let at = world("producers", &json!([]));
    for cmd in [
        "ls -R l7r | xargs cat",
        "ls l7r/diagram/old/* | xargs cat",
        "git ls-files l7r | xargs cat",
        "git ls-files | xargs grep -n x",
        "cat $(git ls-files l7r)",
        "tree -fi l7r | xargs cat",
        "cat l7r/diagram/old/*",
        "head -3 l7r/diagram/*/stage.py",
        "fd py l7r | xargs cat",
        "cat list.txt | xargs cat",
        "xargs cat < list.txt",
        "ls l7r/diagram/old | sort | xargs -I{} cat l7r/diagram/old/{}",
        "locate stage.py | xargs cat",
        "git diff --name-only | xargs cat",
    ] {
        let got = bash(cmd, &at);
        assert!(refused(&got, "Search without them:  "), "{cmd}: {got:?}");
    }
    for cmd in [
        "ls -R l7r --ignore=stage.py | xargs cat",
        "git ls-files l7r ':!l7r/diagram/old' | xargs cat",
        "git ls-files | xargs grep -n x --exclude=stage.py",
        "tree -fi l7r -I stage.py | xargs cat",
        "fd py l7r -E stage.py | xargs cat",
        "cat l7r/diagram/new/*",
        "ls l7r/diagram/new/* | xargs cat",
        "echo l7r/diagram/new/fresh.py | xargs cat",
        "git ls-files l7r | wc -l",
        "ls -R l7r | sort",
        "git ls-files | xargs wc -l",
        "cd l7r/diagram/new && cat list.txt | xargs cat",
        "cat $(git rev-parse --show-toplevel)/README.md",
        "head \"$(pwd)/notes.txt\"",
    ] {
        let got = bash(cmd, &at);
        assert!(got.is_empty(), "{cmd}: {got:?}");
    }
}

/// A checkout holding the parked crate (`homesteads`, `track`), the phases' `lib.rs`, and a transcript where the GM resumed one.
fn parked_world(tag: &str) -> crate::shared::tempdir::Held<(String, String)> {
    crate::shared::log::quiet();
    let d = crate::shared::tempdir::TempDir::new(&format!("guard-parked-{tag}"));
    let at = d.canonicalize().unwrap().to_string_lossy().into_owned();
    std::fs::create_dir_all(format!("{at}/rust/parked/src")).unwrap();
    std::fs::create_dir_all(format!("{at}/rust/phases/src")).unwrap();
    assert!(ask(std::path::Path::new("/"), "git", &["init", "-q", &at], "").ok());
    for f in ["homesteads.rs", "track.rs"] {
        std::fs::write(format!("{at}/rust/parked/src/{f}"), "").unwrap();
    }
    std::fs::write(format!("{at}/rust/phases/src/lib.rs"), "mod seat;\n").unwrap();
    let tr = format!("{at}/tr.jsonl");
    let said =
        json!({"type": "user", "message": {"content": "ok, go ahead with the homesteads now"}});
    std::fs::write(&tr, format!("{said}\n")).unwrap();
    d.hold((at, tr))
}

fn parked_run(tool: &str, input: &Value, at: &str, tr: &str) -> Vec<Answer> {
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": tool, "cwd": at, "transcript_path": tr, "tool_input": input}),
    };
    judge(
        &e,
        &Session::from_input(&e.input),
        at,
        "/nowhere/phase-sources.json",
        "2026-11-22T00:00:00Z",
    )
}

#[test]
fn a_parked_stage_moved_into_the_phases_is_refused_naming_the_ruling() {
    let w = parked_world("move");
    let (at, tr) = (&w.0, &w.1);
    let ruling = "Stop before homesteads, and talk first";
    let git_mv = parked_run(
        "Bash",
        &json!({"command": "git mv rust/parked/src/homesteads.rs rust/phases/src/"}),
        at,
        tr,
    );
    assert!(refused(
        &git_mv,
        "a write moving `homesteads` into rust/phases/src/"
    ));
    assert!(refused(&git_mv, ruling));
    assert!(refused(
        &git_mv,
        "GM_RESUMED=\"<the GM's words resuming it>\""
    ));
    let write = parked_run(
        "Write",
        &json!({"file_path": format!("{at}/rust/phases/src/track.rs"), "content": "x"}),
        at,
        tr,
    );
    assert!(refused(&write, "a write moving `track`"));
    let edit = parked_run(
        "Edit",
        &json!({"file_path": format!("{at}/rust/phases/src/track/law.rs"), "old_string": "", "new_string": "x"}),
        at,
        tr,
    );
    assert!(refused(&edit, "a write moving `track`"));
    // a mention, a read, a stage not parked: nothing
    let mention = parked_run(
        "Bash",
        &json!({"command": "echo git mv rust/parked/src/homesteads.rs rust/phases/src/"}),
        at,
        tr,
    );
    assert!(mention.is_empty());
    let read = parked_run(
        "Read",
        &json!({"file_path": format!("{at}/rust/parked/src/homesteads.rs")}),
        at,
        tr,
    );
    assert!(read.is_empty());
    let seat = parked_run(
        "Write",
        &json!({"file_path": format!("{at}/rust/phases/src/seat.rs"), "content": "x"}),
        at,
        tr,
    );
    assert!(seat.is_empty());
    let other = parked_run(
        "NotebookEdit",
        &json!({"file_path": format!("{at}/rust/phases/src/track.rs")}),
        at,
        tr,
    );
    assert!(other.is_empty());
}

#[test]
fn a_parked_stage_declared_in_the_phases_lib_rs_is_refused() {
    let w = parked_world("declare");
    let (at, tr) = (&w.0, &w.1);
    let lib = format!("{at}/rust/phases/src/lib.rs");
    let edit = parked_run(
        "Edit",
        &json!({"file_path": lib, "old_string": "mod seat;", "new_string": "mod homesteads;\nmod seat;"}),
        at,
        tr,
    );
    assert!(refused(
        &edit,
        "a write declaring `homesteads` in rust/phases/src/lib.rs"
    ));
    let write = parked_run(
        "Write",
        &json!({"file_path": lib, "content": "mod seat;\npub mod track;\n"}),
        at,
        tr,
    );
    assert!(refused(&write, "a write declaring `track`"));
    let edits = json!([{"old_string": "a", "new_string": "b"}, {"old_string": "mod seat;", "new_string": "mod seat;\nmod track;"}]);
    let multi = parked_run(
        "MultiEdit",
        &json!({"file_path": lib, "edits": edits}),
        at,
        tr,
    );
    assert!(refused(&multi, "a write declaring `track`"));
    let shell = parked_run(
        "Bash",
        &json!({"command": format!("echo 'mod track;' >> {lib}")}),
        at,
        tr,
    );
    assert!(refused(&shell, "a write declaring `track`"));
    let untouched = parked_run(
        "Edit",
        &json!({"file_path": lib, "old_string": "mod seat;", "new_string": "mod seat; // the seat"}),
        at,
        tr,
    );
    assert!(untouched.is_empty());
    let no_input = judge(
        &Event {
            name: "PreToolUse".to_owned(),
            input: json!({"tool_name": "Edit"}),
        },
        &Session::from_input(&json!({})),
        at,
        "/nowhere",
        "2026",
    );
    assert!(no_input.is_empty());
}

#[test]
fn the_gm_s_words_resume_a_stage_and_are_recorded() {
    let w = parked_world("resume");
    let (at, tr) = (&w.0, &w.1);
    let mv = "git mv rust/parked/src/homesteads.rs rust/phases/src/";
    // words the GM never wrote, or too few: refused
    let invented = parked_run(
        "Bash",
        &json!({"command": format!("GM_RESUMED=\"carry on with the stage\" {mv}")}),
        at,
        tr,
    );
    assert!(refused(
        &invented,
        "in no message the GM wrote in this session"
    ));
    let short = parked_run(
        "Bash",
        &json!({"command": format!("GM_RESUMED=yes {mv}")}),
        at,
        tr,
    );
    assert!(refused(&short, "under three words"));
    let start = parked_run(
        "Bash",
        &json!({"command": "GM_RESUMED=\"carry on with the stage\" make task-start F=444 T=T30"}),
        at,
        tr,
    );
    assert!(refused(&start, "in no message the GM wrote"));
    // his words: the move passes, recorded, and the stage's lib.rs line then passes with no words
    let start_ok = parked_run(
        "Bash",
        &json!({"command": "GM_RESUMED=\"go ahead with the homesteads\" make task-start F=444 T=T30"}),
        at,
        tr,
    );
    assert!(start_ok.is_empty());
    let moved = parked_run(
        "Bash",
        &json!({"command": format!("GM_RESUMED=\"go ahead with the homesteads\" {mv}")}),
        at,
        tr,
    );
    assert!(moved.is_empty());
    let row = std::fs::read_to_string(format!("{at}/.git/parked-resumed.jsonl")).unwrap();
    assert!(row.contains("\"stage\": \"homesteads\""), "{row}");
    let lib = format!("{at}/rust/phases/src/lib.rs");
    let declared = parked_run(
        "Edit",
        &json!({"file_path": lib, "old_string": "mod seat;", "new_string": "mod homesteads;\nmod seat;"}),
        at,
        tr,
    );
    assert!(declared.is_empty());
    // another stage stays held
    let track = parked_run(
        "Edit",
        &json!({"file_path": lib, "old_string": "mod seat;", "new_string": "mod seat;\nmod track;"}),
        at,
        tr,
    );
    assert!(refused(&track, "`track`"));
}

/// 451 T453: a reader is read by its name however it is spelled - by its path, past a `\` or a wrapper - as its bare name is.
#[test]
fn a_reader_is_read_however_it_is_spelled() {
    let at = world("spelled", &json!([]));
    for s in ["\\", "/usr/bin/", "command ", "env -i ", "nice -n 5 "] {
        for cmd in [
            format!("{s}cat {OLD}"),
            format!("{s}grep -rn x l7r"),
            format!("{s}git show HEAD:{OLD}"),
            format!("find l7r -type f | xargs {s}cat"),
        ] {
            assert!(refused(&bash(&cmd, &at), "old code"), "{cmd}");
        }
        let left_out = format!("{s}grep -rn x l7r --exclude-dir=old");
        assert!(bash(&left_out, &at).is_empty(), "{left_out}");
    }
    assert!(refused(
        &bash(&format!("ls; \"cat\" {OLD}"), &at),
        "old code"
    ));
    assert!(bash("command -v grep", &at).is_empty());
    assert!(bash(&format!("ls rust/cat {OLD}"), &at).is_empty());
}
