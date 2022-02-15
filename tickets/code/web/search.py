import time

from sanic.response import HTTPResponse

from tickets.code.utils import search_in_providers


async def create_search(request):
    app = request.app
    asd = app.add_task(search_in_providers(request))
    return HTTPResponse()


