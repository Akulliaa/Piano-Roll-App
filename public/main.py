import sys
import os
import time
import shutil
import pygame.midi
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QToolButton, QMenu, QAction, QFileDialog, QColorDialog,
    QPushButton, QSlider, QLabel, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QLinearGradient, QIcon
from midiparser import parse_midi

IMPORTS_DIR = os.path.join(os.getcwd(), 'imports')
os.makedirs(IMPORTS_DIR, exist_ok=True)

# ────────────────────────────────────────────────────────────────────────────────
# DATA MODEL
# ────────────────────────────────────────────────────────────────────────────────
class MidiModel:
    def __init__(self):
        self.notes = []
        self.schedule = []
        self.duration = 0.0

    def load(self, path: str, *, filter_notes=False, min_velocity=20, min_duration=0.02):
        data = parse_midi(path)
        notes = data['notes']
        if filter_notes:
            notes = [n for n in notes if n['velocity'] >= min_velocity and (n['end'] - n['start']) >= min_duration]
        self.notes = notes
        self.schedule = data['playback_schedule']
        self.duration = max((e['time'] for e in self.schedule if e['type'] in ('on', 'off')), default=0.0)

# ────────────────────────────────────────────────────────────────────────────────
# GUI WIDGETS
# ────────────────────────────────────────────────────────────────────────────────


class PianoRollCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes = []
        self.duration = 0.0
        self.current_time = 0.0
        self.time_window = 5.0
        self.left_color = QColor('#0077cc')
        self.right_color = QColor('#00bb44')
        self.pedal_text = "Pedals OFF"  # Default to OFF at startup
        self.pedal_on = False

    def load_notes(self, notes, duration):
        self.notes = notes
        self.duration = duration
        self.current_time = 0.0
        self.update()

    def set_time(self, t):
        self.current_time = t
        self.update()

    def set_pedal_state(self, on):
        self.pedal_on = on
        self.pedal_text = "Pedals ON" if on else "Pedals OFF"
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor('#2e2e2e'))
        WHITE_KEY_WIDTH = w / 52.0
        BLACK_KEY_WIDTH = WHITE_KEY_WIDTH * 0.6
        pps = h / self.time_window if self.time_window > 0 else 0
        black_semitones = {1, 3, 6, 8, 10}
        white_positions = []
        white_count = 0
        for midi in range(21, 109):
            if midi % 12 not in black_semitones:
                x = white_count * WHITE_KEY_WIDTH
                white_positions.append((midi, x))
                white_count += 1
        x_map = {m: x for m, x in white_positions}
        for midi, x in white_positions:
            black_midi = midi + 1
            if black_midi % 12 in black_semitones:
                bx = x + WHITE_KEY_WIDTH - BLACK_KEY_WIDTH / 2
                x_map[black_midi] = bx
        for note in self.notes:
            start, end, num = note['start'], note['end'], note['note']
            length = end - start
            rel = start - self.current_time
            if -length <= rel <= self.time_window and num in x_map:
                x = x_map[num]
                width = BLACK_KEY_WIDTH if num % 12 in black_semitones else WHITE_KEY_WIDTH
                y = (self.time_window - rel) * pps - length * pps
                rect = QRectF(x, y, width, length * pps)
                base = self.left_color if num < 60 else self.right_color
                if num % 12 in black_semitones:
                    base = base.darker(130)
                grad = QLinearGradient(rect.topLeft(), rect.topRight())
                grad.setColorAt(0, base.darker(120))
                grad.setColorAt(1, base.lighter(120))
                painter.setBrush(QBrush(grad))
                painter.setPen(QPen(QColor(0, 0, 0, 150), 1))
                painter.drawRoundedRect(rect, 4, 4)

        # Draw pedal status in top-left
        color = QColor('red') if self.pedal_on else QColor('gray')
        font = painter.font()
        font.setPointSize(20)  
        painter.setFont(font)
        painter.setPen(QPen(color))
        painter.drawText(10, 50, self.pedal_text)

        painter.end()


class PianoKeyboardWidget(QWidget):
    def __init__(self, left_color, right_color, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.notes = list(range(21, 109))
        self.pressed = set()
        self.left_color = QColor(left_color)
        self.right_color = QColor(right_color)

    def setPressed(self, note, on):
        if on:
            self.pressed.add(note)
        else:
            self.pressed.discard(note)
        self.update()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        WHITE = w / 52.0
        BLACK = WHITE * 0.6
        BLACK_H = h * 0.6
        black_set = {1, 3, 6, 8, 10}
        wc = 0
        white_pos = []
        for m in self.notes:
            if m % 12 not in black_set:
                x = wc * WHITE
                rect = QRectF(x, 0, WHITE, h)
                painter.fillRect(rect, QColor('#ffffff'))
                painter.setPen(QPen(QColor('#000')))
                painter.drawRect(rect)
                if m in self.pressed:
                    col = self.left_color if m < 60 else self.right_color
                    painter.fillRect(rect, col.lighter(150))
                white_pos.append((m, x))
                wc += 1
        for m, x in white_pos:
            b = m + 1
            if b % 12 in black_set:
                bx = x + WHITE - BLACK / 2
                rect = QRectF(bx, 0, BLACK, BLACK_H)
                painter.fillRect(rect, QColor('#000'))
                painter.setPen(QPen(QColor('#000')))
                painter.drawRect(rect)
                if b in self.pressed:
                    col = self.left_color if b < 60 else self.right_color
                    painter.fillRect(rect, col.lighter(150))
        painter.end()

# ────────────────────────────────────────────────────────────────────────────────
# MAIN WINDOW
# ────────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Piano Roll')
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            QApplication.instance().setWindowIcon(QIcon(icon_path))
        self.resize(1000, 720)

        # MIDI out
        pygame.midi.init()
        out_id = pygame.midi.get_default_output_id()
        if out_id >= 0:
            self.midi_out = pygame.midi.Output(out_id)
        else:
            self.midi_out = None
            print('⚠️  No MIDI output device – playback silent')

        # Data model
        self.model = MidiModel()
        self.event_idx = 0
        self.elapsed = 0.0
        self.last_time = 0.0
        self.speed = 1.0
        self.loop = False
        self.playing = False

        # Layout
        central = QWidget(self)
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self.canvas = PianoRollCanvas()
        vbox.addWidget(self.canvas, 4)

        self.keyboard = PianoKeyboardWidget(self.canvas.left_color.name(), self.canvas.right_color.name())
        vbox.addWidget(self.keyboard, 1)

        # Control bar
        ctrl = QWidget()
        hl = QHBoxLayout(ctrl)
        hl.setContentsMargins(5, 5, 5, 5)
        hl.setSpacing(10)
        vbox.addWidget(ctrl)

        self.play_btn = QPushButton('▶')
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setEnabled(False)
        hl.addWidget(self.play_btn)

        self.time_label = QLabel('0:00 / 0:00')
        hl.addWidget(self.time_label)
        self.pos_slider = QSlider(Qt.Horizontal)
        self.pos_slider.setRange(0, 1000)
        self.pos_slider.sliderMoved.connect(self.seek)
        hl.addWidget(self.pos_slider)

        hl.addWidget(QLabel('Window'))
        self.win_slider = QSlider(Qt.Horizontal)
        self.win_slider.setRange(1, 20)
        self.win_slider.setValue(5)
        self.win_slider.valueChanged.connect(self.change_window)
        hl.addWidget(self.win_slider)

        hl.addWidget(QLabel('Speed'))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.change_speed)
        hl.addWidget(self.speed_slider)

        self.loop_btn = QPushButton('Loop')
        self.loop_btn.setCheckable(True)
        self.loop_btn.toggled.connect(lambda v: setattr(self, 'loop', v))
        hl.addWidget(self.loop_btn)

        self.color_btn = QPushButton('Colors')
        self.color_btn.clicked.connect(self.choose_colors)
        hl.addWidget(self.color_btn)

        self.filter_checkbox = QCheckBox("Activate filter")
        self.filter_checkbox.setChecked(False)
        self.filter_checkbox.stateChanged.connect(self.toggle_filter_sliders)
        hl.addWidget(self.filter_checkbox)

        self.vel_slider = QSlider(Qt.Horizontal)
        self.vel_slider.setRange(0, 127)
        self.vel_slider.setValue(20)
        self.vel_slider.setVisible(False)
        hl.addWidget(QLabel('Min. Velocity'))
        hl.addWidget(self.vel_slider)

        self.dur_slider = QSlider(Qt.Horizontal)
        self.dur_slider.setRange(1, 100)
        self.dur_slider.setValue(2)
        self.dur_slider.setVisible(False)
        hl.addWidget(QLabel('Min. duration (cs)'))
        hl.addWidget(self.dur_slider)

        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.clicked.connect(self.refresh_filter)
        hl.addWidget(self.refresh_btn)

        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.update_playback)

        self._init_menu()
        self.load_files()
        self.update_menu()

    def _init_menu(self):
        self.gear_btn = QToolButton(self)
        self.gear_btn.setText('⚙️')
        self.gear_btn.setPopupMode(QToolButton.InstantPopup)
        self.gear_btn.setStyleSheet('border:none;color:#fff')
        self.gear_btn.setParent(self)
        menu = QMenu()
        imp = QAction('Import MIDI file...', self)
        imp.triggered.connect(self.import_file)
        menu.addAction(imp)
        self.music_menu = QMenu('Piano music', self)
        menu.addMenu(self.music_menu)
        self.gear_btn.setMenu(menu)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x = self.width() - self.gear_btn.width() - 10
        self.gear_btn.move(x, 10)

    def toggle_filter_sliders(self):
        show = self.filter_checkbox.isChecked()
        self.vel_slider.setVisible(show)
        self.dur_slider.setVisible(show)

    def refresh_filter(self):
        if hasattr(self, 'current_midi_path'):
            self.load_midi(self.current_midi_path)
        else:
            QMessageBox.warning(self, 'No file', 'No MIDI file loaded.')

    def import_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Import MIDI', '', 'MIDI (*.mid)')
        if path:
            dst = os.path.join(IMPORTS_DIR, os.path.basename(path))
            try:
                shutil.copy2(path, dst)
            except Exception as ex:
                QMessageBox.critical(self, 'Copy failed', str(ex))
            self.update_menu()

    def load_files(self):
        self.files = [os.path.join(IMPORTS_DIR, f) for f in os.listdir(IMPORTS_DIR) if f.lower().endswith('.mid')]

    def update_menu(self):
        self.load_files()
        self.music_menu.clear()
        if not self.files:
            a = QAction('(empty)', self)
            a.setEnabled(False)
            self.music_menu.addAction(a)
        for p in self.files:
            a = QAction(os.path.basename(p), self)
            a.triggered.connect(lambda _, x=p: self.load_midi(x))
            self.music_menu.addAction(a)

    def load_midi(self, path):
        try:
            filter_enabled = self.filter_checkbox.isChecked()
            min_vel = self.vel_slider.value()
            min_dur = self.dur_slider.value() / 100.0
            self.model.load(path, filter_notes=filter_enabled, min_velocity=min_vel, min_duration=min_dur)
        except Exception as ex:
            return QMessageBox.critical(self, 'Parsing error', str(ex))

        self.current_midi_path = path
        self.event_idx = 0
        self.elapsed = 0.0
        self.play_btn.setEnabled(True)
        self.canvas.load_notes(self.model.notes, self.model.duration)
        self.time_label.setText(f"0:00 / {int(self.model.duration // 60)}:{int(self.model.duration % 60):02d}")

    def toggle_play(self):
        if self.playing:
            self.elapsed += (time.time() - self.last_time) * self.speed
            self.timer.stop()
            self.play_btn.setText('▶')
        else:
            self.last_time = time.time()
            self.timer.start()
            self.play_btn.setText('⏸')
        self.playing = not self.playing

    def update_playback(self):
        now = time.time()
        dt = (now - self.last_time) * self.speed
        self.elapsed += dt
        self.last_time = now

        if self.elapsed >= self.model.duration:
            if self.loop:
                self.elapsed = 0.0
                self.event_idx = 0
            else:
                return self.toggle_play()

        t = self.elapsed
        while self.event_idx < len(self.model.schedule) and self.model.schedule[self.event_idx]['time'] <= t:
            ev = self.model.schedule[self.event_idx]
            typ = ev['type']
            if typ in ('on', 'off'):
                note = ev['note']
                vel = ev['velocity'] if typ == 'on' else 0
                if self.midi_out:
                    if typ == 'on': self.midi_out.note_on(note, vel)
                    else: self.midi_out.note_off(note, vel)
                self.keyboard.setPressed(note, typ == 'on')
            elif typ == 'pedal':
                self.canvas.set_pedal_state(ev['value'] >= 64)
            self.event_idx += 1

        self.canvas.set_time(t)
        self.pos_slider.setValue(int(t / self.model.duration * 1000))
        self.time_label.setText(f"{int(t//60)}:{int(t%60):02d} / {int(self.model.duration//60)}:{int(self.model.duration%60):02d}")

    def seek(self, val):
        self.elapsed = (val / 1000.0) * self.model.duration
        self.last_time = time.time()
        self.event_idx = 0
        self.keyboard.pressed.clear()
        for e in self.model.schedule:
            if e['time'] <= self.elapsed:
                if e['type'] == 'on':
                    self.keyboard.pressed.add(e['note'])
                elif e['type'] == 'off':
                    self.keyboard.pressed.discard(e['note'])
                self.event_idx += 1
            else:
                break
        self.keyboard.update()
        self.canvas.set_time(self.elapsed)

    def change_window(self, val):
        self.canvas.time_window = float(val)
        self.canvas.update()

    def change_speed(self, val):
        self.speed = val / 100.0
        self.time_label.setText(f"{self.speed:.2f}x")

    def choose_colors(self):
        left = QColorDialog.getColor(self.keyboard.left_color, self, 'Choose color for bass notes')
        if left.isValid():
            self.keyboard.left_color = left
            self.canvas.left_color = left
        right = QColorDialog.getColor(self.keyboard.right_color, self, 'Choose color for high notes')
        if right.isValid():
            self.keyboard.right_color = right
            self.canvas.right_color = right
        self.keyboard.update()
        self.canvas.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
             