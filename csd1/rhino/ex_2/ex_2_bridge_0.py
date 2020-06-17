import math as m
import compas_rhino


# create a catenary curve
def catenary_curve(x, type='arch', a=60, xm=0, ym=0):
    if type == 'arch':
        return ym - a * m.cosh((x - xm) / a)
    elif type == 'hanging_cable':
        return ym + a * m.cosh((x - xm) / a)

# ==============================================================================
# INPUT HOW MANY LOADS TO ADD
# INPUT SPAN LENGTH
# INPUT THE INITIAL TYPE OF CATENARY CURVE
# ==============================================================================
loads = 5
length = 100
type = 'arch'
# type = 'hanging_cable'

nodes = []
structure_lines = []
loads_lines = []
reaction_lines = []

# add cable lines
for i in range(loads + 2):
    x = i * length / (loads + 1) - length / 2
    y = catenary_curve(x, type=type)
    nodes.append([x, y, 0])
    if i != 0:
        structure_lines.append({
                'start': nodes[i-1],
                'end':  nodes[i], 
            })
        
# add vertical load lines and rection force lines
for i in range(loads + 2):
    if i == 0 or i == loads + 1:
        x = i * length / (loads + 1) - length / 2
        y = catenary_curve(x, type=type) - 10
        nodes.append([x, y, 0])
        reaction_lines.append({
                'start': nodes[i],
                'end':  nodes[i + loads + 2], 
            })
    else:
        x = i * length / (loads + 1) - length / 2
        y = catenary_curve(x, type=type) + 10
        nodes.append(([x, y, 0]))
        loads_lines.append({
                'start': nodes[i],
                'end':  nodes[i + loads + 2], 
            })

# add horizontal rection force lines
nodes.append([- length / 2 - 10, catenary_curve(-length / 2, type=type), 0])
reaction_lines.append({
                'start': nodes[0],
                'end':  nodes[len(nodes) - 1], 
            })
nodes.append([length / 2 + 10, catenary_curve(length / 2, type=type), 0])
reaction_lines.append({
                'start': nodes[loads + 1],
                'end':  nodes[len(nodes) - 1], 
            })

compas_rhino.draw_lines(structure_lines, layer='structure', clear=False, redraw=False)
compas_rhino.draw_lines(loads_lines, layer='loads', clear=False, redraw=False)
compas_rhino.draw_lines(reaction_lines, layer='reaction', clear=False, redraw=False)

