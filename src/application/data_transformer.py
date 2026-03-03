class DataTransformer:
    def __init__(self, protocol):
        self.protocol = protocol
    
    def transform_and_check_degree_data(self, model):
        if not self._calc_height(model):
            print("height data error")
            return False
        if not self._calc_turning(model):
            print("turning data error")
            return False
        self._calc_x_axis(model)
        self._calc_y_axis(model)
        return True
    
    def switch_data_check(self, model):
        if self.protocol == "CCH->TFCC":
            return self._cch(model)
        elif self.protocol == "GCH->TFCC":
            return self._gch(model)
        elif self.protocol == "CCH->RCWS":
            return self._rcws(model)

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
    
    def range_check(self, data):
        if 0b00 <= data <=0b10:
            return True
        else:
            return False
    
    def _rcws(self, model):
        def check_camera(model):
            camera = model.payload.states.camera
            return self.range_check(camera)
        def check_shoot_mode(model):
            shoot_mode = model.payload.states.shoot_mode
            return self.range_check(shoot_mode)
        def check_control_mode(model):
            control_mode = model.payload.states.control_mode
            return self.range_check(control_mode)
        def check_zoom(model):
            zoom = model.payload.states.zoom
            return self.range_check(zoom)
        def check_modify_dist(model):
            modify_dist = model.payload.states.modify_dist
            return self.range_check(modify_dist)
        camera = check_camera(model)
        shoot_mode = check_shoot_mode(model)
        control_mode = check_control_mode(model)
        zoom = check_zoom(model)
        modify_dist = check_modify_dist(model)
        return camera and shoot_mode and control_mode and zoom and modify_dist

    def _cch(self, model):
        def check_control_mode(model):
            control_mode = model.payload.states.control_mode
            return self.range_check(control_mode)
        def check_zoom(model):
            zoom = model.payload.states.zoom
            return self.range_check(zoom)
        control_mode = check_control_mode(model)
        zoom = check_zoom(model)
        return control_mode and zoom


    def _gch(self, model):
        return True