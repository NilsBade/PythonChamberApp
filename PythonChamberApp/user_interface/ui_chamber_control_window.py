import os
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


class UI_chamber_control_window(QWidget):

    # Properties

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

        buttons_layout = QGridLayout()

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

        self.button_move_stepsize_input = QLineEdit('10.00')
        self.button_move_stepsize_input.setInputMask('000.00')  # input as float with two decimals

        # control section headers
        xy_label = QLabel("X/Y")
        xy_label.setStyleSheet("text-decoration: underline; font-size: 18px;")
        buttons_layout.addWidget(xy_label, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        z_label = QLabel("Z")
        z_label.setStyleSheet("text-decoration: underline; font-size: 18px;")
        buttons_layout.addWidget(z_label, 0, 4, alignment=Qt.AlignmentFlag.AlignCenter)

        # stepsize input
        stepsize_label = QLabel("<< Stepsize 000.00 [mm]")
        buttons_layout.addWidget(stepsize_label, 4, 3, 1, 2)
        buttons_layout.addWidget(self.button_move_stepsize_input, 4, 1, 1, 2)

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

        main_layout.addLayout(buttons_layout)

        # setup console chamber control
        self.chamber_control_console = QTextEdit()
        self.chamber_control_console.setReadOnly(True)
        self.chamber_control_console.setMaximumHeight(70)
        main_layout.addWidget(self.chamber_control_console)

        main_layout.addStretch()

        return main_widget



