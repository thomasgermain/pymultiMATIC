#!/usr/bin/env python3
import asyncio
import json
import os
import shutil
import sys

import aiohttp


sys.path.append("../")
from pymultimatic.api import defaults, Connector, ApiError, urls, urls_senso
from pymultimatic.model import mapper

url_class_map = {defaults.SENSO: urls_senso, defaults.MULTIMATIC: urls}

URLS = {
    "zones": {},
    "gateway_type": {},
    "facilities_details": {},
    "facilities_list": {},
    "system_holiday_mode": {},
    "hvac": {},
    "live_report": {},
    "system_status": {},
    "system_quickmode": {},
    "system_configuration": {},
    "dhws": {},
    "dhw": {"id": "Control_DHW"},
    "emf_devices": {},
    "circulation": {},
    "rooms": {},
    "system": {},
    "system_ventilation": {},
}


async def main(user, passw):
    print("Trying to connect with user " + user)

    async with aiohttp.ClientSession() as sess:

        shutil.rmtree("./dump_result", ignore_errors=True)
        os.mkdir("./dump_result")

        connector = Connector(user, passw, sess)

        try:
            await connector.login(True)
            print("Login successful")
        except ApiError as err:
            print("Cannot login: " + await err.response.text())

        facilities = await connector.get(urls.facilities_list())
        serial = mapper.map_serial_number(facilities)
        system_control = mapper.map_systemcontrol(facilities)
        url_class = url_class_map.get(system_control, urls)
        requests = {}
        for urlName, param in URLS.items():
            url = getattr(url_class, urlName)
            print("requesting " + url.__name__)
            params = {"serial": serial}
            params.update(param)
            req = connector.get(url(**params))
            requests.update({url.__name__: req})

        print("did {} requests".format(len(requests)))

        responses = {}
        for key in requests:
            try:
                responses.update({key: await requests[key]})
            except ApiError as api_err:
                responses.update({key: api_err.response})
            except err:
                print("Cannot get response for {}, skipping it".format(key))

        print("received {} responses".format(len(responses)))

        for key in responses:
            try:
                with open("./dump_result/{}.json".format(key), "w+") as file:
                    data = json.dumps(responses[key]).replace(serial, "SERIAL_NUMBER")
                    json.dump(json.loads(data), file, indent=4)
            except:
                print("cannot write to file {}".format(file.name))


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print("Usage: python3 dump.py user pass")
        sys.exit(0)
    user = sys.argv[1]
    passw = sys.argv[2]

    asyncio.get_event_loop().run_until_complete(main(user, passw))
