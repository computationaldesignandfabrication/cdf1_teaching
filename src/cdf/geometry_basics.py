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
import random
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


def boolean_difference_second(brep_a, brep_b, tolerance=0.001):
    """
    Return only the part of the second Brep outside the first Brep (B - A).

    brep_a    : Rhino.Geometry.Brep -- geometry to subtract from the second Brep
    brep_b    : Rhino.Geometry.Brep -- geometry whose non-overlapping part is kept
    tolerance : float -- Rhino boolean operation tolerance

    Returns a list of Rhino.Geometry.Brep results; an empty list means no part
    of brep_b remains outside brep_a.
    """
    if brep_a is None or brep_b is None:
        raise ValueError("Both brep_a and brep_b must be provided.")
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance must be greater than zero.")

    result = rg.Brep.CreateBooleanDifference([brep_b], [brep_a], tolerance)
    if result is None:
        raise RuntimeError("Boolean difference failed for brep_b minus brep_a.")
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


def create_building(
    origin=None,
    building_width=30.0,
    building_depth=20.0,
    building_height=30.0,
    window_width=3.0,
    window_height=4.0,
    window_depth=1.0,
    spacing=2.0,
    tolerance=0.001,
):
    """
    Create a box building with regularly spaced recessed windows on four sides.

    origin         : Rhino.Geometry.Point3d -- lower corner of the building
    building_width : float -- building size along world X
    building_depth : float -- building size along world Y
    building_height: float -- building size along world Z
    window_width   : float -- window width along each facade
    window_height  : float -- window height
    window_depth   : float -- recess depth into the building
    spacing        : float -- clear gap between adjacent windows
    tolerance      : float -- Rhino boolean tolerance

    Returns a list of Rhino.Geometry.Brep results.
    """
    if origin is None:
        origin = rg.Point3d(0, 0, 0)
    elif not isinstance(origin, rg.Point3d):
        raise TypeError("origin must be a Rhino.Geometry.Point3d.")

    dimensions = (
        building_width,
        building_depth,
        building_height,
        window_width,
        window_height,
        window_depth,
        tolerance,
    )
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("Building, window, and tolerance dimensions must be positive.")
    if not math.isfinite(spacing) or spacing < 0:
        raise ValueError("spacing must be zero or greater.")
    if window_depth * 2 >= min(building_width, building_depth):
        raise ValueError(
            "window_depth must be less than half the smaller building footprint dimension."
        )

    building = create_box(
        origin,
        length=building_width,
        width=building_depth,
        height=building_height,
    )

    cutter_overrun = tolerance * 2.0
    edge_clearance = max(2.0, window_depth + cutter_overrun)

    def centered_positions(span, item_size, margin):
        usable_span = span - 2.0 * margin
        if usable_span < item_size:
            return []
        count = int((usable_span + spacing) // (item_size + spacing))
        occupied = count * item_size + max(0, count - 1) * spacing
        first = (span - occupied) / 2.0
        return [first + index * (item_size + spacing) for index in range(count)]

    x_positions = centered_positions(
        building_width, window_width, edge_clearance
    )
    y_positions = centered_positions(
        building_depth, window_width, edge_clearance
    )
    z_positions = centered_positions(building_height, window_height, 2.0    )
    window_boxes = []

    for z in z_positions:
        for x in x_positions:
            window_origin = origin + rg.Vector3d(x, -cutter_overrun, z)
            window_boxes.append(
                create_box(
                    window_origin,
                    length=window_width,
                    width=window_depth + cutter_overrun,
                    height=window_height,
                )
            )
            window_origin = origin + rg.Vector3d(
                x,
                building_depth - window_depth,
                z,
            )
            window_boxes.append(
                create_box(
                    window_origin,
                    length=window_width,
                    width=window_depth + cutter_overrun,
                    height=window_height,
                )
            )

        for y in y_positions:
            window_origin = origin + rg.Vector3d(-cutter_overrun, y, z)
            window_boxes.append(
                create_box(
                    window_origin,
                    length=window_depth + cutter_overrun,
                    width=window_width,
                    height=window_height,
                )
            )
            window_origin = origin + rg.Vector3d(
                building_width - window_depth,
                y,
                z,
            )
            window_boxes.append(
                create_box(
                    window_origin,
                    length=window_depth + cutter_overrun,
                    width=window_width,
                    height=window_height,
                )
            )

    if not window_boxes:
        return [building]

    result = rg.Brep.CreateBooleanDifference([building], window_boxes, tolerance)
    if result is None or len(result) == 0:
        raise RuntimeError("Boolean difference failed while cutting the windows.")
    return result


def create_spiral(
    origin=None,
    radius=10.0,
    height=20.0,
    revolutions=3.0,
    points_per_revolution=24,
):
    """
    Create a smooth helical curve around a vertical axis through origin.

    The curve follows x = cx + r*cos(t), y = cy + r*sin(t), and
    z = cz + height*t/(2*pi*revolutions), for t from 0 to 2*pi*revolutions.

    origin                  : Rhino.Geometry.Point3d -- center of the spiral axis
    radius                  : float -- distance from the axis to the curve
    height                  : float -- total vertical rise
    revolutions             : float -- number of complete turns
    points_per_revolution   : int -- sampling density used to build the curve

    Returns a Rhino.Geometry.Curve.
    """
    if origin is None:
        origin = rg.Point3d(0, 0, 0)
    elif not isinstance(origin, rg.Point3d):
        raise TypeError("origin must be a Rhino.Geometry.Point3d.")

    if not math.isfinite(radius) or radius <= 0:
        raise ValueError("radius must be greater than zero.")
    if not math.isfinite(height) or height <= 0:
        raise ValueError("height must be greater than zero.")
    if not math.isfinite(revolutions) or revolutions <= 0:
        raise ValueError("revolutions must be greater than zero.")
    if (
        int(points_per_revolution) != points_per_revolution
        or points_per_revolution < 3
    ):
        raise ValueError("points_per_revolution must be a whole number of at least 3.")
    points_per_revolution = int(points_per_revolution)

    sample_count = max(3, int(math.ceil(revolutions * points_per_revolution)))
    points = []
    for index in range(sample_count + 1):
        fraction = index / float(sample_count)
        angle = 2.0 * math.pi * revolutions * fraction
        points.append(
            rg.Point3d(
                origin.X + radius * math.cos(angle),
                origin.Y + radius * math.sin(angle),
                origin.Z + height * fraction,
            )
        )

    curve = rg.Curve.CreateInterpolatedCurve(points, 3)
    if curve is None:
        raise RuntimeError("Rhino failed to interpolate the spiral curve.")
    return curve


def create_spheres_along_spiral(
    origin=None,
    spiral_radius=10.0,
    spiral_height=20.0,
    revolutions=3.0,
    sphere_radius=1.0,
    additional_spheres=5,
    points_per_revolution=24,
):
    """
    Create a spiral and place a sphere at its start and additional spheres along it.

    origin                  : Rhino.Geometry.Point3d -- center of the spiral axis
    spiral_radius           : float -- distance from the axis to the spiral
    spiral_height           : float -- vertical rise of the spiral
    revolutions             : float -- number of complete turns in the spiral
    sphere_radius           : float -- radius of every sphere
    additional_spheres      : int -- number of spheres after the starting sphere
    points_per_revolution   : int -- curve sampling density

    Returns a list of Rhino.Geometry.Brep spheres.
    """
    if not math.isfinite(sphere_radius) or sphere_radius <= 0:
        raise ValueError("sphere_radius must be greater than zero.")
    if int(additional_spheres) != additional_spheres or additional_spheres < 0:
        raise ValueError("additional_spheres must be a non-negative whole number.")
    additional_spheres = int(additional_spheres)

    curve = create_spiral(
        origin=origin,
        radius=spiral_radius,
        height=spiral_height,
        revolutions=revolutions,
        points_per_revolution=points_per_revolution,
    )
    start_point = curve.PointAtNormalizedLength(0.0)
    spheres = [create_sphere(start_point, radius=sphere_radius)]
    if additional_spheres == 0:
        return spheres

    for index in range(1, additional_spheres + 1):
        path_point = curve.PointAtNormalizedLength(
            index / float(additional_spheres)
        )
        sphere = spheres[0].DuplicateBrep()
        sphere.Transform(
            rg.Transform.Translation(
                rg.Vector3d(
                    path_point.X - start_point.X,
                    path_point.Y - start_point.Y,
                    path_point.Z - start_point.Z,
                )
            )
        )
        spheres.append(sphere)

    return spheres


def create_xy_array(geometry, count_x=3, count_y=3, gap=1.0):
    """
    Duplicate Rhino geometry into an X-Y array with clear gaps between copies.

    geometry : Rhino.Geometry.GeometryBase -- object to duplicate
    count_x  : int -- number of copies along world X
    count_y  : int -- number of copies along world Y
    gap      : float -- minimum clear gap between neighboring bounding boxes

    Returns a list of duplicated Rhino geometry objects, including the original position.
    """
    if not isinstance(geometry, rg.GeometryBase):
        raise TypeError("geometry must be a Rhino.Geometry.GeometryBase object.")
    if int(count_x) != count_x or count_x < 1:
        raise ValueError("count_x must be a positive whole number.")
    if int(count_y) != count_y or count_y < 1:
        raise ValueError("count_y must be a positive whole number.")
    if not math.isfinite(gap) or gap <= 0:
        raise ValueError("gap must be greater than zero to keep copies from touching.")

    count_x = int(count_x)
    count_y = int(count_y)
    bounds = geometry.GetBoundingBox(True)
    if not bounds.IsValid:
        raise ValueError("geometry must have a valid bounding box.")

    step_x = bounds.Max.X - bounds.Min.X + gap
    step_y = bounds.Max.Y - bounds.Min.Y + gap
    copies = []

    for row in range(count_y):
        for column in range(count_x):
            duplicate = geometry.Duplicate()
            if duplicate is None:
                raise RuntimeError("Rhino failed to duplicate the input geometry.")
            if row or column:
                translation = rg.Transform.Translation(
                    rg.Vector3d(column * step_x, row * step_y, 0)
                )
                if not duplicate.Transform(translation):
                    raise RuntimeError("Rhino failed to transform an array copy.")
            copies.append(duplicate)

    return copies


def create_building_array(buildings, count_x=3, count_y=3, gap=1.0, seed=0):
    """
    Array one Brep building or a Brep group in XY with random rotations.

    buildings : Rhino.Geometry.Brep or sequence of Breps forming one building
    count_x   : int -- number of building positions along world X
    count_y   : int -- number of building positions along world Y
    gap       : float -- minimum clear gap between the rotated building bounds
    seed      : int -- seed for reproducible random rotations

    Each shifted building is rotated about its own center by a random angle
    between -15 and +15 degrees. The first building remains unrotated.
    Returns a flat list of Rhino.Geometry.Brep objects.
    """
    if isinstance(buildings, rg.Brep):
        building_parts = [buildings]
    else:
        building_parts = list(buildings)
    if not building_parts or any(not isinstance(part, rg.Brep) for part in building_parts):
        raise TypeError("buildings must be a Brep or a non-empty sequence of Breps.")
    if int(count_x) != count_x or count_x < 1:
        raise ValueError("count_x must be a positive whole number.")
    if int(count_y) != count_y or count_y < 1:
        raise ValueError("count_y must be a positive whole number.")
    if not math.isfinite(gap) or gap <= 0:
        raise ValueError("gap must be greater than zero.")

    count_x = int(count_x)
    count_y = int(count_y)
    bounds = [part.GetBoundingBox(True) for part in building_parts]
    if any(not bound.IsValid for bound in bounds):
        raise ValueError("Every building Brep must have a valid bounding box.")

    min_x = min(bound.Min.X for bound in bounds)
    min_y = min(bound.Min.Y for bound in bounds)
    max_x = max(bound.Max.X for bound in bounds)
    max_y = max(bound.Max.Y for bound in bounds)
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    half_width = (max_x - min_x) / 2.0
    half_depth = (max_y - min_y) / 2.0
    rotation_safe_diameter = 2.0 * math.hypot(half_width, half_depth)
    step_x = rotation_safe_diameter + gap
    step_y = rotation_safe_diameter + gap

    rng = random.Random(seed)
    rotation_limit = math.radians(15.0)
    placed_parts = []
    for row in range(count_y):
        for column in range(count_x):
            dx = column * step_x
            dy = row * step_y
            angle = 0.0 if row == 0 and column == 0 else rng.uniform(
                -rotation_limit, rotation_limit
            )
            target_center = rg.Point3d(center_x + dx, center_y + dy, 0.0)
            translation = rg.Transform.Translation(rg.Vector3d(dx, dy, 0.0))
            rotation = rg.Transform.Rotation(angle, rg.Vector3d.ZAxis, target_center)

            for part in building_parts:
                duplicate = part.DuplicateBrep()
                if duplicate is None:
                    raise RuntimeError("Rhino failed to duplicate a building Brep.")
                if (dx or dy) and not duplicate.Transform(translation):
                    raise RuntimeError("Rhino failed to translate an array copy.")
                if angle and not duplicate.Transform(rotation):
                    raise RuntimeError("Rhino failed to rotate an array copy.")
                placed_parts.append(duplicate)

    return placed_parts


def create_building_cutouts(
    buildings,
    cutter_count=30,
    min_width=2.0,
    max_width=5.0,
    min_depth=2.0,
    max_depth=5.0,
    min_height=3.0,
    max_height=10.0,
    tolerance=0.001,
    seed=0,
):
    """
    Cut varied box-shaped voids into an existing building or building array.

    The generated boxes are used only as boolean cutters and are not returned.
    Their XY positions are sampled within the combined building bounds, and
    they start at the lowest building elevation.

    buildings    : Rhino.Geometry.Brep or sequence of Breps to cut
    cutter_count : int -- number of box-shaped voids to generate
    min_width    : float -- minimum cutter size along world X
    max_width    : float -- maximum cutter size along world X
    min_depth    : float -- minimum cutter size along world Y
    max_depth    : float -- maximum cutter size along world Y
    min_height   : float -- minimum cutter height
    max_height   : float -- maximum cutter height
    tolerance    : float -- Rhino boolean operation tolerance
    seed         : int -- seed for reproducible cutter placement and dimensions

    Returns only the building Breps remaining after the boolean differences.
    """
    if isinstance(buildings, rg.Brep):
        building_parts = [buildings]
    else:
        building_parts = list(buildings)
    if not building_parts or any(not isinstance(part, rg.Brep) for part in building_parts):
        raise TypeError("buildings must be a Brep or a non-empty sequence of Breps.")
    if int(cutter_count) != cutter_count or cutter_count < 0:
        raise ValueError("cutter_count must be a non-negative whole number.")
    cutter_count = int(cutter_count)

    dimensions = (
        min_width,
        max_width,
        min_depth,
        max_depth,
        min_height,
        max_height,
        tolerance,
    )
    if any(not math.isfinite(value) or value <= 0 for value in dimensions):
        raise ValueError("Cutter dimensions and tolerance must be greater than zero.")
    if min_width > max_width or min_depth > max_depth or min_height > max_height:
        raise ValueError("Each minimum cutter dimension must not exceed its maximum.")

    bounds = [building.GetBoundingBox(True) for building in building_parts]
    if any(not bound.IsValid for bound in bounds):
        raise ValueError("Every building Brep must have a valid bounding box.")
    if cutter_count == 0:
        return [building.DuplicateBrep() for building in building_parts]

    placement_targets = [
        (building, bound)
        for building, bound in zip(building_parts, bounds)
        if bound.Max.X - bound.Min.X >= min_width
        and bound.Max.Y - bound.Min.Y >= min_depth
    ]
    if not placement_targets:
        raise ValueError(
            "At least one building footprint must fit the minimum cutter width and depth."
        )

    rng = random.Random(seed)
    cutters = []
    cutter_bounds = []
    for _ in range(cutter_count):
        _, target_bound = rng.choice(placement_targets)
        width = rng.uniform(
            min_width,
            min(max_width, target_bound.Max.X - target_bound.Min.X),
        )
        depth = rng.uniform(
            min_depth,
            min(max_depth, target_bound.Max.Y - target_bound.Min.Y),
        )
        height = rng.uniform(min_height, max_height)
        x = rng.uniform(target_bound.Min.X, target_bound.Max.X - width)
        y = rng.uniform(target_bound.Min.Y, target_bound.Max.Y - depth)
        cutter = create_box(
            rg.Point3d(x, y, target_bound.Min.Z),
            length=width,
            width=depth,
            height=height,
        )
        cutters.append(cutter)
        cutter_bounds.append(cutter.GetBoundingBox(True))

    cut_results = []
    for building, building_bounds in zip(building_parts, bounds):
        relevant_cutters = [
            cutter
            for cutter, cutter_bound in zip(cutters, cutter_bounds)
            if (
                building_bounds.Min.X < cutter_bound.Max.X - tolerance
                and building_bounds.Max.X > cutter_bound.Min.X + tolerance
                and building_bounds.Min.Y < cutter_bound.Max.Y - tolerance
                and building_bounds.Max.Y > cutter_bound.Min.Y + tolerance
                and building_bounds.Min.Z < cutter_bound.Max.Z - tolerance
                and building_bounds.Max.Z > cutter_bound.Min.Z + tolerance
            )
        ]
        if not relevant_cutters:
            cut_results.append(building.DuplicateBrep())
            continue

        result = rg.Brep.CreateBooleanDifference(
            [building],
            relevant_cutters,
            tolerance,
        )
        if result is None:
            raise RuntimeError("Boolean difference failed while creating building cutouts.")
        cut_results.extend(result)

    return cut_results


def rotate_building_block(
    buildings,
    axis_origin,
    axis_direction=None,
    angle_degrees=45.0,
):
    """
    Rotate a building or group of buildings around an external axis line.

    buildings      : Rhino.Geometry.Brep or sequence of Breps to rotate together
    axis_origin    : Rhino.Geometry.Point3d -- a point on the rotation axis
    axis_direction : Rhino.Geometry.Vector3d -- axis direction (world Z by default)
    angle_degrees  : float -- rotation angle in degrees

    Returns duplicated Rhino.Geometry.Brep objects; input Breps are unchanged.
    """
    if isinstance(buildings, rg.Brep):
        building_parts = [buildings]
    else:
        building_parts = list(buildings)
    if not building_parts or any(not isinstance(part, rg.Brep) for part in building_parts):
        raise TypeError("buildings must be a Brep or a non-empty sequence of Breps.")
    if not isinstance(axis_origin, rg.Point3d):
        raise TypeError("axis_origin must be a Rhino.Geometry.Point3d.")
    if axis_direction is None:
        axis_direction = rg.Vector3d.ZAxis
    elif not isinstance(axis_direction, rg.Vector3d):
        raise TypeError("axis_direction must be a Rhino.Geometry.Vector3d.")
    if not axis_direction.IsValid or axis_direction.Length <= 0:
        raise ValueError("axis_direction must be a valid non-zero vector.")
    if not math.isfinite(angle_degrees):
        raise ValueError("angle_degrees must be finite.")

    unit_axis = rg.Vector3d(axis_direction)
    if not unit_axis.Unitize():
        raise ValueError("axis_direction must be a valid non-zero vector.")
    transform = rg.Transform.Rotation(
        math.radians(angle_degrees),
        unit_axis,
        axis_origin,
    )

    rotated_buildings = []
    for building in building_parts:
        duplicate = building.DuplicateBrep()
        if duplicate is None:
            raise RuntimeError("Rhino failed to duplicate a building Brep.")
        if not duplicate.Transform(transform):
            raise RuntimeError("Rhino failed to rotate a building Brep.")
        rotated_buildings.append(duplicate)

    return rotated_buildings
