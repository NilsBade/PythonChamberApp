import sys
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit
from PyQt6.QtCore import Qt
from datetime import datetime


class UI_vna_control_window(QWidget):
    # Properties
    visa_command_line_edit: QLineEdit = None
    visa_write_button: QPushButton = None
    visa_read_button: QPushButton = None
    visa_query_button: QPushButton = None
    vna_console_textbox: QTextEdit = None

    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout()
        left_widget = QWidget()
        left_widget.setMaximumWidth(300)
        left_column_layout = QGridLayout()
        left_widget.setLayout(left_column_layout)

        command_title = QLabel("Custom GPIB VISA commands")
        command_title.setStyleSheet("font-weight: bold; text-decoration: underline;")
        command_label = QLabel("Visa string:")
        self.visa_command_line_edit = QLineEdit()
        self.visa_write_button = QPushButton('write')
        self.visa_read_button = QPushButton('read')
        self.visa_query_button = QPushButton('query')

        left_column_layout.addWidget(command_title, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        left_column_layout.addWidget(command_label, 1, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)
        left_column_layout.addWidget(self.visa_command_line_edit, 2, 0, 1, 3)
        left_column_layout.addWidget(self.visa_read_button, 3, 0, 1, 1)
        left_column_layout.addWidget(self.visa_write_button, 3, 1, 1, 1)
        left_column_layout.addWidget(self.visa_query_button, 3, 2, 1, 1)
        left_column_layout.setRowStretch(4, 1)

        right_column = QVBoxLayout()
        self.vna_console_textbox = QTextEdit()
        self.vna_console_textbox.setReadOnly(True)
        self.vna_console_textbox.setPlainText(
            "Here are all custom commands logged that are sent and received to and by the vna.\n")
        console_clear_button = QPushButton("Clear Console")
        console_clear_button.pressed.connect(self.clear_console)
        mini_layout = QHBoxLayout()
        mini_layout.addWidget(console_clear_button)
        mini_layout.addStretch()

        right_column.addWidget(self.vna_console_textbox)
        right_column.addLayout(mini_layout)

        main_layout.addWidget(left_widget)
        main_layout.addLayout(right_column)

        self.setLayout(main_layout)

    def append_message2console(self, message: str):
        """
        Adds the given 'message: str' with extra timestamp to the console field in the config window.
        """
        time_now = datetime.now()
        timestamp = time_now.strftime("%H:%M:%S")
        new_text = '[' + timestamp + ']: ' + message
        self.vna_console_textbox.append(new_text)
        return

    def clear_console(self):
        """
        Clears all console entries.
        """
        self.vna_console_textbox.setPlainText("...Console was cleared...\n")
        return

    def get_visa_string(self):
        """
        :return: string that is put in 'visa string' edit line.
        """
        return str(self.visa_command_line_edit.text())
