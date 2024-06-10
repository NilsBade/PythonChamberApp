from PyQt6.QtWidgets import (QWidget, QLineEdit, QLabel, QBoxLayout, QComboBox, QPushButton, QTextEdit, QGridLayout,
                             QSlider, QVBoxLayout,QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np

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
    xz_plot: pg.ImageItem = None
    yz_plot: pg.ImageItem = None
    xy_plot: pg.ImageItem = None


    def __init__(self):
        super().__init__()

        data_selection_widget = self.__init_data_selection_widget()
        data_details_widget = self.__init_data_details_widget()
        data_plot_widget = self.__init_data_plot_widget()

        main_layout = QHBoxLayout()

        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_frame.setContentsMargins(5, 5, 5, 5)
        left_frame.setFixedWidth(300)
        left_column = QVBoxLayout()
        left_column.addWidget(data_selection_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        left_column.addSpacing(50)
        left_column.addWidget(data_details_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        left_column.addStretch()
        left_frame.setLayout(left_column)
        main_layout.addWidget(left_frame)

        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_frame.setContentsMargins(5, 5, 5, 5)
        right_column = QVBoxLayout()
        right_column.addWidget(data_plot_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        right_frame.setLayout(right_column)
        main_layout.addWidget(right_frame)


        self.setLayout(main_layout)
        return



    def __init_data_selection_widget(self):
        main_widget = QWidget()
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
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        upper_line_widget = QWidget()
        upper_line_layout = QHBoxLayout()
        upper_line_widget.setLayout(upper_line_layout)
        parameter_select_label = QLabel("Show Parameter: ")
        self.parameter_select_comboBox = QComboBox()
        self.parameter_select_comboBox.addItem("Select...")
        self.parameter_select_comboBox.setMinimumWidth(150)
        frequency_label = QLabel("Frequency")
        self.frequency_select_slider = QSlider(orientation=Qt.Orientation.Horizontal)
        self.frequency_select_lineEdit = QLineEdit("...")
        self.frequency_select_slider.setFixedWidth(200)
        upper_line_layout.addWidget(parameter_select_label,alignment=Qt.AlignmentFlag.AlignLeft)
        upper_line_layout.addWidget(self.parameter_select_comboBox,alignment=Qt.AlignmentFlag.AlignLeft)
        upper_line_layout.addSpacing(100)
        upper_line_layout.addWidget(frequency_label, alignment=Qt.AlignmentFlag.AlignLeft)
        upper_line_layout.addWidget(self.frequency_select_slider, alignment=Qt.AlignmentFlag.AlignLeft)
        upper_line_layout.addWidget(self.frequency_select_lineEdit,alignment=Qt.AlignmentFlag.AlignLeft)
        upper_line_layout.addStretch()
        main_layout.addWidget(upper_line_widget, stretch=0, alignment=Qt.AlignmentFlag.AlignLeft)

        graphs_layout_widget = pg.GraphicsLayoutWidget()
        graphs_layout_widget.setBackground(background=(255, 255, 255))
        label_pen = pg.mkPen(color='k', width=1)

        xz_graph: pg.PlotItem = graphs_layout_widget.addPlot(0,0,1,1, title="XZ-Plane")
        yz_graph: pg.PlotItem = graphs_layout_widget.addPlot(0,1,1,1, title="XZ-Plane")
        xy_graph: pg.PlotItem = graphs_layout_widget.addPlot(0,2,1,1, title="XZ-Plane")

        self.xz_plot = pg.ImageItem()
        self.yz_plot = pg.ImageItem()
        self.xy_plot = pg.ImageItem()

        sample_data1 = np.random.rand(10, 10, 3)
        sample_data2 = np.random.rand(10, 10, 3)
        sample_data3 = np.random.rand(10, 10, 3)

        self.xz_plot.setImage(sample_data1)
        self.yz_plot.setImage(sample_data2)
        self.xy_plot.setImage(sample_data3)

        xz_graph.addItem(self.xz_plot)
        yz_graph.addItem(self.yz_plot)
        xy_graph.addItem(self.xy_plot)

        main_layout.addWidget(graphs_layout_widget)

        main_widget.setLayout(main_layout)
        return main_widget

    def __init_canvas_widget(self):
        """
        sets up a widget that holds a matplotlib plot item with toolbar on top

        :return: dict { 'widget': QWidget, 'plot': MplCanvas }
        """
        plot_widget = QWidget()
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(sc, plot_widget)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)
        plot_widget.setLayout(layout)

        ret_dict = { 'widget': plot_widget, 'plot': sc}
        return ret_dict

    def __gen_data_details_string(self, measurement_config: dict):
        """
        Generates formatted string from measurement_config info to be displayed in a Textbox or similiar.
        """
        info_string = ""
        infostring += f"*Filetype: {measurement_config['type']}, "
        infostring += f"Timestamp: {measurement_config['timestamp']}\n"
        infostring += f"*Mesh configuration: [min : num of steps : max], unit [mm]\n"
        infostring += (f"X:[{measurement_config['mesh_x_min']}:{measurement_config['mesh_x_steps']}:{measurement_config['mesh_x_max']}]\t"
                       f"Y:[{measurement_config['mesh_y_min']}:{measurement_config['mesh_y_steps']}:{measurement_config['mesh_y_max']}]\t"
                       f"Z:[{measurement_config['mesh_z_min']}:{measurement_config['mesh_z_steps']}:{measurement_config['mesh_z_max']}]\n")
        infostring += f"Zero position: {measurement_config['zero_position']}\n"
        infostring += f"Movementspeed: {measurement_config['movespeed']} mm/s\n"
        infostring += f"*VNA Configuration:\n"
        infostring += f"Measured parameters: {measurement_config['parameter']}\n"
        infostring += f"Frequency: [{measurement_config['freq_start']}:{measurement_config['freq_stop']}] [Hz] with {measurement_config['sweep_num_points']} points\n"
        infostring += f"IF Bandwidth: {measurement_config['if_bw']} [Hz]\n"
        infostring += f"RF Output Power: {measurement_config['output_power']} [dBm]\n"
        infostring += f"Averaged over {measurement_config['average_number']} sweeps for each point"
        return info_string





