from sanic import Sanic
from sanic import response

from tickets.code.utils import get_fake_data


app = Sanic('tickets')


@app.route('/', methods=['GET'])
async def hello_world(request):
    return response.text("Hello, world.")


@app.route('/search', methods=['POST'])
async def create_search(request):
    static_data = {
        "id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da"
    }
    return response.json(static_data)


@app.route('/search/<search_id>', methods=['GET'])
async def receive_search_by_id(request, search_id):
    static_data = {
        "search_id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da",
        "status": "PENDING",
        "items": []
    }
    return response.json(static_data)


@app.route('/offers/<offer_id>', methods=['GET'])
async def receive_offer_by_id(request, offer_id):
    return response.json(get_fake_data('tickets/offer.json'))


@app.route('/booking', methods=['POST'])
async def create_booking(request):
    return response.json(get_fake_data('tickets/booking.json'))


@app.route('/booking/<booking_id>', methods=['GET'])
async def receive_booking_by_id(request, booking_id):
    return response.json(get_fake_data('tickets/booking.json'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
