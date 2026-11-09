//! The remote path (feature 449 T064, from `l7r/diagram/ci/` and `l7r/diagram/switches.py`): whether a change may run on CodeBuild and what that costs. Every remote run costs money, so what must never run comes first.

pub(crate) mod aws;
pub(crate) mod cachepolicy;
pub(crate) mod config;
pub(crate) mod decision;
pub(crate) mod dispatch;
pub(crate) mod door;
pub(crate) mod features;
pub(crate) mod imagecheck;
pub(crate) mod main;
pub(crate) mod runlog;
pub(crate) mod switches;
pub(crate) mod via_make;

#[cfg(test)]
mod fixtures;
