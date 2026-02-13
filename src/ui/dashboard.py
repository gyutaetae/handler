import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, 
                             QFrame, QHeaderView)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor
from widget import Widgets as ImagePanel

# --- [1. SettingPanel: 장치 연결 및 통신 설정] ---
class SettingPanel(QFrame):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self)

        # 콤보박스 설정
        self.port_combo = self._create_combo(["COM1", "COM2", "COM3"], layout, "Port:")
        self.baud_combo = self._create_combo(["9600", "115200"], layout, "Baud:")
        self.mode_combo = self._create_combo(["RS422", "RS232"], layout, "Mode:")
        layout.addStretch()

        # Connect 버튼
        self.conn_btn = QPushButton("Connect")
        self.conn_btn.setStyleSheet(
            "QPushButton { background-color: #28a745; color: white; font-weight: bold; "
            "padding: 8px 15px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #218838; }"
        )
        self.conn_btn.clicked.connect(self.handle_connect)
        layout.addWidget(self.conn_btn)

    def _create_combo(self, items, layout, label_text):
        layout.addWidget(QLabel(label_text))
        combo = QComboBox()
        combo.addItems(items)
        layout.addWidget(combo)
        return combo

    def handle_connect(self):
        port, baud, mode = self.port_combo.currentText(), self.baud_combo.currentText(), self.mode_combo.currentText()
        self.main_window.connect_device(port, baud, mode)

# --- [2. DataPanel: 동적 데이터 매핑 테이블] ---
class DataPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)

        title = QLabel("Parsed Data")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        self.data_table = QTableWidget(6, 6)
        self.data_table.setHorizontalHeaderLabels(["ID", "ID","Type","Statue","Value1","Value2"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.data_table)

        self.data_map = {}  # {name: row_index}

    def update_data_line(self, name, value):
        """데이터를 테이블에 매핑하여 업데이트 또는 신규 추가"""
        if name in self.data_map:
            row_idx = self.data_map[name]
            self.data_table.setItem(row_idx, 1, QTableWidgetItem(str(value)))
        else:
            row_idx = self.data_table.rowCount()
            self.data_table.insertRow(row_idx)
            self.data_map[name] = row_idx
            self.data_table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.data_table.setItem(row_idx, 1, QTableWidgetItem(str(value)))

# --- [3. LogPanel: 시스템 로그 뷰어] ---
class LogPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Data Log"))
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas';")
        layout.addWidget(self.log_viewer)

    def write_log(self, text):
        time = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
        self.log_viewer.append(f"[{time}] {text}")

# --- [4. ControlPanel: 하단의 clear log, export log 패널] ---
class ControlPanel(QFrame):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self)
        
        self.clear_log_btn = QPushButton("Clear Log")
        self.export_log_btn = QPushButton("Export Log")
        layout.addWidget(self.clear_log_btn)
        layout.addWidget(self.export_log_btn)

# --- [5. MainPanel: 전체 통합 관리] ---
class MainPanel(QMainWindow):   
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RS422 Data Monitor")
        self.resize(1500, 950)

        # 중앙 위젯 및 메인 레이아웃
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 패널 인스턴스화
        self.setting_panel = SettingPanel(self)
        self.image_panel = ImagePanel()
        self.data_panel = DataPanel()
        self.log_panel = LogPanel()
        self.control_panel = ControlPanel(self)

        # 레이아웃 배치
        main_layout.addWidget(self.setting_panel)

        mid_layout = QGridLayout()
        mid_layout.addWidget(self.image_panel, 0, 0, 2, 1)  # 좌측: 이미지 패널
        mid_layout.addWidget(self.data_panel, 0, 1)         # 우측 상단: 데이터 테이블
        mid_layout.addWidget(self.log_panel, 1, 1)          # 우측 중단: 로그 패널
        mid_layout.addWidget(self.control_panel, 2, 1, 1, 1)  # 하단: 제어 패널

        # 비율 설정
        mid_layout.setColumnStretch(0, 3)
        mid_layout.setColumnStretch(1, 1)
        mid_layout.setRowStretch(0, 1)
        mid_layout.setRowStretch(1, 1)
        
        main_layout.addLayout(mid_layout)

        self.log("System Initialized.")
        
        # 테스트용 데이터
        self.data_panel.update_data_line("1", "2")
        self.data_panel.update_data_line("2", "2")

    def log(self, text):
        self.log_panel.write_log(text)

    def connect_device(self, port, baud, mode):
        self.log(f"Attempting connection... Port: {port}, Baud: {baud}")
        self.log(f"Status: Connected to {port} in {mode} mode.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = MainPanel()
    window.show()
    sys.exit(app.exec())