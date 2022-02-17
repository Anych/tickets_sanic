from sanic import response


async def get_offer(request, offer_id):
    app = request.app
    try:
        offer = eval(await app.ctx.redis.get(offer_id))
    except Exception as e:
        offer = {'offer_id': 'offer is expired'}
        print(e)
    return response.json(offer)
