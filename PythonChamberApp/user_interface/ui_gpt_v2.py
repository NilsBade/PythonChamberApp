import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph.opengl as gl


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create main widget to hold OpenGL plot
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create an OpenGLWidget
        self.opengl_widget = gl.GLViewWidget()
        layout.addWidget(self.opengl_widget)

        # Initialize the OpenGL plot
        self.initialize_plot()

    def initialize_plot(self):
        # Define vertices of a square in 3D space
        vertices = np.array([
            [1, 1, 0],
            [-1, 1, 0],
            [-1, -1, 0],
            [1, -1, 0]
        ])

        # Define vertex indices to form triangles
        faces = np.array([
            [0, 1, 2],
            [0, 2, 3]
        ])

        # Create mesh data
        md = gl.MeshData(vertexes=vertices, faces=faces)

        # Create GLMeshItem and add it to the OpenGLWidget
        mesh_item = gl.GLMeshItem(meshdata=md, smooth=False, color=(0.7, 0.7, 1.0, 1.0))
        self.opengl_widget.addItem(mesh_item)

        # Set initial camera position
        self.opengl_widget.setCameraPosition(distance=5)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
