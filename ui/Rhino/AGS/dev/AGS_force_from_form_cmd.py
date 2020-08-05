from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

from compas_ags.utilities import calculate_drawing_scale
from compas_ags.utilities import calculate_force_scale

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

    proxy.package = 'compas_ags.ags.graphstatics'

    forcediagram = ForceDiagram.from_formdiagram(form.diagram)
    force_id = scene.add(forcediagram, name="Force", layer="AGS::ForceDiagram")
    force = scene.find(force_id)

    form.diagram.data = proxy.form_update_q_from_qind_proxy(form.diagram.data)
    force.diagram.data = proxy.force_update_from_form_proxy(force.diagram.data, form.diagram.data)

    # calculate the scale factor for force diagram
    scale_factor = calculate_drawing_scale(form.diagram, force.diagram)
    scale_pipes = calculate_force_scale(form.diagram)

    print("scale factor of the ForceDiagram is %s" % scale_factor)

    # this should become part of "add"
    force.artist.anchor_vertex = 0
    force.artist.anchor_point = compas_rhino.rs.GetPoint("Set Force Diagram Location")
    force.artist.scale = scale_factor
    form.artist.settings['scale.forces'] = scale_pipes

    scene.clear()
    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
