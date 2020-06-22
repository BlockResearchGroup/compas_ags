from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.utilities import geometric_key_xy
from compas.datastructures import network_find_cycles
from compas_ags.diagrams import Diagram


__author__ = ['Tom Van Mele']
__email__ = 'vanmelet@ethz.ch'


__all__ = ['FormDiagram',
           ]


class FormDiagram(Diagram):
    """"""

    def __init__(self):
        super(FormDiagram, self).__init__()
        self.attributes.update({
            'name': 'FormDiagram',
            'color.vertex': (255, 255, 255),
            'color.edge': (0, 0, 0),
            'color.face': (0, 255, 255),
            'color.vertex:is_fixed': (255, 0, 0),
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
            'is_edge': True,
            'is_external': False
        })

    @classmethod
    def from_graph(cls, graph):
        points = graph.to_points()
        cycles = network_find_cycles(graph, breakpoints=graph.leaves())
        # print(cycles)
        form = cls.from_vertices_and_faces(points, cycles)
        form.edges_attribute('is_edge', False, keys=list(form.edges_on_boundary()))
        return form

    # --------------------------------------------------------------------------
    # Topology
    # --------------------------------------------------------------------------

    def edges(self, data=False):
        seen = set()
        for u in self.halfedge:
            for v in self.halfedge[u]:
                if (u, v) in seen or (v, u) in seen:
                    continue
                seen.add((u, v))
                seen.add((v, u))
                if not self.edge_attribute((u, v), 'is_edge'):
                    continue
                if not data:
                    yield u, v
                else:
                    yield (u, v), self.edge_attributes((u, v))

    def leaves(self):
        keys = []
        for key in self.vertices():
            edges = 0
            nbrs = self.vertex_neighbors(key)
            for nbr in nbrs:
                if self.edge_attribute((key, nbr), 'is_edge'):
                    edges += 1
            if edges == 1:
                keys.append(key)
        return keys

    def breakpoints(self):
        return list(set(self.leaves() + self.fixed()))

    def number_of_edges(self):
        return len(list(self.edges()))

    def face_adjacency_edge(self, f1, f2):
        edges = list(self.edges())
        for u, v in self.face_halfedges(f1):
            if self.halfedge[v][u] == f2:
                if (u, v) in edges:
                    return u, v
                return v, u

    def uv_index(self):
        return {key: index for index, key in enumerate(self.edges())}


    def index_uv(self):
        return {index: key for index, key in enumerate(self.edges())}

 
    def external_edges(self):
        external_edges = []
        leaves = self.leaves()
        for i, (u, v) in enumerate(self.edges()):
            if u in leaves or v in leaves:
                external_edges.append((u, v))
                self.edge_attribute((u, v), 'is_external', True)
        return external_edges


    # --------------------------------------------------------------------------
    # Convenience functions for retrieving the attributes of the formdiagram.
    # --------------------------------------------------------------------------

    def q(self):
        return [attr['q'] for key, attr in self.edges(True)]

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
        return [key for key, attr in self.edges(True) if attr['is_ind']]

    # --------------------------------------------------------------------------
    # Set stuff
    # --------------------------------------------------------------------------

    def set_fixed(self, keys):
        for key, attr in self.vertices(True):
            attr['is_fixed'] = key in keys

    def set_edge_force(self, u, v, force):
        l = self.edge_length(u, v)
        self.edge_attribute((u, v), 'is_ind', True)
        self.edge_attribute((u, v), 'q', force / l)

    def set_edge_forcedensity(self, u, v, q):
        self.edge_attribute((u, v), 'is_ind', True)
        self.edge_attribute((u, v), 'q', q)

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
                gkey = geometric_key_xy(self.vertex_coordinates(key, 'xy'))
                xy_key[gkey] = key
            for xy in points:
                gkey = geometric_key_xy(xy)
                if gkey in xy_key:
                    key = xy_key[gkey]
                    self.vertex[key]['is_fixed'] = True

    def identify_constraints(self, points=None):
        if points:
            xy_key = {}
            for key in self.vertices():
                gkey = geometric_key_xy(self.vertex_coordinates(key, 'xy'))
                xy_key[gkey] = key
            for xy in points:
                gkey = geometric_key_xy(xy)
                if gkey in xy_key:
                    key = xy_key[gkey]
                    self.vertex[key]['cx'] = 1.0
                    self.vertex[key]['cy'] = 1.0


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    import compas_ags

    from compas_plotters import NetworkPlotter

    form = FormDiagram.from_obj(compas_ags.get('paper/fink.obj'))

    lines = []
    for u, v in form.edges():
        lines.append({
            'start': form.vertex_coordinates(u),
            'end': form.vertex_coordinates(v),
            'color': '#cccccc',
            'width': 0.5,
        })

    form.identify_fixed()

    vcolor = {key: '#ff0000' for key in form.fixed()}
    vlabel = {key: key for key in form.vertices()}
    elabel = {key: str(index) for index, key in enumerate(form.edges())}

    plotter = NetworkPlotter(form, figsize=(10.0, 7.0), fontsize=8)

    plotter.draw_lines(lines)
    plotter.draw_vertices(facecolor=vcolor, text=vlabel, radius=0.3)
    plotter.draw_edges(text=elabel)

    plotter.show()
