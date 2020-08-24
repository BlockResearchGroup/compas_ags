from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

# from compas_ags.utilities import calculate_drawingscale
from compas_ags.utilities import calculate_drawingscale_forces

import compas_rhino

from compas_ags.diagrams import ForceDiagram


__commandname__ = "AGS_force_from_form"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    proxy = sc.sticky['AGS']['proxy']
    scene = sc.sticky['AGS']['scene']
    form = scene.find_by_name('Form')[0]

    if not form:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    proxy.package = 'compas_ags.ags.graphstatics'

    forcediagram = ForceDiagram.from_formdiagram(form.diagram)
    force_id = scene.add(forcediagram, name="Force", layer="AGS::ForceDiagram")
    force = scene.find(force_id)

    form.diagram.data = proxy.form_update_q_from_qind_proxy(form.diagram.data)
    force.diagram.data = proxy.force_update_from_form_proxy(force.diagram.data, form.diagram.data)

    scene.update()

    # calculate the scale factor for force diagram
    # force.artist.scale = calculate_drawingscale(form.diagram, force.diagram)
    form.artist.settings['scale.forces'] = calculate_drawingscale_forces(form.diagram)

    force.artist.scale = 1.0
    # force.artist.anchor_vertex = next(force.diagram.vertices())
    # force.artist.anchor_point = force.diagram.vertex_attributes(force.artist.anchor_vertex, 'xyz')

    if force.move():
        scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
