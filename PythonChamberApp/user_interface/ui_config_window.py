import sys
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit
from PyQt6.QtCore import QCoreApplication
from datetime import datetime


class UI_config_window(QWidget):

    # Properties
    chamber_ip_line_edit: QLineEdit = None
    chamber_api_line_edit: QLineEdit = None
    chamber_connection_status_label: QLabel = None
    chamber_connect_button: QPushButton = None

    vna_ip_line_edit: QLineEdit = None
    vna_dummy_line_edit: QLineEdit = None
    vna_connection_status_label: QLabel = None
    vna_connect_button: QPushButton = None

    config_console_textbox: QTextEdit = None

    def __init__(self):
        super().__init__()

        # build main widgets
        chamber_connect_widget = self.__init_chamber_connection_block()
        vna_connect_widget = self.__init_vna_connection_block()
        self.config_console_widget = self.__init_console_field()

        # setup overall layout
        main_layout = QHBoxLayout()

        main_left_layout = QVBoxLayout()
        main_left_layout.addWidget(chamber_connect_widget)
        main_left_layout.addWidget(vna_connect_widget)
        main_left_layout.addStretch()

        main_layout.addLayout(main_left_layout, stretch=0)

        main_layout.addWidget(self.config_console_widget, stretch=2)

        self.setLayout(main_layout)

    def __init_chamber_connection_block(self):
        chamber_connect_widget = QWidget()
        chamber_connect_widget.setMinimumWidth(250)
        chamber_connect_layout = QVBoxLayout()
        chamber_connect_widget.setLayout(chamber_connect_layout)

        title_label = QLabel("Chamber Connection")
        title_label.setStyleSheet("font-weight: bold; text-decoration: underline;")
        ip_label = QLabel("IP Address:")
        api_label = QLabel("API Key:")
        self.chamber_ip_line_edit = QLineEdit()
        self.chamber_ip_line_edit.setInputMask("000.000.000.000")
        self.chamber_api_line_edit = QLineEdit()
        self.chamber_connect_button = QPushButton("Connect")
        self.chamber_connection_status_label = QLabel("Status: Not Connected")
        self.chamber_connection_status_label.setStyleSheet("color : red;")

        chamber_connect_layout.addWidget(title_label)
        chamber_connect_layout.addWidget(ip_label)
        chamber_connect_layout.addWidget(self.chamber_ip_line_edit)
        chamber_connect_layout.addWidget(api_label)
        chamber_connect_layout.addWidget(self.chamber_api_line_edit)

        mini_layout = QHBoxLayout()
        mini_layout.addWidget(self.chamber_connect_button)
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
        self.vna_connect_button = QPushButton("Connect")
        self.vna_connection_status_label = QLabel("Status: Not Connected")
        self.vna_connection_status_label.setStyleSheet("color : red;")

        vna_connect_layout.addWidget(title_label)
        vna_connect_layout.addWidget(ip_label)
        vna_connect_layout.addWidget(self.vna_ip_line_edit)
        vna_connect_layout.addWidget(dummy_label)
        vna_connect_layout.addWidget(self.vna_dummy_line_edit)

        mini_layout = QHBoxLayout()
        mini_layout.addWidget(self.vna_connect_button)
        mini_layout.addWidget(self.vna_connection_status_label)
        vna_connect_layout.addLayout(mini_layout)
        return vna_connect_widget

    def __init_console_field(self):
        console_layout = QVBoxLayout()
        console_widget = QWidget()
        console_widget.setLayout(console_layout)

        self.config_console_textbox = QTextEdit()
        self.config_console_textbox.setReadOnly(True)
        self.config_console_textbox.setPlainText("Here are all logged messages displayed the process controller "
                                                 "receives...\nPlease input your network device's network parameters "
                                                 "on the left and click 'Connect' to enable more functionality!")

        console_clear_button = QPushButton("Clear Console")
        console_clear_button.pressed.connect(self.clear_console)
        mini_layout = QHBoxLayout()
        mini_layout.addWidget(console_clear_button)
        mini_layout.addStretch()

        console_layout.addWidget(self.config_console_textbox)
        console_layout.addLayout(mini_layout)

        return console_widget

    def append_message2console(self, message: str):
        """
        Adds the given 'message: str' with extra timestamp to the console field in the config window.
        """
        time_now = datetime.now()
        timestamp = time_now.strftime("%H:%M:%S")
        new_text = '[' + timestamp + ']: ' + message
        self.config_console_textbox.append(new_text)
        return

    def clear_console(self):
        """
        Clears all console entries.
        """
        self.config_console_textbox.setPlainText("...Console was cleared...\n")
        return

    def get_chamber_connect_data(self):
        """
        Returns a dict with {ip_address: str, api_key: str} that are written to the line edits at the moment.
        """
        return {'ip_address': self.chamber_ip_line_edit.text(), 'api_key': self.chamber_api_line_edit.text()}

    def set_chamber_connected(self, state: bool):
        """
        Toggles the status message of the chamber connection widget.

        True >> 'Status: Connected!', green

        False >> 'Status: Not Connected!', red
        """
        if state:
            self.chamber_connection_status_label.setText("Status : Connected!")
            self.chamber_connection_status_label.setStyleSheet("color: green")
        else:
            self.chamber_connection_status_label.setText("Status: Not Connected!")
            self.chamber_connection_status_label.setStyleSheet("color: red")
        return

    def get_vna_connect_data(self):
        """
        Returns a dict with {ip_address: str, dummy: str} that are written to the line edits at the moment.
        """
        return {'ip_address': self.vna_ip_line_edit.text(), 'DUMMY': self.vna_dummy_line_edit.text()}

    def set_vna_connected(self, state: bool):
        """
            Toggles the status message of the VNA connection widget.

            True >> 'Status: Connected!', green

            False >> 'Status: Not Connected!', red
        """
        if state:
            self.vna_connection_status_label.setText("Status : Connected!")
            self.vna_connection_status_label.setStyleSheet("color: green")
        else:
            self.vna_connection_status_label.setText("Status: Not Connected!")
            self.vna_connection_status_label.setStyleSheet("color: red")
        return

    def dummy_function(self):
        print("Dummy_function activated!")
        self.append_message2console("button pressed! Dummy_function activated!")
        return