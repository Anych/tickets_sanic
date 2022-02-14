import aioredis
import asyncpg
from sanic import Sanic
from sanic import response

from tickets.code import settings, web
from tickets.code.utils import get_fake_data, rate_exchange, initialize_scheduler

UUID_PATTERN = r'[0-9a-f]{8}-[0-9a-f]{4}-{4}[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'
app = Sanic('tickets')


app.add_route(web.search, '/search', methods=['POST'])


@app.route('/search/<search_id>', methods=['GET'])
async def search_result(request, search_id):
    static_data = {
        "search_id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da",
        "status": "PENDING",
        "items": []
    }
    return response.json(static_data)


@app.route('/offers/<offer_id>', methods=['GET'])
async def offer_details(request, offer_id):
    return response.json(get_fake_data('tickets/offer.json'))


@app.route('/booking', methods=['POST'])
async def create_booking(request):
    return response.json(get_fake_data(r'tickets/booking.json'))


@app.route('/booking/<booking_id>', methods=['GET'])
async def booking_details(request, booking_id):
    return response.json(get_fake_data(r'tickets/booking.json'))


@app.listener("before_server_start")
async def init_before(app, loop):
    app.ctx.db_pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
    app.ctx.redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True, max_connections=50)
    await rate_exchange(app)
    initialize_scheduler(app, loop)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=settings.DEBUG)
