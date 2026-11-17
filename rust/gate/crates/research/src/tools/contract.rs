//! `l7r-gate record source-tags-contract [--check]` (`make source-tags-contract`; `tools/source_tags_contract.py`, feature 305 FR-012;
//! ported by feature 449 T148): the source vocabulary derived into the `source-applicability` contract, so the agent - which launches
//! without the record's CLAUDE.md files - judges tags against the same explanations the labels show; `--check` writes nothing and exits 1
//! while the block is stale.

use std::path::Path;

use l7r_gate_core::record::args::{parse, Spec};

use super::{said, usage, Run};
use crate::record::source_tags as st;
use crate::Error;

/// The contract, from the tree: `.claude/agents/` beside the record.
pub const CONTRACT: &str = ".claude/agents/source-applicability.md";

/// The command in the repository `tree`; `--contract` and `--research-dir`, the Python's hidden test flags, kept.
///
/// # Errors
/// The contract unreadable or not writable (the Python's uncaught `OSError`).
pub fn run(args: &[String], tree: &Path) -> Run {
    let parsed = match parse(
        args,
        &[
            Spec::flag("--check"),
            Spec::value("--contract"),
            Spec::value("--research-dir"),
        ],
    ) {
        Ok(p) => p,
        Err(complaint) => return Ok(usage("source-tags-contract", &complaint)),
    };
    let default = tree.join(CONTRACT).display().to_string();
    let contract = parsed.text("--contract", &default).to_owned();
    let research = tree.join("research").display().to_string();
    let research = parsed.text("--research-dir", &research);
    let text = crate::read(Path::new(&contract))
        .ok_or_else(|| Error::new("OSError", format!("cannot read '{contract}'")))?;
    let fresh = match st::load_vocabulary(Path::new(research))
        .and_then(|v| st::synced_contract(&text, &v))
    {
        Ok(f) => f,
        Err(e) if e.kind == "SourceTagError" => {
            return Ok(said(
                "",
                format!("source-tags-contract: {}\n", e.message),
                1,
            ))
        }
        Err(e) => return Err(e),
    };
    if fresh == text {
        return Ok(said(
            "source-tags-contract: the contract's vocabulary block is current\n",
            "",
            0,
        ));
    }
    if parsed.on("--check") {
        return Ok(said("", "source-tags-contract: the contract's vocabulary block is stale - run make source-tags-contract\n", 1));
    }
    std::fs::write(&contract, fresh)
        .map_err(|e| Error::new("OSError", format!("{e}: '{contract}'")))?;
    Ok(said(
        format!("source-tags-contract: rewrote the vocabulary block in {contract}\n"),
        "",
        0,
    ))
}

#[cfg(test)]
mod tests;
