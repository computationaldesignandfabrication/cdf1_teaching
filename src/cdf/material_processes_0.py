"""
Material processes 0 -- sand pouring as Rhino.Geometry functions for Grasshopper.

Python versions of exercises/material-processes-0/sand_pouring_geometric.ghx:

* sand_ridge_along_curve           -- a sand ridge poured along a curve
                                      (constant radius and height)
* sand_ridge_along_curve_variable  -- several ridges along the same curve, one
                                      per (radius, height) pair
* sand_cones_at_points             -- sand cones of a given volume poured at points,
                                      unioned into piles

Use in a GHPython 3 component, for example:

    from cdf.material_processes_0 import sand_ridge_along_curve
    a = sand_ridge_along_curve(curve, radius, height)

where `curve` is a Curve input (Item Access) and `radius` / `height` are sliders.
"""

import math
import Rhino.Geometry as rg

_BLEND_CONTINUITY = [
    rg.BlendContinuity.Position,
    rg.BlendContinuity.Tangency,
    rg.BlendContinuity.Curvature,
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _offset_curve(curve, distance, tolerance):
    """Offset a curve in World XY with sharp corners and return a single curve."""
    result = curve.Offset(
        rg.Plane.WorldXY, distance, tolerance, rg.CurveOffsetCornerStyle.Sharp
    )
    if not result:
        raise ValueError("Could not offset curve by {}.".format(distance))
    if len(result) > 1:
        result = rg.Curve.JoinCurves(result, tolerance)
    return result[0]


def _blend(curve_a, curve_b, continuity):
    """Blend from the end of curve_a to the start of curve_b (bulge 1, 1)."""
    index = max(0, min(2, int(continuity)))
    return rg.Curve.CreateBlendCurve(curve_a, curve_b, _BLEND_CONTINUITY[index], 1.0, 1.0)


def _flipped(curve):
    copy = curve.DuplicateCurve()
    copy.Reverse()
    return copy


def _loft(curve_a, curve_b, loft_type=rg.LoftType.Normal):
    breps = rg.Brep.CreateFromLoft(
        [curve_a, curve_b], rg.Point3d.Unset, rg.Point3d.Unset, loft_type, False
    )
    if not breps:
        raise ValueError("Loft failed.")
    return breps[0]


def _cap(curves, tolerance):
    """Join curves into a closed loop and fill it (planar if possible, else a patch)."""
    joined = rg.Curve.JoinCurves(curves, tolerance)
    if not joined:
        raise ValueError("Could not join cap curves.")
    loop = joined[0]
    planar = rg.Brep.CreatePlanarBreps(loop, tolerance)
    if planar:
        return planar[0]
    patch = rg.Brep.CreatePatch([loop], 10, 10, tolerance)
    if patch is None:
        raise ValueError("Could not fill cap curve.")
    return patch


def _ridge_brep(curve, heights, offset_left, offset_right, count, crest_width,
                continuity, tolerance):
    """
    Shared builder for the two curve functions.

    curve        : Rhino.Geometry.Curve -- pouring path (in World XY)
    heights      : list of float -- height per pour point (last value repeats)
    offset_left  : float -- base offset distance on the positive side
    offset_right : float -- base offset distance on the negative side
    """
    if curve is None:
        raise ValueError("curve must be provided.")
    if not heights:
        raise ValueError("At least one height must be given.")

    # Divide the curve into pour points and lift each one to its cone tip.
    params = curve.DivideByCount(int(count), True)
    tips = []
    for i, t in enumerate(params):
        point = curve.PointAt(t)
        h = heights[min(i, len(heights) - 1)]
        tips.append(rg.Point3d(point.X, point.Y, point.Z + h))

    # Crest: a curve through the tips, widened slightly so it can be capped.
    crest = rg.Curve.CreateInterpolatedCurve(tips, 3, rg.CurveKnotStyle.Chord)
    top_a = _offset_curve(crest, crest_width, tolerance)
    top_b = _offset_curve(crest, -crest_width, tolerance)

    # Base: the pouring curve offset to both sides.
    base_a = _offset_curve(curve, offset_left, tolerance)
    base_b = _offset_curve(curve, -offset_right, tolerance)

    # Rounded ends: blend the two sides together at the end and the start.
    base_end = _blend(base_a, _flipped(base_b), continuity)
    base_start = _blend(_flipped(base_a), base_b, continuity)
    top_end = _blend(top_a, _flipped(top_b), continuity)
    top_start = _blend(_flipped(top_a), top_b, continuity)

    parts = [
        _loft(base_a, top_a),                                  # side A
        _loft(base_b, top_b),                                  # side B
        _loft(base_end, top_end, rg.LoftType.Straight),        # end face
        _loft(base_start, top_start, rg.LoftType.Straight),    # start face
        _cap([base_end, base_start, base_a, base_b], tolerance),  # bottom
        _cap([top_end, top_start, top_a, top_b], tolerance),      # crest
    ]
    return list(rg.Brep.JoinBreps(parts, tolerance))


# ---------------------------------------------------------------------------
# 1. ridge along a curve
# ---------------------------------------------------------------------------


def sand_ridge_along_curve(
    curve,
    radius=19.0,
    height=25.0,
    count=10,
    crest_width=0.1,
    continuity=1,
    tolerance=0.001,
):
    """
    Build a sand ridge poured along a curve.

    curve       : Rhino.Geometry.Curve -- pouring path, lying in World XY
    radius      : float -- base half-width (offset to each side of the curve)
    height      : float -- height of the ridge above the curve
    count       : int   -- number of segments the curve is divided into
    crest_width : float -- half-width of the flat crest along the top
    continuity  : int   -- end blend continuity: 0 position, 1 tangency, 2 curvature
    tolerance   : float -- model tolerance for offsets and joins

    Returns a list of Rhino.Geometry.Brep (one closed Brep when the join succeeds).
    """
    return _ridge_brep(
        curve, [height], radius, radius, count, crest_width, continuity, tolerance
    )


# ---------------------------------------------------------------------------
# 2. ridge along a curve with varying widths / heights
# ---------------------------------------------------------------------------


def sand_ridge_along_curve_variable(
    curve,
    radii=None,
    heights=None,
    count=10,
    crest_width=0.1,
    continuity=1,
    tolerance=0.001,
):
    """
    Build several sand ridges along the same curve, one per (radius, height) pair.

    Each radius is used for both the left and the right side of its ridge, so
    radii [27, 18] with heights [22, 15] give a wide, tall ridge (r 27, h 22)
    and a narrower, lower one (r 18, h 15) poured along the same path.

    curve       : Rhino.Geometry.Curve -- pouring path, lying in World XY
    radii       : list of float -- base half-width of each ridge. Default [27, 18].
    heights     : list of float -- height of each ridge. Default [22, 15].
                  If radii and heights have different lengths, the last value of
                  the shorter list is repeated (Grasshopper "longest list").
    count       : int   -- number of segments the curve is divided into
    crest_width : float -- half-width of the crest along the top
    continuity  : int   -- end blend continuity: 0 position, 1 tangency, 2 curvature
    tolerance   : float -- model tolerance for offsets and joins

    Returns a list of Rhino.Geometry.Brep, one ridge per pair.
    """
    if radii is None:
        radii = [27.0, 18.0]
    if heights is None:
        heights = [22.0, 15.0]
    if not isinstance(radii, (list, tuple)):
        radii = [radii]
    if not isinstance(heights, (list, tuple)):
        heights = [heights]
    if not radii or not heights:
        raise ValueError("radii and heights must not be empty.")

    ridges = []
    for i in range(max(len(radii), len(heights))):
        radius = float(radii[min(i, len(radii) - 1)])
        height = float(heights[min(i, len(heights) - 1)])
        ridges.extend(
            _ridge_brep(
                curve, [height], radius, radius, count, crest_width, continuity,
                tolerance,
            )
        )
    return ridges


# ---------------------------------------------------------------------------
# 3. cones at points
# ---------------------------------------------------------------------------


def sand_cones_at_points(points, volumes, slope_angle=34.0, tolerance=0.001):
    """
    Pour a sand cone of a given volume at each point and union overlapping cones.

    points      : list of Rhino.Geometry.Point3d -- cone locations (Z is ignored,
                  every cone base sits on World XY at Z = 0)
    volumes     : list of float -- positive cone volume per point (model units cubed)
    slope_angle : float -- angle of repose of the sand, in degrees above horizontal
    tolerance   : float -- tolerance for the boolean union

    Returns a tuple (cones, breps, status):
        cones  : list of Rhino.Geometry.Brep -- individual capped cones
        breps  : list of Rhino.Geometry.Brep -- unioned result (the cones if the
                 union fails)
        status : str -- description of the union result
    """
    points = list(points or [])
    volumes = list(volumes or [])
    if len(points) != len(volumes):
        raise ValueError("points and volumes must have the same number of items.")

    slope = math.tan(math.radians(slope_angle))
    down = rg.Vector3d(0.0, 0.0, -1.0)

    cones = []
    for index, (point, volume) in enumerate(zip(points, volumes)):
        volume = float(volume)
        if not math.isfinite(volume) or volume <= 0.0:
            raise ValueError(
                "Volume at index {} must be positive and finite.".format(index)
            )

        # V = pi * r^2 * h / 3 with r = h / tan(slope)  ->  solve for h
        height = (3.0 * volume * slope * slope / math.pi) ** (1.0 / 3.0)
        radius = height / slope
        apex = rg.Point3d(point.X, point.Y, height)
        cone = rg.Cone(rg.Plane(apex, down), height, radius)
        if not cone.IsValid:
            raise ValueError("Could not create a valid cone for point {}.".format(index))
        cones.append(cone.ToBrep(True))

    union = rg.Brep.CreateBooleanUnion(cones, tolerance) if cones else None
    breps = [b for b in union if b is not None] if union else []

    if breps:
        status = "Solid union succeeded: {} Brep(s) from {} cone(s).".format(
            len(breps), len(cones)
        )
    elif cones:
        breps = cones
        status = "Warning: solid union failed; returning the {} cone(s).".format(
            len(cones)
        )
    else:
        status = "No cones to union."

    return cones, breps, status
