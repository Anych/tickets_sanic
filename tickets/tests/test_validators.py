import httpx
import pytest

from code import validators


@pytest.mark.parametrize('key, value', [
    ('cabin', 'First Class'),
    ('origin', 'NQZ'),
    ('dep_at', '31-05-22'),
    ('dep_at', '2000-01-01'),
    ('arr_at', '2000-01-01'),
])
async def test_tickets_validator_with_wrong_values(search_data, key, value):
    search_data[key] = value
    result = await validators.SearchValidator(search_data).prepare_data()

    assert result is False


async def test_search_validator_with_httpx_exception(search_data, mocker):
    mocker.patch.object(httpx.AsyncClient, 'get', side_effect=Exception)
    result = await validators.SearchValidator(search_data).prepare_data()

    assert result is False
