from ..constants import (
    SKEY_RETURN_ID, SKEY_PASSENGERS, SKEY_NUM_PAX, SKEY_DEP_ID,
    SKEY_SEAT_CLASS, SKEY_SELECTED_SEATS, SKEY_TOTAL_PRICE,
    SKEY_LUGGAGE, SKEY_EQUIPMENT
)

class BookingSession:
    def __init__(self, request):
        self.session = request.session

    @property
    def num_passengers(self):
        return self.session.get(SKEY_NUM_PAX, 1)

    @num_passengers.setter
    def num_passengers(self, value):
        self.session[SKEY_NUM_PAX] = value

    @property
    def passengers(self):
        return self.session.get(SKEY_PASSENGERS, [])

    @passengers.setter
    def passengers(self, value):
        self.session[SKEY_PASSENGERS] = value

    @property
    def return_flight_id(self):
        return self.session.get(SKEY_RETURN_ID)

    @return_flight_id.setter
    def return_flight_id(self, value):
        self.session[SKEY_RETURN_ID] = value

    @property
    def departure_flight_id(self):
        return self.session.get(SKEY_DEP_ID)

    @departure_flight_id.setter
    def departure_flight_id(self, value):
        self.session[SKEY_DEP_ID] = value

    @property
    def total_price(self):
        return float(self.session.get(SKEY_TOTAL_PRICE, 0.0))

    @total_price.setter
    def total_price(self, value):
        self.session[SKEY_TOTAL_PRICE] = float(value)

    def init_price(self, price):
        if SKEY_TOTAL_PRICE not in self.session:
            self.total_price = price
        return self.total_price

    @property
    def seat_class(self):
        return self.session.get(SKEY_SEAT_CLASS)

    @seat_class.setter
    def seat_class(self, value):
        self.session[SKEY_SEAT_CLASS] = value

    @property
    def selected_seats(self):
        return self.session.get(SKEY_SELECTED_SEATS, {})

    @selected_seats.setter
    def selected_seats(self, value):
        self.session[SKEY_SELECTED_SEATS] = value

    def set_extras(self, luggage, equipment):
        self.session[SKEY_LUGGAGE] = luggage
        self.session[SKEY_EQUIPMENT] = equipment

    def clear(self):
        keys = [
            SKEY_PASSENGERS, SKEY_NUM_PAX, SKEY_SELECTED_SEATS,
            SKEY_SEAT_CLASS, SKEY_TOTAL_PRICE, SKEY_RETURN_ID,
            SKEY_LUGGAGE, SKEY_EQUIPMENT, SKEY_DEP_ID
        ]
        for key in keys:
            self.session.pop(key, None)