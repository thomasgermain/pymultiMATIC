"""Information coming from API."""
import attr


@attr.s
class FacilityDetail:
    """Facility information.

    Args:
        name (str): Name of the facility.
        serial_number (str): Serial number of the facility.
        firmware_version (str): Version of the firmware of the facility.
        ethernet_mac (str): Ethernet mac address
        wifi_mac (str): Wifi mac address
    """

    name = attr.ib(type=str)
    serial_number = attr.ib(type=str)
    firmware_version = attr.ib(type=str)
    ethernet_mac = attr.ib(type=str)
    wifi_mac = attr.ib(type=str)
