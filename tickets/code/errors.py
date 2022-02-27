import traceback

from sanic import response
from sanic.exceptions import SanicException


class BookingCreateException(SanicException):

    status_code = 501


async def booking_create_error_handler(request, error):
    return response.json({'error': 'Ошибка создания бронирования в базе данных.'}, 501)


async def not_fount_error_handler(request, error):
    return response.json({'error': 'Не найдено.'}, 501)


async def server_error_handler(request, error: Exception):
    traceback.print_tb(error.__traceback__)
    status_code = error.status_code if hasattr(error, 'status_code') else 500
    return response.json({'error': str(error)}, status_code)
