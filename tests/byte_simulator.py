import time
import random

class TestPacketGenerator:
    def __init__(self):
        self.packet = [None] * 17
        self.stx = 0x02
        self.etx = 0x03
        self.size_of_payload_data = 0x0C
        self.count = 0x00
    
    def _update_count(self):
        self.count = (self.count + 1) % 256
    
    def _allocate_random(self, start=0, end=255):
        return random.randint(start, end)
        
    def _allocate_random_for_byte(self, bit_idx):
        if bit_idx == 12 or bit_idx == 13:
            bits = [self._allocate_random(0, 1) for i in range(7)]
            bits.append(0)
        elif bit_idx == 14:
            bits = [self._allocate_random(0, 1) for i in range(6)]
            bits.append(0)
            bits.append(0)
        decimal_val = 0
        for bit in bits:
            decimal_val = (decimal_val << 1) | bit
        return decimal_val
        
    
    def init_packet(self):
        self.packet[0] = self.stx
        self.packet[1] = self.count
        self.packet[2] = self.size_of_payload_data
        self.packet[16] = self.etx
        self._update_count()

    def generate_payload(self):
        self.packet[3] = self._allocate_random()
        self.packet[4] = self._allocate_random()
        self.packet[5] = self._allocate_random()
        self.packet[6] = self._allocate_random()
        self.packet[7] = self._allocate_random()
        self.packet[8] = self._allocate_random()
        self.packet[9] = self._allocate_random()
        self.packet[10] = self._allocate_random()
        self.packet[11] = self._allocate_random()
        self.packet[12] = self._allocate_random_for_byte(12)
        self.packet[13] = self._allocate_random_for_byte(13)
        self.packet[14] = self._allocate_random_for_byte(14)

    def calc_checksum(self):
        checksum = 0
        for b in self.packet[3:15]:
            checksum ^= b
        self.packet[15] = checksum
    
    def generate_packet(self):
        self.init_packet()
        self.generate_payload()
        self.calc_checksum()
    
    def print_packet(self, to_byte=False, to_bit=False):
        for p in self.packet:
            if to_byte:
                print(hex(p), end=', ')
            elif to_bit:
                bits = [(p >> i) & 1 for i in range(8)]
                bits.reverse()
                print(bits)
            else:
                print(p, end=', ')
        print()
    
    def get_packet(self, to_byte=False):
        try:
            if not to_byte:
                return self.packet
            else:
                return bytes(self.packet)
        except:
            print(f"발견된 문제 데이터: {self.packet}") # 여기서 255 넘는 놈을 확인!
            raise

# if __name__ == "__main__":
#     tpg = TestPacketGenerator()
#     for i in range(10):
#         tpg.generate_packet()
#         # 1tpg.print_packet(to_bit=True)
#         pk = tpg.get_packet()
#         print(pk)
        