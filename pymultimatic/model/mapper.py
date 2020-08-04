"""Mappers from json to model classes."""
from datetime import datetime
from typing import Optional, List, Any, Tuple

from . import (BoilerStatus, Circulation, Device, HolidayMode, HotWater,
               QuickMode, QuickModes, QuickVeto, Room, TimeProgram,
               TimeProgramDay, TimePeriodSetting, OperatingModes, Error,
               SyncState, SettingModes, SystemInfo, Dhw, OperatingMode, Zone,
               ZoneHeating, ZoneCooling, Report, Ventilation)

_DATE_FORMAT = "%Y-%m-%d"


def map_quick_mode(full_system) -> Optional[QuickMode]:
    """Map *quick mode*."""
    if full_system:
        quick_mode = full_system.get("body", dict()) \
            .get("configuration", dict()).get("quickmode")
        if quick_mode:
            mode = QuickModes.get(quick_mode.get("quickmode"))
            if mode != QuickModes.QUICK_VETO:
                return mode
    return None


def map_outdoor_temp(full_system) -> Optional[float]:
    """get *outdoor_temperature*."""
    if full_system:
        raw_temp = full_system.get("body", dict()).get("status", dict()) \
            .get('outside_temperature')
        if raw_temp is not None:
            return float(raw_temp)
    return None


def map_rooms(raw_rooms) -> List[Room]:
    """Map *rooms*."""
    rooms: List[Room] = []
    if raw_rooms:
        for raw_room in raw_rooms.get("body", dict()).get("rooms", list()):
            room = map_room(raw_room)
            if room:
                rooms.append(room)

    return rooms


def map_room(raw_room) -> Optional[Room]:
    """Map *room*."""
    if raw_room:
        raw_room = raw_room.get("body", raw_room)

        if raw_room:
            config = raw_room.get("configuration", dict())

            func = _map_function(raw_room)

            room_id = raw_room.get("roomIndex")
            child_lock = config.get("childLock")
            current_temp = config.get("currentTemperature")
            devices = map_devices(config.get("devices"))
            window_open = config.get("isWindowOpen")
            name = config.get("name")
            humidity = config.get('currentHumidity')

            raw_quick_veto = config.get("quickVeto")
            quick_veto = None
            if raw_quick_veto:
                quick_veto = QuickVeto(
                    raw_quick_veto.get("remainingDuration"),
                    config.get("temperatureSetpoint"))

            return Room(id=room_id,
                        name=name,
                        time_program=func[0],
                        temperature=current_temp,
                        target_high=func[2],
                        operating_mode=func[1],
                        quick_veto=quick_veto,
                        child_lock=child_lock,
                        window_open=window_open,
                        devices=devices,
                        humidity=humidity)
    return None


def map_devices(raw_devices) -> List[Device]:
    """Map *devices* of a room."""
    devices = []
    if raw_devices:
        for raw_device in raw_devices:
            name = raw_device.get("name")
            device_type = raw_device.get("deviceType")
            battery_low = raw_device.get("isBatteryLow")
            radio_out_of_reach = raw_device.get("isRadioOutOfReach")
            sgtin = raw_device.get("sgtin")
            devices.append(
                Device(name, sgtin, device_type, battery_low,
                       radio_out_of_reach))

    return devices


def map_time_program(raw_time_program, key: Optional[str] = None) \
        -> TimeProgram:
    """Map *time program*."""
    result = {}
    if raw_time_program:
        result["monday"] = map_time_program_day(
            raw_time_program.get("monday"), key)
        result["tuesday"] = map_time_program_day(
            raw_time_program.get("tuesday"), key)
        result["wednesday"] = map_time_program_day(
            raw_time_program.get("wednesday"), key)
        result["thursday"] = map_time_program_day(
            raw_time_program.get("thursday"), key)
        result["friday"] = map_time_program_day(
            raw_time_program.get("friday"), key)
        result["saturday"] = map_time_program_day(
            raw_time_program.get("saturday"), key)
        result["sunday"] = map_time_program_day(
            raw_time_program.get("sunday"), key)

    return TimeProgram(result)


def map_time_program_day(raw_time_program_day, key: Optional[str] = None) \
        -> TimeProgramDay:
    """Map *time program day* and *time program day settings*."""
    settings = []
    if raw_time_program_day:
        for time_setting in raw_time_program_day:
            start_time = time_setting.get("startTime")
            target_temp = time_setting.get("temperatureSetpoint")

            mode = None
            if key:
                mode = SettingModes.get(time_setting.get(key))

            settings.append(
                TimePeriodSetting(start_time, target_temp, mode))

    return TimeProgramDay(settings)


def map_holiday_mode(full_system) -> HolidayMode:
    """Map *holiday mode*."""
    mode = HolidayMode(False)
    if full_system:
        raw_holiday_mode = full_system.get("body", dict()) \
            .get("configuration", dict()).get("holidaymode")

        if raw_holiday_mode:
            mode.is_active = bool(raw_holiday_mode.get("active"))
            mode.target = float(raw_holiday_mode
                                .get("temperature_setpoint"))
            mode.start_date = datetime.strptime(
                raw_holiday_mode.get("start_date"), _DATE_FORMAT).date()
            mode.end_date = datetime.strptime(
                raw_holiday_mode.get("end_date"), _DATE_FORMAT).date()

    return mode


def map_boiler_status(hvac_state) -> Optional[BoilerStatus]:
    """Map *boiler status."""
    if hvac_state:
        hvac_state_info = _find_hvac_message_status(hvac_state)
        if hvac_state_info:
            last_update = _datetime_mandatory(hvac_state_info.get("timestamp"))
            device_name = str(hvac_state_info.get("deviceName"))
            code = str(hvac_state_info.get("statusCode"))
            title = str(hvac_state_info.get("title"))
            description = str(hvac_state_info.get("description"))
            hint = str(hvac_state_info.get("hint"))
            return BoilerStatus(device_name, title, code, description,
                                last_update, hint)

    return None


def _map_status(hvac_state) -> Tuple[str, str]:
    """Map *system status*."""
    meta = hvac_state.get('meta', dict())
    online = meta.get('onlineStatus', dict()).get('status')
    update = meta.get('firmwareUpdateStatus', dict()).get('status')
    return online, update


def map_system_info(facilities, gateway, hvac) -> SystemInfo:
    """Map *system info*."""
    serial = map_serial_number(facilities)

    facility = facilities.get("body", dict()).get("facilitiesList", list())[0]
    name = facility.get("name", None)
    mac_ethernet = facility.get("networkInformation", dict()) \
        .get("macAddressEthernet")
    mac_wifi = facility.get("networkInformation", dict()) \
        .get("macAddressWifiAccessPoint")
    firmware = facility.get("firmwareVersion", None)
    gateway = gateway.get("body", dict()).get("gatewayType", None)

    online, update = _map_status(hvac)

    return SystemInfo(gateway, serial, name, mac_ethernet, mac_wifi, firmware,
                      online, update)


def map_zones(full_system) -> List[Zone]:
    """Map *zones*."""
    zones = []
    if full_system:
        for raw_zone in full_system.get("body", dict()).get("zones", list()):
            zone = map_zone(raw_zone)
            if zone:
                zones.append(zone)

    return zones


def map_zone(raw_zone) -> Optional[Zone]:
    """Map *zones*."""
    raw_zone_body = raw_zone.get("body")

    if raw_zone_body:
        raw_zone = raw_zone_body

    if raw_zone:
        zone_id = raw_zone.get("_id")
        configuration = raw_zone.get("configuration", dict())
        name = configuration.get("name", "").strip()
        temperature = configuration.get("inside_temperature")
        active_function = configuration.get("active_function")
        quick_veto = _map_quick_veto_zone(configuration.get("quick_veto"))
        rbr = raw_zone.get("currently_controlled_by", dict())\
            .get("name", "") == "RBR"

        raw_heating = raw_zone.get("heating", dict())
        raw_cooling = raw_zone.get("cooling", dict())
        enabled = configuration.get("enabled", bool())

        zone_cooling = None
        func = _map_function(raw_heating, "setting")
        zone_heating = ZoneHeating(func[0], func[1], func[2], func[3])

        if raw_cooling:
            func = _map_function(raw_cooling, "setting")
            zone_cooling = ZoneCooling(func[0], func[1], func[2], func[3])

        return Zone(id=zone_id, name=name,  # type: ignore
                    temperature=temperature,
                    quick_veto=quick_veto, active_function=active_function,
                    rbr=rbr, heating=zone_heating, cooling=zone_cooling,
                    enabled=enabled)
    return None


def map_ventilation(system) -> Optional[Ventilation]:
    """Maps *ventilation*."""
    ventilation = None
    if system:
        fans = system.get('body', dict()).get('ventilation', list())
        if fans:
            func = _map_function(fans[0].get('fan', dict()), 'setting')
            fan_id = fans[0].get("_id")
            ventilation = Ventilation(id=fan_id, name='Ventilation',
                                      time_program=func[0],
                                      operating_mode=func[1],
                                      target_high=func[2], target_low=func[3])

    return ventilation


def _map_function(
        raw,
        tp_key=None) -> Tuple[TimeProgram, OperatingMode, float, float]:
    conf = raw.get("configuration", dict())
    mode = conf.get('mode')
    if not mode:
        mode = conf.get('operation_mode')
        if not mode:
            mode = conf.get('operationMode')

    operating_mode = OperatingModes.get(mode)
    target_high = conf.get("setpoint_temperature", None)
    if not target_high:
        target_high = conf.get("temperature_setpoint", None)
        if not target_high:
            target_high = conf.get("temperatureSetpoint", None)
        if not target_high:
            target_high = conf.get("day_level", None)

    target_low = conf.get("setback_temperature", None)
    if not target_low:
        target_low = conf.get("night_level", None)
    time_program = map_time_program(raw.get("timeprogram"), tp_key)

    return time_program, operating_mode, target_high, target_low


def map_hot_water(full_system, live_report) -> Optional[HotWater]:
    """Map *hot water*."""
    hot_water_list = None
    if full_system:
        hot_water_list = full_system.get("body", dict()).get("dhw")

    if hot_water_list:
        raw_hot_water = hot_water_list[0].get("hotwater")
        dwh_id = hot_water_list[0].get("_id")

        if raw_hot_water:
            return _map_hot_water(raw_hot_water, dwh_id, live_report)

    return None


def map_hot_water_alone(raw_hot_water, dhw_id: str, live_report) \
        -> Optional[HotWater]:
    """Map *hot water*."""
    if raw_hot_water:
        raw_hot_water_body = raw_hot_water.get("body", dict())
        return _map_hot_water(raw_hot_water_body, dhw_id, live_report)
    return None


def map_dhw(full_system, live_report) -> Dhw:
    """Map *dhw*."""
    circulation = map_circulation(full_system)
    hotwater = map_hot_water(full_system, live_report)
    return Dhw(hotwater=hotwater, circulation=circulation)


def map_circulation(full_system) -> Optional[Circulation]:
    """Map *circulation*."""
    if full_system:
        hot_water_list = full_system.get("body", dict()).get("dhw", list())

        if hot_water_list:
            raw_circulation = hot_water_list[0].get("circulation")
            dhw_id = hot_water_list[0].get("_id")

            if raw_circulation:
                return _map_circulation(raw_circulation, dhw_id)
    return None


def map_circulation_alone(raw_circulation, dhw_id: str) \
        -> Optional[Circulation]:
    """Map *circulation*."""
    if raw_circulation:
        raw_circulation_body = raw_circulation.get("body", dict())
        return _map_circulation(raw_circulation_body, dhw_id)
    return None


def map_errors(hvac_state) -> List[Error]:
    """Map *errors*."""
    errors = []
    for error in hvac_state.get("body", dict()).get("errorMessages",
                                                    list()):
        if error.get("type") == "ERROR":
            errors.append(Error(error.get('deviceName'),
                                error.get('title'),
                                error.get('statusCode'),
                                error.get('description'),
                                _datetime_mandatory(error.get('timestamp'))))
    return errors


def map_hvac_sync_state(hvac_state) -> Optional[SyncState]:
    """Map sync state."""
    if hvac_state:
        states = hvac_state.get('meta', dict()).get('syncState', list())
        if states:
            return _map_state(states[0])
    return None


def map_serial_number(facilities) -> str:
    """Map serial number."""
    facility = facilities.get("body", dict()).get("facilitiesList", list())[0]
    return str(facility.get("serialNumber", None))


def _map_state(raw_state) -> Optional[SyncState]:
    state = str(raw_state.get('state'))
    timestamp = _datetime_mandatory(raw_state.get('timestamp'))
    link = raw_state.get('link', dict()).get('resourceLink')
    return SyncState(state, timestamp, link)


def map_reports(live_report) -> List[Report]:
    """Maps *Reports*."""
    reports = []

    if live_report:
        for device in live_report.get("body", dict()).get("devices", list()):
            device_id = device.get("_id")
            device_name = device.get("name")

            for report in device.get("reports", list()):
                report_id = report.get("_id")
                name = report.get("name")
                value = report.get("value")
                unit = report.get("unit")
                report = Report(id=report_id, value=value, name=name,
                                unit=unit, device_id=device_id,
                                device_name=device_name)
                reports.append(report)

    return reports


def _map_hot_water(raw_hot_water, dhw_id: str, report) -> Optional[HotWater]:
    func = _map_function(raw_hot_water, "mode")

    current_temp = None

    if report:
        dhw_report = _find_dhw_temperature_report(report)
        if dhw_report:
            current_temp = dhw_report.get("value")

    return HotWater(id=dhw_id,
                    name='hotwater',
                    time_program=func[0],
                    temperature=current_temp,
                    target_high=func[2],
                    operating_mode=func[1])


def _map_circulation(raw_circulation, dhw_id: str) -> Circulation:
    func = _map_function(raw_circulation, "setting")

    return Circulation(id=dhw_id,
                       name='Circulation',
                       time_program=func[0],
                       operating_mode=func[1])


def _find_hvac_message_status(hvac_state) -> Optional[Any]:
    for message in hvac_state.get("body", dict()).get("errorMessages", list()):
        if message.get("type") == "STATUS":
            return message
    return None


def _find_dhw_temperature_report(live_report) -> Optional[Any]:
    for device in live_report.get("body", dict()).get("devices", list()):
        for report in device.get("reports", list()):
            if report.get("associated_device_function") == "DHW" \
                    and report.get("_id") == \
                    "DomesticHotWaterTankTemperature":
                return report
    return None


def _map_quick_veto_zone(raw_quick_veto) -> Optional[QuickVeto]:
    if raw_quick_veto and raw_quick_veto.get("active"):
        # No way to find start_date, Quick veto on zone lasts 6 hours
        return QuickVeto(target=raw_quick_veto.get("setpoint_temperature"))
    return None


def _datetime(timestamp: Optional[int]) -> Optional[datetime]:
    if timestamp:
        return datetime.fromtimestamp(timestamp / 1000)
    return None


def _datetime_mandatory(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000)
