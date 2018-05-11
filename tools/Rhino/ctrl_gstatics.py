import os
import ast

from compas_rhino.utilities import XFunc

import compas_rhino as rhino

try:
    import rhinoscriptsyntax as rs
except ImportError as e:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise e

here = os.path.dirname(__file__)

tempdir = os.path.join(here, '../../_temp')
basedir = os.path.join(here, '../..')

XFUNC = XFunc(basedir, tempdir, mode=1)


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016, Block Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


class GraphicStaticsController(object):

    def __init__(self, main):
        self.main = main
        self.settings = {
            'autoupdate:form': False,
            'autoupdate:force': False,
        }
        self.registry = {}

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

    # --------------------------------------------------------------------------
    # ags stuff
    # --------------------------------------------------------------------------

    def identify_dof(self):
        pass

    def count_dof(self):
        pass

    # --------------------------------------------------------------------------
    # update diagrams
    # --------------------------------------------------------------------------

    def update_forcedensity(self):
        """Update the dependent force densities.

        Run this after changing the force densities of the independent edges.
        Or after after choosing different independent edges.
        """
        XFUNC('compas_ags.ags.graphstatics.update_forcedensity_xfunc',
              self.main.formdiagram.to_data())

        if not XFUNC.error:
            self.main.formdiagram.data = XFUNC.data
            self.main.formdiagram.draw()
        else:
            print XFUNC.error

    def update_forcediagram(self):
        """Update the force diagram using the geometry of the form and the
        current force densities.

        Run this after changing the geometry of the form diagram.
        Or after updating the force densities.
        """
        XFUNC('compas_ags.ags.graphstatics.update_forcediagram_xfunc',
              self.main.forcediagram.to_data(),
              self.main.formdiagram.to_data())
        if not XFUNC.error:
            self.main.forcediagram.data = XFUNC.data
            self.main.forcediagram.draw()
        else:
            print XFUNC.error

    def update_formdiagram(self):
        """Update the form diagram using the geometry of the force diagram.

        Run this after changing the geometry of the force diagram.
        """
        XFUNC('compas_ags.ags.graphstatics.update_formdiagram_xfunc',
              self.main.formdiagram.to_data(),
              self.main.forcediagram.to_data())
        if not XFUNC.error:
            self.main.formdiagram.data = XFUNC.data
            self.main.formdiagram.draw()
        else:
            print XFUNC.error

    def modify_formdiagram(self):
        """Modify the form diagram.

        Use this function to change the geometry of the form diagram.
        Optionally, auto-update the force diagram.
        """
        key = rhino.select_network_vertex(self.main.formdiagram)
        if not key:
            return
        rhino.move_network_vertex(self.main.formdiagram, key)
        if self.settings['autoupdate:force']:
            self.update_forcediagram()

    def modify_forcediagram(self):
        """Modify the force diagram.

        Use this function to change the geometry of the force diagram.
        Optinally, auto-update the form diagram.
        """
        key = rhino.select_network_vertex(self.main.forcediagram)
        if not key:
            return
        rhino.move_network_vertex(self.main.forcediagram, key)
        if self.settings['autoupdate:form']:
            self.update_formdiagram()


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":
    pass
