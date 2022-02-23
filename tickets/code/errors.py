from sanic import response
from sanic.exceptions import SanicException


class BookingCreateException(SanicException):

    status_code = 501


async def validation_error_handler(request, error):
    return response.json({'error': 'Ошибка валидации.'}, 422)


async def booking_create_error_handler(request, error):
    return response.json({'error': 'Ошибка создания бронирования в базе данных.'}, 501)


async def not_fount_error_handler(request, error):
    return response.json({'error': 'Не найдено.'}, 501)