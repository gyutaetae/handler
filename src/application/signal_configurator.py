class SignalConfigurator:
    def __init__(self):
        pass 

    def make_button_update_signal(self, model):
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
        button_signals = {
            "fire": click(model.payload.switch_state.fire),
            "palm": click(model.payload.switch_state.palm),
            "laser": click(model.payload.switch_state.laser),
            "lock_on": click(model.payload.switch_state.lock_on),
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
        return button_signals
    
    def make_graph_update_signal(self, model):
        graph_signals = {
            "height": model.payload.height,
            "turning": model.payload.turning,
            "x_axis": model.payload.x_axis,
            "y_axis": model.payload.y_axis
        }
        return graph_signals
    
    def make_inspection_update_signal(self, model):
        # {"id": ["desctiption", True]}
        # widget에서 알고리즘은.. if my_state == True : ignore elif my_state == False but input == True then ...

        def check(id, model):
            check_list = {
                0: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.lock_on == 1,
                1: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.lock_on == 0,
                2: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.fire == 1,
                3: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.laser == 1,
                4: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.shoot_mode == 0b01, # 단발
                5: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.shoot_mode == 0b00, # 점사
                6: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.shoot_mode == 0b10, # 연사
                7: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.zoom == 0b10, # zoom in
                8: lambda model: model.payload.switch_state.palm == 0 and model.payload.switch_state.zoom == 0b01, # zoom out
                9: lambda model: model.payload.switch_state.palm == 1,
                10: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.lock_on == 1,
                11: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.lock_on == 0,
                12: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.fire == 1,
                13: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.laser == 1,
                14: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.shoot_mode == 0b01, # 단발
                15: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.shoot_mode == 0b00, # 점사
                16: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.shoot_mode == 0b10, # 연사
                17: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.modify_dist == 0b10, # dist up
                18: lambda model: model.payload.switch_state.palm == 1 and model.payload.switch_state.modify_dist == 0b01, # dist down
                19: lambda model: model.payload.switch_state.camera == 0b00, # idle
                20: lambda model: model.payload.switch_state.camera == 0b01, # cam1
                21: lambda model: model.payload.switch_state.camera == 0b10, # cam2
                22: lambda model: model.payload.switch_state.fire_enable == 1,
                23: lambda model: model.payload.switch_state.fire_enable == 0,
                24: lambda model: model.payload.switch_state.override == 1,
                25: lambda model: model.payload.switch_state.override == 0,
                26: lambda model: model.payload.switch_state.ets == 1,
                27: lambda model: model.payload.switch_state.ets == 0,
                28: lambda model: model.payload.switch_state.control_mode == 0b01, # RCWS
                29: lambda model: model.payload.switch_state.control_mode == 0b10, # FCS
                30: lambda model: model.payload.switch_state.cursor == 1 and model.payload.y_axis >= 0,
                31: lambda model: model.payload.switch_state.cursor == 1 and model.payload.y_axis < 0,
                32: lambda model: model.payload.switch_state.cursor == 1 and model.payload.x_axis >= 0,
                33: lambda model: model.payload.switch_state.cursor == 1 and model.payload.x_axis < 0,
                34: lambda model: model.payload.switch_state.load == 1,
                35: lambda model: model.payload.switch_state.auto_tracking == 1,
            }
            return check_list[id](model)

        inspection_list = [
            "버튼 동작 없음 (표적지정 ON)",
            "버튼 동작 없음 (표적지정 OFF)",
            "버튼 동작 없음 (격발)",
            "버튼 동작 없음 (레이저)",
            "스위치 동작 없음 (발사모드 단발)",
            "스위치 동작 없음 (발사모드 점사)",
            "스위치 동작 없음 (발사모드 연사)",
            "FOV 상방향",
            "FOV 하방향",
            "팜 스위치",
            "팜 스위치 + 표적지정 (ON)",
            "팜 스위치 + 표적지정 (OFF)",
            "팜 스위치 + 격발",
            "팜 스위치 + 레이저",
            "팜 스위치 + 발사모드 단발",
            "팜 스위치 + 발사모드 점사",
            "팜 스위치 + 발사모드 연사",
            "팜 스위치 + 거리 수정 상방향",
            "팜 스위치 + 거리 수정 하방향",
            "카메라 선택 스위치 (idle)",
            "카메라 선택 스위치 (cam1)",
            "카메라 선택 스위치 (cam2)",
            "Fire Enable 스위치 ON",
            "Fire Enable 스위치 OFF",
            "Override 스위치 ON",
            "Override 스위치 OFF",
            "Move Enable 스위치 ON",
            "Move Enable 스위치 OFF",
            "연동전환 스위치 RCWS",
            "연동전환 스위치 사통",
            "커서 위",
            "커서 아래",
            "커서 좌",
            "커서 우",
            "모드전환 / 장전 스위치"
        ]

        inspection_signals = {}
        for id, description in enumerate(inspection_list):
            inspection_signals[id] = [description, check(id, model)]
        return inspection_signals