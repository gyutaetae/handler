def validate_packet(packet, protocol):
    packet = bytes(packet)
    if protocol == "CCH->TFCC":
        checksum_bit = 16
    elif protocol == "GCH->TFCC":
        checksum_bit = 15
    elif protocol == "CCH->RCWS":
        checksum_bit = 15
    received_checksum = packet[checksum_bit]

    my_checksum = 0x00
    for b in packet[3:checksum_bit]:
        my_checksum ^= b
    return received_checksum == my_checksum