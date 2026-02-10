import serial
import time
from PyQt6.QtCore import QThread, pyqtSignal

class SerialWorker(QThread):
    # 데이터를 외부(Controller)로 던져줄 신호
    data_received = pyqtSignal(bytearray) ## Controller로 들어가는 시그널 - self.worker.data_received.connect()
    error_occurred = pyqtSignal(str)

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True

    def run(self):
        try:
            # 시리얼 포트 설정
            ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            buffer = bytearray()
            while self.running:
                data = ser.read(ser.in_waiting or 1)
                buffer.extend(data)

                # 버퍼에 17바이트 이상이 있을 때만 반복 확인
                while len(buffer) >= 17:
                    if buffer[0] == 0x02: # 시작 바이트 확인
                        if buffer[16] == 0x03: # 끝 바이트 확인
                            packet = buffer[:17]
                            # 여기서 패리티 체크 후 로직 처리
                            print("Perfect Packet!")

                            self.data_received.emit(packet)
                            del buffer[:17] # 처리한 패킷 삭제
                        else:
                            # 시작은 맞는데 끝이 아니면, 이 0x02는 가짜(데이터 일부)일 수 있음
                            buffer.pop(0) # 첫 바이트 버리고 다음 0x02 찾기
                    else:
                        buffer.pop(0) # 시작 바이트가 아니면 버림
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self.running = False

    def test(self, data):
        data = data
        buffer = bytearray()
        buffer.extend(data)

        # 버퍼에 17바이트 이상이 있을 때만 반복 확인
        while len(buffer) >= 17:
            if buffer[0] == 0x02: # 시작 바이트 확인
                if buffer[16] == 0x03: # 끝 바이트 확인
                    packet = buffer[:17]
                    # print(len(packet))
                    # 여기서 패리티 체크 후 로직 처리
                    # print(f"Perfect Packet!: {packet}")
                    # print(type(packet))
                    # print(packet)
                    self.data_received.emit(packet)
                    del buffer[:17] # 처리한 패킷 삭제
                else:
                    # 시작은 맞는데 끝이 아니면, 이 0x02는 가짜(데이터 일부)일 수 있음
                    buffer.pop(0) # 첫 바이트 버리고 다음 0x02 찾기
            else:
                buffer.pop(0) # 시작 바이트가 아니면 버림