from .check_core_curve import check_away_from_core_curve_iter
from .canonical_keys import canonical_keys_function_for_line
from .geodesic_info import GeodesicInfo

from ...tiling.tile import Tile, compute_tiles

from ...snap.t3mlite import Mcomplex # type: ignore

from typing import Sequence

def compute_tiles_for_geodesic(mcomplex : Mcomplex,
                               geodesic : GeodesicInfo
                               ) -> Sequence[Tile]:
    """
    Computes all GeodesicPiece's needed to cover a tube about the
    given closed geodesic in the given manifold. The geodesic cannot be
    a core curve of a filled cusp.

    A GeodesicTube is constructed from a triangulation with a suitable
    geometric structure and a suitable GeodesicInfo object.

    To add the necessary geometric structure to a triangulation, call
    add_r13_geometry and add_r13_planes_to_tetrahedra.

    The GeodesicInfo object needs to be constructed with a line and
    GeodesicInfo.find_tet_or_core_curve be called on it.

    Calling GeodesicInfo.add_pieces_for_radius will then add the
    necessary pieces to GeodesicInfo.pieces to cover the tube of the
    given radius.
    """

    if geodesic.line is None:
        raise ValueError(
            "GeodesicTube expected GeodesicInfo with line set to start "
            "developing a tube about the geodesic.")

    if not geodesic.lifted_tetrahedra:
        raise ValueError(
            "GeodesicTube expected GeodesicInfo with lifted_tetrahedra "
            "set to start developing a tube about the geodesic.")

    if mcomplex.verified:
        core_curve_epsilon = 0
    else:
        core_curve_epsilon = _compute_epsilon(mcomplex.RF)
        
    return check_away_from_core_curve_iter(
        compute_tiles(
            geodesic.line.r13_line,
            mcomplex.R13_baseTetInCenter,
            canonical_keys_function_for_line(geodesic.line),
            False,
            -(mcomplex.baseTetInRadius/2).cosh(),
            geodesic.lifted_tetrahedra,
            mcomplex.verified),
        epsilon = core_curve_epsilon,
        obj_name = 'Geodesic %s' % geodesic.word)

def _compute_epsilon(RF):
    return RF(0.5) ** (RF.prec() // 2 - 8)
