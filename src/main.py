import sys
import time
from PyQt6.QtWidgets import QApplication

# 1. 각 레이어에서 필요한 클래스 임포트
from physical.serial_worker import SerialWorker
from application.controller import TelemetryController
from ui.dashboard import MainPanel
# from config import SERIAL_PORT, BAUDRATE

### For Test ###
import sys
import os
from PyQt6.QtCore import QTimer

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)
from tests.byte_simulator import TestPacketGenerator
### For Test ###

class Main():

    def main(self):
        # # PyQt6 어플리케이션 시작
        self.app = QApplication(sys.argv)

        # # [Step 1] Physical Layer: 시리얼 통신 주체 생성
        # # QThread 기반으로 백그라운드에서 데이터를 계속 읽어옵니다.
        # serial_worker = SerialWorker(port=SERIAL_PORT, baudrate=BAUDRATE)


        ### For Test ###
        self.serial_worker = SerialWorker(port=1, baudrate=2)
        ### For Test ###


        # [Step 2] Application Layer: 로직 컨트롤러 생성
        # Physical Layer를 주입(Injection)받아 데이터를 감시합니다.
        self.app_controller = TelemetryController(self.serial_worker)

        # # [Step 3] UI Layer: 메인 윈도우 생성
        # # 사용자에게 보여줄 화면을 준비합니다.
        self.main_window = MainPanel()

        # # [Step 4] 레이어 간 조립 (Wiring)
        # # App Layer에서 판단된 결과를 UI의 함수와 연결합니다. (3번 방식 구현)
        self.app_controller.update_button.connect(self.main_window._update_button)
        self.app_controller.update_graph.connect(self.main_window._update_graph)
        self.app_controller.update_inspection.connect(self.main_window._update_inspection)
        # app_controller.error_occurred.connect(main_window.display_error_message)
        
        # # 만약 UI에서 장비로 명령을 보내야 한다면 반대로도 연결 가능합니다.
        # # main_window.btn_stop.clicked.connect(app_controller.send_stop_command)

        ### For Test ###
        # --- 테스트 데이터 자동 생성 타이머 ---
        self.tpg = TestPacketGenerator()
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.inject_test_data)
        self.test_timer.start(5) # 5ms 마다 실행 (200Hz)
        # -----------------------------
        ### For Test ###

        # # [Step 5] 실행
        # self.main_window.show()
        self.main_window.showMaximized()
        # serial_worker.start()  # 시리얼 읽기 시작

        sys.exit(self.app.exec())

    def inject_test_data(self):
        self.tpg.generate_packet()
        packet = self.tpg.get_packet(to_byte=True)
        self.serial_worker.test(packet) # 데이터 주입
        # test_packet = [0x02, 0x00, 0x0C]
        # test_packet.extend([0x01, 0x12, 0x32, 0x45, 0x56, 0x84, 0x10, 0x45, 0x65])
        # test_packet.extend([0x40, 0x20, 0x80, 0x66, 0x03])
        # test_packet = bytes(test_packet)
        # self.serial_worker.test(bytes(test_packet))
        

if __name__ == "__main__":
    main = Main()
    main.main()
