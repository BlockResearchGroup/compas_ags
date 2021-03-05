import compas_ags
from compas_ags.ags import parallelise_edges
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import ForceDiagram
from compas_ags.viewers import Viewer
from compas_ags.ags import form_update_from_force
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.ags import ConstraintsCollection
from compas_ags.ags import form_update_from_force_newton
from compas_ags.ags import form_update_from_force

# ------------------------------------------------------------------------------
#   1. create a simple arch from nodes and edges, make form and force diagrams
# ------------------------------------------------------------------------------

graph = FormGraph.from_obj(compas_ags.get('paper/gs_truss.obj'))
form = FormDiagram.from_graph(graph)
force = ForceDiagram.from_formdiagram(form)

# ------------------------------------------------------------------------------
#   2. prescribe edge force density and set fixed vertices
# ------------------------------------------------------------------------------
# prescribe force density to edge
edges_ind = [
    (6, 14),
]
for index in edges_ind:
    u, v = index
    form.edge_attribute((u, v), 'is_ind', True)
    form.edge_attribute((u, v), 'q', + 1.0)

# set the fixed corners
left = 5
right = 1
fixed = [left, right]

for key in fixed:
    form.vertex_attribute(key, 'is_fixed', True)

# set the horizontal fix in internal nodes:
internal = [0, 2, 3, 4]  # TOP CHORD
internal = [6, 7, 9, 8]  # BOTTOM CHORD

for key in internal:
    form.vertex_attribute(key, 'fix_x', True)

# update the diagrams
form_update_q_from_qind(form)
force_update_from_form(force, form)

# store lines representing the current state of equilibrium
form_lines = []
for u, v in form.edges():
    form_lines.append({
        'start': form.vertex_coordinates(u, 'xy'),
        'end': form.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

force_lines = []
for u, v in force.edges():
    force_lines.append({
        'start': force.vertex_coordinates(u, 'xy'),
        'end': force.vertex_coordinates(v, 'xy'),
        'width': 1.0,
        'color': '#cccccc',
        'style': '--'
    })

# from compas_ags.ags import form_count_dof
# dof = form_count_dof(form)
# k = dof[0]
# print('Required Independents:', k)

# print(form.number_of_edges())
# print(form.number_of_vertices())

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
viewer.draw_force(vertexlabel={key: key for key in force.vertices()}, edgelabel={(u, v): (u, v) for u, v in force.edges() if (u, v) != (8, 3) and (u, v) != (9, 4)})
viewer.show()

lengths_uv = {}
for u, v in force.edges():
    lengths_uv[(u, v)] = force.edge_length(u, v)

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
viewer.draw_force(vertexlabel={key: key for key in force.vertices()}, edgelabel=lengths_uv)
viewer.show()

vertices_fixed = [0, 1, 2, 3, 4, 5]

# edgelabel={(u, v): (u, v) for u, v in force.edges() if (u, v) != (8, 3)}

edges_constant_length = [
    (0, 6),
    (7, 0),
    (0, 8),
    (8, 3),
    (0, 9),
    (0, 10),
]

length = 7.42 # 5.0 #.4204
force.default_edge_attributes.update({'lmin': 0.0, 'lmax': 1e+7})

for u, v in edges_constant_length:
    force.edge_attribute((u, v), 'lmin', length)
    force.edge_attribute((u, v), 'lmax', length)

edges2 = [(6, 1), (10, 5)]
length2 = 6.25
for u, v in edges2:
    force.edge_attribute((u, v), 'lmin', length2)
    force.edge_attribute((u, v), 'lmax', length2)

for u, v in force.edges():
    sp, ep = force.edge_coordinates(u, v)
    dx = ep[0] - sp[0]
    dy = ep[1] - sp[1]
    l = (dx**2 + dy**2)**0.5
    force.edge_attribute((u, v), 'target', [dx/l, dy/l])
    print('u v:', u, v, ' | dx dy:', dx/l, dy/l)
    # if (u, v) in edges_constant_length:
    #     force.edge_attribute((u, v), 'target', [0, 0])
    #     print('takeout')

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
viewer.draw_force(vertexlabel={key: key for key in force.vertices()}, edgelabel={(u, v): force.edge_attribute((u, v), 'lmax') for u, v in force.edges() if (u, v) != (8, 3)})
viewer.show()

_k_i = force.vertex_index()
_xy = force.vertices_attributes('xy')
print('vertices coordinates')
print(_xy)

_edges = list(force.edges())

_edges = [(_k_i[u], _k_i[v]) for u, v in _edges]

_uv = [[_xy[j][0] - _xy[i][0], _xy[j][1] - _xy[i][1]] for i, j in _edges]

_i_nbrs = {_k_i[key]: [_k_i[nbr] for nbr in force.vertex_neighbors(key)] for key in force.vertices()}

edges_ignore_nbr = [(7, 6), (7, 8), (8, 9), (9, 10)]
neighbours_exclude = [(_k_i[u], _k_i[v]) for u, v in edges_ignore_nbr]

_uv_i = {uv: index for index, uv in enumerate(_edges)}

# _ij_e = {(_k_i[u], _k_i[v]): index for (u, v), index in iter(_uv_i.items())}

_ij_e = {(u, v): index for (u, v), index in iter(_uv_i.items())}

# _fixed = [force.anchor()]
_fixed = []
for key in vertices_fixed:
    _fixed.append(key)
# print('key', _fixed)
_fixed = [_k_i[key] for key in _fixed]
# print('index', _fixed)
_lmin = force.edges_attribute('lmin')
_lmax = force.edges_attribute('lmax')

forces = [(dx**2 + dy**2)**0.5 for dx, dy in _uv]

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
viewer.draw_force(vertexlabel={key: _k_i[key] for key in force.vertices()})
viewer.show()

# force_targets = [[v[0] / l, v[1] / l] if l else [0, 0] for v, l in zip(_uv, forces)]
# print(force_targets)

force_targets = force.edges_attribute('target')
print(force_targets)

# print(_uv_i)
# target_dict = {}
# for u, v in _uv_i:
#     index = _uv_i[(u, v)]
#     targ = force_targets[index]
#     target_dict[(u, v)] = targ

target_none = [_uv_i[(_k_i[u], _k_i[v])] for u, v in edges_constant_length]
# none_add = [1, 2, 12, 14]
# for key in none_add:
#     target_none.append(key)

# target_non_dic = {(u, v): _uv_i[(u, v)] for u, v in edges_constant_length}
# # target_none = []

# viewer = Viewer(form, force, delay_setup=False)
# viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
# viewer.draw_force(vertexlabel={key: key for key in force.vertices()}, edgelabel=target_dict)
# viewer.show()

# viewer = Viewer(form, force, delay_setup=False)
# viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
# viewer.draw_force(vertexlabel={key: key for key in force.vertices()}, edgelabel=target_non_dic)
# viewer.show()

# neighbours_exclude = []

parallelise_edges(_xy, _edges, force_targets, _i_nbrs, _ij_e, fixed=_fixed, kmax=100, lmin=_lmin, lmax=_lmax, neighbours_exclude=neighbours_exclude)

# parallelise_edges(_xy, _edges, force_targets, _i_nbrs, _ij_e, fixed=_fixed, kmax=100, lmin=_lmin, lmax=_lmax, target_none=target_none)

for key in force.vertices():
    i = _k_i[key]
    x, y = _xy[i]
    force.vertex_attribute(key, 'x', x)
    force.vertex_attribute(key, 'y', y)

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
viewer.draw_force(vertexlabel={key: _k_i[key] for key in force.vertices()})
viewer.show()

lengths_uv = {}
for u, v in force.edges():
    lengths_uv[(u, v)] = force.edge_length(u, v)

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form(vertexlabel={key: key for key in form.vertices()})
viewer.draw_force(vertexlabel={key: _k_i[key] for key in force.vertices()}, edgelabel=lengths_uv)
viewer.show()

# from compas_tna.equilibrium import horizontal_nodal

# horizontal_nodal(form, force, alpha=50)

# --------------------------------------------------------------------------
#   3. force diagram manipulation and modify the form diagram
# --------------------------------------------------------------------------

# modify the geometry of the force diagram moving nodes further at right to the left
# move_vertices = [6, 7, 8, 9, 10]
# translation = + 1.0
# for key in move_vertices:
#     x0 = force.vertex_attribute(key, 'x')
#     force.vertex_attribute(key, 'x', x0 + translation)

# set constraints automatically with the form diagram's attributes
# C = ConstraintsCollection(form)
# C.constraints_from_form()

# form_update_from_force_newton(form, force, constraints=C)
form_update_from_force(form, force)

# ------------------------------------------------------------------------------
#   4. display the orginal configuration
#      and the configuration after modifying the force diagram
# ------------------------------------------------------------------------------
viewer = Viewer(form, force, delay_setup=False)

viewer.draw_form(lines=form_lines,
                 forces_on=True,
                 vertexlabel={key: key for key in form.vertices()},
                 external_on=False,
                 vertexsize=0.2,
                 vertexcolor={key: '#000000' for key in fixed},
                 edgelabel={uv: index for index, uv in enumerate(form.edges())}
                 )

viewer.draw_force(lines=force_lines,
                  vertexlabel={key: key for key in force.vertices()},
                  vertexsize=0.2,
                  edgelabel={uv: index for index, uv in enumerate(force.edges())}
                  )

viewer.show()
