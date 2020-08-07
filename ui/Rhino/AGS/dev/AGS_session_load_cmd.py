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

from compas_ags.utilities import calculate_drawingscale
from compas_ags.utilities import calculate_drawingscale_forces


__commandname__ = "AGS_session_load"


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
            form_id = scene.add(form, name='Form', layer='AGS::FormDiagram')
            form = scene.find(form_id)

            # calculate the scale factor for FormDiagram
            drawingscale_forces = calculate_drawingscale_forces(form.diagram)
            form.artist.settings['scale.forces'] = drawingscale_forces

        scene.clear()
        scene.update()

        if 'force' in data and data['force']:
            force = ForceDiagram.from_data(data['force'])
            force.dual = form.diagram
            force_id = scene.add(force, name='Force', layer='AGS::ForceDiagram')
            force = scene.find(force_id)

            # choose location of ForceDiagram
            force.artist.anchor_vertex = 0
            force.artist.anchor_point = compas_rhino.rs.GetPoint("Set Force Diagram Location")

            # calculate the scale factor for ForceDiagram
            scale_factor = calculate_drawingscale(form.diagram, force.diagram)
            print("scale factor of the ForceDiagram is %s" % scale_factor)
            force.artist.scale = scale_factor

        scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
