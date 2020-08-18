from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import angle_vectors_xy
from compas.geometry import subtract_vectors


__all__ = [
    'check_deviations',
]


def check_deviations(form, force, tol=10e-3):
    """Checks whether the form and force diagrams are indeed reciprocal, i.e. have their corresponding edges parallel.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to check deviations.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to check deviations.
    tol: float (10e-3)
        The tolerance allowd for the deviations.

    Returns
    -------
    checked : bool
        Return whether of not the diagram passes the check with no deviations greater than the tolerance.

    """

    edges_form = list(form.edges())
    edges_force = force.ordered_edges(form)
    checked = True

    for i in range(len(edges_form)):
        pt0, pt1 = form.edge_coordinates(edges_form[i][0], edges_form[i][1])
        _pt0, _pt1 = force.edge_coordinates(edges_force[i][0], edges_force[i][1])
        a = angle_vectors_xy(subtract_vectors(pt1, pt0), subtract_vectors(_pt1, _pt0), deg=True)
        if a < tol or a > 180 - tol:
            a = 0.0
        else:
            checked = False
            a = min(a, 180 - a)
        form.edge_attribute(edges_form[i], 'a', a)

    return checked
