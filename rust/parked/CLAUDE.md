# Parked Rust stages (feature 444 amendment 11, FR-024 part 2)

The stages after `waterward`, the last efficient one, and the shared `law` and `ways` only they use: `homesteads`, `track`,
`appurtenances`. Moved out of the crate on 2026-11-07 - nothing compiles, tests, counts, budgets or claims them - until the
Rust baseline through `waterward` is fast and the GM resumes the next stage (the GM: "disable it and stop after ... the most
recent phase that runs quickly and efficiently"). The homesteads counted 13.2 million operations at 40 households against a
budget of 4,118 (`dev/work-budget.md`, 2026-11-06). To resume one, move its files back under `rust/phases/src/` and declare it
in `lib.rs`.
