import json
from datetime import datetime

import requests
import xmltodict
from apscheduler.schedulers.asyncio import AsyncIOScheduler


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
        async with app.ctx.db_pool.acquire() as conn:
            await conn.execute('INSERT INTO currency_exchange(title, description, quantity) VALUES($1, $2, $3)',
                               rate['title'], rate['description'], int(rate['quant']))


async def initialize_scheduler(app, loop):
    scheduler = AsyncIOScheduler({
        'event_loop': loop,
        'apscheduler.timezone': 'Asia/Almaty',
    })
    scheduler.add_job(rate_exchange, 'cron', day='*', hour=16, minute=34, args=[app])
    return scheduler.start()


async def change_currency_to_kzt(app, data):
    for num in range(len(data['items'])):
        if data['items'][num]['price']['currency'] != 'KZT':

            try:
                value = await app.ctx.redis.hget(data['items'][num]['price']['currency'], 'description')
                qty = await app.ctx.redis.hget(data['items'][num]['price']['currency'], 'quant')
            except Exception as e:
                print(e)

                title = data['items'][num]['price']['currency']
                async with app.ctx.db_pool.acquire() as conn:
                    currency = await conn.fetch(f"SELECT * FROM currency_exchange WHERE title = '{title}'"
                                                f" ORDER BY TIMESTAMP DESC LIMIT 1")
                    currency = [{'description': d['description'], 'quantity': d['quantity']} for d in currency][0]
                    value = currency['description']
                    qty = currency['qty']

            kzt_value = int(data['items'][num]['price']['amount'] * float(value) / int(qty))
            data['items'][num]['price']['currency'] = 'KZT'
            data['items'][0]['price']['amount'] = kzt_value


async def search_in_providers(request, provider):
    app = request.app
    request.json['provider'] = provider
    data = requests.post(r'https://avia-api.k8s-test.aviata.team/offers/search', json=request.json).json()
    search_id = data['search_id']
    await change_currency_to_kzt(app, data)
    await app.ctx.redis.set(request.json['provider'], str(data))
    return search_id
