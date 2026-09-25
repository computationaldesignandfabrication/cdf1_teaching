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

def create_sphere():
    pass  # TODO: Implement this function to create a sphere using Rhino.Geometry

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