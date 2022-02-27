from unittest.mock import AsyncMock

from aioredis import Redis


def test_create_search_success(app, mocker, fake_uuid, search_data):
    mocker.patch('uuid.uuid1', return_value=fake_uuid)
    request, response = app.test_client.post('/search', json=search_data)

    assert request.method == 'POST'
    assert response.status == 200
    assert response.json == {'search_id': fake_uuid}


def test_create_search_with_cerberus_exception(app):
    request, response = app.test_client.post('/search')

    assert request.method == 'POST'
    assert response.status == 500


async def test_search_result(app, mocker, fake_uuid, providers_id, providers_offer,
                             status_response, search_result_response):
    hget_resp = AsyncMock(side_effect=[providers_id, providers_id, 'DONE'])
    get_resp = AsyncMock(return_value=providers_offer)
    hgetall_resp = AsyncMock(return_value=status_response)
    mocker.patch.object(Redis, 'hget', side_effect=hget_resp)
    mocker.patch.object(Redis, 'get', side_effect=get_resp)
    mocker.patch.object(Redis, 'hgetall', side_effect=hgetall_resp)
    request, response = await app.asgi_client.get(f'/search/{fake_uuid}')

    assert request.method == 'GET'
    assert response.status == 200
    assert response.json == search_result_response
