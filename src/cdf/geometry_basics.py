"""
Geometry basics -- reusable Rhino.Geometry functions for Grasshopper.

Adding a new function with Copilot
-----------------------------------
1. Open this file and select this chat model, then ask Copilot something like:
   "Add a function here, all in Rhino geometry, that builds a <your shape/idea>.
   Follow the same style as create_cone / create_fractal_tree (defaults for
   optional inputs, a docstring listing params, return a Rhino.Geometry object)."
2. Once the function is added, ask Copilot:
   "Give me the Python code to use this function in a Grasshopper GHPython 3
   component, importing it from computational_design_and_fabrication."
3. Copy the snippet Copilot gives you into a GHPython component, wire up the
   inputs as sliders/panels, and set the output variable (e.g. `a`).
"""

import math
import Rhino.Geometry as rg


def offset_point(origin=None, x=0.0, y=0.0, z=0.0):
    """
    Create a point offset from an origin by world X, Y, and Z distances.

    origin : Rhino.Geometry.Point3d -- starting point (world origin by default)
    x      : float or None -- distance to add along world X (None defaults to 0)
    y      : float or None -- distance to add along world Y (None defaults to 0)
    z      : float or None -- distance to add along world Z (None defaults to 0)

    Returns a Rhino.Geometry.Point3d.
    """
    if origin is None:
        origin = rg.Point3d(0, 0, 0)
    elif not isinstance(origin, rg.Point3d):
        raise TypeError("origin must be a Rhino.Geometry.Point3d.")

    x = 0.0 if x is None else x
    y = 0.0 if y is None else y
    z = 0.0 if z is None else z

    return rg.Point3d(origin.X + x, origin.Y + y, origin.Z + z)


def create_cone(base_point=None, height=10.0, radius=5.0, cap_bottom=True):
    """
    Build a cone as a Brep.

    base_point : Rhino.Geometry.Point3d -- center of the cone's base circle
    height     : float -- cone height along the base plane's normal (Z by default)
    radius     : float -- base circle radius
    cap_bottom : bool  -- whether to cap the base circle (closed vs open cone)

    Returns a Rhino.Geometry.Brep.
    """
    if base_point is None:
        base_point = rg.Point3d(0, 0, 0)

    plane = rg.Plane(base_point, rg.Vector3d.ZAxis)
    cone = rg.Cone(plane, height, radius)
    return cone.ToBrep(cap_bottom)


def create_cylinder(origin=None, radius=5.0, height=10.0):
    """
    Build a capped cylinder as a Brep.

    origin : Rhino.Geometry.Point3d -- center of the cylinder's base (origin by default)
    radius : float -- radius of the base circle
    height : float -- cylinder height along the Z-axis

    Returns a Rhino.Geometry.Brep.
    """
    if origin is None:
        origin = rg.Point3d(0, 0, 0)

    plane = rg.Plane(origin, rg.Vector3d.ZAxis)
    circle = rg.Circle(plane, radius)
    cylinder = rg.Cylinder(circle, height)
    return cylinder.ToBrep(True, True)


def create_box(origin=None, length=10.0, width=10.0, height=10.0):
    """
    Build a box as a Brep from an origin point or plane and three dimensions.

    origin : Rhino.Geometry.Point3d or Rhino.Geometry.Plane -- lower corner (world XY if a point)
    length : float -- size along the origin plane's X-axis
    width : float -- size along the origin plane's Y-axis
    height : float -- size along the origin plane's Z-axis

    Returns a Rhino.Geometry.Brep.
    """
    if origin is None:
        origin = rg.Point3d(0, 0, 0)

    if isinstance(origin, rg.Plane):
        plane = origin
    elif isinstance(origin, rg.Point3d):
        plane = rg.Plane(origin, rg.Vector3d.ZAxis)
    else:
        raise TypeError("origin must be a Rhino.Geometry.Point3d or Rhino.Geometry.Plane.")

    box = rg.Box(
        plane,
        rg.Interval(0, length),
        rg.Interval(0, width),
        rg.Interval(0, height),
    )
    return box.ToBrep()




def create_sphere(center_point=None, radius=5.0):
    """
    Build a sphere as a Brep.

    center_point : Rhino.Geometry.Point3d -- center of the sphere (origin by default)
    radius       : float -- sphere radius

    Returns a Rhino.Geometry.Brep.
    """
    if center_point is None:
        center_point = rg.Point3d(0, 0, 5)

    sphere = rg.Sphere(center_point, radius)
    return sphere.ToBrep()


def create_torus(origin=None, major_radius=10.0, minor_radius=2.0):
    """
    Build a torus as a Brep.

    origin       : Rhino.Geometry.Point3d or Rhino.Geometry.Plane -- center and axis orientation
    major_radius : float -- distance from the torus center to the tube center
    minor_radius : float -- radius of the circle revolved around the axis

    Returns a Rhino.Geometry.Brep.
    """
    if origin is None:
        origin = rg.Point3d(0, 0, 0)

    if isinstance(origin, rg.Plane):
        plane = origin
    elif isinstance(origin, rg.Point3d):
        plane = rg.Plane(origin, rg.Vector3d.ZAxis)
    else:
        raise TypeError("origin must be a Rhino.Geometry.Point3d or Rhino.Geometry.Plane.")

    torus = rg.Torus(plane, major_radius, minor_radius)
    return torus.ToBrep()



def boolean_difference(brep_a, brep_b):
    """
    Perform a boolean difference operation between two Breps.

    brep_a : Rhino.Geometry.Brep -- the first Brep
    brep_b : Rhino.Geometry.Brep -- the second Brep to subtract from the first

    Returns a list of Rhino.Geometry.Brep resulting from the difference.
    """
    if brep_a is None or brep_b is None:
        raise ValueError("Both brep_a and brep_b must be provided.")

    result = rg.Brep.CreateBooleanDifference(brep_a, brep_b, 0.001)
    return result


def copy_brep_along_z(brep, distance, copy_count):
    """
    Create copies of a Brep, each offset in the +Z direction.

    brep : Rhino.Geometry.Brep -- the Brep to copy
    distance : float -- the Z spacing between consecutive copies
    copy_count : int -- the number of copies to create

    Returns a list of Rhino.Geometry.Brep copies; copy i is moved by distance * (i + 1).
    """
    if brep is None:
        raise ValueError("brep must be provided.")
    if copy_count < 0:
        raise ValueError("copy_count must not be negative.")

    copies = []
    for i in range(1, int(copy_count) + 1):
        copy = brep.DuplicateBrep()
        copy.Transform(rg.Transform.Translation(rg.Vector3d(0, 0, distance * i)))
        copies.append(copy)
    return copies


def create_windowed_building(
    origin=None,
    building_width=20.0,
    building_depth=10.0,
    building_height=20.0,
    window_width=2.0,
    window_depth=1.0,
    window_height=2.0,
    spacing=1.0,
    tolerance=0.001,
):
    """
    Cut centered grids of rectangular windows into all four vertical faces of a box.

    origin         : Rhino.Geometry.Point3d or Rhino.Geometry.Plane -- lower corner and orientation
    building_width : float -- building size along the origin plane's X-axis
    building_depth : float -- building size along the origin plane's Y-axis
    building_height: float -- building size along the origin plane's Z-axis
    window_width   : float -- window size across each face
    window_depth   : float -- recess depth into the building from each face
    window_height  : float -- window size along the building's Z-axis
    spacing        : float -- minimum gap between windows and edges (at least 1)
    tolerance      : float -- Rhino boolean operation tolerance

    Returns a list of Rhino.Geometry.Brep results.
    """
    if origin is None:
        origin = rg.Point3d(0, 0, 0)

    if isinstance(origin, rg.Plane):
        building_plane = origin
    elif isinstance(origin, rg.Point3d):
        building_plane = rg.Plane(origin, rg.Vector3d.ZAxis)
    else:
        raise TypeError("origin must be a Rhino.Geometry.Point3d or Rhino.Geometry.Plane.")

    dimensions = (
        building_width,
        building_depth,
        building_height,
        window_width,
        window_depth,
        window_height,
    )
    if any(dimension <= 0 for dimension in dimensions):
        raise ValueError("Building and window dimensions must all be greater than zero.")
    if spacing < 1.0:
        raise ValueError("spacing must be at least 1.0.")
    if window_depth > min(building_width, building_depth):
        raise ValueError(
            "window_depth must not be greater than the smaller building footprint dimension."
        )
    if tolerance <= 0:
        raise ValueError("tolerance must be greater than zero.")

    building = create_box(
        building_plane,
        length=building_width,
        width=building_depth,
        height=building_height,
    )

    corner_clearance = max(spacing, window_depth)

    def window_positions(span, window_size, edge_clearance):
        count = max(
            0,
            int(
                math.floor(
                    (span - 2 * edge_clearance + spacing)
                    / (window_size + spacing)
                )
            ),
        )
        occupied = count * window_size + max(0, count - 1) * spacing
        first = (span - occupied) / 2.0
        return [first + index * (window_size + spacing) for index in range(count)]

    front_positions = window_positions(
        building_width, window_width, corner_clearance
    )
    side_positions = window_positions(
        building_depth, window_width, corner_clearance
    )
    height_positions = window_positions(
        building_height, window_height, spacing
    )

    window_boxes = []
    for z in height_positions:
        for x in front_positions:
            front_origin = (
                building_plane.Origin
                + building_plane.XAxis * x
                + building_plane.ZAxis * z
            )
            back_origin = (
                building_plane.Origin
                + building_plane.XAxis * (x + window_width)
                + building_plane.YAxis * building_depth
                + building_plane.ZAxis * z
            )
            window_boxes.extend(
                (
                    create_box(
                        rg.Plane(
                            front_origin,
                            building_plane.XAxis,
                            building_plane.YAxis,
                        ),
                        length=window_width,
                        width=window_depth,
                        height=window_height,
                    ),
                    create_box(
                        rg.Plane(
                            back_origin,
                            -building_plane.XAxis,
                            -building_plane.YAxis,
                        ),
                        length=window_width,
                        width=window_depth,
                        height=window_height,
                    ),
                )
            )

        for y in side_positions:
            left_origin = (
                building_plane.Origin
                + building_plane.YAxis * (y + window_width)
                + building_plane.ZAxis * z
            )
            right_origin = (
                building_plane.Origin
                + building_plane.XAxis * building_width
                + building_plane.YAxis * y
                + building_plane.ZAxis * z
            )
            window_boxes.extend(
                (
                    create_box(
                        rg.Plane(
                            left_origin,
                            -building_plane.YAxis,
                            building_plane.XAxis,
                        ),
                        length=window_width,
                        width=window_depth,
                        height=window_height,
                    ),
                    create_box(
                        rg.Plane(
                            right_origin,
                            building_plane.YAxis,
                            -building_plane.XAxis,
                        ),
                        length=window_width,
                        width=window_depth,
                        height=window_height,
                    ),
                )
            )

    if not window_boxes:
        return [building]

    result = rg.Brep.CreateBooleanDifference([building], window_boxes, tolerance)
    if result is None or len(result) == 0:
        raise RuntimeError("Boolean difference failed while cutting the window openings.")
    return result
