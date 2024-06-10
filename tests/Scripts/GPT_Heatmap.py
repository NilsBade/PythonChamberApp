import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg

class HeatmapViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Heatmap Viewer")

        # Create a central widget and set layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create an ImageView widget from pyqtgraph
        self.image_view = pg.ImageView()
        layout.addWidget(self.image_view)

        # Generate a 2D array representing field strengths (for example purposes)
        self.data = self.generate_field_strengths()

        # Display the heatmap
        self.show_heatmap()

    def generate_field_strengths(self):
        # Generate a 2D array with field strengths
        # Example: Gaussian distribution centered in the middle of the array
        x = np.linspace(-3.0, 3.0, 100)
        y = np.linspace(-3.0, 3.0, 100)
        x, y = np.meshgrid(x, y)
        z = np.exp(-(x**2 + y**4))

        return z

    def show_heatmap(self):
        # Display the 2D array in the ImageView widget
        self.image_view.setImage(self.data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = HeatmapViewer()
    viewer.show()
    sys.exit(app.exec())
