//! Python's knob draw, reproduced (feature 444 T19, D7 amended 2026-10-31): `settlement/_knobs.py`'s `knob_rng(seed, knob)` -
//! a SHA-256 of `"{seed}\0{knob}"`, its first 8 bytes big-endian seeding Python's `random.Random` (MT19937, `init_by_array`) - and
//! `randrange(n)` on it, so a phase rolled in Rust draws the plan Python drew and every seed keeps its map (the GM's landing rule,
//! "no regressed seed"). Public algorithms only: FIPS 180-4's SHA-256, Matsumoto and Nishimura's MT19937, `CPython`'s
//! `_randbelow_with_getrandbits`; no crate dependency.
//!
//! Research:
//!     the draws - NONE: a deterministic generator, the same draws as the Python knob rolls it stands in for (D7)

/// SHA-256's round constants (FIPS 180-4, 4.2.2).
const K: [u32; 64] = [
    0x428a_2f98,
    0x7137_4491,
    0xb5c0_fbcf,
    0xe9b5_dba5,
    0x3956_c25b,
    0x59f1_11f1,
    0x923f_82a4,
    0xab1c_5ed5,
    0xd807_aa98,
    0x1283_5b01,
    0x2431_85be,
    0x550c_7dc3,
    0x72be_5d74,
    0x80de_b1fe,
    0x9bdc_06a7,
    0xc19b_f174,
    0xe49b_69c1,
    0xefbe_4786,
    0x0fc1_9dc6,
    0x240c_a1cc,
    0x2de9_2c6f,
    0x4a74_84aa,
    0x5cb0_a9dc,
    0x76f9_88da,
    0x983e_5152,
    0xa831_c66d,
    0xb003_27c8,
    0xbf59_7fc7,
    0xc6e0_0bf3,
    0xd5a7_9147,
    0x06ca_6351,
    0x1429_2967,
    0x27b7_0a85,
    0x2e1b_2138,
    0x4d2c_6dfc,
    0x5338_0d13,
    0x650a_7354,
    0x766a_0abb,
    0x81c2_c92e,
    0x9272_2c85,
    0xa2bf_e8a1,
    0xa81a_664b,
    0xc24b_8b70,
    0xc76c_51a3,
    0xd192_e819,
    0xd699_0624,
    0xf40e_3585,
    0x106a_a070,
    0x19a4_c116,
    0x1e37_6c08,
    0x2748_774c,
    0x34b0_bcb5,
    0x391c_0cb3,
    0x4ed8_aa4a,
    0x5b9c_ca4f,
    0x682e_6ff3,
    0x748f_82ee,
    0x78a5_636f,
    0x84c8_7814,
    0x8cc7_0208,
    0x90be_fffa,
    0xa450_6ceb,
    0xbef9_a3f7,
    0xc671_78f2,
];

/// The SHA-256 digest of `data` (FIPS 180-4, 6.2).
fn sha256(data: &[u8]) -> [u8; 32] {
    let mut h: [u32; 8] = [
        0x6a09_e667,
        0xbb67_ae85,
        0x3c6e_f372,
        0xa54f_f53a,
        0x510e_527f,
        0x9b05_688c,
        0x1f83_d9ab,
        0x5be0_cd19,
    ];
    let mut msg = data.to_vec();
    let bits = (data.len() as u64).wrapping_mul(8);
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bits.to_be_bytes());
    for block in msg.chunks_exact(64) {
        let mut w = [0u32; 64];
        for (i, word) in block.chunks_exact(4).enumerate() {
            w[i] = u32::from_be_bytes([word[0], word[1], word[2], word[3]]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let mut v = h;
        for i in 0..64 {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7]
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[i])
                .wrapping_add(w[i]);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(maj);
            v = [
                t1.wrapping_add(t2),
                v[0],
                v[1],
                v[2],
                v[3].wrapping_add(t1),
                v[4],
                v[5],
                v[6],
            ];
        }
        for (a, b) in h.iter_mut().zip(v) {
            *a = a.wrapping_add(b);
        }
    }
    let mut out = [0u8; 32];
    for (i, word) in h.iter().enumerate() {
        out[i * 4..i * 4 + 4].copy_from_slice(&word.to_be_bytes());
    }
    out
}

/// FIPS 180-4's SHA-512 of `data`.
#[must_use]
#[expect(
    clippy::too_many_lines,
    reason = "the standard's 80 round constants and its one compression loop"
)]
pub fn sha512(data: &[u8]) -> [u8; 64] {
    const K: [u64; 80] = [
        0x428a_2f98_d728_ae22,
        0x7137_4491_23ef_65cd,
        0xb5c0_fbcf_ec4d_3b2f,
        0xe9b5_dba5_8189_dbbc,
        0x3956_c25b_f348_b538,
        0x59f1_11f1_b605_d019,
        0x923f_82a4_af19_4f9b,
        0xab1c_5ed5_da6d_8118,
        0xd807_aa98_a303_0242,
        0x1283_5b01_4570_6fbe,
        0x2431_85be_4ee4_b28c,
        0x550c_7dc3_d5ff_b4e2,
        0x72be_5d74_f27b_896f,
        0x80de_b1fe_3b16_96b1,
        0x9bdc_06a7_25c7_1235,
        0xc19b_f174_cf69_2694,
        0xe49b_69c1_9ef1_4ad2,
        0xefbe_4786_384f_25e3,
        0x0fc1_9dc6_8b8c_d5b5,
        0x240c_a1cc_77ac_9c65,
        0x2de9_2c6f_592b_0275,
        0x4a74_84aa_6ea6_e483,
        0x5cb0_a9dc_bd41_fbd4,
        0x76f9_88da_8311_53b5,
        0x983e_5152_ee66_dfab,
        0xa831_c66d_2db4_3210,
        0xb003_27c8_98fb_213f,
        0xbf59_7fc7_beef_0ee4,
        0xc6e0_0bf3_3da8_8fc2,
        0xd5a7_9147_930a_a725,
        0x06ca_6351_e003_826f,
        0x1429_2967_0a0e_6e70,
        0x27b7_0a85_46d2_2ffc,
        0x2e1b_2138_5c26_c926,
        0x4d2c_6dfc_5ac4_2aed,
        0x5338_0d13_9d95_b3df,
        0x650a_7354_8baf_63de,
        0x766a_0abb_3c77_b2a8,
        0x81c2_c92e_47ed_aee6,
        0x9272_2c85_1482_353b,
        0xa2bf_e8a1_4cf1_0364,
        0xa81a_664b_bc42_3001,
        0xc24b_8b70_d0f8_9791,
        0xc76c_51a3_0654_be30,
        0xd192_e819_d6ef_5218,
        0xd699_0624_5565_a910,
        0xf40e_3585_5771_202a,
        0x106a_a070_32bb_d1b8,
        0x19a4_c116_b8d2_d0c8,
        0x1e37_6c08_5141_ab53,
        0x2748_774c_df8e_eb99,
        0x34b0_bcb5_e19b_48a8,
        0x391c_0cb3_c5c9_5a63,
        0x4ed8_aa4a_e341_8acb,
        0x5b9c_ca4f_7763_e373,
        0x682e_6ff3_d6b2_b8a3,
        0x748f_82ee_5def_b2fc,
        0x78a5_636f_4317_2f60,
        0x84c8_7814_a1f0_ab72,
        0x8cc7_0208_1a64_39ec,
        0x90be_fffa_2363_1e28,
        0xa450_6ceb_de82_bde9,
        0xbef9_a3f7_b2c6_7915,
        0xc671_78f2_e372_532b,
        0xca27_3ece_ea26_619c,
        0xd186_b8c7_21c0_c207,
        0xeada_7dd6_cde0_eb1e,
        0xf57d_4f7f_ee6e_d178,
        0x06f0_67aa_7217_6fba,
        0x0a63_7dc5_a2c8_98a6,
        0x113f_9804_bef9_0dae,
        0x1b71_0b35_131c_471b,
        0x28db_77f5_2304_7d84,
        0x32ca_ab7b_40c7_2493,
        0x3c9e_be0a_15c9_bebc,
        0x431d_67c4_9c10_0d4c,
        0x4cc5_d4be_cb3e_42b6,
        0x597f_299c_fc65_7e2a,
        0x5fcb_6fab_3ad6_faec,
        0x6c44_198c_4a47_5817,
    ];
    let mut h: [u64; 8] = [
        0x6a09_e667_f3bc_c908,
        0xbb67_ae85_84ca_a73b,
        0x3c6e_f372_fe94_f82b,
        0xa54f_f53a_5f1d_36f1,
        0x510e_527f_ade6_82d1,
        0x9b05_688c_2b3e_6c1f,
        0x1f83_d9ab_fb41_bd6b,
        0x5be0_cd19_137e_2179,
    ];
    let mut msg = data.to_vec();
    let bits = (data.len() as u128) * 8;
    msg.push(0x80);
    while msg.len() % 128 != 112 {
        msg.push(0);
    }
    msg.extend(bits.to_be_bytes());
    for block in msg.chunks(128) {
        let mut w = [0u64; 80];
        for (t, c) in block.chunks(8).enumerate() {
            let mut b = [0u8; 8];
            b.copy_from_slice(c);
            w[t] = u64::from_be_bytes(b);
        }
        for t in 16..80 {
            let s0 = w[t - 15].rotate_right(1) ^ w[t - 15].rotate_right(8) ^ (w[t - 15] >> 7);
            let s1 = w[t - 2].rotate_right(19) ^ w[t - 2].rotate_right(61) ^ (w[t - 2] >> 6);
            w[t] = w[t - 16]
                .wrapping_add(s0)
                .wrapping_add(w[t - 7])
                .wrapping_add(s1);
        }
        let mut v = h;
        for t in 0..80 {
            let s1 = v[4].rotate_right(14) ^ v[4].rotate_right(18) ^ v[4].rotate_right(41);
            let ch = (v[4] & v[5]) ^ (!v[4] & v[6]);
            let t1 = v[7]
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[t])
                .wrapping_add(w[t]);
            let s0 = v[0].rotate_right(28) ^ v[0].rotate_right(34) ^ v[0].rotate_right(39);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(maj);
            v = [
                t1.wrapping_add(t2),
                v[0],
                v[1],
                v[2],
                v[3].wrapping_add(t1),
                v[4],
                v[5],
                v[6],
            ];
        }
        for (x, y) in h.iter_mut().zip(v) {
            *x = x.wrapping_add(y);
        }
    }
    let mut out = [0u8; 64];
    for (i, x) in h.iter().enumerate() {
        out[i * 8..i * 8 + 8].copy_from_slice(&x.to_be_bytes());
    }
    out
}

/// Python's `random.Random`: MT19937 seeded by `init_by_array` from an integer's 32-bit words, least significant first.
pub struct PyRandom {
    mt: [u32; 624],
    index: usize,
}

impl PyRandom {
    /// `random.Random(seed)` for a non-negative integer seed below 2^64.
    #[must_use]
    pub fn new(seed: u64) -> Self {
        let lo = u32::try_from(seed & 0xffff_ffff).unwrap_or(0);
        let hi = u32::try_from(seed >> 32).unwrap_or(0);
        Self::from_key(&if hi == 0 { vec![lo] } else { vec![lo, hi] })
    }

    /// `random.Random(text)` for a string seed (`CPython`'s version 2 seeding, feature 444 T30): the text's UTF-8 bytes followed by
    /// their SHA-512 digest, read as one big-endian integer, its 32-bit words least significant first.
    #[must_use]
    pub fn from_text(text: &str) -> Self {
        let mut bytes = text.as_bytes().to_vec();
        bytes.extend(sha512(text.as_bytes()));
        // the integer's words least significant first; its top word is never zero (the text's first byte leads it, and no seed
        // text starts with a NUL), so none is stripped as Python strips an integer's leading zero words
        let key: Vec<u32> = bytes
            .rchunks(4)
            .map(|c| c.iter().fold(0u32, |acc, &b| (acc << 8) | u32::from(b)))
            .collect();
        Self::from_key(&key)
    }

    /// `shuffle(list(range(n)))`: Fisher-Yates from the end, each swap's index `randbelow(i + 1)`.
    #[must_use]
    pub fn shuffled(&mut self, n: usize) -> Vec<usize> {
        let mut out: Vec<usize> = (0..n).collect();
        for i in (1..n).rev() {
            let j = self.randbelow(u32::try_from(i + 1).unwrap_or(u32::MAX)) as usize;
            out.swap(i, j);
        }
        out
    }

    /// `init_by_array(key)` on a fresh generator.
    fn from_key(key: &[u32]) -> Self {
        let mut r = Self {
            mt: [0; 624],
            index: 624,
        };
        r.init_genrand(19_650_218);
        let (mut i, mut j) = (1usize, 0usize);
        for _ in 0..624.max(key.len()) {
            let prev = r.mt[i - 1] ^ (r.mt[i - 1] >> 30);
            r.mt[i] = (r.mt[i] ^ prev.wrapping_mul(1_664_525))
                .wrapping_add(key[j])
                .wrapping_add(u32::try_from(j).unwrap_or(0));
            i += 1;
            j += 1;
            if i >= 624 {
                r.mt[0] = r.mt[623];
                i = 1;
            }
            if j >= key.len() {
                j = 0;
            }
        }
        for _ in 0..623 {
            let prev = r.mt[i - 1] ^ (r.mt[i - 1] >> 30);
            r.mt[i] = (r.mt[i] ^ prev.wrapping_mul(1_566_083_941))
                .wrapping_sub(u32::try_from(i).unwrap_or(0));
            i += 1;
            if i >= 624 {
                r.mt[0] = r.mt[623];
                i = 1;
            }
        }
        r.mt[0] = 0x8000_0000;
        r
    }

    fn init_genrand(&mut self, s: u32) {
        self.mt[0] = s;
        for i in 1..624 {
            let prev = self.mt[i - 1] ^ (self.mt[i - 1] >> 30);
            self.mt[i] = prev
                .wrapping_mul(1_812_433_253)
                .wrapping_add(u32::try_from(i).unwrap_or(0));
        }
        self.index = 624;
    }

    fn genrand_u32(&mut self) -> u32 {
        if self.index >= 624 {
            for k in 0..624 {
                let y = (self.mt[k] & 0x8000_0000) | (self.mt[(k + 1) % 624] & 0x7fff_ffff);
                let mag = if y & 1 == 0 { 0 } else { 0x9908_b0df };
                self.mt[k] = self.mt[(k + 397) % 624] ^ (y >> 1) ^ mag;
            }
            self.index = 0;
        }
        let mut y = self.mt[self.index];
        self.index += 1;
        y ^= y >> 11;
        y ^= (y << 7) & 0x9d2c_5680;
        y ^= (y << 15) & 0xefc6_0000;
        y ^ (y >> 18)
    }

    /// `randrange(n)` for `0 < n < 2^32`: `CPython`'s `_randbelow_with_getrandbits`, `getrandbits(k)` drawn until below `n`.
    pub fn randbelow(&mut self, n: u32) -> u32 {
        let k = 32 - n.leading_zeros();
        loop {
            let r = self.genrand_u32() >> (32 - k); // n > 0, so k >= 1
            if r < n {
                return r;
            }
        }
    }

    /// `random()`: `CPython`'s 53-bit float in [0, 1), two draws shifted 5 and 6.
    pub fn random(&mut self) -> f64 {
        let a = f64::from(self.genrand_u32() >> 5);
        let b = f64::from(self.genrand_u32() >> 6);
        (a * 67_108_864.0 + b) / 9_007_199_254_740_992.0
    }
}

/// A knob's roll as `Knob.roll` draws it from its typing-filtered pool: `randrange(len)` when `weights` is empty, else the first
/// form whose running weight passes `random()` times the pool's total (the last on float dust). Returns the form's index.
///
/// Research:
///     knob rolls - research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html: each knob's form rolled per hamlet, never chosen
#[must_use]
pub fn roll(seed: i64, knob: &str, n: u32, weights: &[f64]) -> u32 {
    let mut rng = knob_rng(seed, knob);
    if weights.is_empty() {
        return rng.randbelow(n);
    }
    let mut u = rng.random() * weights.iter().sum::<f64>();
    for (i, w) in weights.iter().enumerate() {
        u -= w;
        if u < 0.0 {
            #[expect(clippy::cast_possible_truncation, reason = "a knob's handful of forms")]
            return i as u32;
        }
    }
    n - 1
}

/// `knob_rng(seed, knob)`: the stream of `knob` under the map's `seed`.
#[must_use]
pub fn knob_rng(seed: i64, knob: &str) -> PyRandom {
    let digest = sha256(format!("{seed}\0{knob}").as_bytes());
    let mut first = [0u8; 8];
    first.copy_from_slice(&digest[..8]);
    PyRandom::new(u64::from_be_bytes(first))
}

#[cfg(test)]
mod tests {
    use std::fmt::Write;

    use super::{knob_rng, roll, sha256, sha512, PyRandom};

    #[test]
    fn sha256_is_fips_180_4_s() {
        let hex = sha256(b"abc").iter().fold(String::new(), |mut s, b| {
            let _ = write!(s, "{b:02x}");
            s
        });
        assert_eq!(
            hex,
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
    }

    #[test]
    fn a_draw_is_python_s() {
        // random.Random(42).randrange(10) for ten draws, and the sub-seed of (1, "x")'s first draw below 7, from CPython 3.12
        let mut r = PyRandom::new(42);
        let got: Vec<u32> = (0..10).map(|_| r.randbelow(10)).collect();
        assert_eq!(got, vec![1, 0, 4, 3, 3, 2, 1, 8, 1, 9]);
        assert!(knob_rng(1, "x").randbelow(7) < 7);
        assert_eq!(PyRandom::new(1 << 40).randbelow(1), 0);
        // random.Random(42).random() in CPython 3.12
        assert_eq!(
            PyRandom::new(42).random().to_bits(),
            0.639_426_798_457_883_7_f64.to_bits()
        );
        assert!(roll(3, "paddy_rest", 2, &[0.8, 0.2]) < 2);
        assert_eq!(roll(3, "x", 2, &[1.0, 0.0]), 0);
        assert_eq!(roll(3, "x", 2, &[0.0, 0.0]), 1, "float dust takes the last");
        assert!(roll(3, "x", 5, &[]) < 5);
    }

    #[test]
    fn a_text_seed_shuffles_as_python_does() {
        // `random.Random("4:size_length").shuffle(list(range(10)))` and its draws, read off CPython 3.14
        assert_eq!(
            PyRandom::from_text("4:size_length").shuffled(10),
            vec![9, 2, 3, 4, 6, 8, 0, 1, 7, 5]
        );
        assert_eq!(
            PyRandom::from_text("25:kura").shuffled(10),
            vec![6, 0, 1, 3, 4, 7, 8, 5, 9, 2]
        );
        assert_eq!(
            PyRandom::from_text("x").shuffled(10),
            vec![0, 8, 2, 9, 4, 3, 6, 1, 7, 5]
        );
        let mut r = PyRandom::from_text("4:size_length");
        assert_eq!(r.shuffled(0), Vec::<usize>::new());
        let hex = sha512(b"abc")[..16]
            .iter()
            .fold(String::new(), |mut acc, b| {
                let _ = write!(acc, "{b:02x}");
                acc
            });
        assert_eq!(hex, "ddaf35a193617abacc417349ae204131");
    }
}
