import os
from datetime import datetime
from http.cookies import SimpleCookie
from typing import AsyncGenerator, Optional, Iterator

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses
from yarl import URL

from pymultimatic.api import Connector, urls
from pymultimatic.model import (
    ActiveFunction,
    Circulation,
    HotWater,
    OperatingModes,
    Room,
    SettingMode,
    SettingModes,
    TimePeriodSetting,
    TimeProgram,
    TimeProgramDay,
    Ventilation,
    Zone,
    ZoneCooling,
    ZoneHeating,
)


@pytest.fixture(autouse=True, name="session")
async def fixture_session() -> AsyncGenerator[ClientSession, None]:
    async with ClientSession() as sess:
        yield sess
        await sess.close()


@pytest.fixture
async def resp(raw_resp: aioresponses) -> AsyncGenerator[aioresponses, None]:
    mock_auth(raw_resp)
    yield raw_resp


@pytest.fixture(name="raw_resp")
async def fixture_raw_resp() -> AsyncGenerator[aioresponses, None]:
    with aioresponses() as aioreponses:
        yield aioreponses
        aioreponses.clear()


@pytest.fixture(autouse=True)
async def connector(session: ClientSession) -> AsyncGenerator[Connector, None]:
    con = Connector("test", "test", session)
    orig_login = con.login

    async def new_login(force: bool = False) -> bool:
        result = await orig_login(force)
        cookie = SimpleCookie()  # type: SimpleCookie[str]
        cookie["test"] = "value"
        cookie["test"]["httponly"] = True
        cookie["test"]["secure"] = True
        cookie["test"]["path"] = "/"
        session.cookie_jar.update_cookies(cookie, URL(urls.authenticate()))
        return result

    setattr(con, "login", new_login)
    yield con


# It's necessary to differentiate the connectors so that they can be launched in the same test.
@pytest.fixture(autouse=True)
async def senso_connector(session: ClientSession) -> AsyncGenerator[Connector, None]:
    con = Connector("test", "test", session)
    orig_login = con.login

    async def new_login(force: bool = False) -> bool:
        result = await orig_login(force)
        cookie = SimpleCookie()  # type: SimpleCookie[str]
        cookie["test"] = "value"
        cookie["test"]["httponly"] = True
        cookie["test"]["secure"] = True
        cookie["test"]["path"] = "/"
        session.cookie_jar.update_cookies(cookie, URL(urls.authenticate()))
        return result

    setattr(con, "login", new_login)
    yield con


def mock_auth(resp_mock: aioresponses) -> None:
    resp_mock.post(urls.new_token(), status=200, payload={"body": {"authToken": "123"}})

    resp_mock.post(urls.authenticate(), status=200)

    resp_mock.post(urls.logout(), status=200)


def _room() -> Room:
    timeprogram = _full_day_time_program(None, 20)

    return Room(
        id="id",
        name="name",
        time_program=timeprogram,
        target_high=20,
        temperature=20,
        operating_mode=OperatingModes.AUTO,
    )


def _hotwater() -> HotWater:
    timeprogram = _full_day_time_program()
    return HotWater(
        id="dhw",
        name="HotWater",
        temperature=38,
        time_program=timeprogram,
        target_high=50,
        operating_mode=OperatingModes.AUTO,
    )


def _zone() -> Zone:
    timeprogram = _full_day_time_program(SettingModes.DAY)
    heating = ZoneHeating(
        time_program=timeprogram,
        operating_mode=OperatingModes.AUTO,
        target_high=25,
        target_low=22,
    )
    return Zone(  # type: ignore
        id="zone",
        name="Zone",
        temperature=22,
        active_function=ActiveFunction.HEATING,
        rbr=False,
        heating=heating,
    )


def _zone_senso(active_period_day: Optional[bool] = True) -> Zone:
    timeprogram = _split_day_time_program(temperature=25, active_period_day=active_period_day)
    heating = ZoneHeating(
        time_program=timeprogram,
        operating_mode=OperatingModes.TIME_CONTROLLED,
        target_low=22,
    )

    return Zone(  # type: ignore
        id="zone",
        name="Zone",
        temperature=22,
        active_function=ActiveFunction.HEATING,
        rbr=False,
        heating=heating,
    )


def _zone_cooling() -> Zone:
    timeprogram = _full_day_time_program(SettingModes.ON)
    cooling = ZoneCooling(
        time_program=timeprogram, operating_mode=OperatingModes.AUTO, target_high=23
    )
    return Zone(  # type: ignore
        id="zone",
        name="Zone",
        temperature=22,
        active_function=ActiveFunction.COOLING,
        rbr=False,
        cooling=cooling,
    )


def _circulation() -> Circulation:
    timeprogram = _full_day_time_program()
    return Circulation(
        id="dhw",
        name="Circulation",
        time_program=timeprogram,
        operating_mode=OperatingModes.AUTO,
    )


def _full_day_time_program(
    mode: Optional[SettingMode] = SettingModes.ON, temperature: Optional[float] = None
) -> TimeProgram:
    if mode in [SettingModes.DAY, SettingModes.NIGHT]:
        timeprogram_day_setting = TimePeriodSetting("00:00", None, mode)
    else:
        timeprogram_day_setting = TimePeriodSetting("00:00", temperature, mode)

    timeprogram_day = TimeProgramDay([timeprogram_day_setting])
    timeprogram_days = {
        "monday": timeprogram_day,
        "tuesday": timeprogram_day,
        "wednesday": timeprogram_day,
        "thursday": timeprogram_day,
        "friday": timeprogram_day,
        "saturday": timeprogram_day,
        "sunday": timeprogram_day,
    }
    return TimeProgram(timeprogram_days)


def _split_day_time_program(
    temperature: Optional[float] = None, active_period_day: Optional[bool] = True
) -> TimeProgram:
    """Creates a time program with the current time encompassed in a period of 3 hours in DAY mode
    if "active_period_day" set to True and Night otherwise.
    """
    current_hour = datetime.now().hour
    if current_hour == 23:
        # To obtain 3 active hours, it is necessary to build 2 periods (22->00, 00->01)
        periods = [
            {"start_time": "00:00", "end_time": "01:00"},
            {"start_time": "22:00", "end_time": "24:00"},
        ]
    elif current_hour == 0:
        # To obtain 3 active hours, it is necessary to build 2 periods (23->00, 00->02)
        periods = [
            {"start_time": "00:00", "end_time": "02:00"},
            {"start_time": "23:00", "end_time": "24:00"},
        ]
    else:
        periods = [
            {"start_time": f"{current_hour-1:02n}:00", "end_time": f"{current_hour + 2:02n}:00"}
        ]

    settings = [
        TimePeriodSetting(
            start_time=period["start_time"],
            target_temperature=temperature,
            setting=SettingModes.DAY if active_period_day else SettingModes.NIGHT,
            end_time=period["end_time"],
        )
        for period in periods
    ]

    timeprogram_day = TimeProgramDay(settings)
    timeprogram_day.complete_empty_periods(
        SettingModes.NIGHT if active_period_day else SettingModes.DAY
    )
    timeprogram_days = {
        day: timeprogram_day
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    }
    return TimeProgram(timeprogram_days)


def _ventilation() -> Ventilation:
    timeprogram = _full_day_time_program()
    ventilation = Ventilation(
        id="fan_id",
        name="Ventilation",
        time_program=timeprogram,
        operating_mode=OperatingModes.AUTO,
        target_high=3,
        target_low=1,
    )
    return ventilation


def path(file: str) -> str:
    return os.path.join(os.path.dirname(__file__), file) + ".json"


def sub_folders(path: str) -> Iterator[str]:
    dirfiles = os.listdir(os.path.join(os.path.dirname(__file__), path))
    fullpaths = (os.path.join(path, name) for name in dirfiles)
    for file in fullpaths:
        if os.path.isdir(file):
            yield file


def senso_responses_folders() -> Iterator[str]:
    return sub_folders("files/responses/senso")


def senso_responses_files_paths(file: str) -> Iterator[str]:
    for folder in senso_responses_folders():
        yield path(os.path.join(folder, file))
