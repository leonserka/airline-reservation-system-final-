from datetime import datetime, date
from ..models import Flight

class FlightService:
    @staticmethod
    def valid_date(value):
        """Pomoćna metoda za parsiranje datuma"""
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    @staticmethod
    def search(dep_city, arr_city, dep_date_str, ret_date_str):
        """
        Vraća rezultate pretrage letova.
        Koristi se u flights/views/flights.py
        """
        today = date.today()
        dep_date = FlightService.valid_date(dep_date_str)
        ret_date = FlightService.valid_date(ret_date_str)

        flights = Flight.objects.none()
        returns = Flight.objects.none()
        show_results = False

        if dep_city and arr_city:
            show_results = True
            base = Flight.objects.filter(
                departure_city=dep_city,
                arrival_city=arr_city,
                date__gte=today
            )

            # Ako je zadan datum, filtriraj po njemu, inače daj sve buduće
            flights = base.filter(date=dep_date) if dep_date else base

            # Povratni letovi
            if ret_date:
                returns = Flight.objects.filter(
                    departure_city=arr_city,
                    arrival_city=dep_city,
                    date=ret_date,
                    date__gte=today
                )

        return {
            "flights": flights,
            "return_flights": returns,
            "show_results": show_results,
            "available_dates": [f.date.strftime("%Y-%m-%d") for f in flights]
        }

    @staticmethod
    def get_routes():
        """
        Vraća rječnik ruta { 'PolazniGrad': ['Odredište1', 'Odredište2'] }
        Koristi se u FlightSearchForm i viewovima.
        """
        today = date.today()
        routes = {}
        # Optimizirani dohvat samo potrebnih polja
        qs = Flight.objects.filter(date__gte=today).values_list('departure_city', 'arrival_city').distinct()
        
        for dep, arr in qs:
            routes.setdefault(dep, set()).add(arr)
            
        return {k: list(v) for k, v in routes.items()}

    # --- AJAX Helper Metode ---

    @staticmethod
    def _distinct_list(field, **filters):
        """Privatna pomoćna metoda za dohvat jedinstvenih vrijednosti."""
        return list(
            Flight.objects.filter(**filters)
            .values_list(field, flat=True)
            .distinct()
        )

    @staticmethod
    def get_origin_countries():
        return FlightService._distinct_list("departure_country")

    @staticmethod
    def get_airports_by_country(country):
        return FlightService._distinct_list("departure_city", departure_country=country)

    @staticmethod
    def get_destination_countries(origin_country, origin_city):
        return FlightService._distinct_list(
            "arrival_country",
            departure_country=origin_country,
            departure_city=origin_city
        )

    @staticmethod
    def get_destination_airports(origin_country, origin_city, dest_country):
        return FlightService._distinct_list(
            "arrival_city",
            departure_country=origin_country,
            departure_city=origin_city,
            arrival_country=dest_country
        )

    @staticmethod
    def get_available_dates_for_route(dep_city, arr_city, route_type="departure"):
        today = date.today()
        if not dep_city or not arr_city:
            return []

        if route_type == "departure":
            qs = Flight.objects.filter(departure_city=dep_city, arrival_city=arr_city, date__gte=today)
        else:
            qs = Flight.objects.filter(departure_city=arr_city, arrival_city=dep_city, date__gte=today)

        return [f.date.strftime("%Y-%m-%d") for f in qs.distinct("date")]