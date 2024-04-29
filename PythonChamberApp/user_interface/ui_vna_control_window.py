import sys
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout


class UI_vna_control_window(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel("ich bin VNA widget")

        main_layout = QVBoxLayout()
        main_layout.addWidget(label)

        self.setLayout(main_layout)