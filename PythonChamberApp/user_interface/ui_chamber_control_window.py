import os
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


class UI_chamber_control_window(QWidget):

    # Properties
    button_navigation_widget: QWidget = None    # whole left column of UI
    control_buttons_widget: QWidget = None      # sums up all control buttons and goTo functionality. Can be disabled before first time homed.
    # control_buttons_widget - Button Menu
    home_all_axis_button: QPushButton = None
    button_move_x_inc: QPushButton = None
    button_move_x_dec: QPushButton = None
    button_move_y_inc: QPushButton = None
    button_move_y_dec: QPushButton = None
    button_move_z_inc: QPushButton = None
    button_move_z_dec: QPushButton = None
    button_move_home_xy: QPushButton = None
    button_move_home_z: QPushButton = None
    button_move_stepsize_input_line: QLineEdit = None
    # control_buttons_widget - Go To Menu
    go_abs_coor_x_editfield: QLineEdit = None
    go_abs_coor_y_editfield: QLineEdit = None
    go_abs_coor_z_editfield: QLineEdit = None
    go_abs_coor_go_button: QPushButton = None


    def __init__(self):
        super().__init__()

        self.button_navigation_widget = self.__init_button_navigation_widget()

        main_layout = QHBoxLayout()
        self.button_navigation_widget.setFixedWidth(320)
        main_layout.addWidget(self.button_navigation_widget, stretch=0)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def __init_button_navigation_widget(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.home_all_axis_button = QPushButton()
        self.home_all_axis_button.setText("Home all axis")
        self.home_all_axis_button.setFixedSize(200,30)
        main_layout.addWidget(self.home_all_axis_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.control_buttons_widget = QWidget()     # Summed up widget to enable/disable all together
        buttons_layout = QGridLayout()
        self.control_buttons_widget.setLayout(buttons_layout)

        # Get Icons from library
        #   calculate absolute path for QIcon class -
        #   > implemented check in case somehow the root directory is one level too low
        path_user_interface_module = os.getcwd()
        file_is_at_location = os.path.isfile(os.path.join(path_user_interface_module, "fugue_icons/icons_large/arrow-090.png"))
        if file_is_at_location:
            abs_path_root = path_user_interface_module
        else:
            abs_path_root = os.path.join(path_user_interface_module, 'PythonChamberApp')

        #   get icons by absolute path
        icon_arrow_up = QIcon(os.path.join(abs_path_root, "fugue_icons/icons_large/arrow-090.png"))
        icon_arrow_right = QIcon(os.path.join(abs_path_root, "fugue_icons/icons_large/arrow.png"))
        icon_arrow_left = QIcon(os.path.join(abs_path_root, "fugue_icons/icons_large/arrow-180.png"))
        icon_arrow_down = QIcon(os.path.join(abs_path_root, "fugue_icons/icons_large/arrow-270.png"))
        icon_home = QIcon(os.path.join(abs_path_root, "fugue_icons/home.png"))

        # assign icons to movement buttons
        self.button_move_x_inc = QPushButton(icon=icon_arrow_right)
        self.button_move_x_inc.setFixedSize(50, 50)
        self.button_move_x_dec = QPushButton(icon=icon_arrow_left)
        self.button_move_x_dec.setFixedSize(50,50)

        self.button_move_y_inc = QPushButton(icon=icon_arrow_up)
        self.button_move_y_inc.setFixedSize(50, 50)
        self.button_move_y_dec = QPushButton(icon=icon_arrow_down)
        self.button_move_y_dec.setFixedSize(50, 50)

        self.button_move_z_inc = QPushButton(icon=icon_arrow_up)
        self.button_move_z_inc.setFixedSize(50, 50)
        self.button_move_z_dec = QPushButton(icon=icon_arrow_down)
        self.button_move_z_dec.setFixedSize(50, 50)

        self.button_move_home_xy = QPushButton(icon=icon_home)
        self.button_move_home_xy.setFixedSize(50, 50)
        self.button_move_home_z = QPushButton(icon=icon_home)
        self.button_move_home_z.setFixedSize(50, 50)

        self.button_move_stepsize_input_line = QLineEdit('10.00')
        self.button_move_stepsize_input_line.setInputMask('000.00')  # input as float with two decimals
        self.button_move_stepsize_input_line.setAlignment(Qt.AlignmentFlag.AlignRight)

        # control section headers
        xy_label = QLabel("X/Y")
        xy_label.setStyleSheet("text-decoration: underline; font-size: 18px;")
        buttons_layout.addWidget(xy_label, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        z_label = QLabel("Z")
        z_label.setStyleSheet("text-decoration: underline; font-size: 18px;")
        buttons_layout.addWidget(z_label, 0, 4, alignment=Qt.AlignmentFlag.AlignCenter)

        # stepsize input
        stepsize_label = QLabel("<< Stepsize 000.00 [mm]")
        buttons_layout.addWidget(stepsize_label, 4, 2, 1, 3)
        buttons_layout.addWidget(self.button_move_stepsize_input_line, 4, 0, 1, 2)

        # buttons xy
        buttons_layout.addWidget(self.button_move_y_inc, 1, 1)
        buttons_layout.addWidget(self.button_move_x_dec, 2, 0)
        buttons_layout.addWidget(self.button_move_home_xy, 2, 1)
        buttons_layout.addWidget(self.button_move_x_inc, 2, 2)
        buttons_layout.addWidget(self.button_move_y_dec, 3, 1)

        # buttons z
        buttons_layout.addWidget(self.button_move_z_inc, 1, 4)
        buttons_layout.addWidget(self.button_move_home_z, 2, 4)
        buttons_layout.addWidget(self.button_move_z_dec, 3, 4)

        # Add Menu to go to absolut coordinates
        label_go_abs_coor = QLabel("Go to absolute coordinates [mm]:")
        label_go_abs_coor.setStyleSheet("text-decoration: underline; font-size: 14px;")
        buttons_layout.addWidget(label_go_abs_coor,5,0,1,4)

        xyz_go_abs_layout = QHBoxLayout()
        go_abs_coor_x_label = QLabel("X: ")
        self.go_abs_coor_x_editfield = QLineEdit()
        self.go_abs_coor_x_editfield.setInputMask("000.00;")
        self.go_abs_coor_x_editfield.setText("100.00")
        self.go_abs_coor_x_editfield.setAlignment(Qt.AlignmentFlag.AlignCenter)
        go_abs_coor_y_label = QLabel("Y: ")
        self.go_abs_coor_y_editfield = QLineEdit()
        self.go_abs_coor_y_editfield.setInputMask("000.00;")
        self.go_abs_coor_y_editfield.setText("100.00")
        self.go_abs_coor_y_editfield.setAlignment(Qt.AlignmentFlag.AlignCenter)
        go_abs_coor_z_label = QLabel("Z: ")
        self.go_abs_coor_z_editfield = QLineEdit()
        self.go_abs_coor_z_editfield.setInputMask("000.00;")
        self.go_abs_coor_z_editfield.setText("100.00")
        self.go_abs_coor_z_editfield.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.go_abs_coor_go_button = QPushButton("GO")
        xyz_go_abs_layout.addWidget(go_abs_coor_x_label)
        xyz_go_abs_layout.addWidget(self.go_abs_coor_x_editfield)
        xyz_go_abs_layout.addWidget(go_abs_coor_y_label)
        xyz_go_abs_layout.addWidget(self.go_abs_coor_y_editfield)
        xyz_go_abs_layout.addWidget(go_abs_coor_z_label)
        xyz_go_abs_layout.addWidget(self.go_abs_coor_z_editfield)
        xyz_go_abs_layout.addWidget(self.go_abs_coor_go_button)

        buttons_layout.addLayout(xyz_go_abs_layout, 6, 0, 1, 5)

        main_layout.addWidget(self.control_buttons_widget)
        self.control_buttons_widget.setEnabled(False)

        # setup console chamber control
        self.chamber_control_console = QTextEdit()
        self.chamber_control_console.setReadOnly(True)
        main_layout.addWidget(self.chamber_control_console)

        return main_widget

    def get_go_abs_coor_inputs(self):
        """
        Function gets absolute coordinates put into X,Y,Z fields to react to "GO" button pressed
        :returns: dict {'x': float, 'y': float, 'z': float}
        """
        x_desired = float(self.go_abs_coor_x_editfield.text())
        y_desired = float(self.go_abs_coor_y_editfield.text())
        z_desired = float(self.go_abs_coor_z_editfield.text())
        return {'x': x_desired, 'y': y_desired, 'z': z_desired}

    def get_button_move_stepsize(self):
        """
        :returns: desired stepsize as float
        """
        return float(self.button_move_stepsize_input_line.text())



