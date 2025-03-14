import os
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy
from .ui_3d_visualizer import VisualizerPyqtGraph as Visualizer

class UI_chamber_control_window(QWidget):

    # Properties
    button_navigation_widget: QWidget = None    # whole left column of UI
    control_buttons_widget: QWidget = None      # sums up all control buttons and goTo functionality. Can be disabled before first time homed.
    # main buttons
    home_all_axis_button: QPushButton = None
    z_tilt_adjust_button: QPushButton = None
    # custom home position
    custom_home_x_editfield: QLineEdit = None
    custom_home_y_editfield: QLineEdit = None
    custom_home_z_editfield: QLineEdit = None
    # control_buttons_widget - Button Menu
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
    # control_buttons_widget - Console
    chamber_control_console: QTextEdit = None
    # Override position button
    override_position_button: QPushButton = None
    # live_position_widget
    live_x_coor_label: QLabel = None
    live_y_coor_label: QLabel = None
    live_z_coor_label: QLabel = None
    # position_graph_widget
    position_graph_bed_object: gl.GLMeshItem = None
    position_graph_head_object: gl.GLScatterPlotItem = None
    chamber_workspace_plot: gl.GLLinePlotItem = None
    position_graph_x_max_coor: float = None
    position_graph_y_max_coor: float = None
    position_graph_z_max_coor: float = None
    position_graph_z_head_bed_offset: float = None

    def __init__(self, position_graph_x_max_coor: float, position_graph_y_max_coor: float, position_graph_z_max_coor: float, chamber_z_head_bed_offset: float):
        super().__init__()
        main_layout = QHBoxLayout()

        self.button_navigation_widget = self.__init_button_navigation_widget()
        self.button_navigation_widget.setFixedWidth(350)
        self.control_buttons_widget.setEnabled(False)

        live_position_widget = self.__init_live_position_widget()
        # initial graph setup
        self.position_graph_x_max_coor = position_graph_x_max_coor
        self.position_graph_y_max_coor = position_graph_y_max_coor
        self.position_graph_z_max_coor = position_graph_z_max_coor
        self.position_graph_z_head_bed_offset = chamber_z_head_bed_offset
        self.chamber_position_graph_widget = self.__init_position_graph_widget()

        main_layout.addWidget(self.button_navigation_widget, stretch=0)

        right_layout = QVBoxLayout()
        live_position_widget.setMaximumHeight(100)
        right_layout.addWidget(live_position_widget)
        right_layout.addWidget(self.chamber_position_graph_widget)

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def __init_button_navigation_widget(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.home_all_axis_button = QPushButton()
        self.home_all_axis_button.setText("Home all axis")
        self.home_all_axis_button.setFixedSize(200,30)
        self.home_all_axis_button.setToolTip("Homes XYZ axis, moves to center position and enables \nall subsequent chamber controls when finished.")
        main_layout.addWidget(self.home_all_axis_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.z_tilt_adjust_button = QPushButton()
        self.z_tilt_adjust_button.setText("Z-Tilt-Adjustment")
        self.z_tilt_adjust_button.setFixedSize(200,30)
        self.z_tilt_adjust_button.setEnabled(False)
        self.z_tilt_adjust_button.setToolTip("Starts the Klipper Z-Tilt-Adjustment routine.\nBefore starting make sure the BL-Touch sensor is attached and\ncorrectly wired to the chamber.")
        main_layout.addWidget(self.z_tilt_adjust_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Custom Home position inputs - Header
        home_pos_label = QLabel("Custom Home Position [mm]:")
        home_pos_label.setStyleSheet("text-decoration: underline; font-size: 14px;")
        main_layout.addWidget(home_pos_label, alignment=Qt.AlignmentFlag.AlignCenter)
        # - Inputs
        custom_home_pos_layout = QHBoxLayout()
        cust_x_label = QLabel("X: ")
        cust_y_label = QLabel("Y: ")
        cust_z_label = QLabel("Z: ")
        self.custom_home_x_editfield = QLineEdit("000.00")
        self.custom_home_x_editfield.setInputMask("000.00")
        self.custom_home_y_editfield = QLineEdit("000.00")
        self.custom_home_y_editfield.setInputMask("000.00")
        self.custom_home_z_editfield = QLineEdit("200.00")
        self.custom_home_z_editfield.setInputMask("000.00")
        custom_home_pos_layout.addWidget(cust_x_label)
        custom_home_pos_layout.addWidget(self.custom_home_x_editfield)
        custom_home_pos_layout.addWidget(cust_y_label)
        custom_home_pos_layout.addWidget(self.custom_home_y_editfield)
        custom_home_pos_layout.addWidget(cust_z_label)
        custom_home_pos_layout.addWidget(self.custom_home_z_editfield)
        main_layout.addLayout(custom_home_pos_layout)

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

        self.button_move_jogspeed_input_line = QLineEdit('050.0')
        self.button_move_jogspeed_input_line.setInputMask('000.0')  # input as float with two decimals
        self.button_move_jogspeed_input_line.setAlignment(Qt.AlignmentFlag.AlignRight)

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

        # jogspeed input
        jogspeed_label = QLabel("<< Speed 00.0 [mm/s]")
        buttons_layout.addWidget(jogspeed_label, 5, 2, 1, 3)
        buttons_layout.addWidget(self.button_move_jogspeed_input_line, 5, 0, 1, 2)

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

        main_layout.addWidget(self.control_buttons_widget)

        # Add Menu to go to absolut coordinates
        label_go_abs_coor = QLabel("Go to absolute coordinates [mm]:")
        label_go_abs_coor.setStyleSheet("text-decoration: underline; font-size: 14px;")
        main_layout.addWidget(label_go_abs_coor)

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

        self.go_abs_coor_x_editfield.setEnabled(False)
        self.go_abs_coor_y_editfield.setEnabled(False)
        self.go_abs_coor_z_editfield.setEnabled(False)
        self.go_abs_coor_go_button.setEnabled(False)
        main_layout.addLayout(xyz_go_abs_layout)

        # setup console chamber control
        self.chamber_control_console = QTextEdit()
        self.chamber_control_console.setReadOnly(True)
        main_layout.addWidget(self.chamber_control_console)

        # Override position button
        self.override_position_button = QPushButton("Override App's Position")
        self.override_position_button.setToolTip("Override the current position with [0,0,0].\nUse with caution!")
        main_layout.addWidget(self.override_position_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return main_widget

    def __init_live_position_widget(self):
        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.Box)  # Set the frame shape
        main_frame.setFrameShadow(QFrame.Shadow.Raised)  # Set the frame shadow
        main_frame.setLineWidth(2)  # Set the width of the frame line
        main_frame.setStyleSheet("background-color: lightGray;")  # Set frame background color
        main_frame.setContentsMargins(5,5,5,5)

        frame_layout = QGridLayout()
        main_frame.setLayout(frame_layout)

        pos_header = QLabel("Live Head Position [mm]:")
        pos_header.setStyleSheet("text-decoration: underline; font-size: 16px;")
        frame_layout.addWidget(pos_header, 0, 0, 1, 6, alignment= Qt.AlignmentFlag.AlignCenter)
        live_x_coor_header = QLabel("X:")
        frame_layout.addWidget(live_x_coor_header, 1, 0, 1, 1, alignment= Qt.AlignmentFlag.AlignCenter)
        live_y_coor_header = QLabel("Y:")
        frame_layout.addWidget(live_y_coor_header, 1, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        live_z_coor_header = QLabel("Z:")
        frame_layout.addWidget(live_z_coor_header, 1, 4, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)

        self.live_x_coor_label = QLabel("unknown")
        self.live_x_coor_label.setStyleSheet("font-size: 16px;")
        frame_layout.addWidget(self.live_x_coor_label, 1, 1, 1, 1, alignment= Qt.AlignmentFlag.AlignLeft)
        self.live_y_coor_label = QLabel("unknown")
        self.live_y_coor_label.setStyleSheet("font-size: 16px;")
        frame_layout.addWidget(self.live_y_coor_label, 1, 3, 1, 1, alignment= Qt.AlignmentFlag.AlignLeft)
        self.live_z_coor_label = QLabel("unknown")
        self.live_z_coor_label.setStyleSheet("font-size: 16px;")
        frame_layout.addWidget(self.live_z_coor_label, 1, 5, 1, 1, alignment= Qt.AlignmentFlag.AlignLeft)

        return main_frame

    def __init_position_graph_widget(self):
        chamber_position_widget = gl.GLViewWidget()
        chamber_position_widget.setBackgroundColor("d")

        # Properties to adapt
        chamber_max_x = self.position_graph_x_max_coor
        chamber_max_y = self.position_graph_y_max_coor
        chamber_max_z = self.position_graph_z_max_coor

        # Create GLMeshItem and add it to chamber position widget
        self.position_graph_bed_object = Visualizer.generate_3d_chamber_print_bed_obj(self.position_graph_x_max_coor,
                                                                                   self.position_graph_y_max_coor,
                                                                                   self.position_graph_z_max_coor,
                                                                                   self.position_graph_z_head_bed_offset)
        chamber_position_widget.addItem(self.position_graph_bed_object)

        # Draw Red Chamber border and add it to chamber position widget
        self.chamber_workspace_plot = Visualizer.generate_3d_chamber_workspace(self.position_graph_x_max_coor,
                                                                            self.position_graph_y_max_coor,
                                                                            self.position_graph_z_max_coor,
                                                                            self.position_graph_z_head_bed_offset)
        chamber_position_widget.addItem(self.chamber_workspace_plot)

        # Draw COS axis at 0,0,0
        cos = gl.GLAxisItem()
        cos.setSize(x=-(self.position_graph_x_max_coor + 20), y=(self.position_graph_y_max_coor + 20), z=-(self.position_graph_z_max_coor + 20))
        cos.translate(dx=self.position_graph_x_max_coor, dy=0, dz=0)
        chamber_position_widget.addItem(cos)

        # Label Front side of work-volume
        frontlabel = gl.GLTextItem(pos=numpy.array([chamber_max_x/2, -10, 5]), text="FrontSide")
        chamber_position_widget.addItem(frontlabel)

        # set view point roughly
        chamber_position_widget.pan(chamber_max_x/2, chamber_max_y/2, -chamber_max_z/4)
        #chamber_position_widget.orbit(azim=90, elev=0)
        chamber_position_widget.setCameraPosition(distance=1500)

        # create spot to display head position
        self.position_graph_head_object = gl.GLScatterPlotItem()
        self.position_graph_head_object.setData(pos=(0, 0, self.position_graph_z_head_bed_offset), size=10)
        chamber_position_widget.addItem(self.position_graph_head_object)

        return chamber_position_widget

    def enable_go_to_controls(self):
        """
        Enables the go-to functionality only. Buttons and inputs.
        """
        self.go_abs_coor_x_editfield.setEnabled(True)
        self.go_abs_coor_y_editfield.setEnabled(True)
        self.go_abs_coor_z_editfield.setEnabled(True)
        self.go_abs_coor_go_button.setEnabled(True)
        return

    def get_go_abs_coor_inputs(self):
        """
        Function gets absolute coordinates put into X,Y,Z fields to react to "GO" button pressed.

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

    def get_button_move_jogspeed(self):
        """
        :returns: desired jog speed in [mm/s]
        """
        return float(self.button_move_jogspeed_input_line.text())

    def get_custom_home_position(self):
        """
        :returns: list [x: float, y: float, z: float]
        """
        x = float(self.custom_home_x_editfield.text())
        y = float(self.custom_home_y_editfield.text())
        z = float(self.custom_home_z_editfield.text())
        return [x, y, z]

    def append_message2console(self, message: str):
        """
        Adds the given 'message: str' with extra timestamp to the console field in the chamber_control_window.
        """
        time_now = datetime.now()
        timestamp = time_now.strftime("%H:%M:%S")
        new_text = '[' + timestamp + ']: ' + message
        self.chamber_control_console.append(new_text)
        return

    def update_live_coor_display(self, x: float, y: float, z: float):
        """
        Updates the live position coordinate-labels and the graph visualization
        """
        # Update labels
        self.live_x_coor_label.setText(str(x))
        self.live_y_coor_label.setText(str(y))
        self.live_z_coor_label.setText(str(z))

        # Update visualization bed and head
        self.position_graph_bed_object.resetTransform()
        self.position_graph_bed_object.translate(dx=0, dy=0, dz=-z)
        self.position_graph_head_object.resetTransform()
        self.position_graph_head_object.translate(dx=-x+self.position_graph_x_max_coor, dy=y, dz=0) # X Offset needed since COS visualized mirrord on x axis
        return


