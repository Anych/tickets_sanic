import json
import uuid

import aioredis
import cerberus
from sanic import response, exceptions

from tickets.code.utils import search_in_providers
from tickets.code.validators import SearchValidator


async def create_search(request):
    validated = await SearchValidator(request.json).prepare_data()
    if not validated:
        raise cerberus.SchemaError

    search_id = str(uuid.uuid1())
    request.app.add_task(search_in_providers(request, 'Amadeus', search_id), name=f'Amadeus {search_id}')
    request.app.add_task(search_in_providers(request, 'Sabre', search_id), name=f'Sabre {search_id}')

    return response.json({'search_id': search_id})


async def search_result(request, search_id):
    app = request.app
    result = {'search_id': search_id, 'status': 'PENDING', 'items': []}

    async with app.ctx.redis as redis_conn:
        for provider in ['Amadeus', 'Sabre']:
            try:
                provider_id = await redis_conn.hget(search_id, provider)
                if provider_id != 'timeout error':
                    provider_result = await redis_conn.get(provider_id)
                    provider_result = json.loads(provider_result)
                    result['items'].append(provider_result)
            except aioredis.exceptions.DataError:
                pass
        result['status'] = await redis_conn.hget(search_id, 'status')
        print(await redis_conn.hget(search_id, 'status'))
        status = await redis_conn.hgetall(search_id)
    print(status)
    if status == {}:
        raise exceptions.NotFound
    return response.json(result)
