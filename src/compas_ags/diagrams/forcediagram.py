from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Network
from compas.topology import network_find_faces
from compas.topology import network_dual


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'ForceDiagram'
]


class ForceDiagram(Network):
    """"""

    def __init__(self):
        super(ForceDiagram, self).__init__()
        self.attributes.update({
            'name'         : 'ForceDiagram',
            'color.vertex' : (255, 255, 255),
            'color.edge'   : (200, 200, 200),
            'color.face'   : (0, 255, 255),
        })
        self.update_default_vertex_attributes({
            'is_fixed'  : False,
            'is_anchor' : False,
            'is_param'  : False,
        })
        self.update_default_edge_attributes({
            'l'   : 0.0,
            'lmin': 1e-7,
            'lmax': 1e+7,
        })

    # --------------------------------------------------------------------------
    # Constructors
    # --------------------------------------------------------------------------

    @classmethod
    def from_formdiagram(cls, formdiagram):
        network_find_faces(formdiagram, formdiagram.leaves())
        return network_dual(formdiagram, cls)

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving attributes of the force diagram.
    # --------------------------------------------------------------------------

    def xy(self):
        return [self.vertex_coordinates(key, 'xy') for key in self.vertices()]

    def fixed(self):
        return [key for key, attr in self.vertices(True) if attr['is_fixed']]

    def anchor(self):
        for key, attr in self.vertices(True):
            if attr['is_anchor']:
                return key
        return key

    def set_fixed(self, keys):
        for key, attr in self.vertices(True):
            attr['is_fixed'] = key in keys

    def set_anchor(self, keys):
        for key, attr in self.vertices(True):
            attr['is_fixed'] = key in keys

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    def uv_index(self, form=None):
        if not form:
            return {(u, v): index for index, (u, v) in enumerate(self.edges())}
        uv_index = dict()
        for index, (u, v) in enumerate(form.edges()):
            f1 = form.halfedge[u][v]
            f2 = form.halfedge[v][u]
            uv_index[(f1, f2)] = index
        return uv_index

    def ordered_edges(self, form, index=True):
        key_index = self.key_index()
        uv_index  = self.uv_index(form=form)
        index_uv  = dict((i, uv) for uv, i in uv_index.items())
        edges     = [index_uv[i] for i in range(self.number_of_edges())]
        if not index:
            return edges
        return [[key_index[u], key_index[v]] for u, v in edges]

    # --------------------------------------------------------------------------
    # AGS functions
    # --------------------------------------------------------------------------

    def update(self, formdiagram):
        from compas_ags.algorithms.graphstatics import update_forcediagram
        update_forcediagram(self, formdiagram)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':

    import compas_ags

    from compas_ags.ags import update_forcediagram
    from compas_ags.ags import update_forcedensity
    from compas_ags.diagrams import FormDiagram
    from compas_ags.viewers import Viewer

    form = FormDiagram.from_obj(compas_ags.get('paper/gs_form_force.obj'))

    form.identify_fixed()

    force = ForceDiagram.from_formdiagram(form)

    form.set_edge_force_by_index(0, 3)

    update_forcedensity(form)
    update_forcediagram(force, form)

    viewer = Viewer(form, force, delay_setup=False)

    viewer.draw_form(forcescale=5.0)
    viewer.draw_force()

    viewer.show()
