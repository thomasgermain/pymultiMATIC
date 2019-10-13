"""Convenient manager to easily gets data from API."""
import logging
from datetime import date, timedelta
from typing import Optional, List

from .api import ApiConnector, urls, payloads, defaults, ApiError
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
        file_path: (str): Path where cookie is/will be stored.
    """

    def __init__(self, user: str, password: str,
                 smartphone_id: str = defaults.SMARTPHONE_ID,
                 file_path: str = defaults.FILES_PATH):
        self._connector: ApiConnector = \
            ApiConnector(user, password, smartphone_id, file_path)

    def login(self, force_login: bool = False) -> bool:
        """Try to login to the API, see
        :func:`~pymultimatic.api.connector.ApiConnector.login`

        Args:
            force_login (bool): Whether the login should be forced or not.

        Returns:
            bool: True/False if authentication succeeded or not.
        """
        return self._connector.login(force_login)

    # pylint: disable=too-many-locals
    def get_system(self) -> System:
        """Get the full :class:`~pymultimatic.model.system.System`. It may
        take some times, it actually does 3 or 4 API calls, depending on your
        system configuration.

        Returns:
            System: the full system.
        """
        full_system = self._connector.get(urls.system())
        live_report = self._connector.get(urls.live_report())
        hvac_state = self._connector.get(urls.hvac())

        holiday_mode = mapper.map_holiday_mode(full_system)
        boiler_status = mapper.map_boiler_status(hvac_state, live_report)
        system_status = mapper.map_system_status(hvac_state)

        zones = mapper.map_zones(full_system)

        rooms: List[Room] = []
        for zone in zones:
            if zone.rbr:
                rooms = mapper.map_rooms(self._connector.get(urls.rooms()))
                break

        hot_water = mapper.map_hot_water(full_system, live_report)
        circulation = mapper.map_circulation(full_system)

        outdoor_temp = mapper.map_outdoor_temp(full_system)
        quick_mode = mapper.map_quick_mode(full_system)
        errors = mapper.map_errors(hvac_state)

        return System(holiday_mode, system_status, boiler_status, zones, rooms,
                      hot_water, circulation, outdoor_temp, quick_mode, errors)

    def get_hot_water(self, dhw_id: str) -> Optional[HotWater]:
        """Get the :class:`~pymultimatic.model.component.HotWater`
        information for the given id.

        Args:
            dhw_id (str): domestic hot water id (same as
                :func:`get_circulation`).

        Returns:
            HotWater: the hot water information, if any.
        """

        full_system = self._connector.get(urls.hot_water(dhw_id))
        live_report = self._connector.get(urls.live_report())
        return mapper.map_hot_water_alone(full_system, dhw_id, live_report)

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get the :class:`~pymultimatic.model.component.Room` information
        for the given id.

        Args:
            room_id (str): Id of the room, this is actually an index, 1,2,3,4
            ... depending of the number of rooms you have.

        Returns:
            Room: the room information, if any.
        """
        new_room = self._connector.get(urls.room(room_id))
        return mapper.map_room(new_room)

    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """"Get the :class:`~pymultimatic.model.component.Zone` information
        for the given id.

        Args:
            zone_id (str): Name of the room, basically, you set it through the
                VRC 700.

        Returns:
            Zone: the zone information, if any.
        """
        new_zone = self._connector.get(urls.zone(zone_id))
        return mapper.map_zone(new_zone)

    def get_circulation(self, dhw_id: str) \
            -> Optional[Circulation]:
        """"Get the :class:`~pymultimatic.model.component.Circulation`
        information for the given id.

        Args:
            dhw_id (str): domestic hot water id (same as :func:`get_hot_water`)

        Returns:
            Circulation: the circulation information, if any.
        """
        new_circulation = self._connector.get(urls.circulation(dhw_id))
        return mapper.map_circulation_alone(new_circulation, dhw_id)

    def set_hot_water_setpoint_temperature(self, dhw_id: str,
                                           temperature: float) -> None:
        """This set the target temperature for *hot water*."""
        _LOGGER.debug("Will set dhw target temperature to %s",
                      temperature)
        self._connector.put(
            urls.hot_water_temperature_setpoint(dhw_id),
            payloads.hotwater_temperature_setpoint(self._round(temperature)))

    def set_hot_water_operating_mode(self, dhw_id: str,
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
            self._connector.put(
                urls.hot_water_operating_mode(dhw_id),
                payloads.hot_water_operating_mode(new_mode.name))
        else:
            _LOGGER.debug("New mode is not available for hot water %s",
                          new_mode)

    def set_room_operating_mode(self, room_id: str, new_mode: OperatingMode) \
            -> None:
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
            self._connector.put(urls.room_operating_mode(room_id),
                                payloads.room_operating_mode(
                                    new_mode.name))
        else:
            _LOGGER.debug("mode is not available for room %s", new_mode)

    def set_zone_operating_mode(self, zone_id: str, new_mode: OperatingMode) \
            -> None:
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
            self._connector.put(urls.zone_heating_mode(zone_id),
                                payloads.zone_operating_mode(new_mode.name))
        else:
            _LOGGER.debug("mode is not available for zone %s", new_mode)

    def set_quick_mode(self, quick_mode: QuickMode) -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickMode` system wise.

        This will override the current
        :class:`~pymultimatic.model.mode.QuickMode`, if any.

        Args:
            quick_mode (QuickMode): the quick mode to set, see
                :class:`~pymultimatic.model.mode.QuickModes`
        """
        self._connector.put(urls.system_quickmode(),
                            payloads.quickmode(quick_mode.name))

    def remove_quick_mode(self) -> None:
        """Removes current :class:`~pymultimatic.model.mode.QuickMode`.

        Note:
            if there is not :class:`~pymultimatic.model.mode.QuickMode` set,
            the API returns an error (HTTP 409). **This error is swallowed by
            the manager**, so you don't have to handle it."""
        try:
            self._connector.delete(urls.system_quickmode())
        except ApiError as exc:
            if exc.response is None or exc.response.status_code != 409:
                raise exc

    def set_room_quick_veto(self, room_id: str, quick_veto: QuickVeto) -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickVeto` for a
        :class:`~pymultimatic.model.component.Room`.
        It will override the current
        :class:`~pymultimatic.model.mode.QuickVeto`, if any.

        Args:
            room_id (str): Id of the room.
            quick_veto (QuickVeto): Quick veto to set.
        """
        self._connector.put(urls.room_quick_veto(room_id),
                            payloads.room_quick_veto(
                                quick_veto.target_temperature,
                                quick_veto.remaining_duration))

    def remove_room_quick_veto(self, room_id: str) -> None:
        """Remove the :class:`~pymultimatic.model.mode.QuickVeto` from a
        :class:`~pymultimatic.model.component.Room`.

        Args:
            room_id (str): Id of the room.
        """
        self._connector.delete(urls.room_quick_veto(room_id))

    def set_zone_quick_veto(self, zone_id: str, quick_veto: QuickVeto) -> None:
        """Set a :class:`~pymultimatic.model.mode.QuickVeto` for a
        :class:`~pymultimatic.model.component.Zone`.
        It will override the current
        :class:`~pymultimatic.model.mode.QuickVeto`, if any.

        Args:
            zone_id (str): Id of the zone.
            quick_veto (QuickVeto): Quick veto to set.
        """
        self._connector.put(urls.zone_quick_veto(zone_id),
                            payloads.zone_quick_veto(
                                quick_veto.target_temperature))

    def remove_zone_quick_veto(self, zone_id: str) -> None:
        """Remove the :class:`~pymultimatic.model.mode.QuickVeto` from a
        :class:`~pymultimatic.model.component.Zone`.

        Args:
            zone_id (str): Id of the zone.
        """
        self._connector.delete(urls.zone_quick_veto(zone_id))

    def set_room_setpoint_temperature(self, room_id: str, temperature: float) \
            -> None:
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
        self._connector.put(urls.room_temperature_setpoint(room_id),
                            payloads.room_temperature_setpoint(
                                self._round(temperature)))

    def set_zone_setpoint_temperature(self, zone_id: str, temperature: float) \
            -> None:
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
        self._connector.put(
            urls.zone_heating_setpoint_temperature(zone_id),
            payloads.zone_temperature_setpoint(self._round(temperature)))

    def set_zone_setback_temperature(self, zone_id: str, temperature: float) \
            -> None:
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
        self._connector.put(urls.zone_heating_setback_temperature(zone_id),
                            payloads.zone_temperature_setback(
                                self._round(temperature)))

    def set_holiday_mode(self, start_date: date, end_date: date,
                         temperature: float) -> None:
        """Set the :class:`~pymultimatic.model.mode.HolidayMode`.

        Args:
            start_date (date): Start date of the holiday mode.
            end_date (date): End date of the holiday mode.
            temperature (float): Target temperature while holiday mode
                :class:`~pymultimatic.model.mode.HolidayMode.is_applied`
        """
        self._connector.put(urls.system_holiday_mode(),
                            payloads.holiday_mode(True, start_date, end_date,
                                                  temperature))

    def remove_holiday_mode(self) -> None:
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

        start_date = date.today() - timedelta(days=2)
        end_date = date.today() - timedelta(days=1)
        payload = payloads.holiday_mode(False, start_date, end_date,
                                        constants.FROST_PROTECTION_TEMP)
        self._connector.put(urls.system_holiday_mode(), payload)

    def request_hvac_update(self) -> None:
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

        state = mapper.map_hvac_sync_state(self._connector.get(urls.hvac()))

        if state and not state.is_pending:
            self._connector.put(urls.hvac_update())

    def logout(self) -> None:
        """Get logged out from the API, see
        :func:`~pymultimatic.api.connector.ApiConnector.logout`
        """
        self._connector.logout()

    # pylint: disable=no-self-use
    def _round(self, number: float) -> float:
        """round a float to the nearest 0.5, as vaillant API only accepts 0.5
        step"""
        return round(number * 2) / 2
