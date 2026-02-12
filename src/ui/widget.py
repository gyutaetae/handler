from PyQt6.QtWidgets import QWidget, QPainter, QPen, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class create_button:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.show_img = True
        self.radius = 30
        self.is_on = False
        
        # 1~5번 버튼: fire, palm, laser, lock, ets (빨간색 점 + 동그라미)
        self.red_dot_buttons = ["fire", "palm", "laser", "lock", "ets"]
        # 6~12번 버튼: override, fire_enable, camera, shoot_mode, cursor, load, auto_tracking (동그라미만)
        self.circle_only_buttons = ["override", "fire_enable", "camera", "shoot_mode", "cursor", "load", "auto_tracking"]
        self.buttons_position = {
            "fire": (300, 304),
            "palm": (359, 268),
            "laser": (416, 235),
            "lock": (374, 328),
            "ets": (424, 376),
            "override": (489, 300),
            "fire_enable": (636, 241),
        }
        self.buttons_position = {
            "camera": (724, 202),
            "shoot_mode": (724, 202),
            "cursor": (802, 153),
            "load": (690, 346),
            "auto_tracking": (690, 346),
            "control_mode": (757, 310),
            "zoom": (815, 240),
            "modify_dist": (815, 240)
        }

    def draw_indicators(self):
        """모든 버튼 데이터를 순회하며 캔버스에 그리기"""
        canvas = self.base_pixmap.copy()
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for btn in self.buttons:
            if not btn['is_on']:
                continue

            # 1. 빨간 점 그리기 (옵션)
            if btn['show_img']:
                painter.drawPixmap(btn['x'] - 25, btn['y'] - 25, 50, 50, self.red_indicator)
            
            # 2. 빨간 테두리 그리기 (공통)
            painter.setPen(QPen(QColor(255, 0, 0), 6))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(btn['x'] - 25, btn['y'] - 25, 50, 50)

        painter.end()
        
        # 화면에 맞게 출력
        scaled = canvas.scaled(self.img_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.img_label.setPixmap(scaled)
    
    def resizeEvent(self, event):
        self.draw_indicators()