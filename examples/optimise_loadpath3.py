from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_ags

from compas_ags.ags.loadpath3 import optimise_loadpath3

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram

from compas_ags.viewers import Viewer


__author__     = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__  = 'Copyright 2016, BLOCK Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'liew@arch.ethz.ch'


__all__ = []


# Form and Force diagrams

form = FormDiagram.from_json(compas_ags.get('loadpath/case_1.json'))
form.identify_fixed()
form.update_default_vertex_attributes({'px': 0, 'py': 0, 'pz': 1})
force = ForceDiagram.from_formdiagram(form)

# Optimise differential evolution

fopt, qopt = optimise_loadpath3(form, force, solver='devo', qmax=5, population=20, steps=1000)

# Optimise function and gradient

fopt, qopt = optimise_loadpath3(form, force, solver='slsqp', qid0=qopt, qmax=10, steps=100)

# Form and Force diagrams

viewer = Viewer(form, force)
viewer.setup()
viewer.draw_form(forcescale=10)
# viewer.draw_force()
viewer.show()
