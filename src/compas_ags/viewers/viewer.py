from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import fabs

from compas_plotters.core import draw_xpoints_xy
from compas_plotters.core import draw_xlines_xy
from compas_plotters.core import draw_xarrows_xy
from compas_plotters.core import draw_xlabels_xy
from compas_plotters.core import draw_xpolygons_xy

from compas.geometry import  dot_vectors

from compas.utilities import color_to_colordict
from compas.utilities import is_color_light

from compas_plotters.core import size_to_sizedict

import matplotlib.pyplot as plt


__author__ = ['Tom Van Mele']
__email__  = 'vanmelet@ethz.ch'


__all__ = ['Viewer']


class Viewer(object):
    """"""

    def __init__(self, form, force, delay_setup=True, figsize=(16, 9)):
        self.form  = form
        self.force = force
        self.fig   = None
        self.ax1   = None
        self.ax2   = None

        self.default_facecolor   = '#ffffff'
        self.default_edgecolor   = '#000000'
        self.default_vertexcolor = '#ffffff'
        self.default_vertexsize  = 0.1
        self.default_edgewidth   = 1.0

        self.default_compressioncolor   = '#0000ff'
        self.default_tensioncolor       = '#ff0000'
        self.default_externalforcecolor = '#00ff00'
        self.default_externalforcewidth = 2.0

        self.default_textcolor = '#000000'
        self.default_fontsize  = 8

        self.default_pointsize  = 0.1
        self.default_linewidth  = 1.0
        self.default_pointcolor = '#ffffff'
        self.default_linecolor  = '#000000'
        self.default_linestyle  = '-'

        self.figsize = figsize

        if not delay_setup:
            self.setup()

    def setup(self):
        self.fig = plt.figure(figsize=self.figsize, tight_layout=True, dpi=96)
        self.ax1 = self.fig.add_subplot('121')
        self.ax2 = self.fig.add_subplot('122')
        self.ax1.set_aspect('equal')
        self.ax2.set_aspect('equal')
        self.ax1.set_xticks([])
        self.ax1.set_yticks([])
        self.ax1.set_xmargin(1.0)
        self.ax1.set_ymargin(1.0)
        self.ax1.set_xlim(-1.0, 11.0)
        self.ax1.set_ylim(-1.0, 11.0)
        self.ax2.set_xticks([])
        self.ax2.set_yticks([])
        self.ax2.set_xmargin(1.0)
        self.ax2.set_ymargin(1.0)
        self.ax2.set_xlim(-1.0, 11.0)
        self.ax2.set_ylim(-1.0, 11.0)
        self.fig.patch.set_facecolor('white')
        self.ax1.axis('off')
        self.ax2.axis('off')

    def draw_form(self,
                  vertices_on=True,
                  edges_on=True,
                  faces_on=False,
                  forces_on=True,
                  external_on=True,
                  arrows_on=True,
                  vertexcolor=None,
                  edgecolor=None,
                  facecolor=None,
                  edgelabel=None,
                  vertexlabel=None,
                  facelabel=None,
                  vertexsize=None,
                  forcescale=1.0,
                  lines=None,
                  points=None):
        """"""
        # preprocess

        vertexlabel = vertexlabel or {}
        edgelabel   = edgelabel or {}
        facelabel   = facelabel or {}
        vertexsize  = size_to_sizedict(vertexsize, self.form.vertices(), self.default_vertexsize)
        vertexcolor = color_to_colordict(vertexcolor, self.form.vertices(), self.default_vertexcolor)
        edgecolor   = color_to_colordict(edgecolor, self.form.edges(), self.default_edgecolor)
        facecolor   = color_to_colordict(facecolor, self.form.faces(), self.default_facecolor)

        # scale and position

        x = self.form.vertices_attribute('x')
        y = self.form.vertices_attribute('y')

        if lines:
            x += [line['start'][0] for line in lines]
            x += [line['end'][0] for line in lines]
            y += [line['start'][1] for line in lines]
            y += [line['end'][1] for line in lines]

        xmin, ymin = min(x), min(y)
        xmax, ymax = max(x), max(y)
        dx, dy = -xmin, -ymin
        scale  = max(fabs(xmax - xmin) / 10.0, fabs(ymax - ymin) / 10.0)

        # vertices

        if vertices_on:
            _points = []
            for key, attr in self.form.vertices(True):
                bgcolor = vertexcolor[key]
                _points.append({
                    'pos'       : [(attr['x'] + dx) / scale, (attr['y'] + dy) / scale],
                    'radius'    : vertexsize[key],
                    'facecolor' : vertexcolor[key],
                    'edgecolor' : self.default_edgecolor,
                    'linewidth' : self.default_edgewidth * 0.5,
                    'text'      : None if key not in vertexlabel else str(vertexlabel[key]),
                    'textcolor' : '#000000' if is_color_light(bgcolor) else '#ffffff',
                    'fontsize'  : self.default_fontsize,
                })
            draw_xpoints_xy(_points, self.ax1)

        # edges

        if edges_on:
            leaves  = set(self.form.leaves())

            _lines  = []
            _arrows = []

            for (u, v), attr in self.form.edges_where({'is_edge': True}, True):
                sp, ep = self.form.edge_coordinates(u, v, 'xy')
                sp = ((sp[0] + dx) / scale, (sp[1] + dy) / scale)
                ep = ((ep[0] + dx) / scale, (ep[1] + dy) / scale)

                if external_on:
                    if u in leaves or v in leaves:
                        text  = None if (u, v) not in edgelabel else str(edgelabel[(u, v)])
                        _arrows.append({
                            'start'    : sp,
                            'end'      : ep,
                            'width'    : self.default_externalforcewidth if not attr['is_ind'] else self.default_edgewidth * 3,
                            'color'    : self.default_externalforcecolor if not attr['is_ind'] else '#000000',
                            'text'     : text,
                            'fontsize' : self.default_fontsize
                        })
                    else:
                        if forces_on:
                            width = forcescale * fabs(attr['f'])
                            color = self.default_tensioncolor if attr['f'] > 0 else self.default_compressioncolor
                            text  = None if (u, v) not in edgelabel else str(edgelabel[(u, v)])
                            _lines.append({
                                'start'    : sp,
                                'end'      : ep,
                                'width'    : width,
                                'color'    : color,
                                'text'     : text,
                                'fontsize' : self.default_fontsize
                            })
                        _arrows.append({
                            'start' : sp,
                            'end'   : ep,
                            'width' : self.default_edgewidth
                        })
                else:
                    if forces_on:
                        width = forcescale * fabs(attr['f'])
                        color = self.default_tensioncolor if attr['f'] > 0 else self.default_compressioncolor
                        text  = None if (u, v) not in edgelabel else str(edgelabel[(u, v)])
                        _lines.append({
                            'start'    : sp,
                            'end'      : ep,
                            'width'    : width,
                            'color'    : color,
                            'text'     : text,
                            'fontsize' : self.default_fontsize
                        })
                    _arrows.append({
                        'start' : sp,
                        'end'   : ep,
                        'width' : self.default_edgewidth if not attr['is_ind'] else self.default_edgewidth * 3
                    })

            if _arrows:
                if arrows_on:
                    draw_xarrows_xy(_arrows, self.ax1)
                else:
                    draw_xlines_xy(_arrows, self.ax1)
            if _lines:
                draw_xlines_xy(_lines, self.ax1, alpha=0.5)

        # faces

        if faces_on:
            _face_polygons = []
            for fkey in self.form.faces():
                vkeys = [vkey for vkey in self.form.face_vertices(fkey)]
                polygon_vertices = [self.form.vertex_coordinates(vkey, axes='xy') for vkey in vkeys]
                polygon_vertices = [[(x + dx) / scale, (y + dy) / scale] for (x, y) in polygon_vertices ]  # scale the polygon
                _face_polygons.append({
                    'points'   : polygon_vertices, 
                    'facecolor': '#e5e5e5',
                    'edgecolor': '#ffffff',
                    'edgewidth': 10.0,
                    'text'     : str(fkey) if fkey not in facelabel else str(facelabel[fkey]),
                    'fontsize' : self.default_fontsize * 2,  # TEMP! TO DIFFER FROM OTHER LABELS
                    'textcolor': self.default_textcolor,
                })
            if _face_polygons:
                draw_xpolygons_xy(_face_polygons, self.ax1)


        # points

        if points:
            _points = []
            for point in points:
                x, y, _ = point['pos']
                _points.append({
                    'pos'       : [(x + dx) / scale, (y + dy) / scale],
                    'text'      : point.get('text', ''),
                    'radius'    : point.get('size', self.default_pointsize),
                    'textcolor' : point.get('textcolor', self.default_textcolor),
                    'facecolor' : point.get('facecolor', self.default_pointcolor),
                    'edgecolor' : point.get('edgecolor', self.default_linecolor),
                    'fontsize'  : self.default_fontsize
                })
            draw_xpoints_xy(_points, self.ax1)

        # lines

        if lines:
            _lines = {}
            style = lines[0].get('style', self.default_linestyle)
            for line in lines:
                temp = line.get('style', self.default_linestyle)
                if temp == style:
                    if temp not in _lines:
                        _lines[temp] = []
                else:
                    _lines[temp] = []
                style = temp
                _lines[temp].append({
                    'start'     : [(line['start'][0] + dx) / scale, (line['start'][1] + dy) / scale],
                    'end'       : [(line['end'][0] + dx) / scale, (line['end'][1] + dy) / scale],
                    'width'     : line.get('width', self.default_linewidth),
                    'color'     : line.get('color', self.default_linecolor),
                    'text'      : line.get('text', ''),
                    'textcolor' : line.get('textcolor', self.default_textcolor),
                    'fontsize'  : self.default_fontsize
                })
            for style in _lines:
                draw_xlines_xy(_lines[style], self.ax1, linestyle=style)


    def check_edge_pairs(self):
        # check the uv direction in force diagrams
        # return edge uv that need to be flipped in force digram
        # and edge index corresponding to the form diagram
        edges_to_flip = []
        form_edges = {uv: index for index, uv in enumerate(self.form.edges())}
        force_edgelabel_pairs = {}
        for i, (u, v) in enumerate(self.force.edges()):
            force_vector = self.force.edge_vector(u, v)
            half_edge = self.form.face_adjacency_halfedge(u, v)

            if half_edge in form_edges:
                form_vector = self.form.edge_vector(half_edge[0], half_edge[1])
                dot_product = dot_vectors(form_vector, force_vector)
                force_in_form = self.form.edge_attribute(half_edge, 'f')
                if force_in_form * dot_product < 0:
                    edges_to_flip.append((u, v))

            else:
                half_edge = self.form.face_adjacency_halfedge(v, u)
                form_vector = self.form.edge_vector(half_edge[0], half_edge[1])
                dot_product = dot_vectors(form_vector, force_vector)
                force_in_form = self.form.edge_attribute(half_edge, 'f')
                if force_in_form * dot_product < 0:
                    edges_to_flip.append((u, v))

            force_edgelabel_pairs[u,v] = form_edges[half_edge]

        return edges_to_flip, force_edgelabel_pairs


    def find_force_ind(self):
        # check the corresponding independent edges in the force diagram
        force_idx_uv = {idx:uv for uv, idx in self.check_edge_pairs()[1].items()}
        form_index_uv = self.form.index_uv()

        force_ind = []
        for idx in list(force_idx_uv.keys()):
            u, v = form_index_uv[idx]
            if (u, v) in self.form.ind():
                force_ind.append(force_idx_uv[idx])
        return force_ind


    def draw_force(self,
                   vertices_on=True,
                   edges_on=True,
                   faces_on=False,
                   forces_on=True,
                   arrows_on=True,
                   vertexcolor=None,
                   edgecolor=None,
                   facecolor=None,
                   edgelabel=None,
                   facelabel=None,
                   vertexlabel=None,
                   vertexsize=None,
                   lines=None,
                   points=None):
        """"""
        # preprocess

        vertexlabel = vertexlabel or {}
        edgelabel   = edgelabel or {}
        facelabel   = facelabel or {}
        vertexsize  = size_to_sizedict(vertexsize, self.force.vertices(), self.default_vertexsize)
        vertexcolor = color_to_colordict(vertexcolor, self.force.vertices(), self.default_vertexcolor)
        edgecolor   = color_to_colordict(edgecolor, self.force.edges(), self.default_edgecolor)

        # scale and position

        x = self.force.vertices_attribute('x')
        y = self.force.vertices_attribute('y')
        if lines:
            x += [line['start'][0] for line in lines]
            x += [line['end'][0] for line in lines]
            y += [line['start'][1] for line in lines]
            y += [line['end'][1] for line in lines]
        xmin, ymin = min(x), min(y)
        xmax, ymax = max(x), max(y)
        dx, dy = -xmin, -ymin
        scale  = max(fabs(xmax - xmin) / 10.0, fabs(ymax - ymin) / 10.0)

        # vertices
        if vertices_on:
            _points = []
            for key, attr in self.force.vertices(True):
                bgcolor = vertexcolor[key]
                _points.append({
                    'pos'       : ((attr['x'] + dx) / scale, (attr['y'] + dy) / scale),
                    'radius'    : vertexsize[key],
                    'facecolor' : bgcolor,
                    'edgecolor' : self.default_edgecolor,
                    'linewidth' : self.default_edgewidth * 0.5,
                    'text'      : None if key not in vertexlabel else str(vertexlabel[key]),
                    'textcolor' : '#000000' if is_color_light(bgcolor) else '#ffffff',
                    'fontsize'  : self.default_fontsize
                })
            draw_xpoints_xy(_points, self.ax2)

        # edges
        if edges_on:
            leaves = set(self.form.leaves())
            _arrows = []
            edges_to_flip, force_edgelabel_pairs = self.check_edge_pairs()
            for (u, v), attr in self.force.edges(True):
                if (u, v) in edges_to_flip:
                    ep, sp = self.force.edge_coordinates(u, v, 'xy')
                else:
                    sp, ep = self.force.edge_coordinates(u, v, 'xy')
                sp = ((sp[0] + dx) / scale, (sp[1] + dy) / scale)
                ep = ((ep[0] + dx) / scale, (ep[1] + dy) / scale)
                form_u, form_v = self.form.face_adjacency_edge(u, v)
                text  = None if (u, v) not in edgelabel else str(edgelabel[(u, v)])
                if form_u in leaves or form_v in leaves:
                    _arrows.append({
                        'start' : sp,
                        'end'   : ep,
                        'color' : self.default_externalforcecolor if (u, v) not in self.find_force_ind() else '#000000',
                        'width' : self.default_externalforcewidth if (u, v) not in self.find_force_ind() else self.default_edgewidth * 3,
                        'text'  : text,
                        'fontsize'  : self.default_fontsize,
                    })
                else:
                    _arrows.append({
                        'start' : sp,
                        'end'   : ep,
                        'color' : self.default_edgecolor,
                        'width' : self.default_edgewidth,
                        'text'  : text,
                        'fontsize'  : self.default_fontsize,
                    })
            if arrows_on:
                draw_xarrows_xy(_arrows, self.ax2)
            else:
                draw_xlines_xy(_arrows, self.ax2)

        # lines

        if lines:
            _lines = {}
            style = lines[0].get('style', self.default_linestyle)
            for line in lines:
                temp = line.get('style', self.default_linestyle)
                if temp == style:
                    if temp not in _lines:
                        _lines[temp] = []
                else:
                    _lines[temp] = []
                style = temp
                _lines[temp].append({
                    'start'     : [(line['start'][0] + dx) / scale, (line['start'][1] + dy) / scale],
                    'end'       : [(line['end'][0] + dx) / scale, (line['end'][1] + dy) / scale],
                    'width'     : line.get('width', self.default_linewidth),
                    'color'     : line.get('color', self.default_linecolor),
                    'text'      : line.get('text', ''),
                    'textcolor' : line.get('textcolor', self.default_textcolor),
                    'fontsize'  : self.default_fontsize
                })
            for style in _lines:
                draw_xlines_xy(_lines[style], self.ax2, linestyle=style)

            # faces

        if faces_on:
            _face_polygons = []
            for fkey in self.force.faces():
                vkeys = [vkey for vkey in self.force.face_vertices(fkey)]
                polygon_vertices = [self.force.vertex_coordinates(vkey, axes='xy') for vkey in vkeys]
                polygon_vertices = [[(x + dx) / scale, (y + dy) / scale] for (x, y) in polygon_vertices ]  # scale the polygon
                _face_polygons.append({
                    'points'   : polygon_vertices, 
                    'facecolor': '#e5e5e5',
                    'edgecolor': '#ffffff',
                    'edgewidth': 10.0,
                    'text'     : str(fkey) if fkey not in facelabel else str(facelabel[fkey]),
                    'fontsize' : self.default_fontsize * 2,  # TEMP! TO DIFFER FROM OTHER LABELS
                    'textcolor': self.default_textcolor,
                })
            if _face_polygons:
                draw_xpolygons_xy(_face_polygons, self.ax2)


    def show(self):
        plt.show()

    def save(self, filepath, **kwargs):
        """Saves the plot to a file.

        Parameters
        ----------
        filepath : str
            Full path of the file.

        Notes
        -----
        For an overview of all configuration options, see [1]_.

        References
        ----------
        .. [1] https://matplotlib.org/2.0.2/api/pyplot_api.html#matplotlib.pyplot.savefig

        """
        plt.savefig(filepath, **kwargs)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas_ags
    from compas_ags.diagrams import FormGraph
    from compas_ags.diagrams import FormDiagram
    from compas_ags.diagrams import ForceDiagram

    graph = FormGraph.from_obj(compas_ags.get('paper/gs_form_force.obj')) 
    form = FormDiagram.from_graph(graph)

    # form = FormDiagram.from_obj(compas_ags.get('paper/grid_irregular.obj'))
    # form.identify_fixed()

    force = ForceDiagram.from_formdiagram(form)

    form.set_edge_force_by_index(0, -30.0)

    # update force densities of form and force diagrams
    from compas_ags.ags import graphstatics
    graphstatics.form_update_q_from_qind(form)
    graphstatics.force_update_from_form(force, form)


    viewer = Viewer(form, force, delay_setup=False)
    print(viewer.check_edge_pairs())

    viewer.draw_form(
        edgelabel={(u, v): '{:.1f}'.format(form.edge_length(u, v)) for u, v in form.edges()},
        vertexlabel={key: key for key in form.vertices()},)
    # viewer.draw_force()
    viewer.draw_force(
        vertexsize=0.15,
        vertexlabel={key: key for key in force.vertices()},
        edgelabel={uv: index for index, uv in enumerate(force.edges())},)

    viewer.show()
