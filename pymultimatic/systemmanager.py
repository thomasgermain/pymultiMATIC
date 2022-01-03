"""Convenient manager to easily gets data from API."""
import asyncio
import logging
from datetime import date, timedelta
from typing import Any, Callable, List, Optional, Tuple, Type

from aiohttp import ClientSession
from schema import Schema, SchemaError

from .api import ApiError, Connector, WrongResponseError, defaults, payloads, schemas, urls
from .model import (
    Circulation,
    Dhw,
    FacilityDetail,
    HolidayMode,
    HotWater,
    HvacStatus,
    OperatingMode,
    OperatingModes,
    QuickMode,
    QuickVeto,
    Report,
    Room,
    System,
    Ventilation,
    Zone,
    ZoneCooling,
    ZoneHeating,
    constants,
    mapper,
    EmfReport,
)

_LOGGER = logging.getLogger("SystemManager")


def ignore_http_409(return_value: Any = None) -> Callable[..., Any]:
    """Ignore ApiError if status code is 409."""

    def decorator(func: Callable[..., Any]) -> Any:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except ApiError as ex:
                if ex.status != 409:
                    raise
                return return_value

        return wrapper

    return decorator


def retry_async(
    num_tries: int = 5,
    on_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    on_status_codes: Tuple[int, ...] = (),
    backoff_base: float = 0.5,
) -> Callable[..., Any]:
    """In case of exceptions, retries decorated async function multiple times.

    Uses increasing backoff between tries.

    Args:
         num_tries (int): Max number of tries.
         on_exceptions (tuple): Retries on specific exceptions only.
         on_status_codes (tuple): If `ApiError` occurs,
            retry only on specified status codes.
         backoff_base (float): Backoff base value.
    """
    on_exceptions = on_exceptions + (ApiError,)

    def decorator(func: Callable[..., Any]) -> Any:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            _num_tries = num_tries
            last_response: Optional[str] = None
            while _num_tries > 0:
                _num_tries -= 1
                try:
                    return await func(*args, **kwargs)
                except on_exceptions as ex:
                    if not _num_tries:
                        if isinstance(ex, ApiError):
                            raise ex
                        raise ApiError(
                            "Cannot get correct response",
                            response=last_response,
                            status=200,
                        ) from ex
                    if isinstance(ex, ApiError):
                        last_response = ex.response
                        if ex.status not in on_status_codes:
                            raise
                    retry_in = backoff_base * (num_tries - _num_tries)
                    _LOGGER.debug("Error occurred, retrying in %s", retry_in, exc_info=True)
                    await asyncio.sleep(retry_in)

        return wrapper

    return decorator


class SystemManager:
    """This is a convenient manager to help interact with vaillant API.

    The manager is calling the
    :class:`~pymultimatic.api.connector.ApiConnector`, the manager will
    provide to correct :mod:`~pymultimatic.api.payloads` and
    :mod:`~pymultimatic.api.urls` according to what you want to do.

    The manager is throwing :class:`~pymultimatic.api.error.ApiError`
    without altering it.

    Args:
        user (str): User to login with.
        password (str): Password associated with the user.
        session: (aiohttp.ClientSession): Session.
        smartphone_id (str): This is required by the API to login.
        serial (str): If you have multiple facilities,
            you can specify which one to access
    """

    def __init__(
        self,
        user: str,
        password: str,
        session: ClientSession,
        smartphone_id: str = defaults.SMARTPHONE_ID,
        serial: Optional[str] = None,
    ):
        self._connector: Connector = Connector(user, password, session, smartphone_id)
        self._serial = serial
        self._fixed_serial = self._serial is not None
        self._ensure_ready_lock = asyncio.Lock()

    async def login(self, force_login: bool = False) -> bool:
        """Try to login to the API, see
        :func:`~pymultimatic.api.connector.ApiConnector.login`

        Args:
            force_login (bool): Whether the login should be forced or not.

        Returns:
            bool: True/False if authentication succeeded or not.
        """
        return await self._connector.login(force_login)

    async def logout(self) -> None:
        """Get logged out from the API, see
        :func:`~pymultimatic.api.connector.ApiConnector.logout`
        """
        if not self._fixed_serial:
            self._serial = None
        await self._connector.logout()

    async def get_system(self) -> System:
        """Get the full :class:`~pymultimatic.model.system.System`. It may
        take some times, it actually does multiples API calls, depending on
        your system configuration.

        Returns:
            System: the full system.
        """

        (facilities, full_system, live_report, hvac_state, gateway_json,) = await asyncio.gather(
            self._call_api(urls.facilities_list, schema=schemas.FACILITIES),
            self._call_api(urls.system, schema=schemas.SYSTEM),
            self._call_api(urls.live_report, schema=schemas.LIVE_REPORTS),
            self._call_api(urls.hvac, schema=schemas.HVAC),
            self._call_api(urls.gateway_type, schema=schemas.GATEWAY),
        )

        hvac_status = mapper.map_hvac_status(hvac_state)
        holiday = mapper.map_holiday_mode_from_system(full_system)
        zones = mapper.map_zones_from_system(full_system)
        outdoor_temp = mapper.map_outdoor_temp_from_system(full_system)
        quick_mode = mapper.map_quick_mode_from_system(full_system)
        ventilation = mapper.map_ventilation_from_system(full_system)
        dhw = mapper.map_dhw_from_system(full_system, live_report)
        reports = mapper.map_reports(live_report)
        facility_detail = mapper.map_facility_detail(facilities, self._serial)
        gateway = mapper.map_gateway(gateway_json)

        rooms: List[Room] = []
        if [z for z in zones if z.rbr]:
            rooms_raw = await self._call_api(urls.rooms, schema=schemas.ROOM_LIST)
            rooms = mapper.map_rooms(rooms_raw)

        return System(
            holiday=holiday,
            quick_mode=quick_mode,
            zones=zones,
            rooms=rooms,
            dhw=dhw,
            reports=reports,
            outdoor_temperature=outdoor_temp,
            hvac_status=hvac_status,
            facility_detail=facility_detail,
            ventilation=ventilation,
            gateway=gateway,
        )

    @ignore_http_409(return_value=[])
    async def get_emf_devices(self) -> List[EmfReport]:
        """Get all the EMF reports available.

        Returns:
            The list of report emf devices
        """
        return mapper.map_emf_reports(await self._call_api(urls.emf_devices))

    async def get_gateway(self) -> str:
        """Get the gateway type (VR900, VR920, etc)

        Returns:
            The gateway type
        """
        return mapper.map_gateway(await self._call_api(urls.gateway_type))

    @ignore_http_409()
    async def get_outdoor_temperature(self) -> Optional[float]:
        """Get the outdoor temperature

        Returns:
            The outdoor temperature if available
        """
        return mapper.map_outdoor_temp(await self._call_api(urls.system_status))

    @ignore_http_409()
    async def get_hvac_status(self) -> HvacStatus:
        """Get the :class:`~pymultimatic.model.HvacStatus`

        Returns:
            The hvac status
        """
        return mapper.map_hvac_status(await self._call_api(urls.hvac))

    async def get_facility_detail(self, serial: Optional[str] = None) -> FacilityDetail:
        """Get the :class:`~pymultimatic.model.FacilityDetail` for a given serial

        Returns:
            The facility detail
        """
        serial = serial if serial is not None else self._serial
        return mapper.map_facility_detail(
            await self._call_api(urls.facilities_list, schema=schemas.FACILITIES), serial
        )

    @ignore_http_409()
    async def get_live_reports(self) -> List[Report]:
        """Get available list of :class:`~pymultimatic.model.Report`

        Returns:
            A list of live reports
        """
        return mapper.map_reports(
            await self._call_api(urls.live_report, schema=schemas.LIVE_REPORTS)
        )

    @ignore_http_409()
    async def get_live_report(self, report_id: str, device_id: str) -> Optional[Report]:
        """Get available list of :class:`~pymultimatic.model.Report`

        Returns:
            A list of live reports
        """
        json = await self._call_api(
            urls.live_report_device,
            params={"device_id": device_id, "report_id": report_id},
            schema=schemas.LIVE_REPORT,
        )
        return mapper.map_report(json)

    @ignore_http_409()
    async def get_ventilation(self) -> Optional[Ventilation]:
        """Get the :class:`~pymultimatic.model.component.Ventilation`

        Returns:
            Ventilation: the ventilation
        """
        return mapper.map_ventilation(
            await self._call_api(urls.system_ventilation, schema=schemas.VENTILATION_LIST)
        )

    @ignore_http_409()
    async def get_holiday_mode(self) -> HolidayMode:
        """Get the :class:`~pymultimatic.model.quick_mode.HolidayMode`

        Returns:
            HolidayMode: the holiday mode
        """
        raw = await self._call_api(urls.system_holiday_mode)
        return mapper.map_holiday_mode(raw)

    @ignore_http_409()
    async def get_quick_mode(self) -> Optional[QuickMode]:
        """Get the :class:`~pymultimatic.model.quick_mode.QuickMode`

        Returns:
            QuickMode: the quick mode or None
        """
        return mapper.map_quick_mode(await self._call_api(urls.system_quickmode))

    @ignore_http_409()
    async def get_hot_water(self, dhw_id: str) -> Optional[HotWater]:
        """Get the :class:`~pymultimatic.model.component.HotWater`
        information for the given id.

        Args:
            dhw_id (str): domestic hot water id (same as
                :func:`get_circulation`).

        Returns:
            HotWater: the hot water information, if any.
        """
        dhw = await self._call_api(urls.hot_water, params={"id": dhw_id}, schema=schemas.FUNCTION)
        return mapper.map_hot_water(dhw, dhw_id)

    @ignore_http_409()
    async def get_dhw(self) -> Optional[Dhw]:
        """Get the :class:`~pymultimatic.model.Dhw` (Domestic Hot Water)

        Returns:
            The domestic Hot water (circulation + hot water), if any
        """
        dhw = await self._call_api(urls.dhws, schema=schemas.DHWS)
        return mapper.map_dhw(dhw)

    @ignore_http_409(return_value=[])
    async def get_rooms(self) -> Optional[List[Room]]:
        """Get a list of :class:`~pymultimatic.model.component.Room`

        Returns:
            Rooms: list of room
        """
        rooms = await self._call_api(urls.rooms, schema=schemas.ROOM_LIST)
        return mapper.map_rooms(rooms)

    @ignore_http_409()
    async def get_room(self, room_id: str) -> Optional[Room]:
        """Get the :class:`~pymultimatic.model.component.Room` information
        for the given id.

        Args:
            room_id (str): Id of the room, this is actually an index, 1,2,3,4
            ... depending of the number of rooms you have.

        Returns:
            Room: the room information, if any.
        """
        new_room = await self._call_api(urls.room, params={"id": room_id}, schema=schemas.ROOM)
        return mapper.map_room(new_room)

    @ignore_http_409(return_value=[])
    async def get_zones(self) -> Optional[List[Zone]]:
        """Get a list of :class:`~pymultimatic.model.component.Zone`

        Returns:
            Zones: list of Zone
        """
        rooms = await self._call_api(urls.zones, schema=schemas.ZONE_LIST)
        return mapper.map_zones(rooms)

    @ignore_http_409()
    async def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get the :class:`~pymultimatic.model.component.Zone` information
        for the given id.

        Args:
            zone_id (str): Name of the room, basically, you set it through the
                VRC 700.

        Returns:
            Zone: the zone information, if any.
        """
        new_zone = await self._call_api(urls.zone, params={"id": zone_id}, schema=schemas.ZONE)
        return mapper.map_zone(new_zone)

    @ignore_http_409()
    async def get_circulation(self, dhw_id: str) -> Optional[Circulation]:
        """Get the :class:`~pymultimatic.model.component.Circulation`
        information for the given id.

        Args:
            dhw_id (str): domestic hot water id (same as :func:`get_hot_water`)

        Returns:
            Circulation: the circulation information, if any.
        """
        new_circulation = await self._call_api(
            urls.circulation, params={"id": dhw_id}, schema=schemas.FUNCTION
        )
        return mapper.map_circulation_alone(new_circulation, dhw_id)

    async def set_quick_mode(self, quick_mode: QuickMode) -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickMode` system wise.

        This will override the current
        :class:`~pymultimatic.model.mode.QuickMode`, if any.

        Args:
            quick_mode (QuickMode): the quick mode to set, see
                :class:`~pymultimatic.model.mode.QuickModes`
        """
        await self._call_api(
            urls.system_quickmode, payload=payloads.quickmode(quick_mode.name, quick_mode.duration)
        )

    @ignore_http_409(return_value=False)
    async def remove_quick_mode(self) -> bool:
        """Removes current :class:`~pymultimatic.model.mode.QuickMode`.

        Note:
            if there is not :class:`~pymultimatic.model.mode.QuickMode` set,
            the API returns an error (HTTP 409). **This error is swallowed by
            the manager**, so you don't have to handle it.

        Returns:
              True/False: if quick_mode has been removed or not
                (if there wasn't any quick mode set previously)
        """

        await self._call_api(urls.system_quickmode, "delete")
        return True

    async def set_holiday_mode(self, start_date: date, end_date: date, temperature: float) -> None:
        """Set the :class:`~pymultimatic.model.mode.HolidayMode`.

        Args:
            start_date (date): Start date of the holiday mode.
            end_date (date): End date of the holiday mode.
            temperature (float): Target temperature while holiday mode
                :class:`~pymultimatic.model.mode.HolidayMode.is_applied`
        """
        payload = payloads.holiday_mode(True, start_date, end_date, self._round(temperature))

        await self._call_api(urls.system_holiday_mode, payload=payload)

    async def remove_holiday_mode(self) -> None:
        """Remove :class:`~pymultimatic.model.mode.HolidayMode`.

        Note:
            There is a little workaround here, since the API doesn't simply
            accept a DELETE request to remove the
            :class:`~pymultimatic.model.mode.HolidayMode`, so the manager is
            setting:

            * the start date to two days before

            * the end date to yesterday

            * temperature to frost protection

            * active to `False`

            This will ensure the
            :class:`~pymultimatic.model.mode.HolidayMode` is not active.

        """

        payload = payloads.holiday_mode(
            False,
            date.today() - timedelta(days=2),
            date.today() - timedelta(days=1),
            constants.FROST_PROTECTION_TEMP,
        )

        await self._call_api(urls.system_holiday_mode, payload=payload)

    async def set_hot_water_setpoint_temperature(self, dhw_id: str, temperature: float) -> None:
        """This set the target temperature for *hot water*."""
        _LOGGER.debug("Will set dhw target temperature to %s", temperature)

        payload = payloads.hotwater_temperature_setpoint(self._round(temperature))

        await self._call_api(
            urls.hot_water_temperature_setpoint, params={"id": dhw_id}, payload=payload
        )

    async def set_hot_water_operating_mode(self, dhw_id: str, new_mode: OperatingMode) -> None:
        """Set new operating mode for
        :class:`~pymultimatic.model.component.HotWater`. The mode should be
        listed here :class:`~pymultimatic.model.component.HotWater.MODES`
        otherwise it won't have any effect.


        Note:
            To set :class:`~pymultimatic.model.mode.QuickMode`, you
            have to use :func:`set_quick_mode`.

        Note:
            This call won't have any effect if there is a
            :class:`~pymultimatic.model.mode.QuickMode` activated, if you
            want to remove the quick mode, use :func:`remove_quick_mode`.

        Args:
            dhw_id (str): domestic hot water id.
            new_mode (OperatingMode): The new mode to set.
        """
        _LOGGER.debug("Will try to set hot water mode to %s", new_mode)

        if new_mode in HotWater.MODES:
            _LOGGER.debug("New mode is %s", new_mode)
            await self._call_api(
                urls.hot_water_operating_mode,
                params={"id": dhw_id},
                payload=payloads.hot_water_operating_mode(new_mode.name),
            )
        else:
            _LOGGER.debug("New mode is not available for hot water %s", new_mode)

    async def set_room_operating_mode(self, room_id: str, new_mode: OperatingMode) -> None:
        """Set new operating mode for
        :class:`~pymultimatic.model.component.Room`. The mode should be
        listed here :class:`~pymultimatic.model.component.Room.MODES`
        otherwise it won't have any effect.


        Note:
            To set :class:`~pymultimatic.model.mode.QuickMode`, you
            have to use :func:`set_quick_mode`.

        Note:
            This call won't have any effect if there is a
            :class:`~pymultimatic.model.mode.QuickMode` activated, if you
            want to remove the quick mode, use :func:`remove_quick_mode`.

        Note:
            To set :class:`~pymultimatic.model.mode.QuickVeto`, you have to
            use :func:`set_room_quick_veto`

        Args:
            room_id (str): id of the room.
            new_mode (OperatingMode): The new mode to set.
        """
        if new_mode in Room.MODES and new_mode != OperatingModes.QUICK_VETO:
            _LOGGER.debug("New mode is %s", new_mode)
            await self._call_api(
                urls.room_operating_mode,
                params={"id": room_id},
                payload=payloads.room_operating_mode(new_mode.name),
            )
        else:
            _LOGGER.debug("mode is not available for room %s", new_mode)

    async def set_room_quick_veto(self, room_id: str, quick_veto: QuickVeto) -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickVeto` for a
        :class:`~pymultimatic.model.component.Room`.
        It will override the current
        :class:`~pymultimatic.model.mode.QuickVeto`, if any.

        Args:
            room_id (str): Id of the room.
            quick_veto (QuickVeto): Quick veto to set.
        """
        payload = payloads.room_quick_veto(self._round(quick_veto.target), quick_veto.duration)
        await self._call_api(urls.room_quick_veto, params={"id": room_id}, payload=payload)

    async def remove_room_quick_veto(self, room_id: str) -> None:
        """Remove the :class:`~pymultimatic.model.mode.QuickVeto` from a
        :class:`~pymultimatic.model.component.Room`.

        Args:
            room_id (str): Id of the room.
        """

        await self._call_api(urls.room_quick_veto, "delete", params={"id": room_id})

    async def set_room_setpoint_temperature(self, room_id: str, temperature: float) -> None:
        """Set the new current target temperature for a
        :class:`~pymultimatic.model.component.Room`.

        Note:
            Setting the target temperature this way will actually set the room
            operating mode to
            :class:`~pymultimatic.model.mode.OperatingModes.MANUAL` (and
            target temperature to the desired temperature). It means the target
            temperature will remain the same until you change the target
            temperature again or the operating mode.

        Args:
            room_id (str): Id of the room.
            temperature (float): Target temperature to set.
        """

        _LOGGER.debug("Will try to set room target temperature to %s", temperature)

        await self._call_api(
            urls.room_temperature_setpoint,
            params={"id": room_id},
            payload=payloads.room_temperature_setpoint(self._round(temperature)),
        )

    async def set_zone_quick_veto(self, zone_id: str, quick_veto: QuickVeto) -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickVeto` for a
        :class:`~pymultimatic.model.component.Zone`.
        It will override the current
        :class:`~pymultimatic.model.mode.QuickVeto`, if any.

        Args:
            zone_id (str): Id of the zone.
            quick_veto (QuickVeto): Quick veto to set.
        """
        payload = payloads.zone_quick_veto(self._round(quick_veto.target))

        await self._call_api(urls.zone_quick_veto, params={"id": zone_id}, payload=payload)

    async def set_zone_heating_operating_mode(self, zone_id: str, new_mode: OperatingMode) -> None:
        """Set new operating mode to heat a
        :class:`~pymultimatic.model.component.Zone`. The mode should be
        listed here :class:`~pymultimatic.model.component.ZoneHeating.MODES`
        otherwise it won't have any effect.


        Note:
            To set :class:`~pymultimatic.model.mode.QuickMode`, you
            have to use :func:`set_quick_mode`.

        Note:
            This call won't have any effect if there is a
            :class:`~pymultimatic.model.mode.QuickMode` activated, if you
            want to remove the quick mode, use :func:`remove_quick_mode`.

        Note:
            To set :class:`~pymultimatic.model.mode.QuickVeto`, you have to
            use :func:`set_zone_quick_veto`

        Args:
            zone_id (str): id of the zone.
            new_mode (OperatingMode): The new mode to set.
        """
        if new_mode in ZoneHeating.MODES and new_mode != OperatingModes.QUICK_VETO:
            _LOGGER.debug("New mode is %s", new_mode)
            await self._call_api(
                urls.zone_heating_mode,
                params={"id": zone_id},
                payload=payloads.zone_operating_mode(new_mode.name),
            )
        else:
            _LOGGER.debug("mode is not available for zone %s", new_mode)

    async def set_zone_cooling_operating_mode(self, zone_id: str, new_mode: OperatingMode) -> None:
        """Set new operating mode to cool a
        :class:`~pymultimatic.model.component.Zone`. The mode should be
        listed here :class:`~pymultimatic.model.component.ZoneCooling.MODES`
        otherwise it won't have any effect.


        Note:
            To set :class:`~pymultimatic.model.mode.QuickMode`, you
            have to use :func:`set_quick_mode`.

        Note:
            This call won't have any effect if there is a
            :class:`~pymultimatic.model.mode.QuickMode` activated, if you
            want to remove the quick mode, use :func:`remove_quick_mode`.

        Note:
            To set :class:`~pymultimatic.model.mode.QuickVeto`, you have to
            use :func:`set_zone_quick_veto`

        Args:
            zone_id (str): id of the zone.
            new_mode (OperatingMode): The new mode to set.
        """
        if new_mode in ZoneCooling.MODES and new_mode != OperatingModes.QUICK_VETO:
            _LOGGER.debug("New mode is %s", new_mode)
            await self._call_api(
                urls.zone_cooling_mode,
                params={"id": zone_id},
                payload=payloads.zone_operating_mode(new_mode.name),
            )
        else:
            _LOGGER.debug("mode is not available for zone %s", new_mode)

    async def remove_zone_quick_veto(self, zone_id: str) -> None:
        """Remove the :class:`~pymultimatic.model.mode.QuickVeto` from a
        :class:`~pymultimatic.model.component.Zone`.

        Args:
            zone_id (str): Id of the zone.
        """
        await self._call_api(urls.zone_quick_veto, "delete", params={"id": zone_id})

    async def set_zone_heating_setpoint_temperature(self, zone_id: str, temperature: float) -> None:
        """Set the configured temperature for the
        :class:`~pymultimatic.model.mode.SettingModes.DAY` mode.

        Note:
            It won't alter the
            :class:`~pymultimatic.model.mode.OperatingMode`.

        Args:
            zone_id (str): Id of the zone.
            temperature (float): New temperature.
        """
        _LOGGER.debug("Will try to set zone target temperature to %s", temperature)

        payload = payloads.zone_temperature_setpoint(self._round(temperature))

        await self._call_api(
            urls.zone_heating_setpoint_temperature,
            params={"id": zone_id},
            payload=payload,
        )

    async def set_zone_cooling_setpoint_temperature(self, zone_id: str, temperature: float) -> None:
        """Set the configured cooling temperature for the
        :class:`~pymultimatic.model.mode.SettingModes.ON` mode.

        Note:
            It won't alter the
            :class:`~pymultimatic.model.mode.OperatingMode`.

        Args:
            zone_id (str): Id of the zone.
            temperature (float): New temperature.
        """
        _LOGGER.debug("Will try to set zone target temperature to %s", temperature)

        payload = payloads.zone_temperature_setpoint(self._round(temperature))

        await self._call_api(
            urls.zone_cooling_setpoint_temperature,
            params={"id": zone_id},
            payload=payload,
        )

    async def set_zone_heating_setback_temperature(self, zone_id: str, temperature: float) -> None:
        """Set the configured heating temperature for the
        :class:`~pymultimatic.model.mode.SettingModes.NIGHT` mode.

        Note:
            It won't alter the
            :class:`~pymultimatic.model.mode.OperatingMode`.

        Args:
            zone_id (str): Id of the zone.
            temperature (float): New temperature.
        """
        _LOGGER.debug("Will try to set zone setback temperature to %s", temperature)

        await self._call_api(
            urls.zone_heating_setback_temperature,
            params={"id": zone_id},
            payload=payloads.zone_temperature_setback(self._round(temperature)),
        )

    async def set_ventilation_operating_mode(
        self, ventilation_id: str, mode: OperatingMode
    ) -> None:
        """Set ventilation operating mode.
         Compatible modes are listed here
         :class:`~pymultimatic.model.Ventilation.MODES`

        Args:
            ventilation_id (str): id of the ventilation
            mode (OperatingMode): Mode to set
        """
        await self._call_api(
            urls.set_ventilation_operating_mode,
            params={"id": ventilation_id},
            payload=payloads.ventilation_operating_mode(mode.name),
        )

    async def set_ventilation_day_level(self, ventilation_id: str, level: int) -> None:
        """Set ventilation day level

        Args:
            ventilation_id (str): id of the ventilation
            level (int): Level between 1 and 6
        """
        await self._call_api(
            urls.set_ventilation_day_level,
            params={"id": ventilation_id},
            payload=payloads.ventilation_level(level),
        )

    async def set_ventilation_night_level(self, ventilation_id: str, level: int) -> None:
        """Set ventilation night level

        Args:
            ventilation_id (str): id of the ventilation
            level (int): Level between 1 and 6
        """
        await self._call_api(
            urls.set_ventilation_night_level,
            params={"id": ventilation_id},
            payload=payloads.ventilation_level(level),
        )

    async def request_hvac_update(self) -> None:
        """Request an hvac update. This allow the vaillant API to read the data from your system.

        This is necessary to update
        :class:`~pymultimatic.model.status.BoilerStatus` and
        :class:`~pymultimatic.model.status.Error`

        Note:
            The **request** done by the manager is done **synchronously**,
            but the **update** processing (basically, reading data from your
            system) is done **asynchronously** by vaillant API.

        Note:
            The manager will try to reduce number of call, I think the call is
            costly. If the
            :class:`~pymultimatic.model.syncstate.SyncState`
            :class:`~pymultimatic.model.syncstate.SyncState.is_pending`,
            the manager will skip the call to the API.


        it can take some times for the update to occur (Most of the
        time, it takes about 1 or 2 minutes before you can see changes, if any)

        It the request is done too often, the API may return an error
        (HTTP 409).

        """

        state = mapper.map_hvac_sync_state(await self._call_api(urls.hvac))

        if state and not state.is_pending:
            await self._call_api(urls.hvac_update, "put")

    @staticmethod
    def _round(number: float) -> float:
        """round a float to the nearest 0.5, as vaillant API only accepts 0.5
        step"""
        return round(number * 2) / 2

    @retry_async(
        on_exceptions=(WrongResponseError,),
        on_status_codes=tuple(range(500, 600)),
        backoff_base=1,
        num_tries=3,
    )
    async def _call_api(
        self,
        url_call: Callable[..., str],
        method: Optional[str] = None,
        schema: Optional[Schema] = None,
        **kwargs: Any,
    ) -> Any:
        await self._ensure_ready()

        params = kwargs.get("params", {})
        params.update({"serial": self._serial})

        payload = kwargs.get("payload", None)

        if method is None:
            method = "get"
            if payload is not None:
                method = "put"

        url = url_call(**params)
        response = await self._connector.request(method, url, payload)
        if schema:
            return await self._validate_schema(schema, response, url)
        return response

    @staticmethod
    async def _validate_schema(schema: Schema, response: Any, url: str) -> Any:
        try:
            return schema.validate(response)
        except SchemaError as err:
            raise WrongResponseError(
                message=f"Cannot validate response from {url}: {err.code}",
                response=response,
                status=200,
            ) from err

    async def _ensure_ready(self) -> None:
        if not await self._connector.is_logged():
            async with self._ensure_ready_lock:
                # double check whether other coroutine has already logged in
                if not await self._connector.is_logged():
                    await self._connector.login()
                    await self._fetch_serial()
        if not self._serial:
            async with self._ensure_ready_lock:
                if not self._serial:
                    await self._fetch_serial()

    async def _fetch_serial(self) -> None:
        if not self._fixed_serial:
            facilities = await self._connector.get(urls.facilities_list())
            self._serial = mapper.map_serial_number(facilities)
