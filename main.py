import sys
import os
import subprocess
from importlib import import_module


def load_qt_modules():
	try:
		widgets = import_module("PySide6.QtWidgets")
		gui = import_module("PySide6.QtGui")
		core = import_module("PySide6.QtCore")
		multimedia = import_module("PySide6.QtMultimedia")
		multimedia_widgets = import_module("PySide6.QtMultimediaWidgets")
	except ModuleNotFoundError:
		try:
			widgets = import_module("PyQt6.QtWidgets")
			gui = import_module("PyQt6.QtGui")
			core = import_module("PyQt6.QtCore")
			multimedia = import_module("PyQt6.QtMultimedia")
			multimedia_widgets = import_module("PyQt6.QtMultimediaWidgets")
		except ModuleNotFoundError as exc:
			raise RuntimeError(
				"PySide6 or PyQt6 is not installed. Install one with `pip install PySide6`."
			) from exc

	return {
		"QUrl": core.QUrl,
		"Qt": core.Qt,
		"QObject": core.QObject,
		"Signal": getattr(core, "Signal", getattr(core, "pyqtSignal", None)),
		"QRectF": core.QRectF,
		"QPointF": core.QPointF,
		"QSettings": core.QSettings,
		"QTime": core.QTime,
		"QTimer": core.QTimer,
		"QThread": core.QThread,
		"QAction": gui.QAction,
		"QColor": gui.QColor,
		"QImage": gui.QImage,
		"QPixmap": gui.QPixmap,
		"QPainter": gui.QPainter,
		"QPen": gui.QPen,
		"QApplication": widgets.QApplication,
		"QCheckBox": widgets.QCheckBox,
		"QDialog": widgets.QDialog,
		"QFileDialog": widgets.QFileDialog,
		"QFrame": widgets.QFrame,
		"QHBoxLayout": widgets.QHBoxLayout,
		"QLabel": widgets.QLabel,
		"QMainWindow": widgets.QMainWindow,
		"QMessageBox": widgets.QMessageBox,
		"QProgressDialog": widgets.QProgressDialog,
		"QPushButton": widgets.QPushButton,
		"QScrollArea": widgets.QScrollArea,
		"QSpinBox": widgets.QSpinBox,
		"QTimeEdit": widgets.QTimeEdit,
		"QVBoxLayout": widgets.QVBoxLayout,
		"QWidget": widgets.QWidget,
		"QMediaPlayer": multimedia.QMediaPlayer,
		"QAudioOutput": multimedia.QAudioOutput,
		"QVideoSink": multimedia.QVideoSink,
		"QVideoWidget": multimedia_widgets.QVideoWidget,
		"QVideoWidget": multimedia_widgets.QVideoWidget,
	}

qt = load_qt_modules()
QUrl = qt["QUrl"]
Qt = qt["Qt"]
QObject = qt["QObject"]
Signal = qt["Signal"]
QRectF = qt["QRectF"]
QPointF = qt["QPointF"]
QSettings = qt["QSettings"]
QTime = qt["QTime"]
QTimer = qt["QTimer"]
QThread = qt["QThread"]
QAction = qt["QAction"]
QColor = qt["QColor"]
QImage = qt["QImage"]
QPixmap = qt["QPixmap"]
QPainter = qt["QPainter"]
QPen = qt["QPen"]
QApplication = qt["QApplication"]
QCheckBox = qt["QCheckBox"]
QDialog = qt["QDialog"]
QFileDialog = qt["QFileDialog"]
QFrame = qt["QFrame"]
QHBoxLayout = qt["QHBoxLayout"]
QLabel = qt["QLabel"]
QMainWindow = qt["QMainWindow"]
QMessageBox = qt["QMessageBox"]
QProgressDialog = qt["QProgressDialog"]
QPushButton = qt["QPushButton"]
QScrollArea = qt["QScrollArea"]
QSpinBox = qt["QSpinBox"]
QTimeEdit = qt["QTimeEdit"]
QVBoxLayout = qt["QVBoxLayout"]
QWidget = qt["QWidget"]
QMediaPlayer = qt["QMediaPlayer"]
QAudioOutput = qt["QAudioOutput"]
QVideoSink = qt["QVideoSink"]
QVideoWidget = qt["QVideoWidget"]


class SettingsDialog(QDialog):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Settings")
		self.resize(360, 200)
		self.settings = QSettings("VideoSlicer", "VideoSlicerApp")

		layout = QVBoxLayout()
		
		# Default Pieces
		layout.addWidget(QLabel("Default number of pieces:"))
		self.default_pieces_input = QSpinBox()
		self.default_pieces_input.setMinimum(1)
		self.default_pieces_input.setMaximum(1000)
		self.default_pieces_input.setValue(int(self.settings.value("default_pieces", 4)))
		layout.addWidget(self.default_pieces_input)
		
		# Default Segment Duration
		layout.addWidget(QLabel("Default segment duration:"))
		self.default_time_input = QTimeEdit()
		self.default_time_input.setDisplayFormat("HH:mm:ss")
		default_time_str = str(self.settings.value("default_time", "00:00:30"))
		self.default_time_input.setTime(QTime.fromString(default_time_str, "HH:mm:ss"))
		layout.addWidget(self.default_time_input)

		# Buttons
		btn_layout = QHBoxLayout()
		save_button = QPushButton("Save")
		save_button.clicked.connect(self.save_settings)
		close_button = QPushButton("Cancel")
		close_button.clicked.connect(self.reject)
		
		btn_layout.addStretch(1)
		btn_layout.addWidget(save_button)
		btn_layout.addWidget(close_button)
		layout.addLayout(btn_layout)

		self.setLayout(layout)

	def save_settings(self) -> None:
		self.settings.setValue("default_pieces", self.default_pieces_input.value())
		self.settings.setValue("default_time", self.default_time_input.time().toString("HH:mm:ss"))
		self.accept()


class TimelineWidget(QWidget):
	segment_clicked = Signal(int)

	def __init__(self, parent=None) -> None:
		super().__init__(parent)
		self.setMinimumHeight(40)
		self.setCursor(Qt.CursorShape.PointingHandCursor)
		self.setMouseTracking(True)
		self.video_duration_seconds = 0
		self.current_position_seconds = 0
		self.slice_mode = "pieces"  # "pieces" or "time"
		self.pieces = 4
		self.segment_seconds = 30
		self.hover_index = -1

	def get_segment_index(self, x: float) -> int:
		if self.video_duration_seconds <= 0: return -1
		width = self.width()
		seg_s = 0
		if self.slice_mode == "pieces" and self.pieces > 0:
			seg_s = self.video_duration_seconds / self.pieces
		elif self.slice_mode == "time" and self.segment_seconds > 0:
			seg_s = self.segment_seconds
		if seg_s > 0:
			click_time_s = (x / width) * self.video_duration_seconds
			return int(click_time_s / seg_s)
		return -1

	def mouseMoveEvent(self, event) -> None:
		idx = self.get_segment_index(event.position().x())
		if idx != self.hover_index:
			self.hover_index = idx
			self.update()

	def leaveEvent(self, event) -> None:
		self.hover_index = -1
		self.update()

	def paintEvent(self, event) -> None:
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)

		width = self.width()
		height = self.height()

		# Draw background track
		track_rect = QRectF(0, 10, width, height - 20)
		painter.setBrush(QColor(80, 80, 80))
		painter.setPen(Qt.PenStyle.NoPen)
		painter.drawRoundedRect(track_rect, 4, 4)

		# Pokud není načteno žádné video, skončíme jen u prázdného pozadí (1 velký neaktivní slice)
		if self.video_duration_seconds <= 0:
			return

		# Get segment length
		seg_s = 0
		if self.slice_mode == "pieces" and self.pieces > 0:
			seg_s = self.video_duration_seconds / self.pieces
		elif self.slice_mode == "time" and self.segment_seconds > 0:
			seg_s = self.segment_seconds

		# Hover highlight
		if self.video_duration_seconds > 0 and seg_s > 0 and self.hover_index >= 0:
			start_x = (self.hover_index * seg_s / self.video_duration_seconds) * width
			end_x = ((self.hover_index + 1) * seg_s / self.video_duration_seconds) * width
			if end_x > width:
				end_x = width
			hover_rect = QRectF(start_x, 10, end_x - start_x, height - 20)
			painter.setBrush(QColor(255, 255, 255, 60))  # Semi-transparent white
			painter.setPen(Qt.PenStyle.NoPen)
			painter.drawRoundedRect(hover_rect, 4, 4)

		# Highlight active segment
		if self.video_duration_seconds > 0 and seg_s > 0:
			# Přidáme 300ms (0.3s) toleranci, protože videopřehrávač často skočí 
			# na klíčový snímek lehce před začátkem požadovaného času (např. 29.95s místo 30.0s)
			active_index = int((self.current_position_seconds + 0.3) / seg_s)
			
			start_x = (active_index * seg_s / self.video_duration_seconds) * width
			end_x = ((active_index + 1) * seg_s / self.video_duration_seconds) * width
			
			if end_x > width:
				end_x = width
				
			active_rect = QRectF(start_x, 10, end_x - start_x, height - 20)
			painter.setBrush(Qt.BrushStyle.NoBrush)
			painter.setPen(QPen(QColor(0, 255, 0), 4))
			painter.drawRoundedRect(active_rect, 4, 4)

		# Draw slice separators
		painter.setPen(QPen(QColor(255, 100, 100), 2))

		if self.slice_mode == "pieces" and self.pieces > 0:
			segment_width = width / self.pieces
			for i in range(1, self.pieces):
				x = i * segment_width
				painter.drawLine(QPointF(x, 10), QPointF(x, height - 10))

		elif self.slice_mode == "time" and self.segment_seconds > 0:
			num_segments = self.video_duration_seconds / self.segment_seconds
			if num_segments > 1:
				for i in range(1, int(num_segments)):
					x = (i * self.segment_seconds / self.video_duration_seconds) * width
					painter.drawLine(QPointF(x, 10), QPointF(x, height - 10))
				if num_segments > int(num_segments):
					x = (int(num_segments) * self.segment_seconds / self.video_duration_seconds) * width
					painter.drawLine(QPointF(x, 10), QPointF(x, height - 10))

	def mousePressEvent(self, event) -> None:
		if self.video_duration_seconds <= 0:
			return
			
		x = event.position().x()
		idx = self.get_segment_index(x)
		
		if idx >= 0:
			seg_s = 0
			if self.slice_mode == "pieces" and self.pieces > 0:
				seg_s = self.video_duration_seconds / self.pieces
			elif self.slice_mode == "time" and self.segment_seconds > 0:
				seg_s = self.segment_seconds
				
			if seg_s > 0:
				start_time_ms = int(idx * seg_s * 1000)
				self.segment_clicked.emit(start_time_ms)

class ExportWorker(QThread):
	progress_val = Signal(int)
	progress_text = Signal(str)
	finished_export = Signal(bool, str)

	def __init__(self, input_path, output_path_base, timestamps, parent=None):
		super().__init__(parent)
		self.input_path = input_path
		self.output_path_base = output_path_base
		self.timestamps = timestamps  # list of (start_s, duration_s, index)

	def run(self):
		total = len(self.timestamps)
		base_dir = os.path.dirname(self.output_path_base)
		base_name = os.path.basename(self.output_path_base)
		
		name_part, ext_part = os.path.splitext(base_name)
		if not ext_part:
			_, orig_ext = os.path.splitext(self.input_path)
			ext_part = orig_ext if orig_ext else ".mp4"

		for i, (start_s, duration_s, index) in enumerate(self.timestamps):
			# Vydá signál před začátkem práce na aktuálním videu
			self.progress_val.emit(i)
			self.progress_text.emit(f"Zpracování videa {i + 1} z {total}...")
			
			out_name = f"{name_part}_{index}{ext_part}"
			out_path = os.path.join(base_dir, out_name)

			# Používáme rychlé bezztrátové stříhání přes parametr -c copy
			cmd = [
				"ffmpeg",
				"-y",
				"-ss", str(start_s),
				"-i", self.input_path,
				"-t", str(duration_s),
				"-c", "copy",
				out_path
			]
			
			try:
				subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
			except subprocess.CalledProcessError as e:
				err_msg = e.stderr.decode('utf-8', errors='ignore')
				self.finished_export.emit(False, f"Chyba při exportu části {index}:\n{err_msg}")
				return
			except FileNotFoundError:
				self.finished_export.emit(False, "Program 'ffmpeg' nebyl nalezen. Nainstalujte jej prosím (např. sudo pacman -S ffmpeg).")
				return
				
		self.progress_val.emit(total)
		self.progress_text.emit(f"Hotovo! Bylo exportováno {total} úseků.")
		self.finished_export.emit(True, "Všechna videa byla úspěšně vyexportována.")

class MainWindow(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.setWindowTitle("VideoSlicer")
		self.resize(900, 600)
		self.settings = QSettings("VideoSlicer", "VideoSlicerApp")

		central_widget = QWidget()
		layout = QVBoxLayout()
		layout.setContentsMargins(16, 16, 16, 16)
		layout.setSpacing(16)

		self.video_widget = QVideoWidget()
		self.video_widget.setMinimumHeight(320)
		self.video_widget.setStyleSheet("background-color: black;")
		layout.addWidget(self.video_widget)

		self.player = QMediaPlayer()
		self.audio_output = QAudioOutput()
		self.player.setAudioOutput(self.audio_output)
		self.player.setVideoOutput(self.video_widget)

		playback_layout = QHBoxLayout()
		playback_layout.addStretch(1)
		
		self.btn_start_video = QPushButton("|< Video Start")
		self.btn_start_part = QPushButton("|< Part Start")
		self.btn_play_pause = QPushButton("Play / Pause")
		self.btn_end_part = QPushButton("Part End >|")
		self.btn_end_video = QPushButton("Video End >|")

		playback_layout.addWidget(self.btn_start_video)
		playback_layout.addWidget(self.btn_start_part)
		playback_layout.addWidget(self.btn_play_pause)
		playback_layout.addWidget(self.btn_end_part)
		playback_layout.addWidget(self.btn_end_video)
		playback_layout.addStretch(1)
		
		layout.addLayout(playback_layout)

		self.timeline = TimelineWidget()
		layout.addWidget(self.timeline)

		controls_layout = QHBoxLayout()
		controls_layout.setSpacing(12)
		controls_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
		controls_layout.addStretch(1)

		pieces_panel = QWidget()
		pieces_layout = QVBoxLayout()
		pieces_layout.setSpacing(8)
		pieces_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
		pieces_layout.addWidget(QLabel("Slice by number of pieces"))
		self.pieces_input = QSpinBox()
		self.pieces_input.setMinimum(1)
		self.pieces_input.setMaximum(1000)
		self.pieces_input.setMinimumWidth(190)
		pieces_layout.addWidget(self.pieces_input)
		pieces_panel.setLayout(pieces_layout)
		pieces_panel.setMaximumWidth(220)
		controls_layout.addWidget(pieces_panel, alignment=Qt.AlignmentFlag.AlignBottom)

		self.slice_mode_switch = QCheckBox("Use time-based slicing")
		controls_layout.addWidget(self.slice_mode_switch, alignment=Qt.AlignmentFlag.AlignBottom)

		time_panel = QWidget()
		time_layout = QVBoxLayout()
		time_layout.setSpacing(8)
		time_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
		time_layout.addWidget(QLabel("Slice by segment duration"))
		self.segment_time_input = QTimeEdit()
		self.segment_time_input.setDisplayFormat("HH:mm:ss")
		self.segment_time_input.setMinimumWidth(190)
		time_layout.addWidget(self.segment_time_input)
		time_panel.setLayout(time_layout)
		time_panel.setMaximumWidth(220)
		controls_layout.addWidget(time_panel, alignment=Qt.AlignmentFlag.AlignBottom)

		controls_layout.addStretch(1)

		layout.addLayout(controls_layout)
		central_widget.setLayout(layout)
		self.setCentralWidget(central_widget)

		self.load_settings()
		self.current_video_url = None
		self.current_video_path = None

		self.setup_connections()
		self.setup_menu()

	def load_settings(self) -> None:
		default_pieces = int(self.settings.value("default_pieces", 4))
		default_time_str = str(self.settings.value("default_time", "00:00:30"))
		self.pieces_input.setValue(default_pieces)
		self.segment_time_input.setTime(QTime.fromString(default_time_str, "HH:mm:ss"))

	def setup_connections(self) -> None:
		self.pieces_input.valueChanged.connect(self.update_timeline)
		self.segment_time_input.timeChanged.connect(self.update_timeline)
		self.slice_mode_switch.toggled.connect(self.update_timeline)

		self.player.durationChanged.connect(self.on_duration_changed)
		self.player.playbackStateChanged.connect(self.on_playback_state_changed)

		self.btn_start_video.clicked.connect(self.go_to_video_start)
		self.btn_start_part.clicked.connect(self.go_to_part_start)
		self.btn_play_pause.clicked.connect(self.toggle_play_pause)
		self.btn_end_part.clicked.connect(self.go_to_part_end)
		self.btn_end_video.clicked.connect(self.go_to_video_end)

		self.player.positionChanged.connect(self.on_position_changed)
		self.timeline.segment_clicked.connect(self.player.setPosition)

		# initial call to sync state
		self.update_timeline()

	def on_position_changed(self, position_ms: int) -> None:
		self.timeline.current_position_seconds = position_ms / 1000.0
		self.timeline.update()

	def on_duration_changed(self, duration_ms: int) -> None:
		if duration_ms > 0:
			self.timeline.video_duration_seconds = duration_ms / 1000.0
			self.update_timeline()

	def on_playback_state_changed(self, state) -> None:
		if state == QMediaPlayer.PlaybackState.PlayingState:
			self.btn_play_pause.setText("Pause")
		else:
			self.btn_play_pause.setText("Play")

	def toggle_play_pause(self) -> None:
		if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
			self.player.pause()
		else:
			self.player.play()

	def get_current_part_bounds(self) -> tuple[int, int]:
		duration_ms = self.player.duration()
		if duration_ms <= 0:
			return 0, 0
			
		duration_s = duration_ms / 1000.0
		# Přidáme malou toleranci (300ms) i sem, aby se kvůli I-FRAMEs neskočilo logicky o kus zpět
		pos_s = (self.player.position() + 300) / 1000.0
		
		is_time_mode = self.slice_mode_switch.isChecked()
		if is_time_mode:
			t = self.segment_time_input.time()
			seg_s = t.hour() * 3600 + t.minute() * 60 + t.second()
			if seg_s <= 0:
				return 0, duration_ms
		else:
			pieces = self.pieces_input.value()
			if pieces <= 0:
				return 0, duration_ms
			seg_s = duration_s / pieces

		part_index = int(pos_s / seg_s) if seg_s > 0 else 0
		start_ms = int((part_index * seg_s) * 1000)
		end_ms = int(((part_index + 1) * seg_s) * 1000)
		
		if end_ms > duration_ms:
			end_ms = duration_ms
			
		return start_ms, end_ms

	def go_to_video_start(self) -> None:
		self.player.setPosition(0)

	def go_to_part_start(self) -> None:
		start_ms, _ = self.get_current_part_bounds()
		self.player.setPosition(start_ms)

	def go_to_part_end(self) -> None:
		start_ms, end_ms = self.get_current_part_bounds()
		# O kousicek pred konec, aby hned neskocil na dalsi segment
		self.player.setPosition(max(start_ms, end_ms - 100))

	def go_to_video_end(self) -> None:
		self.player.setPosition(self.player.duration() - 100)

	def update_timeline(self) -> None:
		if self.slice_mode_switch.isChecked():
			self.timeline.slice_mode = "time"
		else:
			self.timeline.slice_mode = "pieces"

		self.timeline.pieces = self.pieces_input.value()
		
		# convert QTime to seconds
		t = self.segment_time_input.time()
		self.timeline.segment_seconds = t.hour() * 3600 + t.minute() * 60 + t.second()
		
		self.timeline.update()

	def setup_menu(self) -> None:
		menu_bar = self.menuBar()

		file_menu = menu_bar.addMenu("File")
		upload_action = QAction("Upload", self)
		upload_action.triggered.connect(self.upload_file)
		file_menu.addAction(upload_action)

		export_action = QAction("Export", self)
		export_action.triggered.connect(self.export_file)
		file_menu.addAction(export_action)

		settings_menu = menu_bar.addMenu("Settings")
		open_settings_action = QAction("Open Settings", self)
		open_settings_action.triggered.connect(self.open_settings_window)
		settings_menu.addAction(open_settings_action)

	def upload_file(self) -> None:
		file_path, _ = QFileDialog.getOpenFileName(self, "Upload File", "", "Video Files (*.mp4 *.mkv *.avi *.mov);;All Files (*)")
		if file_path:
			url = QUrl.fromLocalFile(file_path)
			self.current_video_path = file_path
			self.player.setSource(url)
			self.player.pause() # Připravíme přehrávač (načte video), ale ihned ho pauzneme
			self.player.setPosition(0)

	def export_file(self) -> None:
		if not self.current_video_path or self.player.duration() <= 0:
			QMessageBox.warning(self, "Chyba", "Nejprve otevřete video pro export.")
			return

		file_path, _ = QFileDialog.getSaveFileName(self, "Uložit jako (Zvolte složku a předponu názvu bez přípony)", "", "All Files (*)")
		if not file_path:
			return

		duration_s = self.player.duration() / 1000.0
		timestamps = []
		
		is_time_mode = self.slice_mode_switch.isChecked()
		if is_time_mode:
			t = self.segment_time_input.time()
			seg_s = t.hour() * 3600 + t.minute() * 60 + t.second()
			if seg_s > 0:
				num_segments = int(duration_s / seg_s)
				if duration_s % seg_s > 0.1:  # malý zbytek na konci
					num_segments += 1
				for i in range(num_segments):
					start_s = i * seg_s
					dur_s = min(seg_s, duration_s - start_s)
					timestamps.append((start_s, dur_s, i + 1))
		else:
			pieces = self.pieces_input.value()
			if pieces > 0:
				seg_s = duration_s / pieces
				for i in range(pieces):
					start_s = i * seg_s
					timestamps.append((start_s, seg_s, i + 1))

		if not timestamps:
			return

		self.progress_dialog = QProgressDialog("Inicializace exportu...", "Zrušit", 0, len(timestamps), self)
		self.progress_dialog.setWindowTitle("Probíhá export")
		self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
		# Rychlý export nedovolíme snadno zrušit, skryjeme tlačítko Zrušit
		self.progress_dialog.setCancelButton(None) 
		self.progress_dialog.show()

		self.export_worker = ExportWorker(self.current_video_path, file_path, timestamps)
		self.export_worker.progress_val.connect(self.progress_dialog.setValue)
		self.export_worker.progress_text.connect(self.progress_dialog.setLabelText)
		self.export_worker.finished_export.connect(self.on_export_finished)
		self.export_worker.start()

	def on_export_finished(self, success: bool, message: str) -> None:
		if hasattr(self, 'progress_dialog') and self.progress_dialog:
			self.progress_dialog.close()
			
		if success:
			QMessageBox.information(self, "Dokončeno", message)
		else:
			QMessageBox.critical(self, "Chyba", message)

	def open_settings_window(self) -> None:
		dialog = SettingsDialog(self)
		if dialog.exec():
			self.load_settings()
			self.update_timeline()


def main() -> None:
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
