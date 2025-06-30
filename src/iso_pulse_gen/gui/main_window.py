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
    QComboBox,
    QTextEdit,
    QSplitter,
)
from PySide6.QtGui import QDoubleValidator, QFont
from PySide6.QtCore import Qt, QObject, Signal
from ..audio.stream_manager import AudioStreamManager
import logging
import sys
from datetime import datetime


class LogHandler(logging.Handler, QObject):
    """Custom logging handler that emits signals for GUI updates"""
    log_signal = Signal(str)
    
    def __init__(self):
        super().__init__()
        QObject.__init__(self)
        
    def emit(self, record):
        log_entry = self.format(record)
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        formatted_entry = f"[{timestamp}] {log_entry}"
        self.log_signal.emit(formatted_entry)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isochronic Pulse Generator")
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1200, 800)

        # Set up logging first
        self._setup_logging()

        self.audio_manager = AudioStreamManager()

        # Show audio backend in title if using mock
        if self.audio_manager.backend == "mock":
            self.setWindowTitle("Isochronic Pulse Generator (Mock Audio - No Sound)")

        self.logger = logging.getLogger(__name__)
        self.logger.info("Application started")
        self.logger.info(f"Audio backend: {self.audio_manager.backend}")

        self._init_ui()
        self._connect_signals()
        self._update_ui_state()

    def _setup_logging(self):
        """Set up logging system with GUI handler"""
        # Create custom log handler for GUI
        self.log_handler = LogHandler()
        self.log_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(self.log_handler)
        
        # Also add console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create splitter for main controls and logging
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)

        # Top section - Main controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(15)

        # Audio Device Selection
        device_group = self._create_device_selection_group()
        controls_layout.addWidget(device_group)

        left_group = self._create_channel_group("Left Channel", is_left=True)
        controls_layout.addWidget(left_group)

        self.link_channels_checkbox = QCheckBox("Link Channels")
        self.link_channels_checkbox.setChecked(True)
        controls_layout.addWidget(self.link_channels_checkbox)

        right_group = self._create_channel_group("Right Channel", is_left=False)
        controls_layout.addWidget(right_group)

        play_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.setMinimumHeight(40)
        play_layout.addWidget(self.play_button)
        play_layout.addStretch()

        controls_layout.addLayout(play_layout)
        controls_layout.addStretch()

        splitter.addWidget(controls_widget)

        # Bottom section - Logging display
        log_group = QGroupBox("System Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(200)
        self.log_display.setMinimumHeight(100)
        
        # Use monospace font for better readability
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Monaco", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.log_display.setFont(font)
        
        log_layout.addWidget(self.log_display)
        
        # Add clear button for log
        log_controls = QHBoxLayout()
        clear_log_button = QPushButton("Clear Log")
        clear_log_button.setMaximumWidth(100)
        clear_log_button.clicked.connect(self.log_display.clear)
        log_controls.addWidget(clear_log_button)
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        splitter.addWidget(log_group)
        
        # Set splitter proportions (2/3 controls, 1/3 log)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

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

    def _create_device_selection_group(self) -> QGroupBox:
        group = QGroupBox("Audio Output Device")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(300)
        layout.addWidget(self.device_combo)

        # Add refresh button for device list
        refresh_button = QPushButton("Refresh")
        refresh_button.setMaximumWidth(80)
        refresh_button.clicked.connect(self._refresh_devices)
        layout.addWidget(refresh_button)

        layout.addStretch()
        group.setLayout(layout)

        # Populate devices on startup
        self._refresh_devices()

        return group

    def _connect_signals(self):
        self.play_button.clicked.connect(self._on_play_clicked)
        self.link_channels_checkbox.toggled.connect(self._on_link_channels_toggled)
        self.device_combo.currentIndexChanged.connect(self._on_device_changed)

        self.left_carrier_input.textChanged.connect(self._on_left_params_changed)
        self.left_pulse_input.textChanged.connect(self._on_left_params_changed)
        self.right_carrier_input.textChanged.connect(self._on_right_params_changed)
        self.right_pulse_input.textChanged.connect(self._on_right_params_changed)
        
        # Connect log handler to display
        self.log_handler.log_signal.connect(self._append_log)

    def _append_log(self, message: str):
        """Append log message to the display and auto-scroll"""
        self.log_display.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_play_clicked(self):
        try:
            self.logger.info("Play button clicked")
            self._update_audio_parameters()
            
            # Log current parameters before starting
            left_carrier = self.left_carrier_input.text()
            left_pulse = self.left_pulse_input.text()
            right_carrier = self.right_carrier_input.text()
            right_pulse = self.right_pulse_input.text()
            
            self.logger.info(f"Audio parameters - Left: {left_carrier}Hz carrier, {left_pulse}Hz pulse")
            if not self.link_channels_checkbox.isChecked():
                self.logger.info(f"Audio parameters - Right: {right_carrier}Hz carrier, {right_pulse}Hz pulse")
            else:
                self.logger.info("Channels linked - using left parameters for both")
            
            is_playing = self.audio_manager.toggle_playback()
            action = "Started" if is_playing else "Stopped"
            self.logger.info(f"Audio playback {action}")
            self.play_button.setText("Pause" if is_playing else "Play")
            
        except Exception as e:
            self.logger.error(f"Failed to toggle audio playback: {str(e)}")
            QMessageBox.critical(
                self, "Audio Error", f"Failed to start audio: {str(e)}"
            )

    def _on_link_channels_toggled(self, checked: bool):
        self.logger.info(f"Channel linking {'enabled' if checked else 'disabled'}")
        self.audio_manager.set_channels_linked(checked)
        self._update_ui_state()

        if checked:
            self._sync_right_to_left()
            self.logger.info("Right channel synced to left channel parameters")

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

    def _refresh_devices(self):
        """Refresh the list of available audio devices"""
        try:
            self.device_combo.clear()

            # Add default device option
            self.device_combo.addItem("Default Device", None)

            # Get available devices
            devices = self.audio_manager.get_available_devices()
            for device in devices:
                device_name = f"{device['name']} ({device['channels']} ch, {device['default_samplerate']:.0f} Hz)"
                self.device_combo.addItem(device_name, device["index"])

        except Exception as e:
            QMessageBox.warning(
                self,
                "Device Enumeration Error",
                f"Could not enumerate audio devices: {str(e)}",
            )

    def _on_device_changed(self, index):
        """Handle audio device selection change"""
        try:
            device_index = self.device_combo.itemData(index)
            device_name = self.device_combo.itemText(index)
            self.logger.info(f"Audio device changed to: {device_name}")
            
            self.audio_manager.set_output_device(device_index)

            # Show selected device info in status
            device_info = self.audio_manager.get_current_device_info()
            if self.audio_manager.backend == "mock":
                self.logger.info(f"Selected device: {device_info['name']} (Mock Backend - No Audio Output)")
            else:
                self.logger.info(f"Selected device: {device_info['name']} - {device_info.get('channels', 'Unknown')} channels, {device_info.get('default_samplerate', 'Unknown')} Hz")

        except Exception as e:
            self.logger.error(f"Could not set audio device: {str(e)}")
            QMessageBox.critical(
                self, "Device Selection Error", f"Could not set audio device: {str(e)}"
            )

    def closeEvent(self, event):
        self.logger.info("Application closing")
        self.audio_manager.stop()
        event.accept()
