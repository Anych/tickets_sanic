import httpx


class HTTPClient(httpx.AsyncClient):
    # Made for mocking
    # because sanic-testing also use httpx
    pass
