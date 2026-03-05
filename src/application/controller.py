from PyQt6.QtCore import QObject, pyqtSignal
from protocol.checksum import validate_packet
from protocol.parser import TelemetryParser
from application.data_transformer import DataTransformer
from application.signal_configurator import SignalConfigurator
from models.telemetry import Telemetry


class TelemetryController(QObject):
    update_button = pyqtSignal(dict)
    update_graph = pyqtSignal(dict)
    update_inspection = pyqtSignal(dict)
    def __init__(self, serial_worker):
        super().__init__() 
        self.worker = serial_worker
        self.worker.data_received.connect(self.handle_data)

    def handle_data(self, packet):
        # checksum 확인
        if validate_packet(packet, self.protocol):
            # print('-'*20)
            # print("packet valide")
            parser = TelemetryParser(self.protocol)
            transformer = DataTransformer(self.protocol)
            signal_configurator = SignalConfigurator(self.protocol)
            signal_configurator.create_configuator()
            # packet to model
            model = parser.parse(packet)

            # model value change - int data to degree data
            res = transformer.transform_and_check_degree_data(model)
            if not res:
                return False
            
            # model value change - int data to switch data
            res = transformer.switch_data_check(model)
            if not res:
                print("Switch data error")
                return False
            # print(model)
            # make gui update signal from changed model
            button_signals = signal_configurator.make_button_update_signal(model)
            graph_signals = signal_configurator.make_graph_update_signal(model)
            inspection_signals = signal_configurator.make_inspection_update_signal(model)
            self._send(button_signals, graph_signals, inspection_signals)
            # print('-'*20)
        else:
            print("error")

    def _send(self, button_signals, graph_signals, inspection_signals):
        # print(button_signals)
        self.update_button.emit(button_signals)
        self.update_graph.emit(graph_signals)
        self.update_inspection.emit(inspection_signals)

    def update_worker(self, worker, protocol):
        self.worker = worker
        self.worker.data_received.connect(self.handle_data)
        self.protocol = protocol