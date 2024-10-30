from compas_viewer import Viewer
from compas_viewer.config import Config

from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Circle
from compas.geometry import Polygon
from compas.geometry import bounding_box
from compas_ags.diagrams import ForceDiagram
from compas_ags.diagrams import FormDiagram

loadcolor = Color.green().darkened(50)
reactioncolor = Color.green().darkened(50)
tensioncolor = Color.red().lightened(25)
compressioncolor = Color.blue().lightened(25)


class AGSViewer(Viewer):
    def __init__(self, config: Config | None = None, **kwargs):
        config = config or Config()
        config.renderer.view = "top"
        config.camera.target = [0, 0, 0]
        config.camera.position = [0, 0, 10]
        config.renderer.gridsize = [100, 100, 100, 100]

        super().__init__(config, **kwargs)

        self.renderer.camera.rotation.set(0, 0, 0, False)

        self.form: FormDiagram = None
        self.force: ForceDiagram = None

    def add_form(self, form: FormDiagram, show_forces=True, scale_forces=0.1, nodesize=0.1):
        self.form = form

        self.scene.add(
            self.form,
            show_faces=False,
            show_lines=not show_forces,
            linewidth=2,
            name="FormDiagram",
        )

        nodes = []
        for vertex in self.form.vertices():
            circle = Circle.from_point_and_radius(
                point=self.form.vertex_point(vertex) + [0, 0, 0.001],
                radius=nodesize,
            )
            nodes.append(circle.to_polygon(n=128))

        self.scene.add(
            nodes,
            name="Nodes",
            facecolor=Color.white(),
            linecolor=Color.black(),
        )

        if not show_forces:
            return

        external = []
        compression = []
        tension = []
        for edge in self.form.edges():
            line = self.form.edge_line(edge)
            vector = line.direction.cross([0, 0, 1])
            force = self.form.edge_attribute(edge, name="f")
            is_external = self.form.edge_attribute(edge, name="is_external")

            w = scale_forces * 0.5 * abs(force)
            a = line.start + vector * -w
            b = line.end + vector * -w
            c = line.end + vector * +w
            d = line.start + vector * +w

            if is_external:
                external.append(Polygon([a, b, c, d]))
            elif force > 0:
                tension.append(Polygon([a, b, c, d]))
            elif force < 0:
                compression.append(Polygon([a, b, c, d]))

        self.scene.add(
            external,
            name="External Forces",
            facecolor=reactioncolor,
            linecolor=reactioncolor.contrast,
        )
        self.scene.add(
            compression,
            name="Compression",
            facecolor=compressioncolor,
            linecolor=compressioncolor.contrast,
        )
        self.scene.add(
            tension,
            name="Tension",
            facecolor=tensioncolor,
            linecolor=tensioncolor.contrast,
        )

    def add_force(self, force: ForceDiagram):
        self.force = force

        b1 = Box.from_bounding_box(bounding_box(self.form.vertices_attributes("xyz")))
        b2 = Box.from_bounding_box(bounding_box(self.force.vertices_attributes("xyz")))

        dx = b2.xmin - b1.xmax
        if dx < 1:
            dx = 1.5 * (b1.xmax - b2.xmin)
        else:
            dx = 0

        self.scene.add(
            force.translated([dx, 0, 0]),
            show_faces=False,
            linewidth=2,
            name="ForceDiagram",
        )
