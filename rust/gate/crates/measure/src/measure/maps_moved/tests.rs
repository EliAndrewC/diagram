//! "Did my change move this map's drawing, against HEAD?" (feature 429, its ground moved by 449 T230): a tree's drawing - the generation
//! cache's entry and the artifacts in the map's folder - set beside the mirror's, which `render-sync` drew at the mirror's HEAD, wherever
//! HEAD's inputs for the map are the mirror's. Each fixture is a mirror with a clone under its `.clones/`, the real cache's `is_current`
//! asked of each through a stand-in launcher that names one stand-in engine binary.

use std::fmt::Write as _;
use std::os::unix::fs::MetadataExt as _;
use std::path::{Path, PathBuf};

use l7r_gate_pool::cache::entry::{Artifact, Meta, Record};
use l7r_gate_pool::cache::stat::stat;
use l7r_gate_pool::cache::{engine, table, DIR, ENTRIES, TABLE};

use super::cli;
use crate::write_executable;

fn git(dir: &Path, args: &[&str]) {
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(args)
        .output()
        .unwrap();
    let said = String::from_utf8_lossy(&done.stderr);
    assert!(done.status.success(), "{said}");
}

fn put(root: &Path, rel: &str, text: &str) {
    let at = root.join(rel);
    std::fs::create_dir_all(at.parent().unwrap()).unwrap();
    std::fs::write(at, text).unwrap();
}

fn commit(root: &Path, what: &str) {
    git(root, &["add", "-A"]);
    git(root, &["commit", "-qm", what]);
}

/// A mirror and its clone: (the scratch directory, the mirror, the clone). The launcher both trees run (`scripts/gates/l7r-gate.sh`)
/// names one stand-in binary for either engine, as a fresh engine's launcher does under `L7R_GATE_PRINT_FRESH=1`.
fn trees(tag: &str) -> (l7r_shared::tempdir::TempDir, PathBuf, PathBuf) {
    let tmp = crate::checks::scratch(tag);
    let main = tmp.join("diagram");
    std::fs::create_dir_all(&main).unwrap();
    git(&main, &["init", "-q"]);
    git(&main, &["config", "user.email", "t@t"]);
    git(&main, &["config", "user.name", "t"]);
    std::fs::write(tmp.join("engine.bin"), "a stand-in engine").unwrap();
    put(
        &main,
        ".gitignore",
        ".clones/\n.gencache/\npool/*/*/*.driver.svg\npool/*/*/*.driver.json\npool/*/*/*.png\npool/*/*/*.html\nuntracked.md\n",
    );
    put(&main, "rust/phases/src/lib.rs", "pub fn stage() {}\n");
    put(&main, "l7r/assets/door.md", "a door\n");
    for m in ["sawada", "inashiro"] {
        put(
            &main,
            &format!("pool/hamlets/{m}/{m}.spec.json"),
            "{\"seed\": 1}\n",
        );
        // the deleted Python's manifest, tracked and never rewritten: the comparison this replaced read it
        put(
            &main,
            &format!("pool/hamlets/{m}/{m}.json"),
            "{\"board\": 0}\n",
        );
    }
    put(
        &main,
        "pool/magistracies/office/office.compound.json",
        "{\"program\": 1}\n",
    );
    std::fs::create_dir_all(main.join("scripts/gates")).unwrap();
    write_executable(
        &main.join("scripts/gates/l7r-gate.sh"),
        &format!(
            "#!/bin/sh\nprintf '%s\\n' '{}'\n",
            tmp.join("engine.bin").display()
        ),
    );
    commit(&main, "a");
    let clone = main.join(".clones/c");
    git(
        &main,
        &["clone", "-q", &main.display().to_string(), ".clones/c"],
    );
    (tmp, main, clone)
}

/// The stand-in binary `root`'s launcher names.
fn bin(root: &Path) -> PathBuf {
    let script = std::fs::read_to_string(root.join("scripts/gates/l7r-gate.sh")).unwrap();
    PathBuf::from(script.split('\'').nth(3).unwrap())
}

/// `map` (`<tier>/<name>`) drawn in `root` as the cache publishes it: its artifacts in the map's folder, its entry's meta naming them and
/// the engine, and the read table holding `reads` (each a path the engine read, from the root), the map named in each.
fn draw(root: &Path, map: &str, artifacts: &[(&str, &str)], reads: &[&str], skip_render: bool) {
    let name = map.rsplit('/').next().unwrap();
    let dir = root.join("pool").join(map);
    let spec = ["spec.json", "compound.json"]
        .iter()
        .map(|s| dir.join(format!("{name}.{s}")))
        .find(|p| p.exists())
        .unwrap();
    let mut listed = Vec::new();
    for (file, body) in artifacts {
        std::fs::write(dir.join(file), body).unwrap();
        let md = std::fs::metadata(dir.join(file)).unwrap();
        listed.push(Artifact {
            name: (*file).to_owned(),
            size: md.size(),
            mtime: i128::from(md.mtime()) * 1_000_000_000 + i128::from(md.mtime_nsec()),
            ino: md.ino(),
        });
    }
    let meta = Meta {
        engine: "hamlet".to_owned(),
        engine_id: engine::identity(&bin(root)).unwrap().0,
        skip_render,
        spec: Record {
            path: spec.display().to_string(),
            stat: stat(&spec),
            hashed: 0,
            digest: l7r_shared::sha256::hex(&std::fs::read(&spec).unwrap()),
        },
        artifacts: listed,
        key: "k".to_owned(),
        reads: reads.len(),
    };
    let entry = root.join(DIR).join(ENTRIES).join(map);
    std::fs::create_dir_all(&entry).unwrap();
    std::fs::write(entry.join("meta.json"), meta.json()).unwrap();
    let mut text = format!("{}\n", table::HEADER);
    for read in reads {
        let at = root.join(read);
        let cells = stat(&at).cells().join("\t");
        let digest = l7r_shared::sha256::hex(&std::fs::read(&at).unwrap());
        let _ = writeln!(text, "r\t{read}\t{cells}\t0\t{digest}\t{map}");
    }
    // a font the Mode A raster loads: a system file, the same file for both trees, never compared
    let _ = writeln!(text, "f\t/usr/share/fonts/none.ttf\t-\t-\t-\t-\t0\t\t{map}");
    std::fs::write(root.join(DIR).join(TABLE), text).unwrap();
}

fn hamlet(root: &Path, map: &str, body: &str) {
    let name = map.rsplit('/').next().unwrap();
    draw(
        root,
        map,
        &[
            (&format!("{name}.driver.json"), body),
            (&format!("{name}.driver.svg"), "<svg/>"),
        ],
        &[],
        false,
    );
}

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn holds(out: &str, want: &str) {
    assert!(out.contains(want), "{out}");
}

fn only(clone: &Path, map: &str) -> String {
    let got = cli(&words(&["--only", map]), clone);
    assert_eq!(got.code, 0, "{}", got.stderr);
    got.stdout
}

/// RED FIRST (449 T230): the comparison read the tracked `<name>.json`, which the Rust driver never rewrites, so a hamlet whose drawing
/// moved was reported unchanged.
#[test]
fn a_hamlet_whose_drawing_changed_is_reported_moved() {
    let (_tmp, main, clone) = trees("mm-moved");
    hamlet(&main, "hamlets/sawada", "{\"board\": 0}");
    hamlet(&clone, "hamlets/sawada", "{\"board\": 76.4}");
    assert_eq!(
        only(&clone, "sawada"),
        "moved against HEAD: pool/hamlets/sawada (sawada.driver.json)\n"
    );
}

#[test]
fn a_drawing_the_same_as_the_mirrors_is_unchanged() {
    let (_tmp, main, clone) = trees("mm-same");
    hamlet(&main, "hamlets/sawada", "{\"board\": 0}");
    hamlet(&clone, "hamlets/sawada", "{\"board\": 0}");
    // an engine edit not yet committed is this tree's drawing, not HEAD's: HEAD's inputs are still the mirror's
    put(&clone, "rust/phases/src/lib.rs", "pub fn stage() { }\n");
    for named in [
        "pool/hamlets/sawada",
        "sawada",
        "pool/hamlets/sawada/sawada.spec.json",
    ] {
        assert_eq!(
            only(&clone, named),
            "unchanged against HEAD: pool/hamlets/sawada\n"
        );
    }
}

/// Every way of not knowing says so: it never reads as unchanged.
#[test]
fn what_it_cannot_tell_is_not_compared_never_unchanged() {
    let (_tmp, main, clone) = trees("mm-cannot");
    let says = |clone: &Path, why: &str| {
        let out = only(clone, "sawada");
        holds(
            &out[..out.len().min(36)],
            "NOT COMPARED: pool/hamlets/sawada - ",
        );
        holds(&out, why);
    };
    says(
        &clone,
        "this tree has not drawn it - `make map MAP=pool/hamlets/sawada` draws it",
    );
    hamlet(&clone, "hamlets/sawada", "{\"board\": 1}");
    says(&clone, "the mirror has not drawn it");
    hamlet(&main, "hamlets/sawada", "{\"board\": 0}");
    // the spec edited after the draw: this tree's drawing is not of its spec
    put(
        &clone,
        "pool/hamlets/sawada/sawada.spec.json",
        "{\"seed\": 2}\n",
    );
    says(
        &clone,
        "this tree's drawing is not current - `make map MAP=pool/hamlets/sawada` draws it again",
    );
    hamlet(&clone, "hamlets/sawada", "{\"board\": 1}");
    assert!(only(&clone, "sawada").starts_with("moved against HEAD"));
    // the mirror's artifact rewritten after its entry was published: the folder's file is not the entry's
    put(
        &main,
        "pool/hamlets/sawada/sawada.driver.json",
        "{\"board\": 0}",
    );
    says(&clone, "the mirror's drawing of it is not current");
    hamlet(&main, "hamlets/sawada", "{\"board\": 0}");
    // the clone's commit of its spec: HEAD's spec is not the mirror's, so the mirror's drawing is not HEAD's
    commit(&clone, "spec");
    hamlet(&clone, "hamlets/sawada", "{\"board\": 1}");
    says(
        &clone,
        "HEAD's pool/hamlets/sawada/sawada.spec.json is not the mirror's",
    );
    says(&clone, "drawing HEAD's engines in a worktree");
}

#[test]
fn heads_engine_not_the_mirrors_compares_nothing() {
    let (_tmp, main, clone) = trees("mm-engine");
    hamlet(&main, "hamlets/sawada", "{\"board\": 0}");
    put(
        &clone,
        "rust/phases/src/lib.rs",
        "pub fn stage() { let _ = 1; }\n",
    );
    commit(&clone, "engine");
    hamlet(&clone, "hamlets/sawada", "{\"board\": 0}");
    let out = only(&clone, "sawada");
    holds(
        &out[..out.len().min(36)],
        "NOT COMPARED: pool/hamlets/sawada - ",
    );
    holds(
        &out,
        "HEAD's engine sources (rust/) are not the mirror's (at ",
    );
}

#[test]
fn a_mirror_with_tracked_files_moved_compares_nothing() {
    let (_tmp, main, clone) = trees("mm-dirty");
    hamlet(&main, "hamlets/sawada", "{\"board\": 0}");
    hamlet(&clone, "hamlets/sawada", "{\"board\": 0}");
    put(
        &main,
        "rust/phases/src/lib.rs",
        "pub fn stage() { let _ = 2; }\n",
    );
    let out = only(&clone, "sawada");
    holds(
        &out,
        "the mirror's tracked files are not its HEAD's (M rust/phases/src/lib.rs)",
    );
}

#[test]
fn the_mirror_itself_and_a_tree_with_no_mirror_compare_nothing() {
    let (_tmp, main, _clone) = trees("mm-self");
    hamlet(&main, "hamlets/sawada", "{\"board\": 0}");
    let out = only(&main, "sawada");
    holds(&out, "this tree is the mirror");
    let got = cli(
        &words(&["--root", &main.display().to_string(), "--only", "sawada"]),
        Path::new("/nonexistent"),
    );
    holds(&got.stdout, "this tree is the mirror");
    // a clone whose mirror is not a repository
    let lone = crate::checks::scratch("mm-lone");
    let inner = lone.join(".clones/c");
    git(
        &main,
        &[
            "clone",
            "-q",
            &main.display().to_string(),
            &inner.display().to_string(),
        ],
    );
    hamlet(&inner, "hamlets/sawada", "{\"board\": 0}");
    let out = only(&inner, "sawada");
    holds(&out, "no mirror at");
}

#[test]
fn a_map_head_does_not_have_has_moved() {
    let (_tmp, _main, clone) = trees("mm-new");
    put(
        &clone,
        "pool/hamlets/kuwabata/kuwabata.spec.json",
        "{\"seed\": 9}\n",
    );
    hamlet(&clone, "hamlets/kuwabata", "{}");
    assert_eq!(
        only(&clone, "kuwabata"),
        "moved against HEAD: pool/hamlets/kuwabata (a map HEAD does not have)\n"
    );
}

/// A sheet's reads are HEAD's inputs too: one HEAD holds otherwise than the mirror, or one git does not hold, and the mirror's drawing is
/// not HEAD's; a picture skipped on one side is compared by what both drew.
#[test]
fn a_sheets_reads_and_a_skipped_picture() {
    let (_tmp, main, clone) = trees("mm-sheet");
    let office = "magistracies/office";
    let page = [
        ("office.svg", "<svg/>"),
        ("office.html", "<p/>"),
        ("office.png", "png"),
    ];
    draw(&main, office, &page, &["l7r/assets/door.md"], false);
    draw(&clone, office, &page[..1], &["l7r/assets/door.md"], true);
    assert_eq!(
        only(&clone, "office"),
        "unchanged against HEAD: pool/magistracies/office\n"
    );
    draw(
        &clone,
        office,
        &[("office.svg", "<svg>moved</svg>")],
        &["l7r/assets/door.md"],
        true,
    );
    assert_eq!(
        only(&clone, "office"),
        "moved against HEAD: pool/magistracies/office (office.svg)\n"
    );
    // the same switch on both sides: a picture one side lacks is a move
    draw(&clone, office, &page[..2], &["l7r/assets/door.md"], false);
    assert_eq!(
        only(&clone, "office"),
        "moved against HEAD: pool/magistracies/office (office.png)\n"
    );
    put(&main, "untracked.md", "a read git does not hold\n");
    draw(
        &main,
        office,
        &page,
        &["l7r/assets/door.md", "untracked.md"],
        false,
    );
    draw(&clone, office, &page, &["l7r/assets/door.md"], false);
    let out = only(&clone, "office");
    holds(&out, "it reads untracked.md, which git does not track");
    put(&clone, "l7r/assets/door.md", "a door, moved\n");
    commit(&clone, "a read");
    draw(&main, office, &page, &["l7r/assets/door.md"], false);
    draw(&clone, office, &page, &["l7r/assets/door.md"], false);
    let out = only(&clone, "office");
    holds(&out, "HEAD's l7r/assets/door.md is not the mirror's");
}

#[test]
fn every_live_map_and_a_summary() {
    let (_tmp, main, clone) = trees("mm-all");
    hamlet(&main, "hamlets/sawada", "{\"board\": 0}");
    hamlet(&clone, "hamlets/sawada", "{\"board\": 76.4}");
    hamlet(&main, "hamlets/inashiro", "{}");
    hamlet(&clone, "hamlets/inashiro", "{}");
    std::fs::create_dir_all(clone.join("legacy-hand-authored-pool/hamlets/old")).unwrap();
    put(
        &clone,
        "legacy-hand-authored-pool/hamlets/old/old.json",
        "{}",
    );
    let got = cli(&[], &clone);
    assert_eq!(
        got.stdout,
        "unchanged against HEAD: pool/hamlets/inashiro\n\
         moved against HEAD: pool/hamlets/sawada (sawada.driver.json)\n\
         NOT COMPARED: pool/magistracies/office - this tree has not drawn it - `make map MAP=pool/magistracies/office` draws it\n\
         maps-moved: 1 moved, 1 unchanged, 1 not compared, against the mirror's drawing of HEAD\n"
    );
    assert_eq!(
        only(&clone, "legacy-hand-authored-pool/hamlets/old"),
        "NOT COMPARED: legacy-hand-authored-pool/hamlets/old - a frozen exhibit, never drawn again\n"
    );
    let got = cli(&words(&["--only", "nosuch"]), &clone);
    assert_eq!(got.code, 2);
    holds(&got.stderr, "no pool map is named nosuch");
}
