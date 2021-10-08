from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import angle_vectors_xy
from compas.geometry import subtract_vectors
from compas.geometry import distance_point_point_xy


__all__ = [
    'check_deviations',
    'check_force_length_constraints',
    'check_equilibrium',
]


def check_deviations(form, force, tol_angle=0.5, tol_force=0.05, printout=False):
    """Checks whether the form and force diagrams are indeed reciprocal, i.e. have their corresponding edges parallel.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to check deviations.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to check deviations.
    tol_angle: float, optional
        Stopping criteria tolerance for angle deviations.
        The default value is ``0.5``.
    tol_force: float, optional
        Stopping criteria tolerance for the constraints on the length.
        The default value is ``0.05``.
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

    for i in range(len(edges_form)):
        pt0, pt1 = form.edge_coordinates(edges_form[i][0], edges_form[i][1])
        _pt0, _pt1 = force.edge_coordinates(edges_force[i][0], edges_force[i][1])
        a = angle_vectors_xy(subtract_vectors(pt1, pt0), subtract_vectors(_pt1, _pt0), deg=True)
        if a < tol_angle or a > 180 - tol_angle:
            pass
        else:
            if distance_point_point_xy(_pt0, _pt1) > tol_force:  # exclude edges with zero-force
                checked = False
                break

    if printout:
        if not checked:
            print('> Equilibrium Check | Max deviation exceed angle tolerance:', tol_angle)

    return checked


def check_force_length_constraints(force, tol_force=0.05, printout=False):
    """Checks whether target length constraints applied to the force diagrams are respected, i.e. are below the tolerance criteria.

    Parameters
    ----------
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to check deviations.
    tol_forces: float, optional
        Stopping criteria tolerance for the edge lengths (i.e. force magnitude) in the force diagram.
        The default value is ``0.05``.
    printout: boll, optional
        Whether or not print intermediate messages.
        The default value is ``False``.

    Returns
    -------
    checked : bool
        Return whether of not the diagram passes the check with no deviations greater than the tolerance.

    """
    checked = True

    for u, v in force.edges():
        target_constraint = force.dual_edge_targetforce((u, v))
        if target_constraint:
            length = force.edge_length(u, v)
            diff = abs(length - target_constraint)
            if diff > tol_force:
                checked = False
                break

    if printout:
        if not checked:
            print('> Equilibrium Check | Constraints violate tolerance:', tol_force)

    return checked


def check_equilibrium(form, force, tol_angle=0.5, tol_force=0.05, printout=False):
    """Checks if maximum deviations and constraints exceed is below the tolerance.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to check equilibrium.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to check equilibrium.
    tol_angle: float, optional
        Stopping criteria tolerance for angle deviations.
        The default value is ``0.5``.
    tol_force: float, optional
        Stopping criteria tolerance for the constraints on the length.
        The default value is ``0.05``.
    printout: boll, optional
        Whether or not print intermediate messages.
        The default value is ``False``.

    Returns
    -------
    checked : bool
        Return whether of not the diagram passes the check.

    """

    checked_deviations = check_deviations(form, force, tol_angle=tol_angle, tol_force=tol_force, printout=printout)
    checked_forces = check_force_length_constraints(force, tol_force=tol_force, printout=printout)
    checked = checked_deviations and checked_forces

    return checked
