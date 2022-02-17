import uuid

from sanic import response

from tickets.code.utils import search_in_providers, kill_search


async def create_search(request):
    uuid_id = str(uuid.uuid1())
    request.app.add_task(search_in_providers(request, 'Amadeus', uuid_id), name=f'Amadeus {uuid_id}')
    request.app.add_task(kill_search(request, f'Amadeus {uuid_id}'))

    request.app.add_task(search_in_providers(request, 'Sabre', uuid_id), name=f'Sabre {uuid_id}')
    request.app.add_task(kill_search(request, f'Sabre {uuid_id}'))
    return response.json({'search_id': uuid_id})


async def search_result(request, search_id):
    app = request.app
    result = {'search_id': search_id, 'status': None, 'items': ''}

    try:
        amadeus_id = await app.ctx.redis.hget(search_id, 'Amadeus')
        amadeus_result = await app.ctx.redis.get(amadeus_id)
        result['items'] += amadeus_result
    except Exception as e:
        print(e)
        print(123)
        result['status'] = 'PENDING'

    try:
        sabre_id = await app.ctx.redis.hget(search_id, 'Sabre')
        sabre_result = await app.ctx.redis.get(sabre_id)
        result['items'] += sabre_result
    except Exception as e:
        print(e)
        result['status'] = 'PENDING'

    if result['status'] is None:
        result['status'] = 'DONE'
    expired = await app.ctx.redis.hgetall(search_id)
    if expired == {}:
        result['status'] = 'EXPIRED'
    return response.json(result)
