import serial
import time
from byte_simulator import TestPacketGenerator

# com0com으로 만든 쌍 중 '보내는 쪽' 포트 (예: COM11)
OUT_PORT = 'COM11' 
BAUDRATE = 115200

tpg = TestPacketGenerator()

try:
    ser = serial.Serial(OUT_PORT, BAUDRATE)
    print(f"{OUT_PORT}를 통해 데이터 주입 시작 (200Hz)...")

    count = 0
    for _ in range(1000) :
        tpg.generate_packet()
        packet = tpg.get_packet(to_byte=True)
        # print(packet)
        for p in packet:
            # print(bytes([p]))
            ser.write(bytes([p]))
            time.sleep(0.005)

except KeyboardInterrupt:
    print("중단됨")
except Exception as e:
    print(f"오류: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()