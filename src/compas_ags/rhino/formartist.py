from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from functools import partial
from math import fabs
from compas_ags.rhino.diagramartist import DiagramArtist
from compas.utilities import color_to_colordict

colordict = partial(color_to_colordict, colorformat='rgb', normalize=False)


__all__ = ['FormArtist']


class FormArtist(DiagramArtist):
    """Artist for form diagram in AGS.

    Parameters
    ----------
    form: compas_ags.diagrams.FormDiagram
        The form diagram to draw.

    Attributes
    ----------
    color_compression : 3-tuple
        Default color for compression.
    color_tension : 3-tuple
        Default color for tension.
    scale_forces : float
        Scale factor for the force pipes.
    tol_forces : float
        Tolerance for force magnitudes.
    """

    def __init__(self, form, layer=None):
        super(FormArtist, self).__init__(form, layer=layer)
        self.color_compression = (0, 0, 255)
        self.color_tension = (255, 0, 0)
        self.scale_forces = 0.01
        self.tol_forces = 0.001

    def draw_edges(self, edges=None, color=None):
        """Draw a selection of edges.

        Parameters
        ----------
        edges : list, optional
            A selection of edges to draw.
            The default is ``None``, in which case all edges are drawn.
        color : tuple or dict of tuple, optional
            The color specififcation for the edges.
            The default color is black, ``(0, 0, 0)``.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.

        """
        leaves = set(self.diagram.leaves())
        edges = edges or list(self.diagram.edges())
        vertex_xyz = self.vertex_xyz
        edge_color = colordict(color, edges, default=self.color_edges)
        lines = []
        for edge in edges:
            arrow = None
            if self.diagram.edge_attribute(edge, 'is_external'):
                f = self.diagram.edge_attribute(edge, 'f')
                if f > 0:
                    arrow = 'start' if edge[0] in leaves else 'end'
                elif f < 0:
                    arrow = 'start' if edge[1] in leaves else 'end'
            lines.append({
                'start': vertex_xyz[edge[0]],
                'end': vertex_xyz[edge[1]],
                'color': edge_color[edge],
                'name': "{}.edge.{}-{}".format(self.diagram.name, *edge),
                'arrow': arrow})
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_forcepipes(self, color_compression=None, color_tension=None, scale=None, tol=None):
        """Draw the forces in the internal edges as pipes with color and thickness matching the force value.

        Parameters
        ----------
        color_compression
        color_tension
        scale
        tol

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        color_compression = color_compression or self.color_compression
        color_tension = color_tension or self.color_tension
        scale = scale or self.scale_forces
        tol = tol or self.tol_forces
        vertex_xyz = self.vertex_xyz
        edges = []
        pipes = []
        for edge in self.diagram.edges_where({'is_external': False}):
            force = self.diagram.edge_attribute(edge, 'f')
            if not force:
                continue
            radius = fabs(scale * force)
            if radius < tol:
                continue
            edges.append(edge)
            color = color_tension if force > 0 else color_compression
            pipes.append({'points': [vertex_xyz[edge[0]], vertex_xyz[edge[1]]],
                          'color': color,
                          'radius': radius,
                          'name': "{}.force.{}-{}".format(self.diagram.name, *edge)})
        return compas_rhino.draw_pipes(pipes, layer=self.layer, clear=False, redraw=False)
