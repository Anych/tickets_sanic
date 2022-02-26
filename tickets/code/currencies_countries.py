import asyncio
import datetime
import os

import aioredis
import httpx
import ujson
import xmltodict


async def update_rate_exchange():
    redis = await aioredis.from_url(url=os.environ['REDIS_URL'])
    date = datetime.datetime.today().strftime('%d.%m.%Y')
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f'https://www.nationalbank.kz/rss/get_rates.cfm?fdate={date}')
        except Exception as e:
            print(e)
            await asyncio.sleep(30)
            await update_rate_exchange()
        rates = xmltodict.parse(response.text)['rates']['item']

        async with redis as redis_conn:
            for rate in rates:
                currency = {'description': rate['description'], 'quant': rate['quant']}
                currency = ujson.dumps(currency)
                await redis_conn.hset('currencies', rate['title'], currency)


async def get_countries():
    redis = await aioredis.from_url(url=os.environ['REDIS_URL'])
    async with httpx.AsyncClient() as client:
        try:
            countries = await client.get('https://avia-api.k8s-test.aviata.team/countries')
            countries = countries.json()['items']
            countries = ujson.dumps(countries)
        except Exception as e:
            print(e)
            await asyncio.sleep(30)
            await get_countries()

        async with redis as redis_conn:
            await redis_conn.set('countries', countries)


if __name__ == '__main__':
    asyncio.run(update_rate_exchange())
    asyncio.run(get_countries())
