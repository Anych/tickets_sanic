import asyncio

from cerberus import Validator


class SearchValidator:

    def __init__(self, search_data):
        self.search_data = search_data
        self.is_validated = True
        self.prepare_data()

    def prepare_data(self):
        validate_functions = (self.validate_cabin(), self.validate_origin_and_destination())
        try:
            for func in validate_functions:
                is_validated = func()
                if not is_validated:
                    return False
        except Exception as e:
            print(e)
            return False

    def validate_cabin(self):
        v = Validator()
        v.schema = {'cabin': {'required': True, 'type': 'string', 'allowed': ['Economy', 'Business']}}
        is_validated = v.validate({'cabin': self.search_data['cabin']})
        return is_validated

    def validate_origin_and_destination(self):

        places = (self.search_data['origin'], self.search_data['destination'])
        if places[0] == places[1]:
            return False
        else:
            for place in places:
                v = Validator()
                v.schema = {'city': {'required': True, 'type': 'string', 'maxlength': 3}}
                is_validated = v.validate({'city': place})
                if not is_validated:
                    return False, place
