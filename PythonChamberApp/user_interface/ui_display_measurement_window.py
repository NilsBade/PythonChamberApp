from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QBoxLayout, QComboBox, QPushButton, QTextEdit, QGridLayout, QSlider, QVBoxLayout
from PyQt6.QtCore import Qt
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('QtAgg')

import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class UI_display_measurement_window(QWidget):

    # Properties

    # Data selection widget
    file_select_comboBox: QComboBox = None
    file_select_refresh_button: QPushButton = None
    file_select_read_button: QPushButton = None

    # Data details widget
    data_details_textbox: QTextEdit = None

    # Data plot widget
    parameter_select_comboBox: QComboBox = None
    frequency_select_slider: QSlider = None
    frequency_select_lineEdit: QLineEdit = None
    y_split_coor_slider: QSlider = None
    y_split_coor_lineEdit: QLineEdit = None


    def __init__(self):
        super().__init__()

        data_selection_widget = self.__init_data_selection_widget()
        data_details_widget = self.__init_data_details_widget()
        data_plot_widget = self.__init_data_plot_widget()

        main_layout = QGridLayout()
        main_layout.addWidget(data_selection_widget,0,0,1,1,Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(data_details_widget,1,0,1,1,Qt.AlignmentFlag.AlignLeft)
        main_layout.setRowStretch(3,1)
        main_layout.addWidget(data_plot_widget,0,1,3,2,Qt.AlignmentFlag.AlignCenter)


        self.setLayout(main_layout)
        return



    def __init_data_selection_widget(self):
        main_widget = QWidget()

        return main_widget

    def __init_data_details_widget(self):
        main_widget = QWidget()

        return main_widget

    def __init_data_plot_widget(self):
        main_widget = QWidget()
        main_layout = QGridLayout()
        first_plot_dict = self.__init_canvas_widget()
        main_layout.addWidget(first_plot_dict['widget'])
        self.firstplot = first_plot_dict['plot']

        main_widget.setLayout(main_layout)
        return main_widget

    def __init_canvas_widget(self):
        """
        sets up a widget that holds a matplotlib plot item with toolbar on top

        :return: dict { 'widget': QWidget, 'plot': MplCanvas }
        """
        plot_widget = QWidget()
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(sc, plot_widget)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)
        plot_widget.setLayout(layout)

        ret_dict = { 'widget': plot_widget, 'plot': sc}
        return ret_dict





