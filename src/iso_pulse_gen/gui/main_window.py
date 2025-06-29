from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isochronic Pulse Generator")
        self.setMinimumSize(600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        placeholder_label = QLabel("Isochronic Pulse Generator - Development in Progress")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder_label)