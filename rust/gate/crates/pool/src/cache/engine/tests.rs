//! The engines' identities and the launcher (feature 449 T221).
//!
//! Research: the engines' tests - NONE: fixtures and assertions, deciding nothing about a map

use std::path::Path;

use super::{gnu_build_id, identity, run, Binaries, Engine, Launcher};
use crate::walk::Kind;

/// This test binary, linked as the engines are, carries a GNU build id; a file with none is hashed whole; one not there is an error;
/// a file shaped like an ELF header that does not hold its notes is no build id.
#[test]
fn a_binary_is_its_build_id_and_any_other_file_its_hash() {
    let me = std::env::current_exe().unwrap();
    let (id, hashed) = identity(&me).unwrap();
    assert!(id.starts_with("gnu:") && id.len() > 20 && hashed == 0);
    let dir = l7r_shared::tempdir::TempDir::new("cache-engine");
    let script = dir.path().join("s");
    std::fs::write(&script, "#!/bin/sh\n").unwrap();
    assert_eq!(
        identity(&script).unwrap(),
        (
            format!("sha256:{}", l7r_shared::sha256::hex(b"#!/bin/sh\n")),
            10
        )
    );
    assert!(identity(&dir.path().join("none")).is_err());
    // an ELF64 header naming one program header past the file's end
    let mut head = vec![0u8; 64];
    head[..6].copy_from_slice(b"\x7fELF\x02\x01");
    head[0x20] = 64;
    head[0x36] = 56;
    head[0x38] = 1;
    let elf = dir.path().join("elf");
    std::fs::write(&elf, &head).unwrap();
    assert_eq!(gnu_build_id(&elf), None);
    // its one header a note past the end; then a note of another kind; then a GNU note cut short
    // two program headers: a load segment, then the notes
    let note = |kind: u8, desc: &[u8], end: usize| {
        let mut b = head.clone();
        b[0x38] = 2;
        let mut load = vec![0u8; 56];
        load[0] = 1;
        b.extend(load);
        let mut ph = vec![0u8; 56];
        ph[0] = 4;
        ph[0x08] = 176;
        ph[0x20] = u8::try_from(end).unwrap();
        b.extend(ph);
        let mut n = vec![
            4,
            0,
            0,
            0,
            u8::try_from(desc.len()).unwrap(),
            0,
            0,
            0,
            kind,
            0,
            0,
            0,
        ];
        n.extend(b"GNU\0");
        n.extend(desc);
        b.extend(n);
        b
    };
    for (kind, desc, end, want) in [
        (3u8, &b"\xab\xcd"[..], 200usize, None),
        (1, b"\xab\xcd\x00\x00", 20, None),
        (3, b"\xab\xcd\x00\x00", 20, Some("abcd0000".to_owned())),
        (3, b"\xab\xcd\x00\x00", 18, None),
    ] {
        std::fs::write(&elf, note(kind, desc, end)).unwrap();
        assert_eq!(gnu_build_id(&elf), want, "{kind} {end}");
    }
    std::fs::write(&elf, b"\x7fELF\x01\x01").unwrap();
    assert_eq!(gnu_build_id(&elf), None);
}

/// Each live kind's engine, and none for a frozen exhibit or an unclassified folder.
#[test]
fn each_live_kind_names_its_engine() {
    assert_eq!(Engine::of(Kind::Hamlet), Some(Engine::Hamlet));
    assert_eq!(Engine::of(Kind::Compound), Some(Engine::ModeA));
    assert_eq!(Engine::of(Kind::HandSheet), Some(Engine::ModeA));
    assert_eq!(Engine::of(Kind::Frozen), None);
    assert_eq!(Engine::of(Kind::Report), None);
    assert_eq!(
        (Engine::Hamlet.word(), Engine::ModeA.word()),
        ("hamlet", "mode-a")
    );
}

/// The launcher is asked for the fresh binary - building it, or with `STALE_OK` building none - and its refusals say which; a binary
/// is run from the root with the tree named to it.
#[test]
fn the_launcher_names_a_fresh_binary_or_says_why_not() {
    let dir = l7r_shared::tempdir::TempDir::new("cache-launcher");
    let root = dir.path();
    let gates = root.join("scripts/gates");
    std::fs::create_dir_all(&gates).unwrap();
    let launcher = gates.join("l7r-gate.sh");
    // written by `install`, never this process: a script it wrote itself can be "Text file busy" when run (451 T160)
    l7r_gate_core::write_executable(
        &launcher,
        "#!/bin/sh\n[ -n \"$L7R_GATE_STALE_OK\" ] && exit 1\n[ \"$1\" = hamlet ] && { echo 'it failed' >&2; exit 1; }\necho \"/bin/$1-$L7R_GATE_PRINT_FRESH\"\n",
    );
    let mut built = Launcher {
        root: root.to_path_buf(),
        build: true,
    };
    assert_eq!(
        built.binary(Engine::ModeA).unwrap(),
        Path::new("/bin/mode-a-1")
    );
    assert!(built
        .binary(Engine::Hamlet)
        .unwrap_err()
        .contains("could not be built - fix what the build names: it failed"));
    let mut stale = Launcher {
        root: root.to_path_buf(),
        build: false,
    };
    assert!(stale
        .binary(Engine::ModeA)
        .unwrap_err()
        .contains("older than its sources"));
    let mut none = Launcher {
        root: root.join("nowhere"),
        build: true,
    };
    assert!(none
        .binary(Engine::ModeA)
        .unwrap_err()
        .contains("did not start"));
    let ran = run(
        root,
        Path::new("/bin/sh"),
        &[
            "-c".into(),
            "pwd; echo \"$L7R_GATE_TREE\" >&2; exit 3".into(),
        ],
    )
    .unwrap();
    assert_eq!(
        (ran.code, ran.stdout.trim(), ran.stderr.trim()),
        (3, root.to_str().unwrap(), root.to_str().unwrap())
    );
    assert!(run(root, &root.join("none"), &[])
        .unwrap_err()
        .contains("did not start"));
}
