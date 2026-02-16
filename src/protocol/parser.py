from models.telemetry import Telemetry, Payload, SwitchState

class TelemetryParser:
    stx_ix = 0
    count_ix = 1
    size_of_payload_ix = 2
    id_ix = 3
    height_ix = [4, 5]
    turning_ix = [6, 7]
    x_axis_ix = [8, 9]
    y_axis_ix = [10, 11]
    switch_1 = 12
    switch_2 = 13
    switch_3 = 14
    check_sum_ix = 15
    etx_ix = 16
    def parse(self, packet):
        print("In parser: ", packet)
        return self._parse_packet(packet)
    
    def _parse_switch_states(self, packet):
        def bits_to_int(bits:list):
            res = 0
            for bit in bits:
                res = (res << 1) | bit
            return res
        
        def calc_switch_1(packet, ix):
            p = packet[ix]
            bits = [(p >> i) & 1 for i in range(8)]
            bits.reverse()
            return bits

        def calc_switch_2(packet, ix):
            p = packet[ix]
            bits = [(p >> i) & 1 for i in range(8)]
            bits.reverse()
            camera = bits_to_int(bits[0:2])
            shoot_mode = bits_to_int(bits[2:4])
            switch_2 = [camera, shoot_mode]
            switch_2.extend(bits[4:])
            return switch_2

        def calc_switch_3(packet, ix):
            p = packet[ix]
            bits = [(p >> i) & 1 for i in range(8)]
            bits.reverse()
            control_mode = bits_to_int(bits[0:2])
            zoom = bits_to_int(bits[2:4])
            modify_ist = bits_to_int(bits[4:6])
            switch_3 = [control_mode, zoom, modify_ist]
            switch_3.extend(bits[6:])
            return switch_3

        switch_packet_binary = calc_switch_1(packet, self.switch_1)
        switch_packet_binary.extend(calc_switch_2(packet, self.switch_2))
        switch_packet_binary.extend(calc_switch_3(packet, self.switch_3))

        model = SwitchState(
            *switch_packet_binary
        )
        return model

    def _parse_payload(self, packet):
        def calc_height(packet, ix:list): # Degree
            msb = packet[ix[0]]
            lsb = packet[ix[1]]
            height = (msb << 8) | lsb
            return height
            

        def calc_turning(packet, ix:list): # Degree
            msb = packet[ix[0]]
            lsb = packet[ix[1]]
            turning = (msb << 8) | lsb
            return turning

        def calc_x_axis(packet, ix:list): # ???
            msb = packet[ix[0]]
            lsb = packet[ix[1]]
            x_axis = (msb << 8) | lsb
            return x_axis

        def calc_y_axis(packet, ix:list): # ???
            msb = packet[ix[0]]
            lsb = packet[ix[1]]
            y_axis = (msb << 8) | lsb
            return y_axis

        model = Payload(
            id=packet[self.id_ix],
            height=calc_height(packet, self.height_ix),
            turning=calc_turning(packet, self.turning_ix),
            x_axis=calc_x_axis(packet, self.x_axis_ix),
            y_axis=calc_y_axis(packet, self.y_axis_ix),
            switch_state=self._parse_switch_states(packet)
        )
        return model

    def _parse_packet(self, packet):
        packet = list(packet)
        model = Telemetry(
            stx=packet[self.stx_ix],
            count=packet[self.count_ix],
            size_of_payload=packet[self.size_of_payload_ix],
            payload=self._parse_payload(packet),
            check_sum=packet[self.check_sum_ix],
            etx=packet[self.etx_ix]
        )
        return model
