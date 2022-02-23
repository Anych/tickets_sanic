import datetime

import httpx
from cerberus import Validator


class SearchValidator:

    def __init__(self, data):
        self.data = data
        self.is_validated = True
        self.reason = str()
        self.v = Validator()

    async def prepare_data(self):
        validate_functions = (self.validate_cabin, self.origin_equal_destination,
                              self.search_if_origin_destination_exists, self.validate_date_format,
                              self.compare_dates, self.validate_passengers, self.validate_qty_of_passengers)
        try:
            for func in validate_functions:
                await func()
                if not self.is_validated:

                    return False
            return True
        except Exception as e:
            print(e)

            return False

    async def validate_cabin(self):
        self.v.schema = {'cabin': {'required': True, 'type': 'string', 'allowed': ['Economy', 'Business']}}
        self.is_validated = self.v.validate({'cabin': self.data['cabin']})

    async def origin_equal_destination(self):
        if self.data['origin'] == self.data['destination']:
            self.is_validated = False
        else:
            await self.validate_origin_and_destination()

    async def validate_origin_and_destination(self):
        places = (self.data['origin'], self.data['destination'])
        for place in places:
            self.v.schema = {'city': {'required': True, 'type': 'string', 'maxlength': 3, 'minlength': 3}}
            self.is_validated = self.v.validate({'city': place})

    async def search_if_origin_destination_exists(self):
        places = (self.data['origin'], self.data['destination'])
        for place in places:
            async with httpx.AsyncClient() as client:
                try:
                    cities = await client.get(
                        f'https://avia-api.k8s-test.aviata.team/cities/search?query={place}&limit=1000')
                    cities = cities.json()
                    for city in cities['items']:
                        if city['code'] == place:
                            self.is_validated = True
                            break
                        else:
                            self.is_validated = False
                    return self.is_validated
                except Exception as e:
                    print(e)
                    self.is_validated = False

    async def validate_date_format(self):
        self.v.schema = {'date': {'required': True, 'type': 'string', 'maxlength': 10, 'minlength': 10}}
        self.is_validated = self.v.validate({'date': self.data['dep_at']})
        if not self.is_validated:

            return
        if 'arr_at' in self.data.keys():
            self.is_validated = self.v.validate({'date': self.data['arr_at']})

    async def compare_dates(self):
        departure = datetime.datetime.strptime(self.data['dep_at'], '%Y-%m-%d').date()
        today = datetime.datetime.today().date()
        if today > departure:
            self.is_validated = False

            return
        if 'arr_at' in self.data.keys():
            arrive = datetime.datetime.strptime(self.data['arr_at'], '%Y-%m-%d').date()
            if departure > arrive:
                self.is_validated = False

    async def validate_passengers(self):
        self.v.schema = {'passenger_type': {'required': True, 'type': 'integer', 'min': 1, 'max': 9}}
        self.is_validated = self.v.validate({'passenger_type': self.data['adults']})

    async def validate_qty_of_passengers(self):
        if 'children' and 'infants' in self.data.keys():
            passengers_qty = self.data['adults'] + self.data['children'] + self.data['infants']
        elif 'infants' in self.data.keys():
            passengers_qty = self.data['adults'] + self.data['infants']
        elif 'children' in self.data.keys():
            passengers_qty = self.data['adults'] + self.data['children']
        else:
            passengers_qty = self.data['adults']
        self.v.schema = {'passengers_qty': {'type': 'integer', 'min': 1, 'max': 9}}
        passengers_qty = int(passengers_qty)
        self.is_validated = self.v.validate({'passengers_qty': passengers_qty})
