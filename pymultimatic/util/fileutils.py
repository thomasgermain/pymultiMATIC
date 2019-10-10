"""Some file utilities."""
import logging
import os
import pickle
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger('fileutils')


def load_from_file(path: str, filename: str) -> Any:
    """Load from file."""
    join_path = _join_path(path, filename)
    try:
        with join_path.open("rb") as file:
            return pickle.load(file)

    except (IOError, pickle.PickleError):
        _LOGGER.debug("Cannot open file: %s", join_path, exc_info=True)
        return None


def save_to_file(data: object, path: str, filename: str) -> None:
    """Save to file."""
    join_path = _join_path(path, filename)
    _LOGGER.debug("Will save data to %s", join_path)
    try:
        with join_path.open("wb+") as file:
            pickle.dump(data, file)
    except (IOError, pickle.PickleError):
        _LOGGER.debug("Cannot save data: %s to %s", str(data), join_path,
                      exc_info=True)


def delete_file(path: str, filename: str) -> None:
    """Delete file."""
    join_path = _join_path(path, filename)
    try:
        os.remove(str(join_path))
    except OSError:
        _LOGGER.debug("Cannot delete file %s", join_path, exc_info=True)


def delete_dir(path: str) -> None:
    """Delete directory."""
    try:
        os.rmdir(path)
    except OSError:
        _LOGGER.debug("Cannot delete dir %s", path, exc_info=True)


def _join_path(path: str, filename: str) -> Path:
    """Create path."""
    file_path = Path(path)
    file_path.mkdir(exist_ok=True, parents=True)
    return file_path.joinpath(filename)
