import json


def get_fake_data(filename):
    with open(rf'{filename}', 'r') as json_file:
        json_object = json.load(json_file)
        return json_object
