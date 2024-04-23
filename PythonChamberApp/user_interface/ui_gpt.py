import sys
from idlelib import statusbar

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QFrame, QStatusBar

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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connection Settings")
        self.setGeometry(100, 100, 800, 400)  # Set window dimensions

        # Main Layout
        main_layout = QVBoxLayout()

        # Center Widget
        center_layout = QHBoxLayout()
        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        center_widget.setStyleSheet("border: none;")

        # Left Group
        left_group_layout = QVBoxLayout()
        left_group_widget = QWidget()
        left_group_widget.setStyleSheet("border: 2px solid black; border-radius: 5px;")
        left_group_widget.setLayout(left_group_layout)

        # Upper Left Group
        upper_group_layout = QVBoxLayout() #nötig für einzelnen Rahmen
        upper_group_widget = QWidget()
        upper_group_widget.setLayout(upper_group_layout) #nötig für einzelnen Rahmen
        chamber_connection_widget = ConnectionWidget("Chamber Connection")
        upper_group_layout.addWidget(chamber_connection_widget)
        left_group_layout.addWidget(upper_group_widget)

        # Separator
        left_group_layout.addSpacing(20)

        # Lower Left Group
        lower_group_layout = QVBoxLayout() #nötig für einzelnen Rahmen
        lower_group_widget = QWidget()
        lower_group_widget.setLayout(lower_group_layout) #nötig für einzelnen Rahmen
        network_analyzer_connection_widget = ConnectionWidget("Network Analyzer Connection")
        lower_group_layout.addWidget(network_analyzer_connection_widget)
        left_group_layout.addWidget(lower_group_widget)

        # Add left group widget to center layout
        center_layout.addWidget(left_group_widget)

        # Right Group
        right_group_widget = QLabel("Third Widget")
        right_group_widget.setStyleSheet("border: 2px solid black; border-radius: 5px;")

        #right_group_layout = QVBoxLayout(right_group_widget)
        #right_group_layout.addWidget(QLabel("Third Widget"))

        # Add right group widget to center layout
        center_layout.addWidget(right_group_widget, 2)   # Set the stretch factor to 2

        # Add center widget to main layout
        main_layout.addWidget(center_widget)

        # Status Bar
        status_bar = QStatusBar()
        status_bar.showMessage("Hier steht der Programmstatus (Platzhalter) - Ready")
        status_bar.setFixedHeight(20)
        main_layout.addWidget(status_bar)

        self.setLayout(main_layout)

    # def update_statusbar(self, status_string):
    #     self.setStatusTip(self, status_string)
    #     return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    # main_window.update_statusbar("updated!")
    sys.exit(app.exec())