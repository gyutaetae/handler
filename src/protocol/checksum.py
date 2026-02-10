def validate_packet(packet):
    packet = bytes(packet)
    received_checksum = packet[15]

    my_checksum = 0x00
    for b in packet[3:15]:
        my_checksum ^= b
    return received_checksum == my_checksum