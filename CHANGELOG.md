# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added `tests/test_ags_compas2_api.py` covering the constraints/Newton/nullspace code paths.

### Changed

* Fixed remaining COMPAS 1.x API calls that raise under COMPAS 2.x: `key_index()` is now `vertex_index()` (`ags/core.py`), and `edge_length`/`edge_coordinates` take a single edge tuple instead of two positional vertex keys (`ags/constraints.py`).
* Fixed `force_update_from_constraints` call inside `update_diagrams_from_constraints` (`ags/graphstatics.py`) not forwarding `kmax`, which always solved with the default of 100 iterations.
* Exported `form_compute_nullspace` and `force_update_from_form_geometrical` from `compas_ags.ags`.

### Removed


## [1.3.3] 2024-11-27

### Added

### Changed

* Changed calculation of target vectors to use edge geometry directly (`edge_line` and `edge_direction`).

### Removed


## [1.3.2] 2024-11-21

### Added

### Changed

* Fixed bug in `Formdiagram.from_graph` related to zero-force edges.

### Removed


## [1.3.1] 2024-11-14

## Added

## Changed

* Fixed bug in `compas_ags.diagrams.forcediagram.ForceDiagram.constraints_from_dual()`.

## Removed


## [1.3.0] 2024-11-12

### Added

* Added viewer based on `compas_viewer`.
* Added `compas_ags.ags.core.rref_sympy`.
* Added type annotations where possible.
* Added `requirements-dof.txt` to include `sympy` as optional dependency.
* Added annotations.

### Changed

* Changed examples to use new viewer.
* Fixed bug in viewer rotation.
* Changed code to be compatible with COMPAS 2.

### Removed

* Removed viewer based on `compas_plotter`.


## [1.2.1] 2023-11-10

### Added

### Changed

### Removed


## [1.2.0] 2022-11-17

### Added

### Changed

* Updated workflow.

### Removed
