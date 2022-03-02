from unittest.mock import AsyncMock, MagicMock

import aioredis
import pytest
import ujson

from code import settings, client
from code.utils import get_currency_rates, get_data_from_provider, change_currency_to_kzt
from utils import load_file


async def test_get_currency_rates(mocker):

    redis = await aioredis.from_url(settings.REDIS_URL)
    hgetall_resp = AsyncMock(return_value={'AUD': '{"description":"317.95","quant":"1"}'})
    mocker.patch.object(aioredis.Redis, 'hgetall', side_effect=hgetall_resp)

    currencies = await get_currency_rates(redis)

    assert currencies == {'AUD': {'description': '317.95', 'quant': '1'}}


async def test_get_currency_rates_with_exception(mocker):

    redis = await aioredis.from_url(settings.REDIS_URL)
    hgetall_resp = AsyncMock(return_value={'AUD': '{"description":"317.95","quant":"1"}'})
    mocker.patch.object(aioredis.Redis, 'hgetall', side_effect=hgetall_resp)
    mocker.patch.object(ujson, 'loads', side_effect=Exception)

    currencies = await get_currency_rates(redis)

    assert currencies == {}


async def test_get_data_from_provider(mocker):

    resp = MagicMock(status_code=200, text='Request')
    mocker.patch.object(client.HTTPClient, 'post', return_value=resp)

    data = await get_data_from_provider('data')

    assert data.text == 'Request'


async def test_get_data_from_provider_with_exception(mocker):

    mocker.patch.object(client.HTTPClient, 'post', side_effect=Exception)

    data = await get_data_from_provider('data')

    assert data is None


@pytest.mark.parametrize('key', [
    'KZT',
    'EUR',
])
async def test_change_currency_to_kzt(mocker, key):

    offer = ujson.loads(load_file('tests/data/offers.json'))
    offer['price']['currency'] = key

    mocker.patch('code.utils.get_currency_rates', return_value={'EUR': {'description': '317.95', 'quant': '1'}})
    data = await change_currency_to_kzt([offer], AsyncMock())

    assert data is None
