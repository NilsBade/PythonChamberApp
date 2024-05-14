import sys
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QGridLayout, QFrame, QComboBox, QStackedWidget
from PyQt6.QtCore import QCoreApplication, Qt
from datetime import datetime

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
    button_move_to_zero: QPushButton = None     # coordinate at which AUT and Probe antenna are aligned
    button_set_new_zero: QPushButton = None
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


    def __init__(self, chamber_x_max_coor: float, chamber_y_max_coor: float, chamber_z_max_coor: float, chamber_z_head_bed_offset: float):
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
        second_column.addWidget(vna_measurement_config_widget)
        second_column.addWidget(measurement_data_config_widget)
        # ...

        third_column = QVBoxLayout()
        auto_measurement_progress_widget = QLabel("Here comes depiction of progress and mesh...")
        third_column.addWidget(auto_measurement_progress_widget)

        main_layout.addLayout(first_column, stretch=0)
        main_layout.addLayout(second_column, stretch=0)
        main_layout.addLayout(third_column, stretch=1)
        self.setLayout(main_layout)

    def __init_antenna_info_inputs_widget(self):
        antenna_info_inputs_frame = QFrame()
        antenna_info_inputs_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        antenna_info_inputs_frame.setContentsMargins(5, 5, 5, 5)
        antenna_info_inputs_frame.setMaximumWidth(300)
        frame_layout = QGridLayout()
        antenna_info_inputs_frame.setLayout(frame_layout)

        main_label = QLabel("1. Antenna Info")
        main_label.setStyleSheet("text-decoration: underline; font-size: 16px; font-weight: bold;")
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
        self.aut_height_lineEdit.setToolTip("Put in the height of the AUT from the base plate (print bed) to "
                                            "its highest point in [mm].")
        aut_height_label_unit = QLabel(" [mm]")
        frame_layout.addWidget(aut_height_label,4,0,1,1,Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(self.aut_height_lineEdit,4,1,1,1,Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(aut_height_label_unit,4,2,1,1,Qt.AlignmentFlag.AlignLeft)

        #   Align Antennas
        align_antennas_title_label = QLabel("Antenna Alignment")
        align_antennas_title_label.setStyleSheet("text-decoration: underline; font-size: 14px;")
        frame_layout.addWidget(align_antennas_title_label,5,0,1,3,Qt.AlignmentFlag.AlignLeft)
        auto_measurement_jogSpeed_label = QLabel("Jogspeed AutoMeas:")
        auto_measurement_jogSpeed_label_unit = QLabel(" [mm/s]")
        self.button_move_to_zero = QPushButton("Go to Zero")
        self.button_move_to_zero.setToolTip("Moves probe antenna to stored 'Zero Position'.\nFrom here adjust position "
                                            "via chamber control tab to get to real 'Zero Position'. "
                                            "Then store position as new Zero.")
        self.button_set_new_zero = QPushButton("Set current as Zero")
        self.button_set_new_zero.setToolTip("Set 'Zero Position' when probe antenna is located above XY center of AUT\n"
                                            "and the end of the probe antenna is virtually touching the top of the AUT\n"
                                            "considering Z-direction.")
        self.auto_measurement_jogSpeed_lineEdit = QLineEdit("10")
        frame_layout.addWidget(auto_measurement_jogSpeed_label,6,0,1,1)
        frame_layout.addWidget(self.auto_measurement_jogSpeed_lineEdit,6,1,1,1)
        frame_layout.addWidget(auto_measurement_jogSpeed_label_unit,6,2,1,1)
        frame_layout.addWidget(self.button_move_to_zero,7,0,1,1)
        frame_layout.addWidget(self.button_set_new_zero,7,1,1,2)
        frame_layout.addWidget(self.label_show_current_position,8,0,1,3,Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(self.label_show_current_zero,9,0,1,3,Qt.AlignmentFlag.AlignLeft)

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
        self.mesh_cubic_x_length_lineEdit.setToolTip("Measurement Volume length in X in [mm].\nSymmetric around X-center of AUT.")
        self.mesh_cubic_x_max_length_label = QLabel(str("< max " + str(self.chamber_x_max_coor) + " mm"))
        cubic_x_num_of_steps_label = QLabel("Num of Steps:")
        self.mesh_cubic_x_num_of_steps_lineEdit = QLineEdit("10")

        cubic_y_length_label = QLabel("Length in Y:")
        self.mesh_cubic_y_length_lineEdit = QLineEdit("100")
        self.mesh_cubic_y_length_lineEdit.setToolTip("Measurement Volume length in Y in [mm].\nSymmetric around Y-center of AUT.")
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
        self.mesh_cubic_z_max_distance_label = QLabel(str("< max " + str(self.chamber_z_max_coor - float(self.probe_antenna_length_lineEdit.text())) + " mm"))
        self.mesh_cubic_z_num_of_steps_lineEdit = QLineEdit("50")
        #   X inputs
        cubic_mesh_config_widget_layout.addWidget(cubic_x_length_label,0,0,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_x_length_lineEdit,0,1,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_x_max_length_label,0,2,1,1)
        cubic_mesh_config_widget_layout.addWidget(cubic_x_num_of_steps_label,1,0,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_x_num_of_steps_lineEdit,1,1,1,1)
        #   Y inputs
        cubic_mesh_config_widget_layout.addWidget(cubic_y_length_label,2,0,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_y_length_lineEdit,2,1,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_y_max_length_label,2,2,1,1)
        cubic_mesh_config_widget_layout.addWidget(cubic_y_num_of_steps_label,3,0,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_y_num_of_steps_lineEdit,3,1,1,1)
        #   Z inputs
        cubic_mesh_config_widget_layout.addWidget(cubic_z_start_label,4,0,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_z_start_lineEdit,4,1,1,1)
        cubic_mesh_config_widget_layout.addWidget(cubic_z_start_label_hint,4,2,1,1)
        cubic_mesh_config_widget_layout.addWidget(cubic_z_stop_label,5,0,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_z_stop_lineEdit,5,1,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_z_max_distance_label,5,2,1,1)
        cubic_mesh_config_widget_layout.addWidget(cubic_z_num_of_steps_label,6,0,1,1)
        cubic_mesh_config_widget_layout.addWidget(self.mesh_cubic_z_num_of_steps_lineEdit,6,1,1,1)

        #   cylindrical mesh [2]
        cylindrical_mesh_config_widget = QWidget()
        cylindrical_mesh_config_widget_layout = QGridLayout()
        cylindrical_mesh_config_widget.setLayout(cylindrical_mesh_config_widget_layout)

        cylindrical_mark = QLabel("cylindrical")
        cylindrical_mesh_config_widget_layout.addWidget(cylindrical_mark)

        #   more to come...
        more_to_come_widget = QLabel("more to come...")

        #   Assemble stacked Widget (watch out for order!)
        self.stacked_mesh_config_widget.addWidget(cubic_mesh_config_widget)     # [1]
        self.stacked_mesh_config_widget.addWidget(cylindrical_mesh_config_widget)   # [2]
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
        if self.current_zero_x > self.chamber_x_max_coor/2:
            min_x_distance2border = self.chamber_x_max_coor - self.current_zero_x
        min_y_distance2border = self.current_zero_y
        if self.current_zero_y > self.chamber_y_max_coor/2:
            min_y_distance2border = self.chamber_y_max_coor - self.current_zero_y
        min_z_distance2border = self.chamber_z_max_coor - float(self.probe_antenna_length_lineEdit.text()) - float(self.aut_height_lineEdit.text())

        self.mesh_cubic_x_max_length_label.setText("< max " + str(2*min_x_distance2border) + " mm")
        self.mesh_cubic_y_max_length_label.setText("< max " + str(2*min_y_distance2border) + " mm")
        self.mesh_cubic_z_max_distance_label.setText("< max " + str(min_z_distance2border) + " mm")

        # Update cylindrical mesh max inputs

        # more to come...


