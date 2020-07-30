from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import rhinoscriptsyntax as rs

from compas_ags.diagrams import ForceDiagram


__commandname__ = "AGS_force_from_form"

# SHOULD THIS FUNCTION BE IN THE force_update_cmd? 
# check whether the force diagram exists. if it exists, update, otherwise, construct a force diagram fitst. 

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
    from compas_ags.rhino import calculate_scale, calculate_anchor
    scale_factor = calculate_scale(form.diagram, force.diagram)

    print(scale_factor)

    # this should become part of "add"
    force.artist.anchor_vertex = 5
    force.artist.anchor_point = rs.GetPoint("Set Force Diagram Location") 
    #force_obj.artist.anchor_point = calculate_anchor(form, force)
    force.artist.scale = scale_factor

    scene.clear()
    scene.update()
    

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
