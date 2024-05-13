import sys
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QGridLayout, QFrame
from PyQt6.QtCore import QCoreApplication, Qt
from datetime import datetime

class UI_auto_measurement_window(QWidget):

    # Properties
    #   antenna_info_inputs_field
    probe_antenna_length_lineEdit: QLineEdit = None
    aut_height_lineEdit: QLineEdit = None

    #   fit_coordinate_systems_field
    button_move_to_zero: QPushButton = None     # coordinate at which AUT and Probe antenna ae aligned
    button_set_new_zero: QPushButton = None

    #   measurement_mesh_config_field
    mesh_x_length_lineEdit: QLineEdit = None
    mesh_x_num_of_steps_lineEdit: QLineEdit = None
    mesh_y_length_lineEdit: QLineEdit = None
    mesh_y_num_of_steps_lineEdit: QLineEdit = None
    mesh_z_start_lineEdit: QLineEdit = None
    mesh_z_stop_lineEdit: QLineEdit = None
    mesh_z_num_of_steps_lineEdit: QLineEdit = None

    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()

        #   Most Left column
        first_column = QVBoxLayout()
        probe_antenna_inputs_frame_widget = self.__init_antenna_info_inputs_widget()
        measurement_mesh_config_widget = self.__init_measurement_mesh_config_widget()
        first_column.addWidget(probe_antenna_inputs_frame_widget)
        first_column.addWidget(measurement_mesh_config_widget)

        second_column = QVBoxLayout()
        # ...
        second_column.addStretch()

        main_layout.addLayout(first_column)
        main_layout.addLayout(second_column)
        self.setLayout(main_layout)

    def __init_antenna_info_inputs_widget(self):
        antenna_info_inputs_frame = QFrame()
        antenna_info_inputs_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        antenna_info_inputs_frame.setContentsMargins(5, 5, 5, 5)
        antenna_info_inputs_frame.setFixedSize(300, 150)
        frame_layout = QGridLayout()
        antenna_info_inputs_frame.setLayout(frame_layout)

        main_label = QLabel("1. Antenna Info")
        main_label.setStyleSheet("text-decoration: underline; font-size: 16px;")
        frame_layout.addWidget(main_label,0,0,1,3,Qt.AlignmentFlag.AlignCenter)

        probe_antenna_inputs_title_label = QLabel("Probe Antenna")
        probe_antenna_inputs_title_label.setStyleSheet("text-decoration: underline; font-size: 14px;")
        frame_layout.addWidget(probe_antenna_inputs_title_label,1,0,1,3,Qt.AlignmentFlag.AlignLeft)
        probe_antenna_length_label = QLabel("Antenna Length:")
        self.probe_antenna_length_lineEdit = QLineEdit('000.00')
        self.probe_antenna_length_lineEdit.setInputMask('000.00')
        self.probe_antenna_length_lineEdit.setToolTip("Put in the length in Z-direction from the bottom of the "
                                                      "ProbeHead to the end of the chosen Probe Antenna in [mm]")
        probe_antenna_length_label_unit = QLabel(" [mm]")
        frame_layout.addWidget(probe_antenna_length_label,2,0,1,1,Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(self.probe_antenna_length_lineEdit,2,1,1,1,Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(probe_antenna_length_label_unit,2,2,1,1,Qt.AlignmentFlag.AlignLeft)

        #   AUT inputs
        aut_inputs_title_label = QLabel("Antenna Under Test")
        aut_inputs_title_label.setStyleSheet("text-decoration: underline; font-size: 14px;")
        frame_layout.addWidget(aut_inputs_title_label,3,0,1,3,Qt.AlignmentFlag.AlignLeft)
        aut_height_label = QLabel("Antenna Height:")
        self.aut_height_lineEdit = QLineEdit('060.00')
        self.aut_height_lineEdit.setInputMask('000.00')
        self.aut_height_lineEdit.setToolTip("Put in the height of the AUT from the base plate (print bed) in [mm].")
        aut_height_label_unit = QLabel(" [mm]")
        frame_layout.addWidget(aut_height_label,4,0,1,1,Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(self.aut_height_lineEdit,4,1,1,1,Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(aut_height_label_unit,4,2,1,1,Qt.AlignmentFlag.AlignLeft)

        return antenna_info_inputs_frame

    def __init_measurement_mesh_config_widget(self):
        measurement_mesh_config_frame = QFrame()
        measurement_mesh_config_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        measurement_mesh_config_frame.setContentsMargins(5, 5, 5, 5)
        measurement_mesh_config_frame.setFixedSize(300, 150)
        frame_layout = QGridLayout()
        measurement_mesh_config_frame.setLayout(frame_layout)

        main_label = QLabel("2. Measurement Mesh Configuration")
        main_label.setStyleSheet("text-decoration: underline; font-size: 16px;")
        frame_layout.addWidget(main_label, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        return measurement_mesh_config_frame

