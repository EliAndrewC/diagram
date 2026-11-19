//! A HAND-DRAWN SHEET'S READING (feature 449 T151, `l7r/diagram/labels/hand_sheet.py`'s reader ported): [`hand_sheet`] reads a Mode A
//! sheet's drawn shapes and captions, which the caption placer rebuilt from its derivation (T202, [`crate::caption_place`]) seats. The old
//! placer ported from `l7r/diagram/labels/` (its search, obstacle index, geometry, layout and standard) was deleted by T202; the Python
//! package stays for `compound.py`'s two generated sheets until step 3b.
//!
//! Research: the sheet reader's modules - NONE: the package's index, deciding nothing

pub mod hand_sheet;
