data = {
    "search_id": "1651317769443109666",
    "count": 20,
    "items": [
        {
            "id": "8a5118b7-dd4d-4761-b09e-208b88edcfbe",
            "flights": [
                {
                    "duration": 12300,
                    "segments": [
                        {
                            "operating_airline": "0K",
                            "flight_number": "748",
                            "equipment": "Airbus A330-300",
                            "cabin": "Economy",
                            "dep": {
                                "at": "2022-02-20T03:35:00+06:00",
                                "airport": {
                                    "code": "ALA",
                                    "name": "Алматы"
                                },
                                "terminal": "9"
                            },
                            "arr": {
                                "at": "2022-02-20T07:00:00+06:00",
                                "airport": {
                                    "code": "NQZ",
                                    "name": "Нур-Султан (Астана)"
                                },
                                "terminal": "7"
                            },
                            "baggage": None
                        }
                    ]
                },

            ],
            "price": {
                "amount": 36591,
                "currency": "KZT"
            },
            "refundable": 'false',
            "baggage": 'null',
            "cabin": "Economy",
            "airline": {
                "code": "0K",
                "name": "Kokshetau Airlines",
                "logo": None
            },
            "passengers": {
                "ADT": 1,
                "CHD": 0,
                "INF": 0
            },
            "type": "RT"
        },
        {
            "id": "d69e197a-2ad9-4836-8e89-a335b0282fe6",
            "flights": [
                {
                    "duration": 15300,
                    "segments": [
                        {
                            "operating_airline": "DV",
                            "flight_number": "699",
                            "equipment": "Airbus A300-600 B4",
                            "cabin": "Economy",
                            "dep": {
                                "at": "2022-02-20T03:00:00+06:00",
                                "airport": {
                                    "code": "ALA",
                                    "name": "Алматы"
                                },
                                "terminal": "2"
                            },
                            "arr": {
                                "at": "2022-02-20T07:15:00+06:00",
                                "airport": {
                                    "code": "NQZ",
                                    "name": "Нур-Султан (Астана)"
                                },
                                "terminal": "9"
                            },
                            "baggage": "20KG"
                        }
                    ]
                },
                {
                    "duration": 2400,
                    "segments": [
                        {
                            "operating_airline": "DV",
                            "flight_number": "880",
                            "equipment": "Boeing 737-400",
                            "cabin": "Economy",
                            "dep": {
                                "at": "2022-02-21T03:25:00+06:00",
                                "airport": {
                                    "code": "NQZ",
                                    "name": "Нур-Султан (Астана)"
                                },
                                "terminal": "6"
                            },
                            "arr": {
                                "at": "2022-02-21T04:05:00+06:00",
                                "airport": {
                                    "code": "ALA",
                                    "name": "Алматы"
                                },
                                "terminal": "8"
                            },
                            "baggage": "20KG"
                        }
                    ]
                }
            ],
            "price": {
                "amount": 92592,
                "currency": "KZT"
            },
            "refundable": True,
            "baggage": "20KG",
            "cabin": "Economy",
            "airline": {
                "code": "DV",
                "name": "SCAT",
                "logo": {
                    "url": "https://avia-api.k8s-test.aviata.team/img/5661-501f546c73c976a96cf0d18e600b4d7a.gif",
                    "width": 1416,
                    "height": 274
                }
            },
            "passengers": {
                "ADT": 1,
                "CHD": 0,
                "INF": 0
            },
            "type": "RT"
        },
    ]
}

for x in data['items']:
    print(x)

for x in data['items']:
    print(x['flights'])





# for flight in item['flights']:
#   await app.ctx.redis.hset(item['id'], 'duration', flight['duration'])
#   await app.ctx.redis.hget(item['id'], 'duration')
#   for segment in flight['segments']:
#     await app.ctx.redis.hset(item['id'], 'operating_airline', segment['operating_airline'])
#     await app.ctx.redis.hset(item['id'], 'flight_number', segment['flight_number'])
#     await app.ctx.redis.hset(item['id'], 'equipment', segment['equipment'])
#     await app.ctx.redis.hset(item['id'], 'cabin', segment['cabin'])
#     for dep in segment['dep']:
#       # await app.ctx.redis.hset(item['id'], 'at', dep['at'])
#       print(segment['dep'])
#       # for airport in dep['airport']:
#       #     await app.ctx.redis.hset(item['id'], 'code', airport['code'])
#       #     await app.ctx.redis.hset(item['id'], 'code', airport['code'])
#       #     print(airport['code'])
#     # await app.ctx.redis.hset(item['id'], 'baggage', segment['baggage'])