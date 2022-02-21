import json
import datetime

from sanic import response

from tickets.code.utils import create_booking_in_provider


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


async def create_booking(request):
    data = await create_booking_in_provider(request)
    if 'detail' in data.keys():
        return response.json(data, status=400)
    else:
        async with request.app.ctx.db_pool.acquire() as db_conn:
            transaction = db_conn.transaction()
            await transaction.start()
            try:
                await db_conn.execute('INSERT INTO booking(booking_id, pnr, expires_at, phone, email)'
                                      ' VALUES($1, $2, $3, $4, $5)',
                                      data['id'], data['pnr'], data['expires_at'], data['phone'], data['email'])
                details = await db_conn.fetchval(f"SELECT * FROM booking WHERE booking_id = '{data['id']}'")

                logo = data['offer']['airline']['logo']
                if logo is not None:
                    logo_exist = await db_conn.fetchval(f"SELECT * FROM logo WHERE url = '{logo['url']}'")
                    if logo_exist is None:
                        await db_conn.execute('INSERT INTO logo(url, width, height) VALUES($1, $2, $3)',
                                              logo['url'], logo['width'], logo['height'])
                        logo = await db_conn.fetchval(f"SELECT * FROM logo WHERE url = '{logo['url']}'")
                    else:
                        logo = logo_exist

                airline = data['offer']['airline']
                airline_exist = await db_conn.fetchval(f"SELECT * FROM airline WHERE name = '{airline['name']}' "
                                                       f"AND code = '{airline['code']}'")
                if not airline_exist:
                    await db_conn.execute('INSERT INTO airline(code, name, logo_id) VALUES($1, $2, $3)',
                                          airline['code'], airline['name'], logo)
                    airline = await db_conn.fetchval(f"SELECT * FROM airline WHERE code = '{airline['code']}' AND "
                                                     f"name = '{airline['name']}'")
                else:
                    airline = airline_exist

                passengers_qty = data['offer']['passengers']
                passengers_exist = await db_conn.fetchval(f"SELECT * FROM passengers WHERE "
                                                          f"adt = '{passengers_qty['ADT']}' "
                                                          f"AND chd = '{passengers_qty['CHD']}' "
                                                          f"AND inf = '{passengers_qty['INF']}'")
                if not passengers_exist:
                    await db_conn.execute(
                        'INSERT INTO passengers(adt, chd, inf) VALUES($1, $2, $3)',
                        passengers_qty['ADT'], passengers_qty['CHD'], passengers_qty['INF'])
                    passengers_qty = await db_conn.fetchval(
                        f'SELECT * FROM passengers WHERE ADT = {passengers_qty["ADT"]} AND CHD = {passengers_qty["CHD"]} '
                        f'AND INF = {passengers_qty["INF"]}')
                else:
                    passengers_qty = passengers_exist

                offer = data['offer']
                await db_conn.execute(
                    'INSERT INTO offer(booking_id, offer_id, refundable, baggage, cabin, airline, passengers, type)'
                    ' VALUES($1, $2, $3, $4, $5, $6, $7, $8)',
                    details, offer['id'], offer['refundable'], offer['baggage'],
                    offer['cabin'], airline, passengers_qty, offer['type'])
                offer = await db_conn.fetchval(f"SELECT * FROM offer WHERE offer_id = '{offer['id']}' ORDER BY id DESC "
                                               f"LIMIT 1 ")
                price = data['offer']['price']

                await db_conn.execute(
                    'INSERT INTO price(price, currency, offer_id) VALUES($1, $2, $3)',
                    price['amount'], price['currency'], offer)
                flights = [flight for flight in data['offer']['flights']]
                for flight in flights:
                    await db_conn.execute(
                        'INSERT INTO flight(offer_id, duration) VALUES($1, $2)', offer, flight['duration'])
                    curr_flight = await db_conn.fetchval(f"SELECT * FROM flight WHERE offer_id = {offer} "
                                                         f"AND duration = {flight['duration']} "
                                                         f"ORDER BY id DESC LIMIT 1")

                    segments = flight['segments']
                    for segment in segments:
                        departure_route = segment['dep']
                        departure_airport = departure_route['airport']
                        departure_airport_exist = await db_conn.fetchval(f"SELECT * FROM airport "
                                                                         f"WHERE code = '{departure_airport['code']}' "
                                                                         f"AND name = '{departure_airport['name']}'")
                        if departure_airport_exist is None:
                            await db_conn.execute(
                                'INSERT INTO airport(code, name) VALUES($1, $2)',
                                departure_airport['code'], departure_airport['name'])
                            departure_airport = await db_conn.fetchval(f"SELECT * FROM airport "
                                                                       f"WHERE code = '{departure_airport['code']}' "
                                                                       f"AND name = '{departure_airport['name']}'")
                        else:
                            departure_airport = departure_airport_exist
                        await db_conn.execute('INSERT INTO route_point(time_at, airport_id, terminal) '
                                              'VALUES($1, $2, $3)', departure_route['at'], departure_airport,
                                              departure_route['terminal'])
                        departure_route = await db_conn.fetchval(f"SELECT * FROM route_point "
                                                                 f"WHERE time_at = '{departure_route['at']}' "
                                                                 f"AND airport_id = {departure_airport} "
                                                                 f"ORDER BY id DESC LIMIT 1")

                        arrive_route = segment['arr']
                        arrive_airport = arrive_route['airport']
                        arrive_airport_exist = await db_conn.fetchval(f"SELECT * FROM airport "
                                                                      f"WHERE code = '{arrive_airport['code']}' "
                                                                      f"AND name = '{arrive_airport['name']}' LIMIT 1")
                        if arrive_airport_exist is None:
                            await db_conn.execute(
                                'INSERT INTO airport(code, name) VALUES($1, $2)',
                                arrive_airport['code'], arrive_airport['name'])
                            arrive_airport = await db_conn.fetchval(f"SELECT * FROM airport "
                                                                    f"WHERE code = '{arrive_airport['code']}' "
                                                                    f"AND name = '{arrive_airport['name']}'")
                        else:
                            arrive_airport = arrive_airport_exist

                        await db_conn.execute('INSERT INTO route_point(time_at, airport_id, terminal) '
                                              'VALUES($1, $2, $3)', arrive_route['at'], arrive_airport,
                                              arrive_route['terminal'])
                        arrive_route = await db_conn.fetchval(f"SELECT * FROM route_point "
                                                              f"WHERE time_at = '{arrive_route['at']}' "
                                                              f"AND airport_id = {arrive_airport} "
                                                              f"ORDER BY id DESC LIMIT 1")
                        await db_conn.execute('INSERT INTO segment(flight_id, operating_airline, flight_number, '
                                              'equipment, cabin, departure_id, arrive_id, baggage) '
                                              'VALUES($1, $2, $3, $4, $5, $6, $7, $8)', curr_flight,
                                              segment['operating_airline'], segment['flight_number'],
                                              segment['equipment'], segment['cabin'], departure_route, arrive_route,
                                              segment['baggage'])

                for passenger in data['passengers']:
                    document = passenger['document']
                    document_exist = await db_conn.fetchval(f"SELECT * FROM document "
                                                            f"WHERE number = '{document['number']}' "
                                                            f"AND expires_at = '{document['expires_at']}' "
                                                            f"AND iin = '{document['iin']}'")
                    if not document_exist:
                        await db_conn.execute('INSERT INTO document(number, expires_at, iin) '
                                              'VALUES($1, $2, $3)', document['number'],
                                              document['expires_at'], document['iin'])
                        document = await db_conn.fetchval(f"SELECT * FROM document "
                                                          f"WHERE number = '{document['number']}' "
                                                          f"AND expires_at = '{document['expires_at']}' "
                                                          f"AND iin = '{document['iin']}'")
                    else:
                        document = document_exist

                    await db_conn.execute('INSERT INTO passenger(gender, type, first_name, '
                                          'last_name, date_of_birth, citizenship, document_id, booking_id) '
                                          'VALUES($1, $2, $3, $4, $5, $6, $7, $8)', passenger['gender'],
                                          passenger['type'], passenger['first_name'], passenger['last_name'],
                                          passenger['date_of_birth'], passenger['citizenship'], document,
                                          details)

            except Exception as e:
                print(e)
                await transaction.rollback()
                raise Exception
            else:
                await transaction.commit()
    return response.json(data)
