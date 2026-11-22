//! The landing (feature 449 T121, T83's fifth and last slice, `ask:449-T83-scope`): `l7r-gate land`, the port of `scripts/land.py`
//! behind `make land`, `make land-batch` and `make land-stop`. Its own crate because the landing asks the review ledger (`reviews`),
//! `speckit-todo`'s holding box (`cohort`) and the claims (`claims`) in process, the ruling's three, and no crate below the binary builds
//! on all three without the arbiter's whole build. `l7r-gate replay-owing`, `make replay-owing`'s replay of past commits' owing, ran each
//! commit's own Python and was deleted by feature 449 T247 (`ask:449-T247-python-starts`).

pub mod land;

use l7r_gate_core::Reply;
