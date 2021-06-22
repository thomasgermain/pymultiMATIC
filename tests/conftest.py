import os
from http.cookies import SimpleCookie
from typing import AsyncGenerator, Optional

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


def mock_auth(resp_mock: aioresponses) -> None:
    resp_mock.post(urls.new_token(), status=200, payload={"body": {"authToken": "123"}})

    resp_mock.post(urls.authenticate(), status=200)

    resp_mock.post(urls.logout(), status=200)


def _room() -> Room:
    timeprogram = _time_program(None, 20)

    return Room(
        id="id",
        name="name",
        time_program=timeprogram,
        target_high=20,
        temperature=20,
        operating_mode=OperatingModes.AUTO,
    )


def _hotwater() -> HotWater:
    timeprogram = _time_program()
    return HotWater(
        id="dhw",
        name="HotWater",
        temperature=38,
        time_program=timeprogram,
        target_high=50,
        operating_mode=OperatingModes.AUTO,
    )


def _zone() -> Zone:
    timeprogram = _time_program(SettingModes.DAY)
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


def _zone_cooling() -> Zone:
    timeprogram = _time_program(SettingModes.ON)
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
    timeprogram = _time_program()
    return Circulation(
        id="dhw",
        name="Circulation",
        time_program=timeprogram,
        operating_mode=OperatingModes.AUTO,
    )


def _time_program(
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


def _ventilation() -> Ventilation:
    timeprogram = _time_program()
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
