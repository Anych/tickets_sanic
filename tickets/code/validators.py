import httpx
from cerberus import Validator


class SearchValidator:

    def __init__(self, data):
        self.data = data
        self.is_validated = True
        self.v = Validator()
        self.reason = str()

    async def prepare_data(self):
        validate_functions = (self.validate_cabin, self.validate_origin_and_destination)
        try:
            for func in validate_functions:
                await func()
                if not self.is_validated:
                    return False, self.reason
            return True, self.reason
        except Exception as e:
            print(e)
            return False

    async def validate_cabin(self):
        self.v.schema = {'cabin': {'required': True, 'type': 'string', 'allowed': ['Economy', 'Business']}}
        is_validated = self.v.validate({'cabin': self.data['cabin']})
        if not is_validated:
            await self.not_validated('Не правильный формат кабины класса')

    async def validate_origin_and_destination(self):
        places = (self.data['origin'], self.data['destination'])
        if self.data['origin'] == self.data['destination']:
            await self.not_validated('Нельзя вылететь и приземлиться в одном месте')
        for place in places:

            self.v.schema = {'city': {'required': True, 'type': 'string', 'maxlength': 3}}
            is_validated = self.v.validate({'city': place})

            if not is_validated:
                if place == self.data['origin']:
                    await self.not_validated('Не правильный формат города вылета')
                else:
                    await self.not_validated('Не правильный формат города прилета')

            async with httpx.AsyncClient() as client:
                try:
                    cities = await client.get(
                        f'https://avia-api.k8s-test.aviata.team/cities/search?query={place}&limit=1000')
                    cities = cities.json()
                    for city in cities['items']:
                        if city['code'] == place:
                            self.is_validated = True
                            self.reason = str()
                            break
                        else:
                            self.is_validated = False
                    if not self.is_validated:
                        if place == self.data['origin']:
                            await self.not_validated('Не нашелся город вылета по заданным параметрам')
                        else:
                            await self.not_validated('Не нашелся город прилета по заданным параметрам')
                except Exception as e:
                    print(e)
                    self.is_validated = False
                    self.reason = e
                    return


    async def not_validated(self, reason):
        self.is_validated = False
        self.reason = reason
        return
