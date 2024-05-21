import sys
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QGridLayout, \
    QFrame, QComboBox, QStackedWidget, QProgressBar
from PyQt6.QtCore import QCoreApplication, Qt
from datetime import datetime
from PythonChamberApp.user_interface.ui_3d_visualizer import VisualizerPyqtGraph as Visualizer
import pyqtgraph as pg
import numpy as np
import pyqtgraph.opengl as gl


class UI_auto_measurement_window(QWidget):
    # Properties
    # Chamber workspace properties to display possible inputs in UI
    chamber_x_max_coor: float = None
    chamber_y_max_coor: float = None
    chamber_z_max_coor: float = None
    chamber_z_head_bed_offset: float = None
    current_zero_x: float = None
    current_zero_y: float = None
    current_zero_z: float = None

    #   antenna_info_inputs_field
    probe_antenna_length_lineEdit: QLineEdit = None
    aut_height_lineEdit: QLineEdit = None
    auto_measurement_jogSpeed_lineEdit: QLineEdit = None
    #   > fit_coordinate_systems_interface
    button_set_z_zero_from_antennas: QPushButton = None
    button_move_to_zero: QPushButton = None  # coordinate at which AUT and Probe antenna are aligned
    button_set_current_as_zero: QPushButton = None
    label_show_current_position: QLabel = None
    label_show_current_zero: QLabel = None

    #   measurement_mesh_config_field
    stacked_mesh_config_widget: QStackedWidget = None
    #   > cubic mesh [1]
    mesh_cubic_x_length_lineEdit: QLineEdit = None
    mesh_cubic_x_max_length_label: QLabel = None
    mesh_cubic_x_num_of_steps_lineEdit: QLineEdit = None
    mesh_cubic_y_length_lineEdit: QLineEdit = None
    mesh_cubic_y_max_length_label: QLabel = None
    mesh_cubic_y_num_of_steps_lineEdit: QLineEdit = None
    mesh_cubic_z_start_lineEdit: QLineEdit = None
    mesh_cubic_z_stop_lineEdit: QLineEdit = None
    mesh_cubic_z_max_distance_label: QLabel = None
    mesh_cubic_z_num_of_steps_lineEdit: QLineEdit = None
    #   > cylindrical mesh [2]
    mesh_cylindrical_radius_lineEdit: QLineEdit = None
    mesh_cylindrical_radius_num_of_steps: QLineEdit = None
    mesh_cylindrical_degree_num_of_steps: QLineEdit = None
    mesh_cylindrical_z_start_lineEdit: QLineEdit = None
    mesh_cylindrical_z_stop_lineEdit: QLineEdit = None
    mesh_cylindrical_z_num_of_steps_lineEdit: QLineEdit = None
    #   > more to come... [3]

    #   vna_measurement_config_field
    vna_freq_start_lineEdit: QLineEdit = None
    vna_freq_stop_lineEdit: QLineEdit = None
    vna_freq_num_steps_lineEdit: QLineEdit = None

    #   measurement_data_config_field

    #   start auto measurement button
    auto_measurement_start_button: QPushButton = None

    #   auto measurement progress frame
    meas_progress_points_in_layer: QLabel = None   # Number of points to measure in current layer
    meas_progress_current_point_in_layer: QLabel = None
    meas_progress_in_layer_progressBar: QProgressBar = None
    meas_progress_layer_max_count: QLabel = None
    meas_progress_layer_current: QLabel = None
    meas_progress_layer_progressBar: QProgressBar = None
    meas_progress_total_point_max_count: QLabel = None
    meas_progress_total_point_current: QLabel = None
    meas_progress_total_point_progressBar: QProgressBar = None
    meas_progress_status_label: QLabel = None

    #   3d graph visualization of mesh
    graphic_bed_obj: gl.GLMeshItem = None
    graphic_measurement_mesh_obj: gl.GLScatterPlotItem = None
    graphic_probe_antenna_obj: gl.GLLinePlotItem = None
    __probe_antenna_obj_width: float = 20.0
    graphic_aut_obj: gl.GLLinePlotItem = None
    __aut_obj_width: float = 60.0

    #   2d graph visualization of mesh
    plot_2d_layout_widget: pg.GraphicsLayoutWidget = None
    plot_2d_xy: pg.PlotItem = None
    plot_xy_zero_cos: pg.PlotDataItem = None
    plot_xy_mesh_points: pg.PlotDataItem
    plot_2d_yz: pg.PlotItem = None
    plot_yz_zero_cos: pg.PlotDataItem = None
    plot_yz_mesh_points: pg.PlotDataItem = None

    def __init__(self, chamber_x_max_coor: float, chamber_y_max_coor: float, chamber_z_max_coor: float,
                 chamber_z_head_bed_offset: float):
        super().__init__()
        self.chamber_x_max_coor = chamber_x_max_coor
        self.chamber_y_max_coor = chamber_y_max_coor
        self.chamber_z_max_coor = chamber_z_max_coor
        self.chamber_z_head_bed_offset = chamber_z_head_bed_offset

        self.label_show_current_position = QLabel("Current Position >> Not initialized")
        self.label_show_current_zero = QLabel("Current Zero >> Not initialized")

        main_layout = QHBoxLayout()

        #   first column - from left ...
        first_column = QVBoxLayout()
        probe_antenna_inputs_frame_widget = self.__init_antenna_info_inputs_widget()
        measurement_mesh_config_widget = self.__init_measurement_mesh_config_widget()
        first_column.addWidget(probe_antenna_inputs_frame_widget)
        first_column.addWidget(measurement_mesh_config_widget)

        second_column = QVBoxLayout()
        vna_measurement_config_widget = self.__init_vna_measurement_config_widget()
        measurement_data_config_widget = self.__init_measurement_data_config_widget()
        self.auto_measurement_start_button = QPushButton("Start Auto Measurement Process")
        second_column.addWidget(vna_measurement_config_widget)
        second_column.addWidget(measurement_data_config_widget)
        second_column.addWidget(self.auto_measurement_start_button, alignment=Qt.AlignmentFlag.AlignBottom)
        # ...

        third_column = QVBoxLayout()
        auto_measurement_progress_widget = self.__init_auto_measurement_progress_widget()
        auto_measurement_progress_widget.setFixedHeight(150)
        view_widget = self.__init_3d_graphic()
        self.view_widget_status_label = QLabel("Mesh-display initialized! Display updates once 'Zero Position' defined...")
        view_widget_status_label_holder = QWidget()
        view_widget_status_label_holder.setFixedHeight(30)
        view_widget_status_label_holder_layout = QHBoxLayout()
        view_widget_status_label_holder.setLayout(view_widget_status_label_holder_layout)
        view_widget_status_label_holder_layout.addWidget(self.view_widget_status_label, alignment=Qt.AlignmentFlag.AlignLeft)
        third_column.addWidget(auto_measurement_progress_widget, alignment=Qt.AlignmentFlag.AlignTop)
        third_column.addWidget(view_widget, stretch=1)
        third_column.addWidget(view_widget_status_label_holder)

        fourth_column = QVBoxLayout()
        self.plot_2d_layout_widget = self.__init_2d_plots()
        self.plot_2d_layout_widget.setMinimumWidth(300)
        fourth_column.addWidget(self.plot_2d_layout_widget)

        main_layout.addLayout(first_column, stretch=0)
        main_layout.addLayout(second_column, stretch=0)
        main_layout.addLayout(third_column, stretch=1)
        main_layout.addLayout(fourth_column, stretch=1)
        self.setLayout(main_layout)

        # Disable functionality that needs homed chamber
        #self.disable_chamber_move_interaction()     #ToDo disable all chamber movements in the beginning when debugging finished

    def __init_antenna_info_inputs_widget(self):
        antenna_info_inputs_frame = QFrame()
        antenna_info_inputs_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        antenna_info_inputs_frame.setContentsMargins(5, 5, 5, 5)
        antenna_info_inputs_frame.setMaximumWidth(300)
        frame_layout = QGridLayout()
        antenna_info_inputs_frame.setLayout(frame_layout)

        main_label = QLabel("1. Antenna Info")
        main_label.setStyleSheet("text-decoration: underline; font-size: 16px; font-weight: bold;")
        frame_layout.addWidget(main_label, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        probe_antenna_inputs_title_label = QLabel("Probe Antenna")
        probe_antenna_inputs_title_label.setStyleSheet("text-decoration: underline; font-size: 14px;")
        frame_layout.addWidget(probe_antenna_inputs_title_label, 1, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)
        probe_antenna_length_label = QLabel("Antenna Length:")
        self.probe_antenna_length_lineEdit = QLineEdit('050.00')
        self.probe_antenna_length_lineEdit.setInputMask('000.00')
        self.probe_antenna_length_lineEdit.setToolTip("Put in the length in Z-direction from the bottom of the "
                                                      "ProbeHead to the end of the chosen Probe Antenna in [mm]")
        probe_antenna_length_label_unit = QLabel(" [mm]")
        frame_layout.addWidget(probe_antenna_length_label, 2, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(self.probe_antenna_length_lineEdit, 2, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(probe_antenna_length_label_unit, 2, 2, 1, 1, Qt.AlignmentFlag.AlignLeft)

        #   AUT inputs
        aut_inputs_title_label = QLabel("Antenna Under Test")
        aut_inputs_title_label.setStyleSheet("text-decoration: underline; font-size: 14px;")
        frame_layout.addWidget(aut_inputs_title_label, 3, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)
        aut_height_label = QLabel("Antenna Height:")
        self.aut_height_lineEdit = QLineEdit('050.00')
        self.aut_height_lineEdit.setInputMask('000.00')
        self.aut_height_lineEdit.setToolTip("Put in the height of the AUT from the base plate (print bed) to "
                                            "its highest point in [mm].")
        aut_height_label_unit = QLabel(" [mm]")
        frame_layout.addWidget(aut_height_label, 4, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(self.aut_height_lineEdit, 4, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(aut_height_label_unit, 4, 2, 1, 1, Qt.AlignmentFlag.AlignLeft)

        self.button_set_z_zero_from_antennas = QPushButton("Set Zero Z-Coor from antenna-dimensions")
        self.button_set_z_zero_from_antennas.setToolTip("Calculates theoretical Zero position by sum of both antenna\n"
                                                        "heights while considering the coordinate offset due to "
                                                        "z-homing-sensor")
        self.button_set_z_zero_from_antennas.pressed.connect(self.__update_2d_plots)
        self.button_set_z_zero_from_antennas.pressed.connect(self.update_mesh_display)
        frame_layout.addWidget(self.button_set_z_zero_from_antennas, 5, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        #   Align Antennas
        align_antennas_title_label = QLabel("Antenna Alignment")
        align_antennas_title_label.setStyleSheet("text-decoration: underline; font-size: 14px;")
        frame_layout.addWidget(align_antennas_title_label, 6, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)
        auto_measurement_jogSpeed_label = QLabel("Jogspeed AutoMeas:")
        auto_measurement_jogSpeed_label_unit = QLabel(" [mm/s]")
        self.button_move_to_zero = QPushButton("Go over Zero")
        self.button_move_to_zero.setToolTip("Moves probe antenna to stored 'Zero Position' with +10mm Z-Offset."
                                            "\nFrom here adjust position via chamber control tab to get to real "
                                            "'Zero Position'. Then store position as new Zero.")
        self.button_set_current_as_zero = QPushButton("Set current as Zero")
        self.button_set_current_as_zero.setToolTip("Set 'Zero Position' when probe antenna is located above XY center "
                                                   "of AUT\nand the end of the probe antenna is virtually touching the "
                                                   "top of the AUT\nconsidering Z-direction.")
        self.auto_measurement_jogSpeed_lineEdit = QLineEdit("10")
        frame_layout.addWidget(auto_measurement_jogSpeed_label, 7, 0, 1, 1)
        frame_layout.addWidget(self.auto_measurement_jogSpeed_lineEdit, 7, 1, 1, 1)
        frame_layout.addWidget(auto_measurement_jogSpeed_label_unit, 7, 2, 1, 1)
        frame_layout.addWidget(self.button_move_to_zero, 8, 0, 1, 1)
        frame_layout.addWidget(self.button_set_current_as_zero, 8, 1, 1, 2)
        frame_layout.addWidget(self.label_show_current_position, 9, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(self.label_show_current_zero, 10, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)

        return antenna_info_inputs_frame

    def __init_measurement_mesh_config_widget(self):
        measurement_mesh_config_frame = QFrame()
        measurement_mesh_config_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        measurement_mesh_config_frame.setContentsMargins(5, 5, 5, 5)
        measurement_mesh_config_frame.setMaximumWidth(300)
        frame_layout = QVBoxLayout()
        measurement_mesh_config_frame.setLayout(frame_layout)

        main_label = QLabel("2. Mesh Configuration")
        main_label.setStyleSheet("text-decoration: underline; font-size: 16px; font-weight: bold;")
        frame_layout.addWidget(main_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        #   Setup stacked widget to support different meshes
        self.stacked_mesh_config_widget = QStackedWidget()
        #   cubic mesh [1]
        cubic_mesh_config_widget = QWidget()
        cubic_mesh_config_widget_layout = QGridLayout()
        cubic_mesh_config_widget.setLayout(cubic_mesh_config_widget_layout)

        cubic_x_length_label = QLabel("Length in X:")
        self.mesh_cubic_x_length_lineEdit = QLineEdit("100")
        self.mesh_cubic_x_length_lineEdit.setToolTip(
            "Measurement Volume length in X in [mm].\nSymmetric around X-center of AUT.")
        self.mesh_cubic_x_max_length_label = QLabel(str("< max " + str(self.chamber_x_max_coor) + " mm"))
        cubic_x_num_of_steps_label = QLabel("Num of Steps:")
        self.mesh_cubic_x_num_of_steps_lineEdit = QLineEdit("10")

        cubic_y_length_label = QLabel("Length in Y:")
        self.mesh_cubic_y_length_lineEdit = QLineEdit("100")
        self.mesh_cubic_y_length_lineEdit.setToolTip(
            "Measurement Volume length in Y in [mm].\nSymmetric around Y-center of AUT.")
        self.mesh_cubic_y_max_length_label = QLabel(str("< max " + str(self.chamber_y_max_coor) + " mm"))
        cubic_y_num_of_steps_label = QLabel("Num of Steps:")
        self.mesh_cubic_y_num_of_steps_lineEdit = QLineEdit("10")

        cubic_z_start_label = QLabel("Start distance Z:")
        cubic_z_start_label_hint = QLabel("> 0 mm")
        cubic_z_stop_label = QLabel("Stop distance Z:")
        cubic_z_num_of_steps_label = QLabel("Num of Steps:")
        self.mesh_cubic_z_start_lineEdit = QLineEdit("200")
        self.mesh_cubic_z_start_lineEdit.setToolTip("Start-distance from AUT for measurement volume in [mm].")
        self.mesh_cubic_z_stop_lineEdit = QLineEdit("700")
        self.mesh_cubic_z_stop_lineEdit.setToolTip("Maximum distance from AUT for measurement volume in [mm]")
        self.mesh_cubic_z_max_distance_label = QLabel(
            str("< max " + str(self.chamber_z_max_coor - float(self.probe_antenna_length_lineEdit.text())) + " mm"))
        self.mesh_cubic_z_num_of_steps_lineEdit = QLineEdit("50")
        #   X inputs
        cubic_mesh_config_widget_layout.addWidget(cubic_x_length_label, 0, 0, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_x_length_lineEdit, 0, 1, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_x_max_length_label, 0, 2, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(cubic_x_num_of_steps_label, 1, 0, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_x_num_of_steps_lineEdit, 1, 1, 1, 1)
        #   Y inputs
        cubic_mesh_config_widget_layout.addWidget(cubic_y_length_label, 2, 0, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_y_length_lineEdit, 2, 1, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_y_max_length_label, 2, 2, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(cubic_y_num_of_steps_label, 3, 0, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_y_num_of_steps_lineEdit, 3, 1, 1, 1)
        #   Z inputs
        cubic_mesh_config_widget_layout.addWidget(cubic_z_start_label, 4, 0, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_z_start_lineEdit, 4, 1, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(cubic_z_start_label_hint, 4, 2, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(cubic_z_stop_label, 5, 0, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_z_stop_lineEdit, 5, 1, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_z_max_distance_label, 5, 2, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(cubic_z_num_of_steps_label, 6, 0, 1, 1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_z_num_of_steps_lineEdit, 6, 1, 1, 1)

        #   cylindrical mesh [2]
        cylindrical_mesh_config_widget = QWidget()
        cylindrical_mesh_config_widget_layout = QGridLayout()
        cylindrical_mesh_config_widget.setLayout(cylindrical_mesh_config_widget_layout)

        cylindrical_mark = QLabel("cylindrical")
        cylindrical_mesh_config_widget_layout.addWidget(cylindrical_mark)

        #   more to come...
        more_to_come_widget = QLabel("more to come...")

        #   Assemble stacked Widget (watch out for order!)
        self.stacked_mesh_config_widget.addWidget(cubic_mesh_config_widget)  # [1]
        self.stacked_mesh_config_widget.addWidget(cylindrical_mesh_config_widget)  # [2]
        self.stacked_mesh_config_widget.addWidget(more_to_come_widget)  # [3] end!

        #   create & add Dropdown to select a mesh-option
        mesh_selection_dropdown = QComboBox()
        mesh_selection_dropdown.addItems([
            'cubic mesh',
            'cylindrical mesh',
            'more to come...'
        ])
        mesh_selection_dropdown.currentIndexChanged.connect(self.__switch_mesh_config)
        mesh_selection_dropdown.setCurrentIndex(0)  # select cubic by default

        #   Add dropdown and stacked widget to measurement_mesh_config_frame
        frame_layout.addWidget(mesh_selection_dropdown)
        frame_layout.addWidget(self.stacked_mesh_config_widget)

        #   Connect Signals & Slots to update maximum input labels
        self.probe_antenna_length_lineEdit.editingFinished.connect(self.update_mesh_max_input_labels)
        self.aut_height_lineEdit.editingFinished.connect(self.update_mesh_max_input_labels)
        #   Connect Signals & Slots to update 2d plots when mesh input changed
        self.mesh_cubic_x_length_lineEdit.editingFinished.connect(self.__update_2d_plots)
        self.mesh_cubic_x_num_of_steps_lineEdit.editingFinished.connect(self.__update_2d_plots)
        self.mesh_cubic_y_length_lineEdit.editingFinished.connect(self.__update_2d_plots)
        self.mesh_cubic_y_num_of_steps_lineEdit.editingFinished.connect(self.__update_2d_plots)
        self.mesh_cubic_z_start_lineEdit.editingFinished.connect(self.__update_2d_plots)
        self.mesh_cubic_z_stop_lineEdit.editingFinished.connect(self.__update_2d_plots)
        self.mesh_cubic_z_num_of_steps_lineEdit.editingFinished.connect(self.__update_2d_plots)
        self.mesh_cubic_x_length_lineEdit.editingFinished.connect(self.update_mesh_display)
        self.mesh_cubic_x_num_of_steps_lineEdit.editingFinished.connect(self.update_mesh_display)
        self.mesh_cubic_y_length_lineEdit.editingFinished.connect(self.update_mesh_display)
        self.mesh_cubic_y_num_of_steps_lineEdit.editingFinished.connect(self.update_mesh_display)
        self.mesh_cubic_z_start_lineEdit.editingFinished.connect(self.update_mesh_display)
        self.mesh_cubic_z_stop_lineEdit.editingFinished.connect(self.update_mesh_display)
        self.mesh_cubic_z_num_of_steps_lineEdit.editingFinished.connect(self.update_mesh_display)

        return measurement_mesh_config_frame

    def __switch_mesh_config(self, index):
        self.stacked_mesh_config_widget.setCurrentIndex(index)

    def __init_vna_measurement_config_widget(self):
        vna_measurement_config_frame = QFrame()
        vna_measurement_config_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        vna_measurement_config_frame.setContentsMargins(5, 5, 5, 5)
        vna_measurement_config_frame.setFixedSize(300, 150)
        frame_layout = QGridLayout()
        vna_measurement_config_frame.setLayout(frame_layout)

        main_label = QLabel("3. VNA Configuration")
        main_label.setStyleSheet("text-decoration: underline; font-size: 16px; font-weight: bold;")
        frame_layout.addWidget(main_label, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        return vna_measurement_config_frame

    def __init_measurement_data_config_widget(self):
        measurement_data_config_frame = QFrame()
        measurement_data_config_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        measurement_data_config_frame.setContentsMargins(5, 5, 5, 5)
        measurement_data_config_frame.setFixedSize(300, 150)
        frame_layout = QGridLayout()
        measurement_data_config_frame.setLayout(frame_layout)

        main_label = QLabel("4. Data Management")
        main_label.setStyleSheet("text-decoration: underline; font-size: 16px; font-weight: bold;")
        frame_layout.addWidget(main_label, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        return measurement_data_config_frame

    def __init_auto_measurement_progress_widget(self):
        frame_widget = QFrame()
        frame_widget.setFrameShape(QFrame.Shape.Box)  # Set the frame shape
        frame_widget.setFrameShadow(QFrame.Shadow.Raised)  # Set the frame shadow
        frame_widget.setLineWidth(2)  # Set the width of the frame line
        frame_widget.setStyleSheet("background-color: lightGray;")  # Set frame background color
        frame_widget.setContentsMargins(5, 5, 5, 5)

        frame_layout = QGridLayout()
        frame_widget.setLayout(frame_layout)
        title = QLabel("Auto Measurement Progress")
        title.setStyleSheet("text-decoration: underline; font-size: 16px;")
        frame_layout.addWidget(title, 0,0,1,6, alignment=Qt.AlignmentFlag.AlignCenter)
        curr_point_in_layer_label = QLabel("Current Point in Layer:")
        curr_layer_label = QLabel("Current Layer:")
        curr_point_total_label = QLabel("Total Progress Point-wise:")
        curr_status_label = QLabel("Status:")
        frame_layout.addWidget(curr_point_in_layer_label,1,0,1,1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(curr_layer_label,2,0,1,1,alignment=Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(curr_point_total_label,3,0,1,1,alignment=Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(curr_status_label,4,0,1,1,alignment=Qt.AlignmentFlag.AlignLeft)

        self.meas_progress_points_in_layer = QLabel("0")
        self.meas_progress_current_point_in_layer = QLabel("0")
        self.meas_progress_in_layer_progressBar = QProgressBar()
        self.meas_progress_layer_max_count = QLabel("0")
        self.meas_progress_layer_current = QLabel("0")
        self.meas_progress_layer_progressBar = QProgressBar()
        self.meas_progress_total_point_max_count = QLabel("0")
        self.meas_progress_total_point_current = QLabel("0")
        self.meas_progress_total_point_progressBar = QProgressBar()
        self.meas_progress_status_label = QLabel("Not started...")

        backslash1 = QLabel("/")
        backslash2 = QLabel("/")
        backslash3 = QLabel("/")

        frame_layout.addWidget(self.meas_progress_current_point_in_layer, 1,1,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(backslash1,1,2,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_points_in_layer,1,3,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_in_layer_progressBar,1,4,1,2,alignment=Qt.AlignmentFlag.AlignLeft)

        frame_layout.addWidget(self.meas_progress_layer_current,2,1,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(backslash2,2,2,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_layer_max_count,2,3,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_layer_progressBar,2,4,1,2,alignment=Qt.AlignmentFlag.AlignLeft)

        frame_layout.addWidget(self.meas_progress_total_point_current,3,1,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(backslash3,3,2,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_total_point_max_count,3,3,1,1,alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_total_point_progressBar,3,4,1,2,alignment=Qt.AlignmentFlag.AlignLeft)

        frame_layout.addWidget(self.meas_progress_status_label,4,1,1,5, alignment=Qt.AlignmentFlag.AlignLeft)

        return frame_widget

    def __init_3d_graphic(self):
        view_widget = gl.GLViewWidget()
        view_widget.setBackgroundColor("d")


        #   start graphic properties
        start_position_x = self.chamber_x_max_coor / 2
        start_position_y = self.chamber_y_max_coor / 2
        start_position_z = 150.0

        #   Print bed
        self.graphic_bed_object = Visualizer.generate_3d_chamber_print_bed_obj(self.chamber_x_max_coor,
                                                                               self.chamber_y_max_coor,
                                                                               self.chamber_z_max_coor,
                                                                               self.chamber_z_head_bed_offset)
        self.graphic_bed_object.translate(dx=0, dy=0, dz=-start_position_z)
        view_widget.addItem(self.graphic_bed_object)

        #   Workspace Chamber
        chamber_workspace = Visualizer.generate_3d_chamber_workspace(self.chamber_x_max_coor, self.chamber_y_max_coor,
                                                                     self.chamber_z_max_coor,
                                                                     self.chamber_z_head_bed_offset)
        view_widget.addItem(chamber_workspace)

        #   Probe antenna Dummy
        self.graphic_probe_antenna_obj = Visualizer.generate_3d_antenna_object(self.get_probe_antenna_length(),
                                                                               self.__probe_antenna_obj_width, False)
        self.graphic_probe_antenna_obj.translate(dx=start_position_x, dy=start_position_y,
                                                 dz=self.chamber_z_head_bed_offset)
        view_widget.addItem(self.graphic_probe_antenna_obj)

        #   AUT Dummy
        self.graphic_aut_obj = Visualizer.generate_3d_antenna_object(self.get_aut_height(), self.__aut_obj_width, True)
        self.graphic_aut_obj.translate(dx=start_position_x, dy=start_position_y, dz=-start_position_z)
        view_widget.addItem(self.graphic_aut_obj)

        #   COS at 0,0,0
        cos = gl.GLAxisItem()
        cos.setSize(x=50, y=50, z=50)
        view_widget.addItem(cos)

        #   meas-scatter-plot
        x_vec = np.array([250])
        y_vec = np.array([250])
        z_vec = np.array([-100])
        self.graphic_measurement_mesh_obj = Visualizer.generate_3d_mesh_scatter_plot(x_vec, y_vec, z_vec)
        view_widget.addItem(self.graphic_measurement_mesh_obj)

        # set view point roughly
        view_widget.pan(self.chamber_x_max_coor / 2, self.chamber_y_max_coor / 2, -self.chamber_z_max_coor / 3)
        view_widget.setCameraPosition(distance=1200)

        return view_widget

    def __init_2d_plots(self):
        """
        Draws default graph to self.plot_2d_xy and self.plot_2d_xz
        """
        graph_layout_widget = pg.GraphicsLayoutWidget(title='2D View of Mesh in Chamber COS')
        graph_layout_widget.setBackground(background=(255, 255, 255))
        label_pen = pg.mkPen(color='k', width=1)

        x_axis = pg.AxisItem(orientation='left', text='X [mm]', textPen=label_pen)
        x_axis.setGrid(125)
        x_axis.showLabel()
        y_axis_xy = pg.AxisItem(orientation='top', text='Y [mm]', textPen=label_pen)
        y_axis_xy.setGrid(125)
        y_axis_xy.showLabel()
        y_axis_yz = pg.AxisItem(orientation='top', text='Y [mm]', textPen=label_pen)
        y_axis_yz.setGrid(125)
        y_axis_yz.showLabel()
        z_axis = pg.AxisItem(orientation='left', text='Z [mm]', textPen=label_pen)
        z_axis.setGrid(125)
        z_axis.showLabel()

        xy_workspace_vertices = np.array([[0.0, 0.0], [self.chamber_x_max_coor, 0.0],
                                 [self.chamber_x_max_coor, self.chamber_y_max_coor], [0.0, self.chamber_y_max_coor],
                                 [0, 0]])
        xy_workspace_lines_connect = np.array([[0, 1], [1, 2], [2, 3], [3, 0]])
        xy_workspace_plot = pg.GraphItem(pos=xy_workspace_vertices, adj=xy_workspace_lines_connect, pen='r', symbolPen='r', symbolBrush=None, symbol='+')

        yz_workspace_vertices = np.array([
            [0, -self.chamber_z_head_bed_offset], [0, 0], [0, self.chamber_z_max_coor],
            [self.chamber_y_max_coor, self.chamber_z_max_coor], [self.chamber_y_max_coor, 0],
            [self.chamber_y_max_coor, -self.chamber_z_head_bed_offset]
        ])
        yz_workspace_lines_connect = np.array([[0,1],[1,2],[2,3],[3,4],[4,5],[0,5],[1,4]])
        yz_workspace_plot = pg.GraphItem(pos=yz_workspace_vertices, adj=yz_workspace_lines_connect, pen='r', symbolPen='r', symbolBrush=None, symbol='+')

        # build xy plot --> Graph-x-axis is positive Chamber-Y-axis | Graph-y-axis is negative Chamber-x-axis
        self.plot_2d_xy = pg.PlotItem()
        graph_layout_widget.addItem(self.plot_2d_xy, 0, 0)
        self.plot_2d_xy.setTitle(title='XY-TopView on Mesh', color='k')
        self.plot_2d_xy.setAxisItems(axisItems={'left': x_axis, 'top': y_axis_xy})
        self.plot_2d_xy.hideAxis('bottom')
        self.plot_2d_xy.getViewBox().invertY(True)
        self.plot_2d_xy.getViewBox().setRange(xRange=(0, self.chamber_y_max_coor), yRange=(0, self.chamber_x_max_coor))
        self.plot_2d_xy.getViewBox().setAspectLocked(lock=True, ratio=1)
        self.plot_2d_xy.addItem(xy_workspace_plot)

        # build yz plot
        self.plot_2d_yz = pg.PlotItem()
        graph_layout_widget.addItem(self.plot_2d_yz, 1, 0)
        self.plot_2d_yz.setTitle('YZ-SideView on Mesh', color='k')
        self.plot_2d_yz.setAxisItems(axisItems={'left': z_axis, 'top': y_axis_yz})
        y_axis_xy.linkToView(self.plot_2d_xy.getViewBox())
        self.plot_2d_yz.getViewBox().invertY(True)
        self.plot_2d_yz.getViewBox().setRange(xRange=(0, self.chamber_y_max_coor), yRange=(0, self.chamber_z_max_coor))
        self.plot_2d_yz.getViewBox().setAspectLocked(lock=True, ratio=2)
        self.plot_2d_yz.addItem(yz_workspace_plot)
        self.plot_2d_yz.getViewBox().setXLink(self.plot_2d_xy.getViewBox())

        zero_cos_pen = pg.mkPen(color=(0, 0, 255), width=1)
        self.plot_xy_zero_cos = pg.PlotDataItem(symbol='s', symbolPen=zero_cos_pen)
        self.plot_yz_zero_cos = pg.PlotDataItem(symbol='s', symbolPen=zero_cos_pen)

        mesh_pen = pg.mkPen(color=(10, 255, 10), width=2)
        self.plot_xy_mesh_points = pg.PlotDataItem(symbol='o', symbolPen=mesh_pen, symbolSize=2, pen=None)
        self.plot_yz_mesh_points = pg.PlotDataItem(symbol='o', symbolPen=mesh_pen, symbolSize=2, pen=None)

        self.plot_2d_xy.addItem(self.plot_xy_zero_cos)
        self.plot_2d_yz.addItem(self.plot_yz_zero_cos)
        self.plot_2d_xy.addItem(self.plot_xy_mesh_points)
        self.plot_2d_yz.addItem(self.plot_yz_mesh_points)

        #   default values
        self.__update_2d_plots()
        return graph_layout_widget



    def __update_2d_plots(self):
        """
        Updates mesh points according to given mesh inputs
        > So far only cubic supported
        > skips update if no zero position is logged completely
        """
        #   skip update if no zero position logged
        if self.current_zero_x is None or self.current_zero_y is None or self.current_zero_z is None:
            return
        #   update zero positions in plot
        xy_zero = np.array([[self.current_zero_x, self.current_zero_y]])
        yz_zero = np.array([[self.current_zero_y, self.current_zero_z]])
        self.plot_xy_zero_cos.setData(xy_zero)
        self.plot_yz_zero_cos.setData(yz_zero)
        #   update mesh points
        mesh_info = self.get_mesh_cubic_data()
        xy_mesh_points_list = []
        for x in mesh_info['x_vec']:
            for y in mesh_info['y_vec']:
                xy_mesh_points_list.append([x, y])
        xy_mesh_points_array = np.array(xy_mesh_points_list)
        yz_mesh_points_list = []
        for y in mesh_info['y_vec']:
            for z in mesh_info['z_vec']:
                yz_mesh_points_list.append([y, z - self.get_aut_height()]) # correcting by head bed offset since bed coordinates are stored in z_vec
        yz_mesh_points_array = np.array(yz_mesh_points_list)
        self.plot_xy_mesh_points.setData(xy_mesh_points_array)
        self.plot_yz_mesh_points.setData(yz_mesh_points_array)



    def update_live_coor_display(self, new_x: float, new_y: float, new_z: float):
        """
        Updates live position displays in auto-measurement-tab
        """
        new_position_string = "Current Position >> X:" + str(new_x) + " Y:" + str(new_y) + " Z:" + str(new_z)
        self.label_show_current_position.setText(new_position_string)

    def update_current_zero_pos(self, new_x: float, new_y: float, new_z: float):
        """
        Updates display and buffer of current zero position.
        Initiates update of all max-input-labels in mesh_configurations_widgets.
        """
        self.current_zero_x = new_x
        self.current_zero_y = new_y
        self.current_zero_z = new_z

        new_zero_pos_label = "Current Zero >> X:" + str(new_x) + " Y:" + str(new_y) + " Z:" + str(new_z)
        self.label_show_current_zero.setText(new_zero_pos_label)

        self.update_mesh_max_input_labels()

    def update_mesh_max_input_labels(self):
        """
        Updates the Max-Value-labels in the mesh configuration widgets.
        For every mesh config that is added, this function must be adapted to calculate the resulting max inputs
        and update each widget!

        Draws information from class properties everytime the zero_pos is set or antenna info is updated.
        """
        # Update Cubic mesh max inputs
        min_x_distance2border = self.current_zero_x
        if self.current_zero_x > self.chamber_x_max_coor / 2:
            min_x_distance2border = self.chamber_x_max_coor - self.current_zero_x
        min_y_distance2border = self.current_zero_y
        if self.current_zero_y > self.chamber_y_max_coor / 2:
            min_y_distance2border = self.chamber_y_max_coor - self.current_zero_y
        min_z_distance2border = (self.chamber_z_max_coor - self.get_probe_antenna_length() -
                                 self.get_aut_height() + self.chamber_z_head_bed_offset)

        self.mesh_cubic_x_max_length_label.setText("< max " + str(2 * min_x_distance2border) + " mm")
        self.mesh_cubic_y_max_length_label.setText("< max " + str(2 * min_y_distance2border) + " mm")
        self.mesh_cubic_z_max_distance_label.setText("< max " + str(min_z_distance2border) + " mm")

        # Update cylindrical mesh max inputs

        # more to come...

    def update_mesh_display(self):
        """
        Callback that updates displayed mesh in graph-visualization dependent on configuration

        > skips update if no zero position is logged completely
        """
        #   skip update if no zero position logged
        if self.current_zero_x is None or self.current_zero_y is None or self.current_zero_z is None:
            return

        mesh_info = self.get_mesh_cubic_data()
        new_z_coor_chamber_movement = []
        real_z_measurement_mesh = []

        # flip z orientation for graph
        for nz in mesh_info['z_vec']:
            new_z_coor_chamber_movement.append(-nz)
        for nz in new_z_coor_chamber_movement:
            real_z_measurement_mesh.append(nz + self.get_aut_height())

        if mesh_info['tot_num_of_points'] < (51*51*51):
            # standard routine to display all points
            new_data = Visualizer.generate_point_list(mesh_info['x_vec'], mesh_info['y_vec'],
                                                      tuple(real_z_measurement_mesh))
        else:   # routine if too many points to display
            new_data = Visualizer.generate_outline_point_list(mesh_info['x_vec'], mesh_info['y_vec'],
                                                              tuple(real_z_measurement_mesh))

        self.graphic_measurement_mesh_obj.setData(pos=new_data)



        # set bed to lowest position for mesh
        lowest_z_mesh = -1*mesh_info['z_vec'][-1]
        self.graphic_bed_object.resetTransform()
        self.graphic_bed_object.translate(dx=0, dy=0, dz=lowest_z_mesh)

        probe_obj_vertices = Visualizer.generate_3d_antenna_object_vertices(self.get_probe_antenna_length(),
                                                                            self.__probe_antenna_obj_width, False)
        self.graphic_probe_antenna_obj.setData(pos=probe_obj_vertices)
        self.graphic_probe_antenna_obj.resetTransform()
        self.graphic_probe_antenna_obj.translate(dx=self.current_zero_x, dy=self.current_zero_y,
                                                 dz=self.chamber_z_head_bed_offset)

        aut_obj_vertices = Visualizer.generate_3d_antenna_object_vertices(self.get_aut_height(), self.__aut_obj_width,
                                                                          True)
        self.graphic_aut_obj.setData(pos=aut_obj_vertices)
        self.graphic_aut_obj.resetTransform()
        self.graphic_aut_obj.translate(dx=self.current_zero_x, dy=self.current_zero_y, dz=lowest_z_mesh)

    def update_auto_measurement_progress_state(self, state_info: dict):
        """
        Function receives state info dictionary and updates the gui display accordingly.
        expected state_info keywords are following:
         state_info: dict = {
            'total_points_in_measurement': int,

            'total_current_point_number': int,

            'num_of_layers_in_measurement': int,

            'current_layer_number': int,

            'num_of_points_in_current_layer': int,

            'current_point_number_in_layer': int,

            'status_flag': string (optional)
          }

        :param state_info: dictionary
        """
        num_of_points_in_current_layer = state_info['num_of_points_in_current_layer']
        current_point_number_in_layer = state_info['current_point_number_in_layer']
        num_of_layers_in_measurement = state_info['num_of_layers_in_measurement']
        current_layer_number = state_info['current_layer_number']
        total_points_in_measurement = state_info['total_points_in_measurement']
        total_current_point_number = state_info['total_current_point_number']

        self.meas_progress_points_in_layer.setText(str(num_of_points_in_current_layer))
        self.meas_progress_current_point_in_layer.setText(str(current_point_number_in_layer))
        self.meas_progress_in_layer_progressBar.setMinimum(0)
        self.meas_progress_in_layer_progressBar.setMaximum(num_of_points_in_current_layer)
        self.meas_progress_in_layer_progressBar.setValue(current_point_number_in_layer)

        self.meas_progress_layer_max_count.setText(str(num_of_layers_in_measurement))
        self.meas_progress_layer_current.setText(str(current_layer_number))
        self.meas_progress_layer_progressBar.setMinimum(0)
        self.meas_progress_layer_progressBar.setMaximum(num_of_layers_in_measurement)
        self.meas_progress_layer_progressBar.setValue(current_layer_number)

        self.meas_progress_total_point_max_count.setText(str(total_points_in_measurement))
        self.meas_progress_total_point_current.setText(str(total_current_point_number))
        self.meas_progress_total_point_progressBar.setMinimum(0)
        self.meas_progress_total_point_progressBar.setMaximum(total_points_in_measurement)
        self.meas_progress_total_point_progressBar.setValue(total_current_point_number)

        if 'status_flag' in state_info:
            self.meas_progress_status_label.setText(state_info['status_flag'])



    def get_mesh_cubic_data(self):
        """
        This function returns a dictionary that provides additional info about the measurement mesh.
        The x,y,z vectors describe the necessary points to move to by the chamber, to do the measurement.
        dict:
            {
            'tot_num_of_points' : int
            'num_steps_x' : int
            'num_steps_y' : int
            'num_steps_z' : int
            'x_vec' : tuple(float,...) , vector that stores all x coordinates for chamber movement in growing order
            'y_vec' : tuple(float,...) , vector that stores all y coordinates for chamber movement in growing order
            'z_vec' : tuple(float,...) , vector that stores all z coordinates for chamber movement in growing order
            }

        *Coordinates are already transferred to chamber-movement coordinate system based on set zero!*
        *When used for display measurement-mesh in graph, compensate the AUT-antenna-height of zero-position in [Z]!*
        """
        info_dict = {}
        #   get inputs
        x_length = float(self.mesh_cubic_x_length_lineEdit.text())
        x_num_steps = int(self.mesh_cubic_x_num_of_steps_lineEdit.text())
        y_length = float(self.mesh_cubic_y_length_lineEdit.text())
        y_num_steps = int(self.mesh_cubic_y_num_of_steps_lineEdit.text())
        z_start = float(self.mesh_cubic_z_start_lineEdit.text())
        z_stop = float(self.mesh_cubic_z_stop_lineEdit.text())
        z_num_steps = int(self.mesh_cubic_z_num_of_steps_lineEdit.text())

        #   get current zero
        x_offset = self.current_zero_x
        y_offset = self.current_zero_y
        z_offset = self.current_zero_z

        #   calculate coordinate vectors
        x_linspace = np.linspace(-x_length / 2, x_length / 2, x_num_steps)
        y_linspace = np.linspace(-y_length / 2, y_length / 2, y_num_steps)
        z_linspace = np.linspace(z_start, z_stop, z_num_steps)

        x_vec = []
        for i in x_linspace:
            x_vec.append(i + x_offset)
        y_vec = []
        for i in y_linspace:
            y_vec.append(i + y_offset)
        z_vec = []
        for i in z_linspace:
            z_vec.append(i + z_offset)

        #   fill info dict
        info_dict['tot_num_of_points'] = x_num_steps * y_num_steps * z_num_steps
        info_dict['num_steps_x'] = x_num_steps
        info_dict['num_steps_y'] = y_num_steps
        info_dict['num_steps_z'] = z_num_steps
        info_dict['x_vec'] = tuple(x_vec)
        info_dict['y_vec'] = tuple(y_vec)
        info_dict['z_vec'] = tuple(z_vec)

        return info_dict

    def get_probe_antenna_length(self):
        return float(self.probe_antenna_length_lineEdit.text())

    def get_aut_height(self):
        return float(self.aut_height_lineEdit.text())

    def get_auto_measurement_jogspeed(self):
        return float(self.auto_measurement_jogSpeed_lineEdit.text())

    def disable_chamber_move_interaction(self):
        """
        This function disables all buttons or similar that can move the chamber or use logged position.

        Disables
            > button move to zero
            > button set current position as zero
            > button start automeasurement
        """
        self.button_move_to_zero.setEnabled(False)
        self.button_set_current_as_zero.setEnabled(False)
        self.auto_measurement_start_button.setEnabled(False)

    def enable_chamber_move_interaction(self):
        """
        This function enables buttons on the UI window that can request movement from chamber.
        These functions are only valid once the chamber was homed and has a known, logged position!

        Enables
            > button move to zero
            > button set current position as zero
        """
        self.button_set_current_as_zero.setEnabled(True)
        self.button_move_to_zero.setEnabled(True)
