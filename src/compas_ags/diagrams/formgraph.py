from compas.datastructures import Graph


class FormGraph(Graph):
    """A graph representing the geometry and connectivity of the lines of a form diagram."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def node_index(self) -> dict[int, int]:
        return {node: index for index, node in enumerate(self.nodes())}

    def is_2d(self) -> bool:
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

    def is_planar_embedding(self) -> bool:
        """Verify that the current embedding of the graph is planar."""
        return self.is_2d() and self.is_planar() and not self.is_crossed()

    def embed(self, fixed: list[int] = None, straightline: bool = True) -> bool:
        """Compute a geometry for the graph that embeds it in the plane.

        Returns
        -------
        bool

        """
        return self.embed_in_plane(fixed)
