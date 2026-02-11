import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, 
                             QFrame, QHeaderView)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor
from widget import Widgets

# --- [1. SettingPanel: 상단 설정 UI] ---
class SettingPanel(QFrame):
    def __init__(self, main_window): 
        super().__init__()
        self.main_window = main_window 
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self)
        
        self.port_combo = self._create_combo(["COM1", "COM2", "COM3"], layout, "Port:")
        self.baud_combo = self._create_combo(["9600", "115200"], layout, "Baud:")
        self.mode_combo = self._create_combo(["RS422", "RS232"], layout, "Mode:")

        layout.addStretch()

        self.conn_btn = QPushButton("Connect Device")
        self.conn_btn.setStyleSheet("""
            QPushButton { background-color: #28a745; color: white; font-weight: bold; padding: 8px 15px; border-radius: 4px; }
            QPushButton:hover { background-color: #218838; }
        """)
        # 메인 윈도우의 함수를 직접 호출
        self.conn_btn.clicked.connect(self.handle_connect)
        layout.addWidget(self.conn_btn)

    def _create_combo(self, items, layout, label_text):
        layout.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItems(items)
        layout.addWidget(combo)
        return combo

    def handle_connect(self):
        port = self.port_combo.currentText()
        baud = self.baud_combo.currentText()
        mode = self.mode_combo.currentText()
        # 메인 윈도우에 정의된 연결 로직 실행
        self.main_window.connect_device(port, baud, mode)

# --- [2. DataPanel: 우측 상단 데이터 테이블] ---
class DataPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        title = QLabel("Telemetry Real-time Data")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        self.table = QTableWidget(6, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Status", "Val 1", "Val 2"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

# --- [3. LogPanel: 우측 하단 로그 뷰어] ---
class LogPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("System Logs"))
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("font-family: 'Consolas'; background-color: #f8f9fa;")
        layout.addWidget(self.log_viewer)

    def write_log(self, text):
        time = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.log_viewer.append(f"[{time}] {text}")

# --- [4. MainPanel: 통합 관리 메인 윈도우] ---
class MainPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced RS422 Controller")
        self.resize(1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # UI 패널들 생성 (자기 자신(self)을 인자로 전달하여 연결)
        self.log_panel = LogPanel()
        self.setting_panel = SettingPanel(self) # 메인 윈도우 전달
        self.data_panel = DataPanel()
        self.image_panel = Widgets()
        
        # 레이아웃 배치
        main_layout.addWidget(self.setting_panel)

        mid_layout = QGridLayout()
        mid_layout.addWidget(self.image_panel, 0, 0, 2, 1)
        mid_layout.addWidget(self.data_panel, 0, 1)
        mid_layout.addWidget(self.log_panel, 1, 1)
        
        mid_layout.setColumnStretch(0, 2)
        mid_layout.setColumnStretch(1, 1)
        main_layout.addLayout(mid_layout)

        # 초기 로그
        self.log("프로그램이 시작되었습니다.")

    # 로그 
    def log(self, text):
        self.log_panel.write_log(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainPanel()
    window.show()
    sys.exit(app.exec())