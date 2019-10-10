import json
import os
import tempfile
import uuid
from typing import Optional

from responses import mock as responses  # type: ignore

from pymultimatic.model import TimeProgramDay, TimeProgram, \
    TimePeriodSetting, SettingMode, SettingModes
from pymultimatic.api import urls


def path(file: str) -> str:
    return os.path.join(os.path.dirname(__file__), file)


def temp_path() -> str:
    dir_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    os.mkdir(dir_path)
    return dir_path


def mock_full_auth_success() -> str:
    mock_authentication_success()
    mock_token_success()
    return mock_serial_success()


def mock_token_success() -> None:
    with open(path('files/responses/token'), 'r') as file:
        token_data = json.loads(file.read())

    responses.add(responses.POST, urls.new_token(), json=token_data,
                  status=200)


def mock_authentication_success() -> None:
    responses.add(responses.POST, urls.authenticate(), status=200,
                  headers={
                      "Set-Cookie": "test=value; path=/; Secure; HttpOnly"})


def mock_serial_success() -> str:
    with open(path('files/responses/facilities'), 'r') as file:
        facilities_data = json.loads(file.read())

    responses.add(responses.GET, urls.facilities_list(), json=facilities_data,
                  status=200)

    return str(facilities_data["body"]["facilitiesList"][0]["serialNumber"])


def mock_logout() -> None:
    responses.add(responses.POST, urls.logout(), status=200,
                  headers={"Set-Cookies": ""})


def default_time_program(mode: Optional[SettingMode] = SettingModes.ON,
                         temperature: Optional[float] = None) \
        -> TimeProgram:
    timeprogram_day_setting = TimePeriodSetting('00:00', temperature, mode)

    timeprogram_day = TimeProgramDay([timeprogram_day_setting])
    timeprogram_days = {
        'monday': timeprogram_day,
        'tuesday': timeprogram_day,
        'wednesday': timeprogram_day,
        'thursday': timeprogram_day,
        'friday': timeprogram_day,
        'saturday': timeprogram_day,
        'sunday': timeprogram_day,
    }
    return TimeProgram(timeprogram_days)
