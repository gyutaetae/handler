import os
from typing import override

class SignalConfigurator:
    def __init__(self, protocol):
        self.protocol = protocol

    def create_configuator(self):
        if self.protocol == "CCH->TFCC":
            self.configurator = CCH_SignalConfigurator(self.protocol)
        elif self.protocol == "GCH->TFCC":
            self.configurator = GCH_SignalConfigurator(self.protocol)
        elif self.protocol == "CCH->RCWS":
            self.configurator = RCWS_SignalConfigurator(self.protocol)
    
    def make_button_update_signal(self, model):
        return self.configurator.make_button_update_signal(model)

    def make_graph_update_signal(self, model):
        graph_signals = {
            "height": model.payload.height,
            "turning": model.payload.turning,
            "x_axis": model.payload.x_axis,
            "y_axis": model.payload.y_axis
        }
        return graph_signals

    def make_inspection_update_signal(self, model):
        return self.configurator.make_inspection_update_signal(model)

class CCH_SignalConfigurator(SignalConfigurator):
    def __init__(self, protocol):
        super().__init__(protocol)

    @override
    def make_button_update_signal(self, model):
        def click(bit):
            if bit == 1:
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
        button_signals = {
            "fire": click(model.payload.states.fire),
            "palm": click(model.payload.states.palm),
            "laser": click(model.payload.states.laser),
            "lock_on": click(model.payload.states.lock_on),
            "cursor": click(model.payload.states.cursor),
            "zoom": toggle(model.payload.states.zoom),
            "control_mode": toggle(model.payload.states.control_mode),
        }
        return button_signals
    
    @override
    def make_inspection_update_signal(self, model):
        return {}

class GCH_SignalConfigurator(SignalConfigurator):
    def __init__(self, protocol):
        super().__init__(protocol)

    @override
    def make_button_update_signal(self, model):
        def click(bit):
            if bit == 1:
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
        button_signals = {
            "fire": click(model.payload.states.fire),
            "palm": click(model.payload.states.palm),
            "laser": click(model.payload.states.laser),
            "auto_tracking": click(model.payload.states.auto_tracking),
        }
        return button_signals
    
    @override
    def make_inspection_update_signal(self, model):
        return {}

class RCWS_SignalConfigurator(SignalConfigurator):
    def __init__(self, protocol):
        super().__init__(protocol)

    @override
    def make_button_update_signal(self, model):
        def click(bit):
            if bit == 1:
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
        button_signals = {
            "fire": click(model.payload.states.fire),
            "palm": click(model.payload.states.palm),
            "laser": click(model.payload.states.laser),
            "lock_on": click(model.payload.states.lock_on),
            "ets": click(model.payload.states.ets),
            "override": click(model.payload.states.override),
            "fire_enable": click(model.payload.states.fire_enable),

            "camera": toggle(model.payload.states.camera),
            "shoot_mode": toggle(model.payload.states.shoot_mode),
            "cursor": click(model.payload.states.cursor),
            "load": click(model.payload.states.load),
            "auto_tracking": click(model.payload.states.auto_tracking),

            "control_mode": toggle(model.payload.states.control_mode),
            "zoom": toggle(model.payload.states.zoom),
            "modify_dist": toggle(model.payload.states.modify_dist)
        }
        return button_signals
    
    @override
    def make_inspection_update_signal(self, model):
        # {"id": ["desctiption", True]}
        # widget에서 알고리즘은.. if my_state == True : ignore elif my_state == False but input == True then ...

        def check(id, model):
            check_list = {
                0: lambda model: model.payload.states.palm == 0 and model.payload.states.lock_on == 1,
                1: lambda model: model.payload.states.palm == 0 and model.payload.states.lock_on == 0,
                2: lambda model: model.payload.states.palm == 0 and model.payload.states.fire == 1,
                3: lambda model: model.payload.states.palm == 0 and model.payload.states.laser == 1,
                4: lambda model: model.payload.states.palm == 0 and model.payload.states.shoot_mode == 0b01, # 단발
                5: lambda model: model.payload.states.palm == 0 and model.payload.states.shoot_mode == 0b00, # 점사
                6: lambda model: model.payload.states.palm == 0 and model.payload.states.shoot_mode == 0b10, # 연사
                7: lambda model: model.payload.states.palm == 0 and model.payload.states.zoom == 0b10, # zoom in
                8: lambda model: model.payload.states.palm == 0 and model.payload.states.zoom == 0b01, # zoom out
                9: lambda model: model.payload.states.palm == 1,
                10: lambda model: model.payload.states.palm == 1 and model.payload.states.lock_on == 1,
                11: lambda model: model.payload.states.palm == 1 and model.payload.states.lock_on == 0,
                12: lambda model: model.payload.states.palm == 1 and model.payload.states.fire == 1,
                13: lambda model: model.payload.states.palm == 1 and model.payload.states.laser == 1,
                14: lambda model: model.payload.states.palm == 1 and model.payload.states.shoot_mode == 0b01, # 단발
                15: lambda model: model.payload.states.palm == 1 and model.payload.states.shoot_mode == 0b00, # 점사
                16: lambda model: model.payload.states.palm == 1 and model.payload.states.shoot_mode == 0b10, # 연사
                17: lambda model: model.payload.states.palm == 1 and model.payload.states.modify_dist == 0b10, # dist up
                18: lambda model: model.payload.states.palm == 1 and model.payload.states.modify_dist == 0b01, # dist down
                19: lambda model: model.payload.states.camera == 0b00, # idle
                20: lambda model: model.payload.states.camera == 0b01, # cam1
                21: lambda model: model.payload.states.camera == 0b10, # cam2
                22: lambda model: model.payload.states.fire_enable == 1,
                23: lambda model: model.payload.states.fire_enable == 0,
                24: lambda model: model.payload.states.override == 1,
                25: lambda model: model.payload.states.override == 0,
                26: lambda model: model.payload.states.ets == 1,
                27: lambda model: model.payload.states.ets == 0,
                28: lambda model: model.payload.states.control_mode == 0b01, # RCWS
                29: lambda model: model.payload.states.control_mode == 0b10, # FCS
                30: lambda model: model.payload.states.cursor == 1 and model.payload.y_axis >= 0,
                31: lambda model: model.payload.states.cursor == 1 and model.payload.y_axis < 0,
                32: lambda model: model.payload.states.cursor == 1 and model.payload.x_axis >= 0,
                33: lambda model: model.payload.states.cursor == 1 and model.payload.x_axis < 0,
                34: lambda model: model.payload.states.load == 1,
                35: lambda model: model.payload.states.auto_tracking == 1,
            }
            return check_list[id](model)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        inspection_list = [line.strip() for line in open(os.path.join(BASE_DIR, "..", "inspection_config.txt"), 'r', encoding='utf-8').readlines()]

        inspection_signals = {}
        for id, description in enumerate(inspection_list):
            inspection_signals[id] = [description, check(id, model)]
        return inspection_signals