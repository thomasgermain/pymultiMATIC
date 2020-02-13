"""Convenient manager to easily gets data from API."""
import logging
from datetime import date, timedelta
from typing import Optional, List, Callable, Any

from aiohttp import ClientSession

from .api import Connector, urls, payloads, defaults, ApiError
from .model import mapper, System, HotWater, QuickMode, QuickVeto, Room, \
    Zone, OperatingMode, Circulation, OperatingModes, constants

_LOGGER = logging.getLogger('SystemManager')


# pylint: disable=too-many-public-methods
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
        smartphone_id (str): This is required by the API to login.
    """
    # pylint: disable=too-many-arguments
    def __init__(self,
                 user: str,
                 password: str,
                 session: ClientSession,
                 smartphone_id: str = defaults.SMARTPHONE_ID,
                 serial: Optional[str] = None):
        self._connector: Connector = Connector(
            user,
            password,
            session,
            smartphone_id)
        self._serial = serial
        self._fixed_serial = self._serial is not None

    async def login(self, force_login: bool = False) -> bool:
        """Try to login to the API, see
        :func:`~pymultimatic.api.connector.ApiConnector.login`

        Args:
            force_login (bool): Whether the login should be forced or not.

        Returns:
            bool: True/False if authentication succeeded or not.
        """
        return await self._connector.login(force_login)

    # pylint: disable=too-many-locals
    async def get_system(self) -> System:
        """Get the full :class:`~pymultimatic.model.system.System`. It may
        take some times, it actually does multiples API calls, depending on
        your system configuration.

        Returns:
            System: the full system.
        """

        facilities_req = self._call_api(urls.facilities_list)
        full_system_req = self._call_api(urls.system)
        live_report_req = self._call_api(urls.live_report)
        hvac_state_req = self._call_api(urls.hvac)
        gateway_req = self._call_api(urls.gateway_type)

        gateway = await gateway_req
        facilities = await facilities_req
        hvac_state = await hvac_state_req
        system_info = mapper.map_system_info(facilities, gateway, hvac_state)

        boiler_status = mapper.map_boiler_status(hvac_state)
        errors = mapper.map_errors(hvac_state)

        full_system = await full_system_req
        holiday = mapper.map_holiday_mode(full_system)
        zones = mapper.map_zones(full_system)
        outdoor_temp = mapper.map_outdoor_temp(full_system)
        quick_mode = mapper.map_quick_mode(full_system)
        ventilation = mapper.map_ventilation(full_system)

        live_report = await live_report_req
        dhw = mapper.map_dhw(full_system, live_report)
        reports = mapper.map_reports(live_report)

        rooms: List[Room] = []
        if [z for z in zones if z.rbr]:
            rooms_req = self._call_api(urls.rooms)
            rooms_raw = await rooms_req
            rooms = mapper.map_rooms(rooms_raw)

        return System(holiday=holiday,
                      quick_mode=quick_mode,
                      info=system_info,
                      zones=zones,
                      rooms=rooms,
                      dhw=dhw,
                      reports=reports,
                      outdoor_temperature=outdoor_temp,
                      boiler_status=boiler_status,
                      errors=errors,
                      ventilation=ventilation)

    async def get_hot_water(self, dhw_id: str) -> Optional[HotWater]:
        """Get the :class:`~pymultimatic.model.component.HotWater`
        information for the given id.

        Args:
            dhw_id (str): domestic hot water id (same as
                :func:`get_circulation`).

        Returns:
            HotWater: the hot water information, if any.
        """
        dhw_req = self._call_api(urls.hot_water,
                                 params={'id': dhw_id})
        lv_req = self._call_api(urls.live_report)

        report = await lv_req
        dhw = await dhw_req
        return mapper.map_hot_water_alone(dhw, dhw_id, report)

    async def get_room(self, room_id: str) -> Optional[Room]:
        """Get the :class:`~pymultimatic.model.component.Room` information
        for the given id.

        Args:
            room_id (str): Id of the room, this is actually an index, 1,2,3,4
            ... depending of the number of rooms you have.

        Returns:
            Room: the room information, if any.
        """
        new_room = await self._call_api(urls.room, params={'id': room_id})
        return mapper.map_room(new_room)

    async def get_zone(self, zone_id: str) -> Optional[Zone]:
        """"Get the :class:`~pymultimatic.model.component.Zone` information
        for the given id.

        Args:
            zone_id (str): Name of the room, basically, you set it through the
                VRC 700.

        Returns:
            Zone: the zone information, if any.
        """
        new_zone = await self._call_api(urls.zone, params={'id': zone_id})
        return mapper.map_zone(new_zone)

    async def get_circulation(self, dhw_id: str) -> Optional[Circulation]:
        """"Get the :class:`~pymultimatic.model.component.Circulation`
        information for the given id.

        Args:
            dhw_id (str): domestic hot water id (same as :func:`get_hot_water`)

        Returns:
            Circulation: the circulation information, if any.
        """
        new_circulation = await self._call_api(urls.circulation,
                                               params={'id': dhw_id})
        return mapper.map_circulation_alone(new_circulation, dhw_id)

    async def set_hot_water_setpoint_temperature(self, dhw_id: str,
                                                 temperature: float) -> None:
        """This set the target temperature for *hot water*."""
        _LOGGER.debug("Will set dhw target temperature to %s", temperature)

        payload = payloads \
            .hotwater_temperature_setpoint(self._round(temperature))

        await self._call_api(
            urls.hot_water_temperature_setpoint,
            params={'id': dhw_id},
            payload=payload
        )

    async def set_hot_water_operating_mode(self, dhw_id: str,
                                           new_mode: OperatingMode) -> None:
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
                params={'id': dhw_id},
                payload=payloads.hot_water_operating_mode(new_mode.name)
            )
        else:
            _LOGGER.debug("New mode is not available for hot water %s",
                          new_mode)

    async def set_room_operating_mode(self, room_id: str,
                                      new_mode: OperatingMode) -> None:
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
                params={'id': room_id},
                payload=payloads.room_operating_mode(new_mode.name)
            )
        else:
            _LOGGER.debug("mode is not available for room %s", new_mode)

    async def set_zone_operating_mode(self, zone_id: str,
                                      new_mode: OperatingMode) -> None:
        """Set new operating mode for
        :class:`~pymultimatic.model.component.Zone`. The mode should be
        listed here :class:`~pymultimatic.model.component.Zone.MODES`
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
        if new_mode in Zone.MODES and new_mode != OperatingModes.QUICK_VETO:
            _LOGGER.debug("New mode is %s", new_mode)
            await self._call_api(
                urls.zone_heating_mode,
                params={'id': zone_id},
                payload=payloads.zone_operating_mode(new_mode.name)
            )
        else:
            _LOGGER.debug("mode is not available for zone %s", new_mode)

    async def set_quick_mode(self, quick_mode: QuickMode) -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickMode` system wise.

        This will override the current
        :class:`~pymultimatic.model.mode.QuickMode`, if any.

        Args:
            quick_mode (QuickMode): the quick mode to set, see
                :class:`~pymultimatic.model.mode.QuickModes`
        """
        await self._call_api(
            urls.system_quickmode,
            payload=payloads.quickmode(quick_mode.name)
        )

    async def remove_quick_mode(self) -> None:
        """Removes current :class:`~pymultimatic.model.mode.QuickMode`.

        Note:
            if there is not :class:`~pymultimatic.model.mode.QuickMode` set,
            the API returns an error (HTTP 409). **This error is swallowed by
            the manager**, so you don't have to handle it."""
        try:
            await self._call_api(urls.system_quickmode, 'delete')
        except ApiError as exc:
            if exc.response is None or exc.response.status != 409:
                raise exc

    async def set_room_quick_veto(self, room_id: str,
                                  quick_veto: QuickVeto) -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickVeto` for a
        :class:`~pymultimatic.model.component.Room`.
        It will override the current
        :class:`~pymultimatic.model.mode.QuickVeto`, if any.

        Args:
            room_id (str): Id of the room.
            quick_veto (QuickVeto): Quick veto to set.
        """
        payload = payloads.room_quick_veto(
            self._round(quick_veto.target),
            quick_veto.duration
        )
        await self._call_api(
            urls.room_quick_veto,
            params={'id': room_id},
            payload=payload
        )

    async def remove_room_quick_veto(self, room_id: str) -> None:
        """Remove the :class:`~pymultimatic.model.mode.QuickVeto` from a
        :class:`~pymultimatic.model.component.Room`.

        Args:
            room_id (str): Id of the room.
        """

        await self._call_api(
            urls.room_quick_veto,
            'delete',
            params={'id': room_id}
        )

    async def set_zone_quick_veto(self, zone_id: str, quick_veto: QuickVeto) \
            -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickVeto` for a
        :class:`~pymultimatic.model.component.Zone`.
        It will override the current
        :class:`~pymultimatic.model.mode.QuickVeto`, if any.

        Args:
            zone_id (str): Id of the zone.
            quick_veto (QuickVeto): Quick veto to set.
        """
        payload = payloads.zone_quick_veto(
            self._round(quick_veto.target))

        await self._call_api(
            urls.zone_quick_veto,
            params={'id': zone_id},
            payload=payload
        )

    async def remove_zone_quick_veto(self, zone_id: str) -> None:
        """Remove the :class:`~pymultimatic.model.mode.QuickVeto` from a
        :class:`~pymultimatic.model.component.Zone`.

        Args:
            zone_id (str): Id of the zone.
        """
        await self._call_api(
            urls.zone_quick_veto,
            'delete',
            params={'id': zone_id}
        )

    async def set_room_setpoint_temperature(self, room_id: str,
                                            temperature: float) -> None:
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

        _LOGGER.debug("Will try to set room target temperature to %s",
                      temperature)

        await self._call_api(
            urls.room_temperature_setpoint,
            params={'id': room_id},
            payload=payloads.room_temperature_setpoint(
                self._round(temperature))
        )

    async def set_zone_setpoint_temperature(self, zone_id: str,
                                            temperature: float) -> None:
        """Set the configured temperature for the
        :class:`~pymultimatic.model.mode.SettingModes.DAY` mode.

        Note:
            It won't alter the
            :class:`~pymultimatic.model.mode.OperatingMode`.

        Args:
            zone_id (str): Id of the zone.
            temperature (float): New temperature.
        """
        _LOGGER.debug("Will try to set zone target temperature to %s",
                      temperature)

        payload = payloads.zone_temperature_setpoint(self._round(temperature))

        await self._call_api(
            urls.zone_heating_setpoint_temperature,
            params={'id': zone_id},
            payload=payload
        )

    async def set_zone_setback_temperature(self, zone_id: str,
                                           temperature: float) -> None:
        """Set the configured temperature for the
        :class:`~pymultimatic.model.mode.SettingModes.NIGHT` mode.

        Note:
            It won't alter the
            :class:`~pymultimatic.model.mode.OperatingMode`.

        Args:
            zone_id (str): Id of the zone.
            temperature (float): New temperature.
        """
        _LOGGER.debug("Will try to set zone setback temperature to %s",
                      temperature)

        await self._call_api(
            urls.zone_heating_setback_temperature,
            params={'id': zone_id},
            payload=payloads.zone_temperature_setback(self._round(temperature))
        )

    async def set_holiday_mode(self, start_date: date, end_date: date,
                               temperature: float) -> None:
        """Set the :class:`~pymultimatic.model.mode.HolidayMode`.

        Args:
            start_date (date): Start date of the holiday mode.
            end_date (date): End date of the holiday mode.
            temperature (float): Target temperature while holiday mode
                :class:`~pymultimatic.model.mode.HolidayMode.is_applied`
        """
        payload = payloads.holiday_mode(
            True,
            start_date,
            end_date,
            self._round(temperature)
        )

        await self._call_api(
            urls.system_holiday_mode,
            payload=payload
        )

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
            constants.FROST_PROTECTION_TEMP
        )

        await self._call_api(
            urls.system_holiday_mode,
            payload=payload
        )

    async def request_hvac_update(self) -> None:
        """Request an hvac update. This allow the vaillant API to read the data
        from your system.

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
            await self._call_api(urls.hvac_update, 'put')

    async def logout(self) -> None:
        """Get logged out from the API, see
        :func:`~pymultimatic.api.connector.ApiConnector.logout`
        """
        if not self._fixed_serial:
            self._serial = None
        await self._connector.logout()

    # pylint: disable=no-self-use
    def _round(self, number: float) -> float:
        """round a float to the nearest 0.5, as vaillant API only accepts 0.5
        step"""
        return round(number * 2) / 2

    async def _call_api(self,
                        url_call: Callable[..., str],
                        method: Optional[str] = None,
                        **kwargs: Any) -> Any:
        await self._ensure_ready()

        params = kwargs.get('params', {})
        params.update({'serial': self._serial})

        payload = kwargs.get('payload', None)

        if method is None:
            method = 'get'
            if payload is not None:
                method = 'put'

        url = url_call(**params)
        return await self._connector.request(method, url, payload)

    async def _ensure_ready(self) -> None:
        if not await self._connector.is_logged():
            await self._connector.login()
            await self._fetch_serial()
        if not self._serial:
            await self._fetch_serial()

    async def _fetch_serial(self) -> None:
        if not self._fixed_serial:
            facilities = await self._connector.get(urls.facilities_list())
            self._serial = mapper.map_serial_number(facilities)
