from PyQt6.QtWidgets import (QWidget, QLineEdit, QLabel, QBoxLayout, QComboBox, QPushButton, QTextEdit, QGridLayout,
                             QSlider, QVBoxLayout,QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
# Modules to embed matplotlib canvas // Ignore unrecognized references!
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure

class UI_display_measurement_window(QWidget):

    # Properties
    meas_data_buffer: dict = None

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
    xz_plot_y_select_slider: QSlider = None
    xz_plot_y_select_lineEdit: QLineEdit = None
    yz_plot_x_select_slider: QSlider = None
    yz_plot_x_select_lineEdit: QLineEdit = None
    xy_plot_z_select_slider: QSlider = None
    xy_plot_z_select_lineEdit: QLineEdit = None

    xz_plot: any = None
    yz_plot: any = None
    xy_plot: any = None


    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        data_selection_widget = self.__init_data_selection_widget()
        data_plot_widget = self.__init_data_plot_widget()

        left_column = QVBoxLayout()
        left_column.addWidget(data_selection_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(left_column, stretch=0)

        right_column = QVBoxLayout()
        right_column.addWidget(data_plot_widget, stretch=1)
        main_layout.addLayout(right_column, stretch=1)

        return



    def __init_data_selection_widget(self):
        main_widget = QFrame()
        main_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        main_widget.setContentsMargins(5, 5, 5, 5)
        main_layout = QGridLayout()
        main_widget.setLayout(main_layout)

        header = QLabel("Data Selection")
        header.setStyleSheet("text-decoration: underline; font-size: 16px; font-weight: bold;")
        self.file_select_comboBox = QComboBox()
        self.file_select_comboBox.addItem("Select ...")
        self.file_select_comboBox.setMinimumWidth(150)
        self.file_select_comboBox.setMinimumHeight(30)
        self.file_select_refresh_button = QPushButton("Refresh")
        self.file_select_read_button = QPushButton("Read File")

        main_layout.addWidget(header,0,0,1,3,alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.file_select_comboBox,1,0,2,2,alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.file_select_refresh_button,1,2,1,1,alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.file_select_read_button,2,2,1,1,alignment=Qt.AlignmentFlag.AlignRight)

        data_details = self.__init_data_details_widget()
        main_layout.addWidget(data_details,3,0,1,3,alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.setRowStretch(4,10)

        return main_widget

    def __init_data_details_widget(self):
        main_widget = QWidget()
        main_layout = QGridLayout()
        main_widget.setLayout(main_layout)

        header = QLabel("Data Info")
        header.setStyleSheet("text-decoration: underline; font-size: 16px; font-weight: bold;")
        self.data_details_textbox = QTextEdit()
        self.data_details_textbox.setReadOnly(True)
        self.data_details_textbox.setText("No Data read...")

        main_layout.addWidget(header,0,0,1,1,alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.data_details_textbox,1,0,1,1,alignment=Qt.AlignmentFlag.AlignCenter)

        return main_widget

    def __init_data_plot_widget(self):
        main_widget = QFrame()
        main_widget.setFrameStyle(QFrame.Shape.StyledPanel)
        main_widget.setContentsMargins(5, 5, 5, 5)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        upper_line_layout = QHBoxLayout()
        parameter_select_label = QLabel("Show Parameter: ")
        self.parameter_select_comboBox = QComboBox()
        self.parameter_select_comboBox.addItem("Select...")
        self.parameter_select_comboBox.setMinimumWidth(150)
        frequency_label = QLabel("Frequency")
        self.frequency_select_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.frequency_select_lineEdit = QLineEdit("...")
        self.frequency_select_lineEdit.setFixedWidth(100)
        upper_line_layout.addWidget(parameter_select_label)
        upper_line_layout.addWidget(self.parameter_select_comboBox)
        upper_line_layout.addSpacing(200)
        upper_line_layout.addWidget(frequency_label)
        upper_line_layout.addWidget(self.frequency_select_slider)
        upper_line_layout.addWidget(self.frequency_select_lineEdit)
        main_layout.addLayout(upper_line_layout)
        main_layout.addSpacing(10)

        middle_line_layout = QHBoxLayout()
        xz_split_label = QLabel("XZ-Plane, Y:")
        self.xz_plot_y_select_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.xz_plot_y_select_lineEdit = QLineEdit("...")
        self.xz_plot_y_select_lineEdit.setMaximumWidth(70)
        yz_split_label = QLabel("YZ-Plane, X:")
        self.yz_plot_x_select_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.yz_plot_x_select_lineEdit = QLineEdit("...")
        self.yz_plot_x_select_lineEdit.setMaximumWidth(70)
        xy_split_label = QLabel("XY-Plane, Z:")
        self.xy_plot_z_select_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.xy_plot_z_select_lineEdit = QLineEdit("...")
        self.xy_plot_z_select_lineEdit.setMaximumWidth(70)
        middle_line_layout.addWidget(xz_split_label)
        middle_line_layout.addWidget(self.xz_plot_y_select_slider)
        middle_line_layout.addWidget(self.xz_plot_y_select_lineEdit)
        middle_line_layout.addSpacing(50)
        middle_line_layout.addWidget(yz_split_label)
        middle_line_layout.addWidget(self.yz_plot_x_select_slider)
        middle_line_layout.addWidget(self.yz_plot_x_select_lineEdit)
        middle_line_layout.addSpacing(50)
        middle_line_layout.addWidget(xy_split_label)
        middle_line_layout.addWidget(self.xy_plot_z_select_slider)
        middle_line_layout.addWidget(self.xy_plot_z_select_lineEdit)
        main_layout.addLayout(middle_line_layout)

        # Setup Graphs with default display
        graphs_layout = QHBoxLayout()
        xz_layout = QVBoxLayout()
        yz_layout = QVBoxLayout()
        xy_layout = QVBoxLayout()
        graphs_layout.addLayout(xz_layout)
        graphs_layout.addLayout(yz_layout)
        graphs_layout.addLayout(xy_layout)

        xz_canvas: FigureCanvas = FigureCanvas(Figure(figsize=(3, 5)))
        yz_canvas: FigureCanvas = FigureCanvas(Figure(figsize=(3, 5)))
        xy_canvas: FigureCanvas = FigureCanvas(Figure(figsize=(3, 5)))

        # Watchout: Do not use alignmentflags, since they clash with QT!
        xz_layout.addWidget(xz_canvas)
        xz_layout.addWidget(NavigationToolbar(xz_canvas))
        yz_layout.addWidget(yz_canvas)
        yz_layout.addWidget(NavigationToolbar(yz_canvas))
        xy_layout.addWidget(xy_canvas)
        xy_layout.addWidget(NavigationToolbar(xy_canvas))

        # sample data
        y, x = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
        z = (1 - x / 2. + x ** 5 + y ** 3) * np.exp(-x ** 2 - y ** 2)
        # x and y are bounds, so z should be the value *inside* those bounds.
        # Therefore, remove the last value from the z array.
        z = z[:-1, :-1]
        z_min, z_max = -np.abs(z).max(), np.abs(z).max()

        xz_ax = xz_canvas.figure.subplots()
        xz_ax.set_title("XZ-Plane")
        yz_ax = yz_canvas.figure.subplots()
        yz_ax.set_title("YZ-Plane")
        xy_ax = xy_canvas.figure.subplots()
        xy_ax.set_title("XY-Plane")

        self.xz_plot = xz_ax.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)
        self.yz_plot = yz_ax.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)
        self.xy_plot = xy_ax.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)

        xz_ax.axis([x.min(), x.max(), y.min(), y.max()])
        xz_canvas.figure.colorbar(self.xz_plot, ax=xz_ax)
        yz_ax.axis([x.min(), x.max(), y.min(), y.max()])
        yz_canvas.figure.colorbar(self.yz_plot, ax=yz_ax)
        xy_ax.axis([x.min(), x.max(), y.min(), y.max()])
        xy_canvas.figure.colorbar(self.xy_plot, ax=xy_ax)

        main_layout.addLayout(graphs_layout, stretch=10)

        return main_widget

    def __gen_data_details_string(self, measurement_config: dict):
        """
        Generates formatted string from measurement_config info to be displayed in a Textbox or similiar.
        """
        info_string = ""
        info_string += f"*Filetype: {measurement_config['type']}, "
        info_string += f"Timestamp: {measurement_config['timestamp']}\n"
        info_string += f"*Mesh configuration: [min : num of steps : max], unit [mm]\n"
        info_string += (f"X:[{measurement_config['mesh_x_min']}:{measurement_config['mesh_x_steps']}:{measurement_config['mesh_x_max']}]\t"
                       f"Y:[{measurement_config['mesh_y_min']}:{measurement_config['mesh_y_steps']}:{measurement_config['mesh_y_max']}]\t"
                       f"Z:[{measurement_config['mesh_z_min']}:{measurement_config['mesh_z_steps']}:{measurement_config['mesh_z_max']}]\n")
        info_string += f"Zero position: {measurement_config['zero_position']}\n"
        info_string += f"Movementspeed: {measurement_config['movespeed']} mm/s\n"
        info_string += f"*VNA Configuration:\n"
        info_string += f"Measured parameters: {measurement_config['parameter']}\n"
        info_string += f"Frequency: [{measurement_config['freq_start']}:{measurement_config['freq_stop']}] [Hz] with {measurement_config['sweep_num_points']} points\n"
        info_string += f"IF Bandwidth: {measurement_config['if_bw']} [Hz]\n"
        info_string += f"RF Output Power: {measurement_config['output_power']} [dBm]\n"
        info_string += f"Averaged over {measurement_config['average_number']} sweeps for each point"
        return info_string





