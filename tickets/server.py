from sanic import Sanic
from sanic.response import text, json

from tickets.directories.responds import booking, offer

app = Sanic('tickets')


@app.get('/')
async def hello_world(request):
    return text("Hello, world.")


@app.route('/search')
async def searching(request):
    data = {
        "id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da"
    }
    return json(data)


@app.route('/search/<search_id>')
def return_searching_by_id(request, search_id):
    data = {
        "search_id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da",
        "status": "PENDING",
        "items": []
    }
    return json(data)


@app.route('/offers/<offer_id>')
def return_offer_by_id(request, offer_id):
    return json(offer)


@app.route('/booking')
async def save_booking(request):
    return json(offer)


@app.route('/booking/<booking_id>')
def return_booking_by_id(request, booking_id):
    return json(booking)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
