import os
import json

import compas_rhino as rhino

from compas_ags.cad.rhino.ctrl_forcediagram import ForceDiagramController
from compas_ags.cad.rhino.ctrl_formdiagram import FormDiagramController
from compas_ags.cad.rhino.ctrl_gstatics import GraphicStaticsController
from compas_ags.cad.rhino.ctrl_lpopt import LpOptController

HERE = os.path.dirname(__file__)


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016, Block Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


class Controller(object):

    def __init__(self):
        self.formdiagram = None
        self.forcediagram = None

    def init(self):
        path = os.path.join(HERE, 'config.json')
        with open(path, 'r') as fp:
            config = json.load(fp)
        rhino.create_layers(config['layers'])
        rhino.clear_layers(config['layers'])
        self.ctrl_formdiagram = FormDiagramController(self)
        self.ctrl_forcediagram = ForceDiagramController(self)
        self.ctrl_gstatics = GraphicStaticsController(self)
        self.ctrl_lpopt = LpOptController(self)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    from compas_rhino.ui.rui import Rui
    from compas_rhino.ui.rui import get_macros
    from compas_rhino.ui.rui import update_macro

    with open(os.path.join(HERE, 'config.json'), 'r') as fp:
        config = json.load(fp)

    macros  = get_macros(Controller, 'ags')
    macros += get_macros(FormDiagramController, 'ags.ctrl_formdiagram')
    macros += get_macros(ForceDiagramController, 'ags.ctrl_forcediagram')
    macros += get_macros(GraphicStaticsController, 'ags.ctrl_gstatics')
    macros += get_macros(LpOptController, 'ags.ctrl_lpopt')

    init_script = [
        '-_RunPythonScript ResetEngine (',
        'from compas_ags.cad.rhino.tool import Controller;',
        'ags = Controller();',
        'ags.init();',
        ')'
    ]

    update_macro(macros, 'ags.init', 'script', ''.join(init_script))

    rui = Rui('./ags.rui')

    rui.init()
    rui.add_macros(macros)
    rui.add_menus(config['rui']['menus'])
    rui.add_toolbars(config['rui']['toolbars'])
    rui.add_toolbargroups(config['rui']['toolbargroups'])
    rui.write()
