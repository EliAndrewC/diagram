"""The canvas-filling forest of a town or city (feature 145: moved out of woods.py, whose tree stands the hamlet path executes)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core import Settlement

from typing import TYPE_CHECKING, Any


class ForestMixin:
    def forest(self: Settlement, west_edge: Any, label: str = "", label_xy: Any = None) -> None:  # type: ignore[misc]
        """A woodland filling east of an irregular tree-line to the canvas edge, drawn as a stand of
        INDIVIDUAL TREES (see _tree_stand for the density research). Blocks houses. Deterministic
        (RNG saved/restored) so it never perturbs house placement. The TREE LINE is recorded
        separately from the filled polygon because the frame reveals only a shallow band of wood
        past it (crop_to_content) - deeper in it is undifferentiated canopy, i.e. wasted image."""
        pts = list(west_edge) + [(self.W + 12, west_edge[-1][1]), (self.W + 12, west_edge[0][1])]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        # the litter floor is pushed a crown's width BACK from the tree line (the canvas side stays
        # put) so its straight edge lies under the canopy and the trees alone make the wood's edge
        inset = self.px(self.CANOPY_R_FT)
        self._tree_stand(pts, seed=9, floor=[(x + inset, y) for x, y in west_edge] + pts[len(west_edge) :])
        self.block_polys.append(pts)
        self.M["forest"] = [[round(x, 1), round(y, 1)] for x, y in pts]
        self.M["forest_edge"] = [[round(x, 1), round(y, 1)] for x, y in west_edge]
        if label:
            lx, ly = label_xy if label_xy else (min(xs) + (self.W - min(xs)) / 2, (min(ys) + max(ys)) / 2)
            self.label(lx, ly, label, 14, italic=True, weight="bold", color="#22301A")
