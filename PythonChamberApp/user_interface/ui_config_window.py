import sys
from PyQt6.QtWidgets import QWidget, QLineEdit,QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow


class UI_config_window(QWidget):

    configdata: int = 10
    def __init__(self):
        super().__init__()

        label = QLabel("ich bin config widget")

        main_layout = QVBoxLayout()
        main_layout.addWidget(label)

        self.setLayout(main_layout)