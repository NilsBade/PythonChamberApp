import sys
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PythonChamberApp.chamber_net_interface.chamber_net_interface import ChamberNetworkCommands as Chamber


class UI_config_window(QWidget):

    def __init__(self):
        super().__init__()

        chamber_connect_widget = self.__init_chamber_connection_block()
        vna_connect_widget = self.__init_vna_connection_block()

        self.config_overview_widget = QWidget()

        main_layout = QHBoxLayout()

        main_left_layout = QVBoxLayout()
        main_left_layout.addWidget(chamber_connect_widget)
        main_left_layout.addWidget(vna_connect_widget)
        main_left_layout.addStretch()

        main_layout.addLayout(main_left_layout)

        main_layout.addWidget(self.config_overview_widget, stretch=4)

        self.setLayout(main_layout)

    def __init_chamber_connection_block(self):
        chamber_connect_widget = QWidget()
        chamber_connect_layout = QVBoxLayout()
        chamber_connect_widget.setLayout(chamber_connect_layout)

        title_label = QLabel("Chamber Connection")
        title_label.setStyleSheet("font-weight: bold; text-decoration: underline;")
        ip_label = QLabel("IP Address:")
        api_label = QLabel("API Key:")
        self.chamber_ip_line_edit = QLineEdit()
        self.chamber_api_line_edit = QLineEdit()
        chamber_connect_button = QPushButton("Connect")
        chamber_connect_button.pressed.connect(self.dummy_function)             # ToDo connect right function
        self.chamber_connection_status_label = QLabel("Status: Not Connected")
        self.chamber_connection_status_label.setStyleSheet("color : red;")

        chamber_connect_layout.addWidget(title_label)
        chamber_connect_layout.addWidget(ip_label)
        chamber_connect_layout.addWidget(self.chamber_ip_line_edit)
        chamber_connect_layout.addWidget(api_label)
        chamber_connect_layout.addWidget(self.chamber_api_line_edit)

        mini_layout = QHBoxLayout()
        mini_layout.addWidget(chamber_connect_button)
        mini_layout.addWidget(self.chamber_connection_status_label)
        chamber_connect_layout.addLayout(mini_layout)
        return chamber_connect_widget

    def __init_vna_connection_block(self):
        vna_connect_widget = QWidget()
        vna_connect_layout = QVBoxLayout()
        vna_connect_widget.setLayout(vna_connect_layout)

        title_label = QLabel("VNA Connection")
        title_label.setStyleSheet("font-weight: bold; text-decoration: underline;")
        ip_label = QLabel("IP Address:")
        dummy_label = QLabel("Dummy-label:")
        self.vna_ip_line_edit = QLineEdit()
        self.vna_dummy_line_edit = QLineEdit()
        vna_connect_button = QPushButton("Connect")
        vna_connect_button.pressed.connect(self.dummy_function)                 # ToDo connect right function
        self.vna_connection_status_label = QLabel("Status: Not Connected")
        self.vna_connection_status_label.setStyleSheet("color : red;")

        vna_connect_layout.addWidget(title_label)
        vna_connect_layout.addWidget(ip_label)
        vna_connect_layout.addWidget(self.vna_ip_line_edit)
        vna_connect_layout.addWidget(dummy_label)
        vna_connect_layout.addWidget(self.vna_dummy_line_edit)

        mini_layout = QHBoxLayout()
        mini_layout.addWidget(vna_connect_button)
        mini_layout.addWidget(self.vna_connection_status_label)
        vna_connect_layout.addLayout(mini_layout)
        return vna_connect_widget

    # def


    def dummy_function(self):
        print("TestString")
        return