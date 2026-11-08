//! NO FIXED SEEDS (feature 444 T36; the GM 2026-11-07: "We should probably avoid fixed seeds because of overfitting ... If a seed
//! fails then we want to keep testing it until it succeeds, after which point it gets dropped from the fixed pool and when there are
//! no known bugs then we have no fixed seeds"): the known-failing pool rolled again and fresh seeds rolled beside it. `make seeds`
//! (`hamlet --seeds`) reads and writes the pool, draws the fresh block's start and judges each seed; this is the rule.
//!
//! Research:
//!     the seeds - NONE: the test bed's own bookkeeping

/// The field forms the seeds are rolled on: a comb's valley paddy and the two polders.
pub const FORMS: [&str; 3] = ["comb", "polder_grid", "mulberry_dike_fishpond"];

/// Where the fresh seeds start: past every hand roll and pinned row; a run's own start is drawn from the clock above it.
pub const FRESH_FROM: i64 = 10_000_000;

/// What a run found: the pool written back, a line each seed it reports, and the counts.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Run {
    pub pool: String,
    pub lines: Vec<String>,
    pub failing: usize,
    pub fixed: usize,
    pub added: usize,
}

/// The pool `text` (`#` lines kept as they stand; one line a seed, `<seed> <form> <its first failure>`) rolled again by `judge` - a
/// seed that rolls clean dropped, one that still fails kept with its new failure - and `n` fresh seeds of each form from `start`,
/// a failing one added.
pub fn run(text: &str, n: i64, start: i64, judge: impl Fn(i64, &str) -> Option<String>) -> Run {
    let mut out = Run::default();
    let mut kept: Vec<String> = text
        .lines()
        .filter(|l| l.starts_with('#'))
        .map(str::to_owned)
        .collect();
    for line in text
        .lines()
        .filter(|l| !l.starts_with('#') && !l.trim().is_empty())
    {
        let mut parts = line.splitn(3, ' ');
        let seed: i64 = parts.next().unwrap_or_default().parse().unwrap_or(0);
        let form = parts.next().unwrap_or("comb");
        match judge(seed, form) {
            None => {
                out.fixed += 1;
                out.lines.push(format!(
                    "seeds: pool seed {seed} {form} rolls clean - dropped from the pool"
                ));
            }
            Some(why) => {
                out.failing += 1;
                out.lines.push(format!(
                    "seeds: pool seed {seed} {form} still fails - {why}"
                ));
                kept.push(format!("{seed} {form} {why}"));
            }
        }
    }
    for form in FORMS {
        for seed in start..start + n {
            if let Some(why) = judge(seed, form) {
                out.added += 1;
                out.lines.push(format!(
                    "seeds: fresh seed {seed} {form} FAILS - {why} - added to the pool"
                ));
                kept.push(format!("{seed} {form} {why}"));
            }
        }
    }
    out.pool = kept.join("\n") + if kept.is_empty() { "" } else { "\n" };
    out
}

#[cfg(test)]
mod tests {
    use super::run;

    #[test]
    fn a_failing_seed_stays_until_it_rolls_clean_and_a_fresh_failure_joins_the_pool() {
        let pool = "# the pool\n7 comb an old failure\n9 polder_grid still broken\n\n";
        // seed 9 still fails, seed 7 is fixed, and fresh seed 101 fails on the dike-pond alone
        let r = run(pool, 2, 100, |seed, form| match (seed, form) {
            (9, _) | (101, "mulberry_dike_fishpond") => Some(format!("BROKE: {seed}")),
            _ => None,
        });
        assert_eq!(
            r.pool,
            "# the pool\n9 polder_grid BROKE: 9\n101 mulberry_dike_fishpond BROKE: 101\n"
        );
        assert_eq!((r.failing, r.fixed, r.added), (1, 1, 1));
        assert!(r
            .lines
            .iter()
            .any(|l| l.contains("7 comb rolls clean - dropped")));
        let clean = run("# the pool\n", 1, 100, |_, _| None);
        // no known bug, no fixed seed
        assert_eq!(
            (clean.pool.as_str(), clean.lines.len()),
            (
                "# the pool
",
                0
            )
        );
        // an unreadable seed is rolled as seed 0
        assert_eq!(
            run(
                "x
",
                0,
                0,
                |_, _| None
            )
            .fixed,
            1
        );
    }
}
