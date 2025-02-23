from .triangle import R13IdealTriangle
from .line import R13Line
from .point import R13Point
from .horoball import R13Horoball
from . import r13_dot

from ..math_basics import is_RealIntervalFieldElement # type: ignore
from ..sage_helper import _within_sage # type: ignore

if _within_sage:
    import sage.all # type: ignore

__all__ = ['distance_r13_lines',
           'lower_bound_distance_r13_line_triangle']

def distance_r13_lines(line0 : R13Line, line1 : R13Line):
    """
    Computes distance between two hyperbolic lines.
    """

    p00 = r13_dot(line0.points[0], line1.points[0])
    p01 = r13_dot(line0.points[0], line1.points[1])
    p10 = r13_dot(line0.points[1], line1.points[0])
    p11 = r13_dot(line0.points[1], line1.points[1])

    pp = line0.inner_product * line1.inner_product

    t0 = _safe_sqrt((p00 * p11) / pp)
    t1 = _safe_sqrt((p01 * p10) / pp)

    p = (t0 + t1 - 1) / 2

    return 2 * _safe_sqrt(p).arcsinh()

def distance_r13_horoballs(horoball_defining_vec0,
                           horoball_defining_vec1):
    p = -r13_dot(horoball_defining_vec0, horoball_defining_vec1) / 2
    return _safe_log(p)

def distance_r13_horoball_line(horoball_defining_vec, # Light-like
                               line : R13Line):

    p = (r13_dot(line.points[0], horoball_defining_vec) *
         r13_dot(line.points[1], horoball_defining_vec))
    s = -2 * p / line.inner_product

    return _safe_log(s)/2

def distance_r13_horoball_plane(horoball_defining_vec, # Light-like
                                plane_defining_vec): # Space-like
    p = r13_dot(horoball_defining_vec, plane_defining_vec)
    return _safe_log_non_neg(p.abs())

def distance_r13_point_line(pt, # Time-like
                            line : R13Line):
    p = (r13_dot(line.points[0], pt) *
         r13_dot(line.points[1], pt))
    s = -2 * p / line.inner_product
    return _safe_arccosh(_safe_sqrt(s))

def distance_r13_point_plane(pt, # Time-like
                             plane_defining_vec): # Space-like
    p = r13_dot(pt, plane_defining_vec)
    return p.arcsinh().abs()

def lower_bound_distance_to_r13_triangle(
        geometric_object, triangle : R13IdealTriangle, verified : bool):
    if isinstance(geometric_object, R13Horoball):
        return lower_bound_distance_r13_horoball_triangle(
            geometric_object.defining_vec, triangle, verified)
    if isinstance(geometric_object, R13Line):
        return lower_bound_distance_r13_line_triangle(
            geometric_object, triangle, verified)
    if isinstance(geometric_object, R13Point):
        return lower_bound_distance_r13_point_triangle(
            geometric_object.point, triangle, verified)
    raise ValueError(
        "Distance between %r and triangle not supported" % geometric_object)

def lower_bound_distance_r13_horoball_triangle(
        horoball_defining_vec,
        triangle : R13IdealTriangle, verified : bool):

    if verified:
        epsilon = 0
    else:
        RF = horoball_defining_vec[0].parent()
        epsilon = _compute_epsilon(RF)

    for bounding_plane, edge in zip(triangle.bounding_planes,
                                    triangle.edges):
        if r13_dot(horoball_defining_vec, bounding_plane) > epsilon:
            return distance_r13_horoball_line(horoball_defining_vec, edge)

    return distance_r13_horoball_plane(
        horoball_defining_vec, triangle.plane)

def lower_bound_distance_r13_line_triangle(
        line : R13Line, triangle : R13IdealTriangle, verified : bool):

    if verified:
        epsilon = 0
    else:
        RF = line.points[0][0].parent()
        epsilon = _compute_epsilon(RF)

    a0 = r13_dot(triangle.plane, line.points[0])
    a1 = r13_dot(triangle.plane, line.points[1])

    abs0 = abs(a0)
    abs1 = abs(a1)

    pt = abs1 * line.points[0] + abs0 * line.points[1]

    for bounding_plane, edge in zip(triangle.bounding_planes,
                                    triangle.edges):
        if r13_dot(pt, bounding_plane) > epsilon:
            return distance_r13_lines(line, edge)

    p = a0 * a1

    if p > 0:
        return (-2 * p / line.inner_product).sqrt().arcsinh()

    RF = line.points[0][0].parent()
    return RF(0)

def lower_bound_distance_r13_point_triangle(
        point,
        triangle : R13IdealTriangle, verified : bool):

    if verified:
        epsilon = 0
    else:
        RF = point[0].parent()
        epsilon = _compute_epsilon(RF)

    for bounding_plane, edge in zip(triangle.bounding_planes,
                                    triangle.edges):
        if r13_dot(point, bounding_plane) > epsilon:
            return distance_r13_point_line(point, edge)

    return distance_r13_point_plane(point, triangle.plane)

def _compute_epsilon(RF):
    return RF(0.5) ** (RF.prec() // 2)

def _safe_sqrt(p):
    """
    Compute the sqrt of a number that is known to be non-negative
    though might not be non-negative because of floating point
    issues. When using interval arithmetic, this means that
    while the upper bound will be non-negative, the lower bound
    we computed might be negative because it is too conservative.

    Example of a quantity that can be given to this function:
    negative inner product of two vectors in the positive
    light cone. This is because we know that the inner product
    of two such vectors is always non-positive.
    """

    if is_RealIntervalFieldElement(p):
        RIF = p.parent()
        p = p.intersection(RIF(0, sage.all.Infinity))
    else:
        if p < 0:
            RF = p.parent()
            return RF(0)
    return p.sqrt()

def _safe_log(p):
    if is_RealIntervalFieldElement(p):
        RIF = p.parent()
        p = p.intersection(RIF(0, sage.all.Infinity))
    else:
        if p <= 0:
            RF = p.parent()
            return RF(-1e20)
    return p.log()

def _safe_log_non_neg(p):
    if p == 0:
        if is_RealIntervalFieldElement(p):
            RIF = p.parent()
            return RIF(-sage.all.Infinity)
        else:
            RF = p.parent()
            return RF(-1e20)
    else:
        return p.log()

def _safe_arccosh(p):
    if is_RealIntervalFieldElement(p):
        RIF = p.parent()
        p = p.intersection(RIF(1, sage.all.Infinity))
    else:
        if p < 0:
            RF = p.parent()
            return RF(0)
    return p.arccosh()
