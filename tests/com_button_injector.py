import serial
import time
from button_simulator import TestButtonPacket

# com0com으로 만든 쌍 중 '보내는 쪽' 포트 (예: COM11)
OUT_PORT = 'COM11' 
BAUDRATE = 115200

tpg = TestButtonPacket()
tpg.generate_combinations()

try:
    ser = serial.Serial(OUT_PORT, BAUDRATE)
    print(f"{OUT_PORT}를 통해 데이터 주입 시작 (200Hz)...")

    count = 0
    while len(tpg.combination_list) >0 :
        packet = tpg.get_combination()
        for p in packet:
            ser.write(bytes([p]))
            time.sleep(0.005)

except KeyboardInterrupt:
    print("중단됨")
except Exception as e:
    print(f"오류: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()