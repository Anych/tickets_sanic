import asyncio
import json
import time
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
            await conn.execute('INSERT INTO currency(title, description, quantity) VALUES($1, $2, $3)',
                               rate['title'], rate['description'], int(rate['quant']))


def initialize_scheduler(app, loop):
    scheduler = AsyncIOScheduler({
        'event_loop': loop,
        'apscheduler.timezone': 'Asia/Almaty',
    })
    scheduler.add_job(rate_exchange, 'cron', day='*', hour=12, minute=00, args=[app])
    return scheduler.start()


async def search_in_providers(request):
    search_data = request.json
    app = request.app
    for provider in ['Amadeus', 'Sabre']:
        search_data['provider'] = provider
        data = requests.post(r'https://avia-api.k8s-test.aviata.team/offers/search', json=search_data).json()
        await app.ctx.redis.hset(provider, 'search_id', data['search_id'])
        for item in data['items'][:2]:
            await app.ctx.redis.hset(data['search_id'], 'item_id', item['id'])
            for flight in item['flights']:
                await app.ctx.redis.hset(item['id'], 'duration', flight['duration'])
                print(flight)