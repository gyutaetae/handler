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
# ... (상단 임포트 동일)

class ClickableImagePanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setMouseTracking(True)
        
        # 1. 원본 이미지 로드 및 기준 크기 저장
        self.base_pixmap = QPixmap("image/handle_image.png")
        if self.base_pixmap.isNull():
            self.img_label.setText("Image Not Found")
            # 테스트를 위해 빈 이미지 생성 (파일 없을 때 대비)
            self.base_pixmap = QPixmap(1000, 1000)
            self.base_pixmap.fill(QColor("#2c2c2c"))

        # 버튼 상태 관리 (1~11번)
        self.button_states = {i: False for i in range(1, 13)}
        
        # 버튼 중심 좌표 (원본 이미지 픽셀 기준)
        self.indicator_positions = [
            {"x": 298, "y": 306, "button": 1},
            {"x": 356, "y": 268, "button": 2},
            {"x": 416, "y": 233, "button": 3},
            {"x": 374, "y": 328, "button": 4},
            {"x": 421, "y": 376, "button": 5},
            {"x": 489, "y": 300, "button": 6},
            {"x": 636, "y": 241, "button": 7},
            {"x": 748, "y": 206, "button": 8},
            {"x": 802, "y": 153, "button": 9},
            {"x": 690, "y": 346, "button": 10},
            {"x": 757, "y": 310, "button": 11},
            {"x": 815, "y": 240, "button": 12}
        ]
        
        self.img_label.mousePressEvent = self.on_image_clicked
        layout.addWidget(self.img_label)
        
        # 최초 실행 시 그리기
        self.draw_indicators()

    def resizeEvent(self, event):
        """창 크기가 바뀔 때마다 이미지 다시 스케일링"""
        super().resizeEvent(event)
        self.draw_indicators()

    def get_pixmap_rect(self):
        """Label 안에서 실제로 이미지가 차지하고 있는 영역 계산"""
        if not self.img_label.pixmap(): return self.rect()
        
        label_size = self.img_label.size()
        pix_size = self.img_label.pixmap().size()
        
        # 중앙 정렬이므로 여백 계산
        x_offset = (label_size.width() - pix_size.width()) // 2
        y_offset = (label_size.height() - pix_size.height()) // 2
        
        return x_offset, y_offset, pix_size.width(), pix_size.height()

    def on_image_clicked(self, event: QMouseEvent):
        """화면 클릭 좌표를 원본 이미지 좌표로 변환하여 판정"""
        x_off, y_off, p_w, p_h = self.get_pixmap_rect()
        
        # 1. 클릭 위치가 실제 이미지 내부인지 확인
        click_x = event.pos().x() - x_off
        click_y = event.pos().y() - y_off
        
        if 0 <= click_x <= p_w and 0 <= click_y <= p_h:
            # 2. 클릭한 위치를 원본 이미지 픽셀 비율로 환산
            orig_x = int(click_x * (self.base_pixmap.width() / p_w))
            orig_y = int(click_y * (self.base_pixmap.height() / p_h))
            
            print(f"Original Image Pixel: {orig_x}, {orig_y}")
            
            # 3. 버튼 판정 (원본 좌표 기준 근접도 확인)
            for pos in self.indicator_positions:
                dist = ((pos["x"] - orig_x)**2 + (pos["y"] - orig_y)**2)**0.5
                if dist < 40: # 40픽셀 이내면 클릭으로 인정
                    self.toggle_button(pos["button"])
                    break

    def draw_indicators(self):
        """원본 이미지에 먼저 그리고, 화면 크기에 맞춰 출력"""
        from PyQt6.QtGui import QPainter, QPen
        
        # 원본 복사본 생성 (원본 유지)
        temp_pixmap = self.base_pixmap.copy()
        painter = QPainter(temp_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 빨간색 테두리 설정
        pen = QPen(QColor(255, 0, 0), 6) # 선 굵기도 크게 (원본이 크니까)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # ON 상태인 버튼에 동그라미 그리기 (원본 픽셀 좌표 사용)
        for pos in self.indicator_positions:
            if self.button_states[pos["button"]]:
                radius = 25
                painter.drawEllipse(pos["x"] - radius, pos["y"] - radius, radius * 2, radius * 2)
        
        painter.end()
        
        # 화면(Label) 크기에 맞춰 스케일링
        scaled_pixmap = temp_pixmap.scaled(
            self.img_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.img_label.setPixmap(scaled_pixmap)

    def toggle_button(self, btn_num):
        self.button_states[btn_num] = not self.button_states[btn_num]
        print(f"Button {btn_num} is {'ON' if self.button_states[btn_num] else 'OFF'}")
        self.draw_indicators()

    def set_button_state(self, button_number, state):
        """외부에서 버튼 상태 설정"""
        if button_number in self.button_states:
            self.button_states[button_number] = state
            self.draw_indicators()
    
    def get_button_state(self, button_number):
        """버튼 상태 조회"""
        return self.button_states.get(button_number, False)
    
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
