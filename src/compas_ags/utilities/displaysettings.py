from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import distance_point_point_xy


__all__ = [
    'compute_force_drawingscale',
    'compute_force_drawinglocation',
    'compute_form_forcescale',
]


def compute_force_drawingscale(form, force):
    """Compute an appropriate scale factor to create the force diagram.

    Parameters
    ----------
    form: :class:`compas_ags.rhino.FormObject`
    force: :class:`compas_ags.rhino.ForceObject`

    Returns
    -------
    scale: float
        Appropriate scale factor to draw form and force diagram next to each other
    """
    # form_x = form.diagram.vertices_attribute('x')
    # form_y = form.diagram.vertices_attribute('y')
    # form_xdim = max(form_x) - min(form_x)
    # form_ydim = max(form_y) - min(form_y)
    # force_x = force.diagram.vertices_attribute('x')
    # force_y = force.diagram.vertices_attribute('y')
    # force_xdim = max(force_x) - min(force_x)
    # force_ydim = max(force_y) - min(force_y)
    # scale = 1 / max([force_xdim / form_xdim, force_ydim / form_ydim])
    form_bbox = form.diagram.bounding_box_xy()
    force_bbox = force.diagram.bounding_box_xy()
    form_diagonal = distance_point_point_xy(form_bbox[0], form_bbox[2])
    force_diagonal = distance_point_point_xy(force_bbox[0], force_bbox[2])
    return 0.75 * form_diagonal / force_diagonal


def compute_force_drawinglocation(form, force):
    """Compute an appropriate location for the force diagram.

    Parameters
    ----------
    form: :class:`compas_ags.rhino.FormObject`
    force: :class:`compas_ags.rhino.ForceObject`

    Returns
    -------
    :class:`compas.geometry.Point`
    """
    point = force.location

    form_xyz = list(form.vertex_xyz.values())
    force_xyz = list(force.vertex_xyz.values())
    form_xmax = max([xyz[0] for xyz in form_xyz])
    form_xmin = min([xyz[0] for xyz in form_xyz])
    form_ymin = min([xyz[1] for xyz in form_xyz])
    force_xmin = min([xyz[0] for xyz in force_xyz])
    force_ymin = min([xyz[1] for xyz in force_xyz])

    spacing = 0.5 * (form_xmax - form_xmin)

    point[0] += form_xmax + spacing - force_xmin
    point[1] += form_ymin - force_ymin
    return point


def compute_form_forcescale(form):
    """Calculate an appropriate scale to the thickness of the forces in the form diagram.

    Parameters
    ----------
    form: :class:`compas_ags.rhino.FormObject`

    Returns
    -------
    scale: float
        Appropriate scale factor to thickness of form diagram lines.
    """
    q = [abs(form.diagram.edge_attribute(uv, 'q')) for uv in form.diagram.edges_where({'is_external': False})]

    scale = 0.1 / max(q)
    return scale


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
