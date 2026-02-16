from PyQt6.QtCore import QObject, pyqtSignal
from protocol.checksum import validate_packet
from protocol.parser import TelemetryParser
from models.telemetry import Telemetry


class TelemetryController(QObject):
    update_button = pyqtSignal(dict)
    update_graph = pyqtSignal(dict)
    def __init__(self, serial_worker):
        super().__init__() 
        self.worker = serial_worker
        self.worker.data_received.connect(self.handle_data)

    def handle_data(self, packet):
        if validate_packet(packet):
            print('-'*20)
            print("packet valide")
            parser = TelemetryParser()
            model = parser.parse(packet)
            res = self._transform_and_checck_degree_data(model)
            if not res:
                return False
            
            res = self._switch_data_check(model)
            if not res:
                print("Switch data error")
                return False
            
            button_signals, graph_signals = self._make_update_signal(model)
            self._send(button_signals, graph_signals)
            print('-'*20)
        else:
            print("error")

    def _transform_and_checck_degree_data(self, model):
        if not self._calc_height(model):
            print("height data error")
            return False
        if not self._calc_turning(model):
            print("turning data error")
            return False

        return True

    def _switch_data_check(self, model):
        def range_check(data):
            if 0b00 <= data <=0b10:
                return True
            else:
                return False
        def check_camera(model):
            camera = model.payload.switch_state.camera
            return range_check(camera)
        def check_shoot_mode(model):
            shoot_mode = model.payload.switch_state.shoot_mode
            return range_check(shoot_mode)
        def check_control_mode(model):
            control_mode = model.payload.switch_state.control_mode
            return range_check(control_mode)
        def check_zoom(model):
            zoom = model.payload.switch_state.zoom
            return range_check(zoom)
        def check_modify_dist(model):
            modify_dist = model.payload.switch_state.modify_dist
            return range_check(modify_dist)
        camera = check_camera(model)
        shoot_mode = check_shoot_mode(model)
        control_mode = check_control_mode(model)
        zoom = check_zoom(model)
        modify_dist = check_modify_dist(model)
        return camera and shoot_mode and control_mode and zoom and modify_dist

    def _calc_height(self, model):
        height = model.payload.height
        if 0x0000 <= height <= 0x7FFF:
            model.payload.height = (height / 0x7FFF) * 30
            return True
        elif 0x8000 <= height <= 0xFFFF:
            model.payload.height = ((height - 0x8000) / (0xFFFF - 0x8000)) * 60 + 300
            return True
        else:
            return False
        
    def _calc_turning(self, model):
        turning = model.payload.turning
        if 0x0000 <= turning <= 0x638D:
            model.payload.turning = (turning / 0x638D) * 70
            return True
        elif 0x9C72 <= turning <= 0xFFFF:
            model.payload.turning = ( (turning-0x9C72) / (0xFFFF - 0x9C72) ) * 70 + 290
            return True
        else:
            return False
        
    def _calc_x_axis(self, model):
        return True

    def _calc_y_axis(self, model):
        return True
    
    def _make_update_signal(self, model):
        def click(bit):
            if bit == 0:
                return "ON"
            else:
                return "OFF"
        def toggle(bits):
            if bits == 0b00:
                return "00"
            elif bits == 0b01:
                return "01"
            elif bits == 0b10:
                return "10"
        graph_signals = {
            "height": model.payload.height,
            "turning": model.payload.turning,
            "x_axis": model.payload.x_axis,
            "y_axis": model.payload.y_axis
        }
        button_signals = {
            "fire": click(model.payload.switch_state.fire),
            "palm": click(model.payload.switch_state.palm),
            "laser": click(model.payload.switch_state.laser),
            "lock": click(model.payload.switch_state.lock),
            "ets": click(model.payload.switch_state.ets),
            "override": click(model.payload.switch_state.override),
            "fire_enable": click(model.payload.switch_state.fire_enable),

            "camera": toggle(model.payload.switch_state.camera),
            "shoot_mode": toggle(model.payload.switch_state.shoot_mode),
            "cursor": toggle(model.payload.switch_state.cursor),
            "load": toggle(model.payload.switch_state.load),
            "auto_tracking": toggle(model.payload.switch_state.auto_tracking),

            "control_mode": toggle(model.payload.switch_state.fire),
            "zoom": toggle(model.payload.switch_state.palm),
            "modify_dist": toggle(model.payload.switch_state.laser)
        }
        return button_signals, graph_signals

    def _send(self, button_signals, graph_signals):
        self.update_button.emit(button_signals)
        self.update_graph.emit(graph_signals)