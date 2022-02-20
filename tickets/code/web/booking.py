import json
import datetime

from sanic import response


async def get_booking(request, booking_id):
    async with request.app.ctx.db_pool.acquire() as db_conn:
        details = await db_conn.fetch(f"SELECT * FROM booking WHERE booking_id = '{booking_id}'")
        details = [{'id': d['id'], 'booking_id': d['booking_id'], 'pnr': d['pnr'], 'expires_at': d['expires_at'],
                    'phone': d['phone'], 'email': d['email']
                    } for d in details][0]

        expires_at = details['expires_at']
        if datetime.datetime.now().astimezone() > datetime.datetime.fromisoformat(expires_at):
            return response.json({'detail': 'Ваша бронь истекла.'})

        offer_details = await db_conn.fetch(f"SELECT * FROM offer WHERE booking_id = '{details['id']}'")
        offer_details = [{'id': d['id'], 'offer_id': d['offer_id'], 'flights': None, 'price': None,
                          'refundable': d['refundable'], 'baggage': d['baggage'], 'cabin': d['cabin'],
                          'airline': d['airline'], 'passengers': d['passengers'], 'type': d['type']
                          } for d in offer_details][0]

        flights_details = await db_conn.fetch(f"SELECT * FROM flight WHERE offer_id = {offer_details['id']}")
        flights_details = [{'id': d['id'], 'duration': d['duration']} for d in flights_details]

        for num in range(len(flights_details)):
            segment_details = await db_conn.fetch(f"SELECT * FROM segment "
                                                  f"WHERE flight_id = '{flights_details[num]['id']}'")
            segments = []
            for segment_num in range(len(segment_details)):
                segment = [{'id': d['id'], 'operating_airline': d['operating_airline'],
                            'flight_number': d['flight_number'], 'equipment': d['equipment'],
                            'cabin': d['cabin'], 'dep': d['departure_id'], 'arr': d['arrive_id'],
                            'baggage': d['baggage']} for d in segment_details][segment_num]

                departure_route = await db_conn.fetch(
                    f"SELECT * FROM route_point WHERE id = '{segment['dep']}'")
                departure_route = [{'at': d['time_at'], 'airport': d['airport_id'],
                                    'terminal': d['terminal']} for d in departure_route][0]
                segment['dep'] = departure_route
                departure_airport = await db_conn.fetch(f"SELECT * FROM airport "
                                                        f"WHERE id = '{departure_route['airport']}'")
                departure_airport = [{'code': d['code'], 'name': d['name']} for d in departure_airport][0]
                departure_route['airport'] = departure_airport
                segment['dep'] = departure_route

                arrive_route = await db_conn.fetch(
                    f"SELECT * FROM route_point WHERE id = '{segment['arr']}'")
                arrive_route = [{'time_at': d['time_at'], 'airport': d['airport_id'],
                                 'terminal': d['terminal']} for d in arrive_route][0]
                arrive_airport = await db_conn.fetch(
                    f"SELECT * FROM airport WHERE id = '{arrive_route['airport']}'")
                arrive_airport = [{'code': d['code'], 'name': d['name']} for d in arrive_airport][0]
                arrive_route['airport'] = arrive_airport
                segment['arr'] = arrive_route
                del segment['id']
                segments.append(segment)
            flights_details[num]['segment'] = segments
            del flights_details[num]['id']

        price = await db_conn.fetch(f"SELECT * FROM price WHERE offer_id = {offer_details['id']}")
        price = [{'price': int(d['price']), 'currency': d['currency']} for d in price]

        airline = await db_conn.fetch(f"SELECT * FROM airline WHERE id = '{offer_details['airline']}'")
        airline = [{'code': d['code'], 'name': d['name'], 'logo': d['logo_id']} for d in airline][0]

        if airline['logo'] is not None:
            logo = await db_conn.fetch(f"SELECT * FROM logo WHERE id = {airline['logo']}")
            logo = [{'url': d['url'], 'width': d['width'], 'height': d['height']} for d in logo][0]
            airline['logo'] = logo
        else:
            airline['logo'] = None

        passengers_qty = await db_conn.fetch(f"SELECT * FROM passengers WHERE id = '{offer_details['passengers']}'")
        passengers_qty = [{'ADT': d['adt'], 'CHD': d['chd'], 'INF': d['inf']} for d in passengers_qty]

        passenger = await db_conn.fetch(f"SELECT * FROM passenger WHERE booking_id = '{details['id']}'")
        passenger = [{'gender': d['gender'], 'type': d['type'], 'first_name': d['first_name'],
                      'last_name': d['last_name'], 'date_of_birth': d['date_of_birth'],
                      'citizenship': d['citizenship'], 'document': d['document_id']} for d in passenger]

        passengers = []
        for num in range(len(passenger)):
            document = await db_conn.fetch(f"SELECT * FROM document WHERE id = '{passenger[num]['document']}'")
            document = [{'number': d['number'], 'expires_at': d['expires_at'], 'iin': d['iin']} for d in document]
            passenger[num]['document'] = document[0]
            passengers.append(passenger[num])

        del details['id']
        del offer_details['id']

        details['offer'] = [offer_details]
        details['offer'][0]['flights'] = [flights_details]
        details['offer'][0]['price'] = price
        details['offer'][0]['airline'] = airline
        details['offer'][0]['passengers'] = passengers_qty
        details['passengers'] = passengers
    return response.json(details, dumps=json.dumps, default=str)


async def get_bookings_filter(request):
    async with request.app.ctx.db_pool.acquire() as db_conn:
        if 'limit' in request.args:
            total = await db_conn.fetch(f"SELECT * FROM booking")
            all_bookings = await db_conn.fetch(f"SELECT * FROM booking ORDER BY id "
                                               f"LIMIT {request.args.get('limit')} "
                                               f"OFFSET {request.args.get('page')} * {request.args.get('limit')}")
            all_bookings = [d for d in all_bookings]
            pagination = {'page': f"{request.args.get('page')}", 'items': all_bookings,
                          'limit': f"{request.args.get('limit')}", 'total': f'{len(total)}'}
            return response.json(pagination, dumps=json.dumps, default=str)
        else:
            all_bookings = await db_conn.fetch(f"SELECT * FROM booking "
                                               f"WHERE email = '{request.args.get('email')}' "
                                               f"AND phone = '+{request.args.get('phone').rsplit()[0]}' ORDER BY id")
            all_bookings = [d for d in all_bookings]
            return response.json(all_bookings, dumps=json.dumps, default=str)
