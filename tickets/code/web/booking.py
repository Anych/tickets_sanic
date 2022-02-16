import json

from sanic import response


async def get_booking(request, booking_id):
    async with request.app.ctx.db_pool.acquire() as conn:
        if request.args:
            if 'email' in request.args:
                all_bookings = await conn.fetch(f"SELECT * FROM booking "
                                                f"WHERE email = '{request.args['email']}' "
                                                f"AND phone = '{request.args['phone']}' ORDER BY id")
                return response.json(all_bookings, dumps=json.dumps, default=str)
            else:

                pagination = await conn.fetch(f"SELECT * FROM booking "
                                              f"WHERE email = '{request.args['email']}' "
                                              f"AND phone = '{request.args['phone']}' ORDER BY id"
                                              f"LIMIT {request.args['limit']} OFFSET {request.args['page']} * 10")
                return response.json(pagination, dumps=json.dumps, default=str)
        else:
            details = await conn.fetch(f"SELECT * FROM booking WHERE booking_id = '{booking_id}'")
            details = [{'id': d['id'], 'booking_id': d['booking_id'], 'pnr': d['pnr'], 'expires_at': d['expires_at'],
                        'phone': d['phone'], 'email': d['email']
                        } for d in details][0]

            offer_details = await conn.fetch(f"SELECT * FROM offer WHERE booking_id = '{details['id']}'")
            offer_details = [{'id': d['id'], 'offer_id': d['offer_id'], 'flights': None, 'price': None,
                              'refundable': d['refundable'], 'baggage': d['baggage'], 'cabin': d['cabin'],
                              'airline': d['airline'], 'passengers': d['passengers'], 'type': d['type']
                              } for d in offer_details][0]

            flights_details = await conn.fetch(f"SELECT * FROM flight WHERE offer_id = '{offer_details['id']}'")
            flights_details = [{'id': d['id'], 'duration': d['duration']} for d in flights_details]

            segments = []
            for num in range(len(flights_details)):
                segment_details = await conn.fetch(f"SELECT * FROM segment "
                                                   f"WHERE flight_id = '{flights_details[num]['id']}'")
                segment_details = [{'id': d['id'], 'operating_airline': d['operating_airline'],
                                    'flight_number': d['flight_number'], 'equipment': d['equipment'],
                                    'cabin': d['cabin'], 'dep': d['departure_id'], 'arr': d['arrive_id'],
                                    'baggage': d['baggage']} for d in segment_details]

                departure_route = await conn.fetch(
                    f"SELECT * FROM route_point WHERE id = '{segment_details[0]['dep']}'")
                departure_route = [{'at': d['time_at'], 'airport': d['airport_id'],
                                    'terminal': d['terminal']} for d in departure_route]
                segment_details[0]['dep'] = departure_route
                departure_airport = await conn.fetch(f"SELECT * FROM airport "
                                                     f"WHERE id = '{departure_route[0]['airport']}'")
                departure_airport = [{'code': d['code'], 'name': d['name']} for d in departure_airport]
                departure_route[0]['airport'] = departure_airport
                segment_details[0]['dep'] = departure_route

                arrive_route = await conn.fetch(f"SELECT * FROM route_point "
                                                f"WHERE airport_id = '{segment_details[0]['arr']}'")
                arrive_route = [{'time_at': d['time_at'], 'airport': d['airport_id'],
                                 'terminal': d['terminal']} for d in arrive_route]
                arrive_airport = await conn.fetch(f"SELECT * FROM airport WHERE id = '{arrive_route[0]['airport']}'")
                arrive_airport = [{'code': d['code'], 'name': d['name']} for d in arrive_airport]
                arrive_route[0]['airport'] = arrive_airport
                segment_details[0]['arr'] = arrive_route
                del segment_details[0]['id']
                segments.append(segment_details[0])

            price = await conn.fetch(f"SELECT * FROM price WHERE offer_id = '{offer_details['id']}'")
            price = [{'price': int(d['price']), 'currency': d['currency']} for d in price]

            airline = await conn.fetch(f"SELECT * FROM airline WHERE id = '{offer_details['airline']}'")
            airline = [{'code': d['code'], 'name': d['name'], 'logo': d['logo_id']} for d in airline]

            logos = []
            for num in range(len(airline)):
                logo = await conn.fetch(f"SELECT * FROM logo WHERE id = '{airline[num]['logo']}'")
                logo = [{'url': d['url'], 'height': d['height'], 'weight': d['weight']} for d in logo]
                airline[num]['logo'] = logo[0]
                logos.append(airline[num])

            passengers_qty = await conn.fetch(f"SELECT * FROM passengers WHERE id = '{offer_details['passengers']}'")
            passengers_qty = [{'ADT': d['ADT'], 'CHD': d['CHD'], 'INF': d['INF']} for d in passengers_qty]

            passenger = await conn.fetch(f"SELECT * FROM passenger WHERE booking_id = '{details['id']}'")
            passenger = [{'gender': d['gender'], 'type': d['type'], 'first_name': d['first_name'],
                          'last_name': d['last_name'], 'date_of_birth': d['date_of_birth'],
                          'citizenship': d['citizenship'], 'document': d['document_id']} for d in passenger]

            passengers = []
            for num in range(len(passenger)):
                document = await conn.fetch(f"SELECT * FROM document WHERE id = '{passenger[num]['document']}'")
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
    async with request.app.ctx.db_pool.acquire() as conn:
        transaction = conn.transaction()
        await transaction.start()
        try:
            await conn.execute('INSERT INTO offer(id, name, person) VALUES($1, $2, $3)', 1, 'IT', 'Employer')
            await conn.execute('UPDATE employees SET department = $2 WHERE id = $1', 1, 'IT')
        except Exception as e:
            print(e)
            await transaction.rollback()
            raise
        else:
            await transaction.commit()
    return response.json({})
