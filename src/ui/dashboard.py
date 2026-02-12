import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, 
                             QFrame, QHeaderView)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QColor, QPixmap
from widget import create_button

# --- [1. MainPanel: 통합 관리 메인 윈도우] ---
class MainPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced RS422 Controller")
        self.resize(1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

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
        self.log("Program started.")

     # 로그 
    def log(self, text):
        self.log_panel.write_log(text)

    def connect_device(self, port, baud, mode):
        self.log(f"Port: {port}, Baud: {baud}, Mode: {mode} connected.")
        
# --- [2. SettingPanel: 상단 설정 UI] ---
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


# --- [3. ImagePanel: 좌측 이미지 패널] ---
class ImagePanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.img_label)
        self.base_pixmap = QPixmap("image/cch_front.png")
        if self.base_pixmap.isNull():
            self.base_pixmap = QPixmap(900, 900)
            self.base_pixmap.fill(QColor("#2c2c2c"))
        self.img_label.setPixmap(self.base_pixmap)
        
# --- [4. DataPanel: 우측 상단 데이터 테이블] ---
class DataPanel(QFrame):
    # data: map(string, line)
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        title=QLable("Telemetry Real-time Data")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        self.data_table = QTableWidget()
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["Name", "Value"])
        
        layout.addWidget(self.data_table)
        self.data_map = {}
        
    def update_data_line(self, name, value):
        if name in self.data_map:
            row_idx = self.data_map[name]
            self.data_table.setItem(row_idx, 1, QTableWidgetItem(str(value)))
        else:
            # 새로운 항목 추가
            row_idx = self.data_table.rowCount()
            self.data_table.insertRow(row_idx)
            self.data_map[name] = row_idx
            self.data_table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.data_table.setItem(row_idx, 1, QTableWidgetItem(str(value)))

# --- [5. LogPanel: 우측 하단 로그 뷰어] ---
class LogPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("System Logs"))
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("font-family: 'Consolas';")
        layout.addWidget(self.log_viewer)

    def write_log(self, text):
        time = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
        self.log_viewer.append(f"[{time}] {text}")

# --- [6. control panel: 우측 하단 제어 패널] ---
class ControlPanel(QFrame):
    #clear log, expert log 버튼 추가 
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self)
        self.clear_log_btn = QPushButton("Clear Log")
        self.expert_log_btn = QPushButton("Export Log")
        layout.addWidget(self.clear_log_btn)
        layout.addWidget(self.expert_log_btn)
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainPanel()
    window.show()
    sys.exit(app.exec())