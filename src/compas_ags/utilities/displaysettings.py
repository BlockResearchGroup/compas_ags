from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__all__ = [
    'calculate_drawingscale',
    'initial_position_anchor_point',
    'calculate_drawingscale_forces',
]


def calculate_drawingscale(form, force):
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


def initial_position_anchor_point(form, force):
    """Calculate an appropriate position to draw the force diagram, such as the
    right tip of form and the left tip of force are in the same y-coord and distant
    to each other the amount of 1/2 form's extension in x.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to draw.
    force: compas_ags.diagrams.ForceDiagram
        The force diagram to draw.

    """

    form_xyz = list(form.vertex_xyz.values())
    force_xyz = list(force.vertex_xyz.values())

    form_xmax = max([xyz[0] for xyz in form_xyz])
    form_xmin = min([xyz[0] for xyz in form_xyz])
    form_ymin = min([xyz[1] for xyz in form_xyz])

    force_xmin = min([xyz[0] for xyz in force_xyz])
    force_ymin = min([xyz[1] for xyz in force_xyz])

    spacing = 0.5 * (form_xmax - form_xmin)

    force.location[0] += form_xmax + spacing - force_xmin
    force.location[1] += form_ymin - force_ymin

    return


def calculate_drawingscale_forces(form):
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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
