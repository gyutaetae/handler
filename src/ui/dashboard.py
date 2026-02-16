import sys
import random
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, 
                             QFrame, QHeaderView)
from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt, QDateTime
from PyQt6.QtGui import QPixmap, QColor, QFont, QMouseEvent
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
        self.parent.update_button.connect(self.update)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.widgets = Widgets()
        self.button_map = {}

        self.make_buttons()
        layout = self.construct()

    def construct(self):        
        # 이미지 로드
        pixmap = QPixmap("image/handle_image.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio, 
                                         Qt.TransformationMode.SmoothTransformation)
            # self.img_label.setPixmap(scaled_pixmap)
        # else:
        #     self.img_label.setText("Handle Image Not Found")
        #     self.img_label.setStyleSheet("color: #888; font-size: 14px;")
            
        # layout.addWidget(self.img_label)
        # for button in self.button_map.values():
        #     layout.addWidget(button)

    def make_buttons(self):
        positions = [(550,404),(359,568),(616,735),(300,304),(359,268),(416,235),(374,328),(424,376),(489,300),(636,241),(724,202),(802,153),(690,346),(757,310),(815,240)]
        keys = ["fire", "palm", "laser", "lock", "ets", "override", "fire_enable", "camera", "shoot_mode", "cursor", "load", "auto_tracking", "control_mode", "zoom", "modify_dist"]
        for name, position in zip(keys, positions):
            self.button_map[name] = self.widgets.create_button(name, position, self)

    def update(self, signals):
        for name, value in signals.items():
            self.button_map[name].update_data(value)

# --- [Data Panel: 우측 중간 상단 표] ---
class DataPanel(QFrame):
    def __init__(self, parent):
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
# class LogPanel(QFrame):
#     def __init__(self, parent):
#         super().__init__()
#         self.setFrameStyle(QFrame.Shape.StyledPanel)
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(5, 5, 5, 5)
        
#         title_label = QLabel("Data Log")
#         title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
#         layout.addWidget(title_label)
        
#         self.log_viewer = QTextEdit()
#         self.log_viewer.setReadOnly(True)
#         self.log_viewer.setStyleSheet("""
#             QTextEdit {
#                 font-family: 'Consolas', 'Courier New', monospace;
#                 font-size: 14px;
#                 padding: 5px;
#             }
#         """)
#         layout.addWidget(self.log_viewer)
        
#         # 초기 로그 메시지
#         self.append_log("System initialized")

#     def append_log(self, text):
#         """로그 추가"""
#         timestamp = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
#         self.log_viewer.append(f"[{timestamp}] {text}")
    
#     def clear_log(self):
#         """로그 지우기"""
#         self.log_viewer.clear()


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

        print(len(self.graph_map))
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
        print("In GUI: ", button_signals)
        self.update_button.emit(button_signals)

    def _update_graph(self, graph_signals):
        print("In GUI: ", graph_signals)
        self.update_graph.emit(graph_signals)