from PyQt6.QtWidgets import (QWidget, QLineEdit, QLabel, QBoxLayout, QComboBox, QPushButton, QTextEdit, QGridLayout,
                             QSlider, QVBoxLayout, QHBoxLayout, QFrame, QCheckBox)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from datetime import datetime
# Modules to embed matplotlib canvas // Ignore unrecognized references!
import matplotlib.axes
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure


class UI_display_measurement_window(QWidget):
    # Properties
    frequency_vector: np.ndarray = None
    x_vector: np.ndarray = None
    y_vector: np.ndarray = None
    z_vector: np.ndarray = None
    x_zero_pos: float = None
    y_zero_pos: float = None
    z_zero_pos: float = None

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
    coor_AUT_checkBox: QCheckBox = None
    unit_display_comboBox: QComboBox = None

    xz_plot_y_select_slider: QSlider = None
    xz_plot_y_select_lineEdit: QLineEdit = None
    yz_plot_x_select_slider: QSlider = None
    yz_plot_x_select_lineEdit: QLineEdit = None
    xy_plot_z_select_slider: QSlider = None
    xy_plot_z_select_lineEdit: QLineEdit = None

    xz_canvas: FigureCanvas = None
    yz_canvas: FigureCanvas = None
    xy_canvas: FigureCanvas = None
    xz_figure: Figure = None
    yz_figure: Figure = None
    xy_figure: Figure = None
    xz_plot = None
    xz_phase_plot = None
    xz_colorbar = None
    xz_phase_colorbar = None
    xz_axes: matplotlib.axes.Axes = None
    xz_phase_axes: matplotlib.axes.Axes = None
    yz_plot = None
    yz_phase_plot = None
    yz_colorbar = None
    yz_phase_colorbar = None
    yz_axes: matplotlib.axes.Axes = None
    yz_phase_axes: matplotlib.axes.Axes = None
    xy_plot = None
    xy_phase_plot = None
    xy_colorbar = None
    xy_phase_colorbar = None
    xy_axes: matplotlib.axes.Axes = None
    xy_phase_axes: matplotlib.axes.Axes = None

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

        # disable plot interactions until data was read
        self.disable_plot_interactions()

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
        self.coor_AUT_checkBox = QCheckBox("Display AUT Coordinates")
        self.unit_display_comboBox = QComboBox()
        unit_label = QLabel("Display Unit: ")
        self.unit_display_comboBox.addItems(["Linear", "dBmax"])
        upper_line_layout.addWidget(parameter_select_label)
        upper_line_layout.addWidget(self.parameter_select_comboBox)
        upper_line_layout.addSpacing(200)
        upper_line_layout.addWidget(frequency_label)
        upper_line_layout.addWidget(self.frequency_select_slider)
        upper_line_layout.addWidget(self.frequency_select_lineEdit)
        upper_line_layout.addSpacing(100)
        upper_line_layout.addWidget(unit_label)
        upper_line_layout.addWidget(self.unit_display_comboBox)
        upper_line_layout.addSpacing(50)
        upper_line_layout.addWidget(self.coor_AUT_checkBox)
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

        self.xz_canvas: FigureCanvas = FigureCanvas(Figure(figsize=(3, 5)))
        self.yz_canvas: FigureCanvas = FigureCanvas(Figure(figsize=(3, 5)))
        self.xy_canvas: FigureCanvas = FigureCanvas(Figure(figsize=(3, 5)))

        # Watchout: Do not use alignmentflags, since they clash with QT!
        xz_layout.addWidget(self.xz_canvas)
        xz_layout.addWidget(NavigationToolbar(self.xz_canvas))
        yz_layout.addWidget(self.yz_canvas)
        yz_layout.addWidget(NavigationToolbar(self.yz_canvas))
        xy_layout.addWidget(self.xy_canvas)
        xy_layout.addWidget(NavigationToolbar(self.xy_canvas))

        # sample data
        y, x = np.meshgrid(np.linspace(-3, 3, 100), np.linspace(-3, 3, 100))
        z = (1 - x / 2. + x ** 5 + y ** 3) * np.exp(-x ** 2 - y ** 2)
        # x and y are bounds, so z should be the value *inside* those bounds.
        # Therefore, remove the last value from the z array.
        z = z[:-1, :-1]
        z_min, z_max = -np.abs(z).max(), np.abs(z).max()

        self.xz_figure = self.xz_canvas.figure
        self.yz_figure = self.yz_canvas.figure
        self.xy_figure = self.xy_canvas.figure

        self.xz_axes, self.xz_phase_axes = self.xz_figure.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
        self.xz_axes.set_title("XZ-Plane Amplitude")
        self.xz_phase_axes.set_title("XZ-Plane Phase")
        self.yz_axes, self.yz_phase_axes = self.yz_figure.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
        self.yz_axes.set_title("YZ-Plane Amplitude")
        self.yz_phase_axes.set_title("YZ-Plane Phase")
        self.xy_axes, self.xy_phase_axes = self.xy_figure.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
        self.xy_axes.set_title("XY-Plane Amplitude")
        self.xy_phase_axes.set_title("XY-Plane Phase")

        self.xz_plot = self.xz_axes.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)
        self.yz_plot = self.yz_axes.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)
        self.xy_plot = self.xy_axes.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)
        self.xz_phase_plot = self.xz_phase_axes.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)
        self.yz_phase_plot = self.yz_phase_axes.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)
        self.xy_phase_plot = self.xy_phase_axes.pcolormesh(x, y, z, cmap='Spectral_r', vmin=z_min, vmax=z_max)

        self.xz_axes.axis([x.min(), x.max(), y.min(), y.max()])
        self.xz_colorbar = self.xz_figure.colorbar(self.xz_plot, ax=self.xz_axes)
        self.yz_axes.axis([x.min(), x.max(), y.min(), y.max()])
        self.yz_colorbar = self.yz_figure.colorbar(self.yz_plot, ax=self.yz_axes)
        self.xy_axes.axis([x.min(), x.max(), y.min(), y.max()])
        self.xy_colorbar = self.xy_figure.colorbar(self.xy_plot, ax=self.xy_axes)
        self.xz_phase_axes.axis([x.min(), x.max(), y.min(), y.max()])
        self.xz_phase_colorbar = self.xz_figure.colorbar(self.xz_phase_plot, ax=self.xz_phase_axes)
        self.yz_phase_axes.axis([x.min(), x.max(), y.min(), y.max()])
        self.yz_phase_colorbar = self.yz_figure.colorbar(self.yz_phase_plot, ax=self.yz_phase_axes)
        self.xy_phase_axes.axis([x.min(), x.max(), y.min(), y.max()])
        self.xy_phase_colorbar = self.xy_figure.colorbar(self.xy_phase_plot, ax=self.xy_phase_axes)

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

    @staticmethod
    def __set_slider_values_noSignals(slider_obj: QSlider, val_vec: np.ndarray):
        """
        Sets new minima maxima ACCORDING TO LENGTH of val_vec and resets value to zero while blocking all signals
        of slider object. Silent reset, suppress undesired updates.
        >> The Slider does not hold the values of the val_vec itself but can be used for indexing and retrieving
        values from val_vec!
        """
        slider_obj.blockSignals(True)
        slider_obj.setMinimum(0)
        slider_obj.setMaximum(val_vec.__len__() - 1)  # one offset cause 0 index included
        slider_obj.setSingleStep(1)
        slider_obj.setValue(0)
        slider_obj.blockSignals(False)
        return

    def enable_plot_interactions(self):
        """
        Enables all GUI elements that are used to interact and visualize the read measurement data.
        """
        self.parameter_select_comboBox.setEnabled(True)
        self.frequency_select_slider.setEnabled(True)
        self.frequency_select_lineEdit.setEnabled(True)
        self.unit_display_comboBox.setEnabled(True)
        self.coor_AUT_checkBox.setEnabled(True)
        self.xz_plot_y_select_slider.setEnabled(True)
        self.xz_plot_y_select_lineEdit.setEnabled(True)
        self.yz_plot_x_select_slider.setEnabled(True)
        self.yz_plot_x_select_lineEdit.setEnabled(True)
        self.xy_plot_z_select_slider.setEnabled(True)
        self.xy_plot_z_select_lineEdit.setEnabled(True)
        return

    def disable_plot_interactions(self):
        """
        Disables all GUI elements that are used to interact and visualize the read measurement data.
        """
        self.parameter_select_comboBox.setEnabled(False)
        self.frequency_select_slider.setEnabled(False)
        self.frequency_select_lineEdit.setEnabled(False)
        self.unit_display_comboBox.setEnabled(False)
        self.coor_AUT_checkBox.setEnabled(False)
        self.xz_plot_y_select_slider.setEnabled(False)
        self.xz_plot_y_select_lineEdit.setEnabled(False)
        self.yz_plot_x_select_slider.setEnabled(False)
        self.yz_plot_x_select_lineEdit.setEnabled(False)
        self.xy_plot_z_select_slider.setEnabled(False)
        self.xy_plot_z_select_lineEdit.setEnabled(False)
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
        Receives measurement config dict and prints details to Data Info textbox on GUI.
        Also stores zero position locally in display_window_object for later graph-display in AUT coordinates.
        """
        info_string = self.__gen_data_details_string(measurement_config=measurement_config)
        self.data_details_textbox.clear()
        self.data_details_textbox.setText(info_string)

        self.x_zero_pos = measurement_config['zero_position'][0]
        self.y_zero_pos = measurement_config['zero_position'][1]
        self.z_zero_pos = measurement_config['zero_position'][2]
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
        self.parameter_select_comboBox.blockSignals(True)
        self.parameter_select_comboBox.clear()
        self.parameter_select_comboBox.addItems(parameters)
        self.parameter_select_comboBox.blockSignals(False)
        return

    def get_selected_frequency(self):
        """
        Returns float value of the frequency point currently selected in GUI by slider
        """
        freq_idx = self.frequency_select_slider.value()
        return self.frequency_vector[freq_idx]

    def get_selected_frequency_by_idx(self):
        """
        Returns selected frequency's index in freq-vector according to slider position
        """
        return self.frequency_select_slider.value()

    def set_selectable_frequency(self, f_vec: np.ndarray):
        """
        Configures frequency slider with frequency range.
        """
        # encapsulate setValue to not issue graph updates when new values are configured while reading new meas file
        self.__set_slider_values_noSignals(self.frequency_select_slider, f_vec)
        self.frequency_vector = f_vec
        self.__update_frequency_lineEdit()
        return

    def get_displ_aut_coordinates(self):
        """
        Returns state of checkbox to decide whether AUT coordinates should be used for plotting (True) or chamber
        coordinates should be displayed (False).
        """
        return self.coor_AUT_checkBox.isChecked()

    def get_selected_x_coordinate(self):
        """
        Returns selected x coordinate for YZ-Plane graph according to slider position.
        WARNING: this coordinate is in chamber coordinates like displayed in GUI, not relative to AUT center!
        """
        return float(self.x_vector[self.yz_plot_x_select_slider.value()])

    def get_selected_x_coordinate_by_idx(self):
        """
        Returns selected x coordinate's index in x-vector according to slider position
        """
        return self.yz_plot_x_select_slider.value()

    def set_selectable_x_coordinates(self, x_vec: np.ndarray):
        """
        Configures X-coordinate slider of YZ-Plane graph.
        """
        # encapsulate setValue to not issue graph updates when new values are configured while reading new meas file
        self.__set_slider_values_noSignals(self.yz_plot_x_select_slider, x_vec)
        self.x_vector = x_vec
        self.__update_x_select_lineEdit()
        return

    def get_selected_y_coordinate(self):
        """
        Returns selected y coordinate for XZ-Plane graph according to slider position.
        WARNING: this coordinate is in chamber coordinates like displayed in GUI, not relative to AUT center!
        """
        return float(self.y_vector[self.xz_plot_y_select_slider.value()])

    def get_selected_y_coordinate_by_idx(self):
        """
        Returns selected y coordinate's index in y-vector according to slider position
        """
        return self.xz_plot_y_select_slider.value()

    def set_selectable_y_coordinates(self, y_vec: np.ndarray):
        """
        Configures Y-coordinate slider of XZ-Plane graph.
        """
        # encapsulate setValue to not issue graph updates when new values are configured while reading new meas file
        self.__set_slider_values_noSignals(self.xz_plot_y_select_slider, y_vec)
        self.y_vector = y_vec
        self.__update_y_select_lineEdit()
        return

    def get_selected_z_coordinate(self):
        """
        Returns selected z coordinate for XY-Plane graph according to slider position.
        WARNING: this coordinate is in chamber coordinates like displayed in GUI, not relative to AUT center!
        """
        return float(self.z_vector[self.xy_plot_z_select_slider.value()])

    def get_selected_z_coordinate_by_idx(self):
        """
        Returns selected z coordinate's index in z-vector according to slider position
        """
        return self.xy_plot_z_select_slider.value()

    def set_selectable_z_coordinates(self, z_vec: np.ndarray):
        """
        Configures Z-coordinate slider of XY-Plane graph.
        """
        # encapsulate setValue to not issue graph updates when new values are configured while reading new meas file
        self.__set_slider_values_noSignals(self.xy_plot_z_select_slider, z_vec)
        self.z_vector = z_vec
        self.__update_z_select_lineEdit()

    # noinspection PyUnreachableCode
    def update_xz_plane_plot(self, data_amp_array: np.ndarray, data_phase_array: np.ndarray):
        """
        Receives 2d array with amplitude values sorted so that x,y indexing of array fits to the measured points along
        X and Z Axis.

        Evaluates itself if chamber coordinates should be displayed or AUT coordinates (internal checkbox in display
        window) and acts accordingly.

        e.g. At xvec[0], zvec[0] is data_amp_array[0,0]. At xvec[20], zvec[100] is data_amp_array[20,100] etc.
        """
        # delete current axis/plot
        self.xz_axes.remove()
        self.xz_colorbar.remove()
        self.xz_phase_axes.remove()
        self.xz_phase_colorbar.remove()

        # find min and max amplitude in given dataset to set up axis/colorbar
        max_amp = data_amp_array.max()
        min_amp = data_amp_array.min()

        # check if display value in dBmax is selected and convert data array if necessary
        if self.unit_display_comboBox.currentText() == "dBmax":
            data_amp_array = 10 * np.log10(data_amp_array/max_amp)
            max_amp = data_amp_array.max()
            min_amp = data_amp_array.min()

        if self.coor_AUT_checkBox.isChecked() is True:
            aut_x_vec = self.x_vector.__sub__(self.x_zero_pos)
            aut_z_vec = self.z_vector.__sub__(self.z_zero_pos)
            xmeshv, ymeshv = self.gen_meshgrid_from_meas_points(aut_x_vec, aut_z_vec)
        else:
            # approach with mesh-data of numpy >> would need repositioning of mesh points since quadrilateral-corners
            # must be equally placed AROUND the measured spot which is not straight forward since we have coordinates
            # which describe the precise spot of measurement
            xmeshv, ymeshv = self.gen_meshgrid_from_meas_points(self.x_vector, self.z_vector)

        self.xz_axes, self.xz_phase_axes = self.xz_figure.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
        self.xz_axes.set_title("XZ-Plane Amplitude")
        self.xz_phase_axes.set_title("XZ-Plane Phase")
        self.xz_plot = self.xz_axes.pcolormesh(xmeshv, ymeshv, data_amp_array, cmap='Spectral_r', vmin=min_amp,
                                                            vmax=max_amp)
        self.xz_colorbar = self.xz_figure.colorbar(self.xz_plot, ax=self.xz_axes)
        self.xz_phase_plot = self.xz_phase_axes.pcolormesh(xmeshv, ymeshv, data_phase_array, cmap='Spectral_r')
        self.xz_phase_colorbar = self.xz_figure.colorbar(self.xz_phase_plot, ax=self.xz_phase_axes)
        self.xz_canvas.draw()

        return

    # noinspection PyUnreachableCode
    def update_yz_plane_plot(self, data_amp_array: np.ndarray, data_phase_array: np.ndarray):
        """
        Receives 2d array with amplitude values sorted so that x,y indexing of array fits to the measured points along
        Y and Z Axis.

        Evaluates itself if chamber coordinates should be displayed or AUT coordinates (internal checkbox in display
        window) and acts accordingly.

        e.g. At yvec[0], zvec[0] is data_amp_array[0,0]. At yvec[20], zvec[100] is data_amp_array[20,100] etc.
        """
        # delete current axis/plot
        self.yz_axes.remove()
        self.yz_colorbar.remove()
        self.yz_phase_axes.remove()
        self.yz_phase_colorbar.remove()

        # find min and max amplitude in given dataset to set up axis/colorbar
        max_amp = data_amp_array.max()
        min_amp = data_amp_array.min()

        # check if display value in dBmax is selected and convert data array if necessary
        if self.unit_display_comboBox.currentText() == "dBmax":
            data_amp_array = 10 * np.log10(data_amp_array / max_amp)
            max_amp = data_amp_array.max()
            min_amp = data_amp_array.min()

        if self.coor_AUT_checkBox.isChecked() is True:
            aut_y_vec = self.y_vector.__sub__(self.y_zero_pos)
            aut_z_vec = self.z_vector.__sub__(self.z_zero_pos)
            xmeshv, ymeshv = self.gen_meshgrid_from_meas_points(aut_y_vec, aut_z_vec)
        else:
            xmeshv, ymeshv = self.gen_meshgrid_from_meas_points(self.y_vector, self.z_vector)

        self.yz_axes, self.yz_phase_axes = self.yz_figure.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
        self.yz_axes.set_title("YZ-Plane Amplitude")
        self.yz_phase_axes.set_title("YZ-Plane Phase")
        self.yz_plot = self.yz_axes.pcolormesh(xmeshv, ymeshv, data_amp_array, cmap='Spectral_r', vmin=min_amp,
                                               vmax=max_amp)
        self.yz_colorbar = self.yz_figure.colorbar(self.yz_plot, ax=self.yz_axes)
        self.yz_phase_plot = self.yz_phase_axes.pcolormesh(xmeshv, ymeshv, data_phase_array, cmap='Spectral_r')
        self.yz_phase_colorbar = self.yz_figure.colorbar(self.yz_phase_plot, ax=self.yz_phase_axes)
        self.yz_canvas.draw()
        return

    # noinspection PyUnreachableCode
    def update_xy_plane_plot(self, data_amp_array: np.ndarray, data_phase_array: np.ndarray):
        """
        Receives 2d array with amplitude values sorted so that x,y indexing of array fits to the measured points along
        X and Y Axis.

        Evaluates itself if chamber coordinates should be displayed or AUT coordinates (internal checkbox in display
        window) and acts accordingly.

        e.g. At xvec[0], yvec[0] is data_amp_array[0,0]. At xvec[20], yvec[100] is data_amp_array[20,100] etc.
        """
        # delete current axis/plot
        self.xy_axes.remove()
        self.xy_colorbar.remove()
        self.xy_phase_axes.remove()
        self.xy_phase_colorbar.remove()

        # find min and max amplitude in given dataset to set up axis/colorbar
        max_amp = data_amp_array.max()
        min_amp = data_amp_array.min()

        # check if display value in dBmax is selected and convert data array if necessary
        if self.unit_display_comboBox.currentText() == "dBmax":
            data_amp_array = 10 * np.log10(data_amp_array / max_amp)
            max_amp = data_amp_array.max()
            min_amp = data_amp_array.min()

        if self.coor_AUT_checkBox.isChecked() is True:
            aut_x_vec = self.x_vector.__sub__(self.x_zero_pos)
            aut_y_vec = self.y_vector.__sub__(self.y_zero_pos)
            xmeshv, ymeshv = self.gen_meshgrid_from_meas_points(aut_x_vec, aut_y_vec)
        else:
            xmeshv, ymeshv = self.gen_meshgrid_from_meas_points(self.x_vector, self.y_vector)

        self.xy_axes, self.xy_phase_axes = self.xy_figure.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
        self.xy_axes.set_title("XY-Plane Amplitude")
        self.xy_phase_axes.set_title("XY-Plane Phase")
        self.xy_plot = self.xy_axes.pcolormesh(xmeshv, ymeshv, data_amp_array, cmap='Spectral_r', vmin=min_amp,
                                               vmax=max_amp)
        self.xy_colorbar = self.xy_figure.colorbar(self.xy_plot, ax=self.xy_axes)
        self.xy_phase_plot = self.xy_phase_axes.pcolormesh(xmeshv, ymeshv, data_phase_array, cmap='Spectral_r')
        self.xy_phase_colorbar = self.xy_figure.colorbar(self.xy_phase_plot, ax=self.xy_phase_axes)
        self.xy_canvas.draw()
        return



    @staticmethod
    def gen_meshgrid_from_meas_points(x_vec: np.ndarray, y_vec: np.ndarray):
        """
        Calucalates the stepsize within each vector. subtracts half a stepsize from each entry and adds a new point to
        the end of the vector. Thus, the resulting mesh has the described points by x_vec and y_vec in the center of
        each element.
        The resulting two arrays describe a mesh that has **as many elements as points** that were described in the
        beginning. Therefor, pcolormesh(X,Y,C,..) can be used handing a C-array that holds values for each element
        at the right index-pair [x, y].

        e.g. point describes by x_vec and y_vec:

          x--x--x
          |  |  |
          x--x--x

        becomes

         x--x--x--x
         |  |  |  |
         x--x--x--x
         |  |  |  |
         x--x--x--x

        with points from beginning  in center of each element.
        """
        x_stepsize = abs(x_vec[1] - x_vec[0])
        y_stepsize = abs(y_vec[1] - y_vec[0])

        new_x_vec = np.append(x_vec, x_vec[-1] + x_stepsize)
        new_y_vec = np.append(y_vec, y_vec[-1] + y_stepsize)

        new_x_vec = new_x_vec.__sub__(x_stepsize/2)
        new_y_vec = new_y_vec.__sub__(y_stepsize/2)

        xm_vec, ym_vec = np.meshgrid(new_x_vec, new_y_vec, indexing='ij')

        return xm_vec, ym_vec

