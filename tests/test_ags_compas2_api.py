"""Regression tests for the compas 1.x -> 2.x API migration in compas_ags.ags.

These exercise the code paths that raise under COMPAS 2.x when the pre-2.x
API is still used: `key_index()` (now `vertex_index()`), and `edge_length`/
`edge_coordinates` called with two positional vertex keys instead of a single
edge tuple. Without the accompanying fixes, all three tests here fail with
`AttributeError`/`TypeError`.

Uses `paper/gs_form_force.obj` for fixtures: `paper/gs_arch.json` is a
compas 0.17.2-era serialization that compas 2.x's `from_json` can no longer
reconstruct, which is a separate issue from the ones covered here.
"""

import compas_ags
from compas_ags.ags import ConstraintsCollection
from compas_ags.ags import HorizontalFix
from compas_ags.ags import form_compute_nullspace
from compas_ags.ags import form_update_from_force_newton
from compas_ags.ags import form_update_q_from_qind
from compas_ags.ags import force_update_from_form
from compas_ags.diagrams import FormDiagram
from compas_ags.diagrams import FormGraph
from compas_ags.diagrams import ForceDiagram


def _truss_form_force():
    graph = FormGraph.from_obj(compas_ags.get("paper/gs_form_force.obj"))
    form = FormDiagram.from_graph(graph)
    force = ForceDiagram.from_formdiagram(form)

    form.edge_attribute((0, 1), "q", -5.0 / form.edge_length((0, 1)))
    form.edge_attribute((0, 1), "is_ind", True)
    form.vertex_attribute(5, "is_fixed", True)
    form.vertex_attribute(3, "is_fixed", True)

    form_update_q_from_qind(form)
    force_update_from_form(force, form)
    return form, force


def test_constraints_from_form_runs():
    form, _force = _truss_form_force()
    constraints = ConstraintsCollection(form)
    constraints.constraints_from_form()
    assert len(constraints.constraints) > 0


def test_form_update_from_force_newton_converges():
    form, force = _truss_form_force()

    x0 = force.vertex_attribute(1, "x")
    force.vertex_attribute(1, "x", x0 + 0.3)

    constraints = ConstraintsCollection(form)
    constraints.constraints_from_form()

    # Raises SolutionError if it fails to converge within max_iter.
    form_update_from_force_newton(form, force, constraints=constraints)


def test_form_compute_nullspace_runs():
    form, force = _truss_form_force()

    constraints = ConstraintsCollection(form)
    constraints.add_constraint(HorizontalFix(form, 5))
    constraints.add_constraint(HorizontalFix(form, 3))
    constraints.constrain_dependent_leaf_edges_lengths()

    nullspaces = form_compute_nullspace(form, force, constraints)
    assert len(nullspaces) > 0
    for mode in nullspaces:
        assert mode.shape == (form.number_of_vertices(), 2)
