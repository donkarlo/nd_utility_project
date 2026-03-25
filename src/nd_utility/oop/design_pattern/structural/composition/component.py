from abc import ABC, abstractmethod
from typing import Iterable, Optional, Tuple


class Component(ABC):
    """
    Base class for the Composite pattern.

    Rendering policy:
        - Prefer SVG shown in a Qt window (no file is written automatically).
        - Provide a "Save As..." button in the Qt toolbar (user-triggered save only).
        - If Qt is unavailable, fall back to matplotlib (PNG in-memory) which has a Save button.
    """

    def __init__(self) -> None:
        self.__name: Optional[str] = self.__class__.__name__
        self.__is_name_explicit: bool = False
        self._parent: Optional["Component"] = None

    @abstractmethod
    def stringify(self) -> str:
        raise NotImplementedError

    def set_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a str.")
        if len(name.strip()) == 0:
            raise ValueError("name must not be empty.")
        self.__name = name
        self.__is_name_explicit = True

    def has_explicit_name(self) -> bool:
        return self.__is_name_explicit

    def has_name(self) -> bool:
        return self.__name is not None

    def set_auto_name_if_missing(self, name: str) -> None:
        if self.has_explicit_name():
            return
        if self.__name == self.__class__.__name__:
            self.__name = name

    def set_parent(self, parent: Optional["Component"]) -> None:
        self._parent = parent

    def get_parent(self) -> Optional["Component"]:
        return self._parent

    def get_path(self) -> str:
        path_parts = []
        current_component: Optional["Component"] = self

        while current_component is not None:
            path_parts.append(current_component.get_name())
            current_component = current_component.get_parent()

        path_parts.reverse()
        return "/".join(path_parts)

    def add_child(self, child: "Component") -> None:
        raise NotImplementedError

    def remove_child(self, child: "Component") -> None:
        raise NotImplementedError

    def get_child_group_members(self) -> Tuple["Component", ...]:
        return ()

    def is_leaf(self) -> bool:
        return True

    def get_depth(self) -> int:
        return 1

    def get_size(self) -> int:
        return 1

    def walk(self) -> Iterable["Component"]:
        yield self

    def get_name(self) -> str:
        if self.__name is None:
            return self.__class__.__name__
        return self.__name

    def get_tree(self, prefix: str = "", is_last: bool = True) -> str:
        branch = "└── "
        if not is_last:
            branch = "├── "
        return prefix + branch + self.get_name()

    def get_graphviz_node_identifier(self) -> str:
        """
        Unique node identifier for Graphviz.
        Avoid ':' because Graphviz interprets it as a port separator.
        """
        return self.__class__.__name__ + "_" + str(id(self))

    def get_graphviz_node_label(self) -> str:
        """
        Human readable label shown in the graph.
        - Explicit name is shown as-is.
        - If an origin class name exists, show that.
        - Otherwise show the real runtime class name.
        """
        if self.has_explicit_name():
            return self.get_name()

        if hasattr(self, "_origin_class_name"):
            return self._origin_class_name

        return self.__class__.__name__

    def _create_default_graphviz_dot(self):
        from graphviz import Digraph

        dot = Digraph(comment="Composite Tree")
        dot.engine = "dot"

        dot.graph_attr.update({
            "rankdir": "TB",
            "nodesep": "0.10",
            "ranksep": "0.18",
            "concentrate": "true",
            "splines": "spline",
            "overlap": "false",
            "pack": "true",
            "newrank": "true",
            "pad": "0.02",
            "margin": "0.02",
            "ratio": "compress"
        })

        dot.node_attr.update({
            "shape": "ellipse",
            "fontsize": "10",
            "margin": "0.03,0.02"
        })

        dot.edge_attr.update({
            "arrowsize": "0.6",
            "penwidth": "0.7"
        })

        return dot

    def get_graphviz(self, dot=None, parent_identifier: Optional[str] = None):
        if dot is None:
            dot = self._create_default_graphviz_dot()

        node_identifier = self.get_graphviz_node_identifier()
        dot.node(node_identifier, label=self.get_graphviz_node_label())

        if parent_identifier is not None:
            dot.edge(parent_identifier, node_identifier)

        return dot

    def _show_svg_in_qt_pyside6(self, svg_bytes: bytes, window_title: str) -> bool:
        try:
            from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolBar
            from PySide6.QtGui import QAction
            from PySide6.QtSvgWidgets import QSvgWidget
            from PySide6.QtCore import QByteArray
        except Exception:
            return False

        application = QApplication.instance()
        created_application = False
        if application is None:
            application = QApplication([])
            created_application = True

        main_window = QMainWindow()
        main_window.setWindowTitle(window_title)

        svg_widget = QSvgWidget()
        svg_widget.load(QByteArray(svg_bytes))
        main_window.setCentralWidget(svg_widget)

        toolbar = QToolBar("Tools")
        main_window.addToolBar(toolbar)

        def save_as_action_triggered() -> None:
            file_path, _ = QFileDialog.getSaveFileName(main_window, "Save SVG", "", "SVG Files (*.svg)")
            if file_path is None:
                return
            if len(str(file_path)) == 0:
                return
            if not str(file_path).lower().endswith(".svg"):
                file_path = str(file_path) + ".svg"
            with open(file_path, "wb") as file:
                file.write(svg_bytes)

        save_action = QAction("Save As…", main_window)
        save_action.triggered.connect(save_as_action_triggered)
        toolbar.addAction(save_action)

        main_window.resize(1400, 700)
        main_window.show()

        if created_application:
            application.exec()

        return True

    def _show_svg_in_qt_pyqt5(self, svg_bytes: bytes, window_title: str) -> bool:
        try:
            from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolBar
            from PyQt5.QtWidgets import QAction
            from PyQt5.QtSvg import QSvgWidget
            from PyQt5.QtCore import QByteArray
        except Exception:
            return False

        application = QApplication.instance()
        created_application = False
        if application is None:
            application = QApplication([])
            created_application = True

        main_window = QMainWindow()
        main_window.setWindowTitle(window_title)

        svg_widget = QSvgWidget()
        svg_widget.load(QByteArray(svg_bytes))
        main_window.setCentralWidget(svg_widget)

        toolbar = QToolBar("Tools")
        main_window.addToolBar(toolbar)

        def save_as_action_triggered() -> None:
            file_path, _ = QFileDialog.getSaveFileName(main_window, "Save SVG", "", "SVG Files (*.svg)")
            if file_path is None:
                return
            if len(str(file_path)) == 0:
                return
            if not str(file_path).lower().endswith(".svg"):
                file_path = str(file_path) + ".svg"
            with open(file_path, "wb") as file:
                file.write(svg_bytes)

        save_action = QAction("Save As…", main_window)
        save_action.triggered.connect(save_as_action_triggered)
        toolbar.addAction(save_action)

        main_window.resize(1400, 700)
        main_window.show()

        if created_application:
            application.exec()

        return True

    def _show_png_in_matplotlib(self) -> None:
        import io
        import matplotlib.pyplot as plt

        dot = self.get_graphviz()
        png_bytes = dot.pipe(format="png")
        image = plt.imread(io.BytesIO(png_bytes), format="png")

        height_pixels = image.shape[0]
        width_pixels = image.shape[1]
        aspect_ratio = width_pixels / float(height_pixels)

        figure_height = 4.0
        figure_width = figure_height * aspect_ratio

        plt.figure(figsize=(figure_width, figure_height), dpi=300)
        plt.imshow(image, interpolation="none")
        plt.axis("off")
        plt.tight_layout(pad=0.0)
        plt.show()

    def draw(self) -> None:
        dot = self.get_graphviz()
        svg_bytes = dot.pipe(format="svg")
        window_title = "nd_graph"

        shown = self._show_svg_in_qt_pyside6(svg_bytes=svg_bytes, window_title=window_title)
        if shown:
            return

        shown = self._show_svg_in_qt_pyqt5(svg_bytes=svg_bytes, window_title=window_title)
        if shown:
            return

        self._show_png_in_matplotlib()

    def draw_tree(self) -> None:
        print(self.get_tree())