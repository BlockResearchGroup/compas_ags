from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


from math import fabs

import compas_rhino
from compas.geometry import scale_vector
from compas.utilities import i_to_green

from compas_rhino.artists import MeshArtist


__all__ = ['FormArtist']


class FormArtist(MeshArtist):

    __module__ = 'compas_tna.rhino'

    def __init__(self, form, layer=None):
        super(FormArtist, self).__init__(form, layer=layer)
        self.settings.update({
            'color.vertex': (255, 255, 255),
            'color.edge': (0, 0, 0),
            'color.leaves': (0, 255, 0), 
            'color.face': (210, 210, 210),
            'color.reaction': (0, 255, 0),
            'color.residual': (0, 255, 255),
            'color.load': (0, 255, 0),
            'color.selfweight': (0, 0, 255),
            'color.force': (0, 0, 255),
            'color.compression': (0, 0, 255),
            'color.tension': (255, 0, 0),
            'color.fix':(255, 0, 0), 
            'scale.reaction': 1.0,
            'scale.residual': 1.0,
            'scale.load': 1.0,
            'scale.force': 1.0,
            'scale.selfweight': 1.0,
            'tol.reaction': 1e-3,
            'tol.residual': 1e-3,
            'tol.load': 1e-3,
            'tol.force': 1e-3,
            'tol.selfweight': 1e-3,
        })

    @property
    def form(self):
        return self.mesh


    def draw_diagram(self):
        self.clear()
        self.draw_vertices()
        self.draw_vertexlabels()
        self.draw_edges()
        self.draw_edgelabels(text={uv: index for index, uv in enumerate(self.form.edges())})
        self.redraw()


    def clear_leaves(self):
        compas_rhino.delete_objects_by_name(name='{}.leaf_edge.*'.format(self.form.name))


    def draw_leaves(self, color=None, arrows=False):
        # draw leaves 
        # arrows direction arbitary
        self.clear_leaves()
        leaves  = set(self.form.leaves())
        print('leaves', leaves)
        lines = []
        for index, ((u, v), attr) in enumerate(self.form.edges_where({'is_edge': True}, True)):
            print(index, u, v)
            if u in leaves or v in leaves:
                print(u, v, 'hey im passing here')
                lines.append({
                    'start': self.form.vertex_coordinates(u),
                    'end': self.form.vertex_coordinates(v),
                    'arrow': 'end' if arrows is True else None,
                    'color': color or self.settings.get('color.leaves'), 
                    'name': "{}.leaf_edge.{}".format(self.form.name, index),
                    'width': 0.5
                })
        compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)
    

    def clear_independent_edge(self):
        compas_rhino.delete_objects_by_name(name='{}.independent_edge.*'.format(self.form.name))


    def draw_independent_edge(self):
        self.clear_independent_edge()
        lines = []
        for index, ((u, v), attr) in enumerate(self.form.edges_where({'is_edge': True}, True)):
            if attr['is_ind']:
                lines.append({
                    'start': self.form.vertex_coordinates(u),
                    'end': self.form.vertex_coordinates(v),
                    'name': "{}.independent_edge.{}".format(self.form.name, index),
                    'width': 1.0
                })
        compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def clear_fixed_vertice(self):
        compas_rhino.delete_objects_by_name(name='{}.fixed_vertex.*'.format(self.form.name))


    def draw_fixed_vertice(self, color=None):
        self.clear_fixed_vertice()
        fixed = self.form.fixed()
        self.clear_vertexlabels(keys=fixed)
        labels = []
        for vkey in fixed:
            labels.append({
                'pos'  : self.form.vertex_coordinates(vkey),
                'text' : str(vkey),
                'color': color or self.settings.get('color.fix'),
                'name' : "{}.fixed_vertex.{}".format(self.form.name, vkey)
            })
        compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)


    def clear(self):
        super(FormArtist, self).clear()
        self.clear_loads()
        self.clear_selfweight()
        self.clear_reactions()
        self.clear_forces()
        self.clear_residuals()
        self.clear_angles()


    def clear_loads(self):
        compas_rhino.delete_objects_by_name(name='{}.load.*'.format(self.form.name))


    def clear_selfweight(self):
        compas_rhino.delete_objects_by_name(name='{}.selfweight.*'.format(self.form.name))


    def clear_reactions(self):
        compas_rhino.delete_objects_by_name(name='{}.reaction.*'.format(self.form.name))


    def clear_forces(self):
        compas_rhino.delete_objects_by_name(name='{}.force.*'.format(self.form.name))


    def clear_residuals(self):
        compas_rhino.delete_objects_by_name(name='{}.residual.*'.format(self.form.name))


    def clear_angles(self):
        compas_rhino.delete_objects_by_name(name='{}.angle.*'.format(self.form.name))


    def draw_loads(self, scale=None, color=None):
        self.clear_loads()

        lines = []
        color = color or self.settings['color.load']
        scale = scale or self.settings['scale.load']
        tol = self.settings['tol.load']
        tol2 = tol ** 2

        for key, attr in self.form.vertices_where({'is_anchor': False, '_is_external': False}, True):
            px = scale * attr['px']
            py = scale * attr['py']
            pz = scale * attr['pz']

            if px ** 2 + py ** 2 + pz ** 2 < tol2:
                continue

            sp = self.form.vertex_coordinates(key)
            ep = sp[0] + px, sp[1] + py, sp[2] + pz

            lines.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'end',
                'name': "{}.load.{}".format(self.form.name, key)
            })

        compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)


    def draw_selfweight(self, scale=None, color=None):
        self.clear_selfweight()

        lines = []
        color = color or self.settings['color.selfweight']
        scale = scale or self.settings['scale.selfweight']
        tol = self.settings['tol.selfweight']
        tol2 = tol ** 2

        for key, attr in self.form.vertices_where({'is_anchor': False, '_is_external': False}, True):
            t = attr['t']
            a = self.form.vertex_area(key)
            sp = self.form.vertex_coordinates(key)

            dz = scale * t * a

            if dz ** 2 < tol2:
                continue

            ep = sp[0], sp[1], sp[2] - dz

            lines.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'end',
                'name': "{}.selfweight.{}".format(self.form.name, key)
            })

        compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)


    def draw_reactions(self, scale=None, color=None):
        self.clear_reactions()

        lines = []
        color = color or self.settings['color.reaction']
        scale = scale or self.settings['scale.reaction']
        tol = self.settings['tol.reaction']
        tol2 = tol ** 2

        for key, attr in self.form.vertices_where({'is_anchor': True}, True):
            rx = attr['_rx']
            ry = attr['_ry']
            rz = attr['_rz']

            for nbr in self.form.vertex_neighbors(key):
                is_external = self.form.edge_attribute((key, nbr), '_is_external')

                if is_external:
                    f = self.form.edge_attribute((key, nbr), '_f')
                    u = self.form.edge_direction(key, nbr)
                    u[2] = 0
                    v = scale_vector(u, f)

                    rx += v[0]
                    ry += v[1]

            rx = scale * rx
            ry = scale * ry
            rz = scale * rz

            sp = self.form.vertex_coordinates(key)

            if rx ** 2 + ry ** 2 > tol2:
                e1 = sp[0] + rx, sp[1] + ry, sp[2]
                lines.append({
                    'start': sp,
                    'end': e1,
                    'color': color,
                    'arrow': 'start',
                    'name': "{}.reaction.{}".format(self.form.name, key)
                })

            if rz ** 2 > tol2:
                e2 = sp[0], sp[1], sp[2] + rz
                lines.append({
                    'start': sp,
                    'end': e2,
                    'color': color,
                    'arrow': 'start',
                    'name': "{}.reaction.{}".format(self.form.name, key)
                })

        compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_forces(self, scale=None, color=None):
        self.clear_forces()

        lines = []
        color = color or self.settings['color.compression']
        scale = scale or self.settings['scale.force']
        tol = self.settings['tol.force']
        tol2 = tol ** 2
        leaves  = set(self.form.leaves())

        for (u, v), attr in self.form.edges_where({'is_edge': True}, True):
            if u not in leaves and v not in leaves:
                sp, ep = self.form.edge_coordinates(u, v)
                f = attr['f']

                if f != 0:
                    radius = abs(scale * f)
                else:
                    f = self.form.edge_attribute((v, u), 'f')
                    radius = abs(scale * f)

                if radius ** 2 < tol2:
                    continue

                lines.append({
                    'start': sp,
                    'end': ep,
                    'radius': radius,
                    'color': color if f > 0 else self.settings['color.tension'],
                    'name': "{}.force.{}-{}".format(self.form.name, u, v)
                })
        compas_rhino.draw_cylinders(lines, layer=self.layer, clear=False, redraw=True)


    def draw_residuals(self, scale=None, color=None):
        self.clear_residuals()

        lines = []
        color = color or self.settings['color.residual']
        scale = scale or self.settings['scale.residual']
        tol = self.settings['tol.residual']
        tol2 = tol ** 2

        for key, attr in self.form.vertices_where({'is_anchor': False, '_is_external': False}, True):
            rx = scale * attr['_rx']
            ry = scale * attr['_ry']
            rz = scale * attr['_rz']

            if rx ** 2 + ry ** 2 + rz ** 2 < tol2:
                continue

            sp = self.form.vertex_coordinates(key)
            ep = sp[0] + rx, sp[1] + ry, sp[2] + rz

            lines.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'start',
                'name': "{}.residual.{}".format(self.form.name, key)
            })

        compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_angles(self, tol=5.0):
        self.clear_angles()

        a = self.form.edges_attribute('_a')
        a_max = tol
        a_min = 0
        a_range = a_max - a_min

        if a_range:
            labels = []
            for u, v, attr in self.form.edges(True):
                a = 180 * attr['_a'] / 3.14159
                if a > tol:
                    labels.append({
                        'pos': self.form.edge_midpoint(u, v),
                        'text': "{:.2f}".format(attr['a'] / 3.14159 * 180),
                        'color': i_to_green((attr['a'] - a_min) / a_range),
                        'name': "{}.angle.{}-{}".format(self.form.name, u, v)
                    })

            compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)

# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":
    pass
