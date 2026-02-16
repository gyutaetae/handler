from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtCore import pyqtSignal
import pyqtgraph as pg
import numpy as np

class Widgets(QWidget):
    def __init__(self):
        pass
    def create_button(self, title, position:list, parent=None):
        return CustomButton(title, position, parent)
    
    def create_graph(self, title, parent=None):
        return RealTimeGraph(title, parent)

class CustomButton(QPushButton):
    def __init__(self, title, pos:list, parent=None):
        super().__init__(title, parent)
                
        self.title = title
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.btn_w = 10
        self.btn_h = 10

        self.setGeometry(self.pos_x, self.pos_y, self.btn_w, self.btn_h)

        self.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        self.hide()

        self.current_state = "OFF"

    def update_data(self, value):
        if self.current_state == value:
            return
        if value == "ON":
            self.show()
            self.current_state = "ON"
        elif value == "OFF":
            self.hide()
            self.current_state = "OFF"

class RealTimeGraph(pg.PlotWidget):
    def __init__(self, title="Real-time Data", parent=None):
        super().__init__(parent)
        self.setBackground('w')
        self.setTitle(title)
        self.showGrid(x=True, y=True)
        
        # 데이터 라인 초기화
        self.data_line = self.plot(pen=pg.mkPen(color='b', width=2))
        self.x_data = list(range(100)) # X축 범위
        self.y_data = [0] * 100        # Y축 초기값

    def update_data(self, new_value):
        """새로운 데이터를 그래프에 반영하는 메서드"""
        self.y_data.pop(0)            # 가장 오래된 데이터 제거
        self.y_data.append(new_value)  # 새 데이터 추가
        self.data_line.setData(self.x_data, self.y_data)