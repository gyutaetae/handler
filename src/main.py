import sys
from PyQt6.QtWidgets import QApplication

# 1. 각 레이어에서 필요한 클래스 임포트
from physical.serial_worker import SerialWorker
from application.controller import TelemetryController
# from ui.dashboard import DashboardWindow
# from config import SERIAL_PORT, BAUDRATE

### For Test ###
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)
from tests.byte_simulator import TestPacketGenerator
### For Test ###

def main():
    # # PyQt6 어플리케이션 시작
    # app = QApplication(sys.argv)

    # # [Step 1] Physical Layer: 시리얼 통신 주체 생성
    # # QThread 기반으로 백그라운드에서 데이터를 계속 읽어옵니다.
    # serial_worker = SerialWorker(port=SERIAL_PORT, baudrate=BAUDRATE)


    ### For Test ###
    serial_worker = SerialWorker(port=1, baudrate=2)
    tpg = TestPacketGenerator()
    ### For Test ###


    # [Step 2] Application Layer: 로직 컨트롤러 생성
    # Physical Layer를 주입(Injection)받아 데이터를 감시합니다.
    app_controller = TelemetryController(serial_worker)


    ### For Test ###
    for _ in range(5):
        tpg.generate_packet()
        packet = tpg.get_packet(to_byte=True)
        serial_worker.test(packet)
    ### For Test ###


    # # [Step 3] UI Layer: 메인 윈도우 생성
    # # 사용자에게 보여줄 화면을 준비합니다.
    # main_window = DashboardWindow()

    # # [Step 4] 레이어 간 조립 (Wiring)
    # # App Layer에서 판단된 결과를 UI의 함수와 연결합니다. (3번 방식 구현)
    # app_controller.direction_changed.connect(main_window.update_direction_ui)
    # app_controller.error_occurred.connect(main_window.display_error_message)
    
    # # 만약 UI에서 장비로 명령을 보내야 한다면 반대로도 연결 가능합니다.
    # # main_window.btn_stop.clicked.connect(app_controller.send_stop_command)

    # # [Step 5] 실행
    # main_window.show()
    # serial_worker.start()  # 시리얼 읽기 시작

    # sys.exit(app.exec())

if __name__ == "__main__":
    main()
