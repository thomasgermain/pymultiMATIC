"""Test for payloads"""
import inspect
import json
import unittest
from datetime import date, datetime
from typing import Any, Dict, Union

from pymultimatic.api import payloads, payloads_senso


class PayloadsTest(unittest.TestCase):
    """Test class."""

    def test_all_payload(self) -> None:
        """Test that ensure all payload are well json formatted."""
        functions_list = inspect.getmembers(payloads, predicate=inspect.isfunction)

        self.assertTrue(len(functions_list) > 0)

        for function in functions_list:
            args = self._get_args_name(function[1])

            if not args:
                url = function[1]()
                self._assert_function_call(url)
            else:
                payload = function[1](**args)
                self._assert_function_call(payload)

        payload = payloads.room_quick_veto(15, None)
        self._assert_function_call(payload)
        assert payload["duration"] == 180

    def test_all_payload_senso(self) -> None:
        """Test that ensure all payload senso are well json formatted."""
        functions_list = inspect.getmembers(payloads_senso, predicate=inspect.isfunction)

        self.assertTrue(len(functions_list) > 0)

        for function in functions_list:
            args = self._get_args_name(function[1])

            if not args:
                url = function[1]()
                self._assert_function_call(url)
            else:
                payload = function[1](**args)
                self._assert_function_call(payload)

        payload = payloads_senso.room_quick_veto(15, None)
        self._assert_function_call(payload)
        assert payload["duration"] == 180

    def _get_args_name(self, function: Any) -> Dict[str, Any]:
        args: Dict[str, Any] = {}
        params = inspect.signature(function).parameters

        for item in inspect.signature(function).parameters.items():
            cls = params[item[0]].annotation

            if cls == bool:
                args[item[0]] = False
            elif cls == float:
                args[item[0]] = 10.0
            elif cls == Union[float, None]:
                args[item[0]] = 10.0
            elif cls == date:
                args[item[0]] = datetime.now()
            elif cls == str:
                args[item[0]] = "test"
            elif cls == int:
                args[item[0]] = 10
            elif cls == Union[int, None]:
                args[item[0]] = 10
            else:
                self.fail("Unhandled class " + cls.__name__)

        return args

    def _assert_function_call(self, result: Any) -> Any:
        json.loads(json.dumps(result))
