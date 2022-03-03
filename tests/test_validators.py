import httpx
import pytest

from code import validators


async def test_tickets_validator_success(search_data):

    result = await validators.SearchValidator(search_data).prepare_data()

    assert result is True


@pytest.mark.parametrize('key, value', [
    ('cabin', 'First Class'),
    ('origin', 'NQZ'),
    ('dep_at', '31-05-22'),
    ('dep_at', '2000-01-01'),
    ('arr_at', '2000-01-01'),
])
async def test_search_validator_with_wrong_values(search_data, key, value):
    search_data[key] = value
    result = await validators.SearchValidator(search_data).prepare_data()

    assert result is False


async def test_search_validator_with_httpx_exception(search_data, mocker):
    mocker.patch.object(httpx.AsyncClient, 'get', side_effect=Exception)
    result = await validators.SearchValidator(search_data).prepare_data()

    assert result is False


async def test_passenger_validator_success(booking_data):

    passengers = booking_data['passengers'][0]
    result = await validators.PassengerValidator(passengers).prepare_data()

    assert result is True


@pytest.mark.parametrize('key, value', [
    ('gender', 'A'),
    ('type', 'ADE'),
    ('citizenship', 'UI'),
    ('first_name', None),
    ('date_of_birth', '92-05-02'),
    ('date_of_birth', '2020-05-02'),
])
async def test_passenger_validator_with_wrong_values(booking_data, key, value):

    passengers = booking_data['passengers'][0]
    passengers[key] = value

    result = await validators.PassengerValidator(passengers).prepare_data()

    assert result is False


@pytest.mark.parametrize('type_value, date_of_birth', [
    ('CHD', '1992-05-02'),
    ('CHD', '2022-01-01'),
    ('INF', '1992-05-02'),
])
async def test_passenger_validator_with_wrong_age(booking_data, type_value, date_of_birth):

    passengers = booking_data['passengers'][0]
    passengers['type'] = type_value
    passengers['date_of_birth'] = date_of_birth

    result = await validators.PassengerValidator(passengers).prepare_data()

    assert result is False
