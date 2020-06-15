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
        self.settings.update({
            'color.anchor':(255, 0, 0)
        })
        self.update_edge_force()


    @property
    def force(self):
        return self.mesh


    def draw_diagram(self, form=None, scale=None):
        self.clear()
        compas_rhino.delete_objects_by_name(name='{}.*'.format(self.force.name))

        # scale the force diagram according to the dimension of form diagram
        if scale is True and form is not None:
            scale = self.calculate_scale(form)
            self.scale_diagram(scale)
        elif scale is not None:
            self.scale_diagram(scale)

        self.draw_vertices()
        self.draw_vertexlabels()
        self.draw_edges()
        if form is not None:
            self.draw_edgelabels(text=check_edge_pairs(form, self.force)[1])
        self.redraw()


    def calculate_scale(self, form):
        form_x = form.vertices_attribute('x')
        form_y = form.vertices_attribute('y')
        form_xdim = max(form_x) - min(form_x)
        form_ydim = max(form_y) - min(form_y)

        force_x = self.force.vertices_attribute('x')
        force_y = self.force.vertices_attribute('y')
        force_xdim = max(force_x) - min(force_x)
        force_ydim = max(force_y) - min(force_y)

        scale = max([force_xdim / form_xdim, force_ydim / form_ydim])
        return scale

    
    def scale_diagram(self, scale):
        x = self.force.vertices_attribute('x')
        y = self.force.vertices_attribute('y')
        anchor = self.force.anchor()
        dx = self.force.vertex_coordinates(anchor)[0]
        dy = self.force.vertex_coordinates(anchor)[1]

        for vkey, attr in self.force.vertices(True):
            attr['x'] = dx + (attr['x'] - dx) / scale
            attr['y'] = dy + (attr['y'] - dy) / scale


    def clear_anchor_vertex(self):
        compas_rhino.delete_objects_by_name(name='{}.anchor_vertex.*'.format(self.force.name))


    def draw_anchor_vertex(self, color=None):
        self.clear_anchor_vertex()
        anchor = self.force.anchor()
        self.clear_vertexlabels(keys=[anchor])
        labels = []
        labels.append({
            'pos'  : self.force.vertex_coordinates(anchor),
            'text' : str(anchor),
            'color': color or self.settings.get('color.anchor'),
            'name' : "{}.anchor_vertex.{}".format(self.force.name, anchor)
        })
        compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=True)


    def update_edge_force(self):
        (u, v) = list(self.force.edges())[0] # get an edge
        # check whether the force diagram is scaled already
        if self.force.edge_attribute((u, v), 'force') is None:  
            self.force.update_default_edge_attributes({'force': 0.0})
            for i, ((u, v), attr) in enumerate(self.force.edges(data=True)):
                length = self.force.edge_length(u, v)
                length = round(length, 2)
                attr['force'] = length


    def draw_edge_force(self, draw=True):
        force_dict = {}
        c_dict  = {}
        max_length = 0

        for i, ((u, v), attr) in enumerate(self.force.edges(data=True)):
            length = attr['force']
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
