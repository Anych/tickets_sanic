import datetime

import httpx
from cerberus import Validator


class TicketsValidator:

    def __init__(self, data):
        self.data = data
        self.is_validated = True
        self.v = Validator()
        self.validate_functions = tuple()

    async def prepare_data(self):
        try:
            for func in self.validate_functions:
                await func()
                if self.is_validated:
                    continue
                else:
                    return self.is_validated
            return self.is_validated
        except Exception as e:
            print(e)
            return False


class SearchValidator(TicketsValidator):

    def __init__(self, data):
        super().__init__(data)
        self.validate_functions = (self.validate_cabin, self.origin_equal_destination,
                                   self.search_if_origin_destination_exists, self.validate_date_format,
                                   self.compare_dates, self.validate_passengers, self.validate_qty_of_passengers)

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
        passengers_qty = self.data['adults'] + self.data['children'] + self.data['infants']
        self.v.schema = {'passengers_qty': {'type': 'integer', 'min': 1, 'max': 9}}
        passengers_qty = int(passengers_qty)
        self.is_validated = self.v.validate({'passengers_qty': passengers_qty})


class PassengerValidator(TicketsValidator):

    def __init__(self, data, countries):
        super().__init__(data)
        self.validate_functions = (self.validate_gender, self.validate_passenger_type, self.validate_citizenship,
                                   self.validate_first_and_last_name, self.validate_date_of_birth,
                                   self.validate_type_and_date_of_birth, self.validate_document_number,
                                   self.validate_document_expires_at, self.validate_iin)
        self.countries = countries
        self.document = self.data['document']
        self.prepare_data()

    async def validate_gender(self):
        self.v.schema = {'gender': {'required': True, 'type': 'string', 'allowed': ['M', 'F']}}
        self.is_validated = self.v.validate({'gender': self.data['gender']})

    async def validate_passenger_type(self):
        self.v.schema = {'passenger_type': {'required': True, 'type': 'string', 'allowed': ['ADT', 'CHD', 'INF']}}
        self.is_validated = self.v.validate({'passenger_type': self.data['type']})

    async def validate_citizenship(self):
        citizenship = self.data['citizenship']
        for country in self.countries:
            if country['code'] == citizenship:
                self.is_validated = True
                break
            else:
                self.is_validated = False
        return self.is_validated

    async def validate_first_and_last_name(self):
        self.v.schema = {'names': {'required': True, 'type': 'string'}}
        for name in self.data['first_name'], self.data['last_name']:
            self.is_validated = self.v.validate({'names': name})

    async def validate_date_of_birth(self):
        self.v.schema = {'date': {'required': True, 'type': 'string', 'maxlength': 10, 'minlength': 10}}
        self.is_validated = self.v.validate({'date': self.data['date_of_birth']})

    async def validate_type_and_date_of_birth(self):
        date_of_birth = datetime.datetime.strptime(self.data['date_of_birth'], '%Y-%m-%d').year
        today = datetime.datetime.today().year
        delta = today - date_of_birth
        if self.data['type'] == 'ADT' and delta < 15:
            self.is_validated = False
        elif self.data['type'] == 'CHD' and (delta < 2 or delta > 15):
            self.is_validated = False
        elif self.data['type'] == 'INF' and delta > 2:
            self.is_validated = False
        else:
            self.is_validated = True

    async def validate_document_number(self):
        self.v.schema = {'number': {'required': True, 'type': 'string', 'minlength': 5}}
        self.is_validated = self.v.validate({'number': self.document['number']})

    async def validate_document_expires_at(self):
        self.v.schema = {'date': {'required': True, 'type': 'string', 'maxlength': 10, 'minlength': 10}}
        self.is_validated = self.v.validate({'date': self.document['expires_at']})

    async def validate_iin(self):
        self.v.schema = {'iin': {'required': True, 'type': 'integer', 'maxlength': 12, 'minlength': 12}}
        self.is_validated = self.v.validate({'iin': int(self.document['iin'])})
