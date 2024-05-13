import sys
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit
from PyQt6.QtCore import QCoreApplication
from datetime import datetime

class UI_auto_measurement_window(QWidget):

    # Properties

    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout()
        #  ...
        self.setLayout(main_layout)

        