import unittest
import inspect
from typing import List, Any, Tuple

from pymultimatic.api import urls


class TestUrls(unittest.TestCase):

    def test_all_urls(self) -> None:
        functions_list = inspect.getmembers(urls, predicate=inspect.isroutine)

        self.assertTrue(len(functions_list) > 0)

        for function in functions_list:
            args_name = self._get_args_name(function[1])

            if not args_name:
                url = function[1]()
                self._assert_function_call(url)
            else:
                args = ['test'] * len(args_name)

                f_kwargs = dict(zip(args_name, args))
                url = function[1](**f_kwargs)
                self._assert_function_call(url)

    # pylint: disable=no-self-use
    def _get_args_name(self, func: Any) -> List[str]:
        names: List[str] = []
        item: Tuple[str, Any]
        for item in inspect.signature(func).parameters.items():
            names.append(item[0])
        return names

    def _assert_function_call(self, url: str) -> None:
        clean_url = url.replace('{serial_number}', '')
        self.assertNotIn('{', clean_url)
        self.assertNotIn('}', clean_url)
