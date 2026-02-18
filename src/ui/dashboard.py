import sys
import random
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, 
                             QFrame, QHeaderView)
from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt, QDateTime
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont, QMouseEvent
from ui.widgets import Widgets

# --- [Setting Panel: 상단 설정] ---
class SettingPanel(QFrame):
    def __init__(self, parent):
        super().__init__()
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


# --- [Image Panel: 왼쪽 중간 이미지] ---
class ImagePanel(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.parent.update_button.connect(self._update)
        self.front_pixmap = QPixmap("src/ui/images/front.png")
        self.back_pixmap = QPixmap("src/ui/images/back.png")
        self.spacing = 50  # 두 이미지 사이의 간격 (픽셀)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.widgets = Widgets()
        self.button_map = {}

        self.make_buttons()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#c0c0c0"))
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 1. 첫 번째 이미지(Front) 스케일링 기준 계산
        # 두 이미지가 나란히 들어가야 하므로 전체 너비의 절반(간격 제외)을 최대치로 설정
        max_w = (self.width() - self.spacing) // 2
        max_h = self.height()

        # Front 이미지 스케일링 (비율 유지)
        scaled_front = self.front_pixmap.scaled(
            max_w, max_h, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )

        # 2. 두 번째 이미지(Back) 스케일링
        # 너비를 'scaled_front.width()'와 동일하게 강제 고정
        # 이때 세로 비율도 깨지지 않게 하려면 IgnoreAspectRatio 대신 KeepAspectRatio를 쓰되 
        # 기준 너비를 고정값으로 넘깁니다.
        scaled_back = self.back_pixmap.scaledToWidth(
            scaled_front.width(), 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # 만약 scaled_back의 높이가 창 높이보다 커질 경우를 대비한 예외 처리 (선택 사항)
        if scaled_back.height() > max_h:
            scaled_back = scaled_back.scaledToHeight(max_h, Qt.TransformationMode.SmoothTransformation)
            # 이 경우 다시 front의 너비가 틀어질 수 있으므로, 
            # 엄격하게 동일 가로 크기를 원하시면 위 코드만 사용하세요.

        # 3. 레이아웃 계산 (중앙 정렬)
        total_w = scaled_front.width() + self.spacing + scaled_back.width()
        start_x = (self.width() - total_w) // 2

        # 4. 그리기
        front_y = (self.height() - scaled_front.height()) // 2
        painter.drawPixmap(start_x, front_y, scaled_front)

        back_x = start_x + scaled_front.width() + self.spacing
        back_y = (self.height() - scaled_back.height()) // 2
        painter.drawPixmap(back_x, back_y, scaled_back)

    def make_buttons(self):
        positions = [(550,404),(359,568),(616,735),(300,304),(359,268),(416,235),(374,328),(424,376),(489,300),(636,241),(724,202),(802,153),(690,346),(757,310),(815,240)]
        keys = ["fire", "palm", "laser", "lock_on", "ets", "override", "fire_enable", "camera", "shoot_mode", "cursor", "load", "auto_tracking", "control_mode", "zoom", "modify_dist"]
        for name, position in zip(keys, positions):
            self.button_map[name] = self.widgets.create_button(name, position, self)

    def _update(self, signals):
        for name, value in signals.items():
            self.button_map[name].update_data(value)

# --- [Data Panel: 우측 중간 상단 표] ---
class DataPanel(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.parent.update_inspection.connect(self.update_inspection)
        self.inspection_list = [
            "버튼 동작 없음 (표적지정 ON)",
            "버튼 동작 없음 (표적지정 OFF)",
            "버튼 동작 없음 (격발)",
            "버튼 동작 없음 (레이저)",
            "스위치 동작 없음 (발사모드 단발)",
            "스위치 동작 없음 (발사모드 점사)",
            "스위치 동작 없음 (발사모드 연사)",
            "FOV 상방향",
            "FOV 하방향",
            "팜 스위치",
            "팜 스위치 + 표적지정 (ON)",
            "팜 스위치 + 표적지정 (OFF)",
            "팜 스위치 + 격발",
            "팜 스위치 + 레이저",
            "팜 스위치 + 발사모드 단발",
            "팜 스위치 + 발사모드 점사",
            "팜 스위치 + 발사모드 연사",
            "팜 스위치 + 거리 수정 상방향",
            "팜 스위치 + 거리 수정 하방향",
            "카메라 선택 스위치 (idle)",
            "카메라 선택 스위치 (cam1)",
            "카메라 선택 스위치 (cam2)",
            "Fire Enable 스위치 ON",
            "Fire Enable 스위치 OFF",
            "Override 스위치 ON",
            "Override 스위치 OFF",
            "Move Enable 스위치 ON",
            "Move Enable 스위치 OFF",
            "연동전환 스위치 RCWS",
            "연동전환 스위치 사통",
            "커서 위",
            "커서 아래",
            "커서 좌",
            "커서 우",
            "모드전환 / 장전 스위치"
        ]
        self.widgets = Widgets()
        self.construct()

    def construct(self):
        def init_table():
            self.table.init(self.inspection_list)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        top_panel = QGridLayout()
        title_label = QLabel("Inspection")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        top_panel.addWidget(title_label, 0, 0)

        button = QPushButton("초기화")
        button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color : white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
                border: none;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        button.clicked.connect(init_table)
        top_panel.addWidget(button, 0, 2)
        
        top_panel.setColumnStretch(1, 1)
        top_panel.setColumnStretch(0, 0)
        top_panel.setColumnStretch(2, 0)

        layout.addLayout(top_panel)

        self.table = self.widgets.create_table(len(self.inspection_list), 2)
        self.table.init(self.inspection_list)
        layout.addWidget(self.table)

    def update_inspection(self, signals):
        for id, values in signals.items():
            _, status_change = values
            self.table.update_line(id, status_change)

# --- [Control Panel: 하단 버튼] ---
class ControlPanel(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.parent.update_graph.connect(self.update)
        self.widgets = Widgets()
        self.graph_map = {}
        self.make_graph_map()
        self.construct()

    def construct(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addStretch()

        # print(len(self.graph_map))
        for graph in self.graph_map.values():
            layout.addWidget(graph, stretch=1)

    def make_graph_map(self):
        names = ["height", "turning", "x_axis", "y_axis"]
        for name in names:
            self.graph_map[name] = self.widgets.create_graph(name, self)

    def update(self, signals):
        for name, value in signals.items():
            self.graph_map[name].update_data(value)


# --- [Main Panel: 메인 윈도우] ---
class MainPanel(QMainWindow):
    update_button = pyqtSignal(dict)
    update_graph = pyqtSignal(dict)
    update_inspection = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setting_panel = SettingPanel(self)
        self.image_panel = ImagePanel(self)
        self.data_panel = DataPanel(self)
        # self.log_panel = LogPanel(self)
        self.control_panel = ControlPanel(self)
        self.construct()

    def construct(self):
        self.setWindowTitle("RS422 Data Monitor")
        self.resize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        middle_layout = self.set_middle_layout()
        main_layout.addWidget(self.setting_panel)
        main_layout.addLayout(middle_layout, 2)
        main_layout.addWidget(self.control_panel, 1)
    
    def set_middle_layout(self):
        mid_layout = QGridLayout()
        mid_layout.setSpacing(10)

        mid_layout.addWidget(self.image_panel, 0, 0)  # 왼쪽 (2행 차지)
        mid_layout.addWidget(self.data_panel, 0, 1)                    # 우측 상단
        mid_layout.setColumnStretch(0, 2)
        mid_layout.setColumnStretch(1, 1)
        return mid_layout

    def _update_button(self, button_signals):
        # print("In GUI: ", button_signals)
        self.update_button.emit(button_signals)

    def _update_graph(self, graph_signals):
        # print("In GUI: ", graph_signals)
        self.update_graph.emit(graph_signals)

    def _update_inspection(self, inspection_signals):
        # print("In GUI: ", inspection_signals)
        self.update_inspection.emit(inspection_signals)