""""""

import os
import ast

from compas.utilities.maps import geometric_key

import compas_rhino as rhino

from compas_ags.cad.rhino.formdiagram import FormDiagram

try:
    import rhinoscriptsyntax as rs
except ImportError as e:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise e

HERE = os.path.dirname(__file__)


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016, Block Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# todo: update attributes from input geometry names


class FormDiagramController(object):

    def __init__(self, main):
        self.main = main
        self.settings = {}
        self.registry = {}

    def from_lines(self):
        guids = rhino.select_lines()
        lines = rhino.get_line_coordinates(guids)
        if not lines:
            return
        self.main.formdiagram = FormDiagram.from_lines(lines)
        self.main.formdiagram.identify_fixed()
        # self.main.formdiagram.identify_constraints()
        self._update_edge_attr_from_names(guids)
        self.main.formdiagram.draw()

    def _update_edge_attr_from_names(self, guids):
        names = [rs.ObjectName(guid) for guid in guids]
        lines = rhino.get_line_coordinates(guids)
        form = self.main.formdiagram
        key_coords = form.vertex_coordinates
        precision = '3f'
        xyz_key = dict((geometric_key(key_coords(key), precision), key) for key in form)
        for i in range(len(guids)):
            name = names[i]
            if name:
                sp, ep = lines[i]
                u = xyz_key[geometric_key(sp, precision)]
                v = xyz_key[geometric_key(ep, precision)]
                try:
                    attr = ast.literal_eval(name)
                except:
                    continue
                if v in form.edge[u]:
                    form.edge[u][v].update(attr)
                else:
                    form.edge[v][u].update(attr)

    # --------------------------------------------------------------------------
    # update
    # --------------------------------------------------------------------------

    # text => settings
    def update_settings(self):
        names  = sorted(self.settings.keys())
        values = [str(self.settings[name]) for name in names]
        values = rhino.update_named_values(names, values)
        if values:
            for i in range(len(names)):
                name  = names[i]
                value = values[i]
                try:
                    self.settings[name] = ast.literal_eval(value)
                except:
                    self.settings[name] = value
            self.main.formdiagram.draw()

    # text => attributes
    def update_attributes(self):
        if rhino.update_network_attributes(self.main.formdiagram):
            self.main.formdiagram.draw()

    # text => v_attr
    def update_vertex_attributes(self):
        keys = rhino.select_network_vertices(self.main.formdiagram)
        if not keys:
            return
        names = sorted(self.main.formdiagram.default_vertex_attributes.keys())
        if rhino.update_network_vertex_attributes(self.main.formdiagram, keys, names):
            self.main.formdiagram.draw()

    # text => e_attr
    def update_edge_attributes(self):
        keys = rhino.select_network_edges(self.main.formdiagram)
        if not keys:
            return
        names = sorted(self.main.formdiagram.default_edge_attributes.keys())
        if rhino.update_network_edge_attributes(self.main.formdiagram, keys, names):
            self.main.formdiagram.draw()

    # --------------------------------------------------------------------------
    # display
    # --------------------------------------------------------------------------

    # text => v_label
    def display_vertex_labels(self):
        while True:
            options = ['EXIT', 'key', 'index']
            default = options[0]
            option = rs.GetString('Select label', default, options)
            rhino.delete_objects(
                rhino.get_objects(
                    name='{0}.vertex.label.*'.format(self.main.formdiagram.attributes['name'])
                ))
            if option not in options:
                return
            if option == 'EXIT':
                return
            rhino.display_network_vertex_labels(self.main.formdiagram, option)

    # text => e_label
    def display_edge_labels(self):
        while True:
            options = ['EXIT', 'key', 'index']
            default = options[0]
            option = rs.GetString('Select label', default, options)
            rhino.delete_objects(
                rhino.get_objects(
                    name='{0}.edge.label.*'.format(self.main.formdiagram.attributes['name'])
                ))
            if option not in options:
                return
            if option == 'EXIT':
                return
            rhino.display_network_edge_labels(self.main.formdiagram, option)

    # text => f_label
    def display_face_labels(self):
        while True:
            options = ['EXIT', 'key', 'index']
            default = options[0]
            option = rs.GetString('Select label', default, options)
            rhino.delete_objects(
                rhino.get_objects(
                    name='{0}.face.label.*'.format(self.main.formdiagram.attributes['name'])
                ))
            if option not in options:
                return
            if option == 'EXIT':
                return
            rhino.display_network_face_labels(self.main.formdiagram, option)

    # text => forces
    def display_forces(self):
        rhino.display_network_axial_forces(
            self.main.formdiagram,
            layer=self.main.formdiagram.attributes['layer'],
            scale=0.1
        )


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":
    pass
