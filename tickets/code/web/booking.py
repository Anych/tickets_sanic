import json
import datetime

import cerberus
from sanic import response, exceptions

from code.errors import BookingCreateException
from code.utils import create_booking_in_provider
from code.validators import PassengerValidator


async def get_booking(request, booking_id):
    async with request.app.ctx.db_pool.acquire() as db_conn:
        details = await db_conn.fetch(f"SELECT * FROM booking WHERE booking_id = '{booking_id}'")
        details = [{'booking_id': d['booking_id'], 'pnr': d['pnr'], 'expires_at': d['expires_at'],
                    'phone': d['phone'], 'email': d['email'], 'offer': d['offer'], 'passengers': d['passengers']
                    } for d in details][0]

    expires_at = details['expires_at']
    if datetime.datetime.now().astimezone() > datetime.datetime.fromisoformat(expires_at):
        raise exceptions.NotFound

    details['offer'] = json.loads(details['offer'])
    details['passengers'] = json.loads(details['passengers'])

    return response.json(details, dumps=json.dumps, default=str)


async def create_booking(request):

    async with request.app.ctx.redis as redis_conn:
        countries = await redis_conn.get('countries')
        countries = json.loads(countries)
    for passenger in request.json['passengers']:
        is_validated = await PassengerValidator(passenger, countries).prepare_data()
        if not is_validated:
            raise cerberus.SchemaError

    data = await create_booking_in_provider(request)
    if 'detail' in data.keys():
        raise exceptions.NotFound
    else:

        offer = data['offer']
        offer = json.dumps(offer)

        passengers = data['passengers']
        passengers = json.dumps(passengers)

        async with request.app.ctx.db_pool.acquire() as db_conn:
            transaction = db_conn.transaction()
            await transaction.start()
            try:
                await db_conn.execute('INSERT INTO booking'
                                      '(booking_id, pnr, expires_at, phone, email, offer, passengers) '
                                      'VALUES($1, $2, $3, $4, $5, $6, $7)',
                                      data['id'], data['pnr'], data['expires_at'], data['phone'], data['email'],
                                      offer, passengers)
            except Exception as e:
                print(e)
                await transaction.rollback()
                raise BookingCreateException
            else:
                await transaction.commit()

    return response.json(data)


async def search_booking(request):
    if 'limit' in request.args:
        async with request.app.ctx.db_pool.acquire() as db_conn:
            limit, page = request.args.get('limit'), request.args.get('page')
            total = await db_conn.fetch(f"SELECT COUNT(id) FROM booking")
            total = [{'count': d['count'] for d in total}][0]

            all_bookings = await db_conn.fetch(f"SELECT * FROM booking ORDER BY id "
                                               f"LIMIT {limit} "
                                               f"OFFSET {page} * {limit}")
            all_bookings = [d for d in all_bookings]

        pagination = {'page': f"{page}", 'items': all_bookings,
                      'limit': f"{limit}", 'total': f'{total["count"]}'}

        return response.json(pagination, dumps=json.dumps, default=str)

    else:
        async with request.app.ctx.db_pool.acquire() as db_conn:
            email, phone = request.args.get('email'), request.args.get('phone').rsplit()[0]
            all_bookings = await db_conn.fetch(f"SELECT * FROM booking "
                                               f"WHERE email = '{email}' "
                                               f"AND phone = '+{phone}' ORDER BY id")
        all_bookings = [d for d in all_bookings]

        return response.json(all_bookings, dumps=json.dumps, default=str)
