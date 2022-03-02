from unittest.mock import MagicMock, AsyncMock

import pytest
from asyncpg import Connection

from code import client
from code.validators import PassengerValidator
from data.get_booking import test_booking


@pytest.mark.parametrize('value, expected_status', [
    ('2030-03-02T19:01:15.639813+06:00', 200),
    ('2010-03-02T19:01:15.639813+06:00', 404),
])
async def test_get_booking(app, fake_uuid, value, expected_status):

    test_booking[0]['expires_at'] = value
    Connection.fetch = AsyncMock(return_value=test_booking)

    request, response = await app.asgi_client.get(f'/booking/{fake_uuid}')

    assert request.method == 'GET'
    assert response.status == expected_status


async def test_create_booking_with_create_exception(app, mocker, booking_data):

    resp = MagicMock(status_code=200)

    mocker.patch.object(PassengerValidator, 'prepare_data', return_value=True)
    mocker.patch.object(client.HTTPClient, 'post', return_value=resp)

    request, response = await app.asgi_client.post('/booking', json=booking_data)

    assert request.method == 'POST'
    assert response.status == 501


async def test_create_booking(app, mocker, booking_data):

    resp = MagicMock(status_code=200)

    Connection.transaction.start = AsyncMock()
    Connection.execute = AsyncMock(return_value='INSERT 0 1')

    mocker.patch.object(PassengerValidator, 'prepare_data', return_value=True)
    mocker.patch.object(client.HTTPClient, 'post', return_value=resp)

    request, response = await app.asgi_client.post('/booking', json=booking_data)

    assert request.method == 'POST'
    assert response.status == 200


async def test_create_booking_with_cerberus_exception(app, mocker, booking_data):

    mocker.patch.object(PassengerValidator, 'prepare_data', return_value=False)
    request, response = await app.asgi_client.post('/booking', json=booking_data)

    assert request.method == 'POST'
    assert response.status == 500


async def test_create_booking_not_found_exception(app, mocker, booking_data):

    text = {"detail": "Not found"}

    mocker.patch.object(PassengerValidator, 'prepare_data', return_value=True)
    mocker.patch('code.utils.create_booking_in_provider', return_value=text)

    request, response = await app.asgi_client.post('/booking', json=booking_data)

    assert request.method == 'POST'
    assert response.status == 404


@pytest.mark.parametrize('args, expected_status', [
    ('limit=10&page=0', 200),
])
async def test_search_booking(app, args, expected_status):

    request, response = await app.asgi_client.get(f'/booking?{args}')

    assert request.method == 'GET'
    assert response.status == expected_status

