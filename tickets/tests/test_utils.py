from unittest.mock import AsyncMock, Mock, MagicMock

from aioredis import Redis

from code.utils import get_currency_rates

#
# async def test_currency_rates(app, mocker):
#     currency_dict = {'AUD': 400}
#     redis = MagicMock()
#     hgetall_resp = AsyncMock(return_value=currency_dict)
#     mocker.patch.object(Redis, 'hgetall', side_effect=hgetall_resp)
#     currencies = await get_currency_rates(redis)
#
#     assert currencies == currency_dict
