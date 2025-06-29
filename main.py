import sys
from src.iso_pulse_gen.gui.main_window import MainWindow
from PySide6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Isochronic Pulse Generator")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
