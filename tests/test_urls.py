import inspect
import unittest

from pymultimatic.api import urls, urls_senso


class TestUrls(unittest.TestCase):
    def test_all_urls(self) -> None:
        functions_list = inspect.getmembers(urls, predicate=inspect.isroutine)

        self.assertTrue(len(functions_list) > 0)

        not_called = 0
        for function in functions_list:
            params = inspect.signature(function[1]).parameters.items()
            values = {
                "serial": "123",
                "id": "456",
                "sgtin": "789",
                "device_id": "111",
                "report_id": "222",
            }
            if len(params) > 1:
                values.update(
                    {
                        "energy_type": "type",
                        "function": "func",
                        "time_range": "range",
                        "start": "start",
                        "offset": "offset",
                    }
                )
                not_called += 1

            function[1](**values)

        assert not_called == 1

    def test_all_urls_senso(self) -> None:
        functions_list = inspect.getmembers(urls_senso, predicate=inspect.isroutine)

        self.assertTrue(len(functions_list) > 0)

        not_called = 0
        for function in functions_list:
            params = inspect.signature(function[1]).parameters.items()
            values = {
                "serial": "123",
                "id": "456",
                "sgtin": "789",
                "device_id": "111",
                "report_id": "222",
            }
            if len(params) > 1:
                values.update(
                    {
                        "energy_type": "type",
                        "function": "func",
                        "time_range": "range",
                        "start": "start",
                        "offset": "offset",
                    }
                )
                not_called += 1

            function[1](**values)

        assert not_called == 1
