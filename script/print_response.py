#!/usr/bin/env python3
import asyncio
import json
import sys

import aiohttp

sys.path.append("../")
from pymultimatic.api import Connector, ApiError, urls
from pymultimatic.model import mapper


async def main(user, passw, url_name):
    print('Trying to connect with user ' + user)

    async with aiohttp.ClientSession() as sess:
        connector = Connector(user, passw, sess)

        try:
            await connector.login(True)
            print('Login successful')
        except ApiError as err:
            print(err.message)
            print(err.response)
            print(err.status)

        facilities = await connector.get(urls.facilities_list())
        serial = mapper.map_serial_number(facilities)

        url_method = getattr(urls, url_name)
        url = url_method(**{'serial': serial})
        print(url)

        try:
            print(json.dumps(await connector.get(url)))
        except ApiError as err:
            print(err.message)
            print(err.response)
            print(err.status)


if __name__ == "__main__":
    if not len(sys.argv) == 4:
        print('Usage: python3 print_response.py user pass url_name')
        sys.exit(0)
    user = sys.argv[1]
    passw = sys.argv[2]
    url_name = sys.argv[3]

    asyncio.get_event_loop().run_until_complete(main(user, passw, url_name))