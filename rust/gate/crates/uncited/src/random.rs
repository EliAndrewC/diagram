//! Python's `random.seed(312)` and `random.sample` (`make uncited DO=verify` with `--sample`, feature 312's calibration of the import
//! check): the Mersenne Twister `CPython` seeds an `int` with (`init_by_array` of its 32-bit words), its `getrandbits`, `_randbelow` and
//! `sample` as Python 3.14 writes them, so a sample draws the same pages the Python drew (feature 449 T147; its tests hold the draws
//! Python 3.14.4 gave, observed 2026-11-16, method: `random.seed(312)` then each call, in the interpreter).

const N: usize = 624;
const M: usize = 397;

/// The generator.
pub struct Twister {
    mt: [u32; N],
    i: usize,
}

impl Twister {
    fn init(s: u32) -> Self {
        let mut mt = [0u32; N];
        mt[0] = s;
        for i in 1..N {
            let prev = mt[i - 1];
            mt[i] = 1_812_433_253u32
                .wrapping_mul(prev ^ (prev >> 30))
                .wrapping_add(u32::try_from(i).unwrap_or(0));
        }
        Self { mt, i: N }
    }

    /// `random.seed(n)` for a non-negative `n` below 2^32: `init_by_array([n])`.
    #[must_use]
    pub fn seeded(n: u32) -> Self {
        let key = [n];
        let mut t = Self::init(19_650_218);
        let (mut i, mut j) = (1usize, 0usize);
        for _ in 0..N.max(key.len()) {
            let prev = t.mt[i - 1];
            t.mt[i] = (t.mt[i] ^ (prev ^ (prev >> 30)).wrapping_mul(1_664_525))
                .wrapping_add(key[j])
                .wrapping_add(u32::try_from(j).unwrap_or(0));
            i += 1;
            j += 1;
            if i >= N {
                t.mt[0] = t.mt[N - 1];
                i = 1;
            }
            if j >= key.len() {
                j = 0;
            }
        }
        for _ in 0..N - 1 {
            let prev = t.mt[i - 1];
            t.mt[i] = (t.mt[i] ^ (prev ^ (prev >> 30)).wrapping_mul(1_566_083_941))
                .wrapping_sub(u32::try_from(i).unwrap_or(0));
            i += 1;
            if i >= N {
                t.mt[0] = t.mt[N - 1];
                i = 1;
            }
        }
        t.mt[0] = 0x8000_0000;
        t
    }

    fn twist(&mut self) {
        for k in 0..N {
            let y = (self.mt[k] & 0x8000_0000) | (self.mt[(k + 1) % N] & 0x7fff_ffff);
            let mag = if y & 1 == 1 { 0x9908_b0df } else { 0 };
            self.mt[k] = self.mt[(k + M) % N] ^ (y >> 1) ^ mag;
        }
        self.i = 0;
    }

    /// `genrand_uint32`.
    pub fn next_u32(&mut self) -> u32 {
        if self.i >= N {
            self.twist();
        }
        let mut y = self.mt[self.i];
        self.i += 1;
        y ^= y >> 11;
        y ^= (y << 7) & 0x9d2c_5680;
        y ^= (y << 15) & 0xefc6_0000;
        y ^ (y >> 18)
    }

    /// `getrandbits(k)` for `k` from 1 to 32.
    pub fn bits(&mut self, k: u32) -> u32 {
        self.next_u32() >> (32 - k)
    }

    /// `_randbelow(n)` for `n` from 1 to 2^32 - 1.
    pub fn below(&mut self, n: u32) -> u32 {
        let k = 32 - n.leading_zeros();
        loop {
            let r = self.bits(k);
            if r < n {
                return r;
            }
        }
    }
}

/// `random.sample(population, k)`, or its `ValueError` where `k` is negative or past the population.
///
/// # Errors
/// `k` out of range.
pub fn sample<T: Clone>(t: &mut Twister, population: &[T], k: i64) -> crate::Result<Vec<T>> {
    let n = population.len();
    let k = usize::try_from(k).ok().filter(|k| *k <= n).ok_or_else(|| {
        crate::Error::new("ValueError", "Sample larger than population or is negative")
    })?;
    let mut setsize = 21usize;
    if k > 5 {
        // `4 ** ceil(log(k * 3, 4))`: 3k is never a power of four, so the float log's rounding cannot move the ceiling
        let mut p = 1usize;
        while p < k * 3 {
            p *= 4;
        }
        setsize += p;
    }
    let below = |t: &mut Twister, m: usize| {
        usize::try_from(t.below(u32::try_from(m).unwrap_or(u32::MAX))).unwrap_or(0)
    };
    let mut out = Vec::with_capacity(k);
    if n <= setsize {
        let mut pool = population.to_vec();
        for i in 0..k {
            let j = below(t, n - i);
            out.push(pool[j].clone());
            pool[j] = pool[n - i - 1].clone();
        }
    } else {
        let mut selected = std::collections::HashSet::new();
        for _ in 0..k {
            let mut j = below(t, n);
            while selected.contains(&j) {
                j = below(t, n);
            }
            selected.insert(j);
            out.push(population[j].clone());
        }
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::{sample, Twister};

    #[test]
    fn the_draws_python_gave() {
        let mut t = Twister::seeded(312);
        assert_eq!(
            [t.next_u32(), t.next_u32(), t.next_u32()],
            [2_793_391_835, 623_965_776, 2_820_208_168]
        );
        assert_eq!((t.bits(11), t.bits(1)), (782, 0));
        let pool: Vec<u32> = (0..1085).collect();
        assert_eq!(
            sample(&mut Twister::seeded(312), &pool, 10).unwrap(),
            [297, 782, 66, 303, 669, 474, 394, 934, 903, 247]
        );
        let small: Vec<u32> = (0..20).collect();
        assert_eq!(
            sample(&mut Twister::seeded(312), &small, 7).unwrap(),
            [4, 12, 1, 19, 10, 3, 14]
        );
        let hundred: Vec<u32> = (0..100).collect();
        assert_eq!(
            sample(&mut Twister::seeded(312), &hundred, 100).unwrap()[..5],
            [83, 18, 84, 48, 4]
        );
        assert_eq!(
            sample(&mut Twister::seeded(312), &small, 21)
                .unwrap_err()
                .kind,
            "ValueError"
        );
        assert_eq!(
            sample(&mut Twister::seeded(312), &small, -1)
                .unwrap_err()
                .kind,
            "ValueError"
        );
        // a population past the set's size: the set form, a draw taken twice drawn again
        let wide: Vec<u32> = (0..278).collect();
        assert_eq!(
            sample(&mut Twister::seeded(312), &wide, 30).unwrap(),
            [
                74, 195, 16, 75, 167, 118, 98, 233, 225, 61, 152, 170, 78, 2, 163, 138, 83, 77,
                129, 24, 165, 140, 162, 104, 55, 92, 198, 110, 121, 15
            ]
        );
        // a hundred of 1,046: three draws taken twice, drawn again (103 draws in all, in Python)
        let many: Vec<u32> = (0..1046).collect();
        let got = sample(&mut Twister::seeded(312), &many, 100).unwrap();
        assert_eq!(
            (&got[..5], &got[95..], got.iter().sum::<u32>()),
            (
                &[297, 782, 66, 303, 669][..],
                &[489, 722, 430, 452, 267][..],
                50130
            )
        );
        // a twist past the first 624 draws
        let mut long = Twister::seeded(312);
        let mut last = 0;
        for _ in 0..1300 {
            last = long.next_u32();
        }
        assert_eq!(last, LAST_OF_1300);
    }

    /// `random.seed(312); [random.getrandbits(32) for _ in range(1300)][-1]` in Python 3.14.4.
    const LAST_OF_1300: u32 = 1_173_113_530;
}
