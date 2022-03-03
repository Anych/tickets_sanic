import aioredis
import asyncpg
from sanic import Sanic, exceptions

from code import settings
from code import web
from code.errors import *

app = Sanic('tickets')


app.add_route(web.search, '/search', methods=['POST'])
app.add_route(web.search_result, '/search/<search_id>', methods=['GET'])
app.add_route(web.get_offer, '/offers/<offer_id>', methods=['GET'])
app.add_route(web.create_booking, '/booking', methods=['POST'])
app.add_route(web.get_booking, '/booking/<booking_id>', methods=['GET'])
app.add_route(web.search_booking, '/booking', methods=['GET'])

app.error_handler.add(BookingCreateException, booking_create_error_handler)
app.error_handler.add(exceptions.NotFound, not_fount_error_handler)
app.error_handler.add(Exception, server_error_handler)


@app.listener("before_server_start")
async def init_before(app, loop):
    app.ctx.db_pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
    app.ctx.redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True, max_connections=50)


@app.listener('after_server_stop')
async def cleanup(app, loop):
    await app.ctx.redis.close()
    await app.ctx.db_pool.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=settings.DEBUG)
