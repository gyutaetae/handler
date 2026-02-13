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
        self.base_pixmap = QPixmap("image/cch_front.png")
        if self.base_pixmap.isNull():
            self.base_pixmap = QPixmap(900, 900)
            self.base_pixmap.fill(QColor("#2c2c2c"))
        
        # 2. 빨간색 점 이미지 생성
        self.red_indicator = QPixmap(60, 60)
        self.red_indicator.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.red_indicator)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(15, 15, 30, 30)
        painter.end()

        # 3. 버튼 데이터 관리 (딕셔너리 구조)
        self.buttons = {}
        self._init_all_buttons()
        
        self.img_label.mousePressEvent = self.on_image_clicked
        layout.addWidget(self.img_label)
        
        # 초기 그리기 (지연 실행 대비)
        self.draw_indicators()

    def create_button(self, name, x, y, show_img=True, radius=30):
        """이름을 키로 하여 버튼 데이터 저장"""
        self.buttons[name] = {
            "x": x,
            "y": y,
            "radius": radius,
            "show_img": show_img,
            "is_on": False  # 상태값 (0 또는 1로 활용 가능)
        }

    def _init_all_buttons(self):
        # 그룹 1: 점 + 테두리 표시 (show_img=True)
        group_1 = {
            "fire": (300, 304),
            "palm": (359, 268),
            "laser": (416, 235),
            "lock": (374, 328),
            "ets": (424, 376)
        }
        for name, pos in group_1.items():
            self.create_button(name, pos[0], pos[1], show_img=True)

        # 그룹 2: 테두리만 표시 (show_img=False)
        group_2 = {
            "override": (489, 300),
            "fire_enable": (636, 241),
            "camera": (724, 202),
            "shoot_mode": (724, 202), # 좌표 중첩 시 클릭 판정은 루프 순서에 따름
            "cursor": (802, 153),
            "load": (690, 346),
            "auto_tracking": (690, 346),
            "control_mode": (757, 310),
            "zoom": (815, 240),
            "modify_dist": (815, 240)
        }
        for name, pos in group_2.items():
            self.create_button(name, pos[0], pos[1], show_img=False)

    def on_image_clicked(self, event: QMouseEvent):
        if self.img_label.pixmap() is None:
            return

        # 1. 원본 이미지 크기
        pix_w, pix_h = self.base_pixmap.width(), self.base_pixmap.height()
        # 2. QLabel 크기
        label_w, label_h = self.img_label.width(), self.img_label.height()

        # 3. KeepAspectRatio 모드에서 이미지가 실제로 그려지는 비율(Scale) 계산
        scale = min(label_w / pix_w, label_h / pix_h)
        
        # 4. 레이블 내에서 실제 이미지가 차지하는 크기
        actual_w = pix_w * scale
        actual_h = pix_h * scale

        # 5. AlignCenter로 인해 발생하는 오프셋(여백) 계산
        offset_x = (label_w - actual_w) / 2
        offset_y = (label_h - actual_h) / 2

        # 6. 클릭한 좌표에서 여백을 빼고, 스케일을 역산하여 원본 좌표 추출
        click_x = event.pos().x()
        click_y = event.pos().y()

        orig_x = int((click_x - offset_x) / scale)
        orig_y = int((click_y - offset_y) / scale)

        # 7. 클릭 범위 제한 (이미지 밖을 클릭했을 경우 무시)
        if 0 <= orig_x <= pix_w and 0 <= orig_y <= pix_h:
            # 모든 버튼 검사
            for name, btn in self.buttons.items():
                distance = ((btn['x'] - orig_x)**2 + (btn['y'] - orig_y)**2)**0.5
                if distance < btn['radius']:
                    btn['is_on'] = not btn['is_on']
                    print(f"Button Clicked: {name} | Status: {btn['is_on']}")
                    self.draw_indicators()
                    break

    def draw_indicators(self):
        """현재 버튼 상태에 따라 캔버스 업데이트"""
        if self.img_label.size().width() <= 1: # 초기화 전 예외 처리
            return

        canvas = self.base_pixmap.copy()
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for name, btn in self.buttons.items():
            if not btn['is_on']:
                continue

            # 1. 빨간 점 (show_img 옵션이 있을 때만)
            if btn['show_img']:
                painter.drawPixmap(btn['x'] - 25, btn['y'] - 25, 50, 50, self.red_indicator)
            
            # 2. 빨간 테두리 (공통)
            painter.setPen(QPen(QColor(255, 0, 0), 6))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(btn['x'] - 25, btn['y'] - 25, 50, 50)

        painter.end()
        
        # 화면 비율에 맞게 스케일링 후 출력
        scaled = canvas.scaled(
            self.img_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.img_label.setPixmap(scaled)

    def resizeEvent(self, event):
        self.draw_indicators()
        super().resizeEvent(event)