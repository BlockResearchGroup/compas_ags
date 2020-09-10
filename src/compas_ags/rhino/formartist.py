from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from math import fabs
from compas_ags.rhino.diagramartist import DiagramArtist


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
        self._guid_force = {}
        self.color_compression = (0, 0, 255)
        self.color_tension = (255, 0, 0)
        self.scale_forces = 0.01
        self.tol_forces = 0.001

    @property
    def guids(self):
        guids = super(FormArtist, self).guids
        guids += list(self.guid_force.keys())
        return guids

    @property
    def guid_force(self):
        """Map between Rhino object GUIDs and form diagram edge force identifiers."""
        return self._guid_force

    @guid_force.setter
    def guid_force(self, values):
        self._guid_force = dict(values)

    def clear(self):
        super(FormArtist, self).clear()
        compas_rhino.delete_objects(self.guids, purge=True)
        self._guid_force = {}

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
        guids = compas_rhino.draw_pipes(pipes, layer=self.layer, clear=False, redraw=False)
        self.guid_force = zip(guids, edges)
        return guids


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
