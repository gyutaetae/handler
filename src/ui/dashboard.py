import os
import sys
import random
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, 
                             QFrame, QHeaderView)
from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt, QDateTime, QSize
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
        super().__init__(parent)
        self.parent = parent
        self.parent.update_button.connect(self._update)
        self.setStyleSheet("""
            ImagePanel {
                background-color: #4a5a7b;
            }
        """)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.IMAGE_PATH = os.path.join(BASE_DIR, "images")
        background_front = os.path.join(self.IMAGE_PATH, "front.png")
        background_back = os.path.join(self.IMAGE_PATH, "back.png")
        
        self.front_images = ['laser', 'lock_on', 'move_enable', 'override', 
                             'fire_enable', 'camera','shoot_mode','cursor',
                             'load','auto_tracking','control_mode','zoom',
                             'modify_dist','fcc','rcms']
        self.back_images = ['fire', 'palm']

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.front = ImageSubPanel(background_front, self.front_images)
        self.back = ImageSubPanel(background_back, self.back_images)

        self.base_width = self.front.orig_w
        self.front.set_fixed_scale(self.base_width)
        self.back.set_fixed_scale(self.base_width)

        self.main_layout.addWidget(self.front, stretch=1)
        # self.main_layout.addSpacing(50)
        self.main_layout.addWidget(self.back, stretch=1)

    def _update(self, signals):
        def check_state(status):
            if status == "ON":
                return True
            elif status == "OFF":
                return False

            if status == "00":
                return False
            elif status == "01":
                return True
            elif status == "10":
                return True
        # print(signals)
        # 전면부에서 찾기
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        for name, status in signals.items():
            if name == 'ets': name = 'move_enable'
            if name in self.back_images:
                self.back.layers[name]["label"].setVisible(check_state(status))
            else:
                self.front.layers[name]["label"].setVisible(check_state(status))
                if name == "control_mode":
                    if status == "00":
                        self.front.layers["fcc"]["label"].setVisible(check_state(status))
                        self.front.layers["rcms"]["label"].setVisible(check_state(status))
                    elif status == "10":
                        self.front.layers["fcc"]["label"].setVisible(check_state(status))
                        self.front.layers["rcms"]["label"].setVisible(False)
                    elif status == "01":
                        self.front.layers["rcms"]["label"].setVisible(check_state(status))
                        self.front.layers["fcc"]["label"].setVisible(False)

class ImageSubPanel(QFrame):
    def __init__(self, background_image, btn_images, parent=None):
        super().__init__(parent)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.IMAGE_PATH = os.path.join(BASE_DIR, "images")
        self.layers = {}

        self.bg_pixmap = QPixmap(background_image)
        self.orig_w = self.bg_pixmap.width()
        self.orig_h = self.bg_pixmap.height()

        self.bg_label = QLabel(self)
        self.bg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for btn_name in btn_images:
            btn_file = os.path.join(self.IMAGE_PATH, btn_name+".png")
            layer = QLabel(self)
            pix = QPixmap(btn_file)
            layer.setPixmap(pix)
            layer.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layer.hide() # 초기 상태 숨김
            # 파일명을 ID로 사용
            self.layers[btn_name] = {"label": layer, "pixmap": pix}
    
    def set_fixed_scale(self, target_width):
        """외부에서 지정한 가로폭에 맞춰 이미지를 고정 스케일링"""
        # 지정된 너비에 맞춰 배경 이미지 크기 조정
        scaled_bg = self.bg_pixmap.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
        self.bg_label.setPixmap(scaled_bg)
        
        # 패널 자체의 크기를 실제 이미지 크기에 딱 맞게 고정 (무한 확장 방지)
        new_h = scaled_bg.height()
        self.setFixedSize(target_width, new_h)

        # 강조 레이어들도 동일한 크기로 고정
        for item in self.layers.values():
            lbl, pix = item["label"], item["pixmap"]
            lbl.setPixmap(pix.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation))
            lbl.setFixedSize(target_width, new_h)

    def resizeEvent(self, event):
        """창 크기 변경 시 배경과 모든 레이어 동기화"""
        curr_size = self.size()

        self.bg_label.resize(curr_size)
        if not self.bg_pixmap.isNull():
            self.bg_label.setPixmap(self.bg_pixmap.scaled(
                curr_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))

        for item in self.layers.values():
            lbl, pix = item["label"], item["pixmap"]
            lbl.resize(curr_size)
            lbl.setPixmap(pix.scaled(
                curr_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        super().resizeEvent(event)

 
# --- [Data Panel: 우측 중간 상단 표] ---
class DataPanel(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.parent.update_inspection.connect(self.update_inspection)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.inspection_list = [line.strip() for line in open(os.path.join(BASE_DIR, "..", "inspection_config.txt"), 'r', encoding='utf-8').readlines()]
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
        mid_layout.addWidget(self.data_panel, 0, 1) # 우측 상단
        mid_layout.setColumnStretch(0, 1)
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