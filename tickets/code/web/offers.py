import json

from sanic import response, exceptions


async def get_offer(request, offer_id):
    try:
        async with request.app.ctx.redis as redis_conn:
            offer = await redis_conn.get(offer_id)
            offer = json.loads(offer)
    except Exception as e:
        print(e)
        raise exceptions.NotFound

    return response.json(offer)
