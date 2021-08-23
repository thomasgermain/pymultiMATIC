"""Mappers from json to model classes."""
from datetime import datetime
from typing import Any, List, Optional, Tuple

from . import (
    ActiveFunction,
    BoilerStatus,
    Circulation,
    Device,
    Dhw,
    Error,
    FacilityDetail,
    HolidayMode,
    HotWater,
    HvacStatus,
    OperatingMode,
    OperatingModes,
    QuickMode,
    QuickModes,
    QuickVeto,
    Report,
    Room,
    SettingModes,
    SyncState,
    TimePeriodSetting,
    TimeProgram,
    TimeProgramDay,
    Ventilation,
    Zone,
    ZoneCooling,
    ZoneHeating,
    EmfReport,
)

_DATE_FORMAT = "%Y-%m-%d"
_DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def map_emf_reports(json) -> List[EmfReport]:
    """Map emf reports"""
    reports = []
    if json and json.get("body"):
        for raw_devices in json.get("body"):
            device_id = raw_devices.get("id")
            device_type = raw_devices.get("type")
            device_name = raw_devices.get("marketingName")
            for raw_report in raw_devices.get("reports"):
                reports.append(
                    EmfReport(
                        device_id,
                        device_name,
                        device_type,
                        raw_report.get("function"),
                        raw_report.get("energyType"),
                        raw_report.get("currentMeterReading"),
                        datetime.strptime(raw_report.get("from"), _DATE_FORMAT).date(),
                        datetime.strptime(raw_report.get("to"), _DATE_FORMAT).date(),
                    )
                )
    return reports


def map_gateway(json) -> str:
    """Map gateway."""
    return str(json.get("body", {}).get("gatewayType", None))


def map_quick_mode_from_system(full_system) -> Optional[QuickMode]:
    """Map *quick mode*."""
    if full_system:
        quick_mode = full_system.get("body", {}).get("configuration", {}).get("quickmode")
        return _map_quick_mode(quick_mode) if quick_mode else None
    return None


def map_quick_mode(json) -> Optional[QuickMode]:
    """Map quick mode."""
    return _map_quick_mode(json.get("body"))


def _map_quick_mode(json) -> Optional[QuickMode]:
    if json.get("quickmode"):
        mode = QuickModes.get(json.get("quickmode"), json.get("duration"))
        return mode if mode != QuickModes.QUICK_VETO else None
    return None


def map_holiday_mode(json) -> HolidayMode:
    """Map *holiday mode*."""
    return _map_holiday_mode(json.get("body"))


def map_holiday_mode_from_system(json) -> HolidayMode:
    """Map *holiday mode*."""
    return _map_holiday_mode(json.get("body", {}).get("configuration", {}).get("holidaymode"))


def _map_holiday_mode(json) -> HolidayMode:
    """Map *holiday mode*."""
    mode = HolidayMode(False)
    if json:
        mode.is_active = bool(json.get("active"))
        target = json.get("temperature_setpoint")
        mode.target = float(target) if target else None
        start_date = json.get("start_date")
        end_date = json.get("end_date")
        mode.start_date = datetime.strptime(start_date, _DATE_FORMAT).date() if start_date else None
        mode.end_date = datetime.strptime(end_date, _DATE_FORMAT).date() if end_date else None
    return mode


def map_hvac_status(json) -> HvacStatus:
    """Map hvac status."""
    meta = json.get("meta", {})
    return HvacStatus(
        online=meta.get("onlineStatus", {}).get("status"),
        update=meta.get("firmwareUpdateStatus", {}).get("status"),
        boiler_status=_map_boiler_status(json),
        errors=map_errors(json),
    )


def map_outdoor_temp(json) -> Optional[float]:
    """get *outdoor_temperature*."""
    tmp = json.get("body", {}).get("outside_temperature", None)
    return float(tmp) if tmp else None


def map_outdoor_temp_from_system(json) -> Optional[float]:
    """get *outdoor_temperature*."""
    tmp = json.get("body", {}).get("status", {}).get("outside_temperature", None)
    return float(tmp) if tmp else None


def map_rooms(raw_rooms) -> List[Room]:
    """Map *rooms*."""

    rooms: List[Room] = []
    if raw_rooms:
        rooms = [map_room(raw_room) for raw_room in raw_rooms.get("body", {}).get("rooms", [])]
    return rooms


def map_room(raw_room) -> Optional[Room]:
    """Map *room*."""
    if raw_room:
        raw_room = raw_room.get("body", raw_room)

        if raw_room:
            config = raw_room.get("configuration", {})

            t_prog, mode, high, low = _map_function(raw_room)

            room_id = raw_room.get("roomIndex")
            child_lock = config.get("childLock")
            current_temp = config.get("currentTemperature")
            devices = map_devices(config.get("devices"))
            window_open = config.get("isWindowOpen")
            name = config.get("name")
            humidity = config.get("currentHumidity")

            raw_quick_veto = config.get("quickVeto")
            quick_veto = None
            if raw_quick_veto:
                quick_veto = QuickVeto(
                    raw_quick_veto.get("remainingDuration"),
                    config.get("temperatureSetpoint"),
                )

            return Room(
                id=room_id,
                name=name,
                time_program=t_prog,
                temperature=current_temp,
                target_high=high,
                operating_mode=mode,
                quick_veto=quick_veto,
                child_lock=child_lock,
                window_open=window_open,
                devices=devices,
                humidity=humidity,
            )
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
            devices.append(Device(name, sgtin, device_type, battery_low, radio_out_of_reach))

    return devices


def map_time_program(raw_time_program, key: Optional[str] = None) -> TimeProgram:
    """Map *time program*."""
    result = {}
    if raw_time_program:
        for day_of_week in _DAYS_OF_WEEK:
            result[day_of_week] = map_time_program_day(raw_time_program.get(day_of_week), key)

    return TimeProgram(result)


def map_time_program_day(raw_time_program_day, key: Optional[str] = None) -> TimeProgramDay:
    """Map *time program day* and *time program day settings*."""
    settings = []
    if raw_time_program_day:
        for time_setting in raw_time_program_day:
            start_time = time_setting.get("startTime")
            target_temp = time_setting.get("temperatureSetpoint")

            mode = None
            if key:
                mode = SettingModes.get(time_setting.get(key))

            settings.append(TimePeriodSetting(start_time, target_temp, mode))

    return TimeProgramDay(settings)


def _map_boiler_status(hvac_state) -> Optional[BoilerStatus]:
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
            return BoilerStatus(device_name, title, code, description, last_update, hint)

    return None


def map_facility_detail(facilities, serial=None) -> FacilityDetail:
    """Map facility detail."""
    facilities_list = facilities.get("body", {}).get("facilitiesList", [])

    if serial:
        facility = [
            facility for facility in facilities_list if facility.get("serialNumber") == serial
        ][0]
    else:
        facility = facilities_list[0]
    return FacilityDetail(
        name=facility.get("name", None),
        serial_number=facility.get("serialNumber"),
        firmware_version=facility.get("firmwareVersion", None),
        ethernet_mac=facility.get("networkInformation", {}).get("macAddressEthernet"),
        wifi_mac=facility.get("networkInformation", {}).get("macAddressWifiAccessPoint"),
    )


def map_zones(json) -> List[Zone]:
    """Map *zones*."""
    return _map_zones(json.get("body", []))


def map_zones_from_system(json) -> List[Zone]:
    """Map *zones*."""
    return _map_zones(json.get("body", {}).get("zones", []))


def _map_zones(json) -> List[Zone]:
    """Map *zones*."""
    zones = []
    for raw_zone in json:
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
        configuration = raw_zone.get("configuration", {})
        name = configuration.get("name", "").strip()
        temperature = configuration.get("inside_temperature")
        active_function = ActiveFunction[
            configuration.get("active_function", ActiveFunction.STANDBY.name)
        ]
        quick_veto = _map_quick_veto_zone(configuration.get("quick_veto"))
        rbr = raw_zone.get("currently_controlled_by", {}).get("name", "") == "RBR"

        raw_heating = raw_zone.get("heating", {})
        raw_cooling = raw_zone.get("cooling", {})
        enabled = configuration.get("enabled", bool())

        zone_cooling = None
        func = _map_function(raw_heating, "setting", rbr, quick_veto is not None)
        zone_heating = ZoneHeating(func[0], func[1], func[2], func[3])

        if raw_cooling:
            func = _map_function(raw_cooling, "setting")
            zone_cooling = ZoneCooling(func[0], func[1], func[2], func[3])

        return Zone(  # type: ignore
            id=zone_id,
            name=name,
            temperature=temperature,
            quick_veto=quick_veto,
            active_function=active_function,
            rbr=rbr,
            heating=zone_heating,
            cooling=zone_cooling,
            enabled=enabled,
        )
    return None


def map_ventilation_from_system(system) -> Optional[Ventilation]:
    """Maps *ventilation*."""
    ventilation = None
    if system:
        fans = system.get("body", {}).get("ventilation", [])
        if fans:
            ventilation = _map_ventilation(fans[0])
    return ventilation


def map_ventilation(json) -> Optional[Ventilation]:
    """Maps *ventilation*."""
    return _map_ventilation(json.get("body")[0])


def _map_ventilation(json) -> Optional[Ventilation]:
    tprog, mode, target_high, target_low = _map_function(json.get("fan", {}), "setting")
    fan_id = json.get("_id")
    return Ventilation(
        id=fan_id,
        name="Ventilation",
        time_program=tprog,
        operating_mode=mode,
        target_high=target_high,
        target_low=target_low,
    )


def _map_function(
    raw, tp_key=None, rbr=False, quick_veto=False
) -> Tuple[TimeProgram, OperatingMode, float, float]:
    conf = raw.get("configuration", {})
    mode = conf.get("mode")
    if not mode:
        mode = conf.get("operation_mode")
        if not mode:
            mode = conf.get("operationMode")

    operating_mode: OperatingMode
    if rbr:
        operating_mode = OperatingModes.get(mode) if mode else None
    elif quick_veto:
        operating_mode = OperatingModes.QUICK_VETO
    else:
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


def map_hot_water_from_system(full_system, live_reports) -> Optional[HotWater]:
    """Map *hot water*."""
    dhws = full_system.get("body", {}).get("dhw")

    if dhws:
        hotwater = dhws[0].get("hotwater")
        dhw_id = dhws[0].get("_id")
        temp = _get_report_value(_find_dhw_temperature_report(live_reports))
        return _map_hot_water(hotwater, dhw_id, temp)

    return None


def map_hot_water_from_dhw(json) -> Optional[HotWater]:
    """Mapp hotware from dhw."""
    dhw = json.get("body")[0]
    dhw_id = dhw.get("_id")
    return _map_hot_water(dhw.get("hotwater"), dhw_id, None)


def map_hot_water(json, dhw_id: str) -> Optional[HotWater]:
    """Map *hot water*."""
    if json:
        hotwater = json.get("body", {})
        return _map_hot_water(hotwater, dhw_id, None)
    return None


def map_dhw_from_system(full_system, live_reports) -> Dhw:
    """Map *dhw*."""
    circulation = map_circulation_from_system(full_system)
    hotwater = map_hot_water_from_system(full_system, live_reports)
    return Dhw(hotwater=hotwater, circulation=circulation)


def map_dhw(dhw) -> Dhw:
    """Map *dhw*."""
    circulation = map_circulation_from_dhw(dhw)
    hotwater = map_hot_water_from_dhw(dhw)
    return Dhw(hotwater=hotwater, circulation=circulation)


def map_circulation_from_dhw(json) -> Optional[Circulation]:
    """Map *circulation*."""
    if json:
        dhws = json.get("body", [])

        if dhws:
            circulation = dhws[0].get("circulation")
            dhw_id = dhws[0].get("_id")
            return _map_circulation(circulation, dhw_id)
    return None


def map_circulation_from_system(full_system) -> Optional[Circulation]:
    """Map *circulation*."""
    if full_system:
        hot_water_list = full_system.get("body", {}).get("dhw", [])

        if hot_water_list:
            raw_circulation = hot_water_list[0].get("circulation")
            dhw_id = hot_water_list[0].get("_id")

            if raw_circulation:
                return _map_circulation(raw_circulation, dhw_id)
    return None


def map_circulation_alone(raw_circulation, dhw_id: str) -> Optional[Circulation]:
    """Map *circulation*."""
    if raw_circulation:
        raw_circulation_body = raw_circulation.get("body", {})
        return _map_circulation(raw_circulation_body, dhw_id)
    return None


def map_errors(hvac_state) -> List[Error]:
    """Map *errors*."""
    errors = []
    for error in hvac_state.get("body", {}).get("errorMessages", []):
        if error.get("type") == "ERROR":
            errors.append(
                Error(
                    error.get("deviceName"),
                    error.get("title"),
                    error.get("statusCode"),
                    error.get("description"),
                    _datetime_mandatory(error.get("timestamp")),
                )
            )
    return errors


def map_hvac_sync_state(hvac_state) -> Optional[SyncState]:
    """Map sync state."""
    if hvac_state:
        states = hvac_state.get("meta", {}).get("syncState", [])
        if states:
            return _map_state(states[0])
    return None


def map_serial_number(facilities) -> str:
    """Map serial number."""
    facility = facilities.get("body", {}).get("facilitiesList", [])[0]
    return str(facility.get("serialNumber", None))


def _map_state(raw_state) -> Optional[SyncState]:
    state = str(raw_state.get("state"))
    timestamp = _datetime_mandatory(raw_state.get("timestamp"))
    link = raw_state.get("link", {}).get("resourceLink")
    return SyncState(state, timestamp, link)


def map_reports(live_report) -> List[Report]:
    """Maps *Reports*."""
    reports = []

    if live_report:
        for device in live_report.get("body", {}).get("devices", []):
            device_id = device.get("_id")
            device_name = device.get("name")

            for report_json in device.get("reports", []):
                report = _map_report(report_json)
                if report:
                    report.device_id = device_id
                    report.device_name = device_name
                    reports.append(report)

    return reports


def map_report(json) -> Optional[Report]:
    """Map report."""
    return _map_report(json.get("body"))


def _map_report(json) -> Optional[Report]:
    if json:
        return Report(
            id=json.get("_id"),
            value=json.get("value"),
            name=json.get("name"),
            unit=json.get("unit"),
        )
    return None


def _map_hot_water(raw_hot_water, dhw_id, current_temp) -> Optional[HotWater]:
    timep, mode, high, low = _map_function(raw_hot_water, "mode")
    return HotWater(
        id=dhw_id,
        name="hotwater",
        time_program=timep,
        temperature=current_temp,
        target_high=high,
        operating_mode=mode,
    )


def _map_circulation(raw_circulation, dhw_id: str) -> Circulation:
    func = _map_function(raw_circulation, "setting")

    return Circulation(id=dhw_id, name="Circulation", time_program=func[0], operating_mode=func[1])


def _find_hvac_message_status(hvac_state) -> Optional[Any]:
    for message in hvac_state.get("body", {}).get("errorMessages", []):
        if message.get("type") == "STATUS":
            return message
    return None


def _find_dhw_temperature_report(live_report) -> Optional[Any]:
    for device in live_report.get("body", {}).get("devices", []):
        for report in device.get("reports", []):
            if (
                report.get("associated_device_function") == "DHW"
                and report.get("_id") == "DomesticHotWaterTankTemperature"
            ):
                return report
    return None


def _get_report_value(report) -> Any:
    if report:
        body = report.get("body")
        if body:
            return body.get("value")
        return report.get("value")
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
