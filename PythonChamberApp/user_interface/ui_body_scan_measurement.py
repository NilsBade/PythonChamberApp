import os
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, \
    QProgressBar, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QPixmap
import pyqtgraph as pg
import numpy as np
from datetime import datetime


class UI_body_scan_measurement_window(QWidget):
    # Properties
    # display current zero / origin (lower, left, front corner of measurement volume)
    current_origin_x: float = None
    current_origin_y: float = None
    current_origin_z: float = None
    chamber_x_max_coor: float = None  # given via init to calculate maximum inputs on UI obj-level
    chamber_y_max_coor: float = None  # given via init to calculate maximum inputs on UI obj-level
    chamber_z_max_coor: float = None  # given via init to calculate maximum inputs on UI obj-level

    # Mesh config inputs
    button_set_current_as_origin: QPushButton = None
    label_show_current_origin: QLabel = None
    label_show_current_position: QLabel = None
    body_scan_jogSpeed_LineEdit: QLineEdit = None  # input jogspeed in [mm/s]

    mesh_x_length_lineEdit: QLineEdit = None
    mesh_x_max_length_label: QLabel = None
    mesh_x_num_of_steps_lineEdit: QLineEdit = None
    mesh_y_length_lineEdit: QLineEdit = None
    mesh_y_max_length_label: QLabel = None
    mesh_y_num_of_steps_lineEdit: QLineEdit = None
    mesh_z_length_lineEdit: QLineEdit = None
    mesh_z_max_length_label: QLabel = None
    mesh_z_num_of_steps_lineEdit: QLineEdit = None
    z_move_sleepTime_lineEdit: QLineEdit = None  # input sleep time as float [s] - after each movement in z-direction wait shortly because of vibration in body model

    # VNA config inputs
    vna_config_filepath_lineEdit: QLineEdit = None  # filepath to .cst config file
    vna_config_filepath_check_button: QPushButton = None  # presets with .cst file and reads config from pna

    # Data-management inputs
    filename_lineEdit: QLineEdit = None

    #   start body scan button
    body_scan_start_button: QPushButton = None

    #   body scan progress frame
    body_scan_stop_button = QPushButton = None
    meas_progress_points_in_layer: QLabel = None  # Number of points to measure in XY-plane
    meas_progress_current_point_in_layer: QLabel = None
    meas_progress_in_layer_progressBar: QProgressBar = None
    meas_progress_layer_max_count: QLabel = None
    meas_progress_layer_current: QLabel = None  # each point is probed at all layer heights before next point
    meas_progress_layer_progressBar: QProgressBar = None
    meas_progress_total_point_max_count: QLabel = None
    meas_progress_total_point_current: QLabel = None
    meas_progress_total_point_progressBar: QProgressBar = None
    meas_progress_status_label: QLabel = None

    #   2d graph visualization of mesh
    plot_2d_layout_widget: pg.GraphicsLayoutWidget = None
    plot_2d_xy: pg.PlotItem = None
    plot_xy_origin_cos: pg.PlotDataItem = None  # use 'origin' instead 'zero'!
    plot_xy_mesh_points: pg.PlotDataItem
    plot_2d_xz: pg.PlotItem = None
    plot_xz_origin_cos: pg.PlotDataItem = None  # use 'origin' instead 'zero'!
    plot_xz_mesh_points: pg.PlotDataItem = None

    def __init__(self, chamber_x_max_coor: float, chamber_y_max_coor: float, chamber_z_max_coor: float,
                 chamber_z_head_bed_offset: float):
        super().__init__()

        self.chamber_x_max_coor = chamber_x_max_coor
        self.chamber_y_max_coor = chamber_y_max_coor
        self.chamber_z_max_coor = chamber_z_max_coor
        self.chamber_z_head_bed_offset = chamber_z_head_bed_offset

        self.label_show_current_position = QLabel("Current Position >> Not initialized")
        self.label_show_current_origin = QLabel("Current Origin >> Not initialized")

        main_layout = QHBoxLayout()
        # Column 1,2
        configs_layout = QGridLayout()
        mesh_config_widget = self.__init_mesh_config_widget()
        vna_config_widget = self.__init_vna_config_widget()
        data_management_widget = self.__init_data_management_widget()
        self.body_scan_start_button = QPushButton("Start Body Scan Process")
        configs_layout.addWidget(mesh_config_widget, 0, 0, 3, 1)
        configs_layout.addWidget(vna_config_widget, 0, 1, 1, 1, Qt.AlignmentFlag.AlignTop)
        configs_layout.addWidget(data_management_widget, 1, 1, 1, 1, Qt.AlignmentFlag.AlignTop)
        configs_layout.addWidget(self.body_scan_start_button, 2, 1, 1, 1, Qt.AlignmentFlag.AlignBottom)

        # Column 3
        third_column = QVBoxLayout()
        body_scan_progress_widget = self.__init_body_scan_progress_widget()
        # body_scan_progress_widget.setFixedHeight(170)
        figure_widget = self.__init_figure_widget()
        # figure_widget.setFixedWidth(300)
        # figure_widget.setFixedHeight(400)
        third_column.addWidget(body_scan_progress_widget, stretch=1)
        third_column.addWidget(figure_widget, stretch=2)

        # Column 4
        fourth_column = QVBoxLayout()
        self.plot_2d_layout_widget = self.__init_2d_plots()
        self.plot_2d_layout_widget.setMinimumWidth(300)
        fourth_column.addWidget(self.plot_2d_layout_widget)

        main_layout.addLayout(configs_layout, stretch=0)
        main_layout.addLayout(third_column, stretch=1)
        main_layout.addLayout(fourth_column, stretch=1)
        self.setLayout(main_layout)

    def __init_mesh_config_widget(self):
        """
        Initialize '1. Mesh Config' Frame Widget and return it
        """
        mesh_config_frame = QFrame()
        mesh_config_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        mesh_config_frame.setContentsMargins(5, 5, 5, 5)
        mesh_config_frame.setFixedWidth(300)
        frame_layout = QVBoxLayout()
        mesh_config_frame.setLayout(frame_layout)

        # todo put in all the inputs etc as planned on paper

        return mesh_config_frame

    def __init_vna_config_widget(self):
        """
        Initialize '2. VNA Config' Frame Widget and return it
        """
        vna_config_frame = QFrame()
        vna_config_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        vna_config_frame.setContentsMargins(5, 5, 5, 5)
        vna_config_frame.setFixedWidth(300)
        frame_layout = QVBoxLayout()
        vna_config_frame.setLayout(frame_layout)

        # todo put in all the inputs etc as planned on paper

        return vna_config_frame

    def __init_data_management_widget(self):
        """
        Initialize '3. Data Management' Frame Widget and return it
        """
        data_management_frame = QFrame()
        data_management_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        data_management_frame.setContentsMargins(5, 5, 5, 5)
        data_management_frame.setFixedWidth(300)
        frame_layout = QVBoxLayout()
        data_management_frame.setLayout(frame_layout)

        # todo put in all the inputs etc as planned on paper

        return data_management_frame

    def __init_body_scan_progress_widget(self):
        """
        Initialize 'Body Scan Progress' Frame Widget and return it
        """
        frame_widget = QFrame()
        frame_widget.setFrameShape(QFrame.Shape.Box)  # Set the frame shape
        frame_widget.setFrameShadow(QFrame.Shadow.Raised)  # Set the frame shadow
        frame_widget.setLineWidth(2)  # Set the width of the frame line
        frame_widget.setStyleSheet("background-color: lightGray;")  # Set frame background color
        frame_widget.setContentsMargins(5, 5, 5, 5)

        frame_layout = QGridLayout()
        frame_widget.setLayout(frame_layout)
        title = QLabel("Body Scan Progress")
        title.setStyleSheet("text-decoration: underline; font-size: 16px;")
        frame_layout.addWidget(title, 0, 0, 1, 6, alignment=Qt.AlignmentFlag.AlignCenter)
        curr_point_in_layer_label = QLabel("Current Point in Layer:")
        curr_layer_label = QLabel("Current Layer:")
        curr_point_total_label = QLabel("Total Progress Point-wise:")
        curr_status_label = QLabel("Status:")
        time_to_go_label = QLabel("Time to go:")
        frame_layout.addWidget(curr_point_in_layer_label, 1, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(curr_layer_label, 2, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(curr_point_total_label, 3, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(curr_status_label, 4, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(time_to_go_label, 5, 0, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)

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
        self.meas_progress_time_to_go = QLabel("00:00:00")
        self.body_scan_stop_button = QPushButton("Stop Measurement")

        backslash1 = QLabel("/")
        backslash2 = QLabel("/")
        backslash3 = QLabel("/")

        frame_layout.addWidget(self.meas_progress_current_point_in_layer, 1, 1, 1, 1,
                               alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(backslash1, 1, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_points_in_layer, 1, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_in_layer_progressBar, 1, 4, 1, 2,
                               alignment=Qt.AlignmentFlag.AlignLeft)

        frame_layout.addWidget(self.meas_progress_layer_current, 2, 1, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(backslash2, 2, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_layer_max_count, 2, 3, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_layer_progressBar, 2, 4, 1, 2, alignment=Qt.AlignmentFlag.AlignLeft)

        frame_layout.addWidget(self.meas_progress_total_point_current, 3, 1, 1, 1,
                               alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(backslash3, 3, 2, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_total_point_max_count, 3, 3, 1, 1,
                               alignment=Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.meas_progress_total_point_progressBar, 3, 4, 1, 2,
                               alignment=Qt.AlignmentFlag.AlignLeft)

        frame_layout.addWidget(self.meas_progress_status_label, 4, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(self.body_scan_stop_button, 4, 4, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        frame_layout.addWidget(self.meas_progress_time_to_go, 5, 1, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)

        return frame_widget

    def __init_figure_widget(self):
        """
        Initialize SVG widget with smart path handling. return widget.
        """
        abs_path_root = os.getcwd()
        file_is_at_location = os.path.isfile(
            os.path.join(abs_path_root, "figures/bodyscan_measurement.svg"))
        if not file_is_at_location:
            # correct root if working directory 'too high'
            abs_path_root = os.path.join(abs_path_root, 'PythonChamberApp')

        figure_widget = QSvgWidget()
        figure_widget.load(os.path.join(abs_path_root, 'figures/bodyscan_measurement.svg'))
        return figure_widget

    def __init_2d_plots(self):
        """
        Initialize 2D Plots of configured probe-mesh and return widget
        """

        graph_layout_widget = pg.GraphicsLayoutWidget(title='2D View of Mesh in Klipper COS')
        graph_layout_widget.setBackground(background=(255, 255, 255))
        label_pen = pg.mkPen(color='k', width=1)

        x_axis_xy = pg.AxisItem(orientation='top', text='X [mm]', textPen=label_pen)
        x_axis_xy.setGrid(125)
        x_axis_xy.showLabel()
        y_axis_xy = pg.AxisItem(orientation='left', text='Y [mm]', textPen=label_pen)
        y_axis_xy.setGrid(125)
        y_axis_xy.showLabel()
        x_axis_xz = pg.AxisItem(orientation='top', text='X [mm]', textPen=label_pen)
        x_axis_xz.setGrid(125)
        x_axis_xz.showLabel()
        z_axis = pg.AxisItem(orientation='left', text='Z [mm]', textPen=label_pen)
        z_axis.setGrid(125)
        z_axis.showLabel()

        xy_workspace_vertices = np.array([[0.0, 0.0], [self.chamber_x_max_coor, 0.0],
                                 [self.chamber_x_max_coor, self.chamber_y_max_coor], [0.0, self.chamber_y_max_coor],
                                 [0, 0]])
        xy_workspace_lines_connect = np.array([[0, 1], [1, 2], [2, 3], [3, 0]])
        xy_workspace_plot = pg.GraphItem(pos=xy_workspace_vertices, adj=xy_workspace_lines_connect, pen='r', symbolPen='r', symbolBrush=None, symbol='+')

        xz_workspace_vertices = np.array([
            [0, -self.chamber_z_head_bed_offset], [0, 0], [0, self.chamber_z_max_coor],
            [self.chamber_x_max_coor, self.chamber_z_max_coor], [self.chamber_x_max_coor, 0],
            [self.chamber_x_max_coor, -self.chamber_z_head_bed_offset]
        ])
        xz_workspace_lines_connect = np.array([[0,1],[1,2],[2,3],[3,4],[4,5],[0,5],[1,4]])
        xz_workspace_plot = pg.GraphItem(pos=xz_workspace_vertices, adj=xz_workspace_lines_connect, pen='r', symbolPen='r', symbolBrush=None, symbol='+')

        # build xy plot --> Graph-x-axis is positive Chamber-Y-axis | Graph-y-axis is negative Chamber-x-axis
        self.plot_2d_xy = pg.PlotItem()
        graph_layout_widget.addItem(self.plot_2d_xy, 0, 0)
        self.plot_2d_xy.setTitle(title='XY-TopView on Mesh', color='k')
        self.plot_2d_xy.setAxisItems(axisItems={'left': y_axis_xy, 'top': x_axis_xy})
        self.plot_2d_xy.hideAxis('bottom')
        self.plot_2d_xy.getViewBox().invertX(True)
        self.plot_2d_xy.getViewBox().setRange(xRange=(0, self.chamber_y_max_coor), yRange=(0, self.chamber_x_max_coor))
        self.plot_2d_xy.getViewBox().setAspectLocked(lock=True, ratio=1)
        self.plot_2d_xy.addItem(xy_workspace_plot)

        # build xz plot
        self.plot_2d_xz = pg.PlotItem()
        graph_layout_widget.addItem(self.plot_2d_xz, 1, 0)
        self.plot_2d_xz.setTitle('XZ-FrontView on Mesh', color='k')
        self.plot_2d_xz.setAxisItems(axisItems={'left': z_axis, 'top': x_axis_xz})
        y_axis_xy.linkToView(self.plot_2d_xy.getViewBox())
        self.plot_2d_xz.getViewBox().invertX(True)
        self.plot_2d_xz.getViewBox().invertY(True)
        self.plot_2d_xz.getViewBox().setRange(xRange=(0, self.chamber_y_max_coor), yRange=(0, self.chamber_z_max_coor))
        self.plot_2d_xz.getViewBox().setAspectLocked(lock=True, ratio=2)
        self.plot_2d_xz.addItem(xz_workspace_plot)
        self.plot_2d_xz.getViewBox().setXLink(self.plot_2d_xy.getViewBox())

        zero_cos_pen = pg.mkPen(color=(0, 0, 255), width=1)
        self.plot_xy_zero_cos = pg.PlotDataItem(symbol='s', symbolPen=zero_cos_pen)
        self.plot_xz_zero_cos = pg.PlotDataItem(symbol='s', symbolPen=zero_cos_pen)

        mesh_pen = pg.mkPen(color=(10, 255, 10), width=2)
        self.plot_xy_mesh_points = pg.PlotDataItem(symbol='o', symbolPen=mesh_pen, symbolSize=2, pen=None)
        self.plot_xz_mesh_points = pg.PlotDataItem(symbol='o', symbolPen=mesh_pen, symbolSize=2, pen=None)

        self.plot_2d_xy.addItem(self.plot_xy_zero_cos)
        self.plot_2d_xz.addItem(self.plot_xz_zero_cos)
        self.plot_2d_xy.addItem(self.plot_xy_mesh_points)
        self.plot_2d_xz.addItem(self.plot_xz_mesh_points)

        #   default values
        self.update_2d_plots()
        return graph_layout_widget



    def update_2d_plots(self):
        """
        Updates mesh points according to given mesh inputs
        > So far only cubic supported
        > skips update if no zero position is logged completely
        """
        #   skip update if no zero position logged
        if self.current_origin_x is None or self.current_origin_y is None or self.current_origin_z is None:
            return
        #   update zero positions in plot
        xy_zero = np.array([[self.current_origin_x, self.current_origin_y]])
        xz_zero = np.array([[self.current_origin_x, self.current_origin_z]])
        self.plot_xy_zero_cos.setData(xy_zero)
        self.plot_xz_zero_cos.setData(xz_zero)
        #   update mesh points
        mesh_info = self.get_mesh_data()
        xy_mesh_points_list = []
        for x in mesh_info['x_vec']:
            for y in mesh_info['y_vec']:
                xy_mesh_points_list.append([x, y])
        xy_mesh_points_array = np.array(xy_mesh_points_list)
        xz_mesh_points_list = []
        for x in mesh_info['x_vec']:
            for z in mesh_info['z_vec']:
                xz_mesh_points_list.append([x, z])
        xz_mesh_points_array = np.array(xz_mesh_points_list)
        self.plot_xy_mesh_points.setData(xy_mesh_points_array)
        self.plot_xz_mesh_points.setData(xz_mesh_points_array)

    def get_mesh_data(self):
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

                *Coordinates are already transferred to chamber-movement coordinate system based on set origin!*
                """
        info_dict = {}
        #   get inputs
        x_length = float(self.mesh_x_length_lineEdit.text())
        x_num_steps = int(self.mesh_x_num_of_steps_lineEdit.text())
        y_length = float(self.mesh_y_length_lineEdit.text())
        y_num_steps = int(self.mesh_y_num_of_steps_lineEdit.text())
        z_length = float(self.mesh_z_length_lineEdit.text())
        z_num_steps = int(self.mesh_z_num_of_steps_lineEdit.text())

        #   get current zero
        x_origin = self.current_origin_x
        y_origin = self.current_origin_y
        z_origin = self.current_origin_z

        #   calculate coordinate vectors in Klipper/Chamber COS
        x_linspace = np.linspace(x_origin, x_origin + x_length, x_num_steps)
        y_linspace = np.linspace(y_origin, y_origin + y_length, y_num_steps)
        z_linspace = np.linspace(z_origin, z_origin + z_length, z_num_steps)

        x_vec = []
        for i in x_linspace:
            x_vec.append(i)
        y_vec = []
        for i in y_linspace:
            y_vec.append(i)
        z_vec = []
        for i in z_linspace:
            z_vec.append(i)

        #   fill info dict
        info_dict['tot_num_of_points'] = x_num_steps * y_num_steps * z_num_steps
        info_dict['num_steps_x'] = x_num_steps
        info_dict['num_steps_y'] = y_num_steps
        info_dict['num_steps_z'] = z_num_steps
        info_dict['x_vec'] = tuple(x_vec)
        info_dict['y_vec'] = tuple(y_vec)
        info_dict['z_vec'] = tuple(z_vec)

        return info_dict

    def update_live_coor_display(self, new_x: float, new_y: float, new_z: float):
        """
        Updates live position displays in auto-measurement-tab
        """
        new_position_string = "Current Position >> X:" + str(new_x) + " Y:" + str(new_y) + " Z:" + str(new_z)
        self.label_show_current_position.setText(new_position_string)

    def update_current_origin(self, new_x: float, new_y: float, new_z: float):
        """
        Updates display and buffer of current zero position.
        Initiates update of all max-input-labels in mesh_configurations_widgets.
        """
        self.current_origin_x = new_x
        self.current_origin_y = new_y
        self.current_origin_z = new_z

        new_origin_label = "Current Origin >> X:" + str(new_x) + " Y:" + str(new_y) + " Z:" + str(new_z)
        self.label_show_current_origin.setText(new_origin_label)

        self.update_mesh_max_input_labels()

    def update_mesh_max_input_labels(self):
        """
        Updates the Max-Value-labels in the mesh configuration widget.

        Draws information from class properties everytime the origin is set or updated.
        """
        # Update Cubic mesh max inputs
        x_distance2border = self.chamber_x_max_coor - self.current_origin_x
        y_distance2border = self.chamber_y_max_coor - self.current_origin_y
        z_distance2border = self.chamber_z_max_coor - self.current_origin_z

        self.mesh_x_max_length_label.setText("< max " + str(x_distance2border) + " mm")
        self.mesh_y_max_length_label.setText("< max " + str(y_distance2border) + " mm")
        self.mesh_z_max_length_label.setText("< max " + str(z_distance2border) + " mm")
