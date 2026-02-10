from PyQt6.QtCore import QObject, pyqtSignal
from protocol.checksum import validate_packet
from protocol.parser import TelemetryParser


class TelemetryController(QObject):
    def __init__(self, serial_worker):
        super().__init__() 
        self.worker = serial_worker
        self.worker.data_received.connect(self.handle_data)

    def handle_data(self, packet):
        if validate_packet(packet):
            print("valide")
            parser = TelemetryParser()
            model = parser.parse(packet)
            print(model)
        else:
            print("error")