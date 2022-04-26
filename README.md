# pymultiMATIC
![PyPI - License](https://img.shields.io/github/license/thomasgermain/pymultiMATIC)
[![codecov](https://codecov.io/gh/thomasgermain/pymultiMATIC/branch/master/graph/badge.svg?token=KKM0BRHJR7)](https://codecov.io/gh/thomasgermain/pymultiMATIC)
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
This is the low level connector using the vaillant API and returning raw data directly coming from the API (basically, `json` formatted responses). The connector is handling the login and session (cookie based).
There are 2 helper packages for urls and payload: `pymultimatic.api.urls` and `pymultimatic.api.payloads`.

Here is an example on how to use it:
```python
import aiohttp
from pymultimatic.api import Connector, urls, payloads

async with aiohttp.ClientSession() as session:
    connector = Connector('user', 'pass', session)
    # get information about your system
    response = await connector.request('get', urls.system(serial='123'))
    #set the target low heating temperature of a zone to 15 °C
    response = await connector.request('put', urls.zone_heating_setback_temperature(id='1', serial='123'), payload=payloads.zone_temperature_setback(15))
```
Here is an example of response:
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
I would recommend using this layer if you only want to retrieve basic data (outdoor temperature, current temperature of zone, etc.)

#### 2. SystemManager
This layer allows you to interact in a more friendly way with the system and it computes some data for you.
The underlying `Connector` is hidden and raw responses are mapped to more useful objects.


Here is a script example:
```python3
#!/usr/bin/env python3

import asyncio
import sys

import aiohttp

from pymultimatic.systemmanager import SystemManager
from pymultimatic.model import System


async def main(user, passw):
    print('Trying to connect with user ' + user)

    async with aiohttp.ClientSession() as session:
        manager = SystemManager(user, passw, session)
        system =  await manager.get_system()
        print(system)


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print('Usage: python3 dump.py user pass')
        sys.exit(0)
    user = sys.argv[1]
    passw = sys.argv[2]

    asyncio.get_event_loop().run_until_complete(main(user, passw))
```

Then you can run the script:
`python3 script.py user passw`

The main object to manipulate is `pymultimatic.model.System`, which is grouping all the information about your system.

In case of error coming from the API, a `pymultimtic.api.Error` is raised, containing the response and the payload sent to the API.

I would recommend using this layer if you want to do more complex things, e.g: if you want to get the target temperature for 
a room or a zone, it can become a bit complex since you have to deal with holiday mode, quick mode, quick veto, time program, etc.
This layer is hiding you this complexity.

---
<a href="https://www.buymeacoffee.com/tgermain" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
