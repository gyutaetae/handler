import random 

class TestButtonPacket:
    def __init__(self, single=False):
        self.single = single
        self.packet = [None] * 17
        self.combination_list = []
        self.stx = 0x02
        self.etx = 0x03
        self.size_of_payload_data = 0x0C
        self.count = 0x00
        self.__button_packet_map()
        if single:
            self.__single_btn_test()
        else:
            self.__combinations()
    
    def _allocate_random(self, start=0, end=255):
        return random.randint(start, end)
    
    def _update_count(self):
        self.count = (self.count + 1) % 256
    
    def init_packet(self):
        self.packet = [None] * 17
        self.packet[0] = self.stx
        self.packet[1] = self.count
        self.packet[2] = self.size_of_payload_data
        self.packet[16] = self.etx
        self._update_count()
    
    def calc_checksum(self):
        checksum = 0
        for b in self.packet[3:15]:
            checksum ^= b
        self.packet[15] = checksum

    def generate_no_switch_payload(self):
        self.packet[3] = self._allocate_random()
        self.packet[4] = self._allocate_random()
        self.packet[5] = self._allocate_random()
        temp = random.randint(0, 1)
        if temp == 0:
            self.packet[6] = self._allocate_random(start=0x00,end=0x63)
            self.packet[7] = self._allocate_random(start=0x00,end=0x8D)
        else:
            self.packet[6] = self._allocate_random(start=0x9C,end=0xFF)
            self.packet[7] = self._allocate_random(start=0x72,end=0xFF)
        self.packet[8] = self._allocate_random()
        self.packet[9] = self._allocate_random()
        self.packet[10] = self._allocate_random()
        self.packet[11] = self._allocate_random()
        
    def generate_combinations(self):
        for comb_name in self.combinations.keys():
            self.init_packet()
            self.generate_no_switch_payload()
            self.config_packet(comb_name)
            self.calc_checksum()
            self.combination_list.append((comb_name, self.packet.copy()))
            if self.single:
                comb_name = "idle"
                self.init_packet()
                self.generate_no_switch_payload()
                self.config_packet(comb_name)
                self.calc_checksum()
                self.combination_list.append((comb_name, self.packet.copy()))

    
    def config_packet(self, comb_name):
        def make_or(packet_id, names:list):
            if packet_id == 12:
                switch = self.switch_1
            elif packet_id == 13:
                switch = self.switch_2
            elif packet_id == 14:
                switch = self.switch_3

            for ix, name in enumerate(names):
                if ix == 0:
                    res = switch[name]
                else:
                    res = res | switch[name]
            return res
        
        packet_12 = self.combinations[comb_name][12]
        packet_13 = self.combinations[comb_name][13]
        packet_14 = self.combinations[comb_name][14]
        self.packet[12] = make_or(12, packet_12)
        self.packet[13] = make_or(13, packet_13)
        self.packet[14] = make_or(14, packet_14)

    def get_combination(self):
        try:
            name, packet = self.combination_list.pop(0)
            print(name)
        except:
            exit()
        return bytes(packet)

    def __combinations(self):
        self.combinations = {
            "lock_on": {12: ["idle", "lock_on"], 13: ["idle"], 14: ["idle"]},
            "lock_off": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
            "fire": {12: ["idle", "fire"], 13: ["idle"], 14: ["idle"]},
            "laser": {12: ["idle","laser"], 13: ["idle"], 14: ["idle"]},
            "shoot_mode_single": {12: ["idle"], 13: ["idle", "shoot_mode_single"], 14: ["idle"]},
            "shoot_mode_interrupted": {12: ["idle"], 13: ["idle", "shoot_mode_interrupted"], 14: ["idle"]},
            "shoot_mode_fusillade": {12: ["idle"], 13: ["idle", "shoot_mode_fusillade"], 14: ["idle"]},
            "fov_up": {12: ["idle"], 13: ["idle"], 14: ["idle", "zoom_in"]},
            "fov_down": {12: ["idle"], 13: ["idle"], 14: ["idle", "zoom_out"]},
            "palm": {12: ["idle", "palm"], 13: ["idle"], 14: ["idle"]},
            "palm_lock_on": {12: ["idle", "palm", "lock_on"], 13: ["idle"], 14: ["idle"]},
            "palm_lock_off": {12: ["idle", "palm"], 13: ["idle"], 14: ["idle"]},
            "palm_fire": {12: ["idle", "palm", "fire"], 13: ["idle"], 14: ["idle"]},
            "palm_laser": {12: ["idle", "palm", "laser"], 13: ["idle"], 14: ["idle"]},
            "palm_shoot_mode_single": {12: ["idle", "palm"], 13: ["idle", "shoot_mode_single"], 14: ["idle"]},
            "palm_shoot_mode_interrupted": {12: ["idle", "palm"], 13: ["idle", "shoot_mode_interrupted"], 14: ["idle"]},
            "palm_shoot_mode_fusillade": {12: ["idle", "palm"], 13: ["idle", "shoot_mode_fusillade"], 14: ["idle"]},
            "palm_modify_dist_up": {12: ["idle", "palm"], 13: ["idle"], 14: ["idle", "modify_dist_up"]},
            "palm_modify_dist_down": {12: ["idle", "palm"], 13: ["idle"], 14: ["idle", "modify_dist_down"]},
            "cam_idle": {12: ["idle"], 13: ["idle", "camera_idle"], 14: ["idle"]},
            "cam1": {12: ["idle"], 13: ["idle", "camera_cam1"], 14: ["idle"]},
            "cam2": {12: ["idle"], 13: ["idle", "camera_cam2"], 14: ["idle"]},
            "fire_enable_on": {12: ["idle", "fire_enable"], 13: ["idle"], 14: ["idle"]},
            "fire_enable_off": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
            "override_on": {12: ["idle", "override"], 13: ["idle"], 14: ["idle"]},
            "override_off": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
            "move_enable_on": {12: ["idle", "ets"], 13: ["idle"], 14: ["idle"]},
            "move_enable_off": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
            "control_mode_rcws": {12: ["idle"], 13: ["idle"], 14: ["idle", "control_mode_rcws"]},
            "control_mode_fcs": {12: ["idle"], 13: ["idle"], 14: ["idle", "control_mode_fcs"]},
            "load": {12: ["idle"], 13: ["idle", "load"], 14: ["idle"]},
            "auto_tracking": {12: ["idle"], 13: ["idle", "auto_tracking"], 14: ["idle"]},
            "cursor": {12: ["idle"], 13: ["idle", "cursor"], 14: ["idle"]},
            "idle": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
        }

    def __single_btn_test(self):
        self.combinations = {
            "lock_on": {12: ["idle", "lock_on"], 13: ["idle"], 14: ["idle"]},
            # "lock_off": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
            "fire": {12: ["idle", "fire"], 13: ["idle"], 14: ["idle"]},
            "laser": {12: ["idle","laser"], 13: ["idle"], 14: ["idle"]},
            # "shoot_mode_single": {12: ["idle"], 13: ["idle", "shoot_mode_single"], 14: ["idle"]},
            # "shoot_mode_interrupted": {12: ["idle"], 13: ["idle", "shoot_mode_interrupted"], 14: ["idle"]},
            "shoot_mode_fusillade": {12: ["idle"], 13: ["idle", "shoot_mode_fusillade"], 14: ["idle"]},
            # "fov_up": {12: ["idle"], 13: ["idle"], 14: ["idle", "zoom_in"]},
            "fov_down": {12: ["idle"], 13: ["idle"], 14: ["idle", "zoom_out"]},
            "palm": {12: ["idle", "palm"], 13: ["idle"], 14: ["idle"]},
            # "cam_idle": {12: ["idle"], 13: ["idle", "camera_idle"], 14: ["idle"]},
            "cam1": {12: ["idle"], 13: ["idle", "camera_cam1"], 14: ["idle"]},
            "fire_enable_on": {12: ["idle", "fire_enable"], 13: ["idle"], 14: ["idle"]},
            # "fire_enable_off": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
            "override_on": {12: ["idle", "override"], 13: ["idle"], 14: ["idle"]},
            # "override_off": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
            "move_enable_on": {12: ["idle", "ets"], 13: ["idle"], 14: ["idle"]},
            # "move_enable_off": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
            "control_mode_rcws": {12: ["idle"], 13: ["idle"], 14: ["idle", "control_mode_rcws"]},
            "control_mode_fcs": {12: ["idle"], 13: ["idle"], 14: ["idle", "control_mode_fcs"]},
            # "load": {12: ["idle"], 13: ["idle", "load"], 14: ["idle"]},
            "auto_tracking": {12: ["idle"], 13: ["idle", "auto_tracking"], 14: ["idle"]},
            "cursor": {12: ["idle"], 13: ["idle", "cursor"], 14: ["idle"]},
            "idle": {12: ["idle"], 13: ["idle"], 14: ["idle"]},
        }

    def __button_packet_map(self):
        self.switch_1 = {
            "idle"                    : 0b00000000,
            "fire"                    : 0b10000000,
            "palm"                    : 0b01000000,
            "laser"                   : 0b00100000,
            "lock_on"                 : 0b00010000,
            "ets"                     : 0b00001000,
            "override"                : 0b00000100,
            "fire_enable"             : 0b00000010
        }

        self.switch_2 = {
            "idle"                    : 0b00000000,
            "camera_idle"             : 0b00000000,
            "camera_cam1"             : 0b01000000,
            "camera_cam2"             : 0b10000000,
            "shoot_mode_interrupted"  : 0b00000000,
            "shoot_mode_single"       : 0b00010000,
            "shoot_mode_fusillade"    : 0b00100000,
            "cursor"                  : 0b00001000,
            "load"                    : 0b00000100,
            "auto_tracking"           : 0b00000010
        }

        self.switch_3 = {
            "idle"                    : 0b00000000,
            "control_mode_rcws"       : 0b01000000,
            "control_mode_fcs"        : 0b10000000,
            "zoom_idle"               : 0b00000000,
            "zoom_out"                : 0b00010000,
            "zoom_in"                 : 0b00100000,
            "modify_dist_idle"        : 0b00000000,
            "modify_dist_up"          : 0b00001000,
            "modify_dist_down"        : 0b00000100
        }