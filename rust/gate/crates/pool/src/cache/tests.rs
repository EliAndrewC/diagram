//! The generation cache on a fixture pool with stand-in engines (feature 449 T221): shell scripts that draw as the engines do - into the
//! staging folder `--out` names, the Mode A one replying with the reads a fixture file lists - so no test builds an engine.
//!
//! Research: the cache's tests - NONE: fixtures and assertions, deciding nothing about a map

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use super::engine::{Binaries, Engine};
use super::{is_current, run, Options, Outcome, Verdict, DIR, TABLE};
use crate::counts::Counts;
use crate::walk::tests::{put, TYPES};
use crate::walk::{walk, Map, DECLARATION, LIVE};

/// The stand-in Mode A engine: `hand-sheet|compound <spec> --out <dir>`. It reads each path `engine-reads` lists, then does what
/// `engine-mode` says (`refuse`, `census`, `nopng`, `touch:<path>` - append to a read while it runs - or nothing), writes the page,
/// the picture (none where `skip` exists) and, a compound, the sheet, and replies with its reads and the spec.
const MODE_A: &str = r#"#!/bin/sh
T=$L7R_GATE_TREE; cmd=$1; spec=$2; out=$4
mode=$(cat "$T/engine-mode" 2>/dev/null)
base=$(basename "$spec"); name=${base%.compound.json}; name=${name%.svg}
if [ "$mode" = refuse ]; then echo '{"error": {"kind": "ValueError", "message": "no"}}'; echo "ValueError: no" >&2; exit 1; fi
reads=""
IFS='
'
for p in $(cat "$T/engine-reads" 2>/dev/null); do cat "$p" >/dev/null 2>&1; reads="$reads\"$(printf '%s' "$p" | sed 's/\t/\\t/g')\", "; done
case "$mode" in touch:*) printf 'more' >> "${mode#touch:}";; esac
echo html > "$out/$name.html"
[ "$mode" = nopng ] || [ -e "$T/skip" ] || echo png > "$out/$name.png"
[ "$cmd" = compound ] && echo svg > "$out/$name.svg"
printf '%s\n' "{\"counts\": [], \"reads\": [$reads\"$spec\"]}"
if [ "$mode" = census ]; then echo "$name.svg: untagged ink ['x']; unknown kinds []" >&2; exit 1; fi
exit 0
"#;

/// The stand-in hamlet driver: `<spec>`, its map and record written beside it; `engine-mode` `refuse` exits 1, `hamlet-touch:<path>`
/// appends to a file (a read of the sheets drawn around it) and waits out the clock's tick.
const HAMLET: &str = r#"#!/bin/sh
mode=$(cat "$L7R_GATE_TREE/engine-mode" 2>/dev/null)
[ "$mode" = refuse ] && { echo "hamlet: no" >&2; exit 1; }
case "$mode" in hamlet-touch:*) printf 'more' >> "${mode#hamlet-touch:}"; sleep 0.02;; esac
d=$(dirname "$1"); echo svg > "$d/h.driver.svg"; echo json > "$d/h.driver.json"; echo "hamlet: rolled"
"#;

/// The stand-in engines, by path; an engine with none cannot be named.
pub(crate) struct Stand(pub BTreeMap<Engine, PathBuf>);

impl Binaries for Stand {
    fn binary(&mut self, e: Engine) -> Result<PathBuf, String> {
        self.0
            .get(&e)
            .cloned()
            .ok_or_else(|| format!("no {} engine", e.word()))
    }
}

/// A fixture pool: a hamlet, a compound, two hand sheets, a frozen exhibit and an unclassified folder; the stand-in engines; a read
/// the sheets share; a font root.
pub(crate) struct Fixture {
    /// held so the scratch tree outlives the test
    pub _held: l7r_shared::tempdir::TempDir,
    pub root: PathBuf,
    pub stand: Stand,
}

pub(crate) fn fixture(tag: &str) -> Fixture {
    let dir = l7r_shared::tempdir::TempDir::new(&format!("cache-{tag}"));
    let root = std::fs::canonicalize(dir.path()).unwrap();
    put(&root, DECLARATION, TYPES);
    for (rel, text) in [
        ("pool/hamlets/h/h.spec.json", "{\"name\": \"H\"}"),
        ("pool/magistracies/c/c.compound.json", "{}"),
        ("pool/magistracies/s/s.svg", "<svg/>"),
        ("pool/magistracies/t/t.svg", "<svg/>"),
        ("legacy-hand-authored-pool/villages/v/v.json", "{}"),
        ("legacy-hand-authored-pool/magistracies/x/x.svg", "<svg/>"),
        ("pool/magistracies/u/stray.txt", "x"),
        ("assets/page.css", "css"),
        ("fonts/a.ttf", "font"),
        ("engines/mode-a", MODE_A),
        ("engines/hamlet", HAMLET),
    ] {
        put(&root, rel, text);
    }
    for e in ["mode-a", "hamlet"] {
        let p = root.join("engines").join(e);
        std::fs::set_permissions(&p, std::os::unix::fs::PermissionsExt::from_mode(0o755)).unwrap();
    }
    put(
        &root,
        "engine-reads",
        &format!("{}\n", root.join("assets/page.css").display()),
    );
    tick(&root);
    let stand = Stand(BTreeMap::from([
        (Engine::ModeA, root.join("engines/mode-a")),
        (Engine::Hamlet, root.join("engines/hamlet")),
    ]));
    Fixture {
        _held: dir,
        root,
        stand,
    }
}

impl Fixture {
    pub(crate) fn opts(&self) -> Options {
        Options {
            skip_render: self.root.join("skip").exists(),
            font_roots: vec![self.root.join("fonts"), self.root.join("no-fonts")],
            // A FORKED CHILD HOLDS THE LOCK A MOMENT (449 T222's gate, 2026-11-19): another test's spawn forks while this one's lock file
            // is open, and the child holds that open file until it execs, so a run taking the lock again in that window was refused at a
            // 0 s wait - twice in the loaded counting build, never alone; the held-lock test asks for 0 s itself
            lock_wait: 10.0,
        }
    }

    /// The maps named, from a fresh walk.
    pub(crate) fn maps(&self, names: &[&str]) -> Vec<Map> {
        let w = walk(&self.root);
        names.iter().map(|n| w.folder(n).unwrap().clone()).collect()
    }

    /// One run over the maps named (every live map: `every`), each outcome's verdict, and the counts.
    pub(crate) fn run(
        &mut self,
        names: &[&str],
        every: bool,
    ) -> (Vec<Verdict>, Counts, Vec<Outcome>) {
        let maps = self.maps(names);
        let mut counts = Counts::default();
        let opts = self.opts();
        let out = run(&self.root, &maps, every, &mut self.stand, &mut counts, opts).unwrap();
        (out.iter().map(|o| o.verdict.clone()).collect(), counts, out)
    }

    pub(crate) fn verdicts(&mut self, names: &[&str]) -> Vec<Verdict> {
        self.run(names, false).0
    }

    pub(crate) fn current(&mut self, name: &str) -> bool {
        let m = self.maps(&[name]).remove(0);
        let skip = self.opts().skip_render;
        is_current(&self.root, &m, &mut self.stand, skip)
    }

    pub(crate) fn mode(&self, mode: &str) {
        put(&self.root, "engine-mode", mode);
    }

    /// A file rewritten, and the filesystem's clock waited past it.
    pub(crate) fn edit(&self, rel: &str, text: &str) {
        put(&self.root, rel, text);
        tick(&self.root);
    }
}

/// The filesystem's clock waited out to its next tick: a file written before is settled against any time taken after (its timestamps are
/// the kernel's coarse clock, a tick of a few milliseconds).
pub(crate) fn tick(root: &Path) {
    let probe = root.join(".tick");
    let start = super::stat::fs_clock(&probe).unwrap();
    while super::stat::fs_clock(&probe).unwrap() <= start {
        std::thread::sleep(std::time::Duration::from_millis(1));
    }
}

/// The file's stat moved with its content kept: its mtime set long ago (its ctime moves to now), and the clock waited past it.
pub(crate) fn touch(root: &Path, p: &Path) {
    let then = std::time::UNIX_EPOCH + std::time::Duration::from_secs(1_000_000_000);
    std::fs::File::options()
        .write(true)
        .open(p)
        .unwrap()
        .set_modified(then)
        .unwrap();
    tick(root);
}

fn regenerated(v: &Verdict) -> bool {
    matches!(v, Verdict::Regenerated(_))
}

fn why(v: &Verdict) -> String {
    match v {
        Verdict::Regenerated(w) | Verdict::Unpublished(w) | Verdict::Failed(w) => w.clone(),
        _ => String::new(),
    }
}

/// Every live kind drawn on a cold run, published, and linked into its folder; the next run serves each from the cache; a frozen
/// exhibit is FROZEN and an unclassified folder fails, both never keyed.
#[test]
fn a_cold_run_draws_every_kind_and_the_next_serves_them() {
    let mut f = fixture("cold");
    let names = ["h", "c", "s", "v", "u", "x"];
    let (v, _, _) = f.run(&names, false);
    assert!(v[..3].iter().all(regenerated), "{v:?}");
    assert_eq!(v[3], Verdict::Frozen);
    // a legacy folder's svg in a declared tier is an exhibit too: never drawn
    assert_eq!(v[5], Verdict::Frozen);
    assert!(why(&v[4]).contains("no map the pool walk can classify"));
    for p in [
        "hamlets/h/h.driver.svg",
        "magistracies/c/c.svg",
        "magistracies/c/c.png",
        "magistracies/s/s.html",
    ] {
        assert!(f.root.join("pool").join(p).is_file(), "{p}");
    }
    assert!(f
        .root
        .join(DIR)
        .join("staging")
        .read_dir()
        .unwrap()
        .next()
        .is_none());
    let (v, _, _) = f.run(&names[..3], false);
    assert_eq!(v, [Verdict::Cached, Verdict::Cached, Verdict::Cached]);
    assert!(f.current("s") && f.current("h"));
}

/// THE WARM ALL-HIT RUN (the derivation's counted run): every row held by its stat, nothing hashed, each kind counted as the derivation
/// prices it - 3 a row, 2 a live map, 3 a spec, 3 an artifact.
#[cfg(feature = "counters")]
#[test]
fn the_warm_run_holds_every_row_by_its_stat_and_hashes_nothing() {
    let mut f = fixture("warm");
    let live = ["h", "c", "s", "t"];
    f.run(&live, true);
    let (v, counts, _) = f.run(&live, true);
    assert!(v.iter().all(|v| *v == Verdict::Cached), "{v:?}");
    let k: BTreeMap<&str, u64> = counts.of(LIVE).into_iter().collect();
    // rows: page.css and the font set's 3 (the root, a.ttf, the root not there)
    let rows = 4;
    let artifacts = 2 + 3 + 2 + 2;
    // the stand-in engines are scripts with no build-id note, so each is hashed whole once a run (a real engine's id is its note: 0)
    let script_blocks: u64 = ["engines/mode-a", "engines/hamlet"]
        .iter()
        .map(|e| {
            std::fs::metadata(f.root.join(e))
                .unwrap()
                .len()
                .div_ceil(64)
        })
        .sum();
    assert_eq!(k["hash_block"], script_blocks);
    assert_eq!((k["lock"], k["file_read"], k["engine_id"]), (1, 1, 2));
    assert_eq!((k["meta_read"], k["id_compare"]), (4, 4));
    assert_eq!(k["record"], rows + 4 + artifacts);
    assert_eq!(k["stat"], rows + 4 + artifacts);
    assert_eq!(k["stat_compare"], k["stat"]);
    assert_eq!(
        k["list_read"] + k["engine_run"] + k["rename"] + k["link"],
        0
    );
}

/// A MISS IS A READ (T219's derivation, assumption 3): a file the engine looked for and did not find, created later, regenerates the
/// sheet - and the read the sheets share, changed, regenerates them both, a single map's run removing the other's entry too (Keep 3).
#[test]
fn a_looked_for_file_created_later_and_a_shared_read_changed_regenerate() {
    let mut f = fixture("miss");
    let notes = f.root.join("pool/magistracies/s/s.notes.md");
    put(
        &f.root,
        "engine-reads",
        &format!(
            "{}\n{}\n",
            f.root.join("assets/page.css").display(),
            notes.display()
        ),
    );
    f.run(&["s", "t"], false);
    assert_eq!(f.verdicts(&["s"]), [Verdict::Cached]);
    f.edit("pool/magistracies/s/s.notes.md", "# notes\n");
    assert!(!f.current("s"));
    let v = f.verdicts(&["s"]);
    assert!(why(&v[0]).contains("s.notes.md changed"), "{v:?}");
    // t looked for s's notes too (the same reads listed): its entry went with the row
    f.edit("assets/page.css", "css 2");
    assert!(!f.current("t"));
    let v = f.verdicts(&["s"]);
    assert!(why(&v[0]).contains("assets/page.css changed"), "{v:?}");
    let v = f.verdicts(&["t"]);
    assert!(regenerated(&v[0]), "{v:?}");
    assert_eq!(f.verdicts(&["s", "t"]), [Verdict::Cached, Verdict::Cached]);
}

/// A file whose stat moved and whose content did not is re-hashed and its row refreshed, the map served; the spec the same; a spec edit
/// alone re-keys its map (Keep 8).
#[test]
fn a_touched_file_is_rehashed_and_served_and_a_spec_edit_regenerates() {
    let mut f = fixture("touch");
    f.run(&["c", "h"], false);
    touch(&f.root, &f.root.join("assets/page.css"));
    touch(&f.root, &f.root.join("pool/magistracies/c/c.compound.json"));
    assert!(f.current("c"));
    assert_eq!(f.verdicts(&["c"]), [Verdict::Cached]);
    let table = std::fs::read_to_string(f.root.join(DIR).join(TABLE)).unwrap();
    assert!(table.contains("assets/page.css"));
    f.edit(
        "pool/hamlets/h/h.spec.json",
        "{\"name\": \"H\", \"seed\": 2}",
    );
    assert!(!f.current("h"));
    let v = f.verdicts(&["h", "c"]);
    assert_eq!(why(&v[0]), "its spec changed");
    assert_eq!(v[1], Verdict::Cached);
}

/// A new engine binary, or the picture switch thrown, regenerates; an engine that cannot be named draws nothing and is not current.
#[test]
fn the_engine_and_the_picture_switch_key_the_map() {
    let mut f = fixture("engine");
    f.run(&["s"], false);
    f.edit("engines/mode-a", &format!("{MODE_A}# rebuilt\n"));
    assert!(!f.current("s"));
    assert_eq!(why(&f.verdicts(&["s"])[0]), "its engine (mode-a) changed");
    put(&f.root, "skip", "");
    let v = f.verdicts(&["s"]);
    assert!(why(&v[0]).contains("picture switch"));
    assert!(!f
        .root
        .join(DIR)
        .join("entries/magistracies/s/s.png")
        .exists());
    assert_eq!(f.verdicts(&["s"]), [Verdict::Cached]);
    f.stand.0.remove(&Engine::ModeA);
    assert!(!f.current("s"));
    assert_eq!(why(&f.verdicts(&["s"])[0]), "no mode-a engine");
}

/// An artifact gone from the map's folder is linked back from the entry and the map served; one edited in place (the entry's own file,
/// a hard link) is no longer the one published, and the map is drawn again.
#[test]
fn a_lost_artifact_is_linked_back_and_an_edited_one_redrawn() {
    let mut f = fixture("artifact");
    f.run(&["s"], false);
    let png = f.root.join("pool/magistracies/s/s.png");
    std::fs::remove_file(&png).unwrap();
    assert!(!f.current("s"));
    assert_eq!(f.verdicts(&["s"]), [Verdict::Cached]);
    assert!(png.is_file() && f.current("s"));
    f.edit("pool/magistracies/s/s.png", "edited");
    let v = f.verdicts(&["s"]);
    assert_eq!(why(&v[0]), "its entry's s.png is not the one published");
    assert_eq!(std::fs::read_to_string(&png).unwrap(), "png\n");
}

/// A READ CHANGED WHILE THE ENGINE RAN (the second judgment on the derivation, 2026-11-19): its digest, taken after the run, is not of the
/// content the map was drawn from, so the entry is not published - the map's folder shows what was drawn, and the next run draws it again.
/// Red first: before the rule, the run published the new content's digest and the next run served the stale map as CACHED.
#[test]
fn a_read_changed_while_the_engine_ran_is_never_recorded() {
    let mut f = fixture("racy");
    let css = f.root.join("assets/page.css");
    f.mode(&format!("touch:{}", css.display()));
    let v = f.verdicts(&["s"]);
    assert!(
        matches!(&v[0], Verdict::Unpublished(w) if w.contains("assets/page.css changed while its engine ran"))
    );
    assert!(f.root.join("pool/magistracies/s/s.html").is_file());
    f.mode("");
    assert_eq!(why(&f.verdicts(&["s"])[0]), "no cache entry");
    assert_eq!(f.verdicts(&["s"]), [Verdict::Cached]);
}

/// An absent read whose directory moved while the engine ran, a spec edited while it ran, and a read the table cannot hold are each not
/// published either.
#[test]
fn an_absence_or_spec_unsettled_or_an_unholdable_read_is_not_published() {
    let mut f = fixture("unsettled");
    let gone = f.root.join("assets/gone.md");
    put(&f.root, "engine-reads", &format!("{}\n", gone.display()));
    f.mode(&format!("touch:{}", f.root.join("assets/new.md").display()));
    assert!(
        matches!(&f.verdicts(&["s"])[0], Verdict::Unpublished(w) if w.contains("assets/gone.md"))
    );
    f.mode(&format!(
        "touch:{}",
        f.root.join("pool/magistracies/s/s.svg").display()
    ));
    assert!(matches!(&f.verdicts(&["s"])[0], Verdict::Unpublished(w) if w.contains("s/s.svg")));
    f.mode("");
    put(
        &f.root,
        "engine-reads",
        &format!("{}\n", f.root.join("assets/a\tb").display()),
    );
    put(&f.root, "assets/a\tb", "x");
    let v = f.verdicts(&["s"]);
    assert!(matches!(&v[0], Verdict::Unpublished(w) if w.contains("a\tb")));
}

/// A refusal, a census that fails (its page linked so its folder shows it) and an artifact the engine owed and did not write each fail
/// the map and publish nothing; a hamlet's refusal too.
#[test]
fn a_refusal_a_failed_census_and_a_missing_artifact_fail_the_map() {
    let mut f = fixture("fail");
    f.mode("refuse");
    let (v, _, out) = f.run(&["s", "h"], false);
    assert!(why(&v[0]).contains("refused") && out[0].said.contains("ValueError: no"));
    assert!(why(&v[1]).contains("refused") && out[1].said.contains("hamlet: no"));
    f.mode("census");
    assert!(why(&f.verdicts(&["s"])[0]).contains("census failed"));
    assert!(f.root.join("pool/magistracies/s/s.html").is_file());
    f.mode("nopng");
    assert_eq!(why(&f.verdicts(&["s"])[0]), "its engine wrote no s.png");
    std::fs::remove_file(f.root.join("pool/magistracies/c/c.compound.json")).unwrap();
    put(&f.root, "pool/magistracies/c/c.compound.json/x", "");
    assert!(why(&f.verdicts(&["c"])[0]).contains("cannot be read"));
    assert!(!f.current("s"));
}

/// The table gone, or not a table, throws every entry away: no entry is trusted whose reads nothing watches.
#[test]
fn no_table_that_reads_throws_every_entry_away() {
    let mut f = fixture("table");
    f.run(&["s"], false);
    std::fs::remove_file(f.root.join(DIR).join(TABLE)).unwrap();
    assert!(!f.current("s"));
    assert_eq!(why(&f.verdicts(&["s"])[0]), "no cache entry");
    std::fs::write(f.root.join(DIR).join(TABLE), "not a table").unwrap();
    assert_eq!(why(&f.verdicts(&["s"])[0]), "no cache entry");
    assert_eq!(f.verdicts(&["s"]), [Verdict::Cached]);
}

/// THE FONT SET: a font added under a root moves its directory's stat, which removes every sheet's entry and walks the set again; a
/// hamlet's run holds no font row.
#[test]
fn a_font_added_regenerates_the_sheets_and_not_the_hamlet() {
    let mut f = fixture("fonts");
    f.run(&["s", "c", "h"], false);
    f.edit("fonts/b.otf", "font b");
    assert!(!f.current("s"));
    let v = f.verdicts(&["h", "s"]);
    assert_eq!(v[0], Verdict::Cached);
    assert_eq!(why(&v[1]), "the font set changed");
    // the compound's entry went with the font rows in the run before
    assert_eq!(why(&f.verdicts(&["c"])[0]), "no cache entry");
    let table = std::fs::read_to_string(f.root.join(DIR).join(TABLE)).unwrap();
    assert!(table.contains("fonts/b.otf"));
    assert_eq!(f.verdicts(&["s", "c"]), [Verdict::Cached, Verdict::Cached]);
}

/// A map drawn earlier in a run whose read a later map's draw finds changed (here by the hamlet drawn between them) has its entry removed
/// before its meta is renamed - so it is not published, and the next run draws it again; the cache's own directory that cannot be made
/// fails the run.
#[test]
fn a_run_publishes_no_entry_it_removed_and_fails_where_it_cannot_write() {
    let mut f = fixture("late");
    f.mode(&format!(
        "hamlet-touch:{}",
        f.root.join("assets/page.css").display()
    ));
    let (v, _, _) = f.run(&["s", "h", "t"], false);
    assert!(v.iter().all(regenerated), "{v:?}");
    assert!(!f
        .root
        .join(DIR)
        .join("entries/magistracies/s/meta.json")
        .exists());
    f.mode("");
    let v = f.verdicts(&["s", "t"]);
    assert_eq!(
        (why(&v[0]).as_str(), &v[1]),
        ("no cache entry", &Verdict::Cached)
    );
    let blocked = fixture("blocked");
    put(
        &blocked.root,
        ".gencache",
        "a file where the cache's directory goes",
    );
    let maps = walk(&blocked.root).maps;
    let mut stand = Stand(BTreeMap::new());
    let err = run(
        &blocked.root,
        &maps,
        true,
        &mut stand,
        &mut Counts::default(),
        Options::default(),
    )
    .unwrap_err();
    assert!(err.contains(".gencache"), "{err}");
    assert!(run(
        Path::new("/no/such/root"),
        &[],
        true,
        &mut stand,
        &mut Counts::default(),
        Options::default()
    )
    .is_err());
}

/// The process's options read the render switch and the font roots; a frozen exhibit has no spec.
#[test]
fn the_options_are_the_processes_and_a_frozen_map_has_no_spec() {
    assert_eq!(Options::current().font_roots, super::fonts::system_roots());
    let frozen = Map {
        tree: LIVE,
        tier: "t".into(),
        name: "n".into(),
        dir: PathBuf::from("/x"),
        files: vec![],
        kind: crate::walk::Kind::Frozen,
    };
    assert_eq!(super::spec_of(&frozen), None);
    assert_eq!(super::map_id(&frozen), "t/n");
}

/// A run waits for another's lock only so long, then says so; a staging folder a crashed run left is cleared before the engine draws
/// into it; a verdict with no reason has none.
#[test]
fn a_held_lock_refuses_and_a_leftover_staging_folder_is_cleared() {
    let mut f = fixture("lock");
    let lock = f.root.join(DIR).join(super::LOCK);
    let held = l7r_shared::tool::flock_within(&lock, 0.0).unwrap().unwrap();
    let maps = f.maps(&["s"]);
    let opts = Options {
        lock_wait: 0.0,
        ..f.opts()
    };
    let err = run(
        &f.root,
        &maps,
        false,
        &mut f.stand,
        &mut Counts::default(),
        opts,
    )
    .unwrap_err();
    assert!(err.contains("another run held the cache's lock past 0 s"));
    drop(held);
    let left = f
        .root
        .join(DIR)
        .join(super::STAGING)
        .join(format!("magistracies--s.{}", std::process::id()));
    put(&left, "stale.png", "old");
    assert!(regenerated(&f.verdicts(&["s"])[0]));
    assert!(!left.exists() && !f.root.join("pool/magistracies/s/stale.png").exists());
    assert_eq!(why(&Verdict::Cached), "");
}
