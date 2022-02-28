from unittest.mock import AsyncMock

import ujson
from aioredis import Redis
from sanic import exceptions


async def test_search_result(app, mocker, fake_uuid, providers_offer):
    get_resp = AsyncMock(return_value=providers_offer)
    mocker.patch.object(Redis, 'get', side_effect=get_resp)
    request, response = await app.asgi_client.get(f'/offers/{fake_uuid}')

    assert request.method == 'GET'
    assert response.status == 200
    assert response.json == ujson.loads(providers_offer)


async def test_search_result_with_exception(app, mocker, fake_uuid, providers_offer):
    get_resp = AsyncMock(side_effect=exceptions.NotFound)
    mocker.patch.object(Redis, 'get', side_effect=get_resp)
    request, response = await app.asgi_client.get(f'/offers/{fake_uuid}')

    assert request.method == 'GET'
    assert response.status == 404
