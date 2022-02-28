import httpx
import ujson
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from code.currencies_countries import update_rate_exchange
from code.settings import SEARCH_EXPIRE_TIME


async def get_currency_rates(redis):
    async with redis as redis_conn:
        currencies = await redis_conn.hgetall('currencies')
    print(currencies, 123123312231)
    currencies_dict = dict()
    for title, value in currencies.items():
        try:
            title = ujson.loads(title)
            value = ujson.loads(value)
            currencies_dict[title] = value
        except Exception as e:
            pass

    return currencies_dict


async def change_currency_to_kzt(offers, redis):
    currencies = await get_currency_rates(redis)
    for offer in offers:
        if offer['price']['currency'] == 'KZT':
            continue

        else:
            currency_values = currencies[offer['price']['currency']]
            value = float(currency_values['description'])
            qty = int(currency_values['quant'])
            kzt_value = int(offer['price']['amount'] * float(value) / int(qty))
            offer['price']['currency'] = 'KZT'
            offer['price']['amount'] = kzt_value


async def check_if_searching_is_done(redis_conn, search_id):
    if len(await redis_conn.hgetall(search_id)) == 3:
        await redis_conn.hset(search_id, 'status', 'DONE')
    else:
        await redis_conn.hset(search_id, 'status', 'PENDING')
    await redis_conn.expire(search_id, SEARCH_EXPIRE_TIME)


async def get_data_from_provider(data):
    try:
        async with httpx.AsyncClient() as client:
            data = await client.post(r'https://avia-api.k8s-test.aviata.team/offers/search',
                                     json=data, timeout=30)
    except Exception as e:
        print(e)
        data = None

    return data


async def search_in_providers(request, provider, search_id):
    app = request.app
    async with app.ctx.redis as redis_conn:
        request.json['provider'] = provider
        await redis_conn.hset(search_id, 'status', 'PENDING')
    data = await get_data_from_provider(request.json)

    async with app.ctx.redis.pipeline(transaction=True) as pipe:
        if data:
            data = data.json()
            provider_id = data['search_id']

            await change_currency_to_kzt(data['items'], app.ctx.redis)
            await pipe.hset(search_id, provider, provider_id)

            items = ujson.dumps(data['items'])
            await pipe.set(provider_id, items)
            await pipe.expire(provider_id, SEARCH_EXPIRE_TIME)

            for item in data['items']:
                offer = ujson.dumps(item)
                await pipe.set(item['id'], offer)
                await pipe.expire(item['id'], SEARCH_EXPIRE_TIME)

        else:
            await pipe.hset(search_id, provider, 'timeout error')
        await pipe.execute()
        await check_if_searching_is_done(app.ctx.redis, search_id)


async def create_booking_in_provider(request):
    async with httpx.AsyncClient() as client:
        data = await client.post(r'https://avia-api.k8s-test.aviata.team/offers/booking',
                                 json=request.json, timeout=60)

        return data.json()


async def initialize_scheduler(app, loop):
    scheduler = AsyncIOScheduler({
        'event_loop': loop,
        'apscheduler.timezone': 'Asia/Almaty',
    })
    scheduler.add_job(update_rate_exchange, 'cron', day='*', hour=12, minute=0)

    return scheduler.start()
