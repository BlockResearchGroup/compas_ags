from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import scriptcontext as sc

import compas_rhino
from compas.utilities import DataDecoder

from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram


__commandname__ = "AGS_open"


def RunCommand(is_interactive):
    
    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    system = sc.sticky['AGS']['system']
    scene = sc.sticky['AGS']['scene']

    filepath = compas_rhino.select_file(folder=system['session.dirname'], filter=system['session.extension'])

    if not filepath:
        return 
    if not os.path.exists(filepath):
        return 
    if not os.path.isfile(filepath):
        return 
    if not filepath.endswith(".{}".format(system['session.extension'])):
        return 
    
    dirname, basename = os.path.split(filepath)
    filename, extension = os.path.splitext(basename)

    system['session.dirname'] = dirname
    system['session.filename'] = filename

    with open(filepath, "r") as f:
        session = json.load(f, cls=DataDecoder)

    if 'data' in session:
        data = session['data']

        if 'form' in data and data['form']:
            form = FormDiagram.from_data(data['form'])
            scene.add(form, name='Form', layer='AGS::FormDiagram')

        if 'force' in data and data['force']:
            force = ForceDiagram.from_data(data['force'])
            force.dual = form
            scene.add(force, name='Forcd', layer='AGS::FormDiagram')

        
    scene.clear()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)