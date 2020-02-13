"""Groups everything related to the ventilation."""
import attr

from . import Component, Function, ActiveMode, OperatingModes


@attr.s
class Ventilation(Function, Component):
    """Represent the ventilation."""

    temperature = attr.ib(default=None, init=False)

    def _active_mode(self) -> ActiveMode:
        if self.operating_mode == OperatingModes.OFF:
            mode = ActiveMode(1, OperatingModes.OFF)
        elif self.operating_mode == OperatingModes.DAY:
            mode = ActiveMode(self.target_high, OperatingModes.DAY)
        else:  # MODE_NIGHT
            mode = ActiveMode(self.target_low, OperatingModes.NIGHT)
        return mode
