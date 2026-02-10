import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, 
                             QFrame, QHeaderView)
from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt, QDateTime
from PyQt6.QtGui import QPixmap, QColor, QFont, QMouseEvent
import serial  # pyserial


# --- [Controller: 데이터 및 통신 관리] ---
class TelemetryController(QObject):
    log_updated = pyqtSignal(str)
    data_updated = pyqtSignal(list)  # [ID, ID, Type, Status, V1, V2]
    
    def __init__(self):
        super().__init__()
        self.serial_port = None

    def connect_serial(self, port, baud, mode):
        """시리얼 연결"""
        self.log_updated.emit(f"Connected to {port} at {baud} bps (Mode: {mode})")


# --- [Setting Panel: 상단 설정] ---
class SettingPanel(QFrame):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Port
        layout.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(["COM1", "COM2", "COM3"])
        layout.addWidget(self.port_combo)

        # Baud Rate
        layout.addWidget(QLabel("Baud Rate:"))
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "115200"])
        layout.addWidget(self.baud_combo)

        # Mode
        layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["RS422", "RS232"])
        layout.addWidget(self.mode_combo)

        layout.addStretch()

        # Connect 버튼
        self.conn_btn = QPushButton("Connect")
        self.conn_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color : white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.conn_btn.clicked.connect(self.handle_connect)
        layout.addWidget(self.conn_btn)

    def handle_connect(self):
        port = self.port_combo.currentText()
        baud = self.baud_combo.currentText()
        mode = self.mode_combo.currentText()
        self.controller.connect_serial(port, baud, mode)


# --- [Clickable Image Panel: 클릭 가능한 이미지 패널] ---
class ClickableImagePanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setMouseTracking(True)
        
        # 현재 이미지 번호
        self.current_image = 0
        
        # 토글 상태 (4 또는 5)
        self.toggle_state = 4
        
        # 클릭 가능한 영역 정의 (x, y, width, height, button_number)
        # 여기에 실제 좌표를 입력하세요
        self.click_areas = [
            {"x": 147, "y": 159, "w": 80, "h": 80, "button": 1},  # 버튼 1 영역
            {"x": 180, "y": 137, "w": 80, "h": 80, "button": 2},  # 버튼 2 영역
            {"x": 212, "y": 118, "w": 80, "h": 80, "button": 3},  # 버튼 3 영역
            {"x": 201, "y": 239, "w": 80, "h": 80, "button": "toggle"},  # 토글 스위치 (4↔5)
        ]
        
        # 마우스 이벤트 연결
        self.img_label.mousePressEvent = self.on_image_clicked
        
        # 기본 이미지 로드
        self.load_image("image/handle_image.png")
        
        layout.addWidget(self.img_label)
    
    def load_image(self, image_path):
        """이미지 로드"""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio, 
                                         Qt.TransformationMode.SmoothTransformation)
            self.img_label.setPixmap(scaled_pixmap)
        else:
            self.img_label.setText(f"Image Not Found: {image_path}")
            self.img_label.setStyleSheet("color: #888; font-size: 14px;")
    
    def on_image_clicked(self, event: QMouseEvent):
        """이미지 클릭 이벤트"""
        x = event.pos().x()
        y = event.pos().y()
        
        # 클릭 좌표 출력 (개발용)
        print(f"\n[클릭 좌표] x={x}, y={y}")
        print(f'    {{"x": {x}, "y": {y}, "w": 80, "h": 80, "button": ?}},')
        
        # 클릭 영역 확인
        for area in self.click_areas:
            # 넉넉한 클릭 영역 (±10 픽셀)
            margin = 3
            if (area["x"] - margin <= x <= area["x"] + area["w"] + margin and
                area["y"] - margin <= y <= area["y"] + area["h"] + margin):
                
                button_num = area["button"]
                print(f"[버튼 {button_num} 클릭됨!]")
                
                # 토글 버튼 처리
                if button_num == "toggle":
                    self.toggle_switch()
                else:
                    self.switch_image(button_num)
                return
    
    def toggle_switch(self):
        """토글 스위치 (4 ↔ 5)"""
        if self.toggle_state == 4:
            self.toggle_state = 5
        else:
            self.toggle_state = 4
        
        image_path = f"image/{self.toggle_state}.png"
        self.load_image(image_path)
        self.current_image = self.toggle_state
        print(f"[토글 전환] {self.toggle_state}.png로 변경됨")
    
    def switch_image(self, button_number):
        """버튼 번호에 따라 이미지 전환"""
        if button_number in [1, 2, 3]:
            image_path = f"image/{button_number}.png"
            self.load_image(image_path)
            self.current_image = button_number
            print(f"[이미지 전환] {button_number}.png로 변경됨")
    
    def set_image_visible(self, visible):
        """이미지 표시/숨김 제어"""
        self.img_label.setVisible(visible)


# --- [Image Panel: 왼쪽 중간 이미지] ---
class ImagePanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 이미지 로드
        pixmap = QPixmap("image/handle_image.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio, 
                                         Qt.TransformationMode.SmoothTransformation)
            self.img_label.setPixmap(scaled_pixmap)
        else:
            self.img_label.setText("Handle Image Not Found")
            self.img_label.setStyleSheet("color: #888; font-size: 14px;")
            
        layout.addWidget(self.img_label)

    def set_image_visible(self, visible):
        """이미지 표시/숨김 제어"""
        self.img_label.setVisible(visible)


# --- [Data Panel: 우측 중간 상단 표] ---
class DataPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        title_label = QLabel("Parsed Data")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)

        self.table = QTableWidget(6, 6)
        self.table.setHorizontalHeaderLabels(["ID", "ID", "Type", "Status", "Value 1", "Value 2"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # 샘플 데이터 초기화
        self.init_sample_data()
        layout.addWidget(self.table)

    def init_sample_data(self):
        """초기 샘플 데이터 설정"""
        data = [
            ["01", "01", "Command", "OK", str(random.randint(100, 150)), str(random.randint(50, 80))],
            ["02", "02", "Sensor", "Active", f"{random.uniform(30, 35):.1f}", f"{random.uniform(65, 70):.1f}"],
            ["03", "03", "Alarm", "Error", "--", "--"],
            ["04", "04", "Data", "Normal", str(random.randint(70, 85)), str(random.randint(40, 50))],
            ["05", "05", "Status", "Fault", "--", "--"],
            ["06", "06", "Command", "OK", str(random.randint(180, 220)), str(random.randint(90, 110))]
        ]
        
        for row, items in enumerate(data):
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Status 열(3번 열) 색상 처리
                if col == 3:
                    if text in ["OK", "Normal"]:
                        item.setForeground(QColor("#28a745"))  # 초록색
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    elif text == "Active":
                        item.setForeground(QColor("#ffc107"))  # 노란색
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    elif text in ["Error", "Fault"]:
                        item.setForeground(QColor("#dc3545"))  # 빨간색
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                
                self.table.setItem(row, col, item)


# --- [Log Panel: 우측 중간 하단 로그] ---
class LogPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        title_label = QLabel("Data Log")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)
        
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.log_viewer)
        
        # 초기 로그 메시지
        self.append_log("System initialized")

    def append_log(self, text):
        """로그 추가"""
        timestamp = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
        self.log_viewer.append(f"[{timestamp}] {text}")
    
    def clear_log(self):
        """로그 지우기"""
        self.log_viewer.clear()


# --- [Control Panel: 하단 버튼] ---
class ControlPanel(QFrame):
    def __init__(self, log_panel):
        super().__init__()
        self.log_panel = log_panel
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        layout.addStretch()

        # Clear Log 버튼
        clear_btn = QPushButton("Clear Log")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        clear_btn.clicked.connect(self.log_panel.clear_log)
        layout.addWidget(clear_btn)
        
        # Export Log 버튼
        export_btn = QPushButton("Export Log")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
        """)
        layout.addWidget(export_btn)


# --- [Main Panel: 메인 윈도우] ---
class MainPanel(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("RS422 Data Monitor")
        self.resize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 1. 상단 설정 패널
        self.setting_panel = SettingPanel(controller)
        main_layout.addWidget(self.setting_panel)

        # 2. 중간 그리드 (클릭 가능한 이미지 + 데이터 + 로그)
        mid_layout = QGridLayout()
        mid_layout.setSpacing(10)
        
        # ClickableImagePanel 사용
        self.clickable_image_panel = ClickableImagePanel()
        self.data_panel = DataPanel()
        self.log_panel = LogPanel()

        mid_layout.addWidget(self.clickable_image_panel, 0, 0, 2, 1)  # 왼쪽 (2행 차지)
        mid_layout.addWidget(self.data_panel, 0, 1)                    # 우측 상단
        mid_layout.addWidget(self.log_panel, 1, 1)                     # 우측 하단
        mid_layout.setColumnStretch(0, 1)
        mid_layout.setColumnStretch(1, 1)
        main_layout.addLayout(mid_layout)

        # 3. 하단 컨트롤 패널
        self.control_panel = ControlPanel(self.log_panel)
        main_layout.addWidget(self.control_panel)

        # 컨트롤러 시그널 연결
        controller.log_updated.connect(self.log_panel.append_log)

# --- [Entry Point] ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Fusion 스타일 적용
    app.setStyle("Fusion")
    
    controller = TelemetryController()
    window = MainPanel(controller)
    window.show()
    sys.exit(app.exec())
