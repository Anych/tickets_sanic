import time
import uuid

from sanic import response

from tickets.code.utils import search_in_providers


async def create_search(request):
    uuid_id = str(uuid.uuid1())
    try:
        provider = request.json['provider']
        request.app.add_task(search_in_providers(request, provider, uuid_id), name=f'{provider} {uuid_id}')
        if provider == 'Amadeus':
            request.app.add_task(search_in_providers(request, 'Sabre', uuid_id), name=f'Sabre {uuid_id}')
        else:
            request.app.add_task(search_in_providers(request, 'Amadeus', uuid_id), name=f'Amadeus {uuid_id}')

    except KeyError:
        request.app.add_task(search_in_providers(request, 'Amadeus', uuid_id), name=f'Amadeus {uuid_id}')
        request.app.add_task(search_in_providers(request, 'Sabre', uuid_id), name=f'Sabre {uuid_id}')

    start_time = time.time()
    async with request.app.ctx.redis as redis_conn:
        await redis_conn.hset(uuid_id, 'starting_time', start_time)
    return response.json({'search_id': uuid_id})


async def search_result(request, search_id):
    app = request.app
    result = {'search_id': search_id, 'status': None, 'items': []}
    async with app.ctx.redis as redis_conn:
        start_time = await redis_conn.hget(search_id, 'starting_time')
        if start_time is None:
            start_time = 0
        try:
            amadeus_id = await redis_conn.hget(search_id, 'Amadeus')
            amadeus_result = eval(await redis_conn.get(amadeus_id))
            result['items'].append(amadeus_result)
        except Exception as e:
            print(e)
            result['status'] = 'PENDING'

        try:
            sabre_id = await redis_conn.hget(search_id, 'Sabre')
            sabre_result = eval(await redis_conn.get(sabre_id))
            result['items'].append(sabre_result)
        except Exception as e:
            print(e)
            result['status'] = 'PENDING'

        if result['status'] is None or time.time() - float(start_time) > 30 and result['status'] == 'PENDING':
            result['status'] = 'DONE'
        expired = await redis_conn.hgetall(search_id)
        if expired == {}:
            result['status'] = 'EXPIRED'
    return response.json(result)
