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
from tests.button_simulator import TestButtonPacket
### For Test ###

class Main():

    def main(self):
        # # PyQt6 어플리케이션 시작
        self.app = QApplication(sys.argv)
        self.serial_worker = SerialWorker(0, 0)

        # Application Layer: 로직 컨트롤러 생성
        # Physical Layer를 주입(Injection)받아 데이터를 감시합니다.
        # Default do Nothing
        self.app_controller = TelemetryController(self.serial_worker)

        # UI Layer: 메인 윈도우 생성
        # 사용자에게 보여줄 화면을 준비합니다.
        self.main_window = MainPanel()

        # 레이어 간 조립 (Wiring)
        # App Layer에서 판단된 결과를 UI의 함수와 연결합니다. 
        self.app_controller.update_button.connect(self.main_window._update_button)
        self.app_controller.update_graph.connect(self.main_window._update_graph)
        self.app_controller.update_inspection.connect(self.main_window._update_inspection)
        # app_controller.error_occurred.connect(main_window.display_error_message)
        
        # # 만약 UI에서 장비로 명령을 보내야 한다면 반대로도 연결 가능합니다.
        self.main_window.setting_panel.conn_btn.clicked.connect(self.run_serial_worker)

        # 실행
        self.main_window.showMaximized()
        sys.exit(self.app.exec())

    def run_serial_worker(self):
        # Physical Layer: 시리얼 통신 주체 생성
        # QThread 기반으로 백그라운드에서 데이터를 계속 읽어옵니다.
        SERIAL_PORT , BAUDRATE, _ = self.main_window.setting_panel.get_info()
        print("SERIAL_PORT: ", SERIAL_PORT)
        print("BAUDRATE: ", BAUDRATE)
        self.serial_worker = SerialWorker(port=SERIAL_PORT, baudrate=BAUDRATE)
        # 시리얼 읽기 시작 
        # Serial_worker의 thread run()을 실행
        self.serial_worker.start()
        self.app_controller.update_worker(self.serial_worker)

        # self.random_test()
        # self.specific_test()
    
    def random_test(self):
        ## For Test ###
        # --- 테스트 데이터 자동 생성 타이머 ---
        self.tpg = TestPacketGenerator()
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.inject_test_random_data)
        self.test_timer.start(5) # 5ms 마다 실행 (200Hz)
        # -----------------------------

    def specific_test(self):
        ### For Test ###
        # --- 테스트 데이터 자동 생성 타이머 ---
        self.tpg = TestButtonPacket()
        self.tpg.generate_combinations()
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.inject_test_specific_data)
        self.test_timer.start(500) # 0.5s 마다 실행
        # -----------------------------

    def inject_test_random_data(self):
        # unlimited random
        self.tpg.generate_packet()
        packet = self.tpg.get_packet(to_byte=True)
        self.serial_worker.test(packet)

    def inject_test_specific_data(self):
        # limited test per button 
        packet = self.tpg.get_combination()
        self.serial_worker.test(packet) # 데이터 주입

if __name__ == "__main__":
    main = Main()
    main.main()
