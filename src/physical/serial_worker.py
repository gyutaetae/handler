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
            ser = serial.Serial(self.port, self.baudrate, timeout=0) # Non-blocking 모드
            buffer = bytearray()
            
            while self.running:
                if ser.in_waiting > 0:
                    # 1. 있는 데이터를 한꺼번에 다 긁어오기 (속도 핵심)
                    data = ser.read(ser.in_waiting)
                    buffer.extend(data)

                    print(f"현재 버퍼 크기: {len(buffer)} / 내용: {buffer.hex()}")
                    # 2. 버퍼에 쌓인 모든 패킷을 한 번의 루프에서 다 처리하기
                    while len(buffer) >= 3:
                        if buffer[0] == 0x02:
                            payload_len = buffer[2]
                            # 3 = stx, count, size_of_payload, 2 = checksum, etx
                            total_len = 3 + payload_len + 2

                            if len(buffer) >= total_len:
                                if buffer[total_len-1] == 0x03:
                                    packet = buffer[:total_len]
                                    self.data_received.emit(packet)
                                    del buffer[:total_len]
                                else:
                                    # 끝 바이트가 안 맞으면 시작 바이트가 잘못된 것임
                                    buffer.pop(0)
                            else:
                                # 데이터 덜 쌓임
                                break
                        else:
                            # 시작이 0x02가 아님
                            buffer.pop(0)
                else:
                    # 데이터가 없을 때만 아주 잠깐 쉼
                    self.msleep(1)
        except Exception as e:
            self.error_occurred.emit(str(e))
                            
    def run_17bytes(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=0) # Non-blocking 모드
            buffer = bytearray()
            
            while self.running:
                if ser.in_waiting > 0:
                    # 1. 있는 데이터를 한꺼번에 다 긁어오기 (속도 핵심)
                    data = ser.read(ser.in_waiting)
                    buffer.extend(data)

                    print(f"현재 버퍼 크기: {len(buffer)} / 내용: {buffer.hex()}")
                    # 2. 버퍼에 쌓인 모든 패킷을 한 번의 루프에서 다 처리하기
                    while len(buffer) >= 17:
                        if buffer[0] == 0x02:
                            if buffer[16] == 0x03:
                                packet = buffer[:17]
                                print(f"Perfect Packet!: {packet}")
                                self.data_received.emit(packet) # GUI로 전송
                                del buffer[:17]
                            else:
                                # 끝 바이트가 안 맞으면 시작 바이트가 잘못된 것임
                                buffer.pop(0)
                        else:
                            buffer.pop(0)
                else:
                    # 데이터가 없을 때만 아주 잠깐 쉽니다.
                    # 200Hz면 1~2ms 정도가 적당합니다.
                    self.msleep(1)
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
                    # print(f"Perfect Packet!: {packet}")
                    self.data_received.emit(packet)
                    del buffer[:17] # 처리한 패킷 삭제
                else:
                    # 시작은 맞는데 끝이 아니면, 이 0x02는 가짜(데이터 일부)일 수 있음
                    buffer.pop(0) # 첫 바이트 버리고 다음 0x02 찾기
            else:
                buffer.pop(0) # 시작 바이트가 아니면 버림