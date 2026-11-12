//! The landing and the owing replay (feature 449 T121, T83's fifth and last slice, `ask:449-T83-scope`): `l7r-gate land`, the port of
//! `scripts/land.py` behind `make land`, `make land-batch` and `make land-stop`, and `l7r-gate replay-owing`, the port of
//! `scripts/measure/replay_owing.py` behind `make replay-owing`. Its own crate because the landing asks the review ledger (`reviews`),
//! `speckit-todo`'s holding box (`cohort`) and the claims (`claims`) in process, the ruling's three, and no crate below the binary builds
//! on all three without the arbiter's whole build; the replay asks the claims and the pop-up owing (`owed`) in process.

pub mod land;
pub mod replay_owing;

use l7r_gate_core::Reply;
