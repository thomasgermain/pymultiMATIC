"""Test for fileutils"""
import os
import pickle
import unittest
from unittest.mock import Mock, patch

from tests import testutil
from pymultimatic.util import fileutils


class FileUtilsTest(unittest.TestCase):
    """Test class."""

    def test_load_from_file_not_exists(self) -> None:
        """Test load non-existing file."""
        path = testutil.temp_path()
        result = fileutils.load_from_file(path, 'test_load_from_file.txt')
        self.assertIsNone(result)

    def test_load_from_file_exists(self) -> None:
        """Test load existing file."""
        path = testutil.temp_path()
        file = 'test_load_from_file.txt'
        data = bytes('test data', 'utf-8')

        with open(path + '/' + file, 'wb+') as opened:
            pickle.dump(data, opened)

        result = fileutils.load_from_file(path, file)
        self.assertEqual(data, result)

    def test_save_to_file_exists(self) -> None:
        """Test save to an existing file."""
        path = testutil.temp_path()
        file = 'test_save_to_file.txt'
        data = bytes('test data', 'utf-8')

        with open(path + '/' + file, 'wb+'):
            pass

        fileutils.save_to_file(data, path, file)

        with open(path + '/' + file, 'rb') as opened:
            self.assertEqual(data, pickle.load(opened))

    def test_save_to_file_not_exists(self) -> None:
        """Test save to a non-existing file."""
        path = testutil.temp_path()
        file = 'test_save_to_file.txt'
        data = bytes('test data', 'utf-8')

        fileutils.save_to_file(data, path, file)

        with open(path + '/' + file, 'rb') as opened:
            self.assertEqual(data, pickle.load(opened))

    @patch.object(pickle, 'dump')
    def test_save_to_file_no_error_on_exception(self, mock_dump: Mock) -> None:
        """Test save error."""
        path = testutil.temp_path()
        file = 'test_save_to_file.txt'
        data = bytes('test data', 'utf-8')

        mock_dump.side_effect = OSError('Test exception')

        fileutils.save_to_file(data, path, file)

        self.assertEqual(0, os.stat(os.path.join(path, file)).st_size)

    def test_delete_dir(self) -> None:
        """Test delete dir."""
        path = testutil.temp_path()
        self.assertTrue(os.path.exists(path))
        fileutils.delete_dir(path)
        self.assertFalse(os.path.exists(path))

    def test_delete_dir_exception(self) -> None:
        """Test delete dir error."""
        path = testutil.temp_path()
        self.assertTrue(os.path.exists(path))
        os.rmdir = Mock(side_effect=OSError('Test exception'))
        fileutils.delete_dir(path)
        self.assertTrue(os.path.exists(path))
