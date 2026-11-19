//! The sheet's rolls (feature 449 T152): each attested choice a knob rolled from the map's seed, never chosen - the docs' own formula,
//! `random.Random(zlib.crc32(b"<map>:<knob>"))` (docs/buildings.md, the residence veranda and the second kami; the county example's
//! notes record four knobs rolled so). Python's generator reproduced: zlib's CRC-32 and MT19937 seeded by `init_by_array` from the
//! integer's one 32-bit word, `choice` by `_randbelow_with_getrandbits` and `random()` by two draws - the same public algorithms
//! `rust/phases/src/pyrand.rs` reproduces for the hamlet knobs, written again here because that module is private to its crate and its
//! crate is the hamlet engine, which this one does not build on.
//!
//! Research: the rolls - NONE: a deterministic generator, the draws the docs' formula names

use super::count;

/// zlib's CRC-32 of `bytes` (the reflected polynomial 0xEDB88320, all ones in and out).
#[must_use]
pub fn crc32(bytes: &[u8]) -> u32 {
    let mut crc = 0xffff_ffff_u32;
    for &b in bytes {
        crc ^= u32::from(b);
        for _ in 0..8 {
            let mask = (crc & 1).wrapping_neg();
            crc = (crc >> 1) ^ (0xedb8_8320 & mask);
        }
    }
    !crc
}

/// Python's `random.Random(n)` for `n` below 2^32.
pub struct Rng {
    mt: Vec<u32>,
    index: usize,
}

impl Rng {
    /// `random.Random(zlib.crc32(key))`.
    #[must_use]
    pub fn keyed(key: &str) -> Self {
        Self::new(crc32(key.as_bytes()))
    }

    /// `random.Random(seed)`: `init_by_array([seed])`.
    #[must_use]
    pub fn new(seed: u32) -> Self {
        let mut mt = vec![0_u32; 624];
        mt[0] = 19_650_218;
        for i in 1..624 {
            let prev = mt[i - 1] ^ (mt[i - 1] >> 30);
            mt[i] = prev
                .wrapping_mul(1_812_433_253)
                .wrapping_add(u32::try_from(i).unwrap_or(0));
        }
        let mut i = 1;
        for _ in 0..624 {
            let prev = mt[i - 1] ^ (mt[i - 1] >> 30);
            mt[i] = (mt[i] ^ prev.wrapping_mul(1_664_525)).wrapping_add(seed);
            i += 1;
            if i >= 624 {
                mt[0] = mt[623];
                i = 1;
            }
        }
        for _ in 0..623 {
            let prev = mt[i - 1] ^ (mt[i - 1] >> 30);
            mt[i] = (mt[i] ^ prev.wrapping_mul(1_566_083_941))
                .wrapping_sub(u32::try_from(i).unwrap_or(0));
            i += 1;
            if i >= 624 {
                mt[0] = mt[623];
                i = 1;
            }
        }
        mt[0] = 0x8000_0000;
        Self { mt, index: 624 }
    }

    fn next_u32(&mut self) -> u32 {
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

    /// `choice(range(n))`'s index for `0 < n`: `getrandbits(k)` drawn until below `n`.
    pub fn below(&mut self, n: u32) -> u32 {
        let k = 32 - n.leading_zeros();
        loop {
            let r = self.next_u32() >> (32 - k);
            if r < n {
                return r;
            }
        }
    }

    /// `random()`: a 53-bit float in [0, 1).
    pub fn random(&mut self) -> f64 {
        let a = f64::from(self.next_u32() >> 5);
        let b = f64::from(self.next_u32() >> 6);
        (a * 67_108_864.0 + b) / 9_007_199_254_740_992.0
    }
}

/// `random.Random(zlib.crc32(b"<sheet>:<key>")).choice(options)` - one roll counted.
#[must_use]
pub fn choice<'o>(sheet: &str, key: &str, options: &'o [String]) -> Option<&'o String> {
    count("roll@compound_choice", 1);
    let n = u32::try_from(options.len()).ok().filter(|n| *n > 0)?;
    let i = Rng::keyed(&format!("{sheet}:{key}")).below(n);
    options.get(usize::try_from(i).ok()?)
}

/// `random.Random(zlib.crc32(b"<sheet>:<key>")).random() < p` - one roll counted.
#[must_use]
pub fn chance(sheet: &str, key: &str, p: f64) -> bool {
    count("roll@compound_chance", 1);
    Rng::keyed(&format!("{sheet}:{key}")).random() < p
}
