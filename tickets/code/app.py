import aioredis
import asyncpg
from sanic import Sanic

from tickets.code import settings, web
from tickets.code.utils import rate_exchange, initialize_scheduler

app = Sanic('tickets')


app.add_route(web.search, '/search', methods=['POST'])
app.add_route(web.search_result, '/search/<search_id>', methods=['GET'])
app.add_route(web.get_offer, '/offers/<offer_id>', methods=['GET'])
app.add_route(web.create_booking, '/offers/booking', methods=['POST'])
app.add_route(web.get_booking, '/booking/<booking_id>', methods=['GET'])
app.add_route(web.get_bookings_filter, '/booking', methods=['GET'])


@app.listener("before_server_start")
async def init_before(app, loop):
    app.ctx.db_pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
    app.ctx.redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True, max_connections=50)
    # await rate_exchange(app)
    # await initialize_scheduler(app, loop)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=settings.DEBUG)
