from ..geometric_structure.cusp_neighborhood.cusp_cross_section import RealCuspCrossSection
from ..math_basics import correct_min
from ..verify.shapes import compute_hyperbolic_shapes
from ..matrix import matrix

__all__ = ['triangulation_dependent_cusp_area_matrix']

def triangulation_dependent_cusp_area_matrix(
                            snappy_manifold, bits_prec, verified):
    """
    Interesting case: t12521

    Maximal cusp area matrix:

    [ 77.5537626509970512653317518641810890989543820290380458409? 11.40953140648583915022197187043644048603871960228564151087?]
    [11.40953140648583915022197187043644048603871960228564151087?     91.1461442179608339668518063027198489593908228325190920?]

    This result:

    [  77.553762651?   11.409531407?]
    [  11.409531407? 5.508968850234?]

    After M.canonize:

    [  62.42018359?  11.409531407?]
    [ 11.409531407? 15.1140644993?]
    """
    # Get shapes, as intervals if requested
    shapes = compute_hyperbolic_shapes(
        snappy_manifold, verified=verified, bits_prec=bits_prec)

    # Compute cusp cross section, the code is agnostic about whether
    # the numbers are floating-point or intervals.
    # Note that the constructed cusp cross section will always be too "large"
    # and we need to scale them down (since during construction the
    # cross-section of each cusp will have one edge of length 1, the
    # corresponding tetrahedron does not intersect in "standard" form.)
    c = RealCuspCrossSection.fromManifoldAndShapes(snappy_manifold, shapes)

    # If no areas are given, scale (up or down) all the cusps so that
    # they are in standard form.
    c.ensure_std_form(allow_scaling_up=True)

    areas = c.cusp_areas()
    RIF = areas[0].parent()

    def entry(i, j):
        if i > j:
            i, j = j, i
        result = areas[i] * areas[j]
        if (i, j) in c._edge_dict:
            result *= correct_min(
                [ RIF(1), RealCuspCrossSection._exp_distance_of_edges(
                        c._edge_dict[(i,j)])]) ** 2
        return result

    n = len(areas)

    return matrix([[entry(i, j) for i in range(n)]
                   for j in range(n)])
