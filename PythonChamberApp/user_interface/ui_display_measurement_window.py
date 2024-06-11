from PyQt6.QtWidgets import (QWidget, QLineEdit, QLabel, QBoxLayout, QComboBox, QPushButton, QTextEdit, QGridLayout,
                             QSlider, QVBoxLayout, QHBoxLayout, QFrame)
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
    frequency_vector: np.ndarray[float] = None
    x_vector: np.ndarray[float] = None
    y_vector: np.ndarray[float] = None
    z_vector: np.ndarray[float] = None

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

    xz_figure: Figure = None
    yz_figure: Figure = None
    xy_figure: Figure = None
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

        # connect internal Signals & Slots
        self.frequency_select_slider.valueChanged.connect(self.__update_frequency_lineEdit)
        self.yz_plot_x_select_slider.valueChanged.connect(self.__update_x_select_lineEdit)
        self.xz_plot_y_select_slider.valueChanged.connect(self.__update_y_select_lineEdit)
        self.xy_plot_z_select_slider.valueChanged.connect(self.__update_z_select_lineEdit)

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

        main_layout.addWidget(header, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.file_select_comboBox, 1, 0, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.file_select_refresh_button, 1, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.file_select_read_button, 2, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)

        data_details = self.__init_data_details_widget()
        main_layout.addWidget(data_details, 3, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.setRowStretch(4, 10)

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
        self.data_details_textbox.setMinimumHeight(400)

        main_layout.addWidget(header, 0, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.data_details_textbox, 1, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

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
        self.frequency_select_slider.setMaximumWidth(300)
        self.frequency_select_lineEdit = QLineEdit("...")
        self.frequency_select_lineEdit.setFixedWidth(150)
        upper_line_layout.addWidget(parameter_select_label)
        upper_line_layout.addWidget(self.parameter_select_comboBox)
        upper_line_layout.addSpacing(200)
        upper_line_layout.addWidget(frequency_label)
        upper_line_layout.addWidget(self.frequency_select_slider)
        upper_line_layout.addWidget(self.frequency_select_lineEdit)
        upper_line_layout.addStretch()
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

        self.xz_figure = xz_canvas.figure
        self.yz_figure = yz_canvas.figure
        self.xy_figure = xy_canvas.figure

        xz_ax.axis([x.min(), x.max(), y.min(), y.max()])
        self.xz_figure.colorbar(self.xz_plot, ax=xz_ax)
        yz_ax.axis([x.min(), x.max(), y.min(), y.max()])
        self.yz_figure.colorbar(self.yz_plot, ax=yz_ax)
        xy_ax.axis([x.min(), x.max(), y.min(), y.max()])
        self.xy_figure.colorbar(self.xy_plot, ax=xy_ax)

        main_layout.addLayout(graphs_layout, stretch=10)

        return main_widget

    def __gen_data_details_string(self, measurement_config: dict):
        """
        Generates formatted string from measurement_config info to be displayed in a Textbox or similiar.
        """
        info_string = ""
        info_string += f"*Filetype: {measurement_config['type']}\n"
        info_string += f"Timestamp: {measurement_config['timestamp']}\n"
        info_string += f"*Mesh configuration:\n[min : num of steps : max], unit [mm]\n"
        info_string += (
            f"X:[{measurement_config['mesh_x_min']} : {measurement_config['mesh_x_steps']} :  {measurement_config['mesh_x_max']}]\n"
            f"Y:[{measurement_config['mesh_y_min']} : {measurement_config['mesh_y_steps']} : {measurement_config['mesh_y_max']}]\n"
            f"Z:[{measurement_config['mesh_z_min']} : {measurement_config['mesh_z_steps']} : {measurement_config['mesh_z_max']}]\n")
        info_string += f"Zero position: {measurement_config['zero_position']}\n"
        info_string += f"Movementspeed: {measurement_config['movespeed']} mm/s\n"
        info_string += f"*VNA Configuration:\n"
        info_string += f"Measured parameters: {measurement_config['parameter']}\n"
        info_string += f"Frequency: [{measurement_config['freq_start']} : {measurement_config['freq_stop']}] [Hz] with {measurement_config['sweep_num_points']} points\n"
        info_string += f"IF Bandwidth: {measurement_config['if_bw']} [Hz]\n"
        info_string += f"RF Output Power: {measurement_config['output_power']} [dBm]\n"
        info_string += f"Averaged over {measurement_config['average_number']} sweeps for each point"
        return info_string

    def __update_frequency_lineEdit(self):
        """
        updates frequency lineEdit according to slider position. Must be connected to slider value changed signal.
        """
        slider_val = self.frequency_select_slider.value()
        if self.frequency_vector[slider_val] > 1e9:
            self.frequency_select_lineEdit.setText(f"{self.frequency_vector[slider_val] / 1e9} GHz")
        elif self.frequency_vector[slider_val] > 1e6:
            self.frequency_select_lineEdit.setText(f"{self.frequency_vector[slider_val] / 1e6} MHz")
        elif self.frequency_vector[slider_val] > 1e3:
            self.frequency_select_lineEdit.setText(f"{self.frequency_vector[slider_val] / 1e3} kHz")
        else:
            self.frequency_select_lineEdit.setText(f"{self.frequency_vector[slider_val]} Hz")
        return

    def __update_x_select_lineEdit(self):
        """
        updates x value lineEdit according to slider position. Must be connected to slider value changed signal.
        """
        slider_val = self.yz_plot_x_select_slider.value()
        self.yz_plot_x_select_lineEdit.setText(f"{round(self.x_vector[slider_val],3)} mm")
        return

    def __update_y_select_lineEdit(self):
        """
        updates y value lineEdit according to slider position. Must be connected to slider value changed signal.
        """
        slider_val = self.xz_plot_y_select_slider.value()
        self.xz_plot_y_select_lineEdit.setText(f"{round(self.y_vector[slider_val],3)} mm")
        return

    def __update_z_select_lineEdit(self):
        """
        updates z value lineEdit according to slider position. Must be connected to slider value changed signal.
        """
        slider_val = self.xy_plot_z_select_slider.value()
        self.xy_plot_z_select_lineEdit.setText(f"{round(self.z_vector[slider_val],3)} mm")
        return

    def get_selected_measurement_file(self):
        """
        Returns the selected filename as string from dropdown menu in GUI-Data Selection
        """
        return self.file_select_comboBox.currentText()

    def set_selectable_measurement_files(self, file_names: list[str]):
        """
        Receives selectable file names and updates the file-dropdown menu accordingly

        :param file_names: File names with type ending but without Path to result folder
        """
        self.file_select_comboBox.clear()
        self.file_select_comboBox.addItems(file_names)
        return

    def set_measurement_details(self, measurement_config: dict):
        """
        Receives measurement config dict and prints details to Data Info textbox on GUI
        """
        info_string = self.__gen_data_details_string(measurement_config=measurement_config)
        self.data_details_textbox.clear()
        self.data_details_textbox.setText(info_string)
        return

    def get_selected_parameter(self):
        """
        Returns currently selected S-Parameter from dropdown menu as string ("S11" or "S12" or "S22")
        """
        return self.parameter_select_comboBox.currentText()

    def set_selectable_parameters(self, parameters: list[str]):
        """
        clears dropdown and updates available items according to given list
        """
        self.parameter_select_comboBox.clear()
        self.parameter_select_comboBox.addItems(parameters)
        return

    def get_selected_frequency(self):
        """
        Returns float value of the frequency point currently selected in GUI by slider
        """
        freq_idx = self.frequency_select_slider.value()
        return self.frequency_vector[freq_idx]

    def set_selectable_frequency(self, f_min: float, f_max: float, num_points: int):
        """
        Configures frequency slider with frequency range.
        """
        self.frequency_select_slider.setMinimum(0)
        self.frequency_select_slider.setMaximum(num_points-1)   # one offset cause 0 index included
        self.frequency_select_slider.setSingleStep(1)
        self.frequency_select_slider.setValue(0)
        self.frequency_vector = np.linspace(start=f_min, stop=f_max, num=num_points)
        self.__update_frequency_lineEdit()
        return

    def get_selected_x_coordinate(self):
        """
        Returns selected x coordinate for YZ-Plane graph according to slider position.
        """
        return float(self.x_vector[self.yz_plot_x_select_slider.value()])

    def set_selectable_x_coordinates(self, x_min: float, x_max: float, num_points: int):
        """
        Configures X-coordinate slider of YZ-Plane graph.
        """
        self.yz_plot_x_select_slider.setMinimum(0)
        self.yz_plot_x_select_slider.setMaximum(num_points-1)
        self.yz_plot_x_select_slider.setSingleStep(1)
        self.yz_plot_x_select_slider.setValue(0)
        self.x_vector = np.linspace(start=x_min, stop=x_max, num=num_points)
        self.__update_x_select_lineEdit()
        return

    def get_selected_y_coordinate(self):
        """
        Returns selected y coordinate for XZ-Plane graph according to slider position.
        """
        return float(self.y_vector[self.xz_plot_y_select_slider.value()])

    def set_selectable_y_coordinates(self, y_min: float, y_max: float, num_points: int):
        """
        Configures Y-coordinate slider of XZ-Plane graph.
        """
        self.xz_plot_y_select_slider.setMinimum(0)
        self.xz_plot_y_select_slider.setMaximum(num_points - 1)
        self.xz_plot_y_select_slider.setSingleStep(1)
        self.xz_plot_y_select_slider.setValue(0)
        self.y_vector = np.linspace(start=y_min, stop=y_max, num=num_points)
        self.__update_y_select_lineEdit()
        return

    def get_selected_z_coordinate(self):
        """
        Returns selected z coordinate for XY-Plane graph according to slider position.
        """
        return float(self.z_vector[self.xy_plot_z_select_slider.value()])

    def set_selectable_z_coordinates(self, z_min: float, z_max: float, num_points: int):
        """
        Configures Z-coordinate slider of XY-Plane graph.
        """
        self.xy_plot_z_select_slider.setMinimum(0)
        self.xy_plot_z_select_slider.setMaximum(num_points - 1)
        self.xy_plot_z_select_slider.setSingleStep(1)
        self.xy_plot_z_select_slider.setValue(0)
        self.z_vector = np.linspace(start=z_min, stop=z_max, num=num_points)
        self.__update_z_select_lineEdit()

    def update_xz_plane_plot(self, data_format):
        """
        Receives dataset as 2D coordinates + 1D Amplitude Values and updates the xz-splitplane plot accordingly
        """
        # delete current axis/plot
        self.xz_figure.gca().clear()
        self.xz_plot = self.xz_figure.subplots().pcolormesh()
