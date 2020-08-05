from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__all__ = [
    'calculate_drawing_scale',
    'find_anchor_point',
    'calculate_force_scale',
]


def calculate_drawing_scale(form, force):
    """Calculate an appropriate scale factor to create the force diagram.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to draw.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to draw.

    Returns
    -------
    scale : float
        Appropriate scale factor to draw form and force diagram next to each other

    """

    form_x = form.vertices_attribute('x')
    form_y = form.vertices_attribute('y')
    form_xdim = max(form_x) - min(form_x)
    form_ydim = max(form_y) - min(form_y)

    force_x = force.vertices_attribute('x')
    force_y = force.vertices_attribute('y')
    force_xdim = max(force_x) - min(force_x)
    force_ydim = max(force_y) - min(force_y)

    scale = 1 / max([force_xdim / form_xdim, force_ydim / form_ydim])

    return scale


def find_anchor_point(form, force):
    """Calculate an appropriate position to draw the force diagram.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to draw.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to draw.

    Returns
    -------
    [X, Y, Z] : list
        Proposed position hang the anchor point of the force diagram

    """

    form_x = form.vertices_attribute('x')
    form_y = form.vertices_attribute('y')
    form_xdim = max(form_x) - min(form_x)
    form_xmax = max(form_x)
    form_ymid = 0.5 * (max(form_y) - min(form_y)) + min(form_y)

    return [form_xdim + form_xmax, form_ymid, 0]


def calculate_force_scale(form):
    """Calculate an appropriate scale to the thickness of the forces in the form diagram.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to draw.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to draw.

    Returns
    -------
    scale : float
        Appropriate scale factor to thickness of form diagram lines.

    """

    q = [abs(form.edge_attribute(uv, 'q')) for uv in form.edges_where({'is_external': False})]
    scale = 0.1/max(q)  # highest force/length radio equals 10% of length

    return scale
