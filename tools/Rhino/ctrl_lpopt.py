import os
import ast

from compas_rhino.utilities import ScriptServer
from compas_rhino.utilities import XFunc

import compas_rhino as rhino

try:
    import rhinoscriptsyntax as rs
except ImportError as e:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise e

here = os.path.dirname(__file__)

scriptdir = os.path.join(here, '../../_xscripts')
tempdir = os.path.join(here, '../../_temp')
basedir = os.path.join(here, '../..')

SERVER = ScriptServer(scriptdir, tempdir)
XFUNC = XFunc(basedir, tempdir, mode=1)


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016, Block Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


class LpOptController(object):

    def __init__(self, main):
        self.main = main
        self.settings = {}
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


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":
    pass
