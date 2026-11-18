//! THE ONE CAPTION PLACER (feature 449 T151, `l7r/diagram/labels/` ported; feature 266) - owned by neither mode; [`hand_sheet`] runs it
//! over a hand-drawn Mode A sheet's declared captions in the sheet's render (feature 286). Read [`placer`] first: its doc is the standard
//! in the order it decides. [`standard`] holds every number, each with its source or its calibration; [`obstacles`] the index; [`layout`]
//! the line cuts; [`geom`] the plain geometry; [`svg`] the caption written as SVG.
//!
//! THE BAR (the GM 2026-11-17, engine-plan.md: "the resulting maps do NOT need to be bitwise identical"): a caption's in-between values may
//! differ from the Python's where a crate computes geometry differently (shapely onto `geo`); what binds is every research claim the
//! placer rests on, carried here word for word where it describes the Rust, and the sheet's checks. The port follows the Python's
//! arithmetic, candidates and ties in their order, so a difference comes only from the two shapely calls the hand sheet made, and
//! `parse/lockstep_labels.rs` lists every caption of the four caption-placing pool sheets that stands apart, with its distance.
//!
//! LOCKSTEP: the Python package stays for `compound.py`, `compound_view.py`, `pack_audit`'s program rules and the three magistracies'
//! generators until step 3b; the claims stay keyed to its `.py` units (`ask:449-phase4-slices` Q10).
//!
//! Research: the caption placer's modules - NONE: the package's index, deciding nothing

pub mod geom;
pub mod hand_sheet;
pub mod layout;
pub mod obstacles;
pub mod placer;
pub mod standard;
pub mod svg;
