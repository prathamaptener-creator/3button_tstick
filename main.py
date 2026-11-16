import sys
import math
import serial

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QLineEdit, QMessageBox, QFrame, QComboBox,
    QCompleter, QHBoxLayout
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# IMPORTANT: PyQt5 application -> use Qt Matplotlib backend
import matplotlib
matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt

import time
import base64
import gzip
import sqlite3

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from datetime import datetime
import threading
import time
import websocket
from erp import *
from config import *
# import schedule
# import requests
import json
# import ui_sql
# import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def get_mysql_conn():
    import pymysql
    return pymysql.connect(**MYSQL_CONFIG)










# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM STYLE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
PREMIUM_BG = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0a1a, stop:0.4 #0d1b3e, stop:0.7 #1a0a2e, stop:1 #0a0a1a)"
GLASS_CARD = """
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.13), stop:1 rgba(255,255,255,0.05));
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
"""
ACCENT_BLUE  = "#4fc3f7"
ACCENT_CYAN  = "#00e5ff"
ACCENT_GREEN = "#00e676"
ACCENT_RED   = "#ff1744"


class PremiumMessageBox(QtWidgets.QDialog):
    """Auto-dismissing result overlay — no OK button needed.
    Shows for `duration_ms` milliseconds then closes itself.
    Still supports exec_() for non-result dialogs (info/go-back).
    """

    def __init__(self, parent, kind, title, message, duration_ms=2800, auto_close=True):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(480)

        if kind == "pass":
            accent    = "#00e676"
            icon_text = "✓"
            icon_bg   = "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #00875a,stop:1 #00e676)"
        elif kind == "fail":
            accent    = "#ff4444"
            icon_text = "✕"
            icon_bg   = "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #9b0000,stop:1 #ff4444)"
        else:
            accent    = "#00dcff"
            icon_text = "i"
            icon_bg   = "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #006080,stop:1 #00dcff)"

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Outer border glow
        outer = QFrame()
        outer.setStyleSheet(f"""
            QFrame {{
                background: rgba(6,10,24,0.97);
                border: 1.5px solid {accent};
                border-radius: 28px;
            }}
        """)
        root.addWidget(outer)

        inner = QVBoxLayout(outer)
        inner.setContentsMargins(40, 36, 40, 36)
        inner.setSpacing(14)

        # Top accent bar
        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.2 {accent}, stop:0.8 {accent}, stop:1 transparent);
            border:none; border-radius:2px;
        """)
        inner.addWidget(bar)
        inner.addSpacing(6)

        # Icon
        icon_frame = QFrame()
        icon_frame.setFixedSize(88, 88)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background: {icon_bg};
                border-radius: 44px;
                border: none;
            }}
        """)
        il = QVBoxLayout(icon_frame)
        il.setContentsMargins(0,0,0,0)
        icon_lbl = QtWidgets.QLabel(icon_text)
        icon_lbl.setAlignment(QtCore.Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size:40px; font-weight:900; color:#fff; background:transparent; border:none;")
        il.addWidget(icon_lbl)
        inner.addWidget(icon_frame, alignment=QtCore.Qt.AlignHCenter)

        # Title
        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        title_lbl.setStyleSheet(f"""
            font-size:26px; font-weight:900; color:{accent};
            background:transparent; border:none; letter-spacing:3px;
        """)
        inner.addWidget(title_lbl)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:rgba(255,255,255,0.08); border:none;")
        inner.addWidget(sep)

        # Message
        msg_lbl = QtWidgets.QLabel(message)
        msg_lbl.setAlignment(QtCore.Qt.AlignCenter)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("""
            font-size:14px; color:rgba(220,240,250,0.85);
            background:transparent; border:none;
        """)
        inner.addWidget(msg_lbl)

        # Auto-progress bar (shows time remaining)
        if auto_close:
            inner.addSpacing(8)
            self._progress_bar = QFrame()
            self._progress_bar.setFixedHeight(3)
            self._progress_bar.setStyleSheet(f"""
                background: {accent}; border:none; border-radius:2px;
            """)
            inner.addWidget(self._progress_bar)

            # Animate progress bar shrinking
            self._anim = QtCore.QPropertyAnimation(self._progress_bar, b"maximumWidth")
            self._anim.setDuration(duration_ms)
            self._anim.setStartValue(400)
            self._anim.setEndValue(0)
            self._anim.setEasingCurve(QtCore.QEasingCurve.Linear)
            self._anim.start()

            # Auto close
            QtCore.QTimer.singleShot(duration_ms, self.accept)

        else:
            # For info dialogs (go-back etc) — add a manual close button
            ok_btn = QtWidgets.QPushButton("OK")
            ok_btn.setFixedHeight(46)
            ok_btn.setMinimumWidth(120)
            ok_btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(0,220,255,0.15);
                    color: #00dcff;
                    font-weight: 800; font-size: 14px;
                    border: 1px solid rgba(0,220,255,0.40);
                    border-radius: 12px; letter-spacing: 2px;
                }}
                QPushButton:hover {{
                    background: rgba(0,220,255,0.28);
                    border-color: #00dcff; color: #fff;
                }}
            """)
            ok_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            ok_btn.clicked.connect(self.accept)
            inner.addSpacing(4)
            inner.addWidget(ok_btn, alignment=QtCore.Qt.AlignHCenter)


class EmployeeEntry(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Employee ID")
        
        # ~ self.vbox=QtWidgets.QVBoxLayout()
        # ~ self.setLayout(self.vbox)
        
        # ~ self.frame=QtWidgets.QFrame()
        # ~ self.vbox.addWidget(self.frame)
        

        # Style — ultra premium dark
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #050510, stop:0.3 #08122a, stop:0.6 #0e0620, stop:1 #050510);
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            }
        """)

        # Set fullscreen properly
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.raise_()
        self.activateWindow()
        self.show()

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Outer stylish container — premium frosted card
        self.container = QFrame()
        self.container.setFixedSize(780, 560)
        self.container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(10,22,65,0.98),
                    stop:0.45 rgba(8,6,28,0.98),
                    stop:1 rgba(6,18,55,0.98));
                border-radius: 36px;
                border: 1px solid rgba(0,229,255,0.28);
            }
        """)

        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignTop)
        self.vbox.setContentsMargins(48, 36, 48, 36)
        self.vbox.setSpacing(0)

        # Top accent line — electric teal glow bar
        accent_line = QFrame()
        accent_line.setFixedHeight(3)
        accent_line.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 transparent, stop:0.15 #00e5ff,
                    stop:0.85 #7b61ff, stop:1 transparent);
                border: none; border-radius: 2px;
            }
        """)
        self.vbox.addWidget(accent_line)
        self.vbox.addSpacing(28)

        # Brand pill / logo area
        brand_row = QHBoxLayout()
        brand_pill = QFrame()
        brand_pill.setFixedSize(42, 42)
        brand_pill.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #0091ea, stop:1 #00e5ff);
                border-radius: 13px; border: none;
            }
        """)
        bl = QVBoxLayout(brand_pill)
        bl.setContentsMargins(0,0,0,0)
        bicon = QLabel("B")
        bicon.setAlignment(Qt.AlignCenter)
        bicon.setStyleSheet("font-size:22px; font-weight:900; color:#fff; background:transparent; border:none;")
        bl.addWidget(bicon)

        brand_text_v = QVBoxLayout()
        brand_text_v.setSpacing(1)
        brand_name = QLabel("bluArmor")
        brand_name.setStyleSheet("""
            font-size:14px; font-weight:800; color:#00e5ff;
            letter-spacing:4px; background:transparent; border:none;
        """)
        brand_sub = QLabel("Button Displacement Jig")
        brand_sub.setStyleSheet("""
            font-size:10px; color:rgba(79,195,247,0.55);
            letter-spacing:2px; background:transparent; border:none;
        """)
        brand_text_v.addWidget(brand_name)
        brand_text_v.addWidget(brand_sub)

        brand_row.addWidget(brand_pill)
        brand_row.addSpacing(10)
        brand_row.addLayout(brand_text_v)
        brand_row.addStretch()
        self.vbox.addLayout(brand_row)
        self.vbox.addSpacing(32)

        title = QLabel("SELECT OPERATOR")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 30px;
                font-weight: 900;
                color: #ffffff;
                letter-spacing: 6px;
                background: transparent;
                border: none;
            }
        """)
        self.vbox.addWidget(title)
        self.vbox.addSpacing(6)

        subtitle = QLabel("Choose your employee profile to begin a test session")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: rgba(79,195,247,0.60);
                letter-spacing: 1px;
                background: transparent;
                border: none;
            }
        """)
        self.vbox.addWidget(subtitle)
        self.vbox.addSpacing(28)

        # Employee Dropdown — premium frosted style
        dropdown_label = QLabel("OPERATOR")
        dropdown_label.setStyleSheet("""
            font-size:10px; font-weight:800; color:rgba(0,229,255,0.65);
            letter-spacing:3px; background:transparent; border:none;
        """)
        self.vbox.addWidget(dropdown_label)
        self.vbox.addSpacing(6)

        self.emp_dropdown = QComboBox()
        self.emp_dropdown.setEditable(True)
        self.emp_dropdown.setFixedHeight(58)
        self.emp_dropdown.setStyleSheet("""
            QComboBox {
                background: rgba(0,229,255,0.06);
                padding: 0px 20px;
                font-size: 20px;
                font-weight: 600;
                border-radius: 16px;
                border: 1px solid rgba(0,229,255,0.35);
                color: #e0f7fa;
                selection-background-color: transparent;
            }
            QComboBox:hover {
                border: 1px solid rgba(0,229,255,0.70);
                background: rgba(0,229,255,0.10);
            }
            QComboBox:focus {
                border: 1px solid #00e5ff;
                background: rgba(0,229,255,0.12);
            }
            QComboBox QAbstractItemView {
                background: #080e26;
                color: #e0f7fa;
                selection-background-color: rgba(0,229,255,0.20);
                font-size: 16px;
                border: 1px solid rgba(0,229,255,0.30);
                border-radius: 10px;
                padding: 6px;
                outline: none;
            }
            QComboBox::drop-down { border: none; width: 36px; }
            QComboBox::down-arrow { image: none; }
        """)

        # Load employee list
        employee_list = fetch_employees()
        if employee_list:
            self.emp_dropdown.addItems(employee_list)
            completer = QCompleter(employee_list)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.emp_dropdown.setCompleter(completer)
        else:
            self.emp_dropdown.addItem("No employees available")

        # Prevent first item from being selected initially
        self.emp_dropdown.setCurrentIndex(-1)  # This ensures no item is selected initially

        self.vbox.addWidget(self.emp_dropdown)

        # Spacer to balance layout
        self.vbox.addSpacing(24)

        # PROCEED Button — primary CTA
        fetch_btn = QPushButton("PROCEED  →")
        fetch_btn.setFixedHeight(62)
        fetch_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #005fa3, stop:1 #00b4d8);
                color: #ffffff;
                font-size: 15px;
                font-weight: 900;
                border-radius: 18px;
                padding: 0 28px;
                letter-spacing: 4px;
                border: 1px solid rgba(0,180,216,0.45);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00b4d8, stop:1 #48cae4);
                border: 1px solid rgba(72,202,228,0.65);
            }
            QPushButton:pressed {
                background: #023e58;
                color: #90e0ef;
            }
        """)
        fetch_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        fetch_btn.clicked.connect(self.show_model_buttons)
        self.vbox.addWidget(fetch_btn)
        self.model_button_layout = QHBoxLayout()
        self.model_button_layout.setAlignment(Qt.AlignCenter)
        self.model_button_layout.setSpacing(16)

        self.BUTTON = QPushButton("⬡  BUTTON")
        self.TSTICK = QPushButton("⟳  TSTICK")

        for btn in [self.BUTTON, self.TSTICK]:
            btn.setFixedSize(168, 60)
            btn.setVisible(False)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(123,97,255,0.14);
                    color: #c3b1ff;
                    font-size: 13px;
                    font-weight: 800;
                    border-radius: 18px;
                    border: 1px solid rgba(123,97,255,0.45);
                    letter-spacing: 2px;
                }
                QPushButton:hover {
                    background: rgba(123,97,255,0.30);
                    border: 1px solid #9c7cff;
                    color: #ffffff;
                }
                QPushButton:pressed {
                    background: #1a0060;
                    color: #c3b1ff;
                }
            """)
            btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.model_button_layout.addWidget(btn)

        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.model_button_layout)

        # Connect model buttons
        self.BUTTON.clicked.connect(lambda: self.start_test("BUTTON"))
        self.TSTICK.clicked.connect(lambda: self.start_test("TSTICK"))

        self.container.setLayout(self.vbox)
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)



    def show_model_buttons(self):
        employee_id = self.emp_dropdown.currentText().strip()
        if not employee_id:
            QMessageBox.warning(self, "Error", "Please select an Employee ID")
            return

        self.employee_id = employee_id
       
            
        # Show buttons
        for btn in [self.BUTTON,self.TSTICK]:
            btn.setVisible(True)
            print(btn)

    def start_test(self, model_name):
        # employee_id=self.employee_id
        # job_card_id=self.job_card_id
        if not hasattr(self, "employee_id"):
            QMessageBox.warning(self, "Error", "Please select employee and click PROCEED first.")
            return

        model_to_test_type = {
            "BUTTON": "SF-3Buttons Test (Cassini)",
            "TSTICK": "SF-T-Stick Button Test(Cassini)",
        }

        test_type = model_to_test_type.get(model_name)
        print("📦 Test Type being searched:", test_type)
        print(self.employee_id)
        self.job_card_id = fetch_job_card_for_employee(self.employee_id, test_type)
        # self.job_card_id="Testing"
    

        if not self.job_card_id:
            QMessageBox.warning(self, "Error", f"No Job Card found for {model_name}")
            return
        
        
        print(f"✅ Model Selected: {model_name}")
        print(f"👤 Employee: {self.employee_id}, 🧾 Job Card: {self.job_card_id}")

        self.test_window = Ui_MainWindow(self.employee_id, self.job_card_id,model_name)
        self.test_window.selected_model = model_name
        self.test_window.comboBox.setCurrentText(model_name)
        self.test_window.comboBox.setEnabled(False)  # lock the model selection
        self.test_window.show()
        # Home once when the selected model window opens.
        self.test_window.home_gcode()
        self.close()



class PressDipDetector:
    """Detect a dip and return the force at its onset."""
    def __init__(self, threshold=DIP_THRESHOLD):
        self.threshold = threshold
        self.peak = None
        self.valley = None
        self.onset_force = None

    def update(self, force):
        if not math.isfinite(force):
            return None

        if self.peak is None:
            self.peak = force
            return None

        if self.valley is None:
            if self.peak - force > self.threshold + 1e-9:
                # Save the force BEFORE the drop (blue-circle point)
                self.onset_force = self.peak
                self.valley = force
            else:
                self.peak = max(self.peak, force)

        else:
            # Continue tracking the bottom of the dip
            self.valley = min(self.valley, force)

            # Confirm the dip after force recovers
            if force - self.valley > self.threshold + 1e-9:
                value = self.onset_force

                self.peak = force
                self.valley = None
                self.onset_force = None

                if value is not None and 3 <= value < 15:
                    return value

        return None

class SerialThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port, poort, baudrate):
        super().__init__()
        self.port = port
        self.poort = poort
        self.baudrate = baudrate
        self.serial_port = None
        self.running = False
        self.ser = serial.Serial(self.poort, self.baudrate, timeout=0.1)
        self._grbl_opened_at = time.monotonic()
        self._motion_lock = threading.RLock()
        self._grbl_condition = threading.Condition()
        self._startup_count = 0
        self._ack_count = 0
        self._status_count = 0
        self._last_motion_status_count = 0
        self._idle_streak = 0
        self._grbl_status = None
        self._grbl_error = None
        self.callback = None

    def run(self):
        self.serial_port = serial.Serial(self.port, self.baudrate, timeout=0.1)   # Arduino
        self.running = True

        while self.running:

            # 🔹 Arduino data (force readings)
            if self.serial_port.in_waiting:
                data = self.serial_port.readline().decode(errors='ignore').strip()
                self.data_received.emit(data)
                if self.callback:
                    self.callback(data)

            # 🔹 GRBL response (HOME / ok)
            if self.ser.in_waiting:
                grbl_data = self.ser.readline().decode(errors='ignore').strip()
                print("GRBL:", grbl_data)   # DEBUG
                with self._grbl_condition:
                    if grbl_data.startswith("Grbl "):
                        self._startup_count += 1
                    elif grbl_data == "ok":
                        self._ack_count += 1
                    elif grbl_data.startswith(("error:", "ALARM:")):
                        self._grbl_error = grbl_data
                    elif grbl_data.startswith("<"):
                        self._grbl_status = grbl_data[1:].split("|")[0].rstrip(">")
                        self._status_count += 1
                        if self._grbl_status in ("Jog", "Run"):
                            self._last_motion_status_count = self._status_count
                        self._idle_streak = self._idle_streak + 1 if self._grbl_status == "Idle" else 0
                    self._grbl_condition.notify_all()
                if self.callback:
                    self.callback(grbl_data)

        self.serial_port.close()
    def stop(self):
        self.running = False
        self.wait()

    def send_gcode(self, gcode, callback=None):
        with self._motion_lock:
            self.callback = callback
            if self.ser and self.ser.is_open:
                self.ser.write(gcode.encode('utf-8') + b'\n')

    def move_and_wait(self, gcode, callback, timeout=60):
        """Worker-thread only: wait for command acknowledgement AND fresh Idle.

        GRBL 'ok' means accepted, not physically completed. Keep collecting
        the same button until a status report confirms the movement is done.
        """
        with self._motion_lock:
            if not self.ser or not self.ser.is_open:
                raise RuntimeError("GRBL port is not open")
            deadline = time.monotonic() + timeout
            with self._grbl_condition:
                ack_before = self._ack_count
                self._grbl_error = None
                self.callback = callback
                self.ser.write(gcode.encode('ascii') + b'\n')
                self.ser.flush()
                while self._ack_count == ack_before:
                    self._check_motion_wait(deadline, gcode)
                    self._grbl_condition.wait(0.1)
                while True:
                    self._check_motion_wait(deadline, gcode)
                    status_before = self._status_count
                    self.ser.write(b'?')
                    while self._status_count == status_before:
                        self._check_motion_wait(deadline, gcode)
                        self._grbl_condition.wait(0.1)
                    if self._grbl_status == "Idle":
                        return
                    self._grbl_condition.wait(0.1)

    def wait_grbl_ready(self, timeout=8.0):
        """Wait out USB auto-reset and require a fresh GRBL status response.

        The force-reader running flag does not mean GRBL has booted.
        Alarm is a valid ready state here: $H is how it is cleared.
        """
        deadline = time.monotonic() + timeout
        with self._grbl_condition:
            while time.monotonic() - self._grbl_opened_at < 2.0:
                if not self.isRunning() or time.monotonic() >= deadline:
                    raise TimeoutError("GRBL reader unavailable during startup")
                self._grbl_condition.wait(0.05)
            before = self._status_count
            next_query = 0.0
            while self._status_count == before:
                if not self.isRunning() or time.monotonic() >= deadline:
                    raise TimeoutError("GRBL did not answer startup status queries; homing was not sent")
                if time.monotonic() >= next_query:
                    self.ser.write(b"?")
                    self.ser.flush()
                    next_query = time.monotonic() + 0.2
                self._grbl_condition.wait(0.05)
            if self._grbl_status not in ("Idle", "Alarm"):
                raise RuntimeError(f"GRBL is {self._grbl_status}; cannot begin automatic homing")
            print(f"GRBL ready ({self._grbl_status}); sending $H")

    def home_and_wait(self, recover=False):
        """Worker only. Clear feed hold on recovery, then confirm homing."""
        with self._motion_lock:
            self.callback = None
            if recover:
                with self._grbl_condition:
                    before = self._startup_count
                    self.ser.write(b"\x85\x18")
                    deadline = time.monotonic() + 5.0
                    while self._startup_count == before:
                        if time.monotonic() >= deadline:
                            raise TimeoutError("GRBL did not restart for recovery homing")
                        self._grbl_condition.wait(0.05)
            self.wait_grbl_ready()
            self.move_and_wait("$H", None, timeout=90)
            self.move_and_wait("G90 G21", None)

    def press_until_force(self, callback, max_travel_mm=8.0):
        """Continuous F50 jog; stop at 15 N without a dip, or dip + 2 N.

        GRBL 1.1 jogging is required. max_travel_mm is a fault-travel budget,
        not the normal pressing depth. The sensor decides when to cancel.
        """
        if not math.isfinite(max_travel_mm) or not 0 < max_travel_mm <= 12.0:
            raise ValueError("Press travel allowance must be greater than 0 and at most 12 mm")
        state = {"force": None, "last": None, "dip": None,
                 "cancelled": False, "active": False, "peak": 0.0}
        detector = PressDipDetector()

        def collect(data):
            callback(data)
            try:
                parts = data.strip().strip("()").split(",")
                if len(parts) != 2:
                    return
                force, displacement = map(float, parts)
                if not math.isfinite(force) or not math.isfinite(displacement):
                    return
            except (ValueError, TypeError):
                return
            with self._grbl_condition:
                state["force"] = force
                state["last"] = time.monotonic()
                if state["active"]:
                    state["peak"] = max(state["peak"], force)
                    if not state["cancelled"]:
                        if state["dip"] is None:
                            state["dip"] = detector.update(force)
                        target = PRESS_TARGET_FORCE if state["dip"] is None else state["dip"] + POST_DIP_EXTRA_FORCE
                        if force >= target or force >= PRESS_MAX_FORCE:
                            state["cancelled"] = True
                            self.ser.write(b"\x85")  # cancel jog immediately
                self._grbl_condition.notify_all()

        with self._motion_lock:
            try:
                with self._grbl_condition:
                    self._grbl_error = None
                    self.callback = collect
                    deadline = time.monotonic() + 2.0
                    while state["last"] is None:
                        self._check_motion_wait(deadline, "waiting for fresh force data")
                        self._grbl_condition.wait(0.01)
                    if state["force"] >= PRESS_TARGET_FORCE:
                        raise RuntimeError("Force is already at/above 15 N before pressing")
                    ack_before = self._ack_count
                    status_before = self._status_count
                    press_started = time.monotonic()
                    # Command submission and arming are atomic with sensor decisions.
                    self.ser.write(f"$J=G91 G21 Z{max_travel_mm:g} F50\n".encode("ascii"))
                    state["active"] = True
                    deadline = time.monotonic() + PRESS_TIMEOUT
                    next_query = 0.0
                    stop_status_before = None
                    while True:
                        self._check_motion_wait(deadline, "force-controlled F50 press")
                        if time.monotonic() - state["last"] > 0.5:
                            raise RuntimeError("Force data stopped during pressing")
                        if state["cancelled"] and self._ack_count > ack_before:
                            if stop_status_before is None:
                                stop_status_before = self._status_count
                                self.ser.write(b"?")
                                next_query = time.monotonic() + 0.03
                            elif (self._status_count >= stop_status_before + 2
                                  and self._idle_streak >= 2 and self._grbl_status == "Idle"):
                                break
                        elif self._ack_count > ack_before:
                            # A status requested during positioning can arrive after
                            # the jog's 'ok'. One Idle does NOT prove the jog ended.
                            motion_seen = self._last_motion_status_count > status_before
                            if (motion_seen and self._idle_streak >= 2
                                    and self._grbl_status == "Idle"):
                                elapsed = time.monotonic() - press_started
                                if elapsed >= max_travel_mm * 60.0 / 50.0 - 0.1:
                                    raise RuntimeError(f"{max_travel_mm:g} mm travel guard reached; target force not reached (last {state['force']:.2f} N)")
                                raise RuntimeError(f"GRBL stopped before target force (last {state['force']:.2f} N)")
                            if not motion_seen and time.monotonic() - press_started > 2.0:
                                raise RuntimeError("GRBL did not confirm press motion; check Jog support and controller state")
                        if time.monotonic() >= next_query:
                            self.ser.write(b"?")
                            next_query = time.monotonic() + 0.05
                        self._grbl_condition.wait(0.01)
                    state["active"] = False
                    print(f"Force press: dip={state['dip']} N, peak={state['peak']:.2f} N")
                    return state["dip"]
            except Exception:
                self.ser.write(b"\x85!")
                raise
            finally:
                state["active"] = False
                self.callback = callback

    def _check_motion_wait(self, deadline, gcode):
        if self._grbl_error:
            raise RuntimeError(self._grbl_error)
        if not self.isRunning() or time.monotonic() >= deadline:
            # GRBL realtime feed hold; never continue into another button.
            self.ser.write(b'!')
            raise TimeoutError("Movement did not complete: " + gcode)


# Daily golden-device calibration settings (24-hour IST).
# Keep independent golden devices and limits for each selected model.
import datetime as calibration_datetime
import os as calibration_os

CALIBRATION_IST = calibration_datetime.timezone(calibration_datetime.timedelta(hours=5, minutes=30))

def daily_calibration_now():
    return calibration_datetime.datetime.now(CALIBRATION_IST)

# BCM numbering: GPIO8=physical24, GPIO10=physical19, GPIO17=physical11.
# Dry contacts to GND only; internal pull-ups make a press active LOW.



class HarnessGPIOCheck:
    def __init__(self):
        self.buttons = {}
        self.lock = threading.Lock()
        self.expected = None
        self.seen = threading.Event()
        self.errors = {}
        try:
            from gpiozero import Button
            from gpiozero.pins.lgpio import LGPIOFactory
            self.factory = LGPIOFactory()
            for key, pin in GPIO_BUTTON_PINS.items():
                button = Button(pin, pull_up=True, bounce_time=0.02, pin_factory=self.factory)
                button.when_pressed = lambda key=key: self._pressed(key)
                self.buttons[key] = button
        except Exception:
            self.close()
            raise

    def reset(self):
        """Start another run without recreating GPIO pins or callbacks."""
        with self.lock:
            self.expected = None
            self.seen.clear()
            self.errors.clear()

    def disarm(self):
        with self.lock:
            self.expected = None
            self.seen.clear()

    def _pressed(self, key):
        with self.lock:
            if self.expected == key and key not in self.errors:
                self.seen.set()
                print(f"GPIO PASS: {key} -> BCM{GPIO_BUTTON_PINS[key]}", flush=True)

    def arm(self, key):
        with self.lock:
            self.expected = key
            self.seen.clear()
            if self.buttons[key].is_pressed:
                self.errors[key] = f"{key} GPIO{GPIO_BUTTON_PINS[key]} already LOW before press (held/shorted)"

    def finish(self, key):
        received = self.seen.wait(GPIO_RESPONSE_TIMEOUT)
        with self.lock:
            self.expected = None
            if not received and key not in self.errors:
                self.errors[key] = f"{key} GPIO{GPIO_BUTTON_PINS[key]} response missing"
            return received and key not in self.errors

    def close(self):
        for button in self.buttons.values():
            button.close()
        self.buttons.clear()
        factory = getattr(self, "factory", None)
        if factory is not None:
            factory.close()


def button_failure_issue(dips, responses):
    """Describe only failed button checks for ERP's issue field."""
    failures = []
    for key, label, low, high in (("right", "Right", 5, 13),
                                  ("centre", "Centre", 4, 13),
                                  ("left", "Left", 5, 13)):
        value = dips.get(key)
        if value is None:
            failures.append(f"{label} DIP missing")
        elif not low <= float(value) <= high:
            failures.append(f"{label} DIP failed: {float(value):g} N")
        if not responses.get(key, False):
            failures.append(f"{label} button not functioning")
    return "; ".join(failures)


def short_gpio_status(dips, responses):
    """Only failed checks; full explanation is stored in issue."""
    parts = []
    for key, label, low, high in (("right", "R", 5, 13),
                                  ("centre", "C", 4, 13),
                                  ("left", "L", 5, 13)):
        value = dips.get(key)
        if value is None:
            parts.append(f"{label} DIP missing")
        elif not low <= float(value) <= high:
            parts.append(f"{label} DIP={float(value):.2f}N")
        if not responses.get(key, False):
            parts.append(f"{label} GPIO fail")
    return "; ".join(parts)[:140]


def shorten_pending_gpio_records():
    """Repair old oversized GPIO payloads in the local retry queue."""
    try:
        with sqlite3.connect(DB_FILE) as db:
            rows = db.execute("SELECT rowid, dips FROM job_card_fail WHERE system=?",
                              ("3BUTTONButtonDisplacement",)).fetchall()
            for row_id, payload in rows:
                try:
                    data = json.loads(payload)
                    if not isinstance(data, dict) or not isinstance(data.get("dips"), dict) or not isinstance(data.get("gpio"), dict):
                        continue
                    text = short_gpio_status(data["dips"], data["gpio"])
                except (TypeError, ValueError):
                    continue
                db.execute("UPDATE job_card_fail SET dips=?, issue=? WHERE rowid=?",
                           (text, button_failure_issue(data["dips"], data["gpio"]), row_id))
    except Exception as exc:
        print(f"Could not shorten pending GPIO records: {exc}", flush=True)


def insert_gpio_fail_record(serial, model, batch, employee, job_card, dips, reason, responses):
    """Queue a short force/GPIO summary for the ERP button_status field."""
    if not employee or not job_card:
        return False
    try:
        with sqlite3.connect(DB_FILE) as db:
            db.execute("""INSERT INTO job_card_fail
                (device_serial_number,model,batch,employee_id,job_card_id,qc_system,system,issue,status,dips,timestamp)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (serial,model,batch,employee,job_card,"CASSINI-02","3BUTTONButtonDisplacement",button_failure_issue(dips, responses),"fail",
                 short_gpio_status(dips, responses), daily_calibration_now().strftime("%Y-%m-%d %H:%M:%S")))
        retry_records()
        return True
    except Exception as exc:
        print(f"GPIO failure could not be queued: {exc}", flush=True)
        return False

class Ui_MainWindow(QMainWindow):



    def _init_daily_calibration(self):
        self._daily_mode = "production"
        self._daily_attempt = None
        self._daily_reminder = None
        self._daily_input_mode = None
        with sqlite3.connect(DAILY_CALIBRATION_DB) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS jig_calibration (
                id INTEGER PRIMARY KEY, day TEXT, model TEXT, serialnumber TEXT,
                employee TEXT, started_at TEXT, finished_at TEXT, status TEXT,
                limits_json TEXT, dips_json TEXT, reason TEXT, erp_sent INTEGER DEFAULT 0)""")
        row = QHBoxLayout()
        self.production_mode_button = QPushButton("PRODUCTION")
        self.calibration_mode_button = QPushButton("CALIBRATION")
        for button in (self.production_mode_button, self.calibration_mode_button):
            button.setCheckable(True)
            button.setMinimumHeight(34)
            button.setStyleSheet("QPushButton {color:#cddded;background:#162030;border:1px solid #3A5070;border-radius:6px;padding:6px;} QPushButton:checked {color:white;background:#205c99;border:2px solid #4A9EFF;}")
            row.addWidget(button)
        self.production_mode_button.clicked.connect(lambda: self._select_daily_mode("production"))
        self.calibration_mode_button.clicked.connect(lambda: self._select_daily_mode("calibration"))
        self.calibration_schedule_label = QLabel()
        self.calibration_schedule_label.setWordWrap(True)
        self.calibration_schedule_label.setStyleSheet("color:#F5A623;font-size:11px;")
        self.widget_4.layout().insertLayout(0, row)
        self.widget_4.layout().insertWidget(1, self.calibration_schedule_label)
        self._daily_timer = QtCore.QTimer(self)
        self._daily_timer.timeout.connect(self._refresh_daily_calibration)
        self._daily_timer.start(1000)
        self._refresh_daily_calibration()

    def _daily_state(self):
        now = daily_calibration_now()
        model = self.selected_model or self.model_name
        cfg = DAILY_CALIBRATION[model]
        start = now.replace(hour=cfg["start"][0], minute=cfg["start"][1], second=0, microsecond=0)
        limits = json.dumps(cfg["limits"], sort_keys=True)
        with sqlite3.connect(DAILY_CALIBRATION_DB) as db:
            rows = db.execute("SELECT status, started_at, limits_json, serialnumber FROM jig_calibration WHERE day=? AND model=? ORDER BY id DESC",
                              (now.date().isoformat(), model)).fetchall()
        eligible = [r for r in rows if calibration_datetime.datetime.fromisoformat(r[1]) >= start]
        failed = any(r[0] == "FAIL" for r in eligible)
        valid = bool(eligible and eligible[0][0] == "PASS" and eligible[0][2] == limits and eligible[0][3] == cfg["serial"])
        minutes = now.hour * 60 + now.minute
        opens = cfg["start"][0] * 60 + cfg["start"][1]
        ends = cfg["end"][0] * 60 + cfg["end"][1]
        return now, cfg, valid, failed, minutes, opens, ends

    def _select_daily_mode(self, mode):
        if self._daily_busy():
            return
        self._daily_mode = mode
        self._refresh_daily_calibration()

    def _daily_busy(self):
        thread = getattr(self, "_test_thread", None)
        return bool(getattr(self, "_homing_busy", False) or (thread and thread.is_alive()))

    def _refresh_daily_calibration(self):
        try:
            now, cfg, valid, failed, minutes, opens, ends = self._daily_state()
        except Exception as exc:
            self.pushButton_19.setEnabled(False)
            self.production_mode_button.setEnabled(False)
            self.calibration_mode_button.setEnabled(False)
            self.calibration_schedule_label.setText(f"Calibration database error: {exc}")
            return
        busy = self._daily_busy()
        if not busy:
            if valid or minutes < opens:
                self._daily_mode = "production"
            elif minutes >= ends:
                self._daily_mode = "calibration"
        calibration = self._daily_mode == "calibration"
        if not busy and self._daily_input_mode != self._daily_mode:
            if calibration:
                self._saved_production_serial = self.lineEdit_3.text()
                self.lineEdit_3.setText(cfg["serial"])
            elif self._daily_input_mode == "calibration":
                self.lineEdit_3.setText(getattr(self, "_saved_production_serial", ""))
            self._daily_input_mode = self._daily_mode
        self.lineEdit_3.setReadOnly(calibration)
        production_ok = not failed and (valid or minutes < ends)
        calibration_ok = not valid and not failed and minutes >= opens
        self.production_mode_button.setChecked(not calibration)
        self.calibration_mode_button.setChecked(calibration)
        self.production_mode_button.setEnabled(production_ok and not busy)
        self.calibration_mode_button.setEnabled(calibration_ok and not busy)
        self.pushButton_19.setEnabled(not busy and self.home_done and (calibration_ok if calibration else production_ok))
        window = f"{cfg['start'][0]:02d}:{cfg['start'][1]:02d}–{cfg['end'][0]:02d}:{cfg['end'][1]:02d} IST"
        text = "PASS — next calibration tomorrow" if valid else "FAILED — service required; retry blocked today" if failed else "REQUIRED — production blocked" if minutes >= ends else f"Due by {cfg['end'][0]:02d}:{cfg['end'][1]:02d}" if minutes >= opens else "Scheduled"
        self.calibration_schedule_label.setText(f"{self.selected_model}: {window} | {text}")
        today = now.date().isoformat()
        if not busy and self.home_done and not valid and not failed and opens <= minutes < ends and self._daily_reminder != today:
            self._daily_reminder = today
            QMessageBox.information(self, "Calibration time", f"Golden-device calibration is due ({window}). Production is available until the end of the window; after that it is blocked until calibration passes.")

    def _prepare_daily_calibration(self):
        if not self.home_done:
            return True  # Existing homing-required message handles this.
        try:
            self._refresh_daily_calibration()
            now, cfg, valid, failed, minutes, opens, ends = self._daily_state()
            if failed:
                QMessageBox.warning(self, "Service required", "Today's calibration failed. Production and retry are blocked.")
                return False
            calibration = self._daily_mode == "calibration" and not valid
            if calibration and minutes < opens:
                return False
            if not calibration and not valid and minutes >= ends:
                return False
            if calibration:
                limits = "; ".join(f"{k}: {v[0]:g}–{v[1]:g} N" for k, v in cfg["limits"].items())
                if QMessageBox.question(self, "Golden-device calibration", f"Place {cfg['serial']} in the jig.\n{limits}\nStart calibration?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
                    return False
                # Recheck date/window after the modal before creating the attempt.
                now, cfg, valid, failed, minutes, opens, ends = self._daily_state()
                if valid or failed or minutes < opens:
                    return False
                with sqlite3.connect(DAILY_CALIBRATION_DB) as db:
                    cur = db.execute("INSERT INTO jig_calibration(day,model,serialnumber,employee,started_at,status,limits_json) VALUES(?,?,?,?,?,'RUNNING',?)",
                        (now.date().isoformat(), self.selected_model, cfg["serial"], str(self.employee_id), now.isoformat(), json.dumps(cfg["limits"], sort_keys=True)))
                    self._daily_attempt = cur.lastrowid
                self._daily_started_day = now.date().isoformat()
                self.lineEdit_3.setText(cfg["serial"])
            elif not self.lineEdit_3.text().strip():
                QMessageBox.warning(self, "Scan required", "Scan the production serial number.")
                return False
            self.is_jig_calibration = calibration
            return True
        except Exception as exc:
            QMessageBox.warning(self, "Calibration error", f"Test blocked: {exc}")
            return False

    def _finish_daily_calibration(self, error=""):
        if self._daily_attempt is None:
            return
        cfg = DAILY_CALIBRATION[self.selected_model]
        online = getattr(self, "_online_button_dips", {})
        dips = {key: online.get(key) for key in cfg["limits"]}
        failures = []
        for key, (low, high) in cfg["limits"].items():
            value = dips[key]
            if value is None or not math.isfinite(value) or not low <= value <= high:
                failures.append(f"{key}: {value} N; expected {low:g}–{high:g} N")
        if self.selected_model == "BUTTON":
            failures.extend(self.gpio_failures.get(key, f"{key} GPIO{pin} response missing")
                            for key, pin in GPIO_BUTTON_PINS.items() if not self.gpio_validation.get(key, False))
        if error:
            failures.append(error)
        now = daily_calibration_now()
        if now.date().isoformat() != self._daily_started_day:
            failures.append("IST date changed during calibration")
        passed = not failures
        reason = "; ".join(failures)
        with sqlite3.connect(DAILY_CALIBRATION_DB) as db:
            db.execute("UPDATE jig_calibration SET finished_at=?,status=?,dips_json=?,reason=? WHERE id=?",
                       (now.isoformat(), "PASS" if passed else "FAIL", json.dumps(dips), reason, self._daily_attempt))
        report_note = ""
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            folder = calibration_os.path.join(calibration_os.path.dirname(DAILY_CALIBRATION_DB), "calibration_reports", now.date().isoformat())
            calibration_os.makedirs(folder, exist_ok=True)
            stem = calibration_os.path.join(folder, f"{self.selected_model}_{self._daily_attempt}")
            fig = Figure(figsize=(9, 5), tight_layout=True)
            FigureCanvasAgg(fig)
            ax = fig.add_subplot(111)
            for key, data in {"right": self.data1, "centre": self.data2, "left": self.data3, "joystick": self.data4, "tstick": self.data5}.items():
                if key in cfg["limits"]:
                    force, distance = self.parse_data(data)
                    ax.plot(distance, force, label=f"{key}: {dips[key]} N")
            ax.set(xlabel="Displacement (mm)", ylabel="Force (N)", title=f"{self.selected_model} calibration: {'PASS' if passed else 'FAIL'}")
            ax.legend(); ax.grid(alpha=.25)
            fig.savefig(stem + ".png", dpi=150)
            with open(stem + ".json", "w") as file:
                json.dump(dict(serial=cfg["serial"], employee=str(self.employee_id), model=self.selected_model, time=now.isoformat(), dips=dips, passed=passed, reason=reason), file, indent=2)
        except Exception as exc:
            report_note = f"\nReport error: {exc}"
        try:
            import requests as calibration_requests
            response = calibration_requests.post(JIG_PASS, headers=HEADERS, json={"data": {
                "calibrate_by": self.employee_id, "qc_system": "C60FamilyBDTJ01",
                "system": "3ButtonButtonDisplacement" if self.selected_model == "BUTTON" else "TSTICKButtonDisplacement",
                "model": "Button" if self.selected_model == "BUTTON" else "tstick",
                "date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "serial_number": cfg["serial"], "calibrate_date": now.strftime("%Y-%m-%d %H:%M:%S"),
                "values": json.dumps(dips), "calibration_status": "PASS" if passed else "FAIL"}}, timeout=10)
            sent = response.status_code in (200, 201)
            if not sent:
                report_note += f"\nERP upload failed (HTTP {response.status_code}); local result retained."
        except Exception as exc:
            sent = False
            report_note += f"\nERP upload failed: {exc}; local result retained."
        with sqlite3.connect(DAILY_CALIBRATION_DB) as db:
            db.execute("UPDATE jig_calibration SET erp_sent=? WHERE id=?", (int(sent), self._daily_attempt))
        self._daily_attempt = None
        self.is_jig_calibration = False
        self._daily_mode = "production" if passed else "calibration"
        self.lineEdit_3.clear()
        self._refresh_daily_calibration()
        self.label_2.setText("CALIBRATION PASS" if passed else "CALIBRATION FAIL — SERVICE REQUIRED")
        if passed:
            QMessageBox.information(self, "Calibration passed", "Today's calibration passed. Next calibration tomorrow." + report_note)
        else:
            QMessageBox.warning(self, "Service required", reason + "\nProduction and retry blocked for today." + report_note)


    def goto_employee_selection(self):
        dlg = PremiumMessageBox(self, "info", "Go Back?",
            "Return to Employee Selection?\nAny unsaved progress will be lost.", auto_close=False)
        # Add a Cancel button dynamically
        ok_btn_ref = dlg.findChild(QtWidgets.QPushButton)
        cancel_btn = QtWidgets.QPushButton("  CANCEL  ")
        cancel_btn.setFixedHeight(52)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.08);
                color: rgba(224,247,250,0.75);
                font-weight: 700; font-size: 15px;
                border-radius: 14px; border: 1px solid rgba(255,255,255,0.15);
                letter-spacing: 2px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.14); }
        """)
        cancel_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        cancel_btn.clicked.connect(dlg.reject)
        # Insert cancel next to ok
        if ok_btn_ref:
            parent_layout = ok_btn_ref.parentWidget().layout()
            if parent_layout:
                row = QHBoxLayout()
                row.setSpacing(14)
                row.addStretch()
                row.addWidget(cancel_btn)
                row.addWidget(ok_btn_ref)
                row.addStretch()
                parent_layout.insertLayout(parent_layout.count(), row)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.new_window = EmployeeEntry()
            self.new_window.show()
            self.close()

    # def home_gcode(self):
    #     try:
    #         print("🏠 Sending HOME ($H) command...")
    #         self.send_gcode("$H", self.handle_data)  # send to GRBL
    #         self.label_2.setText("Homing in progress...")
    #         time.sleep(2.6)  # give GRBL some time
    #         self.label_2.setText("✅ Homing complete")
    #     except Exception as e:
    #         print("❌ Error in home_gcode:", e)
    #         self.label_2.setText(f"Error: {e}")

    def closeEvent(self, event):
        # Never close GPIO underneath an active motion/test worker.
        if self._daily_busy():
            QMessageBox.warning(self, "Test in progress", "Wait for homing or the current test to finish before closing.")
            event.ignore()
            return
        try:
            if self._gpio_check is not None:
                self._gpio_check.close()
                self._gpio_check = None
        except Exception as e:
            print(f"GPIO cleanup error: {e}")
        try:
            if hasattr(self, "serial_thread"):
                self.serial_thread.stop()
        except Exception as e:
            print(f"❌ Error while stopping serial thread: {e}")
        event.accept()
    def __init__(self,employee_id,job_card_id,model_name):
        super().__init__()
        
        self.employee_id=employee_id
        self.job_card_id=job_card_id
        self.model_name=model_name

        self.selected_model = model_name
        self.setupUi(self)

        self.serial_thread = SerialThread(ARDUINO_PORT, GRBL_PORT, SERIAL_BAUDRATE)#arduino,grbl

        self.serial_thread.data_received.connect(self.handle_data)
        

        self.data1=[]
        self.data2=[]
        self.data3=[] 
        self.data4=[] 
        self.data5=[]
        self.serial_number = None
        self._gpio_check = None
        shorten_pending_gpio_records()
        self.gpio_validation = {}
        self.gpio_failures = {}


        self.home_done = False
        self.is_jig_calibration = False
        self._init_daily_calibration()

        # ui_sql.online_status(self)
        def read_serial_data(self):
            while True:
                if self.ser.in_waiting > 0:
                    try:
                        data = self.ser.readline().decode('utf-8').strip()
                        print(f"🔁 Serial Data Received: {data}")
                    except Exception as e:
                        print("❌ Error reading serial:", e)



    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        # ─── GLOBAL STYLESHEET ──────────────────────────────────────────────────
        MainWindow.setStyleSheet("""
            QMainWindow, QWidget#centralwidget {
                background: #07080f;
            }
            QWidget {
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                color: #cde4f0;
                background: transparent;
            }
            QLabel { background: transparent; }
            QLineEdit {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(0,220,255,0.25);
                border-radius: 8px;
                color: #e8f4fa;
                padding: 4px 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0,220,255,0.70);
                background: rgba(0,220,255,0.07);
            }
            QComboBox {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(0,220,255,0.25);
                border-radius: 8px;
                color: #e8f4fa;
                padding: 4px 10px;
                font-size: 13px;
            }
            QComboBox QAbstractItemView {
                background: #0d1525;
                color: #e8f4fa;
                border: 1px solid rgba(0,220,255,0.20);
                selection-background-color: rgba(0,220,255,0.15);
                outline: none;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; }
            QTextEdit {
                background: rgba(0,0,0,0.85);
                color: #00e5b8;
                border: 1px solid rgba(0,220,255,0.12);
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 8px;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.03);
                width: 4px; border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,220,255,0.30);
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        # ─── CENTRAL WIDGET ─────────────────────────────────────────────────────
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background: #07080f;")

        # Root horizontal layout: sidebar | main content
        root_layout = QHBoxLayout(self.centralwidget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # ═══════════════════════════════════════════════════════════════════════
        # LEFT SIDEBAR
        # ═══════════════════════════════════════════════════════════════════════
        self.full_menu_widget = QtWidgets.QWidget()
        self.full_menu_widget.setObjectName("full_menu_widget")
        self.full_menu_widget.setFixedWidth(120)
        self.full_menu_widget.setStyleSheet("""
            QWidget#full_menu_widget {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(0,220,255,0.14);
                border-radius: 18px;
            }
        """)

        sidebar_layout = QVBoxLayout(self.full_menu_widget)
        sidebar_layout.setContentsMargins(10, 14, 10, 14)
        sidebar_layout.setSpacing(6)

        # Brand label
        self.label_3 = QtWidgets.QLabel("bluArmor")
        self.label_3.setObjectName("label_3")
        self.label_3.setAlignment(Qt.AlignCenter)
        self.label_3.setStyleSheet("""
            font-size: 11px; font-weight: 900; color: #00dcff;
            letter-spacing: 2px; padding: 6px 0 8px 0;
            border-bottom: 1px solid rgba(0,220,255,0.15);
            border-radius: 0;
        """)
        sidebar_layout.addWidget(self.label_3)
        sidebar_layout.addSpacing(6)

        def _sidebar_btn(text, color_hex=None):
            btn = QtWidgets.QPushButton(text)
            c = color_hex or "rgba(0,220,255,0.55)"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {c};
                    border: 1px solid rgba(0,220,255,0.12);
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: 700;
                    padding: 9px 4px;
                    letter-spacing: 0.5px;
                }}
                QPushButton:hover {{
                    background: rgba(0,220,255,0.10);
                    border: 1px solid rgba(0,220,255,0.40);
                    color: #ffffff;
                }}
                QPushButton:pressed {{
                    background: rgba(0,220,255,0.18);
                }}
            """)
            btn.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
            return btn

        self.pushButton_7 = _sidebar_btn("⌂  HOME", "#69f0ae")
        self.pushButton_7.setObjectName("pushButton_7")
        sidebar_layout.addWidget(self.pushButton_7)

        self.pushButton_8 = _sidebar_btn("B")
        self.pushButton_8.setObjectName("pushButton_8")
        sidebar_layout.addWidget(self.pushButton_8)

        self.pushButton_9 = _sidebar_btn("C")
        self.pushButton_9.setObjectName("pushButton_9")
        sidebar_layout.addWidget(self.pushButton_9)

        self.pushButton_10 = _sidebar_btn("D")
        self.pushButton_10.setObjectName("pushButton_10")
        sidebar_layout.addWidget(self.pushButton_10)

        self.pushButton_11 = _sidebar_btn("← Back")
        self.pushButton_11.setObjectName("pushButton_11")
        sidebar_layout.addWidget(self.pushButton_11)
        self.pushButton_11.clicked.connect(self.goto_employee_selection)

        sidebar_layout.addSpacing(4)

        # Divider
        div1 = QtWidgets.QFrame()
        div1.setFixedHeight(1)
        div1.setStyleSheet("background: rgba(0,220,255,0.10); border: none; border-radius: 0;")
        sidebar_layout.addWidget(div1)
        sidebar_layout.addSpacing(4)

        self.pause_button = _sidebar_btn("⏸  Pause", "#ffca28")
        self.pause_button.setObjectName("pause_button")
        sidebar_layout.addWidget(self.pause_button)

        self.resume_button = _sidebar_btn("▶  Resume", "#40c4ff")
        self.resume_button.setObjectName("resume_button")
        sidebar_layout.addWidget(self.resume_button)

        self.complete_button = _sidebar_btn("✓  Complete", "#69f0ae")
        self.complete_button.setObjectName("complete_button")
        sidebar_layout.addWidget(self.complete_button)

        sidebar_layout.addStretch()

        # Toggle/Exit at bottom
        self.pushButton_13 = QtWidgets.QPushButton("≡")
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_13.setCheckable(True)
        self.pushButton_13.setStyleSheet("""
            QPushButton {
                background: transparent; color: rgba(0,220,255,0.45);
                border: 1px solid rgba(0,220,255,0.12); border-radius: 10px;
                font-size: 16px; padding: 6px;
            }
            QPushButton:hover { background: rgba(0,220,255,0.10); color: #fff; }
        """)
        sidebar_layout.addWidget(self.pushButton_13)

        self.pushButton_12 = QtWidgets.QPushButton("✕  Exit")
        self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_12.setStyleSheet("""
            QPushButton {
                background: rgba(255,60,60,0.10);
                color: #ff5252;
                border: 1px solid rgba(255,60,60,0.25);
                border-radius: 10px;
                font-size: 10px; font-weight: 700;
                padding: 9px 4px; letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: rgba(255,60,60,0.22);
                border: 1px solid #ff5252; color: #fff;
            }
            QPushButton:pressed { background: #3a0010; }
        """)
        self.pushButton_12.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        sidebar_layout.addWidget(self.pushButton_12)

        root_layout.addWidget(self.full_menu_widget)

        # ═══════════════════════════════════════════════════════════════════════
        # MAIN CONTENT AREA (vertical: topbar | body)
        # ═══════════════════════════════════════════════════════════════════════
        content_col = QVBoxLayout()
        content_col.setSpacing(10)
        root_layout.addLayout(content_col)

        # ── TOP BAR ─────────────────────────────────────────────────────────────
        self.widget = QtWidgets.QWidget()
        self.widget.setObjectName("widget")
        self.widget.setFixedHeight(48)
        self.widget.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(0,220,255,0.12);
                border-radius: 14px;
            }
        """)
        topbar_layout = QHBoxLayout(self.widget)
        topbar_layout.setContentsMargins(16, 0, 16, 0)
        topbar_layout.setSpacing(10)

        # Status pill
        self.label_2 = QtWidgets.QLabel("● READY FOR TEST")
        self.label_2.setObjectName("label_2")
        self.label_2.setStyleSheet("""
            font-size: 11px; font-weight: 700; color: #69f0ae;
            letter-spacing: 1.5px;
        """)
        topbar_layout.addWidget(self.label_2)

        topbar_layout.addStretch()

        # Title
        self.label_5 = QtWidgets.QLabel("BUTTON DISPLACEMENT JIG")
        self.label_5.setObjectName("label_5")
        self.label_5.setAlignment(Qt.AlignCenter)
        self.label_5.setStyleSheet("""
            font-size: 13px; font-weight: 900; color: #00dcff;
            letter-spacing: 4px;
        """)
        topbar_layout.addWidget(self.label_5)

        topbar_layout.addStretch()

        # Clear graph button (was pushButton_14)
        self.pushButton_14 = QtWidgets.QPushButton("Clear Graph")
        self.pushButton_14.setObjectName("pushButton_14")
        self.pushButton_14.setFixedHeight(30)
        self.pushButton_14.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.05);
                color: rgba(200,230,240,0.60);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 8px;
                font-size: 10px; font-weight: 600;
                padding: 0 12px; letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.10);
                color: #fff;
            }
        """)
        self.pushButton_14.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        topbar_layout.addWidget(self.pushButton_14)

        content_col.addWidget(self.widget)

        # ── BODY ROW (left panel | graph panel) ─────────────────────────────────
        body_row = QHBoxLayout()
        body_row.setSpacing(10)
        content_col.addLayout(body_row, stretch=1)

        # ── LEFT PANEL: Control card + Log card ──────────────────────────────────
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        body_row.addLayout(left_col, stretch=1)

        # ── CONTROL CARD ─────────────────────────────────────────────────────────
        self.widget_4 = QtWidgets.QWidget()
        self.widget_4.setObjectName("widget_4")
        self.widget_4.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(0,220,255,0.16);
                border-radius: 18px;
            }
        """)
        control_layout = QVBoxLayout(self.widget_4)
        control_layout.setContentsMargins(24, 20, 24, 20)
        control_layout.setSpacing(16)

        # Card header
        ctrl_header = QHBoxLayout()
        ctrl_title = QtWidgets.QLabel("TEST CONFIGURATION")
        ctrl_title.setStyleSheet("""
            font-size: 10px; font-weight: 800; color: rgba(0,220,255,0.55);
            letter-spacing: 3px;
        """)
        ctrl_header.addWidget(ctrl_title)
        ctrl_header.addStretch()
        control_layout.addLayout(ctrl_header)

        # Device row
        dev_row = QHBoxLayout()
        dev_row.setSpacing(16)
        self.label = QtWidgets.QLabel("Device")
        self.label.setObjectName("label")
        self.label.setStyleSheet("font-size: 12px; font-weight: 600; color: rgba(200,230,240,0.70);")
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItems(["BUTTON", "TSTICK"])
        self.comboBox.setFixedHeight(36)
        self.comboBox.setStyleSheet("""
            QComboBox {
                background: rgba(0,220,255,0.06);
                border: 1px solid rgba(0,220,255,0.28);
                border-radius: 9px;
                color: #e8f4fa;
                padding: 0 12px;
                font-size: 13px; font-weight: 600;
            }
            QComboBox:hover { border: 1px solid rgba(0,220,255,0.55); }
            QComboBox QAbstractItemView {
                background: #0d1525; color: #e8f4fa;
                selection-background-color: rgba(0,220,255,0.15);
                border: 1px solid rgba(0,220,255,0.20);
                outline: none;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; }
        """)
        dev_row.addWidget(self.label)
        dev_row.addWidget(self.comboBox, stretch=1)
        control_layout.addLayout(dev_row)

        # Serial number row
        ser_row = QHBoxLayout()
        ser_row.setSpacing(16)
        self.label_4 = QtWidgets.QLabel("Serial No.")
        self.label_4.setObjectName("label_4")
        self.label_4.setStyleSheet("font-size: 12px; font-weight: 600; color: rgba(200,230,240,0.70);")
        self.lineEdit_3 = QtWidgets.QLineEdit()
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_3.setEnabled(True)
        self.lineEdit_3.setFixedHeight(36)
        self.lineEdit_3.setStyleSheet("""
            QLineEdit {
                background: rgba(0,220,255,0.06);
                border: 1px solid rgba(0,220,255,0.28);
                border-radius: 9px;
                color: #e8f4fa;
                padding: 0 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0,220,255,0.70);
                background: rgba(0,220,255,0.09);
            }
        """)
        ser_row.addWidget(self.label_4)
        ser_row.addWidget(self.lineEdit_3, stretch=1)
        control_layout.addLayout(ser_row)

        # Divider
        ctrl_div = QtWidgets.QFrame()
        ctrl_div.setFixedHeight(1)
        ctrl_div.setStyleSheet("background: rgba(0,220,255,0.10); border: none; border-radius: 0;")
        control_layout.addWidget(ctrl_div)

        # RUN button (full width)
        self.pushButton_19 = QtWidgets.QPushButton("▶   RUN TEST")
        self.pushButton_19.setObjectName("pushButton_19")
        self.pushButton_19.setFixedHeight(46)
        self.pushButton_19.setStyleSheet("""
            QPushButton:enabled {
                background: rgba(0,200,83,0.16);
                color: #69f0ae;
                font-size: 13px; font-weight: 900;
                border: 1px solid rgba(0,200,83,0.42);
                border-radius: 12px;
                letter-spacing: 3px;
            }
            QPushButton:enabled:hover {
                background: rgba(0,200,83,0.30);
                border: 1px solid #69f0ae;
                color: #ffffff;
            }
            QPushButton:enabled:pressed {
                background: rgba(0,100,40,0.50);
                color: #69f0ae;
            }
            QPushButton:disabled {
                background: rgba(255,255,255,0.04);
                color: rgba(255,255,255,0.18);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
                font-size: 13px;
                letter-spacing: 3px;
            }
        """)
        self.pushButton_19.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        control_layout.addWidget(self.pushButton_19)

        # Hidden stub buttons (kept for code compatibility — not shown)
        self.pass_button = QtWidgets.QPushButton()
        self.pass_button.setObjectName("PASS")
        self.pass_button.setVisible(False)
        self.fail_button = QtWidgets.QPushButton()
        self.fail_button.setObjectName("FAIL")
        self.fail_button.setVisible(False)

        left_col.addWidget(self.widget_4, stretch=1)

        # ── LOG / DATABASE CARD ───────────────────────────────────────────────────
        self.db_widget = QtWidgets.QWidget()
        self.db_widget.setObjectName("db_widget")
        self.db_widget.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(0,220,255,0.12);
                border-radius: 18px;
            }
        """)
        db_layout = QVBoxLayout(self.db_widget)
        db_layout.setContentsMargins(18, 14, 18, 14)
        db_layout.setSpacing(8)

        db_header = QtWidgets.QLabel("ACTIVITY LOG")
        db_header.setStyleSheet("""
            font-size: 9px; font-weight: 800; color: rgba(0,220,255,0.45);
            letter-spacing: 3px;
        """)
        db_layout.addWidget(db_header)

        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setStyleSheet("""
            QTextEdit {
                background: rgba(0,0,0,0.70);
                color: #00e5b8;
                border: 1px solid rgba(0,220,255,0.10);
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                padding: 8px;
            }
        """)
        db_layout.addWidget(self.textEdit)
        left_col.addWidget(self.db_widget, stretch=1)

        # ── GRAPH PANEL ───────────────────────────────────────────────────────────
        self.graph_widget = QtWidgets.QWidget()
        self.graph_widget.setObjectName("graph_widget")
        self.graph_widget.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(0,220,255,0.14);
                border-radius: 18px;
            }
        """)
        graph_layout = QVBoxLayout(self.graph_widget)
        graph_layout.setContentsMargins(16, 14, 16, 14)
        graph_layout.setSpacing(8)

        self.label_6 = QtWidgets.QLabel("FORCE GRAPH")
        self.label_6.setObjectName("label_6")
        self.label_6.setStyleSheet("""
            font-size: 9px; font-weight: 800; color: rgba(0,220,255,0.45);
            letter-spacing: 3px;
        """)
        graph_layout.addWidget(self.label_6)

        self.canvas = QtWidgets.QWidget()
        self.canvas.setObjectName("canvas")
        graph_layout.addWidget(self.canvas, stretch=1)

        body_row.addWidget(self.graph_widget, stretch=3)

        # ── WIDGET STUBS for compatibility ────────────────────────────────────────
        self.widget_2 = QtWidgets.QWidget()
        self.widget_2.setObjectName("widget_2")
        self.widget_3 = QtWidgets.QWidget()
        self.widget_3.setObjectName("widget_3")
        self.layoutWidget = QtWidgets.QWidget()
        self.layoutWidget.setObjectName("layoutWidget")

        # ── WIRE UP ───────────────────────────────────────────────────────────────
        MainWindow.setCentralWidget(self.centralwidget)
        self.pushButton_14.clicked.connect(self.clear_graph)
        self.pushButton_19.clicked.connect(self.send_gcode_btn1)
        self.pushButton_19.setEnabled(True)
        self.pushButton_7.hide()  # Homing is automatic; no operator HOME button.
     

        self.retranslateUi(MainWindow)
        self.pause_button.clicked.connect(self.pause_jobcard)
        self.resume_button.clicked.connect(self.resume_jobcard)
        self.complete_button.clicked.connect(self.submit_jobcard)
        self.pushButton_13.toggled['bool'].connect(self.full_menu_widget.setHidden) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "bluArmor — Button Displacement Jig"))
        self.label_3.setText(_translate("MainWindow", "bluArmor"))
        self.pushButton_7.setText(_translate("MainWindow", "⌂  HOME"))
        self.pushButton_8.setText(_translate("MainWindow", "B"))
        self.pushButton_9.setText(_translate("MainWindow", "C"))
        self.pushButton_10.setText(_translate("MainWindow", "D"))
        self.pushButton_11.setText(_translate("MainWindow", "← Back"))
        self.pushButton_12.setText(_translate("MainWindow", "✕  Exit"))
        self.pause_button.setText(_translate("MainWindow", "⏸  Pause"))
        self.resume_button.setText(_translate("MainWindow", "▶  Resume"))
        self.complete_button.setText(_translate("MainWindow", "✓  Complete"))
        self.label_5.setText(_translate("MainWindow", "BUTTON DISPLACEMENT JIG"))
        self.pushButton_19.setText(_translate("MainWindow", "▶   RUN TEST"))
        self.label.setText(_translate("MainWindow", "Device"))
        self.label_4.setText(_translate("MainWindow", "Serial No."))
        self.label_2.setText(_translate("MainWindow", "● READY FOR TEST"))
        self.label_6.setText(_translate("MainWindow", "FORCE GRAPH"))
        self.textEdit.setPlainText("ACTIVITY LOG\n─────────────────\n")


    def clear_all_datas(self):
        self.data1.clear()
        self.data2.clear()
        self.data3.clear()
        self.data4.clear()
        self.data5.clear()



    def handle_home_complete(self, data):
        if "ok" in data.lower():
            QtCore.QTimer.singleShot(0, self._handle_home_complete_ui)

    def enable_run_mode(self):
        self.label_2.setText("READY FOR TEST")
        self.pushButton_19.setEnabled(True)

    

    def start_serial(self):
      
        self.clear_all_datas()
        if not self.serial_thread.isRunning():
            self.serial_thread.start()

    def send_gcode(self, gcode, callback=None):
        # entered_gcode = self.gcode_edit.text()
        # if entered_gcode:
       self.serial_thread.send_gcode(gcode, callback)
    @app.route("/home", methods=["POST"])
    def home_command():
        try:
            # Example: send $H to GRBL via serial
            # ser.write(b"$H\n")
            # time.sleep(2.6)
            return jsonify({"success": True, "status": "ACTIVATE"})
        except Exception as e:
            return jsonify({"success": False, "status": f"Error: {e}"})


    
    def home_gcode(self):
        if getattr(self, "_homing_busy", False):
            return
        self._homing_busy = True
        self.home_done = False
        self.pushButton_19.setEnabled(False)
        self.label_2.setText("HOMING...")
        if not self.serial_thread.isRunning():
            self.start_serial()
        def worker():
            try:
                deadline = time.monotonic() + 3
                while not self.serial_thread.running:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Serial reader did not start")
                    time.sleep(0.01)
                self.serial_thread.home_and_wait()
                self.home_done = True
                QtCore.QMetaObject.invokeMethod(self, "_handle_home_complete_ui",
                    QtCore.Qt.QueuedConnection)
            except Exception as exc:
                QtCore.QMetaObject.invokeMethod(self, "_show_motion_error",
                    QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, str(exc)))
            finally:
                self._homing_busy = False
                QtCore.QMetaObject.invokeMethod(self.pushButton_19, "setEnabled",
                    QtCore.Qt.QueuedConnection, QtCore.Q_ARG(bool, self.home_done))
        threading.Thread(target=worker, daemon=True).start()

    def handle_home_complete(self, data):
        if "ok" in data.lower():
            QtCore.QTimer.singleShot(0, self._handle_home_complete_ui)

    @QtCore.pyqtSlot()
    def _handle_home_complete_ui(self):
        self.enable_run_mode()
        self._refresh_daily_calibration()




    def check_serial_exists(self, serial_number):
        if not VALIDATE_FUNCTIONALITY:
            return True
        
        """
        Check functionality PASS based on selected model.

        BUTTON:
            field  = 3_button_serialnumber
            system = 3buttoniptesting

        TSTICK:
            field  = t_stick_serialnumber
            system = TStickFunctionality
        """

        model = (self.selected_model or "").strip().upper()

        if model == "BUTTON":
            serial_field, system_name = FUNCTIONALITY_STAGES["BUTTON"]

        elif model == "TSTICK":
            serial_field, system_name = FUNCTIONALITY_STAGES["TSTICK"]

        else:
            print(f"❌ Unsupported model for serial check: {model}")
            return False

        filters = [
            [serial_field, "=", serial_number.strip()],
            ["system", "=", system_name],
            ["status", "=", "pass"]
        ]

        try:
            response = requests.get(
                ERP_PASS,
                headers=HEADERS,
                params={"filters": json.dumps(filters)}
            )

            if response.status_code != 200:
                print(f"❌ ERP Error: Status code {response.status_code}")
                return False

            data = response.json()
            results = data.get("data", [])

            if results:
                print(
                    f"✅ Functionality found: {serial_number} | "
                    f"model={model} | field={serial_field} | system={system_name}"
                )
                return True

            print(
                f"❌ Functionality not found: {serial_number} | "
                f"model={model} | field={serial_field} | system={system_name}"
            )
            return False

        except Exception as e:
            print(f"⚠️ Exception connecting to ERP: {e}")
            return False






    def check_serial(self,serial_number): 
        server_url = WEBSOCKET_URL

        try:
            ws = websocket.create_connection(server_url)
            print("Connected to WebSocket server (Fetch Data)")

            message = {
                "type": "sleepcurrent",
                "serial": serial_number
            }
            ws.send(json.dumps(message))

            response = ws.recv()
            print(response)
            ws.close()
            print("Connection closed\n")

        
            data = json.loads(response)
            print(data)

            
            if data.get("status") == "success" :
                first_entry = data["data"][0]  
                batch = first_entry.get("batch")
                if batch:
                    return batch

                else:
                    print("BATCH not found in response.")
            else:
                print("Unexpected or error response:", data)

        except Exception as e:
            print(f"Error fetching data for serial '{serial_number}':", e)

    def send_gcode_btn1(self):
        if getattr(self, "_homing_busy", False) or (getattr(self, "_test_thread", None) and self._test_thread.is_alive()):
            return
        if not self._prepare_daily_calibration():
            return

        if not self.home_done:
            QMessageBox.warning(self, "Homing required", "Initial homing has not completed. Reopen the model window to home again.")
            return

        # ── NORMAL TEST RUN ───────────────────────────────────────────────
        # Run jig motion and force measurement in a background thread so
        # time.sleep() calls do not block the Qt UI.
        self.pushButton_19.setEnabled(False)
        self.label_2.setText("● RUNNING TEST")
        self.label_2.setStyleSheet("font-size:11px; font-weight:700; color:#00dcff; letter-spacing:1.5px;")

        self.clear_graph()
        self.start_serial()
        self.serial_number = self.lineEdit_3.text().strip()
        if not self.is_jig_calibration:
            # Production devices must pass the previous-stage and rejection gates.
            # ~ if not self.check_serial_exists(self.serial_number):
                # ~ self.label_2.setText("Previous stage not done")
                # ~ self.pushButton_19.setEnabled(True)
                # ~ return

            # ~ if check_serial_existss(self.serial_number):
                # ~ self.label_2.setText("Already failed")
                # ~ self.pushButton_19.setEnabled(True)
                # ~ return

            print("Serial number is valid. Proceeding...")
            self.label_2.setText("Serial number is valid.")
        else:
            # Golden devices are independent of production functionality/results.
            print("Golden-device calibration: skipping functionality and rejection checks.")
            self.label_2.setText("Golden-device calibration running.")

        self._test_thread = threading.Thread(target=self._run_test, daemon=True)
        self._test_thread.start()

    def _run_test(self):
        """Run jig motion and force/DIP measurement in background."""
        try:
            dips = {}
            self._online_button_dips = {}
            self.gpio_validation = {}
            self.gpio_failures = {}
            if self.selected_model == "BUTTON":
                try:
                    if self._gpio_check is None:
                        self._gpio_check = HarnessGPIOCheck()
                    self._gpio_check.reset()
                except Exception as exc:
                    QtCore.QMetaObject.invokeMethod(self, "_gpio_setup_failed", QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, str(exc)))
                    return  # No motion started; do not recovery-home for a GPIO setup error.
            deadline = time.monotonic() + 3
            while not self.serial_thread.running:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Force sensor serial thread did not start")
                time.sleep(0.01)


            if self.selected_model in ["BUTTON"]:
                self._online_button_dips = {}
                # Complete each press/retract before switching its data callback.
                self._run_button_motion(self.handle_data_btn1, [
                    "G0 X70.755 Y38.808 Z13.798",
                    "FORCE_PRESS","G0 Z13.798"])
                self._run_button_motion(self.handle_data_btn2, [
                    "G0 X57.124 Y37.753 Z11.880",
                    "FORCE_PRESS","G0 Z11.880"])
                self._run_button_motion(self.handle_data_btn3, [
                    "G0 X43.493 Y38.8808 Z13.798",
                    "FORCE_PRESS","G0 Z11.798"])
                self.serial_thread.callback = self.handle_data
                self.serial_thread.move_and_wait(
                    "G0 X8.070 Y38.528 Z12.66", self.handle_data)

            elif self.selected_model in ["TSTICK"]:
                # Both force presses wait for confirmed retraction.
                self.send_tstick_btn1()
                self.send_tstick_btn2()
                # send_tstick_btn2 already returns to X7.922 Y38.221 Z11.119.
                # Stay at that reference point; do not add a move to origin.

            self.serial_thread.stop()
            QtCore.QMetaObject.invokeMethod(
                self, "plot", QtCore.Qt.BlockingQueuedConnection
            )
            self.serial_thread.stop()

        except Exception as e:
            print(f"❌ _run_test error: {e}")
            message = str(e)
            try:
                # Keep the reader alive until reset and recovery homing finish.
                self.home_done = False
                self.serial_thread.home_and_wait(recover=True)
                self.home_done = True
                message += "\nAutomatic recovery homing completed. Scan and start a new test."
            except Exception as home_error:
                message += f"\nAutomatic homing failed: {home_error}. Check the controller/jig."
            QtCore.QMetaObject.invokeMethod(self, "_show_motion_error",
                QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, message))
        finally:
            if self._gpio_check is not None:
                # Keep the pin factory and callbacks alive for the next Run.
                self._gpio_check.disarm()
            self.serial_thread.callback = self.handle_data
            if self.serial_thread.isRunning():
                self.serial_thread.stop()
            QtCore.QMetaObject.invokeMethod(
                self.pushButton_19, "setEnabled",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(bool, self.home_done)
            )
    def _run_button_motion(self, callback, commands):
        for command in commands:
            if command == "FORCE_PRESS":
                key = {"handle_data_btn1": "right", "handle_data_btn2": "centre",
                       "handle_data_btn3": "left", "handle_data_btn4": "joystick",
                       "handle_data_btn5": "tstick"}[callback.__name__]
                if not hasattr(self, "_online_button_dips"):
                    self._online_button_dips = {}
                # Extra approach travel for the two TSTICK points only.
                allowance = 12.0 if key in ("joystick", "tstick") else 8.0
                if self._gpio_check is not None and key in GPIO_BUTTON_PINS:
                    self._gpio_check.arm(key)
                self._online_button_dips[key] = self.serial_thread.press_until_force(
                    callback, max_travel_mm=allowance)
            else:
                self.serial_thread.move_and_wait(command, callback)
        # Short sensor settling window after confirmed retraction, not a
        # guessed movement delay. Keep the outgoing button's callback active.
        time.sleep(0.2)
        key = {"handle_data_btn1": "right", "handle_data_btn2": "centre", "handle_data_btn3": "left"}.get(callback.__name__)
        if self._gpio_check is not None and key:
            self.gpio_validation[key] = self._gpio_check.finish(key)
            self.gpio_failures = dict(self._gpio_check.errors)

    @QtCore.pyqtSlot(str)
    def _gpio_setup_failed(self, message):
        if self.is_jig_calibration:
            self._finish_daily_calibration("GPIO setup failed: " + message)
        self.label_2.setText("GPIO UNAVAILABLE — TEST NOT STARTED")
        QMessageBox.warning(self, "GPIO setup failed", message)

    @QtCore.pyqtSlot(str)
    def _show_motion_error(self, message):
        if self.is_jig_calibration:
            self._finish_daily_calibration(message)
        self.label_2.setText("TEST STOPPED - MOTION ERROR")
        QMessageBox.critical(self, "Motion error", message)

    def send_gcode_btn2(self):
        time.sleep(10)
        # self.send_gcode("$H",self.handle_data_btn2)
        self.send_gcode("G0 X57.532 Y38.221 Z11.119", self.handle_data_btn2)
        self.send_gcode("G1 Z14.622 F50", self.handle_data_btn2)
        # self.send_gcode("G1 Z15.2 F80", self.handle_data_btn2)#15
        self.send_gcode("G0 Z11", self.handle_data_btn2)

    def send_gcode_btn3(self):
        # self.send_gcode("$H",self.handle_data_btn3)

        self.send_gcode("G0 X43 .737 Y38.889 Z11.119", self.handle_data_btn3)
        self.send_gcode("G1 Z18.816 F50", self.handle_data_btn3)
        self.send_gcode("G0 z7", self.handle_data_btn3)
        self.send_gcode("G0 X7.922 Y38.221 Z10",self.handle_data_btn3)
        self.send_gcode("G0 Z11.119",self.handle_data_btn3)

        # if self.is_jig_calibration:
        #     self.send_gcode("X8.129 Y38.528 z12.66",self.handle_data_btn3)

        time.sleep(0.5)

    def send_gcode_btn4(self):
        self.send_gcode("$H", self.handle_data_btn4)
    
    def send_tstick_btn1(self):
        # Joystick: original approach/return with force-controlled F50 press.
        self._run_button_motion(self.handle_data_btn4, [
            "G0 X101.922 Y49.156 Z15.174",
            "FORCE_PRESS","G0 Z15.174"])

    def send_tstick_btn2(self):
        time.sleep(2)
        # T-stick: original approach/return with force-controlled F50 press.
        self._run_button_motion(self.handle_data_btn5, [
            "G0 X140.492 Y27.984 Z19.398",
            "FORCE_PRESS", "G0 Z19.32988", "G0 X7.922 Y38.221 Z11.119"])


    def handle_data(self, data):
        # print(f"Received data: {data}")
        pass

    def handle_data_btn1(self, data):
        self.data1.append(data)
        # print(f"Received data for Btn1: {data}")
        # print(self.data1)

    def handle_data_btn2(self, data):
        self.data2.append(data)

        # print(f"Received data for Btn2: {data}")

    def handle_data_btn3(self, data):
        self.data3.append(data)

        # print(f"Received data for Btn3: {data}")
    def handle_data_btn4(self, data):
        self.data4.append(data)

        # print(f"Received data for Btn4: {data}")   
        
    def handle_data_btn5(self, data):
        self.data5.append(data)

        # print(f"Received data for Btn5: {data}")
    def parse_data(self, data):
        x_values = []
        y_values = []

        for point in data:
            try:
                # Ignore non numeric (ok, MSG, etc.)
                if not any(ch.isdigit() for ch in point):
                    continue

                clean = point.replace("(", "").replace(")", "")
                x, y = map(float, clean.split(","))

                x_values.append(x)
                y_values.append(y)

            except Exception as e:
                print(f"error processing data: {e}")

        return x_values, y_values



    def find_dips(self, x_values, threshold=DIP_THRESHOLD, force_one=False):
            dips = []
            cleaned = [x for x in x_values if x > 0]
            if not cleaned:
                return dips

            max_idx = cleaned.index(max(cleaned))
            for i in range(1, max_idx):
                if cleaned[i] <= cleaned[i-1] and cleaned[i] <= cleaned[i+1]:
                    left_diff = abs(cleaned[i-1] - cleaned[i])
                    right_diff = abs(cleaned[i+1] - cleaned[i])
                    if left_diff > threshold or right_diff > threshold:
                        dips.append(round(cleaned[i], 2))

            # Remove near-duplicates
            final_dips = []
            for d in dips:
                if all(abs(existing - d) > threshold for existing in final_dips):
                    final_dips.append(d)

            if not final_dips and force_one:
                final_dips = [round(min(cleaned[:max_idx+1]), 2)]
            return final_dips
        

    def filter_dips(self, dips, curve_name):
        if curve_name.lower() in [ "right","centre","left","joystick","tstick"]:
            return [d for d in dips if FILTER_DIP_RANGE[0] <= d <= FILTER_DIP_RANGE[1]]
        else:
            return dips
    def pause_gcode(self):
        self.send_gcode("M226",self.handle_data)
        print("Pausing G-code execution at x = 5")
    def clear_graph(self):
        # Remove all widgets from the layout
        while self.graph_widget.layout().count() > 0:
            widget = self.graph_widget.layout().takeAt(0).widget()
            if widget is not None:
                # Check if the widget is a QLabel
                if isinstance(widget, QLabel):
                    # Clear the pixmap of the QLabel
                    widget.clear()
                widget.deleteLater()




    @QtCore.pyqtSlot()
    def plot(self):
        if self.is_jig_calibration:
            self._finish_daily_calibration()
            return
        x1, y1 = self.parse_data(self.data1)
        x2, y2 = self.parse_data(self.data2)
        x3, y3 = self.parse_data(self.data3)
        x4, y4 = self.parse_data(self.data4)
        x5, y5 = self.parse_data(self.data5)

        # Calculate exponential moving averages
        alpha = 0.99
        z1 = [0] if y1 else []
        z2 = [0] if y2 else []
        z3 = [0] if y3 else []
        z4 = [0] if y4 else []
        z5 = [0] if y5 else []

        for i in range(1, len(y1)):
            z1.append(z1[i-1] * alpha + (1-alpha) * y1[i])

        for i in range(1, len(y2)):
            z2.append(z2[i-1] * alpha + (1-alpha) * y2[i])

        for i in range(1, len(y3)):
            z3.append(z3[i-1] * alpha + (1-alpha) * y3[i])

        for i in range(1, len(y4)):
            z4.append(z4[i-1] * alpha + (1-alpha) * y4[i])

        for i in range(1, len(y5)):
            z5.append(z5[i-1] * alpha + (1-alpha) * y5[i])

        #x1_cut = []
        #z1_cut = []
        #for x, z in zip(x1, z1):
         #   if x <= 5:  # Cut at 5N for x1
          #      x1_cut.append(x)
           #     z1_cut.append(z)

        #x2_cut = []
        #z2_cut = []
        #for x, z in zip(x2, z2):
         #   if x <= 6:  # Cut at 6N for x2
          #      x2_cut.append(x)
           #     z2_cut.append(z)

        #x3_cut = []
        #z3_cut = []
        #for x, z in zip(x3, z3):
         #   if x <= 7:  # Cut at 7N for x3
          #      x3_cut.append(x)
           #     z3_cut.append(z)
        # Clear the graph widget
        self.clear_graph()
        
        total_data = [(z1,x1),(z2,x2),(z3,x3),(z4,x4),(z5,x5)
                      ]
        
        dips = {
            "right": self.filter_dips(self.find_dips(x1), "right"),
            "centre": self.filter_dips(self.find_dips(x2), "centre"),
            "left": self.filter_dips(self.find_dips(x3), "left"),
            "joystick":self.filter_dips(self.find_dips(x4), "joystick"),
            "tstick":self.filter_dips(self.find_dips(x5), "tstick")
        }
        # Use the pressing dip; do not pick a new minimum during retraction.
        if self.selected_model in ("BUTTON", "TSTICK") and getattr(self, "_online_button_dips", None):
            for key, value in self._online_button_dips.items():
                dips[key] = [round(value, 2)] if value is not None else []
        print("Dips found:", dips)
        # total_data=[(1,2),(212,322),(32,42)]
        # Plot the data
        if self.selected_model in ["BUTTON"]:
            plt.plot(z1, x1, label=f"Right {dips['right']}")
            plt.plot(z2, x2, label=f"Center {dips['centre']}")
            plt.plot(z3, x3, label=f"Left {dips['left']}")
            
        if self.selected_model in ["TSTICK"]:
            plt.plot(z4, x4, label=f"Joystick {dips['joystick']}")
            plt.plot(z5, x5, label=f"Tstick {dips['tstick']}")

        # max_value = max(max(z1), max(z2), max(z3))

        # # Set the limits and ticks of the x-axis
        # plt.xlim(0, max_value)
        # plt.xticks(np.arange(0, max_value + 1, 1))

        # Add labels and legend
        plt.xlabel('Displacement (mm)')
        plt.ylabel('Force (N)')
        plt.legend()
        plt.show()
        imageName = 'plot_{0}_{1}.svg'.format(self.serial_number,datetime.datetime.now().strftime("%d%m%Y_%H%M%S"))

        # Save the plot
        plt.savefig(imageName)
        plt.show(block=True)
        plt.figure().clear()
        # plt.close()
        plt.cla()   #clear the current axes
        plt.clf()  

        # Create a new QLabel to display the image

        for i in reversed(range(self.graph_widget.layout().count())):                #for repeating same position
            self.graph_widget.layout().itemAt(i).widget().setParent(None)
        pixmap = QtGui.QPixmap(imageName)
        label = QtWidgets.QLabel(self.graph_widget)
        label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        label.setPixmap(pixmap)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setScaledContents(True)
        self.graph_widget.layout().addWidget(label)

        
        if self.selected_model == "TSTICK":
            required_keys = ["joystick", "tstick"]
        else:
            required_keys = ["right", "centre", "left"]

        missing = [k for k in required_keys if not dips.get(k)]

        auto_result = None
        fail_reason = ""

        # ---------------- BUTTON ----------------
        if self.selected_model == "BUTTON":

            if missing:
                auto_result = "0"
                fail_reason = f"DIP missing for: {', '.join(missing)}"

            else:
                r = dips["right"][0]
                c = dips["centre"][0]
                l = dips["left"][0]

                if not (PRODUCTION_LIMITS["BUTTON"]["right"][0] <= r <= PRODUCTION_LIMITS["BUTTON"]["right"][1]):
                    auto_result = "0"
                    fail_reason = f"Right DIP out of range ({r}N)"

                elif not (PRODUCTION_LIMITS["BUTTON"]["centre"][0] <= c <= PRODUCTION_LIMITS["BUTTON"]["centre"][1]):
                    auto_result = "0"
                    fail_reason = f"Centre DIP out of range ({c}N)"

                elif not (PRODUCTION_LIMITS["BUTTON"]["left"][0] <= l <= PRODUCTION_LIMITS["BUTTON"]["left"][1]):
                    auto_result = "0"
                    fail_reason = f"Left DIP out of range ({l}N)"

                else:
                    auto_result = "1"
                    fail_reason = ""

        # ---------------- TSTICK ----------------
        elif self.selected_model == "TSTICK":

            if missing:
                auto_result = "0"
                fail_reason = f"DIP missing for: {', '.join(missing)}"

            else:
                j = dips["joystick"][0]
                t = dips["tstick"][0]

                if not (PRODUCTION_LIMITS["TSTICK"]["joystick"][0] <= j <= PRODUCTION_LIMITS["TSTICK"]["joystick"][1]):
                    auto_result = "0"
                    fail_reason = f"Joystick DIP out of range ({j}N)"

                elif not (PRODUCTION_LIMITS["TSTICK"]["tstick"][0] <= t <= PRODUCTION_LIMITS["TSTICK"]["tstick"][1]):
                    auto_result = "0"
                    fail_reason = f"T-Stick DIP out of range ({t}N)"

                else:
                    auto_result = "1"
                    fail_reason = ""

        if self.selected_model == "BUTTON":
            gpio_errors = [self.gpio_failures.get(key, f"{key} GPIO{pin} response missing")
                           for key, pin in GPIO_BUTTON_PINS.items() if not self.gpio_validation.get(key, False)]
            if gpio_errors:
                auto_result = "0"
                fail_reason = "; ".join(([fail_reason] if fail_reason else []) + gpio_errors)

        print("AUTO RESULT:", auto_result, fail_reason)

        if auto_result == "1" and self.selected_model in ["BUTTON"]:
            self.label_2.setText("● DEVICE PASSED")
            self.label_2.setStyleSheet("font-size:11px; font-weight:700; color:#00e676; letter-spacing:1.5px;")
            dlg = PremiumMessageBox(self, "pass", "DEVICE PASSED",
                f"Right: {r} N  ·  Centre: {c} N  ·  Left: {l} N",
                duration_ms=3000, auto_close=True)
            dlg.show()
        elif auto_result == "1" and self.selected_model in ["TSTICK"]:
            self.label_2.setText("● DEVICE PASSED")
            self.label_2.setStyleSheet("font-size:11px; font-weight:700; color:#00e676; letter-spacing:1.5px;")
            dlg = PremiumMessageBox(self, "pass", "DEVICE PASSED",
                f"T-Stick: {t} N  ·  Joystick: {j} N",
                duration_ms=3000, auto_close=True)
            dlg.show()
        else:
            self.label_2.setText("✕  DEVICE FAILED")
            self.label_2.setStyleSheet("font-size:11px; font-weight:700; color:#ff4444; letter-spacing:1.5px;")
            dlg = PremiumMessageBox(self, "fail", "DEVICE FAILED",
                f"Reason: {fail_reason}",
                duration_ms=3500, auto_close=True)
            dlg.show()

        # Save automatically — no button click needed
        single_dips = {
            k: (v[0] if isinstance(v, list) and len(v) > 0 else None)
            for k, v in dips.items()
        }
        self.handle_button_press(imageName, total_data, auto_result, single_dips, fail_reason)

        return total_data

    
    def handle_button_press(self, imageName, total_data, result, dips, fail_reason=""):
        print("handle_button_press result:", result)

        # Save data to SQLite + send to ERP
        self.save_data(self.serial_number, total_data, result, imageName, dips)

        if not self.employee_id or not self.job_card_id:
            print("Error: Employee ID or Job Card ID is missing.")
            return

        if result == "1":
            new_count = increment_pass_count(self.employee_id, self.job_card_id)
            self.pass_count = new_count
            insert_pass_record(self.serial_number, self.selected_model, self.batch, self.employee_id, self.job_card_id, dips)
        elif result == "0":
            if self.selected_model == "BUTTON":
                queued = insert_gpio_fail_record(self.serial_number, self.selected_model, self.batch,
                    self.employee_id, self.job_card_id, dips, fail_reason, self.gpio_validation)
                if not queued:
                    QMessageBox.warning(self, "ERP queue error", "Button failure was not saved to the ERP queue. Check the local database.")
            else:
                insert_fail_record(self.serial_number, self.selected_model, self.batch, self.employee_id, self.job_card_id, dips)


    def save_data(self, serial_no: str, graph: list,result, imageName: str,dips=None):
        print("RESULT:", result)
        batch=self.check_serial(self.serial_number)
        self.batch=batch
        print(batch)
        try:
            # ~ graph_payload = {
                 # ~ "curves": [
                    # ~ {"label": f"Right {dips.get('right', [])}", "data": graph[0]},
                    # ~ {"label": f"Center {dips.get('center', [])}", "data": graph[1]},
                     # ~ {"label": f"Left {dips.get('left', [])}", "data": graph[2]},
                 # ~ ],
                 # ~ "timestamp": datetime.now().isoformat(),
                 # ~ "serial_no": serial_no,
                 # ~ "result": result
            # ~ }
            graph_payload={
                "graph":graph,
                "dips":dips,
                "serial_no":serial_no
            }

            # ✅ Convert → compress → base64 encode
            

            encoded_graph_old = base64.b64encode(
                gzip.compress(json.dumps(graph_payload).encode("utf-8"))
            ).decode("utf-8")
            


            # ✅ Save graph data into database
            if not self.save_graph(serial_no,encoded_graph_old,imageName, result,dips):
                return False

            # Upload all pending rows, including the current measurement.
            return self.send_data_to_server()

        except Exception as e:
            print(f"❌ Error in save_data(): {e}")



    def save_graph(self, serial_no: str, graph, imagename: str, result: int, dips=None):
        """Save graph and dips into SQLite safely"""
        try:
            import json, gzip, base64, sqlite3

            # --- Ensure dips is stored as JSON string ---
            dips_str = json.dumps(dips) if isinstance(dips, (dict, list)) else str(dips)

            # --- Convert and compress graph ---
            if isinstance(graph, (dict, list)):
                graph_json = json.dumps(graph)
            else:
                graph_json = str(graph)

            # ~ compressed_graph = base64.b64encode(
                # ~ gzip.compress(graph_json.encode("utf-8"))
            # ~ ).decode("utf-8")

            # --- Insert into database ---
            conn = sqlite3.connect(JIG_DB_FILE)
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS ampl_btndisp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sr_number CHAR(17) NOT NULL,
                    filename CHAR(50) NOT NULL,
                    graph TEXT,
                    data_send TEXT,
                    result INTEGER,
                    dips TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')

            cur.execute(
                '''INSERT OR IGNORE INTO ampl_btndisp
                (sr_number, filename, graph, data_send, result, dips)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (serial_no, imagename, graph, "no", result, dips_str)
            )

            conn.commit()
            conn.close()
            print(f"✅ Saved graph for {serial_no}")
            return True

        except Exception as e:
            print(f"❌ Error in save_graph(): {e}")
            return False



    def send_data_to_server(self):
        """Upload pending graphs using TTNEW's MySQL table and payload."""
        mysql_conn = None
        mysql_cur = None
        try:
            with sqlite3.connect(JIG_DB_FILE) as local:
                rows = local.execute("""
                    SELECT sr_number, filename, graph, result, dips, date, id
                    FROM ampl_btndisp
                    WHERE COALESCE(LOWER(TRIM(data_send)), '') != 'yes'
                    ORDER BY id
                """).fetchall()
                if not rows:
                    return True
                mysql_conn = get_mysql_conn()
                mysql_cur = mysql_conn.cursor()
                for row in rows:
                    mysql_cur.execute("""
                        INSERT INTO sub_button_displacement_data
                        (sr_number, filename, graph, result, date)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (row[0], row[1], row[2], row[3], row[5]))
                    mysql_conn.commit()
                    local.execute(
                        "UPDATE ampl_btndisp SET data_send='yes' WHERE id=?", (row[6],))
                    local.commit()
            print(f"✅ Uploaded {len(rows)} records to MySQL")
            return True
        except Exception as exc:
            print(f"❌ Error uploading SQL data: {exc}. Unsent rows remain queued.")
            return False
        finally:
            for resource in (mysql_cur, mysql_conn):
                if resource is not None:
                    try:
                        resource.close()
                    except Exception:
                        pass

    def pause_jobcard(self, checked=False):
        try:
            job_card = self.job_card_id
            print(job_card)
            qty = get_pass_count(self.employee_id, job_card)

            if qty < 0:
                QtWidgets.QMessageBox.warning(None, "Invalid", "Quantity must be greater than 0.")
                return

            url = f"{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card}"
            HEADERS = {
                "Authorization": f"token {API_KEY}:{API_SECRET}",
                "Content-Type": "application/json",
            }

            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                QtWidgets.QMessageBox.warning(None, "Error", "Job Card not found.")
                return

            job_data = response.json().get("data", {})
            time_logs = job_data.get("time_logs", [])

            if not time_logs:
                QtWidgets.QMessageBox.warning(None, "Error", "No time logs to pause.")
                return

            time_logs[-1]["to_time"] = datetime.datetime.now().isoformat()
            time_logs[-1]["completed_qty"] = qty

            payload = {"time_logs": time_logs}
            response = requests.put(url, headers=HEADERS, json=payload)

            if response.status_code == 200:
                QtWidgets.QMessageBox.information(None, "Paused", "✅ Job paused and quantity saved.")
                # clear_pass_count(self.employee_id, job_card)
                # self.jobcard_count = 0
                self.lineEdit_3.setDisabled(True)
            else:
                   QtWidgets.QMessageBox.critical(None, "Error", f"❌ Error: {response.text}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Exception", str(e))


    def resume_jobcard(self, checked=False):
            try:
                job_card = self.job_card_id
                employee_id = self.employee_id

                url = f"{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card}"
                response = requests.get(url, headers=HEADERS)
                if response.status_code != 200:
                    QtWidgets.QMessageBox.warning(None, "Error", "Job Card not found.")
                    return

                job_data = response.json().get("data", {})
                time_logs = job_data.get("time_logs", [])

                last_to_time = time_logs[-1].get("to_time") if time_logs else None
                if not last_to_time:
                    QtWidgets.QMessageBox.warning(None, "Error", "No paused time log found.")
                    return

                new_log = {
                    "from_time": last_to_time,
                    "employee": employee_id,
                    "completed_qty": 0
                }
                time_logs.append(new_log)

                payload = {"time_logs": time_logs}
                response = requests.put(url, headers=HEADERS, json=payload)

                if response.status_code == 200:
                    QtWidgets.QMessageBox.information(None, "Resumed", "▶️ Resumed successfully.")
                    clear_pass_count(employee_id, job_card)  # ✅ Clear JSON
                    self.jobcard_count = 0  
                    self.lineEdit_3.setDisabled(False)

                else:
                    QtWidgets.QMessageBox.critical(None, "Error", f"❌ {response.text}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Exception", str(e))



    def submit_jobcard(self):
            try:
                job_card = self.job_card_id
                completed_qty = get_pass_count(self.employee_id,job_card)# The qty to set in the last time log

                if not job_card or completed_qty < 0:
                    QtWidgets.QMessageBox.warning(None, "Invalid", "❌ Invalid Job Card or quantity.")
                    return

                # Step 1: Fetch job card
                url = f"{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card}"
                response = requests.get(url, headers=HEADERS)
                if response.status_code != 200:
                    QtWidgets.QMessageBox.critical(None, "Error", "❌ Job Card not found.")
                    return

                job_data = response.json().get("data", {})
                time_logs = job_data.get("time_logs", [])
                if not time_logs:
                    QtWidgets.QMessageBox.warning(None, "Error", "❌ No active time log found.")
                    return

                # Step 2: Update last time log's completed_qty to current count (replace)
                time_logs[-1]["completed_qty"] = completed_qty
                time_logs[-1]["to_time"] =datetime.now().isoformat()

                # Step 3: Calculate total completed quantity (sum all time logs completed_qty)
                total_qty = sum(float(log.get("completed_qty", 0)) for log in time_logs)

                # Step 4: Update for_quantity to total_qty
                update_payload = {
                    "for_quantity": total_qty,
                    "time_logs": time_logs
                }

                # Step 5: Update job card in ERPNext
                update_response = requests.put(url, headers=HEADERS, json=update_payload)
                if update_response.status_code != 200:
                    QtWidgets.QMessageBox.critical(None, "Error", "❌ Failed to update time log.")
                    return

                # Step 6: Verify updated job card
                verify_response = requests.get(url, headers=HEADERS)
                if verify_response.status_code != 200:
                    QtWidgets.QMessageBox.critical(None, "Error", "❌ Failed to verify updated Job Card.")
                    return

                updated_data = verify_response.json().get("data", {})
                for_qty = float(updated_data.get("for_quantity", 0))
                total_completed_qty = float(updated_data.get("total_completed_qty", 0))

                # Check for consistency
                if for_qty != total_completed_qty:
                    QtWidgets.QMessageBox.warning(None, "Mismatch",
                        f"❌ Cannot submit. for_quantity ({for_qty}) ≠ total_completed_qty ({total_completed_qty})")
                    return

                # Step 7: Submit job card
                submit_url = f"{ERP_JOB_CARD_URL}/api/resource/Job Card/{job_card}?run_method=submit"
                submit_response = requests.post(submit_url, headers=HEADERS)

                if submit_response.status_code == 200:
                    QtWidgets.QMessageBox.information(None, "Submitted", "✅ Job Card submitted successfully!")
                    clear_pass_count(self.employee_id, job_card)  # ✅ Clear file count
                    self.jobcard_count = 0 
                    self.lineEdit_3.setDisabled(True)


                    self.new_window = EmployeeEntry()
                    self.new_window.show()
                    self.close()
        # Reset count after submit if needed
                else:
                    QtWidgets.QMessageBox.critical(None, "Submit Failed", f"❌ {submit_response.text}")

            except Exception as e:
                QtWidgets.QMessageBox.critical(None, "Exception", str(e))


if __name__ == '__main__':
        init_db()
        app = QApplication(sys.argv)
        window = EmployeeEntry()
        window.show()
        # a=check_serial("BU5SYG")
        # print("aa",a)
    # time.sleep(3)
    # while True:
    #         print("HAI")
    #     else:
    #         time.sleep(60)
    # db_process.start()
    # Ui_MainWindow.send_gcode("$H")
        sys.exit(app.exec_()) 
