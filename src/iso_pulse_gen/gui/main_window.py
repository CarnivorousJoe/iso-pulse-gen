from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QMessageBox,
)
from PySide6.QtGui import QDoubleValidator
from ..audio.stream_manager import AudioStreamManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isochronic Pulse Generator")
        self.setMinimumSize(600, 400)
        self.setMaximumSize(800, 500)

        self.audio_manager = AudioStreamManager()
        
        # Show audio backend in title if using mock
        if self.audio_manager.backend == "mock":
            self.setWindowTitle("Isochronic Pulse Generator (Mock Audio - No Sound)")

        self._init_ui()
        self._connect_signals()
        self._update_ui_state()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)

        left_group = self._create_channel_group("Left Channel", is_left=True)
        main_layout.addWidget(left_group)

        self.link_channels_checkbox = QCheckBox("Link Channels")
        self.link_channels_checkbox.setChecked(True)
        main_layout.addWidget(self.link_channels_checkbox)

        right_group = self._create_channel_group("Right Channel", is_left=False)
        main_layout.addWidget(right_group)

        controls_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.setMinimumHeight(40)
        controls_layout.addWidget(self.play_button)

        main_layout.addLayout(controls_layout)
        main_layout.addStretch()

    def _create_channel_group(self, title: str, is_left: bool) -> QGroupBox:
        group = QGroupBox(title)
        layout = QGridLayout()

        layout.addWidget(QLabel("Carrier Frequency (Hz):"), 0, 0)
        carrier_input = QLineEdit("440")
        carrier_input.setValidator(QDoubleValidator(0.1, 20000.0, 2))
        layout.addWidget(carrier_input, 0, 1)

        layout.addWidget(QLabel("Pulse Frequency (Hz):"), 1, 0)
        pulse_input = QLineEdit("10")
        pulse_input.setValidator(QDoubleValidator(0.1, 100.0, 2))
        layout.addWidget(pulse_input, 1, 1)

        group.setLayout(layout)

        if is_left:
            self.left_carrier_input = carrier_input
            self.left_pulse_input = pulse_input
        else:
            self.right_carrier_input = carrier_input
            self.right_pulse_input = pulse_input

        return group

    def _connect_signals(self):
        self.play_button.clicked.connect(self._on_play_clicked)
        self.link_channels_checkbox.toggled.connect(self._on_link_channels_toggled)

        self.left_carrier_input.textChanged.connect(self._on_left_params_changed)
        self.left_pulse_input.textChanged.connect(self._on_left_params_changed)
        self.right_carrier_input.textChanged.connect(self._on_right_params_changed)
        self.right_pulse_input.textChanged.connect(self._on_right_params_changed)

    def _on_play_clicked(self):
        try:
            self._update_audio_parameters()
            is_playing = self.audio_manager.toggle_playback()
            self.play_button.setText("Pause" if is_playing else "Play")
        except Exception as e:
            QMessageBox.critical(
                self, "Audio Error", f"Failed to start audio: {str(e)}"
            )

    def _on_link_channels_toggled(self, checked: bool):
        self.audio_manager.set_channels_linked(checked)
        self._update_ui_state()

        if checked:
            self._sync_right_to_left()

    def _on_left_params_changed(self):
        if self.link_channels_checkbox.isChecked():
            self._sync_right_to_left()

    def _on_right_params_changed(self):
        if self.link_channels_checkbox.isChecked():
            self._sync_left_to_right()

    def _sync_right_to_left(self):
        self.right_carrier_input.setText(self.left_carrier_input.text())
        self.right_pulse_input.setText(self.left_pulse_input.text())

    def _sync_left_to_right(self):
        self.left_carrier_input.setText(self.right_carrier_input.text())
        self.left_pulse_input.setText(self.right_pulse_input.text())

    def _update_ui_state(self):
        linked = self.link_channels_checkbox.isChecked()
        self.right_carrier_input.setEnabled(not linked)
        self.right_pulse_input.setEnabled(not linked)

    def _update_audio_parameters(self):
        try:
            left_carrier = float(self.left_carrier_input.text() or "440")
            left_pulse = float(self.left_pulse_input.text() or "10")
            self.audio_manager.set_left_parameters(left_carrier, left_pulse)

            if not self.link_channels_checkbox.isChecked():
                right_carrier = float(self.right_carrier_input.text() or "440")
                right_pulse = float(self.right_pulse_input.text() or "10")
                self.audio_manager.set_right_parameters(right_carrier, right_pulse)
        except ValueError:
            pass

    def closeEvent(self, event):
        self.audio_manager.stop()
        event.accept()
