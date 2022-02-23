import asyncio
import datetime
import json
import os

import aioredis
import httpx
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
                currency = json.dumps(currency)
                await redis_conn.hset('currencies', rate['title'], currency)


if __name__ == '__main__':
    asyncio.run(update_rate_exchange())
