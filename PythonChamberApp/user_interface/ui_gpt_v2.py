import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QMainWindow, QMenuBar
from PyQt6.QtGui import QAction


class ConnectionWidget(QWidget):
    def __init__(self, title):
        super().__init__()

        # Layout
        layout = QVBoxLayout()

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; text-decoration: underline;")
        layout.addWidget(title_label)

        # IP Address
        ip_label = QLabel("IP Address:")
        self.ip_line_edit = QLineEdit()
        layout.addWidget(ip_label)
        layout.addWidget(self.ip_line_edit)

        # API Key
        api_key_label = QLabel("API Key:")
        self.api_key_line_edit = QLineEdit()
        layout.addWidget(api_key_label)
        layout.addWidget(self.api_key_line_edit)

        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.connect_button)

        # Status label
        self.status_label = QLabel("Status: Not Connected")
        layout.addWidget(self.status_label)

        # Connect button clicked event
        self.connect_button.clicked.connect(self.connect)

        self.setLayout(layout)

        # Set border style for the entire widget
        self.setStyleSheet("border: none;")

    def connect(self):
        ip_address = self.ip_line_edit.text()
        api_key = self.api_key_line_edit.text()

        # Check if IP address and API key are not empty
        if not ip_address or not api_key:
            QMessageBox.warning(self, "Warning", "IP address and API key cannot be empty!")
            return

        # Add your connection logic here
        # For demonstration purposes, just print the IP address and API key
        print("Connecting to:", ip_address)
        print("API Key:", api_key)

        # Assume connection is successful for demonstration
        self.status_label.setText("Status: Connected")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connection Settings")
        self.setGeometry(100, 100, 800, 400)  # Set window dimensions

        # Create menu bar
        menu_bar = self.menuBar()

        # Create Measurement Setup action
        measurement_setup_action = QAction("Measurement Setup", self)
        measurement_setup_action.triggered.connect(self.show_measurement_setup)
        menu_bar.addAction(measurement_setup_action)

        # Create Manual Chamber Control action
        manual_chamber_control_action = QAction("Manual Chamber Control", self)
        manual_chamber_control_action.triggered.connect(self.show_manual_chamber_control)
        menu_bar.addAction(manual_chamber_control_action)

        # Create Process Control action
        process_control_action = QAction("Process Control", self)
        process_control_action.triggered.connect(self.show_process_control)
        menu_bar.addAction(process_control_action)

        # Set default window to Measurement Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.show_measurement_setup()

    def show_measurement_setup(self):
        self.central_widget.deleteLater()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create and set Measurement Setup widget
        measurement_setup_widget = QWidget()
        measurement_setup_layout = QVBoxLayout(measurement_setup_widget)
        measurement_setup_layout.addWidget(ConnectionWidget("Chamber Connection"))
        measurement_setup_layout.addWidget(ConnectionWidget("Network Analyzer Connection"))
        self.central_widget.setLayout(measurement_setup_layout)

    def show_manual_chamber_control(self):
        self.central_widget.deleteLater()
        self.central_widget = QLabel("Manual Chamber Control")
        self.setCentralWidget(self.central_widget)

    def show_process_control(self):
        self.central_widget.deleteLater()
        self.central_widget = QLabel("Process Control")
        self.setCentralWidget(self.central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())