"""Groups everything related to the ventilation."""
import attr

from . import ActiveMode, Component, Function, OperatingModes


@attr.s
class Ventilation(Function, Component):
    """Represent the ventilation."""

    MODES = [OperatingModes.OFF, OperatingModes.NIGHT, OperatingModes.DAY]
    """List of mode that are applicable to ventilation."""

    MAX_LEVEL: float = 6
    """Maximum level for ventilation"""
    MIN_LEVEL: float = 1
    """Minimum level for ventilation"""

    temperature = attr.ib(default=None, init=False)

    def _active_mode(self) -> ActiveMode:
        if self.operating_mode == OperatingModes.OFF:
            mode = ActiveMode(Ventilation.MIN_LEVEL, OperatingModes.OFF)
        elif self.operating_mode == OperatingModes.DAY:
            mode = ActiveMode(self.target_high, OperatingModes.DAY)
        else:  # MODE_NIGHT
            mode = ActiveMode(self.target_low, OperatingModes.NIGHT)
        return mode
