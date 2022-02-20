from sanic import response

from tickets.code.utils import create_booking_in_provider


async def get_offer(request, offer_id):
    app = request.app
    try:
        async with app.ctx.redis as redis_conn:
            offer = eval(await redis_conn.get(offer_id))
    except Exception as e:
        offer = {'offer_id': 'offer is expired'}
        print(e)
    return response.json(offer)


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
