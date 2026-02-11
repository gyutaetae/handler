from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen, QMouseEvent

#  [1. BaseIndicator: 모든 버튼의 부모 클래스] 
class BaseIndicator:
    def __init__(self, num, x, y, radius=30):
        self.num = num
        self.x = x
        self.y = y
        self.radius = radius
        self.state = "OFF"  # 기본 상태

    def is_clicked(self, ox, oy):
        return ((self.x - ox)**2 + (self.y - oy)**2)**0.5 < self.radius

    def draw(self, painter, red_pixmap):
        """오버라이딩"""
        pass

#  [2. ToggleIndicator: 1~5번(점+동그라미) 6~12번(동그라미)] 
class ToggleIndicator(BaseIndicator):
    def __init__(self, num, x, y, show_img=True):
        super().__init__(num, x, y)
        self.show_img = show_img
        self.is_on = False
    
    def handle_click(self):
        self.is_on = not self.is_on
        self.state = "ON" if self.is_on else "OFF"
        return self.state

    def draw(self, painter, red_pixmap):
        if not self.is_on: 
            return 

        # 빨간 불 이미지 표시 (1~5번)
        if self.show_img:
            painter.drawPixmap(self.x - 25, self.y - 25, 50, 50, red_pixmap)
        
        # 빨간 테두리 동그라미 (공통)
        painter.setPen(QPen(QColor(255, 0, 0), 6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(self.x - 25, self.y - 25, 50, 50)

#  [3. ClickableImagePanel: 전체 관리자] 
class ClickableImagePanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(self)
        
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 1. 원본 이미지 로드
        self.base_pixmap = QPixmap("image/handle_image.png")
        if self.base_pixmap.isNull():
            self.base_pixmap = QPixmap(900, 900)
            self.base_pixmap.fill(QColor("#2c2c2c"))
        
        # 2. 빨간색 점
        self.red_indicator = QPixmap(60,60)
        self.red_indicator.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.red_indicator)
        painter.setBrush(QColor(255,0,0))
        painter.drawEllipse(15,15,30,30)
        painter.end()       

        # 3. 인디케이터 객체 생성 및 리스트 관리
        self.indicators = []
        self._setup_indicators()
        
        self.img_label.mousePressEvent = self.on_image_clicked
        layout.addWidget(self.img_label)
        self.draw_indicators()

    def _setup_indicators(self):
        # 1~5번: 점+동그라미
        toggle_img_pos = [(300, 304), (359, 268), (416, 235),(374,328),(424,376)]
        for i, (x, y) in enumerate(toggle_img_pos, 1):
            self.indicators.append(ToggleIndicator(i, x, y, show_img=True))

        # 6~12번: 동그라미미
        extra_pos = [(489, 300), (636, 241), (724, 202), (802, 153), (690, 346), (757, 310), (815, 240)]
        for i, (x, y) in enumerate(extra_pos, 6):
            self.indicators.append(ToggleIndicator(i, x, y, show_img=False))

    def on_image_clicked(self, event: QMouseEvent):
        """클릭 좌표 변환 및 상태 업데이트"""
        label_w = self.img_label.width()
        label_h = self.img_label.height()
        orig_x = int(event.pos().x() * (self.base_pixmap.width() / label_w))
        orig_y = int(event.pos().y() * (self.base_pixmap.height() / label_h))

        for ind in self.indicators:
            if ind.is_clicked(orig_x, orig_y):
                ind.handle_click()
                self.draw_indicators()
                break

    def draw_indicators(self):
        canvas = self.base_pixmap.copy()
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for ind in self.indicators:
            ind.draw(painter, self.red_indicator)

        painter.end()
        
        # 화면 크기에 맞춰 스케일링하여 출력
        scaled = canvas.scaled(self.img_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.img_label.setPixmap(scaled)

    def resizeEvent(self, event):
        self.draw_indicators()