from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__all__ = ['calculate_scale',
            'calculate_anchor',
            'calculate_pipe_scale']


def calculate_scale(form, force):
    # calculate the scale factor of force diagram
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


def calculate_anchor(form, force):
    # calculate a nice position for force diagram
    form_x = form.vertices_attribute('x')
    form_y = form.vertices_attribute('y')
    form_xdim = max(form_x) - min(form_x)
    form_xmax = max(form_x)
    form_ymid = 0.5 * (max(form_y) - min(form_y)) + min(form_y)

    return [form_xdim + form_xmax, form_ymid, 0]


def calculate_pipe_scale(form):
    # calculate a maximum scale for pipes in the diagram.
    q = [abs(form.edge_attribute(uv, 'q')) for uv in form.edges_where({'is_external': False})]
    scale = 0.1/max(q)  # highest force/length radio equals 10% of length
    return scale
