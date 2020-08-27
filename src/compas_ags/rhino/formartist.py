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
    scale : float, optional
        The drawing scale.
        Default is ``1.0``.
    settings : dict, optional
        Customisation of the artist settings.

    Other Parameters
    ----------------
    See the parent artists for other parameters.

    Attributes
    ----------
    guid_force : dict
        Map between Rhino object GUIDs and force diagram force identifiers.

    """

    def __init__(self, form, scale=None, settings=None, **kwargs):
        super(FormArtist, self).__init__(form, **kwargs)
        self._guid_force = {}
        self.scale = scale
        if settings:
            self.settings.update(settings)

    @property
    def guid_force(self):
        """Map between Rhino object GUIDs and form diagram edge force identifiers."""
        return self._guid_force

    @guid_force.setter
    def guid_force(self, values):
        self._guid_force = dict(values)

    def clear(self):
        super(FormArtist, self).clear()
        guids = []
        guids += list(self.guid_force.keys())
        compas_rhino.delete_objects(guids, purge=True)
        self._guid_force = {}

    def draw(self):
        """Draw the form diagram.

        The visible components, display properties and visual style of the form diagram
        drawn by this method can be fully customised using the configuration items
        in the settings dict: ``FormArtist.settings``.

        The method will clear the scene of any objects it has previously drawn
        and keep track of any newly created objects using their GUID.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        tol = self.settings['tol.forces']
        # vertices
        if self.settings['show.vertices']:
            color = {}
            color.update({vertex: self.settings['color.vertices'] for vertex in self.diagram.vertices()})
            color.update({vertex: self.settings['color.vertices:is_fixed'] for vertex in self.diagram.vertices_where({'is_fixed': True})})
            self.draw_vertices(color=color)
        # edges
        if self.settings['show.edges']:
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where({'is_load': True})})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where({'is_reaction': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where({'is_ind': True})})
            # forces of the structure
            if self.settings['show.forces']:
                color.update({edge: self.settings['color.tension'] for edge in self.diagram.edges_where({'is_external': False}) if self.diagram.edge_attribute(edge, 'f') > tol})
                color.update({edge: self.settings['color.compression'] for edge in self.diagram.edges_where({'is_external': False}) if self.diagram.edge_attribute(edge, 'f') < -tol})
            self.draw_edges(color=color)
        # vertex labels
        if self.settings['show.vertexlabels']:
            text = {vertex: index for index, vertex in enumerate(self.diagram.vertices())}
            color = {}
            color.update({vertex: self.settings['color.vertexlabels'] for vertex in self.diagram.vertices()})
            color.update({vertex: self.settings['color.vertices:is_fixed'] for vertex in self.diagram.vertices_where({'is_fixed': True})})
            self.draw_vertexlabels(text=text, color=color)
        # edge labels
        if self.settings['show.edgelabels']:
            text = {edge: index for index, edge in enumerate(self.diagram.edges())}
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where({'is_load': True})})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where({'is_reaction': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where({'is_ind': True})})
            # forces of the structure
            if self.settings['show.forces']:
                color.update({edge: self.settings['color.tension'] for edge in self.diagram.edges_where({'is_external': False}) if self.diagram.edge_attribute(edge, 'f') > tol})
                color.update({edge: self.settings['color.compression'] for edge in self.diagram.edges_where({'is_external': False}) if self.diagram.edge_attribute(edge, 'f') < -tol})
            self.draw_edgelabels(text=text, color=color)
        # force magnitude labels
        if self.settings['show.forcelabels']:
            text = {}
            for index, edge in enumerate(self.diagram.edges()):
                f = self.diagram.edge_attribute(edge, 'f')
                text[edge] = "%s kN {%s}" % (round(abs(f), 2), index)
            color = {}
            color.update({edge: self.settings['color.edges'] for edge in self.diagram.edges()})
            color.update({edge: self.settings['color.edges:is_external'] for edge in self.diagram.edges_where({'is_external': True})})
            color.update({edge: self.settings['color.edges:is_load'] for edge in self.diagram.edges_where({'is_load': True})})
            color.update({edge: self.settings['color.edges:is_reaction'] for edge in self.diagram.edges_where({'is_reaction': True})})
            color.update({edge: self.settings['color.edges:is_ind'] for edge in self.diagram.edges_where({'is_ind': True})})
            color.update({edge: self.settings['color.tension'] for edge in self.diagram.edges_where({'is_external': False}) if self.diagram.edge_attribute(edge, 'f') > tol})
            color.update({edge: self.settings['color.compression'] for edge in self.diagram.edges_where({'is_external': False}) if self.diagram.edge_attribute(edge, 'f') < -tol})
            self.draw_edgelabels(text=text, color=color)
        # forces
        if self.settings['show.forces']:
            self.draw_forces()

    def draw_forces(self):
        """Draw the forces in the internal edges as pipes with color and thickness matching the force value.

        Parameters
        ----------
        None

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        color_compression = self.settings['color.compression']
        color_tension = self.settings['color.tension']
        scale = self.settings['scale.forces']
        tol = self.settings['tol.forces']
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
