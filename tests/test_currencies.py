from unittest.mock import MagicMock


from anuarbek.code import client
from anuarbek.code.currencies import update_rate_exchange
from utils import load_file


async def test_rate_exchange(app, mocker):

    provider_response = load_file('anuarbek/tests/data/rates_provider_response.xml')
    resp = MagicMock(status_code=200, text=provider_response)
    mocker.patch.object(client.HTTPClient, 'get', return_value=resp)

    rates = await update_rate_exchange()

    assert rates is None
