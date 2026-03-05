from PyQt6.QtWidgets import QPushButton, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtCore import pyqtSignal, Qt, QSize
import pyqtgraph as pg
import numpy as np
import os

class Widgets(QWidget):
    def __init__(self):
        pass
    def create_button(self, title, position:list, parent=None):
        return CustomButton(title, position, parent)
    
    def create_graph(self, title, parent=None):
        return RealTimeGraph(title, parent)
    
    def create_table(self, num_row, num_col):
        return CustomTableWidget(num_row, num_col)

class CustomButton(QPushButton):
    def __init__(self, title, pos:list, parent=None):
        super().__init__("", parent)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        self.image_path = os.path.join(BASE_DIR, "images", "circle.png")
        self.title = title
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.btn_w = 30
        self.btn_h = 30

        if self.image_path:
            self.setIcon(QIcon(self.image_path))
            self.setIconSize(QSize(self.btn_w, self.btn_h)) # 아이콘 크기 지정

        self.setGeometry(self.pos_x, self.pos_y, self.btn_w, self.btn_h)

        self.setStyleSheet("""
            QPushButton {
                background-color: transparent; /* 배경을 투명하게 */
                border: none;                 /* 테두리 제거 */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 50); /* 호버 시 살짝 밝게 */
                border-radius: 5px;
            }
        """)
        self.hide()

        self.current_state = ["OFF", "00"]

    def update_data(self, value):
        ## control_mode는 추후 조작 추가되어야.
        if self.current_state[0] == value or self.current_state[1] == value:
            return
        
        if value == "ON":
            self.show()
            self.current_state[0] = "ON"
            return
        elif value == "OFF":
            self.hide()
            self.current_state[0] = "OFF"
            return

        if value == "00":
            self.hide()
            self.current_state[1] = "00"
            return
        elif value == "01":
            self.show()
            self.current_state[1] = "01"
            return
        elif value == "10":
            self.show()
            self.current_state[1] = "10"
            return

class RealTimeGraph(pg.PlotWidget):
    def __init__(self, title="Real-time Data", parent=None):
        super().__init__(parent)
        self.setBackground('w')
        self.setTitle(title)
        self.setMinimumHeight(200)
        self.title = title
        self.showGrid(x=True, y=True)
        if self.title == 'height' or self.title == 'turning':
            self.setYRange(-180, 180, padding=0)
        
        # 데이터 라인 초기화
        self.data_line = self.plot(pen=pg.mkPen(color='b', width=2))
        self.x_data = list(range(100)) # X축 범위
        self.y_data = [0] * 100        # Y축 초기값

    def update_data(self, new_value):
        """새로운 데이터를 그래프에 반영하는 메서드"""
        self.y_data.pop(0)            # 가장 오래된 데이터 제거
        if self.title == 'height' or self.title == 'turning':
            new_value -= 180
        self.y_data.append(new_value)  # 새 데이터 추가
        self.data_line.setData(self.x_data, self.y_data)

class CustomTableWidget(QTableWidget):
    def __init__(self, num_row, num_col):
        super().__init__()
        self.setRowCount(num_row)
        self.setColumnCount(num_col)
        self.item_registry = {}
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def init(self, inspection_list):
        for ix, description in enumerate(inspection_list):
            self.item_registry[ix] = {}
            description_item = QTableWidgetItem(description)
            description_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            inspection_item = QTableWidgetItem("미점검")
            inspection_item.setForeground(QColor("#dc3545"))
            inspection_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(ix, 0, description_item)
            self.setItem(ix, 1, inspection_item)

            self.item_registry[ix][0] = description_item
            self.item_registry[ix][1] = inspection_item
            self.item_registry[ix][2] = False


    def update_line(self, row, status):
        # print(row, status)
        def change(row):
            self.item_registry[row][1].setText("점검")
            self.item_registry[row][1].setForeground(QColor("#28a745"))
            self.item_registry[row][2] = True
        if self.item_registry[row][2] == True:
            return
        elif status == False:
            return
        else:
            if row == 0:
                change(row)
            else:
                if self.item_registry[row-1][2] == False:
                    return
                else:
                    change(row)