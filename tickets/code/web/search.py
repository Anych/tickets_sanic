import time
import uuid

from sanic import response

from tickets.code.utils import search_in_providers


async def create_search(request):
    uuid_id = str(uuid.uuid1())
    request.app.add_task(search_in_providers(request, 'Amadeus', uuid_id), name=f'Amadeus {uuid_id}')
    request.app.add_task(search_in_providers(request, 'Sabre', uuid_id), name=f'Sabre {uuid_id}')
    start_time = time.time()
    async with request.app.ctx.redis as redis_conn:
        await redis_conn.set(uuid_id, start_time)
    return response.json({'search_id': uuid_id})


async def search_result(request, search_id):
    app = request.app
    result = {'search_id': search_id, 'status': None, 'items': []}
    async with app.ctx.redis as redis_conn:
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

        if result['status'] is None:
            result['status'] = 'DONE'
        expired = await redis_conn.hgetall(search_id)
        if expired == {}:
            result['status'] = 'EXPIRED'
    return response.json(result)
