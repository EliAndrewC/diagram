//! The shards' format (feature 449 T138).

use crate::testkit::q;
use l7r_shared::tempdir::TempDir;

use super::{dos_time, f32_to_half, half_to_f32, read, write, Shard};

/// A shard `semantic_index.save_shard` wrote (2026-11-16): two rows of four, the second fingerprint at the full twenty, a path not ASCII.
const SAMPLE: &[u8] = include_bytes!("sample.npz");

#[test]
fn a_shard_numpy_wrote_is_read() {
    let dir = TempDir::new("npz-read");
    let p = dir.path().join("s.npz");
    std::fs::write(&p, SAMPLE).unwrap();
    let s = read(&p).unwrap().unwrap();
    assert_eq!(s.fps, ["aaaa", "bbbbbbbbbbbbbbbbbbbb"]);
    assert_eq!(s.paths, [String::from("x/\u{e9}.txt"), q("0001-q.html")]);
    assert_eq!(s.spans, [[0, 5], [7, 900]]);
    assert_eq!(
        (s.dim, s.vecs.clone()),
        (4, vec![14336, 49152, 17, 31743, 11878, 12902, 13517, 13926])
    );
    // written again and read back the same
    let q = dir.path().join("sub/t.npz");
    write(&q, &s, dos_time(1_763_251_200)).unwrap();
    assert_eq!(read(&q).unwrap().unwrap(), s);
    assert!(read(&dir.path().join("none.npz")).unwrap().is_none());
    // a shard that cannot be read, and one that cannot be written (its folder a file; the shard itself a folder)
    std::fs::set_permissions(&q, std::os::unix::fs::PermissionsExt::from_mode(0o000)).unwrap();
    assert!(read(&q).is_err());
    assert!(write(&p.join("x.npz"), &s, (0, 0)).is_err());
    assert!(write(dir.path(), &s, (0, 0)).is_err());
}

#[test]
fn numpy_s_npy_headers_byte_for_byte() {
    // numpy 2.5's `np.save` of a `<U20` array of two (observed 2026-11-16): 128 bytes of header
    let dir = TempDir::new("npz-head");
    let p = dir.path().join("h.npz");
    let s = Shard {
        fps: vec!["ab".into(), "c".into()],
        vecs: vec![0; 2048],
        dim: 1024,
        paths: vec![],
        spans: vec![],
    };
    write(&p, &s, (0, 0)).unwrap();
    let z = std::fs::read(&p).unwrap();
    let head = b"\x93NUMPY\x01\x00v\x00{'descr': '<U20', 'fortran_order': False, 'shape': (2,), }";
    let at = z.windows(head.len()).position(|w| w == head).unwrap();
    assert_eq!(z[at + 127], b'\n');
    assert!(z
        .windows(30)
        .any(|w| w == b"'descr': '<U1', 'fortran_order'"[..30].as_ref()));
    assert!(z.windows(9).any(|w| w == b"(2, 1024)"));
    assert!(z.windows(6).any(|w| w == b"(0, 2)"));
}

#[test]
fn what_is_not_a_shard_is_refused() {
    let dir = TempDir::new("npz-bad");
    let p = dir.path().join("b.npz");
    let refused = |bytes: &[u8]| {
        std::fs::write(&p, bytes).unwrap();
        read(&p).unwrap_err().0
    };
    assert!(refused(b"not a zip").contains("not a zip"));
    let mut z = SAMPLE.to_vec();
    let end = z.len() - 22;
    z[end + 16] = 0xff; // the directory's offset past the end
    assert!(refused(&z).contains("damaged"));
    let mut z = SAMPLE.to_vec();
    let cd = z.windows(4).position(|w| w == [0x50, 0x4b, 1, 2]).unwrap();
    z[cd + 10] = 8; // deflated
    assert!(refused(&z).contains("compressed"));
    let one = |name: &str, body: &[u8]| super::zip(&[(name, body.to_vec())], (0, 0));
    assert!(refused(&one("fps.npy", b"plain")).contains("not .npy"));
    let npy = |descr: &str, extra: &str, shape: &str| {
        let h = format!("{{'descr': '{descr}', 'fortran_order': {extra}, 'shape': {shape}, }}");
        let mut v = b"\x93NUMPY\x02\x00".to_vec();
        v.extend(u32::try_from(h.len()).unwrap().to_le_bytes());
        v.extend(h.as_bytes());
        v
    };
    assert!(refused(&one("fps.npy", &npy("<U2", "True", "(1,)"))).contains("Fortran"));
    assert!(refused(&one("fps.npy", &npy("<i8", "False", "(1,)"))).contains("strings of type"));
    assert!(refused(&one("fps.npy", &npy("<U2", "False", "(1,)"))).contains("short"));
    assert!(refused(&one("odd.npy", &npy("<U2", "False", "(0,)"))).contains("unexpected member"));
    let mut bad = npy("<U1", "False", "(1,)");
    bad.extend(0xd800u32.to_le_bytes());
    std::fs::write(&p, one("fps.npy", &bad)).unwrap();
    assert_eq!(read(&p).unwrap().unwrap().fps, ["\u{fffd}"]);
}

#[test]
fn half_precision_as_numpy_rounds_it() {
    for (x, h) in [
        (0.5_f32, 14336_u16),
        (-2.0, 49152),
        (1e-6, 17),
        (65504.0, 31743),
        (0.1, 11878),
        (0.0, 0),
        (-0.0, 0x8000),
        (1e9, 0x7c00),
        (f32::INFINITY, 0x7c00),
        (1e-9, 0),
        (2049.0, 0x6800), // a tie, to even
        (2051.0, 0x6802), // a tie, up to even
        (5.96e-8, 1),
        (2.98e-8, 0),
    ] {
        assert_eq!(f32_to_half(x), h, "{x}");
    }
    assert_eq!(f32_to_half(f32::NAN) & 0x7c00, 0x7c00);
    assert_eq!(f32_to_half(f32::from_bits(0x7f80_0001)), 0x7c01);
    for h in [0_u16, 1, 0x3ff, 0x400, 14336, 0x7c00, 0xfc00, 0x8001] {
        assert_eq!(f32_to_half(half_to_f32(h)), h);
    }
    assert!(half_to_f32(0x7e00).is_nan());
    assert_eq!(dos_time(0), (33, 0));
    assert_eq!(
        dos_time(1_763_251_262),
        (((2025 - 1980) << 9) | (11 << 5) | 16, (1 << 5) | 1)
    );
    assert_eq!(
        dos_time(951_782_400).0,
        ((2000 - 1980) << 9) | (2 << 5) | 29
    );
}
