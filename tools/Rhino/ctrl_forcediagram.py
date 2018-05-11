import ast
import os

import compas_rhino as rhino

from compas_ags.cad.rhino.forcediagram import ForceDiagram

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


class ForceDiagramController(object):

    def __init__(self, main):
        self.main = main
        self.settings = {}
        self.registry = {}

    def from_formdiagram(self):
        self.main.forcediagram = ForceDiagram.from_formdiagram(self.main.formdiagram)
        self.main.forcediagram.draw()

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
            self.main.forcediagram.draw()

    # text => attributes
    def update_attributes(self):
        if rhino.update_network_attributes(self.main.forcediagram):
            self.main.forcediagram.draw()

    # text => v_attr
    def update_vertex_attributes(self):
        keys = rhino.select_network_vertices(self.main.forcediagram)
        if not keys:
            return
        names = sorted(self.main.forcediagram.default_vertex_attributes.keys())
        if rhino.update_network_vertex_attributes(self.main.forcediagram, keys, names):
            self.main.forcediagram.draw()

    # text => e_attr
    def update_edge_attributes(self):
        keys = rhino.select_network_edges(self.main.forcediagram)
        if not keys:
            return
        names = sorted(self.main.forcediagram.default_edge_attributes.keys())
        if rhino.update_network_edge_attributes(self.main.forcediagram, keys, names):
            self.main.forcediagram.draw()

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
                    name='{0}.vertex.label.*'.format(self.main.forcediagram.attributes['name'])
                ))
            if option not in options:
                return
            if option == 'EXIT':
                return
            rhino.display_network_vertex_labels(self.main.forcediagram, option)

    # text => e_label
    def display_edge_labels(self):
        while True:
            options = ['EXIT', 'key', 'index']
            default = options[0]
            option = rs.GetString('Select label', default, options)
            rhino.delete_objects(
                rhino.get_objects(
                    name='{0}.edge.label.*'.format(self.main.forcediagram.attributes['name'])
                ))
            if option not in options:
                return
            if option == 'EXIT':
                return
            rhino.display_network_edge_labels(self.main.forcediagram, option)

    # --------------------------------------------------------------------------
    # move
    # --------------------------------------------------------------------------

    def move_diagram(self):
        rhino.move_network(self.main.forcediagram)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":
    pass
