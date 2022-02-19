import json

from sanic import response

from tickets.code.utils import create_booking_in_provider


async def get_booking(request, booking_id):
    async with request.app.ctx.db_pool.acquire() as db_conn:
        if request.args:
            if 'email' in request.args:
                all_bookings = await db_conn.fetch(f"SELECT * FROM booking "
                                                   f"WHERE email = '{request.args['email']}' "
                                                   f"AND phone = '{request.args['phone']}' ORDER BY id")
                return response.json(all_bookings, dumps=json.dumps, default=str)
            else:

                pagination = await db_conn.fetch(f"SELECT * FROM booking "
                                                 f"WHERE email = '{request.args['email']}' "
                                                 f"AND phone = '{request.args['phone']}' ORDER BY id"
                                                 f"LIMIT {request.args['limit']} OFFSET {request.args['page']} * 10")
                return response.json(pagination, dumps=json.dumps, default=str)
        else:
            details = await db_conn.fetch(f"SELECT * FROM booking WHERE booking_id = '{booking_id}'")
            details = [{'id': d['id'], 'booking_id': d['booking_id'], 'pnr': d['pnr'], 'expires_at': d['expires_at'],
                        'phone': d['phone'], 'email': d['email']
                        } for d in details][0]

            offer_details = await db_conn.fetch(f"SELECT * FROM offer WHERE booking_id = '{details['id']}'")
            offer_details = [{'id': d['id'], 'offer_id': d['offer_id'], 'flights': None, 'price': None,
                              'refundable': d['refundable'], 'baggage': d['baggage'], 'cabin': d['cabin'],
                              'airline': d['airline'], 'passengers': d['passengers'], 'type': d['type']
                              } for d in offer_details][0]

            flights_details = await db_conn.fetch(f"SELECT * FROM flight WHERE offer_id = '{offer_details['id']}'")
            flights_details = [{'id': d['id'], 'duration': d['duration']} for d in flights_details]

            segments = []
            for num in range(len(flights_details)):
                segment_details = await db_conn.fetch(f"SELECT * FROM segment "
                                                      f"WHERE flight_id = '{flights_details[num]['id']}'")
                segment_details = [{'id': d['id'], 'operating_airline': d['operating_airline'],
                                    'flight_number': d['flight_number'], 'equipment': d['equipment'],
                                    'cabin': d['cabin'], 'dep': d['departure_id'], 'arr': d['arrive_id'],
                                    'baggage': d['baggage']} for d in segment_details]

                departure_route = await db_conn.fetch(
                    f"SELECT * FROM route_point WHERE id = '{segment_details[0]['dep']}'")
                departure_route = [{'at': d['time_at'], 'airport': d['airport_id'],
                                    'terminal': d['terminal']} for d in departure_route]
                segment_details[0]['dep'] = departure_route
                departure_airport = await db_conn.fetch(f"SELECT * FROM airport "
                                                        f"WHERE id = '{departure_route[0]['airport']}'")
                departure_airport = [{'code': d['code'], 'name': d['name']} for d in departure_airport]
                departure_route[0]['airport'] = departure_airport
                segment_details[0]['dep'] = departure_route

                arrive_route = await db_conn.fetch(f"SELECT * FROM route_point "
                                                   f"WHERE airport_id = '{segment_details[0]['arr']}'")
                arrive_route = [{'time_at': d['time_at'], 'airport': d['airport_id'],
                                 'terminal': d['terminal']} for d in arrive_route]
                arrive_airport = await db_conn.fetch(f"SELECT * FROM airport WHERE id = '{arrive_route[0]['airport']}'")
                arrive_airport = [{'code': d['code'], 'name': d['name']} for d in arrive_airport]
                arrive_route[0]['airport'] = arrive_airport
                segment_details[0]['arr'] = arrive_route
                del segment_details[0]['id']
                segments.append(segment_details[0])

            price = await db_conn.fetch(f"SELECT * FROM price WHERE offer_id = '{offer_details['id']}'")
            price = [{'price': int(d['price']), 'currency': d['currency']} for d in price]

            airline = await db_conn.fetch(f"SELECT * FROM airline WHERE id = '{offer_details['airline']}'")
            airline = [{'code': d['code'], 'name': d['name'], 'logo': d['logo_id']} for d in airline][0]

            logo = await db_conn.fetch(f"SELECT * FROM logo WHERE id = '{airline['logo']}'")
            logo = [{'url': d['url'], 'height': d['height'], 'weight': d['weight']} for d in logo][0]
            airline['logo'] = logo

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
            for num in range(len(flights_details)):
                del flights_details[num]['id']
                flights_details[num]['segments'] = segments[num]

            details['offer'] = [offer_details]
            details['offer'][0]['flights'] = [flights_details]
            details['offer'][0]['price'] = price[0]
            details['offer'][0]['airline'] = airline
            details['offer'][0]['passengers'] = passengers_qty
            details['passengers'] = passengers
        return response.json(details, dumps=json.dumps, default=str)


async def create_booking(request):
    data = await create_booking_in_provider(request)
    if 'detail' in data.keys():
        return response.json(data, status=400)
    else:
        async with request.app.ctx.db_pool.acquire() as db_conn:
            transaction = db_conn.transaction()
            await transaction.start()
            try:
                details = await db_conn.fetchval(f"SELECT * FROM booking WHERE booking_id = '{data['id']}'")
                if not details:
                    await db_conn.execute('INSERT INTO booking(booking_id, pnr, expires_at, phone, email)'
                                          ' VALUES($1, $2, $3, $4, $5)',
                                          data['id'], data['pnr'], data['expires_at'], data['phone'], data['email'])
                    details = await db_conn.fetchval(f"SELECT * FROM booking WHERE booking_id = '{data['id']}'")
                else:
                    return response.json({'detail': 'По данному id бронь уже существует'}, status=400)

                logo = data['offer']['airline']['logo']
                if logo is not None:
                    logo_exist = await db_conn.fetchval(f"SELECT * FROM logo WHERE url = '{logo['url']}' AND width = "
                                                        f"'{logo['width']}' AND height = '{logo['height']}'")
                    if logo_exist is None:
                        await db_conn.execute('INSERT INTO logo(url, width, height) VALUES($1, $2, $3)',
                                              logo['url'], logo['width'], logo['height'])
                        logo = await db_conn.fetchval(f"SELECT * FROM logo WHERE url = '{logo['url']}' "
                                                      f"AND width = '{logo['width']}' AND height = '{logo['height']}'")
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

                passengers = data['offer']['passengers']
                passengers_exist = await db_conn.fetchval(f"SELECT * FROM passengers WHERE "
                                                          f"adt = '{passengers['ADT']}' "
                                                          f"AND chd = '{passengers['CHD']}' "
                                                          f"AND inf = '{passengers['INF']}'")
                if not passengers_exist:
                    await db_conn.execute(
                        'INSERT INTO passengers(adt, chd, inf) VALUES($1, $2, $3)',
                        passengers['ADT'], passengers['CHD'], passengers['INF'])
                    passengers = await db_conn.fetchval(
                        f'SELECT * FROM passengers WHERE ADT = {passengers["ADT"]} AND CHD = {passengers["CHD"]} '
                        f'AND INF = {passengers["INF"]}')
                else:
                    passengers = passengers_exist

                offer = data['offer']
                await db_conn.execute(
                    'INSERT INTO offer(booking_id, offer_id, refundable, baggage, cabin, airline, passengers, type)'
                    ' VALUES($1, $2, $3, $4, $5, $6, $7, $8)',
                    details, offer['id'], offer['refundable'], offer['baggage'],
                    offer['cabin'], airline, passengers, offer['type'])
                offer = await db_conn.fetchval(f"SELECT * FROM offer WHERE offer_id = '{offer['id']}'")

                flights = [flight for flight in data['offer']['flights']]
                flights_list = []
                for flight in flights:
                    await db_conn.execute(
                        'INSERT INTO flight(offer_id, duration) VALUES($1, $2)', offer, flight['duration'])
                    flights_list.append(await db_conn.fetchval(f"SELECT * FROM flight WHERE offer_id = {offer} "
                                                               f"AND duration = {flight['duration']}"))
                    segment = flight['segments'][0]
                    departure_route = segment['dep']
                    departure_airport = departure_route['airport']
                    departure_airport_exist = await db_conn.fetchval(f"SELECT * FROM airport "
                                                                     f"WHERE code = '{departure_airport['code']}' "
                                                                     f"AND name = '{departure_airport['name']}'")
                    if departure_airport_exist is None:
                        await db_conn.execute(
                            'INSERT INTO airport(code, name) VALUES($1, $2)',
                            departure_airport['code'], departure_airport['name'])
                        departure_airport = db_conn.fetchval(f"SELECT * FROM airport "
                                                             f"WHERE code = '{departure_airport['code']}' "
                                                             f"AND name = '{departure_airport['name']}'")
                    else:
                        departure_airport = departure_airport_exist



            except Exception as e:
                print(e)
                await transaction.rollback()
                raise
            else:
                await transaction.commit()

    print(data)
    return response.json(data)
