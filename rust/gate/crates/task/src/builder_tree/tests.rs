//! The builder pool on a real repository and its worktrees (feature 451 T285): a tree handed out warm, a landed tree's edits no
//! hold, a cold tree made only when none is free, the cap, the release that never fails a landing, the drop and the adoption.

use std::os::unix::fs::PermissionsExt as _;
use std::path::{Path, PathBuf};

use l7r_gate_core::ci::fixtures::{commit, git, put};
use l7r_gate_core::write_executable;
use l7r_shared::builder_pool;

use super::{run, Env};
use crate::tests::{repo, root_of};

pub(crate) fn words(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

pub(crate) fn env(dir: &Path) -> Env {
    Env {
        cache: dir.join("cache"),
        cap: 2,
        now: "2026-11-26T12:00:00Z".to_owned(),
        lock_tries: 1,
        discard: String::new(),
        reason: String::new(),
        guard_secs: "5".to_owned(),
        prewarm: true,
        sampler: Vec::new(),
    }
}

/// The fixture's clone with a guard wrapper committed, which leaves `<tree>.guard-built` beside the tree it runs from.
pub(crate) fn world(tag: &str) -> (l7r_shared::tempdir::TempDir, PathBuf) {
    let dir = repo(tag);
    let root = root_of(&dir);
    std::fs::create_dir_all(root.join("scripts/hooks")).unwrap();
    write_executable(
        &root.join("scripts/hooks/l7r-guard.sh"),
        "#!/bin/sh\n[ \"$L7R_GUARD_PRINT_FRESH\" = 1 ] && [ \"$L7R_GUARD_BUILD_SECS\" = 5 ] && touch \"$(cd \"$(dirname \"$0\")/../..\" && pwd).guard-built\"\n",
    );
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the guard wrapper"]);
    (dir, root)
}

pub(crate) fn pool_of(root: &Path) -> Vec<builder_pool::Tree> {
    builder_pool::read(&root.join(".git"))
}

#[test]
fn a_tree_is_made_cold_handed_out_again_warm_and_survives_its_landing() {
    let (dir, root) = world("pool-take");
    let e = env(&dir);
    // none in the pool: one made, held, said to be cold, its guard built
    let first = run(&words(&["take", "T01", "9001-x"]), &root, &e);
    let b1 = dir.join("repo-b1");
    assert_eq!(first.code, 0, "{}", first.stderr);
    assert_eq!(first.stdout, format!("{}\n", b1.display()));
    assert!(
        first.stderr.contains("is NEW and held by 9001 T01: COLD"),
        "{}",
        first.stderr
    );
    assert!(
        first.stderr.contains("its guard binary is built")
            && dir.join("repo-b1.guard-built").exists()
    );
    assert_eq!(pool_of(&root)[0].holder(), "9001 T01");
    assert!(!root.join(".git/builder-pool.lock").exists());
    // asked again by its task, from the tree itself: the same tree
    let again = run(&words(&["take", "T01", "9001"]), &b1, &e);
    assert_eq!(
        (again.code, again.stdout.as_str()),
        (0, first.stdout.as_str())
    );
    assert!(again.stderr.contains("9001 T01 already holds it"));
    // the builder's work, carried to the clone and landed there: the tree still holds the same edits, uncommitted
    put(&b1, "scripts/a.py", "x = 2\n");
    put(&b1, "scripts/new.py", "y = 1\n");
    std::fs::remove_file(b1.join("dev/bypass-log/.keep")).unwrap();
    put(&root, "scripts/a.py", "x = 2\n");
    put(&root, "scripts/new.py", "y = 1\n");
    std::fs::remove_file(root.join("dev/bypass-log/.keep")).unwrap();
    commit(&root, "scripts/landed.py", "z = 1\n");
    std::fs::create_dir_all(e.cache.join("repo-b1/tool")).unwrap();
    let landed = run(&words(&["landed", "9001", "T01", "T02"]), &root, &e);
    assert_eq!(landed.code, 0);
    assert!(landed.stdout.contains("is free (9001 T01 released), the tree and its build cache left in place, at the clone's HEAD"), "{}", landed.stdout);
    assert!(b1.join("scripts/landed.py").exists() && e.cache.join("repo-b1/tool").is_dir());
    assert_eq!(git(&b1, &["status", "--porcelain"]), "");
    // a task that holds none: quiet
    let none = run(&words(&["release", "T07"]), &root, &e);
    assert_eq!(
        (none.code, none.stdout.as_str()),
        (0, "builder-tree: T07 holds no pool tree\n")
    );
    // the next task gets the same tree, warm, at the clone's new HEAD
    commit(&root, "scripts/later.py", "w = 1\n");
    let next = run(&words(&["take", "T02,T03", "specs/9001-x/"]), &root, &e);
    assert_eq!(next.stdout, first.stdout);
    assert!(
        next.stderr
            .contains("held by 9001 T02,T03, at the clone's HEAD")
            && next.stderr.contains("warm"),
        "{}",
        next.stderr
    );
    assert!(b1.join("scripts/later.py").exists());
    assert_eq!(pool_of(&root).len(), 1);
    let listed = run(&words(&["list"]), &root, &e);
    assert!(
        listed
            .stdout
            .starts_with("builder-trees: 1 of 2 (the cap, L7R_BUILDER_POOL)"),
        "{}",
        listed.stdout
    );
    assert!(
        listed
            .stdout
            .contains("repo-b1  9001 T02,T03  since 2026-11-26T12:00:00Z  cache ")
            && !listed.stdout.contains("cache none")
    );
    let log = std::fs::read_to_string(root.join(".git/builder-pool.log")).unwrap();
    assert_eq!(log.lines().count(), 3, "{log}");
}

#[test]
fn work_not_in_head_holds_a_free_tree_and_no_cold_one_is_made_past_it() {
    let (dir, root) = world("pool-held");
    let mut e = env(&dir);
    let b1 = dir.join("repo-b1");
    run(&words(&["take", "T01", "9001"]), &root, &e);
    for n in 0..7 {
        put(&b1, &format!("scripts/w{n}.py"), "unlanded\n");
    }
    put(&b1, "scripts/a.py", "x = 3\n");
    let freed = run(&words(&["release", "T01", "9001"]), &root, &e);
    assert!(freed.stdout.contains("left as it is, holding uncommitted work that is not in the clone's HEAD (scripts/a.py, ") && freed.stdout.contains(" and 3 more)"), "{}", freed.stdout);
    let held = run(&words(&["take", "T02", "9001"]), &root, &e);
    assert_eq!(held.code, 2);
    assert!(
        held.stderr.contains("is free and held by uncommitted work")
            && held.stderr.contains("DISCARD="),
        "{}",
        held.stderr
    );
    assert!(!dir.join("repo-b2").exists());
    // the discard needs its reason, then takes the tree over the work
    e.discard = "no".to_owned();
    assert!(run(&words(&["take", "T02", "9001"]), &root, &e)
        .stderr
        .contains("DISCARD needs a reason"));
    e.discard = "the probe is done".to_owned();
    let taken = run(&words(&["take", "T02", "9001"]), &root, &e);
    assert_eq!(taken.code, 0, "{}", taken.stderr);
    assert_eq!(git(&b1, &["status", "--porcelain"]), "");
    assert!(std::fs::read_to_string(root.join(".git/builder-pool.log"))
        .unwrap()
        .contains("\"event\":\"discard\""));
    // a holder that died left the lock: the next command takes its turn
    put(&root, ".git/builder-pool.lock", "");
    e.discard.clear();
    // a second tree while the first is held, then the cap, naming who holds each
    let second = run(&words(&["take", "T03", "9001"]), &root, &e);
    assert_eq!(
        second.stdout,
        format!("{}\n", dir.join("repo-b2").display())
    );
    let full = run(&words(&["take", "T04", "9001"]), &root, &e);
    assert_eq!(full.code, 2);
    assert!(
        full.stderr.contains("at its cap of 2")
            && full.stderr.contains("repo-b1  held by 9001 T02 since")
            && full.stderr.contains("repo-b2  held by 9001 T03"),
        "{}",
        full.stderr
    );
    // a feature that is not the holder's releases nothing; a tree gone from disk is named, never handed out
    assert!(run(&words(&["release", "T03", "77"]), &root, &e)
        .stdout
        .contains("holds no pool tree"));
    run(&words(&["release", "T02 T03"]), &root, &e);
    std::fs::rename(dir.join("repo-b1"), dir.join("moved")).unwrap();
    let gone = run(&words(&["take", "T05", "9001"]), &root, &e);
    assert_eq!(gone.stdout, format!("{}\n", dir.join("repo-b2").display()));
    assert!(
        gone.stderr
            .contains("repo-b1 is in the pool and gone from disk - make builder-tree-drop"),
        "{}",
        gone.stderr
    );
    assert!(run(&words(&["list"]), &root, &e)
        .stdout
        .contains("cache none  GONE from disk"));
    run(&words(&["release", "T05"]), &root, &e);
    assert_eq!(pool_of(&root).iter().filter(|t| t.free()).count(), 2);
}

#[test]
fn a_tree_goes_only_by_the_drop_with_its_cache_and_its_reason() {
    let (dir, root) = world("pool-drop");
    let mut e = env(&dir);
    let b1 = dir.join("repo-b1");
    let b1_text = b1.to_string_lossy().into_owned();
    run(&words(&["take", "T01", "9001"]), &root, &e);
    std::fs::create_dir_all(e.cache.join("repo-b1/debug")).unwrap();
    assert!(run(&words(&["drop", &b1_text]), &root, &e)
        .stderr
        .contains("REASON needs two words"));
    e.reason = "the pool shrinks".to_owned();
    assert!(run(&words(&["drop", "/nowhere"]), &root, &e)
        .stderr
        .contains("is not a pool tree"));
    let held = run(&words(&["drop", &b1_text]), &root, &e);
    assert!(
        held.stderr
            .contains("is held by 9001 T01 - make builder-tree-release T=T01 first"),
        "{}",
        held.stderr
    );
    run(&words(&["release", "T01"]), &root, &e);
    put(&b1, "scripts/probe.py", "p\n");
    let done = run(&words(&["drop", &b1_text]), &root, &e);
    assert_eq!(done.code, 0, "{}", done.stderr);
    assert!(
        done.stdout.contains("are removed (the pool shrinks)")
            && done
                .stdout
                .contains("uncommitted work went with it: scripts/probe.py"),
        "{}",
        done.stdout
    );
    assert!(!b1.exists() && !e.cache.join("repo-b1").exists() && pool_of(&root).is_empty());
    // one already gone from disk drops too
    run(&words(&["take", "T02", "9001"]), &root, &e);
    run(&words(&["release", "T02"]), &root, &e);
    std::fs::remove_dir_all(&b1).unwrap();
    let late = run(&words(&["drop", &b1_text]), &root, &e);
    assert!(
        late.code == 0 && !late.stdout.contains("uncommitted work") && pool_of(&root).is_empty()
    );
}

#[test]
fn a_tree_made_before_the_pool_is_adopted_under_its_own_name() {
    let (dir, root) = world("pool-adopt");
    let e = env(&dir);
    let old = dir.join("repo-t269");
    let old_text = old.to_string_lossy().into_owned();
    for name in ["repo-t269", "repo-land", "repo-t270", "repo-t271"] {
        git(
            &root,
            &[
                "worktree",
                "add",
                "-q",
                "--detach",
                &dir.join(name).to_string_lossy(),
                "HEAD",
            ],
        );
    }
    for not in [
        root.to_string_lossy().into_owned(),
        dir.join("repo-land").to_string_lossy().into_owned(),
        "/nowhere".to_owned(),
    ] {
        let said = run(&words(&["adopt", &not]), &root, &e);
        assert!(
            said.code == 2 && said.stderr.contains("is not a builder's worktree"),
            "{}",
            said.stderr
        );
    }
    let held = run(&words(&["adopt", &old_text, "T285", "451"]), &root, &e);
    assert_eq!(held.stdout, format!("builder-tree-adopt: {old_text} joins the pool under its own name (451 T285), its build cache as it is\n"));
    assert!(run(&words(&["adopt", &old_text]), &root, &e)
        .stderr
        .contains("already in the pool"));
    let free = run(
        &words(&["adopt", &dir.join("repo-t270").to_string_lossy()]),
        &root,
        &e,
    );
    assert!(free.stdout.contains("(free)"), "{}", free.stdout);
    assert!(run(
        &words(&["adopt", &dir.join("repo-t271").to_string_lossy()]),
        &root,
        &e
    )
    .stderr
    .contains("at its cap of 2"));
    // the adopted free tree is the one handed out
    assert_eq!(
        run(&words(&["take", "T09", "9001"]), &root, &e).stdout,
        format!("{}\n", dir.join("repo-t270").display())
    );
}

#[test]
fn what_cannot_be_done_says_so_and_a_landing_s_release_never_fails() {
    let (dir, root) = world("pool-fail");
    let e = env(&dir);
    let outside = dir.join("outside");
    std::fs::create_dir_all(&outside).unwrap();
    // `GIT_CEILING_DIRECTORIES` is not needed: the fixture's scratch is under no repository
    let lost = run(&words(&["take", "T01", "9001"]), &outside, &e);
    assert_eq!(
        (lost.code, lost.stderr.as_str()),
        (2, "builder-tree: not in a git repository\n")
    );
    let landing = run(&words(&["landed", "9001", "T01"]), &outside, &e);
    assert_eq!(landing.code, 0);
    assert!(landing
        .stderr
        .starts_with("builder-tree: the release failed - the landing stands:"));
    for bad in [
        &["take"][..],
        &["release"],
        &["landed", "9001"],
        &["drop"],
        &["adopt"],
        &["nonsense"],
        &[],
    ] {
        let said = run(&words(bad), &root, &e).stderr;
        assert!(said.starts_with("usage: l7r-gate builder-tree"), "{bad:?}");
    }
    assert!(super::cli(&[], &root).stderr.starts_with("usage:"));
    // a hold names its feature, so every hold is one the handout's freeing step reads
    let old = dir.join("repo-old").to_string_lossy().into_owned();
    for unnamed in [&["take", "T01"][..], &["adopt", &old, "T01"]] {
        let no = run(&words(unnamed), &root, &e);
        assert_eq!((no.code, no.stderr.as_str()), (2, super::NO_FEATURE));
    }
    assert!(pool_of(&root).is_empty());
    assert_eq!(super::size_word(""), "?");
    assert_eq!(super::size_word("8.1G\t/x\n"), "8.1G");
    // a guard that does not build is said, the tree still handed out, with what builds it next: the disk floor's bounded build
    // (451 T286), not the hook wrapper's 45 s limit (451 T448)
    git(&root, &["rm", "-q", "scripts/hooks/l7r-guard.sh"]);
    git(&root, &["commit", "-qm", "no wrapper"]);
    let made = run(&words(&["take", "T01", "9001"]), &root, &e);
    assert!(
        made.code == 0 && made.stderr.contains("its guard binary did NOT build"),
        "{}",
        made.stderr
    );
    assert!(made.stderr.contains("the disk floor of its first `make closing-checks`, `make done` or `make land` builds it, waiting up to L7R_GUARD_COLD_SECS (600 s) for another call's build"), "{}", made.stderr);
    assert!(!made.stderr.contains("45 s limit"), "{}", made.stderr);
    // the registry unwritable: a release says so and fails, a landing's says so and does not
    let registry = root.join(".git/builder-pool.json");
    let kept = std::fs::read_to_string(&registry).unwrap();
    let block = |on: bool| {
        let tmp = root.join(".git/builder-pool.json.tmp");
        if on {
            std::fs::create_dir_all(tmp.join("x")).unwrap();
        } else {
            std::fs::remove_dir_all(tmp).unwrap();
        }
    };
    block(true);
    let failed = run(&words(&["release", "T01"]), &root, &e);
    assert!(
        failed.code == 1 && failed.stderr.contains("builder-pool.json"),
        "{}",
        failed.stderr
    );
    let stands = run(&words(&["landed", "9001", "T01"]), &root, &e);
    assert_eq!(stands.code, 0);
    assert!(
        stands
            .stderr
            .starts_with("builder-tree: the release failed - the landing stands: builder-tree: "),
        "{}",
        stands.stderr
    );
    block(false);
    std::fs::write(&registry, kept).unwrap();
    // git cannot make the next tree where its place is taken by a registered path's twin: the clones directory read-only
    let lock_dir =
        |mode: u32| std::fs::set_permissions(&*dir, std::fs::Permissions::from_mode(mode)).unwrap();
    lock_dir(0o555);
    let refused = run(&words(&["take", "T02", "9001"]), &root, &e);
    lock_dir(0o755);
    assert!(
        refused.code == 2 && refused.stderr.contains("git worktree add could not make"),
        "{}",
        refused.stderr
    );
}

#[test]
fn a_tree_whose_tasks_landed_by_any_route_is_free_at_the_next_handout() {
    let (dir, root) = world("pool-landed");
    let e = env(&dir);
    // T09 is ticked in the fixture's tasks.md, as a land-batch or a hand tick leaves it, and nothing released its tree
    let first = run(&words(&["take", "T09", "9001"]), &root, &e);
    put(&root, "specs/9001-x/tasks-done.md", "- [X] T08 archived\n");
    let again = run(&words(&["take", "T02", "9001"]), &root, &e);
    assert_eq!(again.stdout, first.stdout);
    assert!(
        again
            .stderr
            .contains("was held by 9001 T09, which has landed: free"),
        "{}",
        again.stderr
    );
    assert_eq!(pool_of(&root)[0].holder(), "9001 T02");
    // an open task's tree is not: the next handout makes another
    let other = run(&words(&["take", "T08", "9001"]), &root, &e);
    assert_eq!(other.stdout, format!("{}\n", dir.join("repo-b2").display()));
    // ... and T08, archived as done, frees that one in its turn
    assert_eq!(
        run(&words(&["take", "T03", "9001"]), &root, &e).stdout,
        other.stdout
    );
    // a held tree gone from disk is released as gone, never called at the clone's HEAD
    std::fs::remove_dir_all(dir.join("repo-b2")).unwrap();
    let gone = run(&words(&["release", "T03", "9001"]), &root, &e);
    assert_eq!(gone.code, 0, "{}", gone.stderr);
    assert!(gone.stdout.contains("GONE from disk"), "{}", gone.stdout);
    assert!(pool_of(&root)[1].free());
}

/// The fixture's clone with a gate wrapper too, which notes its words in `<tree>.prewarm` beside the tree it runs from.
fn warm_world(tag: &str) -> (l7r_shared::tempdir::TempDir, PathBuf) {
    let (dir, root) = world(tag);
    std::fs::create_dir_all(root.join("scripts/gates")).unwrap();
    write_executable(
        &root.join("scripts/gates/l7r-gate.sh"),
        "#!/bin/sh\necho \"$@ in $(pwd)\" >> \"$(cd \"$(dirname \"$0\")/../..\" && pwd).prewarm\"\n",
    );
    git(&root, &["add", "-A"]);
    git(&root, &["commit", "-qm", "the gate wrapper"]);
    (dir, root)
}

/// The pre-warms the pool's log says were started.
fn prewarms(root: &Path) -> usize {
    std::fs::read_to_string(root.join(".git/builder-pool.log"))
        .unwrap()
        .lines()
        .filter(|l| l.contains("\"event\":\"prewarm\""))
        .count()
}

#[test]
fn a_warm_handout_starts_the_pre_warm_of_what_moved_since_the_tree_s_last_handout() {
    let (dir, root) = warm_world("pool-prewarm");
    let mut e = env(&dir);
    let b1 = dir.join("repo-b1");
    // a cold tree: nothing to warm it for, and its handout is what the next is measured from
    let cold = run(&words(&["take", "T01", "9001"]), &root, &e);
    assert!(!cold.stderr.contains("pre-warm"), "{}", cold.stderr);
    let first = git(&root, &["rev-parse", "HEAD"]);
    // others land a crate's edit; the release brings the tree to it, so the tree's HEAD at the next handout says nothing moved
    commit(&root, "rust/a/src/lib.rs", "//! x\n");
    run(&words(&["release", "T01", "9001"]), &root, &e);
    assert_eq!(
        git(&b1, &["rev-parse", "HEAD"]),
        git(&root, &["rev-parse", "HEAD"])
    );
    let warm = run(&words(&["take", "T02", "9001"]), &root, &e);
    assert_eq!(
        (warm.code, warm.stdout.as_str()),
        (0, format!("{}\n", b1.display()).as_str())
    );
    let log = root.join(".git/worktrees/repo-b1/prewarm.log");
    assert!(warm.stderr.contains(&format!("builder-tree: pre-warming it in the background - the test builds of the crates moved since its last handout ({}); log {} (L7R_PREWARM=0 for none)", &first[..10], log.display())), "{}", warm.stderr);
    assert_eq!(prewarms(&root), 1);
    // the tree's own gate was started in the tree, told the commit, and was not waited for
    let marker = dir.join("repo-b1.prewarm");
    let began = std::time::Instant::now();
    while std::fs::read_to_string(&marker)
        .unwrap_or_default()
        .is_empty()
    {
        assert!(began.elapsed().as_secs() < 60);
        std::thread::sleep(std::time::Duration::from_millis(5));
    }
    assert_eq!(
        std::fs::read_to_string(&marker).unwrap(),
        format!("rust prewarm --since {first} in {}\n", b1.display())
    );
    assert!(log.is_file());
    // a handout after commits that moved no crate's build starts none
    commit(&root, "docs/a.md", "words\n");
    run(&words(&["release", "T02", "9001"]), &root, &e);
    let same = run(&words(&["take", "T03", "9001"]), &root, &e);
    assert!(same.stderr.contains("builder-tree: nothing to pre-warm - no crate's build moved since the tree's last handout ("), "{}", same.stderr);
    assert_eq!(prewarms(&root), 1);
    // off at the knob: none, whatever moved
    commit(&root, "rust/a/src/lib.rs", "//! y\n");
    run(&words(&["release", "T03", "9001"]), &root, &e);
    e.prewarm = false;
    let off = run(&words(&["take", "T04", "9001"]), &root, &e);
    assert!(
        off.code == 0
            && off
                .stderr
                .contains("builder-tree: no pre-warm (L7R_PREWARM=0)"),
        "{}",
        off.stderr
    );
    assert_eq!(prewarms(&root), 1);
    e.prewarm = true;
    // a tree with no handout on record is measured from where it stood: brought on by its release, nothing
    commit(&root, "rust/a/src/lib.rs", "//! z\n");
    run(&words(&["release", "T04", "9001"]), &root, &e);
    std::fs::remove_file(root.join(".git/worktrees/repo-b1/prewarm-base")).unwrap();
    let unknown = run(&words(&["take", "T05", "9001"]), &root, &e);
    assert!(
        unknown.stderr.contains("nothing to pre-warm"),
        "{}",
        unknown.stderr
    );
    // a pre-warm that cannot start - the tree has no gate wrapper - fails no handout
    std::fs::remove_file(root.join("scripts/gates/l7r-gate.sh")).unwrap();
    git(&root, &["add", "-A"]);
    commit(&root, "rust/a/src/lib.rs", "//! w\n");
    run(&words(&["release", "T05", "9001"]), &root, &e);
    let broken = run(&words(&["take", "T06", "9001"]), &root, &e);
    assert_eq!(
        (broken.code, broken.stdout.as_str()),
        (0, format!("{}\n", b1.display()).as_str())
    );
    assert!(
        broken
            .stderr
            .contains("builder-tree: its pre-warm did not start (")
            && broken.stderr.contains("the handout stands"),
        "{}",
        broken.stderr
    );
    assert_eq!(prewarms(&root), 1);
}

#[test]
fn a_handout_asks_for_the_clone_s_sampler_and_never_fails_on_it() {
    let (dir, root) = world("pool-sampler");
    let mut e = env(&dir);
    // the gate's `measure sampler start`, stood in for: it says where it ran, on standard error, and fails
    let stub = dir.join("sampler-start");
    write_executable(
        &stub,
        "#!/bin/sh\necho \"sampler: asked with $* in $(pwd)\" >&2\nexit 1\n",
    );
    e.sampler = words(&[&stub.to_string_lossy(), "measure", "sampler", "start"]);
    let first = run(&words(&["take", "T01", "9001-x"]), &root, &e);
    let said = format!(
        "sampler: asked with measure sampler start in {}\n",
        root.display()
    );
    assert_eq!(first.code, 0);
    assert!(first.stderr.ends_with(&said), "{}", first.stderr);
    // a handout that is refused asks for none
    let none = run(&words(&["take", "T02", ""]), &root, &e);
    assert_eq!((none.code, none.stderr.contains("sampler:")), (2, false));
    // a program that is not there: said, and the handout stands
    e.sampler = words(&["/no/such/gate"]);
    let again = run(&words(&["take", "T01", "9001"]), &root, &e);
    assert_eq!(again.code, 0);
    let not_asked = "the memory sampler was not asked for (/no/such/gate: ";
    assert!(again.stderr.contains(not_asked));
    // the words: the gate binary's own `measure sampler start`; none at the knob's 0 or with no binary known
    let gate = || Some(std::path::PathBuf::from("/x/l7r-gate"));
    let asked = super::sampler_words(gate(), "");
    assert_eq!(
        asked,
        words(&["/x/l7r-gate", "measure", "sampler", "start"])
    );
    assert_eq!(super::sampler_words(gate(), "1"), asked);
    assert!(super::sampler_words(gate(), "0").is_empty());
    assert!(super::sampler_words(None, "").is_empty());
}

#[test]
fn a_warm_handout_empties_the_tree_s_store_of_rendered_messages() {
    // 451 T486: a pool tree's `<git dir>/hooks-test/messages` outlived its handout, so `make guard-messages` there named wordings its
    // new HEAD does not render (T485's two keys, a pre-T282 wording; t269's nine of T483's uncarried edit)
    let (dir, root) = world("pool-messages");
    let e = env(&dir);
    let b1 = dir.join("repo-b1");
    assert_eq!(run(&words(&["take", "T01", "9001-x"]), &root, &e).code, 0);
    let store = super::tree_git_dir(&b1).join("hooks-test/messages");
    put(
        &store,
        "escalation-hooks.sh.jsonl",
        "{\"key\": \"a01405381091d548\"}\n",
    );
    assert_eq!(run(&words(&["release", "T01", "9001"]), &root, &e).code, 0);
    assert_eq!(run(&words(&["take", "T02", "9001-x"]), &root, &e).code, 0);
    assert!(!store.join("escalation-hooks.sh.jsonl").exists());
}
