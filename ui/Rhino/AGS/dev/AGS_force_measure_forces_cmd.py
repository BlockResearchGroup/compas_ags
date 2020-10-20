from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc

import compas_rhino


__commandname__ = "AGS_force_measure_forces"


def RunCommand(is_interactive):

    if 'AGS' not in sc.sticky:
        compas_rhino.display_message('AGS has not been initialised yet.')
        return

    scene = sc.sticky['AGS']['scene']

    objects = scene.find_by_name('Form')
    if not objects:
        compas_rhino.display_message("There is no FormDiagram in the scene.")
        return

    objects = scene.find_by_name('Force')
    if not objects:
        compas_rhino.display_message("There is no ForceDiagram in the scene.")
        return
    force = objects[0]

    scale = force.scale
    force.settings['show.edges'] = True
    force.settings['show.forcelabels'] = False
    force.settings['show.edgelabels'] = False
    scene.update()

    while True:
        edge = force.select_edge()
        if not edge:
            break

        edge_index = force.diagram.edge_index(force.diagram.dual)
        edge_index.update({(v, u): index for (u, v), index in edge_index.items()})
        index = edge_index[edge]

        f = force.diagram.dual_edge_f(edge)
        l = f * scale

        text = {edge: "{:.4g}kN".format(abs(f))}
        color = {}
        tol = force.settings['tol.forces']

        if edge in force.diagram.edges_where_dual({'is_external': True}):
            color[edge] = force.settings['color.edges:is_external']
        if edge in force.diagram.edges_where_dual({'is_load': True}):
            color[edge] = force.settings['color.edges:is_load']
        if edge in force.diagram.edges_where_dual({'is_reaction': True}):
            color[edge] = force.settings['color.edges:is_reaction']
        if edge in force.diagram.edges_where_dual({'is_ind': True}):
            color[edge] = force.settings['color.edges:is_ind']

        if edge in force.diagram.edges_where_dual({'is_external': False}):
            if f > + tol:
                color[edge] = force.settings['color.tension']
            elif f < - tol:
                color[edge] = force.settings['color.compression']

        guid_edgelabel = force.artist.draw_edgelabels(text=text, color=color)
        force.guid_edgelabel = zip(guid_edgelabel, edge)
        force.redraw()

        compas_rhino.display_message("Edge Index: {0}\nForce Diagram Edge Length: {1:.3g}\nForce Drawing Scale: {2:.3g}\nForce Magnitude: {3:.3g}kN".format(index, l, scale, f))

        answer = compas_rhino.rs.GetString("Continue selecting edges?", "No", ["Yes", "No"])
        if not answer:
            break
        if answer == "No":
            break
        if answer == "Yes":
            scene.update()

    scene.update()
    scene.save()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
