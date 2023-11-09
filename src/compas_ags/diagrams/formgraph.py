from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
from compas.datastructures import Network
from compas.datastructures import network_is_crossed


__all__ = ["FormGraph"]


class FormGraph(Network):
    """A graph representing the geometry and connectivity of the lines of a form diagram."""

    def __init__(self):
        super(FormGraph, self).__init__()

    def node_index(self):
        return {node: index for index, node in enumerate(self.nodes())}

    def is_2d(self):
        """Verify that all nodes of the graph lie in a horizontal plane.

        Returns
        -------
        bool
        """
        z = self.nodes_attribute("z")
        zmin = min(z)
        zmax = max(z)
        if (zmax - zmin) ** 2 > 0.001:
            return False
        return True

    # def make_2d(self):
    #     self.nodes_attribute('z', 0.0)

    def is_planar(self):
        """Verify that the graph has a planar embedding.

        Returns
        -------
        bool
        """
        if compas.IPY:
            from compas.rpc import Proxy

            proxy = Proxy("compas.datastructures")
            network_is_planar = proxy.network_is_planar
        else:
            from compas.datastructures import network_is_planar
        return network_is_planar(self)

    def is_crossed(self):
        """Verify that the current embedding of the graph has crossing edges.

        Returns
        -------
        bool
        """
        return network_is_crossed(self)

    def is_planar_embedding(self):
        """Verify that the current embedding of the graph is planar."""
        return self.is_2d() and self.is_planar() and not self.is_crossed()

    def embed(self, fixed=None, straightline=True):
        """Compute a geometry for the graph that embeds it in the plane.

        Returns
        -------
        bool
        """
        if compas.IPY:
            from compas.rpc import Proxy

            proxy = Proxy("compas.datastructures")

            def network_embed_in_plane(network, fixed, straightline):
                network.data = proxy.network_embed_in_plane_proxy(network.data, fixed, straightline)

        else:
            from compas.datastructures import network_embed_in_plane
        return network_embed_in_plane(self, fixed, straightline)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
