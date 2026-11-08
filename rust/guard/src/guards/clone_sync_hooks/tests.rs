//! The decider on the suite's shapes (`tests/hooks/test-clone-sync-hooks.sh`, replayed through the shim, is the verdict). Each world
//! is a mirror with one commit and a clone of it, copied in-process from one template so a test starts no `git clone`; the tree's
//! tools are `sh` fakes, steered by marker files.

use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

use serde_json::{json, Value};

use super::{both, decide, forbidden, judge, notes, sid_is_live, tail, Ctx};
use crate::protocol::{Answer, Event};
use crate::shared::session::Session;
use crate::shared::tool::{ask, Said};

fn git(dir: &Path, args: &[&str]) -> Said {
    let d = dir.to_string_lossy();
    let all: Vec<&str> = [
        "-C",
        d.as_ref(),
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "-c",
        "commit.gpgsign=false",
    ]
    .into_iter()
    .chain(args.iter().copied())
    .collect();
    ask(Path::new("/"), "git", &all, "")
}

fn script(p: &Path, body: &str) {
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, format!("#!/bin/sh\n{body}\n")).unwrap();
    std::fs::set_permissions(p, std::fs::Permissions::from_mode(0o755)).unwrap();
}

fn copy(from: &Path, to: &Path) {
    std::fs::create_dir_all(to).unwrap();
    for e in std::fs::read_dir(from).unwrap().filter_map(Result::ok) {
        let (src, dst) = (e.path(), to.join(e.file_name()));
        if e.file_type().unwrap().is_dir() {
            copy(&src, &dst);
        } else {
            std::fs::copy(&src, &dst).unwrap();
        }
    }
}

/// The template, made once: `diagram` (one commit, `origin/main` at it) and its clone `.clones/mine`, the fakes beside them.
fn template() -> &'static PathBuf {
    static T: OnceLock<PathBuf> = OnceLock::new();
    T.get_or_init(|| {
        let root = std::env::temp_dir().join(format!("l7r-guard-cs-template-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&root);
        let main = root.join("diagram");
        std::fs::create_dir_all(&main).unwrap();
        std::fs::write(main.join(".gitignore"), ".clones/\n").unwrap();
        git(&main, &["init", "-q", "-b", "main"]);
        git(&main, &["add", ".gitignore"]);
        git(&main, &["commit", "-q", "-m", "one"]);
        git(&main, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
        let clone = main.join(".clones/mine");
        let (m, c) = (main.to_string_lossy(), clone.to_string_lossy());
        assert!(ask(Path::new("/"), "git", &["clone", "-q", &m, &c], "").ok());
        // `.claude/settings.local.json`: git ignores it in the real repository, and the hook writes it on every prompt
        std::fs::write(clone.join(".git/info/exclude"), "scripts/\n.making\n.claude/settings.local.json\n").unwrap();
        // the clone's sync: its output, its exit from `.git/sync-rc`, a fast-forward when `.git/sync-ff` is there
        script(
            &clone.join("scripts/sync-with-main.sh"),
            "echo 'sync-with-main: NOTE kept'; echo said >&2\n[ -f .git/sync-ff ] && git fetch -q origin && git merge -q --ff-only FETCH_HEAD\nexit $(cat .git/sync-rc 2>/dev/null || echo 0)",
        );
        let tree = root.join("tree");
        script(&tree.join("scripts/hooks/lib/own-make.sh"), "[ -f .making ]");
        script(&tree.join("scripts/hooks/lib/usage_log.py"), "exit 0");
        script(&tree.join("scripts/reviews/layout_carry.sh"), "echo carried");
        root
    })
}

/// A world of its own, copied from the template.
struct World {
    main: PathBuf,
    clone: PathBuf,
    tree: PathBuf,
    sessions: PathBuf,
}

impl World {
    fn new(tag: &str) -> Self {
        crate::shared::log::quiet();
        let root = std::env::temp_dir().join(format!("l7r-guard-cs-{tag}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&root);
        copy(template(), &root);
        let main = root.join("diagram");
        let sessions = root.join("sessions");
        std::fs::create_dir_all(&sessions).unwrap();
        let clone = main.join(".clones/mine");
        git(
            &clone,
            &["remote", "set-url", "origin", &main.to_string_lossy()],
        );
        Self {
            clone,
            tree: root.join("tree"),
            main,
            sessions,
        }
    }

    /// Main moves on a commit the clone does not have; `origin` follows unless the commit is a stray.
    fn advance(&self, file: &str, stray: bool) {
        std::fs::create_dir_all(self.main.join(file).parent().unwrap()).unwrap();
        std::fs::write(self.main.join(file), "x").unwrap();
        git(&self.main, &["add", file]);
        git(&self.main, &["commit", "-q", "-m", "two"]);
        if !stray {
            git(
                &self.main,
                &["update-ref", "refs/remotes/origin/main", "HEAD"],
            );
        }
        git(&self.clone, &["fetch", "-q", "origin"]);
    }

    fn claim(&self, sid: &str, clone: &Path) {
        let map = self.main.join(".clones/.session-clones");
        std::fs::create_dir_all(&map).unwrap();
        std::fs::write(map.join(sid), clone.to_string_lossy().as_bytes()).unwrap();
    }

    /// A transcript whose last `/rename` names the session `title`.
    fn titled(&self, title: &str) -> String {
        let t = self.sessions.join(format!("{title}.jsonl"));
        std::fs::write(
            &t,
            json!({"type": "custom-title", "customTitle": title}).to_string(),
        )
        .unwrap();
        t.to_string_lossy().into_owned()
    }

    fn session(&self, input: &Value) -> Session {
        let (m, s) = (
            self.main.to_string_lossy().into_owned(),
            self.sessions.to_string_lossy().into_owned(),
        );
        Session::with_env(input, |k| match k {
            "CLONE_MAIN" => Some(m.clone()),
            "CLONE_SESSIONS_DIR" => Some(s.clone()),
            _ => None,
        })
    }

    fn run(&self, name: &str, input: Value) -> Vec<Answer> {
        let session = self.session(&input);
        let event = Event {
            name: name.to_owned(),
            input,
        };
        judge(&Ctx {
            event: &event,
            session: &session,
            main: self.main.clone(),
            tree: self.tree.clone(),
            python: "sh",
            solo_forced: Some(
                if self.tree.join("scripts/hooks/lib/solo").exists() {
                    "1"
                } else {
                    "0"
                }
                .to_owned(),
            ),
        })
    }

    fn edit(&self, sid: &str, transcript: &str, path: &Path) -> Vec<Answer> {
        self.run(
            "PreToolUse",
            json!({"session_id": sid, "transcript_path": transcript, "tool_name": "Write", "tool_input": {"file_path": path.to_string_lossy()}}),
        )
    }

    fn prompt(&self, sid: &str, transcript: &str) -> String {
        let got = self.run(
            "UserPromptSubmit",
            json!({"session_id": sid, "transcript_path": transcript}),
        );
        if let [Answer::Print(s)] = &got[..] {
            s.clone()
        } else {
            assert!(got.is_empty());
            String::new()
        }
    }
}

fn refused(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Refuse(w)] if w.contains(words))
}

fn told(got: &[Answer], words: &str) -> bool {
    matches!(got, [Answer::Notice(w)] if w.contains(words))
}

#[test]
fn an_edit_outside_a_clone_or_into_a_dirty_one_is_let_through() {
    let w = World::new("through");
    let me = w.titled("mine");
    assert!(w.edit("s", &me, &w.main.join("a.txt")).is_empty());
    assert!(w.edit("s", &me, &w.main.join(".clones/mine/")).is_empty());
    assert!(w
        .edit("s", &me, &w.main.join(".clones/ghost/a.txt"))
        .is_empty());
    std::fs::write(w.clone.join("wip.txt"), "x").unwrap();
    assert!(w.edit("s", &me, &w.clone.join("a.txt")).is_empty());
    let claimed = std::fs::read_to_string(w.main.join(".clones/.session-clones/s")).unwrap();
    assert_eq!(claimed, w.clone.to_string_lossy());
}

#[test]
fn a_forbidden_name_or_another_sessions_clone_is_refused() {
    let w = World::new("names");
    let a = w.clone.join("a.txt");
    assert!(refused(
        &w.edit("s", &w.titled("gm-assistant"), &a),
        "has no distinct name"
    ));
    let gm = w.main.join(".clones/gm-assistant");
    std::fs::create_dir_all(gm.join(".git")).unwrap();
    assert!(refused(&w.edit("s", "", &gm.join("a.txt")), "is a FORBIDDEN clone name (a repository's name, not a session). Work in .clones/<your-session-name>."));
    assert!(refused(
        &w.edit("s", &w.titled("other"), &gm.join("a.txt")),
        "(this session resolves to"
    ));
    assert!(refused(
        &w.edit("s", &w.titled("other"), &a),
        "this session's clone is"
    ));
    assert!(forbidden(&w.main, &w.main) && !forbidden(&w.clone, &w.main));
}

#[test]
fn a_clone_another_live_session_claims_is_refused() {
    let w = World::new("live");
    let mut other = std::process::Command::new("sh")
        .args(["-c", "sleep 5; :", "claude"])
        .spawn()
        .unwrap();
    std::fs::write(
        w.sessions.join(format!("{}.json", other.id())),
        json!({"sessionId": "them"}).to_string(),
    )
    .unwrap();
    std::fs::write(
        w.sessions.join("x.json"),
        json!({"sessionId": "nopid"}).to_string(),
    )
    .unwrap();
    std::fs::write(w.sessions.join("bad.json"), "{").unwrap();
    w.claim("them", &w.clone);
    w.claim(".hidden", &w.clone);
    let got = w.edit("s", "", &w.clone.join("a.txt"));
    let _ = other.kill();
    let _ = other.wait();
    assert!(refused(
        &got,
        "already occupied by another live session (them)"
    ));
    assert!(!sid_is_live("nopid", &w.sessions) && !sid_is_live("them", Path::new("/nowhere")));
    assert!(w.edit("", "", &w.clone.join("a.txt")).is_empty());
}

#[test]
fn a_clean_clone_on_main_is_claimed_and_one_behind_a_stray_is_refused() {
    let w = World::new("stray");
    assert!(w.edit("s", "", &w.clone.join("a.txt")).is_empty());
    w.advance("b.txt", true);
    assert!(refused(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "is carrying a commit GitHub main does not have"
    ));
}

#[test]
fn a_clone_behind_under_a_make_or_a_gate_lock_waits() {
    let w = World::new("running");
    w.advance("b.txt", false);
    std::fs::write(w.clone.join(".making"), "").unwrap();
    assert!(told(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "but a make runs in it"
    ));
    std::fs::remove_file(w.clone.join(".making")).unwrap();
    script(
        &w.clone.join("scripts/gates/gate_lock.py"),
        "[ -f \"$2/held\" ]",
    );
    std::fs::write(w.clone.join(".git/held"), "").unwrap();
    assert!(told(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "but a make runs in it"
    ));
}

#[test]
fn a_clone_behind_that_cannot_fast_forward_is_refused() {
    let w = World::new("ff");
    w.advance("b.txt", false);
    std::fs::write(w.clone.join(".git/sync-rc"), "1").unwrap();
    assert!(refused(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "has a clean tree (a new work unit) but its HEAD is behind main"
    ));
}

#[test]
fn a_clone_behind_is_fast_forwarded() {
    let w = World::new("ff-ok");
    w.advance("b.txt", false);
    std::fs::write(w.clone.join(".git/sync-ff"), "").unwrap();
    assert!(told(
        &w.edit("s", "", &w.clone.join("a.txt")),
        "so main was merged in"
    ));
}

#[test]
fn a_mirror_with_no_head_judges_nothing() {
    let bare = World::new("bare");
    std::fs::remove_dir_all(bare.main.join(".git")).unwrap();
    assert!(bare.edit("s", "", &bare.clone.join("a.txt")).is_empty());
}

#[test]
fn a_dirty_clones_test_run_behind_main_is_told_why() {
    let w = World::new("behind");
    let make = |cmd: &str, tool: &str| {
        w.run(
            "PreToolUse",
            json!({"session_id": "s", "tool_name": tool, "tool_input": {"command": cmd}}),
        )
    };
    assert!(make("make quick", "Bash").is_empty());
    w.claim("s", &w.clone);
    assert!(make("make quick", "Bash").is_empty());
    std::fs::write(w.clone.join("wip.txt"), "x").unwrap();
    assert!(make("make quick", "Bash").is_empty());
    assert!(make("make lines", "Bash").is_empty());
    assert!(make("make quick", "Read").is_empty());
    w.advance("l7r/x.py", false);
    assert!(told(&make("make quick", "Bash"), "are ENGINE paths"));
    w.advance("docs/y.md", false);
    let got = make("make done", "Bash");
    assert!(told(&got, "main has 2 commit(s)") && told(&got, "1 changed file(s) are ENGINE"));
}

#[test]
fn a_dirty_clones_run_behind_on_docs_alone_is_told_it_is_cheap() {
    let clean = World::new("behind-clean");
    clean.claim("s", &clean.clone);
    std::fs::write(clean.clone.join("wip.txt"), "x").unwrap();
    clean.advance("docs/y.md", false);
    let quick = clean.run(
        "PreToolUse",
        json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "make quick"}}),
    );
    assert!(told(&quick, "no changed file is an engine path"));
    git(
        &clean.main,
        &["commit", "-q", "--allow-empty", "-m", "unfetched"],
    );
    git(
        &clean.main,
        &["update-ref", "refs/remotes/origin/main", "HEAD"],
    );
    let unfetched = clean.run(
        "PreToolUse",
        json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "make quick"}}),
    );
    assert!(told(&unfetched, "main has new commit(s)"));
    git(
        &clean.main,
        &["update-ref", "-d", "refs/remotes/origin/main"],
    );
    assert!(clean
        .run(
            "PreToolUse",
            json!({"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "make quick"}})
        )
        .is_empty());
}

#[test]
fn an_unnamed_session_is_told_once() {
    let w = World::new("unnamed");
    assert!(w.prompt("", "").is_empty());
    assert!(w.prompt("s", "").contains("does not resolve"));
    assert!(w.prompt("s", "").is_empty());
    assert!(w
        .prompt("g", &w.titled("diagram"))
        .contains("resolves to the FORBIDDEN '.clones/diagram'"));
    assert!(w.prompt("n", &w.titled("mine")).is_empty());
    w.claim("gone", &w.main.join(".clones/ghost"));
    assert!(w.prompt("gone", "").is_empty());
}

#[test]
fn a_mid_task_prompt_refreshes_only_the_mirror() {
    let w = World::new("midtask");
    w.claim("s", &w.clone);
    std::fs::create_dir_all(w.clone.join(".specify")).unwrap();
    std::fs::write(w.clone.join(".specify/feature.json"), "{}").unwrap();
    git(&w.clone, &["add", "-f", ".specify/feature.json"]);
    let said = w.prompt("s", "");
    assert!(
        said.contains("feature.json is TRACKED again")
            && said.contains(
                "has uncommitted work (mid-task) - clone merge skipped; mirror refreshed"
            )
            && said.ends_with("sync-with-main: NOTE kept")
    );
    assert!(!w.prompt("s", "").contains("TRACKED"));
    git(&w.clone, &["rm", "-q", "--cached", ".specify/feature.json"]);
    std::fs::remove_dir_all(w.clone.join(".specify")).unwrap();
    std::fs::write(w.clone.join(".making"), "").unwrap();
    std::fs::write(w.clone.join(".git/sync-rc"), "1").unwrap();
    assert!(w.prompt("s", "").contains("has a make run going (a gate or a roll) - clone merge skipped; mirror refresh FAILED: said"));
    std::fs::remove_file(w.clone.join(".making")).unwrap();
    std::fs::remove_file(w.clone.join(".git/sync-rc")).unwrap();
    script(
        &w.clone.join("scripts/gates/gate_lock.py"),
        "[ -f \"$2/held\" ]",
    );
    std::fs::write(w.clone.join(".git/held"), "").unwrap();
    std::fs::create_dir_all(w.tree.join("scripts/l7r/diagram")).unwrap();
    std::fs::write(w.tree.join("scripts/l7r/diagram/__init__.py"), "").unwrap();
    std::fs::create_dir_all(w.clone.join(".claude/skills/diagram")).unwrap();
    std::fs::write(w.clone.join(".claude/skills/diagram/Makefile"), "").unwrap();
    git(&w.clone, &["add", "-f", ".claude/skills/diagram/Makefile"]);
    let old = w.prompt("s", "");
    assert!(old.contains("has uncommitted work") && old.contains("still on the old layout"));
    git(
        &w.clone,
        &["rm", "-q", "--cached", ".claude/skills/diagram/Makefile"],
    );
    std::fs::remove_dir_all(w.clone.join(".claude")).unwrap();
    assert!(w.prompt("s", "").contains("holds a running gate's lock"));
}

#[test]
fn an_idle_prompt_syncs_the_clone_unless_it_is_the_only_session() {
    let w = World::new("idle");
    w.claim("s", &w.clone);
    assert_eq!(
        w.prompt("s", ""),
        format!(
            "clone-sync: auto-synced {} with main (git)\ncarried\nsync-with-main: NOTE kept",
            w.clone.display()
        )
    );
    std::fs::write(w.clone.join(".git/sync-rc"), "1").unwrap();
    assert!(w
        .prompt("s", "")
        .ends_with("resolve before modifying the repo: sync-with-main: NOTE kept\nsaid"));
    std::fs::write(w.tree.join("scripts/hooks/lib/solo"), "").unwrap();
    assert!(w.prompt("s", "").is_empty());
}

#[test]
fn the_helpers_and_the_entry() {
    assert_eq!(tail("a\nb\nc", 2), "b\nc");
    assert_eq!(
        notes("x\nsync-with-main: WARNING w\nsync-with-main: NOTE n"),
        ["sync-with-main: WARNING w", "sync-with-main: NOTE n"]
    );
    assert_eq!(
        both(&Said {
            code: 0,
            out: String::new(),
            err: "e".into()
        }),
        "e"
    );
    let e = Event {
        name: "PreToolUse".to_owned(),
        input: json!({"tool_name": "Bash", "tool_input": {"command": "ls"}}),
    };
    assert!(decide(&e, &Session::from_input(&e.input)).is_empty());
}
