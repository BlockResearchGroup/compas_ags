from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino
from compas_ags.diagrams import ForceDiagram
from compas_ags.utilities import calculate_drawingscale_forces


__commandname__ = "AGS_force_from_form"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    proxy = sc.sticky['AGS']['proxy']
    scene = sc.sticky['AGS']['scene']

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return
    form = objects[0]

    proxy.package = 'compas_ags.ags.graphstatics'

    edges = list(form.diagram.edges_where({'is_ind': True}))

    if not len(edges):
        compas_rhino.display_message(
            "You have not yet assigned force values to the form diagram. Please assign forces first.")
        return

    dof = proxy.form_count_dof(form.diagram)
    if dof[0] != len(edges):
        compas_rhino.display_message(
            "You have not assigned the correct number of force values. Please, check the degrees of freedom of the form diagram and update the assigned forces accordingly.")
        return

    forcediagram = ForceDiagram.from_formdiagram(form.diagram)
    force_id = scene.add(forcediagram, name="Force", layer="AGS::ForceDiagram")
    force = scene.find(force_id)

    form.diagram.data = proxy.form_update_q_from_qind_proxy(form.diagram.data)
    force.diagram.data = proxy.force_update_from_form_proxy(force.diagram.data, form.diagram.data)

    form.artist.settings['scale.forces'] = calculate_drawingscale_forces(form.diagram)

    form_xyz = list(form.artist.vertex_xyz.values())
    force_xyz = list(force.artist.vertex_xyz.values())

    form_xmax = max([xyz[0] for xyz in form_xyz])
    force_xmin = min([xyz[0] for xyz in force_xyz])
    force_xmax = max([xyz[0] for xyz in force_xyz])

    spacing = 0.1 * (force_xmax - force_xmin)
    dx = form_xmax + spacing - force_xmin

    if dx:
        point = force.artist.vertex_xyz[force.artist.anchor_vertex]
        point[0] += dx
        force.artist.anchor_point = point

    scene.update()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
