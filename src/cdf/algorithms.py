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
import Rhino
import Rhino.Geometry as rg
import random
import System

def create_fractal_tree(
    base_point=None,
    base_plane=None,
    length=10.0,
    angle=25.0,
    length_factor=0.7,
    depth=8,
    branch_count=2,
):
    """
    Build a fractal (recursively branching) tree as a list of line segments.

    base_point    : Rhino.Geometry.Point3d -- start point of the trunk
    base_plane    : Rhino.Geometry.Plane   -- plane whose YAxis is the trunk
                     direction and ZAxis is the branching rotation axis
    length        : float -- trunk length
    angle         : float -- angle in degrees between sibling branches
    length_factor : float -- length multiplier applied at each new generation
    depth         : int   -- number of recursive branching generations
    branch_count  : int   -- number of branches spawned at each node

    Returns a list of Rhino.Geometry.Line.
    """
    if base_point is None:
        base_point = rg.Point3d(0, 0, 0)
    if base_plane is None:
        base_plane = rg.Plane.WorldXY

    lines = []

    def _grow(start, direction, branch_length, remaining_depth):
        if remaining_depth <= 0 or branch_length <= 1e-6:
            return

        end = start + direction * branch_length
        lines.append(rg.Line(start, end))

        if branch_count <= 1:
            offsets = [0.0]
        else:
            span = angle * (branch_count - 1)
            offsets = [-span / 2.0 + i * angle for i in range(branch_count)]

        for offset in offsets:
            rotated_direction = rg.Vector3d(direction)
            rotated_direction.Rotate(math.radians(offset), base_plane.ZAxis)
            _grow(end, rotated_direction, branch_length * length_factor, remaining_depth - 1)

    _grow(base_point, base_plane.YAxis, length, depth)

    return lines


def create_fractal_tree_3d(
    base_point=None,
    base_plane=None,
    length=25.0,
    angle=25.0,
    length_factor=0.7,
    depth=8,
    branch_count=2,
):
    """Build a vertically growing, three-dimensional fractal tree.

    Args:
        base_point: Rhino.Geometry.Point3d at the trunk base (origin by default).
        base_plane: Rhino.Geometry.Plane whose ZAxis sets the upward direction
            (WorldXY by default).
        length: Length of the trunk segment.
        angle: Angle in degrees between each branch and its parent direction.
        length_factor: Length multiplier for each successive generation.
        depth: Number of segment generations, including the trunk.
        branch_count: Number of child branches at each non-terminal node.

    Returns:
        A tuple containing:
            - A list of Rhino.Geometry.Line segments.
            - A list of Rhino.Geometry.Point3d objects at the terminal branch tips.

        Terminal endpoints are kept at least 0.2 units apart in 3D distance.
    """
    if base_point is None:
        base_point = rg.Point3d(0, 0, 0)
    if base_plane is None:
        base_plane = rg.Plane.WorldXY

    min_tip_distance_squared = 0.2 ** 2
    terminal_points = []
    lines = []
    branch_angle = math.radians(angle)

    def _grow(start, direction, branch_length, remaining_depth):
        if remaining_depth <= 0 or branch_length <= 1e-6:
            return False

        end = start + direction * branch_length
        line_index = len(lines)
        lines.append(rg.Line(start, end))
        children_added = False

        if remaining_depth > 1:
            unit_direction = rg.Vector3d(direction)
            unit_direction.Unitize()
            reference = rg.Vector3d(base_plane.XAxis)
            if abs(rg.Vector3d.Multiply(unit_direction, reference)) > 0.99:
                reference = rg.Vector3d(base_plane.YAxis)
            side = rg.Vector3d.CrossProduct(unit_direction, reference)
            side.Unitize()
            other_side = rg.Vector3d.CrossProduct(unit_direction, side)
            other_side.Unitize()

            phase = math.radians((depth - remaining_depth) * 137.5)
            for index in range(max(0, branch_count)):
                azimuth = phase + 2.0 * math.pi * index / max(1, branch_count)
                radial = side * math.cos(azimuth) + other_side * math.sin(azimuth)
                child_direction = (
                    unit_direction * math.cos(branch_angle)
                    + radial * math.sin(branch_angle)
                )
                if _grow(
                    end,
                    child_direction,
                    branch_length * length_factor,
                    remaining_depth - 1,
                ):
                    children_added = True

        if not children_added:
            for tip in terminal_points:
                dx = end.X - tip.X
                dy = end.Y - tip.Y
                dz = end.Z - tip.Z
                if dx * dx + dy * dy + dz * dz < min_tip_distance_squared:
                    del lines[line_index:]
                    return False
            terminal_points.append(end)

        return True

    _grow(base_point, base_plane.ZAxis, length, depth)
    return lines, terminal_points





def _create_crochet_pseudosphere_impl(
    rounds=4,
    first_round=12,
    increase=3,
    base_chain=4,
    stitch_width=1.0,
    stitch_height=2.0,
    iterations=150,
    seed=1,
    max_stitches=1500,
    jitter=0.3,
    vertical_bias=0.0,
    origin=None,
    twist_degrees=0.0,
):
    """Internal mesh builder with optional growth-direction modifiers."""
    try:
        jitter = float(jitter)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("jitter must be a non-negative finite number.")
    if not math.isfinite(jitter) or jitter < 0:
        raise ValueError("jitter must be a non-negative finite number.")
    try:
        vertical_bias = float(vertical_bias)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("vertical_bias must be a finite number.")
    if not math.isfinite(vertical_bias):
        raise ValueError("vertical_bias must be a finite number.")
    try:
        twist_degrees = float(twist_degrees)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("twist_degrees must be a finite number.")
    if not math.isfinite(twist_degrees):
        raise ValueError("twist_degrees must be a finite number.")
    twist_radians = math.radians(twist_degrees)
    twist_cos = math.cos(twist_radians)
    twist_sin = math.sin(twist_radians)

    if origin is None:
        origin = rg.Point3d(0, 0, 0)
    else:
        pending = [origin]
        visited = set()
        origin = None
        while pending:
            candidate = pending.pop(0)
            if candidate is None or id(candidate) in visited:
                continue
            visited.add(id(candidate))
            if isinstance(candidate, rg.Point3d):
                origin = candidate
                break
            if isinstance(candidate, rg.Point):
                origin = candidate.Location
                break
            try:
                point_coordinates = (
                    float(candidate.X),
                    float(candidate.Y),
                    float(candidate.Z),
                )
            except AttributeError:
                pass
            except (TypeError, ValueError, OverflowError):
                raise TypeError("origin must be a Rhino or Grasshopper point.")
            else:
                origin = rg.Point3d(*point_coordinates)
                break

            for attribute in ("Value", "ScriptVariable"):
                unwrapped = getattr(candidate, attribute, None)
                if callable(unwrapped):
                    unwrapped = unwrapped()
                if unwrapped is not None and unwrapped is not candidate:
                    pending.append(unwrapped)

        if origin is None:
            raise TypeError("origin must be a Rhino or Grasshopper point.")
        if not origin.IsValid:
            raise ValueError("origin must be a valid finite point.")

    rng = random.Random(seed)
    jitter_amount = jitter * stitch_width

    points = []    # [x, y, z] of every stitch
    fixed = []     # True for stitches that must not move (the starting ring)
    springs = []   # (i, j, rest_length, stiffness)
    linked = set() # pairs joined by a spring, these are skipped in collision
    faces = []     # (a, b, c) vertex indices

    def add_spring(i, j, rest, stiffness):
        springs.append((i, j, rest, stiffness))
        linked.add((min(i, j), max(i, j)))

    # ------------------------------------------------------------------
    # 1 + 2. Starting ring (the joined chain). It stays fixed at the origin.
    # ------------------------------------------------------------------
    ring_radius = base_chain * stitch_width / (2.0 * math.pi)
    ring = []
    for i in range(first_round):
        angle = 2.0 * math.pi * i / first_round
        points.append([ring_radius * math.cos(angle),
                       ring_radius * math.sin(angle),
                       0.0])
        fixed.append(True)
        ring.append(i)

    # ------------------------------------------------------------------
    # Relaxation: springs keep stitch sizes, collisions keep stitches apart.
    # ------------------------------------------------------------------
    collision_distance = 0.9 * stitch_width

    def relax(steps):
        for _ in range(steps):
            # springs
            for i, j, rest, stiffness in springs:
                a = points[i]
                b = points[j]
                dx = b[0] - a[0]
                dy = b[1] - a[1]
                dz = b[2] - a[2]
                length = math.sqrt(dx * dx + dy * dy + dz * dz)
                if length < 1e-9:
                    continue
                move = stiffness * (length - rest) / length
                if fixed[i] and fixed[j]:
                    continue
                if fixed[i]:
                    b[0] -= dx * move
                    b[1] -= dy * move
                    b[2] -= dz * move
                elif fixed[j]:
                    a[0] += dx * move
                    a[1] += dy * move
                    a[2] += dz * move
                else:
                    move *= 0.5
                    a[0] += dx * move
                    a[1] += dy * move
                    a[2] += dz * move
                    b[0] -= dx * move
                    b[1] -= dy * move
                    b[2] -= dz * move

            # collisions: sort stitches into a grid, compare only neighbours
            cell = collision_distance
            grid = {}
            for index, p in enumerate(points):
                key = (int(math.floor(p[0] / cell)),
                       int(math.floor(p[1] / cell)),
                       int(math.floor(p[2] / cell)))
                grid.setdefault(key, []).append(index)

            for (cx, cy, cz), members in grid.items():
                for ox in (-1, 0, 1):
                    for oy in (-1, 0, 1):
                        for oz in (-1, 0, 1):
                            others = grid.get((cx + ox, cy + oy, cz + oz))
                            if not others:
                                continue
                            for i in members:
                                for j in others:
                                    if j <= i:
                                        continue
                                    if fixed[i] and fixed[j]:
                                        continue
                                    if (i, j) in linked:
                                        continue
                                    a = points[i]
                                    b = points[j]
                                    dx = b[0] - a[0]
                                    dy = b[1] - a[1]
                                    dz = b[2] - a[2]
                                    d2 = dx * dx + dy * dy + dz * dz
                                    if d2 >= cell * cell or d2 < 1e-12:
                                        continue
                                    dist = math.sqrt(d2)
                                    push = (cell - dist) / dist
                                    if fixed[i]:
                                        b[0] += dx * push
                                        b[1] += dy * push
                                        b[2] += dz * push
                                    elif fixed[j]:
                                        a[0] -= dx * push
                                        a[1] -= dy * push
                                        a[2] -= dz * push
                                    else:
                                        push *= 0.5
                                        a[0] -= dx * push
                                        a[1] -= dy * push
                                        a[2] -= dz * push
                                        b[0] += dx * push
                                        b[1] += dy * push
                                        b[2] += dz * push

    # ------------------------------------------------------------------
    # 3 + 4. Work the rounds. Round 1 puts one stitch on each ring position,
    # every later round puts `increase` stitches into each stitch.
    # ------------------------------------------------------------------
    grow_from = {}  # stitch index -> index of the stitch it was worked into

    for round_index in range(rounds):
        per_stitch = 1 if round_index == 0 else increase
        if len(ring) * per_stitch > max_stitches:
            break  # next round would be too big, stop at the last one that fits
        new_ring = []
        children_of = []

        for parent in ring:
            p = points[parent]

            # growth direction: continue the line from grandparent to parent
            if parent in grow_from:
                g = points[grow_from[parent]]
                direction = [p[0] - g[0], p[1] - g[1], p[2] - g[2]]
            else:
                direction = [p[0], p[1], 0.0]
            size = math.sqrt(sum(c * c for c in direction)) or 1.0
            direction = [c / size for c in direction]
            direction[2] += math.sin(parent * 0.5) * vertical_bias
            if twist_degrees != 0.0:
                dx, dy = direction[0], direction[1]
                direction[0] = dx * twist_cos - dy * twist_sin
                direction[1] = dx * twist_sin + dy * twist_cos

            children = []
            for _ in range(per_stitch):
                points.append([
                    p[0] + direction[0] * stitch_height
                    + rng.uniform(-jitter_amount, jitter_amount),
                    p[1] + direction[1] * stitch_height
                    + rng.uniform(-jitter_amount, jitter_amount),
                    p[2] + direction[2] * stitch_height
                    + rng.uniform(-jitter_amount, jitter_amount),
                ])
                fixed.append(False)
                child = len(points) - 1
                grow_from[child] = parent
                children.append(child)
                new_ring.append(child)
                # the post of the stitch
                add_spring(parent, child, stitch_height, 1.0)
            children_of.append(children)

        count = len(new_ring)
        for k in range(count):
            # top of the round: every stitch is one stitch_width wide
            add_spring(new_ring[k], new_ring[(k + 1) % count], stitch_width, 1.0)
            # weak spring to the stitch after next, keeps the round smooth
            if count > 4:
                add_spring(new_ring[k], new_ring[(k + 2) % count],
                           2.0 * stitch_width, 0.15)

        # faces between the old round and the new round
        parents = len(ring)
        for j in range(parents):
            children = children_of[j]
            next_parent = ring[(j + 1) % parents]
            next_child = children_of[(j + 1) % parents][0]
            for k in range(len(children) - 1):
                faces.append((ring[j], children[k], children[k + 1]))
            faces.append((ring[j], children[-1], next_child))
            faces.append((ring[j], next_child, next_parent))

        ring = new_ring
        relax(iterations)

    # ------------------------------------------------------------------
    # Build the Rhino mesh
    # ------------------------------------------------------------------
    mesh = rg.Mesh()
    for p in points:
        mesh.Vertices.Add(
            p[0] + origin.X,
            p[1] + origin.Y,
            p[2] + origin.Z,
        )
    for a, b, c in faces:
        mesh.Faces.AddFace(a, b, c)
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh


def create_crochet_pseudosphere(
    rounds=4,
    first_round=12,
    increase=3,
    base_chain=4,
    stitch_width=1.0,
    stitch_height=2.0,
    iterations=150,
    seed=1,
    max_stitches=1500,
):
    """Build a crocheted hyperbolic form ("pseudosphere") as a mesh.

    The function follows the crochet pattern step by step:
      1. a small ring made of chain stitches,
      2. a first round of double crochets into the ring,
      3. more rounds, where every stitch gets `increase` new stitches.

    Each stitch is one mesh vertex. After every new round the stitches are
    relaxed like small springs: a stitch wants to keep its width and its
    height, and two stitches cannot be in the same place. Each round has more
    stitches than a flat circle has room for, so the surface has to ruffle.

    Params:
        rounds (int): Number of rounds worked into the ring. Default 4.
            Stitch count is multiplied by `increase` every round, so keep
            this low (5 rounds with increase 3 is already 972 stitches).
        first_round (int): Stitches in the first round. Default 12.
        increase (int): New stitches worked into each stitch. Default 3.
            1 gives a tube, 2 gives soft ruffles, 3 gives dense ruffles.
        base_chain (int): Chain stitches in the starting ring. Default 4.
            Only sets the size of the hole in the middle.
        stitch_width (float): Width of one stitch. Default 1.0.
        stitch_height (float): Height of one round. Default 2.0
            (a double crochet is about twice as tall as it is wide).
        iterations (int): Relaxation steps after each round. Default 150.
            More steps give a smoother result but take longer.
        seed (int): Seed for the small random offsets that let the surface
            ruffle. Same seed gives the same shape. Default 1.
        max_stitches (int): Safety limit on stitches in a single round.
            Rounds that would exceed it are skipped, so the form stops
            growing instead of freezing Rhino. Default 1500.

    Returns:
        Rhino.Geometry.Mesh: The crocheted surface. Each vertex is the top
        of one stitch, each ring of vertices is one round.
    """
    rng = random.Random(seed)

    points = []    # [x, y, z] of every stitch
    fixed = []     # True for stitches that must not move (the starting ring)
    springs = []   # (i, j, rest_length, stiffness)
    linked = set() # pairs joined by a spring, these are skipped in collision
    faces = []     # (a, b, c) vertex indices

    def add_spring(i, j, rest, stiffness):
        springs.append((i, j, rest, stiffness))
        linked.add((min(i, j), max(i, j)))

    # ------------------------------------------------------------------
    # 1 + 2. Starting ring (the joined chain). It stays fixed at the origin.
    # ------------------------------------------------------------------
    ring_radius = base_chain * stitch_width / (2.0 * math.pi)
    ring = []
    for i in range(first_round):
        angle = 2.0 * math.pi * i / first_round
        points.append([ring_radius * math.cos(angle),
                       ring_radius * math.sin(angle),
                       0.0])
        fixed.append(True)
        ring.append(i)

    # ------------------------------------------------------------------
    # Relaxation: springs keep stitch sizes, collisions keep stitches apart.
    # ------------------------------------------------------------------
    collision_distance = 0.9 * stitch_width

    def relax(steps):
        for _ in range(steps):
            # springs
            for i, j, rest, stiffness in springs:
                a = points[i]
                b = points[j]
                dx = b[0] - a[0]
                dy = b[1] - a[1]
                dz = b[2] - a[2]
                length = math.sqrt(dx * dx + dy * dy + dz * dz)
                if length < 1e-9:
                    continue
                move = stiffness * (length - rest) / length
                if fixed[i] and fixed[j]:
                    continue
                if fixed[i]:
                    b[0] -= dx * move
                    b[1] -= dy * move
                    b[2] -= dz * move
                elif fixed[j]:
                    a[0] += dx * move
                    a[1] += dy * move
                    a[2] += dz * move
                else:
                    move *= 0.5
                    a[0] += dx * move
                    a[1] += dy * move
                    a[2] += dz * move
                    b[0] -= dx * move
                    b[1] -= dy * move
                    b[2] -= dz * move

            # collisions: sort stitches into a grid, compare only neighbours
            cell = collision_distance
            grid = {}
            for index, p in enumerate(points):
                key = (int(math.floor(p[0] / cell)),
                       int(math.floor(p[1] / cell)),
                       int(math.floor(p[2] / cell)))
                grid.setdefault(key, []).append(index)

            for (cx, cy, cz), members in grid.items():
                for ox in (-1, 0, 1):
                    for oy in (-1, 0, 1):
                        for oz in (-1, 0, 1):
                            others = grid.get((cx + ox, cy + oy, cz + oz))
                            if not others:
                                continue
                            for i in members:
                                for j in others:
                                    if j <= i:
                                        continue
                                    if fixed[i] and fixed[j]:
                                        continue
                                    if (i, j) in linked:
                                        continue
                                    a = points[i]
                                    b = points[j]
                                    dx = b[0] - a[0]
                                    dy = b[1] - a[1]
                                    dz = b[2] - a[2]
                                    d2 = dx * dx + dy * dy + dz * dz
                                    if d2 >= cell * cell or d2 < 1e-12:
                                        continue
                                    dist = math.sqrt(d2)
                                    push = (cell - dist) / dist
                                    if fixed[i]:
                                        b[0] += dx * push
                                        b[1] += dy * push
                                        b[2] += dz * push
                                    elif fixed[j]:
                                        a[0] -= dx * push
                                        a[1] -= dy * push
                                        a[2] -= dz * push
                                    else:
                                        push *= 0.5
                                        a[0] -= dx * push
                                        a[1] -= dy * push
                                        a[2] -= dz * push
                                        b[0] += dx * push
                                        b[1] += dy * push
                                        b[2] += dz * push

    # ------------------------------------------------------------------
    # 3 + 4. Work the rounds. Round 1 puts one stitch on each ring position,
    # every later round puts `increase` stitches into each stitch.
    # ------------------------------------------------------------------
    grow_from = {}  # stitch index -> index of the stitch it was worked into

    for round_index in range(rounds):
        per_stitch = 1 if round_index == 0 else increase
        if len(ring) * per_stitch > max_stitches:
            break  # next round would be too big, stop at the last one that fits
        new_ring = []
        children_of = []

        for parent in ring:
            p = points[parent]

            # growth direction: continue the line from grandparent to parent
            if parent in grow_from:
                g = points[grow_from[parent]]
                direction = [p[0] - g[0], p[1] - g[1], p[2] - g[2]]
            else:
                direction = [p[0], p[1], 0.0]
            size = math.sqrt(sum(c * c for c in direction)) or 1.0
            direction = [c / size for c in direction]

            children = []
            for _ in range(per_stitch):
                jitter = 0.3 * stitch_width
                points.append([
                    p[0] + direction[0] * stitch_height + rng.uniform(-jitter, jitter),
                    p[1] + direction[1] * stitch_height + rng.uniform(-jitter, jitter),
                    p[2] + direction[2] * stitch_height + rng.uniform(-jitter, jitter),
                ])
                fixed.append(False)
                child = len(points) - 1
                grow_from[child] = parent
                children.append(child)
                new_ring.append(child)
                # the post of the stitch
                add_spring(parent, child, stitch_height, 1.0)
            children_of.append(children)

        count = len(new_ring)
        for k in range(count):
            # top of the round: every stitch is one stitch_width wide
            add_spring(new_ring[k], new_ring[(k + 1) % count], stitch_width, 1.0)
            # weak spring to the stitch after next, keeps the round smooth
            if count > 4:
                add_spring(new_ring[k], new_ring[(k + 2) % count],
                           2.0 * stitch_width, 0.15)

        # faces between the old round and the new round
        parents = len(ring)
        for j in range(parents):
            children = children_of[j]
            next_parent = ring[(j + 1) % parents]
            next_child = children_of[(j + 1) % parents][0]
            for k in range(len(children) - 1):
                faces.append((ring[j], children[k], children[k + 1]))
            faces.append((ring[j], children[-1], next_child))
            faces.append((ring[j], next_child, next_parent))

        ring = new_ring
        relax(iterations)

    # ------------------------------------------------------------------
    # Build the Rhino mesh
    # ------------------------------------------------------------------
    mesh = rg.Mesh()
    for p in points:
        mesh.Vertices.Add(p[0], p[1], p[2])
    for a, b, c in faces:
        mesh.Faces.AddFace(a, b, c)
    mesh.Normals.ComputeNormals()
    mesh.Compact()
    return mesh


def create_crochet_pseudosphere_with_jitter(
    rounds=4,
    first_round=12,
    increase=3,
    base_chain=4,
    stitch_width=1.0,
    stitch_height=2.0,
    iterations=150,
    seed=1,
    max_stitches=1500,
    jitter=0.3,
    origin=None,
    twist_degrees=0.0,
):
    """Build a crochet pseudosphere with configurable jitter.

    Jitter is a non-negative fraction of stitch_width. The default 0.3 keeps
    the same offset range as create_crochet_pseudosphere.
    origin: Optional Rhino or Grasshopper point for the mesh's starting center.
    twist_degrees: Rotation in degrees applied to each growth direction.
        Repeated growth steps accumulate this rotation into a spiral.
    """
    return _create_crochet_pseudosphere_impl(
        rounds=rounds,
        first_round=first_round,
        increase=increase,
        base_chain=base_chain,
        stitch_width=stitch_width,
        stitch_height=stitch_height,
        iterations=iterations,
        seed=seed,
        max_stitches=max_stitches,
        jitter=jitter,
        origin=origin,
        twist_degrees=twist_degrees,
    )


def create_crochet_pseudosphere_with_vertical_bias(
    rounds=4,
    first_round=12,
    increase=3,
    base_chain=4,
    stitch_width=1.0,
    stitch_height=2.0,
    iterations=150,
    seed=1,
    max_stitches=1500,
    origin=None,
):
    """Build a crochet pseudosphere with a sinusoidal vertical growth bias.

    After normalizing each growth direction, its Z component is offset by
    ``sin(parent * 0.5) * 0.5``. The original function remains unchanged.
    origin: Optional Rhino or Grasshopper point for the mesh's starting center.
    """
    return _create_crochet_pseudosphere_impl(
        rounds=rounds,
        first_round=first_round,
        increase=increase,
        base_chain=base_chain,
        stitch_width=stitch_width,
        stitch_height=stitch_height,
        iterations=iterations,
        seed=seed,
        max_stitches=max_stitches,
        jitter=0.3,
        vertical_bias=0.5,
        origin=origin,
    )


def create_crochet_pseudosphere_from_curve(
    start_curve,
    rounds=4,
    first_round=12,
    increase=3,
    base_chain=4,
    stitch_width=1.0,
    stitch_height=2.0,
    iterations=150,
    seed=1,
    max_stitches=1500,
    growth_direction=None,
    growth_delay=2,
    growth_variation=2,
):
    """Build a variable-growth crochet mesh along an open seed curve.

    The seed curve becomes the first open row. Subsequent crochet rows extend
    along one side of it. By default, growth is biased toward world Z; supply
    another Vector3d to orient the strip differently. Stitch counts stay
    steady during growth_delay rounds, then ramp up by one per round to
    increase. Later rounds vary each stitch's offspring count from zero up to
    the ramp target plus growth_variation.

    Args:
        start_curve: Valid open Rhino.Geometry.Curve to use as the seed row.
            In Grasshopper, use a Curve type hint and Item access.
        rounds: Number of crochet rounds to generate.
        first_round: Number of seed-curve samples and initial stitches.
        increase: Maximum ramp target for children per stitch.
        base_chain: Starting-ring size parameter.
        stitch_width: Width of one stitch.
        stitch_height: Height of one crochet round.
        iterations: Relaxation iterations after each round.
        seed: Seed for deterministic growth variation and stitch offsets.
        max_stitches: Per-round safety limit.
        growth_direction: Optional Vector3d indicating the side to grow toward.
        growth_delay: Initial rounds with one child per stitch and no stitch-
            count increase.
        growth_variation: Maximum extra children above the round's ramp target
            at each stitch. Zero-child locations are allowed after the delay.

    Returns:
        Rhino.Geometry.Mesh: An open crochet strip whose first row follows
        start_curve. The original create_crochet_pseudosphere function is
        unchanged.
    """
    original_input = start_curve
    pending = [start_curve]
    visited = set()
    start_curve = None
    while pending:
        candidate = pending.pop(0)
        if candidate is None or id(candidate) in visited:
            continue
        visited.add(id(candidate))
        if isinstance(candidate, rg.Curve):
            start_curve = candidate
            break
        if isinstance(candidate, (list, tuple)):
            if len(candidate) == 1:
                pending.append(candidate[0])
            continue
        for attribute in ("Value", "ScriptVariable"):
            unwrapped = getattr(candidate, attribute, None)
            if callable(unwrapped):
                unwrapped = unwrapped()
            if unwrapped is not candidate and unwrapped is not None:
                pending.append(unwrapped)

    if start_curve is None:
        input_type = "{}.{}".format(
            type(original_input).__module__,
            type(original_input).__name__,
        )
        raise TypeError(
            "start_curve must be a single Rhino.Geometry.Curve. "
            "Received {}; set the Grasshopper input type hint to Curve "
            "and access to Item.".format(input_type)
        )
    if not start_curve.IsValid:
        raise ValueError("start_curve must be a valid Rhino curve.")
    if start_curve.IsClosed:
        raise ValueError("start_curve must be open to form a one-sided strip.")

    def _whole_number(name, value, minimum):
        try:
            integer = int(value)
        except (TypeError, ValueError, OverflowError):
            raise ValueError(
                "{} must be a whole number of at least {}.".format(
                    name, minimum
                )
            )
        if isinstance(value, bool) or integer != value or integer < minimum:
            raise ValueError(
                "{} must be a whole number of at least {}.".format(
                    name, minimum
                )
            )
        return integer

    rounds = _whole_number("rounds", rounds, 1)
    first_round = _whole_number("first_round", first_round, 3)
    increase = _whole_number("increase", increase, 1)
    iterations = _whole_number("iterations", iterations, 0)
    max_stitches = _whole_number("max_stitches", max_stitches, 1)
    growth_delay = _whole_number("growth_delay", growth_delay, 0)
    growth_variation = _whole_number("growth_variation", growth_variation, 0)
    try:
        base_chain = float(base_chain)
        stitch_width = float(stitch_width)
        stitch_height = float(stitch_height)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Crochet counts and dimensions must be valid numbers.")

    if not math.isfinite(base_chain) or base_chain <= 0:
        raise ValueError("base_chain must be a positive finite number.")
    if not math.isfinite(stitch_width) or stitch_width <= 0:
        raise ValueError("stitch_width must be a positive finite number.")
    if not math.isfinite(stitch_height) or stitch_height <= 0:
        raise ValueError("stitch_height must be a positive finite number.")

    if growth_direction is None:
        growth_direction = rg.Vector3d.ZAxis
    elif not isinstance(growth_direction, rg.Vector3d):
        for attribute in ("Value", "ScriptVariable"):
            unwrapped = getattr(growth_direction, attribute, None)
            if callable(unwrapped):
                unwrapped = unwrapped()
            if isinstance(unwrapped, rg.Vector3d):
                growth_direction = unwrapped
                break

    if not isinstance(growth_direction, rg.Vector3d):
        raise TypeError("growth_direction must be a Rhino.Geometry.Vector3d.")
    preferred_direction = rg.Vector3d(growth_direction)
    if not preferred_direction.Unitize():
        raise ValueError("growth_direction must not be a zero vector.")

    rng = random.Random(seed)
    points = []
    fixed = []
    springs = []
    linked = set()
    faces = []
    grow_from = {}
    ring = []
    ring_radius = base_chain * stitch_width / (2.0 * math.pi)
    for index in range(first_round):
        angle = 2.0 * math.pi * index / first_round
        points.append([
            ring_radius * math.cos(angle),
            ring_radius * math.sin(angle),
            0.0,
        ])
        fixed.append(True)
        ring.append(index)

    ring_curve_fractions = [
        index / float(first_round - 1) for index in range(first_round)
    ]
    curve_fraction_by_vertex = list(ring_curve_fractions)

    def _add_spring(first, second, rest, stiffness):
        springs.append((first, second, rest, stiffness))
        linked.add((min(first, second), max(first, second)))

    collision_distance = 0.9 * stitch_width

    def _relax(step_count):
        for _ in range(step_count):
            for first, second, rest, stiffness in springs:
                a = points[first]
                b = points[second]
                dx = b[0] - a[0]
                dy = b[1] - a[1]
                dz = b[2] - a[2]
                length = math.sqrt(dx * dx + dy * dy + dz * dz)
                if length < 1e-9:
                    continue
                move = stiffness * (length - rest) / length
                if fixed[first] and fixed[second]:
                    continue
                if fixed[first]:
                    b[0] -= dx * move
                    b[1] -= dy * move
                    b[2] -= dz * move
                elif fixed[second]:
                    a[0] += dx * move
                    a[1] += dy * move
                    a[2] += dz * move
                else:
                    move *= 0.5
                    a[0] += dx * move
                    a[1] += dy * move
                    a[2] += dz * move
                    b[0] -= dx * move
                    b[1] -= dy * move
                    b[2] -= dz * move

            grid = {}
            for index, point in enumerate(points):
                key = (
                    int(math.floor(point[0] / collision_distance)),
                    int(math.floor(point[1] / collision_distance)),
                    int(math.floor(point[2] / collision_distance)),
                )
                grid.setdefault(key, []).append(index)

            for (cx, cy, cz), members in grid.items():
                for ox in (-1, 0, 1):
                    for oy in (-1, 0, 1):
                        for oz in (-1, 0, 1):
                            others = grid.get((cx + ox, cy + oy, cz + oz))
                            if not others:
                                continue
                            for first in members:
                                for second in others:
                                    if second <= first:
                                        continue
                                    if fixed[first] and fixed[second]:
                                        continue
                                    if (first, second) in linked:
                                        continue
                                    a = points[first]
                                    b = points[second]
                                    dx = b[0] - a[0]
                                    dy = b[1] - a[1]
                                    dz = b[2] - a[2]
                                    distance_squared = dx * dx + dy * dy + dz * dz
                                    if (
                                        distance_squared >= collision_distance ** 2
                                        or distance_squared < 1e-12
                                    ):
                                        continue
                                    distance = math.sqrt(distance_squared)
                                    push = (collision_distance - distance) / distance
                                    if fixed[first]:
                                        b[0] += dx * push
                                        b[1] += dy * push
                                        b[2] += dz * push
                                    elif fixed[second]:
                                        a[0] -= dx * push
                                        a[1] -= dy * push
                                        a[2] -= dz * push
                                    else:
                                        push *= 0.5
                                        a[0] -= dx * push
                                        a[1] -= dy * push
                                        a[2] -= dz * push
                                        b[0] += dx * push
                                        b[1] += dy * push
                                        b[2] += dz * push

    ring_sizes = [len(ring)]
    for round_index in range(rounds):
        if round_index < growth_delay:
            offspring_counts = [1] * len(ring)
        else:
            ramp_target = min(increase, 2 + round_index - growth_delay)
            maximum_children = ramp_target + growth_variation
            offspring_counts = [
                rng.randint(0, maximum_children) for _ in ring
            ]
            while sum(count > 0 for count in offspring_counts) < 3:
                empty_locations = [
                    index for index, count in enumerate(offspring_counts)
                    if count == 0
                ]
                if not empty_locations:
                    break
                offspring_counts[rng.choice(empty_locations)] = 1

        if sum(offspring_counts) > max_stitches:
            break

        children_of = []
        new_ring = []
        new_ring_curve_fractions = []
        for parent, child_count in zip(ring, offspring_counts):
            parent_point = points[parent]
            if parent in grow_from:
                grandparent_point = points[grow_from[parent]]
                direction = [
                    parent_point[axis] - grandparent_point[axis]
                    for axis in range(3)
                ]
            else:
                direction = [parent_point[0], parent_point[1], 0.0]
            direction_length = math.sqrt(sum(value * value for value in direction))
            if direction_length == 0:
                direction_length = 1.0
            direction = [value / direction_length for value in direction]

            children = []
            jitter = 0.3 * stitch_width
            parent_index = len(children_of)
            parent_fraction = ring_curve_fractions[parent_index]
            left_fraction = (
                0.0
                if parent_index == 0
                else 0.5 * (
                    ring_curve_fractions[parent_index - 1] + parent_fraction
                )
            )
            right_fraction = (
                1.0
                if parent_index == len(ring) - 1
                else 0.5 * (
                    parent_fraction + ring_curve_fractions[parent_index + 1]
                )
            )
            for child_index in range(child_count):
                if child_count == 1:
                    child_fraction = parent_fraction
                else:
                    child_fraction = left_fraction + (
                        (right_fraction - left_fraction)
                        * (child_index + 1)
                        / float(child_count + 1)
                    )
                points.append([
                    parent_point[0] + direction[0] * stitch_height
                    + rng.uniform(-jitter, jitter),
                    parent_point[1] + direction[1] * stitch_height
                    + rng.uniform(-jitter, jitter),
                    parent_point[2] + direction[2] * stitch_height
                    + rng.uniform(-jitter, jitter),
                ])
                child = len(points) - 1
                fixed.append(False)
                grow_from[child] = parent
                children.append(child)
                new_ring.append(child)
                new_ring_curve_fractions.append(child_fraction)
                _add_spring(parent, child, stitch_height, 1.0)
            children_of.append(children)

        if len(new_ring) < 3:
            raise RuntimeError("Variable growth produced fewer than three stitches.")

        for index, stitch in enumerate(new_ring):
            _add_spring(
                stitch,
                new_ring[(index + 1) % len(new_ring)],
                stitch_width,
                1.0,
            )
            if len(new_ring) > 4:
                _add_spring(
                    stitch,
                    new_ring[(index + 2) % len(new_ring)],
                    2.0 * stitch_width,
                    0.15,
                )

        parent_count = len(ring)
        for parent_index, parent in enumerate(ring):
            next_children = None
            for offset in range(1, parent_count + 1):
                candidate_children = children_of[
                    (parent_index + offset) % parent_count
                ]
                if candidate_children:
                    next_children = candidate_children
                    break

            children = children_of[parent_index]
            if children:
                for child_index in range(len(children) - 1):
                    faces.append((
                        parent,
                        children[child_index],
                        children[child_index + 1],
                    ))
                faces.append((parent, children[-1], next_children[0]))
            faces.append((
                parent,
                next_children[0],
                ring[(parent_index + 1) % parent_count],
            ))

        ring = new_ring
        ring_curve_fractions = new_ring_curve_fractions
        curve_fraction_by_vertex.extend(ring_curve_fractions)
        ring_sizes.append(len(ring))
        _relax(iterations)

    source_mesh = rg.Mesh()
    for point in points:
        source_mesh.Vertices.Add(point[0], point[1], point[2])
    for first, second, third in faces:
        source_mesh.Faces.AddFace(first, second, third)
    source_mesh.Normals.ComputeNormals()
    source_mesh.Compact()
    if not source_mesh.IsValid:
        raise RuntimeError("Rhino created an invalid variable-growth crochet mesh.")

    expected_vertex_count = sum(ring_sizes)
    if source_mesh.Vertices.Count != expected_vertex_count:
        raise RuntimeError(
            "The variable-growth mesh has an unexpected ring layout."
        )

    curve_sample_count = max(first_round, min(max_stitches, 2048))
    curve_sample_parameters = start_curve.DivideByCount(
        curve_sample_count - 1, True
    )
    if (
        curve_sample_parameters is None
        or len(curve_sample_parameters) != curve_sample_count
    ):
        raise RuntimeError("Rhino failed to sample start_curve.")

    def _parameter_at_fraction(fraction):
        scaled_index = max(
            0.0, min(1.0, fraction)
        ) * (curve_sample_count - 1)
        lower_index = int(math.floor(scaled_index))
        upper_index = min(lower_index + 1, curve_sample_count - 1)
        blend = scaled_index - lower_index
        return (
            curve_sample_parameters[lower_index] * (1.0 - blend)
            + curve_sample_parameters[upper_index] * blend
        )

    def _project_off_tangent(vector, tangent):
        return vector - tangent * rg.Vector3d.Multiply(vector, tangent)

    def _curve_frames(parameters):
        frames = []
        previous_side = None
        fallback_axes = (
            rg.Vector3d.XAxis,
            rg.Vector3d.YAxis,
            rg.Vector3d.ZAxis,
        )

        for parameter in parameters:
            tangent = rg.Vector3d(start_curve.TangentAt(parameter))
            if not tangent.Unitize():
                raise ValueError("start_curve has a degenerate tangent.")

            reference = (
                previous_side
                if previous_side is not None
                else preferred_direction
            )
            side = _project_off_tangent(reference, tangent)
            if not side.Unitize():
                for axis in fallback_axes:
                    side = _project_off_tangent(axis, tangent)
                    if side.Unitize():
                        break
                else:
                    raise ValueError(
                        "Could not derive a growth direction along start_curve."
                    )

            if (
                previous_side is not None
                and rg.Vector3d.Multiply(side, previous_side) < 0
            ):
                side.Reverse()

            binormal = rg.Vector3d.CrossProduct(tangent, side)
            if not binormal.Unitize():
                raise ValueError("Could not derive a frame along start_curve.")
            frames.append((side, binormal))
            previous_side = side

        return frames

    mapped_mesh = rg.Mesh()
    parameter_by_vertex = []
    curve_parameters_by_vertex = [
        _parameter_at_fraction(fraction)
        for fraction in curve_fraction_by_vertex
    ]
    frames_by_vertex = []
    vertex_offset = 0
    for ring_size in ring_sizes:
        ring_parameters = curve_parameters_by_vertex[
            vertex_offset:vertex_offset + ring_size
        ]
        frames_by_vertex.extend(_curve_frames(ring_parameters))
        vertex_offset += ring_size

    base_radius = base_chain * stitch_width / (2.0 * math.pi)
    vertex_offset = 0

    for ring_size in ring_sizes:
        for local_index in range(ring_size):
            vertex_index = vertex_offset + local_index
            source_point = source_mesh.Vertices[vertex_offset + local_index]
            radial_distance = math.sqrt(
                source_point.X * source_point.X
                + source_point.Y * source_point.Y
            )
            side_offset = max(0.0, radial_distance - base_radius)
            side, binormal = frames_by_vertex[vertex_index]
            curve_point = start_curve.PointAt(
                curve_parameters_by_vertex[vertex_index]
            )
            mapped_point = (
                curve_point
                + side * side_offset
                + binormal * source_point.Z
            )
            mapped_mesh.Vertices.Add(
                mapped_point.X, mapped_point.Y, mapped_point.Z
            )
            parameter_by_vertex.append(curve_fraction_by_vertex[vertex_index])

        vertex_offset += ring_size

    for face_index in range(source_mesh.Faces.Count):
        face = source_mesh.Faces[face_index]
        if face.IsTriangle:
            face_vertices = (face.A, face.B, face.C)
        else:
            face_vertices = (face.A, face.B, face.C, face.D)

        edges = zip(face_vertices, face_vertices[1:] + face_vertices[:1])
        if any(
            abs(parameter_by_vertex[a] - parameter_by_vertex[b]) > 0.5
            for a, b in edges
        ):
            continue

        if face.IsTriangle:
            mapped_mesh.Faces.AddFace(face.A, face.B, face.C)
        else:
            mapped_mesh.Faces.AddFace(face.A, face.B, face.C, face.D)

    if mapped_mesh.Faces.Count == 0:
        raise RuntimeError("The curve-based crochet strip has no faces.")
    mapped_mesh.Normals.ComputeNormals()
    mapped_mesh.Compact()
    if not mapped_mesh.IsValid:
        raise RuntimeError("Rhino created an invalid curve-based crochet mesh.")

    return mapped_mesh


def create_flowers(
    tip_points,
    rounds=4,
    first_round=12,
    increase=3,
    base_chain=4,
    stitch_width=1.0,
    stitch_height=2.0,
    iterations=150,
    seed=1,
    max_stitches=1500,
):
    """Create one crochet pseudosphere at each Grasshopper-supplied point.

    Connect the point output from ``create_fractal_tree_3d`` to this function's
    ``tip_points`` input. A single point, a list, nested lists, or a Grasshopper
    data tree of points are accepted. Grasshopper point wrappers and Rhino
    object GUIDs that refer to document point objects are resolved.

    Args:
        tip_points: Rhino.Geometry.Point3d values from a Grasshopper component.
        Other parameters: Passed directly to ``create_crochet_pseudosphere``.

    Returns:
        A list of Rhino.Geometry.Mesh objects, translated to the corresponding
        input points.
    """
    if tip_points is None:
        raise ValueError("tip_points must contain Rhino.Geometry.Point3d values.")

    points = []
    active_items = set()

    def _collect_points(item):
        if isinstance(item, (str, bytes)):
            raise TypeError(
                "tip_points must contain only Rhino.Geometry.Point3d values."
            )
        if isinstance(item, rg.Point3d):
            points.append(item)
            return

        if isinstance(item, System.Guid):
            document = Rhino.RhinoDoc.ActiveDoc
            if document is None:
                raise RuntimeError("Cannot resolve point GUIDs without an active Rhino document.")
            rhino_object = document.Objects.FindId(item)
            if rhino_object is None:
                raise ValueError(
                    "tip_points GUID {} does not match an object in the active Rhino document.".format(item)
                )
            geometry = rhino_object.Geometry
            if not isinstance(geometry, rg.Point):
                raise TypeError(
                    "tip_points GUID {} refers to {}, not a Rhino point.".format(
                        item, type(geometry).__name__
                    )
                )
            points.append(geometry.Location)
            return

        try:
            x, y, z = item.X, item.Y, item.Z
        except AttributeError:
            pass
        else:
            points.append(rg.Point3d(float(x), float(y), float(z)))
            return

        item_id = id(item)
        if item_id in active_items:
            raise ValueError("tip_points contains a cyclic collection.")
        active_items.add(item_id)
        try:
            for attribute in ("Value", "ScriptVariable"):
                unwrapped = getattr(item, attribute, None)
                if callable(unwrapped):
                    unwrapped = unwrapped()
                if unwrapped is not None and unwrapped is not item:
                    _collect_points(unwrapped)
                    return

            branches = getattr(item, "Branches", None)
            if branches is not None:
                for branch in branches:
                    _collect_points(branch)
                return

            branch_count = getattr(item, "BranchCount", None)
            branch_method = getattr(item, "Branch", None)
            if branch_count is not None and callable(branch_method):
                for index in range(branch_count):
                    _collect_points(branch_method(index))
                return

            try:
                items = iter(item)
            except TypeError:
                raise TypeError(
                    "tip_points contains an unsupported item of type {}.{}; "
                    "expected Rhino points or a Grasshopper point tree.".format(
                        type(item).__module__, type(item).__name__
                    )
                )
            for child in items:
                _collect_points(child)
        finally:
            active_items.remove(item_id)

    _collect_points(tip_points)

    meshes = []
    for point in points:
        mesh = create_crochet_pseudosphere(
            rounds=rounds,
            first_round=first_round,
            increase=increase,
            base_chain=base_chain,
            stitch_width=stitch_width,
            stitch_height=stitch_height,
            iterations=iterations,
            seed=seed,
            max_stitches=max_stitches,
        )
        translation = rg.Transform.Translation(
            rg.Vector3d(point.X, point.Y, point.Z)
        )
        if not mesh.Transform(translation):
            raise RuntimeError("Rhino failed to translate a crochet pseudosphere.")
        meshes.append(mesh)

    return meshes


def Hexagon_grid(plane=None, size=None, extent_x=None, extent_y=None):
    """Create a staggered hexagonal grid on a Rhino plane.

    Args:
        plane: Rhino.Geometry.Plane defining the grid origin and orientation
            (WorldXY by default).
        size: Distance between opposite side centers (the hexagon's
            flat-to-flat size).
        extent_x: Number of columns.
        extent_y: Number of rows.

    Returns:
        A tuple containing:
            - A list of independent closed cell outline curves.
            - A list of unique corner points.
            - A list of matching cell labels.
            - A list of cell center points, in the same order as the cells.

        The first hexagon is centered at the plane origin. Labels report the
        hexagon's overall width and height in the plane's local axes.

        In a Grasshopper Python component, unpack the results into separate
        outputs, for example:
        ``C, Pts, Labels, Centers = Hexagon_grid(P, S, Ex, Ey)``.
    """
    if plane is None:
        plane = rg.Plane.WorldXY

    if not isinstance(plane, rg.Plane):
        for attribute in ("Value", "ScriptVariable"):
            unwrapped = getattr(plane, attribute, None)
            if callable(unwrapped):
                unwrapped = unwrapped()
            if isinstance(unwrapped, rg.Plane):
                plane = unwrapped
                break

    if not isinstance(plane, rg.Plane):
        raise TypeError(
            "plane must be a Rhino.Geometry.Plane or Grasshopper plane input."
        )
    if not plane.IsValid:
        raise ValueError("plane must be a valid Rhino.Geometry.Plane.")

    try:
        size = float(size)
    except (TypeError, ValueError):
        raise ValueError("size must be a positive finite number.")
    if not math.isfinite(size) or size <= 0:
        raise ValueError("size must be a positive finite number.")

    extents = []
    for name, value in (("extent_x", extent_x), ("extent_y", extent_y)):
        try:
            extent = int(value)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("{} must be a positive whole number.".format(name))
        if isinstance(value, bool) or extent != value or extent < 1:
            raise ValueError("{} must be a positive whole number.".format(name))
        extents.append(extent)
    extent_x, extent_y = extents

    radius = size / math.sqrt(3.0)
    vertex_x_indices = (2, 1, -1, -2, -1, 1)
    vertex_y_indices = (0, 1, 1, 0, -1, -1)

    base_vertices = [
        plane.PointAt(
            vertex_x_indices[index] * radius / 2.0,
            vertex_y_indices[index] * size / 2.0,
        )
        for index in range(6)
    ]
    base_cell = rg.PolylineCurve(
        rg.Polyline(base_vertices + [base_vertices[0]])
    )

    corner_points = {}
    cells = []
    center_points = []

    for row in range(extent_y):
        for column in range(extent_x):
            cell = base_cell.DuplicateCurve()
            if cell is None:
                raise RuntimeError("Rhino failed to duplicate the hexagon cell.")

            offset_x = column * 1.5 * radius
            offset_y = (row + 0.5 * (column % 2)) * size
            translation = rg.Transform.Translation(
                plane.XAxis * offset_x + plane.YAxis * offset_y
            )
            if not cell.Transform(translation):
                raise RuntimeError("Rhino failed to move a hexagon cell.")
            cells.append(cell)
            center_points.append(plane.PointAt(offset_x, offset_y))

            for vertex in range(6):
                corner_key = (
                    3 * column + vertex_x_indices[vertex],
                    2 * row + column % 2 + vertex_y_indices[vertex],
                )
                if corner_key not in corner_points:
                    corner_points[corner_key] = plane.PointAt(
                        corner_key[0] * radius / 2.0,
                        corner_key[1] * size / 2.0,
                    )

    cell_width = 2.0 * radius
    cell_height = size
    cell_label = "Hexagon (w={:.2f}, h={:.2f})".format(
        cell_width, cell_height
    )
    labels = [cell_label for _ in cells]

    return cells, list(corner_points.values()), labels, center_points
# ======================================================================
# Tangent sphere growth
# ======================================================================


def random_unit_vector():
    """Return a random direction on the unit sphere."""
    z = random.uniform(-1.0, 1.0)
    t = random.uniform(0.0, 2.0 * math.pi)
    r = math.sqrt(1.0 - z * z)
    return rg.Vector3d(r * math.cos(t), r * math.sin(t), z)


def rotate_vector(v, axis, angle_rad):
    """Rotate vector v around axis by angle (radians).

    Params:
        v (Rhino.Geometry.Vector3d): Vector to rotate. It is not changed.
        axis (Rhino.Geometry.Vector3d): Rotation axis.
        angle_rad (float): Rotation angle in radians.

    Returns:
        Rhino.Geometry.Vector3d: The rotated copy of v.
    """
    # 1.1 -- copy the input vector and the axis
    vv = rg.Vector3d(v)
    ax = rg.Vector3d(axis)

    # 1.2 -- the axis must be unit length
    ax.Unitize()

    # 1.3 -- build a Rhino rotation transform around the world origin
    xform = rg.Transform.Rotation(
        angle_rad,
        ax,
        rg.Point3d.Origin,
    )

    # 1.4 -- apply the transform to the vector (in place)
    vv.Transform(xform)

    return vv


def random_deflect(dir_vec, angle_max):
    """Deflect a direction vector by a random small rotation.

    Idea:
      - build a plane perpendicular to the direction,
      - pick a random axis in that plane,
      - rotate by a random angle up to angle_max.

    Params:
        dir_vec (Rhino.Geometry.Vector3d): Direction to deflect.
        angle_max (float): Largest deflection angle in radians.

    Returns:
        Rhino.Geometry.Vector3d: The deflected direction.
    """
    # 1.5 -- copy and unitize the incoming direction
    d = rg.Vector3d(dir_vec)
    d.Unitize()

    # choose a helper vector that is not (nearly) parallel to d
    helper = rg.Vector3d(0, 0, 1)
    if abs(rg.Vector3d.Multiply(d, helper)) > 0.95:
        helper = rg.Vector3d(0, 1, 0)

    # 1.6 -- build a perpendicular frame U, V around d
    U = rg.Vector3d.CrossProduct(d, helper)
    U.Unitize()
    V = rg.Vector3d.CrossProduct(d, U)
    V.Unitize()

    # 1.7 -- pick a random axis in the perpendicular plane
    phi = random.uniform(0.0, 2.0 * math.pi)
    axis = U * math.cos(phi) + V * math.sin(phi)

    # 1.8 -- rotate by a random angle up to angle_max
    ang = random.uniform(0.0, angle_max)
    return rotate_vector(d, axis, ang)


def cell_key(pt, cs):
    """Map a 3D point to a grid cell index (ix, iy, iz) for cell size cs."""
    return (
        int(math.floor(pt.X / cs)),
        int(math.floor(pt.Y / cs)),
        int(math.floor(pt.Z / cs)),
    )


def neighbor_keys(k):
    """Yield the 27 cell keys around and including cell k (3x3x3)."""
    x, y, z = k
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                yield (x + dx, y + dy, z + dz)


def can_place_tangent(center, r_child, grid, cs, eps=1e-6):
    """Check whether a sphere can be placed without overlapping others.

    Touching is allowed, overlapping is not. Two spheres overlap when
        distance < r_child + r_existing - eps

    Params:
        center (Rhino.Geometry.Point3d): Center of the new sphere.
        r_child (float): Radius of the new sphere.
        grid (dict): Spatial hash, cell key -> list of (center, radius).
        cs (float): Cell size of the grid.
        eps (float): Tolerance so touching spheres count as free. Default 1e-6.

    Returns:
        bool: True if the sphere fits.
    """
    k = cell_key(center, cs)

    # 2.2 -- only check spheres in nearby grid cells
    for nk in neighbor_keys(k):
        if nk not in grid:
            continue

        for (c2, r2) in grid[nk]:
            # 2.1 -- overlap rule
            if center.DistanceTo(c2) < (r_child + r2 - eps):
                return False

    return True


def add_to_grid(center, radius, grid, cs):
    """Store (center, radius) in its grid cell for fast lookup later."""
    key = cell_key(center, cs)
    # 2.3 -- store center and radius
    grid.setdefault(key, []).append((center, radius))


def grow_tangent_spheres(
    seed_pt=None,
    seed_radius=5.0,
    iterations=30,
    radius_decay=0.92,
    branch_chance=0.2,
    angle_max=0.8,
    min_radius=0.5,
    seed_dir=None,
    seed=None,
):
    """Grow a branching chain of touching spheres from a seed sphere.

    Every generation, each tip places one child sphere (sometimes two) that
    touches its parent. The child is a bit smaller and points in a slightly
    deflected direction. Children that would overlap an existing sphere are
    retried in another direction; growth stops when nothing fits anymore.

    Params:
        seed_pt (Rhino.Geometry.Point3d): Start point. Default world origin.
        seed_radius (float): Radius of the first sphere. Default 5.0.
        iterations (int): Maximum number of generations. Default 30.
        radius_decay (float): Shrink factor per generation. Default 0.92.
        branch_chance (float): Chance (0-1) that a tip gets a second child.
            Default 0.2.
        angle_max (float): Largest deflection per generation, in radians.
            Default 0.8. Below about 0.6 a second child never fits beside
            its sibling, so the growth does not branch.
        min_radius (float): Stop growing a branch when spheres get smaller
            than this. Default 0.5.
        seed_dir (Rhino.Geometry.Vector3d): Initial direction. None picks a
            random one. Default None.
        seed (int): Random seed; the same seed gives the same result.
            None gives a new result every time. Default None.

    Returns:
        tuple: (spheres, lines, tip_points)
            spheres    -- list of Rhino.Geometry.Sphere
            lines      -- list of Rhino.Geometry.Line, parent to child
            tip_points -- list of Rhino.Geometry.Point3d, the last tips
    """
    if seed_pt is None:
        seed_pt = rg.Point3d(0, 0, 0)
    if seed is not None:
        random.seed(seed)

    # STEP 3 -- initial direction: use seed_dir if given, otherwise random
    if seed_dir:
        # 3.1 -- copy and unitize seed_dir
        d0 = rg.Vector3d(seed_dir)
        d0.Unitize()
    else:
        d0 = random_unit_vector()

    spheres, lines = [], []

    # 4.1 -- cell size for the spatial hash. Two spheres can only collide
    # when their centers are closer than the sum of their radii, which is
    # at most 2 * seed_radius. With cells at least that big, checking the
    # 3x3x3 neighbouring cells is enough to find every possible collision.
    cell_size = max(2.0 * seed_radius, 2.0 * min_radius)

    grid = {}

    # 4.2 -- create the seed sphere and store it in the grid
    spheres.append(rg.Sphere(seed_pt, seed_radius))
    add_to_grid(seed_pt, seed_radius, grid, cell_size)

    # 4.3 -- tips are the active growth states: (point, direction, radius)
    tips = [(seed_pt, d0, seed_radius)]

    for i in range(iterations):

        new_tips = []

        # 4.4 -- grow from each active tip
        for (pt, d, r_parent) in tips:

            # child radius shrinks
            r_child = r_parent * radius_decay
            if r_child < min_radius:
                continue

            # 4.5 -- branching: usually 1 child, sometimes 2
            n_children = 1 + (1 if random.random() < branch_chance else 0)

            for c in range(n_children):

                # 4.6 -- try up to 20 directions to find a free placement
                for t in range(20):

                    # new direction = deflected parent direction
                    d_child = random_deflect(d, angle_max)
                    d_child.Unitize()

                    # 4.7 -- tangency rule:
                    # distance between centers = r_parent + r_child
                    step = r_parent + r_child
                    new_pt = pt + d_child * step

                    # 4.8 -- accept only if nothing overlaps
                    if can_place_tangent(new_pt, r_child, grid, cell_size, eps=1e-4):

                        spheres.append(rg.Sphere(new_pt, r_child))
                        add_to_grid(new_pt, r_child, grid, cell_size)

                        # connection line from parent to child
                        lines.append(rg.Line(pt, new_pt))

                        # the child becomes a new tip
                        new_tips.append((new_pt, d_child, r_child))
                        break  # placed, stop trying

        # 4.9 -- stop early if nothing new could be placed
        if not new_tips:
            break

        tips = new_tips

    # STEP 5 -- output only the tip points
    tip_points = [pt for (pt, d, r) in tips]

    return spheres, lines, tip_points
