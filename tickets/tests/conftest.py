import os
import sys

import ujson
from pytest import fixture

from sanic import Sanic

from utils import load_file

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir))
sys.path.insert(0, PROJECT_ROOT)


@fixture
async def app():
    from code import app as sanic_app

    test_app = Sanic('test-app')
    test_app.router = sanic_app.app.router

    test_app.register_listener(sanic_app.init_before, 'before_server_start')
    test_app.register_listener(sanic_app.cleanup, 'after_server_stop')

    return test_app


@fixture
def search_data():
    return ujson.loads(load_file('tests/data/details_for_search.json'))


@fixture
def fake_uuid():
    return '557d187d-6465-4850-b4ea-6121752614f8'


@fixture
def search_response(fake_uuid):
    return {'search_id': fake_uuid}


@fixture
def providers_id():
    return '379011404402921475'


@fixture
def providers_offer():
    return load_file('tests/data/provider_response.json')


@fixture
def status_response():
    return {'status': 'DONE', 'Sabre': '-7558284433437330976', 'Amadeus': '379011404402921475'}


@fixture
def search_result_response(fake_uuid, providers_offer):
    providers_offer = ujson.loads(providers_offer)
    return {'search_id': fake_uuid, 'status': 'DONE', 'items': [providers_offer, providers_offer]}


@fixture
def booking_data():
    return ujson.loads(load_file('tests/data/data_for_booking.json'))


@fixture
def created_booking():
    return ujson.loads(load_file('tests/data/booking_created.json'))
