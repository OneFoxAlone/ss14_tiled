"""GUI application for SS14 Tiled tileset generation."""
import sys
import threading
import time
import os
import warnings
import traceback
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar,
    QTextEdit, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont

from .generate import generate
from .shared import eprint

# Suppress libpng warnings about color profiles
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'
warnings.filterwarnings('ignore')


class WorkerSignals(QObject):
    """Signals for worker thread."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    progress_percent = pyqtSignal(int)


class GenerateWorker(threading.Thread):
    """Worker thread for generation task."""
    def __init__(self, ss14_path: Path, output_path: Path):
        super().__init__(daemon=True)
        self.ss14_path = ss14_path
        self.output_path = output_path
        self.signals = WorkerSignals()
        self._stop_event = threading.Event()

    def stop(self):
        """Signal the worker to stop."""
        self._stop_event.set()

    def run(self):
        """Run the generation."""
        try:
            self.signals.progress.emit(f"[{self._get_timestamp()}] Starting tileset generation...\n")
            self.signals.progress.emit(f"[{self._get_timestamp()}] SS14 Repository: {self.ss14_path}\n")
            self.signals.progress.emit(f"[{self._get_timestamp()}] Output Directory: {self.output_path}\n")
            self.signals.progress.emit(f"[{self._get_timestamp()}] Validating repository structure...\n")
            self.signals.progress_percent.emit(5)
            
            # Change to output directory for generation
            old_cwd = os.getcwd()
            os.chdir(self.output_path)
            
            try:
                # Capture all stdout/stderr to display in log
                import io
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                
                captured_output = io.StringIO()
                
                class OutputCapture:
                    """Captures output and filters unwanted warnings."""
                    def __init__(self, original, capture_stream):
                        self.original = original
                        self.capture = capture_stream
                    
                    def write(self, msg):
                        if msg and msg.strip():
                            # Filter out libpng warnings
                            if 'libpng warning' not in msg.lower() and 'iCCP' not in msg:
                                self.original.write(msg)
                                self.capture.write(msg)
                    
                    def flush(self):
                        self.original.flush()
                        self.capture.flush()
                
                capture_out = OutputCapture(old_stdout, captured_output)
                capture_err = OutputCapture(old_stderr, captured_output)
                
                sys.stdout = capture_out
                sys.stderr = capture_err
                
                # Define progress callback
                def progress_callback(current, total):
                    percent = int((current / total) * 100) if total > 0 else 0
                    self.signals.progress_percent.emit(percent)
                
                try:
                    generate(self.ss14_path, progress_callback, self.output_path)
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                
                # Display captured output
                captured = captured_output.getvalue()
                if captured.strip():
                    self.signals.progress.emit(f"\n[{self._get_timestamp()}] Generation Output:\n")
                    self.signals.progress.emit(captured)
                
                self.signals.progress.emit(f"\n[{self._get_timestamp()}] ✓ Tileset generation completed successfully!\n")
                self.signals.progress.emit(f"[{self._get_timestamp()}] Output files created in: {self.output_path}\n")
                self.signals.progress_percent.emit(100)
                self.signals.finished.emit()
            finally:
                os.chdir(old_cwd)
        except Exception as e:
            error_msg = str(e) if str(e) else type(e).__name__
            tb = traceback.format_exc()
            self.signals.error.emit(f"[{self._get_timestamp()}] Error during generation: {error_msg}\n\nTraceback:\n{tb}")
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp for logging."""
        return time.strftime("%H:%M:%S")


class SS14TiledGUI(QMainWindow):
    """Main GUI application window."""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.output_path = Path("dist").absolute()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("SS14 Tiled - Tileset Generator")
        self.setGeometry(100, 100, 900, 700)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("SS14 Tiled Tileset Generator")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Description
        description = QLabel(
            "Select your Space Station 14 repository folder and configure output, "
            "then click 'Generate' to create tileset files."
        )
        description.setWordWrap(True)
        main_layout.addWidget(description)
        
        # SS14 Folder selection
        folder_layout = QHBoxLayout()
        folder_label = QLabel("SS14 Folder:")
        folder_label.setMinimumWidth(100)
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select your SS14 repository...")
        self.folder_input.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_button)
        main_layout.addLayout(folder_layout)
        
        # Output directory selection
        output_layout = QHBoxLayout()
        output_label = QLabel("Output:")
        output_label.setMinimumWidth(100)
        self.output_display = QLineEdit()
        self.output_display.setText(str(self.output_path))
        self.output_display.setReadOnly(True)
        output_browse_button = QPushButton("Browse...")
        output_browse_button.clicked.connect(self.browse_output_folder)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_display)
        output_layout.addWidget(output_browse_button)
        main_layout.addLayout(output_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Tileset")
        self.generate_button.clicked.connect(self.generate_tileset)
        self.generate_button.setMinimumHeight(40)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_generation)
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setEnabled(False)
        
        open_output_button = QPushButton("Open Output Folder")
        open_output_button.clicked.connect(self.open_output_folder)
        open_output_button.setMinimumHeight(40)
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(open_output_button)
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Output text area
        log_label = QLabel("Generation Log:")
        log_font = QFont()
        log_font.setBold(True)
        log_label.setFont(log_font)
        main_layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(300)
        main_layout.addWidget(self.log_output)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def browse_folder(self):
        """Open folder browser dialog for SS14 repository."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select SS14 Repository",
            str(Path.home())
        )
        if folder:
            self.folder_input.setText(folder)
            self.log_output.append(f"[INFO] Selected SS14 folder: {folder}")
    
    def browse_output_folder(self):
        """Open folder browser dialog for output directory."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            str(self.output_path)
        )
        if folder:
            self.output_path = Path(folder)
            self.output_display.setText(str(self.output_path))
            self.log_output.append(f"[INFO] Selected output folder: {folder}")
    
    def generate_tileset(self):
        """Start tileset generation."""
        folder_path = self.folder_input.text().strip()
        
        if not folder_path:
            self.log_output.setText("Error: Please select an SS14 folder first!")
            self.statusBar().showMessage("Error: No folder selected")
            return
        
        ss14_path = Path(folder_path)
        if not ss14_path.exists():
            self.log_output.setText(f"Error: Folder does not exist: {folder_path}")
            self.statusBar().showMessage("Error: Folder does not exist")
            return
        
        if not self.output_path.exists():
            try:
                self.output_path.mkdir(parents=True, exist_ok=True)
                self.log_output.append(f"[INFO] Created output directory: {self.output_path}")
            except Exception as e:
                self.log_output.setText(f"Error: Cannot create output directory: {str(e)}")
                self.statusBar().showMessage("Error: Cannot create output directory")
                return
        
        # Disable controls during generation
        self.generate_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate progress
        self.log_output.clear()
        self.statusBar().showMessage("Generating tileset...")
        
        # Create and start worker thread
        self.worker = GenerateWorker(ss14_path, self.output_path)
        self.worker.signals.progress.connect(self.append_log)
        self.worker.signals.progress_percent.connect(self.update_progress)
        self.worker.signals.finished.connect(self.generation_finished)
        self.worker.signals.error.connect(self.generation_error)
        self.worker.start()
    
    def cancel_generation(self):
        """Cancel the ongoing generation."""
        if self.worker:
            self.log_output.append("\n[WARNING] Cancellation requested...")
            self.worker.stop()
            self.cancel_generation_finished()
    
    def cancel_generation_finished(self):
        """Handle generation cancellation."""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.statusBar().showMessage("Generation cancelled")
        self.log_output.append("[INFO] Generation cancelled by user")
    
    def append_log(self, message: str):
        """Append message to log."""
        self.log_output.append(message)
    
    def update_progress(self, percent: int):
        """Update the progress bar."""
        self.progress_bar.setValue(min(100, max(0, percent)))
    
    def generation_finished(self):
        """Handle generation completion."""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.statusBar().showMessage("Generation completed successfully!")
    
    def generation_error(self, error: str):
        """Handle generation error."""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.log_output.append(f"\n{error}")
        self.statusBar().showMessage("Error during generation")
    
    def open_output_folder(self):
        """Open the output folder."""
        if self.output_path.exists():
            import subprocess
            subprocess.Popen(f'explorer "{self.output_path}"')
        else:
            self.log_output.append("[INFO] Output folder does not exist yet. Generate tileset first!")


def main():
    """Run the GUI application."""
    app = QApplication(sys.argv)
    window = SS14TiledGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
