class DataTransformer:
    def __init__(self):
        pass
    
    def _transform_and_checck_degree_data(self, model):
        if not self._calc_height(model):
            # print("height data error")
            return False
        if not self._calc_turning(model):
            # print("turning data error")
            return False
        self._calc_x_axis(model)
        self._calc_y_axis(model)
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
        model.payload.x_axis = model.payload.x_axis - 32768
        return True

    def _calc_y_axis(self, model):
        model.payload.y_axis = model.payload.y_axis - 32768
        return True