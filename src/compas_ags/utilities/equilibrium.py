from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import angle_vectors_xy
from compas.geometry import subtract_vectors


__all__ = [
    'check_deviations',
    'check_force_length_constraints',
    'check_equilibrium',
]


def check_deviations(form, force, tol=10e-3, printout=False):
    """Checks whether the form and force diagrams are indeed reciprocal, i.e. have their corresponding edges parallel.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to check deviations.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to check deviations.
    tol: float, optional
        Stopping criteria tolerance for angle deviations.
        The default value is ``10e-3``.
    printout: boll, optional
        Whether or not print intermediate messages.
        The default value is ``False``.

    Returns
    -------
    checked : bool
        Return whether of not the diagram passes the check with no deviations greater than the tolerance.

    """

    edges_form = list(form.edges())
    edges_force = force.ordered_edges(form)
    checked = True
    a_max = 0.0

    for i in range(len(edges_form)):
        pt0, pt1 = form.edge_coordinates(edges_form[i][0], edges_form[i][1])
        _pt0, _pt1 = force.edge_coordinates(edges_force[i][0], edges_force[i][1])
        a = angle_vectors_xy(subtract_vectors(pt1, pt0), subtract_vectors(_pt1, _pt0), deg=True)
        if a < tol or a > 180 - tol:
            a = 0.0
        else:
            checked = False
            a = min(a, 180 - a)
        if a > a_max:
            a_max = a
        form.edge_attribute(edges_form[i], 'a', a)

    if printout:
        if a_max > tol:
            print('> Equilibrium Check | Max deviation:', a_max)

    return checked


def check_force_length_constraints(force, tol=10e-3, printout=False):
    """Checks whether target length constraints applied to the force diagrams are respected, i.e. are below the tolerance criteria.

    Parameters
    ----------
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to check deviations.
    tol: float, optional
        Stopping criteria tolerance for angle deviations.
        The default value is ``10e-3``.
    printout: boll, optional
        Whether or not print intermediate messages.
        The default value is ``False``.

    Returns
    -------
    checked : bool
        Return whether of not the diagram passes the check with no deviations greater than the tolerance.

    """
    checked = True
    max_diff = 0.0

    for u, v in force.edges():
        target_constraint = force.edge_attribute((u, v), 'target_length')
        if target_constraint:
            length = force.edge_length(u, v)
            diff = abs(length - target_constraint)
            if diff > tol:
                checked = False
            if diff > max_diff:
                max_diff = diff

    if printout:
        if max_diff > tol:
            print('> Equilibrium Check | Constraints violation:', max_diff)

    return checked


def check_equilibrium(form, force, tol=10e-3, printout=False):
    """Checks if maximum deviations and constraints exceed is below the tolerance.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to check equilibrium.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to check equilibrium.
    tol: float, optional
        Stopping criteria tolerance for angle deviations.
        The default value is ``10e-3``.
    printout: boll, optional
        Whether or not print intermediate messages.
        The default value is ``False``.

    Returns
    -------
    checked : bool
        Return whether of not the diagram passes the check.

    """

    checked = check_deviations(form, force, tol=tol, printout=printout) and check_force_length_constraints(force, tol=tol, printout=printout)

    return checked
