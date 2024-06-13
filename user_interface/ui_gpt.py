import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
import numpy as np

# Create a plot widget
win = pg.GraphicsLayoutWidget(show=True)
plot = win.addPlot(title="Rectangle Example")

# Define the rectangle's vertices
vertices = [
    (0, 0),  # Bottom-left corner
    (5, 0),  # Bottom-right corner
    (5, 3),  # Top-right corner
    (0, 3)   # Top-left corner
]

# Create a GraphItem for the rectangle
rect_item = pg.GraphItem()
rect_item.setData(pos=vertices, adj=np.array([[0, 1], [1, 2], [2, 3], [3, 0]]), pen='r', brush=(255, 0, 0, 100))

# Add the rectangle GraphItem to the plot
plot.addItem(rect_item)

# Example: Add some data to the plot
x = [1, 2, 3, 4, 5]
y = [1, 3, 2, 4, 5]
plot.plot(x, y, pen='b')  # Plotting some data

# Start Qt event loop
if __name__ == '__main__':
    QtGui.QApplication.instance().exec_()
