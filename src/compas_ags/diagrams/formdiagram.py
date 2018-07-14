from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import FaceNetwork
from compas.utilities import geometric_key2

from compas.topology import network_is_xy
# from compas.topology import network_is_planar
# from compas.topology import network_is_planar_embedding
# from compas.topology import network_embed_in_plane


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'FormDiagram'
]


class FormDiagram(FaceNetwork):
    """"""

    def __init__(self):
        super(FormDiagram, self).__init__()
        self.attributes.update({
            'name'                  : 'FormDiagram',
            'color.vertex'          : (255, 255, 255),
            'color.edge'            : (0, 0, 0),
            'color.face'            : (0, 255, 255),
            'color.vertex:is_fixed' : (255, 0, 0),
        })
        self.update_default_vertex_attributes({
            'is_fixed': False,
            'cx': 0.0,
            'cy': 0.0,
        })
        self.update_default_edge_attributes({
            'q': 1.0,
            'f': 0.0,
            'l': 0.0,
            'is_ind': False,
            'is_element': False,
            'is_reaction': False,
            'is_load': False,

        })

    # --------------------------------------------------------------------------
    # faces
    # --------------------------------------------------------------------------

    def breakpoints(self):
        return list(set(self.leaves() + self.fixed()))

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving the attributes of the formdiagram.
    # --------------------------------------------------------------------------

    def q(self):
        return [attr['q'] for u, v, attr in self.edges(True)]

    def xy(self):
        return [[attr['x'], attr['y']] for key, attr in self.vertices(True)]

    def fixed(self):
        return [key for key, attr in self.vertices(True) if attr['is_fixed']]

    def constrained(self):
        return [key for key, attr in self.vertices(True) if attr['cx'] or attr['cy']]

    def constraints(self):
        cx = [attr['cx'] for key, attr in self.vertices(True)]
        cy = [attr['cy'] for key, attr in self.vertices(True)]
        return cx, cy

    def ind(self):
        return [(u, v) for u, v, attr in self.edges(True) if attr['is_ind']]

    # --------------------------------------------------------------------------
    # Set stuff
    # --------------------------------------------------------------------------

    def set_fixed(self, keys):
        for key, attr in self.vertices(True):
            attr['is_fixed'] = key in keys

    def set_edge_force(self, u, v, force):
        l = self.edge_length(u, v)
        self.edge[u][v]['is_ind'] = True
        self.edge[u][v]['q'] = force / l

    def set_edge_force_by_index(self, index, force):
        for i, (u, v) in enumerate(self.edges()):
            if i == index:
                self.set_edge_force(u, v, force)
                break

    # --------------------------------------------------------------------------
    # Identify features of the formdiagram based on geometrical inputs.
    # --------------------------------------------------------------------------

    def identify_fixed(self, points=None, fix_degree=1):
        for key, attr in self.vertices(True):
            attr['is_fixed'] = self.vertex_degree(key) <= fix_degree
        if points:
            xy_key = {}
            for key in self.vertices():
                gkey = geometric_key2(self.vertex_coordinates(key, 'xy'))
                xy_key[gkey] = key
            for xy in points:
                gkey = geometric_key2(xy)
                if gkey in xy_key:
                    key = xy_key[gkey]
                    self.vertex[key]['is_fixed'] = True

    def identify_constraints(self, points=None):
        if points:
            xy_key = {}
            for key in self.vertices():
                gkey = geometric_key2(self.vertex_coordinates(key, 'xy'))
                xy_key[gkey] = key
            for xy in points:
                gkey = geometric_key2(xy)
                if gkey in xy_key:
                    key = xy_key[gkey]
                    self.vertex[key]['cx'] = 1.0
                    self.vertex[key]['cy'] = 1.0

    # --------------------------------------------------------------------------
    # Topological functionality
    # --------------------------------------------------------------------------

    def is_2d(self):
        return network_is_xy(self)

    # def is_planar(self):
    #     return network_is_planar(self)

    # def is_embedded(self):
    #     return network_is_planar_embedding(self)

    # --------------------------------------------------------------------------
    # Geometric functionality
    # --------------------------------------------------------------------------

    # def embed(self, fix=None):
    #     network_embed_in_plane(self, fix=fix)

    # def embedded(self):
    #     network = self.copy()
    #     network.embed()
    #     return network


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    import compas_ags

    from compas.plotters import NetworkPlotter

    form = FormDiagram.from_obj(compas_ags.get('paper/fink.obj'))

    lines = []
    for u, v in form.edges():
        lines.append({
            'start': form.vertex_coordinates(u),
            'end'  : form.vertex_coordinates(v),
            'color': '#cccccc',
            'width': 0.5,
        })

    form.identify_fixed()

    vcolor = {key: '#ff0000' for key in form.fixed()}
    vlabel = {key: key for key in form.vertices()}
    elabel = {(u, v): str(index) for index, (u, v) in enumerate(form.edges())}

    plotter = NetworkPlotter(form, figsize=(10.0, 7.0), fontsize=8)

    plotter.draw_lines(lines)
    plotter.draw_vertices(facecolor=vcolor, text=vlabel, radius=0.3)
    plotter.draw_edges(text=elabel)

    plotter.show()
