import asyncio
import time

from sanic import response

from tickets.code.utils import search_in_providers


async def create_search(request):  # TODO: validator
    start_time = time.time()
    search_id = await asyncio.gather(search_in_providers(request, 'Amadeus'), search_in_providers(request, 'Sabre'),
                                     return_exceptions=True)
    while True:
        if time.time() - start_time < 30:
            await asyncio.sleep(0.1)
            return response.json({'search_id': search_id})
        else:
            return response.json({'search_id': search_id})

