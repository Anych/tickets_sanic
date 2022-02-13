import json
from datetime import datetime

import requests
import xmltodict


def get_fake_data(filename):
    with open(filename, 'r') as json_file:
        json_object = json.load(json_file)
        return json_object


async def rate_exchange(app):
    date = datetime.today().strftime('%d.%m.%Y')
    response = requests.get(f'https://www.nationalbank.kz/rss/get_rates.cfm?fdate={date}')

    rates = xmltodict.parse(response.text)
    for rate in rates['rates']['item']:
        currency = {'description': rate['description'], 'quant': rate['quant']}
        await app.ctx.redis.hset(rate['title'], mapping=currency)
