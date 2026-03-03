from dataclasses import dataclass

@dataclass
class States:
    pass

@dataclass
class CCH(States):
    palm: int # 12-1 bit 팜
    fire: int # 12-2 bit 격발
    laser: int # 12-3 bit 레이저발사
    lock_on: int # 12-4 bit 표적지정
    cursor: int # 12-5 bit 커서선택
    zoom: int # 12-6,7 bits 00:idle, 01:zoom out, 10:zoom in, 11:error
    reserved_12: int

    control_mode: int # 13-1,2 bits 00:error, 01: RCWS, 10:FCS, 11:error
    reserved_13_3: int
    reserved_13_4: int
    reserved_13_5: int
    reserved_13_6: int
    reserved_13_7: int
    reserved_13_8: int

    switch_error: int # 14-1 bit 스위치 오류
    fcs_signal_error: int # 14-2 bit 사통 이산 신호 오류
    rcws_signal_error: int # 14-3 bit RCWS 이산 신호 오류
    rcws_cable_continuity_check: int # 14-4 bit RCWS 케이블 연속성 점검
    reserved_14_5: int
    reserved_14_6: int
    reserved_14_7: int
    reserved_14_8: int

    internal_power_error: int # 15-1 bit 내부전원 오류
    turning_error: int # 15-2 bit 선회 오류
    height_error: int # 15-3 bit 고저오류
    reserved_15_4: int
    reserved_15_5: int
    reserved_15_6: int
    reserved_15_7: int
    reserved_15_8: int

@dataclass
class GCH(States):
    palm: int # 12-1 bit 팜
    fire: int # 12-2 bit 격발
    laser: int # 12-3 bit 레이저발사
    auto_tracking: int # 12-4 bit 자동추적
    reserved_12_5: int
    reserved_12_6: int
    reserved_12_7: int
    reserved_12_8: int

    switch_error: int # 13-1 bit 스위치 오류
    fcs_signal_error: int # 13-2 bit 사통 이산 신호 오류
    reserved_13_3: int
    reserved_13_4: int
    reserved_13_5: int
    reserved_13_6: int
    reserved_13_7: int
    reserved_13_8: int

    internal_power_error: int # 14-1 bit 내부전원 오류
    turning_error: int # 14-2 bit 선회 오류
    height_error: int # 14-3 bit 고저오류
    reserved_14_4: int
    reserved_14_5: int
    reserved_14_6: int
    reserved_14_7: int
    reserved_14_8: int

@dataclass
class RCWS(States):
    fire: int # 12-1 bit 격발
    palm : int # 12-2 bit 팜
    laser: int # 12-3 bit 레이저발사
    lock_on: int # 12-4 bit 표적지정
    ets: int # 12-5 bit ETS
    override: int # 12-6 bit Override
    fire_enable: int # 12-7 bit Fire enable
    reserved_12: int # 12-8 bit reserved

    camera: int # 13-1,2 bits camera 00:idle, 01:cam1, 10:cam2, 11:error
    shoot_mode: int # 13-3,4 bits shoot_mode 00:점사, 01:단발, 10:연사, 11:error
    cursor: int # 13-5 bit 커서선택
    load: int # 13-6 bit 장전(모드전환 이용1)
    auto_tracking: int # 13-7 bit 자동추적(모드전환 이용2)
    reserved_13: int # 13-8 bit reserved

    control_mode: int # 14-1,2 bits 00:error, 01: RCWS, 10:FCS, 11:error
    zoom: int # 14-3,4 bits 00:idle, 01:zoom out, 10:zoom in, 11:error
    modify_dist: int # 14-5,6 bits 00:idle, 10:거리수정up, 01:거리수정down, 11:error
    reserved_14_1: int # 14-7 bit reserved
    reserved_14_2: int # 14-8 bit reserved

@dataclass
class Payload:
    id: int # 3 byte TDB : random
    height: int # 4,5 bytes 고저
    turning: int # 6,7 bytes 선회
    x_axis: int # 8,9 bytes X축
    y_axis: int # 10,11 bytes Y축
    states: States

@dataclass
class Telemetry:
    stx: int # TBD : 0x02
    count: int
    size_of_payload: int
    payload: Payload
    check_sum: int
    etx: int # TBD : 0x03