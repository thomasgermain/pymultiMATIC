"""Mappers from json to model classes."""
from datetime import datetime
from typing import Optional, List, Any

from . import BoilerStatus, Circulation, Device, HolidayMode, HotWater, \
    QuickMode, QuickModes, QuickVeto, Room, TimeProgram, TimeProgramDay, \
    TimePeriodSetting, Zone, OperatingModes, Error, SystemStatus, SyncState, \
    SettingModes


_DATE_FORMAT = "%Y-%m-%d"


def map_quick_mode(full_system) -> Optional[QuickMode]:
    """Map *quick mode*."""
    if full_system:
        quick_mode = full_system.get("body", dict())\
            .get("configuration", dict()).get("quickmode")
        if quick_mode:
            mode = QuickModes.get(quick_mode.get("quickmode"))
            if mode != QuickModes.QUICK_VETO:
                return mode
    return None


def map_outdoor_temp(full_system) -> Optional[float]:
    """get *outdoor_temperature*."""
    if full_system:
        raw_temp = full_system.get("body", dict()).get("status", dict())\
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

            component_id = raw_room.get("roomIndex")
            child_lock = config.get("childLock")
            target_temp = config.get("temperatureSetpoint")
            current_temp = config.get("currentTemperature")
            devices = map_devices(config.get("devices"))
            window_open = config.get("isWindowOpen")
            name = config.get("name")
            operation_mode = OperatingModes.get(config.get("operationMode"))
            humidity = config.get('currentHumidity')

            raw_quick_veto = config.get("quickVeto")
            quick_veto = None
            if raw_quick_veto:
                quick_veto = QuickVeto(
                    raw_quick_veto.get("remainingDuration"),
                    config.get("temperatureSetpoint"))

            time_program = map_time_program(raw_room.get("timeprogram"))

            return Room(component_id, name, time_program, current_temp,
                        target_temp, operation_mode, quick_veto,
                        child_lock, window_open, devices, humidity)
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


def map_time_program(raw_time_program, key: Optional[str] = None)\
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
        raw_holiday_mode = full_system.get("body", dict())\
            .get("configuration", dict()).get("holidaymode")

        if raw_holiday_mode:
            mode.is_active = bool(raw_holiday_mode.get("active"))
            mode.target_temperature = float(raw_holiday_mode
                                            .get("temperature_setpoint"))
            mode.start_date = datetime.strptime(
                raw_holiday_mode.get("start_date"), _DATE_FORMAT).date()
            mode.end_date = datetime.strptime(
                raw_holiday_mode.get("end_date"), _DATE_FORMAT).date()

    return mode


def map_boiler_status(hvac_state, live_report) -> Optional[BoilerStatus]:
    """Map *boiler status*."""
    if hvac_state:
        hvac_state_info = _find_hvac_message_status(hvac_state)
        if hvac_state_info:
            last_update = _datetime_mandatory(hvac_state_info.get("timestamp"))
            device_name = str(hvac_state_info.get("deviceName"))
            code = str(hvac_state_info.get("statusCode"))
            title = str(hvac_state_info.get("title"))
            description = str(hvac_state_info.get("description"))
            hint = str(hvac_state_info.get("hint"))
            water_pressure = _find_water_pressure_report(live_report)
            boiler_temperature = _find_boiler_temperature_report(live_report)

            return BoilerStatus(device_name, title, code, description,
                                last_update, hint, water_pressure,
                                boiler_temperature)
    return None


def map_system_status(hvac_state) -> SystemStatus:
    """Map *system status*."""
    meta = hvac_state.get('meta', dict())
    online = meta.get('onlineStatus', dict()).get('status')
    update = meta.get('firmwareUpdateStatus', dict()).get('status')
    return SystemStatus(online, update)


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
        heating = raw_zone.get("heating", dict())
        configuration = raw_zone.get("configuration", dict())
        heating_configuration = heating.get("configuration", dict())

        zone_id = raw_zone.get("_id")
        operation_mode = OperatingModes.get(heating_configuration.get("mode"))
        target_temp = heating_configuration.get("setpoint_temperature")
        target_min_temp = heating_configuration.get("setback_temperature")
        time_program = map_time_program(heating.get("timeprogram"), "setting")

        name = configuration.get("name", "").strip()
        current_temperature = configuration.get("inside_temperature")
        active_function = configuration.get("active_function")

        quick_veto = _map_quick_veto_zone(configuration.get("quick_veto"))

        rbr = raw_zone.get("currently_controlled_by", dict())\
                      .get("name", "") == "RBR"

        return Zone(zone_id, name, time_program, current_temperature,
                    target_temp, operation_mode, quick_veto,
                    target_min_temp, active_function, rbr)

    return None


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


def map_circulation_alone(raw_circulation, dhw_id: str)\
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
    """Map """
    if hvac_state:
        states = hvac_state.get('meta', dict()).get('syncState', list())
        if states:
            return _map_state(states[0])
    return None


def _map_state(raw_state) -> Optional[SyncState]:
    if raw_state:
        state = str(raw_state.get('state'))
        timestamp = _datetime_mandatory(raw_state.get('timestamp'))
        link = raw_state.get('link', dict()).get('resourceLink')
        return SyncState(state, timestamp, link)
    return None


def _map_hot_water(raw_hot_water, dhw_id: str, live_report) \
        -> Optional[HotWater]:
    if raw_hot_water:
        target_temp = raw_hot_water.get("configuration", dict())\
            .get("temperature_setpoint")

        raw_operation_mode = raw_hot_water.get("configuration", dict())\
            .get("operation_mode")

        operation_mode = OperatingModes.get(raw_operation_mode)

        time_program = map_time_program(raw_hot_water.get("timeprogram",
                                                          dict()), "mode")

        current_temp = None
        name = None

        if live_report:
            dhw_report = _find_dhw_temperature_report(live_report)

            if dhw_report:
                current_temp = dhw_report.get("value")
                name = dhw_report.get("name")

        return HotWater(dhw_id, name, time_program, current_temp, target_temp,
                        operation_mode)
    return None


def _map_circulation(raw_circulation, circulation_id: str) -> Circulation:
    name = "Circulation"
    time_program = map_time_program(raw_circulation.get("timeprogram"),
                                    "setting")
    raw_operation_mode = raw_circulation.get("configuration", dict())\
        .get("operationMode")

    operation_mode = OperatingModes.get(raw_operation_mode)

    return Circulation(circulation_id, name, time_program, operation_mode)


def _find_hvac_message_status(hvac_state) -> Optional[Any]:
    for message in hvac_state.get("body", dict()).get("errorMessages", list()):
        if message.get("type") == "STATUS":
            return message
    return None


def _find_water_pressure_report(live_report) -> Optional[float]:
    if live_report:
        for device in live_report.get("body", dict()).get("devices", list()):
            for report in device.get("reports", list()):
                if report.get("associated_device_function") == "HEATING" \
                        and report.get("_id") == "WaterPressureSensor":
                    return float(report.get("value"))
    return None


def _find_boiler_temperature_report(live_report) -> Optional[float]:
    if live_report:
        for device in live_report.get("body", dict()).get("devices", list()):
            for report in device.get("reports", list()):
                if report.get("associated_device_function") == "HEATING" \
                        and report.get("_id") == "FlowTemperatureSensor":
                    return float(report.get("value"))
    return None


def _find_dhw_temperature_report(live_report) -> Optional[Any]:
    if live_report:
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
        return QuickVeto(None, raw_quick_veto.get("setpoint_temperature"))
    return None


def _datetime(timestamp: Optional[int]) -> Optional[datetime]:
    if timestamp:
        return datetime.fromtimestamp(timestamp / 1000)
    return None


def _datetime_mandatory(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000)
