"""Tests for boiler status."""
import json
import unittest

from schema import SchemaError

from pymultimatic.api import schemas
from tests.conftest import path


class SchemaTest(unittest.TestCase):
    """Test class."""

    def test_schema_system_validation(self) -> None:
        """Ensure schema validation doesn't alter the response"""
        my_path = 'files/responses/'

        files = ['systemcontrol', 'systemcontrol_holiday', 'systemcontrol_hotwater_boost',
                 'systemcontrol_no_outside_temp', 'systemcontrol_off', 'systemcontrol_quick_veto',
                 'systemcontrol_ventilation', 'systemcontrol_zone_no_config_rbr']

        for file in files:
            with open(path(my_path + file), 'r') as open_f:
                json_val = json.loads(open_f.read())
                result = schemas.SYSTEM.validate(json_val)
                json_val.pop('meta')
                json_val.get('body').pop('parameters')
                self.assertDictEqual(result, json_val, 'error for ' + file)

    def test_schema_system_validation_error(self) -> None:
        """Ensure validation fails."""
        with open(path('files/responses/systemcontrol_zone_no_config'), 'r') as open_f:
            json_val = json.loads(open_f.read())
            try:
                schemas.SYSTEM.validate(json_val)
            except SchemaError as err:
                self.assertIn("Missing key: 'configuration'", err.args[0])

    def test_schema_livereport_validation(self) -> None:
        """Ensure schema validation doesn't alter the response"""
        my_path = 'files/responses/'
        files = ['livereport', 'livereport_FlowTemperatureVF1']

        for file in files:
            with open(path(my_path + file), 'r') as open_f:
                json_val = json.loads(open_f.read())
                result = schemas.LIVE_REPORT.validate(json_val)
                json_val.pop('meta')
                self.assertDictEqual(result, json_val, 'error for ' + file)

    def test_schema_hvac_validation(self) -> None:
        """Ensure schema validation doesn't alter the response"""
        my_path = 'files/responses/'

        files = ['hvacstate', 'hvacstate_empty', 'hvacstate_errors', 'hvacstate_pending']

        for file in files:
            with open(path(my_path + file), 'r') as open_f:
                json_val = json.loads(open_f.read())
                result = schemas.HVAC.validate(json_val)
                json_val.get('meta').pop('syncState')
                self.assertDictEqual(result, json_val, 'error for ' + file)

    def test_schema_facilities_validation(self) -> None:
        """Ensure schema validation doesn't alter the response"""
        my_path = 'files/responses/'

        files = ['facilities', 'facilities_multiple']

        for file in files:
            with open(path(my_path + file), 'r') as open_f:
                json_val = json.loads(open_f.read())
                result = schemas.FACILITIES.validate(json_val)
                json_val.pop('meta')
                self.assertDictEqual(result, json_val, 'error for ' + file)

    def test_schema_zone_validation(self) -> None:
        """Ensure schema validation doesn't alter the response"""
        my_path = 'files/responses/'

        files = ['zone', 'zone_always_off', 'zone_always_on',
                 'zone_no_active_function', 'zone_no_quickveto']

        for file in files:
            with open(path(my_path + file), 'r') as open_f:
                json_val = json.loads(open_f.read())
                result = schemas.ZONE.validate(json_val)
                json_val.pop('meta')
                self.assertDictEqual(result, json_val, 'error for ' + file)

    def test_schema_zones_validation(self) -> None:
        """Ensure schema validation doesn't alter the response"""
        my_path = 'files/responses/'

        files = ['zones']

        for file in files:
            with open(path(my_path + file), 'r') as open_f:
                json_val = json.loads(open_f.read())
                result = schemas.ZONE_LIST.validate(json_val)
                json_val.pop('meta')
                self.assertDictEqual(result, json_val, 'error for ' + file)

    def test_schema_rooms_validation(self) -> None:
        """Ensure schema validation doesn't alter the response"""
        my_path = 'files/responses/'

        files = ['rooms', 'rooms_quick_veto']

        for file in files:
            with open(path(my_path + file), 'r') as open_f:
                json_val = json.loads(open_f.read())
                result = schemas.ROOM_LIST.validate(json_val)
                json_val.pop('meta')
                self.assertDictEqual(result, json_val, 'error for ' + file)
