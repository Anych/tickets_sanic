from unittest.mock import AsyncMock


async def test_create_search_(app, mocker):
    request, response = await app.asgi_client.post('/search')
    assert request.method == 'POST'
    assert response.status == 200
