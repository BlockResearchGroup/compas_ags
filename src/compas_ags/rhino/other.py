from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os


def get_logger(name):
    logger = logging.getLogger(name)

    try:
        from colorlog import ColoredFormatter
        formatter = ColoredFormatter("%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
                                     datefmt=None,
                                     reset=True,
                                     log_colors={'DEBUG': 'cyan', 'INFO': 'green',
                                                 'WARNING': 'yellow',
                                                 'ERROR': 'red', 'CRITICAL': 'red',
                                                 }
                                     )
    except ImportError:
        formatter = logging.Formatter('[%(levelname)s] %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


__all__ = ['get_logger']


# from compas.geometry import  dot_vectors

# __all__ = [
#     'check_edge_pairs',
#     ]

# def check_edge_pairs(form, force):
#     # check the uv direction in force diagrams
#     # return edge uv that need to be flipped in force digram
#     # and edge index corresponding to the form diagram
#     edges_to_flip = []
#     form_edges = {uv: index for index, uv in enumerate(form.edges())}
#     force_edgelabel_pairs = {}
#     for i, (u, v) in enumerate(force.edges()):
#         force_vector = force.edge_vector(u, v)
#         half_edge = form.face_adjacency_halfedge(u, v)

#         if half_edge in form_edges:
#             form_vector = form.edge_vector(half_edge[0], half_edge[1])
#             dot_product = dot_vectors(form_vector, force_vector)
#             force_in_form = form.edge_attribute(half_edge, 'f')
#             if force_in_form * dot_product < 0:
#                 edges_to_flip.append((u, v))

#         else:
#             half_edge = form.face_adjacency_halfedge(v, u)
#             form_vector = form.edge_vector(half_edge[0], half_edge[1])
#             dot_product = dot_vectors(form_vector, force_vector)
#             force_in_form = form.edge_attribute(half_edge, 'f')
#             if force_in_form * dot_product < 0:
#                 edges_to_flip.append((u, v))

#         force_edgelabel_pairs[u,v] = form_edges[half_edge]

#     return edges_to_flip, force_edgelabel_pairs

# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':
    pass