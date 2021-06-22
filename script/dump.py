#!/usr/bin/env python3
import asyncio
import json
import os
import shutil
import sys

import aiohttp


sys.path.append("../")
from pymultimatic.systemmanager import SystemManager
from pymultimatic.api import Connector, ApiError, urls
from pymultimatic.model import mapper

URLS = [

]


async def main(user, passw):
    print('Trying to connect with user ' + user)

    async with aiohttp.ClientSession() as sess:

        shutil.rmtree('./dump_result', ignore_errors=True)
        os.mkdir('./dump_result')

        connector = Connector(user, passw, sess)

        try:
            await connector.login(True)
            print('Login successful')
        except ApiError as err:
            print('Cannot login: ' + await err.response.text())

        facilities = await connector.get(urls.facilities_list())
        serial = mapper.map_serial_number(facilities)

        requests = {}
        for url in URLS:
            print('requesting ' + url.__name__)
            req = connector.get(url(**{'serial': serial}))
            requests.update({url.__name__: req})

        print('did {} requests'.format(len(requests)))

        responses = {}
        for key in requests:
            try:
                responses.update({key: await requests[key]})
            except:
                print('Cannot get response for {}, skipping it'.format(key))

        print('received {} responses'.format(len(responses)))

        for key in responses:
            try:
                with open('./dump_result/{}.json'.format(key), 'w+') as file:
                    data = json.dumps(responses[key])\
                        .replace(serial, 'SERIAL_NUMBER')
                    json.dump(json.loads(data), file, indent=4)
            except:
                print('cannot write to file {}'.format(file.name))

        manager = SystemManager(user, passw, sess)
        print(await manager.get_zones())
        print(await manager.get_gateway())
        print(await manager.get_facility_detail())
        print(await manager.get_holiday_mode())
        print(await manager.get_hvac_status())
        print(await manager.get_live_reports())
        print(await manager.get_outdoor_temperature())
        print(await manager.get_ventilation())
        print(await manager.get_quick_mode())
        print(await manager.get_dhw())
        print(await manager.get_rooms())
        print(await manager.get_live_report('DomesticHotWaterTankTemperature', 'Control_DHW'))
        print(await manager.get_hot_water('Control_DHW'))
        print(await manager.get_room('1'))
        print(await manager.get_zone('Control_ZO1'))
        print(await manager.get_system())
        print(await manager.get_circulation('Control_DHW'))


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print('Usage: python3 dump.py user pass')
        sys.exit(0)
    user = sys.argv[1]
    passw = sys.argv[2]

    asyncio.get_event_loop().run_until_complete(main(user, passw))
