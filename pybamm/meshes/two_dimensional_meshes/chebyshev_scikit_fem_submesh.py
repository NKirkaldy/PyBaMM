#
# Chebyshev scikit-fem mesh for use in PyBaMM
#
import pybamm
from .base_scikit_fem_submesh import ScikitSubMesh2D

import numpy as np


class ScikitChebyshev2DSubMesh(ScikitSubMesh2D):
    """
    Contains information about the 2D finite element mesh generated by taking the
    tensor product of two 1D meshes which use Chebyshev nodes on the
    interval (a, b), given by

   .. math::
    x_{k} = \\frac{1}{2}(a+b) + \\frac{1}{2}(b-a) \\cos(\\frac{2k-1}{2N}\\pi),

    for k = 1, ..., N, where N is the number of nodes. Note: this mesh then
    appends the boundary nodes, so that the 1D mesh edges are given by

    .. math ::
     a < x_{1} < ... < x_{N} < b.

    Note: This class only allows for the use of piecewise-linear triangular
    finite elements.

    Parameters
    ----------
    lims : dict
        A dictionary that contains the limits of each
        spatial variable
    npts : dict
        A dictionary that contains the number of points to be used on each
        spatial variable
    tabs : dict
        A dictionary that contains information about the size and location of
        the tabs
    """

    def __init__(self, lims, npts, tabs):

        # check that two variables have been passed in
        if len(lims) != 2:
            raise pybamm.GeometryError(
                "lims should contain exactly two variables, not {}".format(len(lims))
            )

        # get spatial variables
        spatial_vars = list(lims.keys())

        # check coordinate system agrees
        if spatial_vars[0].coord_sys == spatial_vars[1].coord_sys:
            coord_sys = spatial_vars[0].coord_sys
        else:
            raise pybamm.DomainError(
                """spatial variables should have the same coordinate system,
                but have coordinate systems {} and {}""".format(
                    spatial_vars[0].coord_sys, spatial_vars[1].coord_sys
                )
            )

        # compute edges
        edges = {}
        for var in spatial_vars:
            if var.name not in ["y", "z"]:
                raise pybamm.DomainError(
                    "spatial variable must be y or z not {}".format(var.name)
                )
            else:
                # Create N Chebyshev nodes in the interval (a,b)
                N = npts[var.id] - 2
                ii = np.array(range(1, N + 1))
                a = lims[var]["min"]
                b = lims[var]["max"]
                x_cheb = (a + b) / 2 + (b - a) / 2 * np.cos(
                    (2 * ii - 1) * np.pi / 2 / N
                )

                # Append the boundary nodes. Note: we need to flip the order the
                # Chebyshev nodes as they are created in descending order.
                edges[var.name] = np.concatenate(([a], np.flip(x_cheb), [b]))

        super().__init__(edges, coord_sys, tabs)
