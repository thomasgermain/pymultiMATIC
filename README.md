# pymultiMATIC
![PyPI - License](https://img.shields.io/github/license/thomasgermain/pymultiMATIC)
[![Build Status](https://travis-ci.org/thomasgermain/pymultiMATIC.svg?branch=master)](https://travis-ci.org/thomasgermain/pymultiMATIC)
[![Coverage Status](https://coveralls.io/repos/github/thomasgermain/pymultiMATIC/badge.svg?branch=master)](https://coveralls.io/github/thomasgermain/pymultiMATIC?branch=master)
![PyPI](https://img.shields.io/pypi/v/pymultiMATIC)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pymultiMATIC.svg)

## Legal Disclaimer
This software is not affiliated with Vaillant and the developers take no legal responsibility for the functionality or security of your vaillant devices.

## Install
```bash
[sudo] pip3 install pymultimatic 
```

## Tests
You can run tests with
```bash
pytest
```

## Usages

### Module usage
 
The project is separated in two layers:

#### 1. ApiConnector
This is the low level connector using the vaillant API and returning raw data directly coming from the API (basically, `json` formatted responses. The connector is handling the login and session.
The connector able to reuse an already existing session (cookies). Two files are saved (cookies and serial number of your installation) on the file system. Default location is:
`~/.pymultimatic` but it can be overridden. Files are named `.cookies` and `.serial`.


Here is an example how to use it:
```python
from pymultimatic.api import Connector, urls

session = ...  # aiohttp.ClientSession
connector = Connector('user', 'pass', session)
json = await connector.get(urls.facilities_list()) 
```
to get some information about your installation, this returns the raw response, something like this:
```json
{
    "body": {
        "facilitiesList": [
            {
                "serialNumber": "1234567891234567891234567890",
                "name": "Name",
                "responsibleCountryCode": "BE",
                "supportedBrand": "GREEN_BRAND_COMPATIBLE",
                "capabilities": [
                    "ROOM_BY_ROOM",
                    "SYSTEMCONTROL_MULTIMATIC"
                ],
                "networkInformation": {
                    "macAddressEthernet": "12:34:56:78:9A:BC",
                    "macAddressWifiAccessPoint": "34:56:78:9A:BC:DE",
                    "macAddressWifiClient": "56:78:9A:BC:DE:F0"
                },
                "firmwareVersion": "1.1.1"
            }
        ]
    },
    "meta": {}
}
```

Basically, you can use 
```python
from pymultimatic.api import Connector, urls
   
connector = Connector('user', 'pass')
connector.request('get', urls.system(serial='123')) 
```
with urls from `pymultimatic.api.urls`

I would recommend using this layer if you only want to retrieve basic data (outdoor temperature, current temperature, etc.)

#### 2. SystemManager
This layer allows you to interact in a more friendly way with the system and compute some data for you.
The underlying `Connector` is hidden and raw responses are mapped to more useful objects.


Here is an example:
```python
from pymultimatic.systemmanager import SystemManager
from pymultimatic.model import OperatingModes

session = ...  # aiohttp.ClientSession 
manager = SystemManager('user', 'pass', session)

# get the complete system
system = await manager.get_system()

# set the hot water target temperature to 55
await manager.set_hot_water_setpoint_temperature('dhw_id', 55)

# set the zone operation mode to 'AUTO'
await manager.set_zone_heating_operating_mode('zone_id', OperatingModes.AUTO)
```

The main object to manipulate is `pymultimatic.model.System`, which is grouping all the information about your system.

I would recommend using this layer if you want to do more complex things, e.g: if you want to get the target temperature for 
a room or a zone, it can become a bit complex since you have to deal with holiday mode, quick mode, quick veto, time program, etc.
This layer is hiding you  this complexity.

## Documentation
You can find a deeper documentation [here](https://thomasgermain.github.io/pymultiMATIC/).

## Todo's
- Handling ventilation
- Moving some constructors (System) to **kwargs