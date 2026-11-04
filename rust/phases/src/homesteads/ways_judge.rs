//! The lane law's verdicts as the households' ways ask them (feature 444 T30): a leg on lawful ground as the web will draw it -
//! squared at its water and judged by the ground half at a footpath's tread - and a way admitted where the tree keeps the lane law
//! with it, the way as laid first held clear of its own household and of every other homestead where the laying moved it
//! (`homesteads/stages.py` `corridor_ground`; `ways/tree.py` `seating_judge`, `own_clear`, `others_clear`, `seating_drawn`).
//!
//! Research:
//!     a corridor judged as the web will lay it - research/questions/0246-how-our-maps-lay-a-clustered-settlements-lanes.drawing.html: each household's way, laid once the last house stands, refused where its squared run crosses its own household's house, beds, sheds or fixtures (`own_clear`) or another standing homestead (`others_clear`), nothing built on a lane
//!     the seating's corridor - NONE: the ground half of `Lawful`, claimed there

use super::access::Parts;
use super::gap_ways::Judge;
use super::standing::Standing;
use super::Counts;
use crate::field::fan::Pt;
use crate::field::geom::dist;
use crate::law::tree::{Tree, TREE};
use crate::ways::squaring::square_run;

/// The households' judge: the tree, each household's parts and house, and what stands that a way keeps off.
pub struct WaysJudge<'a> {
    /// The access tree.
    pub tree: Tree<'a>,
    /// Each household's parts.
    pub parts: Vec<Parts>,
    /// Each household's house's center.
    pub centers: Vec<Pt>,
    /// What stands, each household's own homestead set aside when its way is asked.
    pub standing: Standing<'a>,
}

impl WaysJudge<'_> {
    /// Does every leg of the run - the leg onto the tree passing where it has no length - pass `ok`?
    fn every_leg(run: &[Pt], ok: &mut dyn FnMut(Pt, Pt) -> bool) -> bool {
        let last = run.len().saturating_sub(2);
        run.windows(2)
            .enumerate()
            .all(|(n, w)| (n == last && dist(w[0], w[1]) < 1e-6) || ok(w[0], w[1]))
    }
}

impl Judge for WaysJudge<'_> {
    fn lawful_leg(&mut self, a: Pt, b: Pt, tests: &mut Counts) -> bool {
        let run = square_run(&[a, b], self.tree.waters, tests);
        self.tree.ground.on_lawful_ground(&run, TREE.0, None, tests)
    }

    fn tree_admits(&mut self, drawn: &[Pt], k: usize, tests: &mut Counts) -> bool {
        let laid = self.tree.laid(drawn, tests);
        if laid != drawn {
            let p = &self.parts[k];
            let own = Self::every_leg(&laid, &mut |a, b| {
                p.house_clear(a, b, tests)
                    && p.fixtures_clear(a, b, tests)
                    && p.parts_clear(a, b, tests)
            });
            let st = &mut self.standing;
            let mut inner = Counts::default();
            let others =
                own && Self::every_leg(&laid, &mut |a, b| st.clear(a, b, Some(k), &mut inner));
            for (key, n) in inner.0 {
                tests.add(&key, n);
            }
            if !others {
                return false;
            }
        }
        self.tree.admits(drawn, self.centers[k], tests)
    }

    fn reserve(&mut self, drawn: &[Pt], k: usize) {
        let mut t = Counts::default();
        self.tree.append(drawn, self.centers[k], &mut t);
    }
}
