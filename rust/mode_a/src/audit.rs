//! The Mode A sheet audit's checks, registry and report (feature 449 T175, the engine port's step 1, its fourth piece): the rest of
//! `l7r/diagram/tools/pack_audit/` - [`checks`], [`labels`], [`marks_drawn`], [`sun`], [`palette`], [`program_rules`], [`roads`],
//! [`mapmatch`], [`onmap`], [`shared`], [`registry`] and [`report`] - beside its parse, tagged marks, grids and sized marks (T170, T174),
//! and what it reads of the compound engine ([`crate::compound`]). `__main__.py` and `make pack-audit` are the piece's second part.
//!
//! The package's layers are kept (feature 173): every reference points backwards - checks, then the program and the map, then the
//! registry over all of them, then the report - so a module is read alone.
//!
//! THE PYTHON IS DELETED (feature 449 T212): the package went once nothing imported it, and its lockstep with it (`specs/449-rust-codebase/
//! engine-plan.md`: lockstep tests retire with their Python); each module's own tests pin its behavior, and the pool sweep
//! (`crate::pool_sweep`) holds every pool sheet to its tier's checks and every check to firing on its red fixtures. Its claims were
//! carried onto these modules by `dev/claims-ports.json` (`ask:449-phase4-slices` Q10). Where to look: a check is a function of
//! [`checks`] (the wall's, [`checks::walls`]), [`shared`], [`program_rules`], [`roads`], [`palette`], [`marks_drawn`], [`sun`] or
//! [`mapmatch`]; a new check is registered, with its red fixture under `tests/fixtures/` and the fix its failure names, in [`registry`];
//! the printed report and `make pack-audit` are [`report`].
//!
//! Research:
//!     the Mode A audit - NONE: the package's modules gathered, deciding nothing about a building

use std::cell::OnceCell;
use std::collections::BTreeMap;

use l7r_gate_research::Error;

use crate::tagged::Mark;

pub mod checks;
pub mod labels;
pub mod mapmatch;
pub mod marks_drawn;
pub mod onmap;
pub mod palette;
pub mod program_rules;
pub mod registry;
pub mod report;
pub mod roads;
pub mod shared;
pub mod sun;

/// A sheet's source text, with its tagged marks and its element kinds read the first time a check asks: the Python's checks each call
/// `marks(svg)`, which its memo answered from the first reading, and a reading is a pure function of the text - so one reading serves
/// every check, and a refusal is the same refusal wherever it is first asked (the memo kept no exception, so the Python raised it
/// again on each ask).
pub struct Sheet<'a> {
    pub text: &'a str,
    marks: OnceCell<Result<Vec<Mark>, Error>>,
    kinds: OnceCell<Result<BTreeMap<i64, String>, Error>>,
}

impl<'a> Sheet<'a> {
    #[must_use]
    pub fn new(text: &'a str) -> Self {
        Self {
            text,
            marks: OnceCell::new(),
            kinds: OnceCell::new(),
        }
    }

    /// `tagged.marks(text)`.
    ///
    /// # Errors
    /// The reader's refusal.
    pub fn marks(&self) -> Result<&[Mark], Error> {
        self.marks
            .get_or_init(|| crate::tagged::marks(self.text))
            .as_deref()
            .map_err(Clone::clone)
    }

    /// `sheet.element_kinds(text)`.
    ///
    /// # Errors
    /// The reader's refusal.
    pub fn kinds(&self) -> Result<&BTreeMap<i64, String>, Error> {
        self.kinds
            .get_or_init(|| crate::sheet::element_kinds(self.text))
            .as_ref()
            .map_err(Clone::clone)
    }
}

#[cfg(test)]
mod tests {
    use super::Sheet;

    #[test]
    fn a_sheet_is_read_once_and_a_refusal_kept() {
        let s = Sheet::new(r#"<svg><rect x="1" y="1" width="2" height="2" data-kind="k"/></svg>"#);
        assert_eq!(s.marks().unwrap().len(), 1);
        assert_eq!(s.kinds().unwrap().len(), 1);
        let bad = Sheet::new(r#"<svg><g transform="translate(1.2.3)"><rect/></g></svg>"#);
        assert_eq!(bad.marks().unwrap_err().kind, "ValueError");
        assert_eq!(bad.marks().unwrap_err().kind, "ValueError");
        assert!(Sheet::new("<svg>").kinds().is_err());
    }
}
