import math as m
import compas_rhino


# create a catenary curve
def catenary_curve(x, type='hanging_cable', a=60, xm=0, ym=0):
    if type == 'arch':
        return ym - a * m.cosh((x - xm) / a)
    elif type == 'hanging_cable':
        return ym + a * m.cosh((x - xm) / a)

# ==============================================================================
# INPUT HOW MANY LOADS TO ADD
# INPUT SPAN LENGTH
# ==============================================================================
loads = 5
span = 100

nodes = []
structure_lines = []
loads_lines = []
reaction_lines = []

# add cable lines
y0 = catenary_curve(- span / 2)

for i in range(loads + 2):
    x = i * span / (loads + 1) - span / 2
    y = catenary_curve(x)
    nodes.append([x, y0, 0])
    if i != 0 and i!= loads + 1:
        nodes.append([x, y, 0])

for i in range(loads + 1):
    if i == 0: 
        structure_lines.append({
                'start': nodes[i],
                'end':  nodes[i + 1], 
            })
        structure_lines.append({
                'start': nodes[i],
                'end':  nodes[i + 2], 
            })
    else:
        structure_lines.append({
            'start': nodes[i * 2 - 1],
            'end':  nodes[i * 2 + 1], 
        })
        structure_lines.append({
            'start': nodes[i * 2 - 1],
            'end':  nodes[i * 2], 
        })
        if i == loads:
            structure_lines.append({
                'start': nodes[i * 2],
                'end':  nodes[i * 2 + 1], 
            })
        else:
            structure_lines.append({
                'start': nodes[i * 2],
                'end':  nodes[i * 2 + 2], 
            })
        
# add vertical load lines and rection force lines
for i in range(loads + 2):
    x = i * span / (loads + 1) - span / 2
    if i == 0:
        nodes.append([x, y0 - 10, 0])
        reaction_lines.append({
            'start': nodes[i],
            'end':  nodes[len(nodes) - 1], 
            })
    elif i == loads + 1:
        nodes.append([x, y0 - 10, 0])
        reaction_lines.append({
            'start': nodes[i * 2 - 1],
            'end':  nodes[len(nodes) - 1], 
            })
    else:
        nodes.append([x, y0 + 10, 0])
        loads_lines.append({
            'start': nodes[i * 2 - 1],
            'end':  nodes[len(nodes) - 1], 
            })

# add horizontal rection force lines
nodes.append([-span / 2 - 10, y0, 0])
reaction_lines.append({
                'start': nodes[0],
                'end':  nodes[len(nodes) - 1], 
            })
nodes.append([span / 2 + 10, y0, 0])
reaction_lines.append({
                'start': nodes[2 * loads + 1],
                'end':  nodes[len(nodes) - 1], 
            })


compas_rhino.draw_lines(structure_lines, layer='structure', clear=False, redraw=True)
compas_rhino.draw_lines(loads_lines, layer='loads', clear=False, redraw=True)
compas_rhino.draw_lines(reaction_lines, layer='reaction', clear=False, redraw=True)

