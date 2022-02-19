import asyncio
from datetime import datetime

import httpx
import xmltodict
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tickets.code.settings import SEARCH_EXPIRE_TIME


async def rate_exchange(app):
    date = datetime.today().strftime('%d.%m.%Y')
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f'https://www.nationalbank.kz/rss/get_rates.cfm?fdate={date}')
        except Exception as e:
            print(e)
            await asyncio.sleep(30)
            await rate_exchange(app)

        rates = xmltodict.parse(response.text)
        for rate in rates['rates']['item']:
            currency = {'description': rate['description'], 'quant': rate['quant']}
            async with app.ctx.redis as redis_conn:
                await redis_conn.hset(rate['title'], mapping=currency)
            async with app.ctx.db_pool.acquire() as conn:
                await conn.execute('INSERT INTO currency_exchange(title, description, quantity) VALUES($1, $2, $3)',
                                   rate['title'], rate['description'], int(rate['quant']))


async def initialize_scheduler(app, loop):
    scheduler = AsyncIOScheduler({
        'event_loop': loop,
        'apscheduler.timezone': 'Asia/Almaty',
    })
    scheduler.add_job(rate_exchange, 'cron', day='*', hour=12, minute=0, args=[app])
    return scheduler.start()


async def change_currency_to_kzt(app, data, redis_conn):
    for num in range(len(data['items'])):
        if data['items'][num]['price']['currency'] != 'KZT':
            try:
                value = await redis_conn.hget(data['items'][num]['price']['currency'], 'description')
                qty = await redis_conn.hget(data['items'][num]['price']['currency'], 'quant')
            except Exception as e:
                print(e)
                async with app.ctx.db_pool.acquire() as db_conn:
                    title = data['items'][num]['price']['currency']
                    currency = await db_conn.fetch(f"SELECT * FROM currency_exchange WHERE title = '{title}'"
                                                   f" ORDER BY TIMESTAMP DESC LIMIT 1")
                    currency = [{'description': d['description'], 'quantity': d['quantity']} for d in currency][0]
                    value = currency['description']
                    qty = currency['qty']

            kzt_value = int(data['items'][num]['price']['amount'] * float(value) / int(qty))
            data['items'][num]['price']['currency'] = 'KZT'
            data['items'][0]['price']['amount'] = kzt_value


async def search_in_providers(request, provider, uuid_id):
    app = request.app
    async with app.ctx.redis as redis_conn:
        request.json['provider'] = provider
        async with httpx.AsyncClient() as client:
            data = await client.post(r'https://avia-api.k8s-test.aviata.team/offers/search',
                                     json=request.json, timeout=30)

        data = data.json()
        search_id = data['search_id']
        await change_currency_to_kzt(app, data, redis_conn)

        await redis_conn.hset(uuid_id, provider, search_id)
        await redis_conn.expire(uuid_id, SEARCH_EXPIRE_TIME)

        await redis_conn.set(search_id, str(data['items']))
        await redis_conn.expire(search_id, SEARCH_EXPIRE_TIME)

        for offer in data['items']:
            await redis_conn.set(offer['id'], str(offer))
            await redis_conn.expire(offer['id'], SEARCH_EXPIRE_TIME)


async def create_booking_in_provider(request):
    async with httpx.AsyncClient() as client:
        data = await client.post(r'https://avia-api.k8s-test.aviata.team/offers/booking',
                                 json=request.json, timeout=60)
        return data.json()
