from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen, QMouseEvent

class Widgets(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 1. 배경 이미지 로드
        self.base_pixmap = QPixmap("image/handle_image.png")
        if self.base_pixmap.isNull():
            self.base_pixmap = QPixmap(900, 900)
            self.base_pixmap.fill(QColor("#2c2c2c"))
        
        # 2. 빨간색 점 이미지 생성
        self.red_indicator = QPixmap(60, 60)
        self.red_indicator.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.red_indicator)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(15, 15, 30, 30)
        painter.end()

        # 3. 버튼(인디케이터) 데이터 리스트
        self.buttons = []
        self._init_all_buttons()
        
        self.img_label.mousePressEvent = self.on_image_clicked
        layout.addWidget(self.img_label)
        self.draw_indicators()

    def create_button(self, num, x, y, show_img=True, radius=30):
        button_data = {
            "num": num,
            "x": x,
            "y": y,
            "radius": radius,
            "show_img": show_img,
            "is_on": False  # 상태값
        }
        self.buttons.append(button_data)

    def _init_all_buttons(self):
        # 1~5번: 점+동그라미 (show_img=True)
        pos_group_1 = [(300, 304), (359, 268), (416, 235), (374, 328), (424, 376)]
        for i, (x, y) in enumerate(pos_group_1, 1):
            self.create_button(i, x, y, show_img=True)

        # 6~12번: 동그라미만 (show_img=False)
        pos_group_2 = [(489, 300), (636, 241), (724, 202), (802, 153), (690, 346), (757, 310), (815, 240)]
        for i, (x, y) in enumerate(pos_group_2, 6):
            self.create_button(i, x, y, show_img=False)

    def on_image_clicked(self, event: QMouseEvent):
        label_w, label_h = self.img_label.width(), self.img_label.height()
        orig_x = int(event.pos().x() * (self.base_pixmap.width() / label_w))
        orig_y = int(event.pos().y() * (self.base_pixmap.height() / label_h))

        for btn in self.buttons:
            distance = ((btn['x'] - orig_x)**2 + (btn['y'] - orig_y)**2)**0.5
            if distance < btn['radius']:
                btn['is_on'] = not btn['is_on']  # 상태 토글
                self.draw_indicators()
                break

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