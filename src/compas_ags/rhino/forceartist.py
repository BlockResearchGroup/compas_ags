from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas.geometry import distance_point_point
from compas.utilities import i_to_rgb
from compas_rhino.artists import MeshArtist

from compas_ags.rhino import find_force_ind
from .diagramhelper import check_edge_pairs

__all__ = ['ForceArtist']


class ForceArtist(MeshArtist):
    """Inherits the compas :class:`MeshArtist`, provides functionality for visualisation of 3D graphic statics applications.
    
    Parameters
    ----------
    form: compas_ags.forcediagram.ForceDiagram
        The force diagram to draw.
    layer: string, optional
        The name of the layer that will contain the forcediagram.
    """
    
    __module__ = 'compas_tna.rhino'

    def __init__(self, force, layer=None):
        super(ForceArtist, self).__init__(force, layer=layer)


    @property
    def force(self):
        return self.mesh


    def draw_diagram(self, form=None):
        self.clear()
        self.draw_vertices()
        self.draw_vertexlabels()
        self.draw_edges()
        if form is not None:
            self.draw_edgelabels(text=check_edge_pairs(form, self.force)[1])
        self.redraw()


    def draw_edge_force(self, draw=True):
        force_dict = {}
        c_dict  = {}

        max_length = 0
        for i, (u, v) in enumerate(self.force.edges()):
            length = distance_point_point(self.force.vertex_coordinates(u), self.force.vertex_coordinates(v))
            length = round(length, 2)
            if length > max_length:
                max_length = length
            force_dict[(u, v)] = length
        
        for i, (u, v) in enumerate(self.force.edges()):
            value = force_dict[(u, v)] / max_length
            c_dict[(u, v)] = i_to_rgb(value)
        
        if draw is True:
            self.draw_edgelabels(text=dict((v,"%s kN" % k) for v, k in force_dict.items()), color=c_dict)
        return c_dict

    
    def clear_independent_edge(self):
        compas_rhino.delete_objects_by_name(name='{}.independent_edge.*'.format(self.force.name))


    def draw_independent_edges(self, form):
        self.clear_independent_edge()
        indices = find_force_ind(form, self.force)
        print(indices)
        lines = []
        for index, ((u, v), attr) in enumerate(self.force.edges(True)):
            if (u, v) in indices:
                lines.append({
                    'start': self.force.vertex_coordinates(u),
                    'end': self.force.vertex_coordinates(v),
                    'name': "{}.independent_edge.{}".format(self.force.name, index),
                    'width': 1.0
                })
        return compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
