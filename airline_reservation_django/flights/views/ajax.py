from django.http import JsonResponse
from ..services.flight_service import FlightService

def get_origin_countries(request):
    data = FlightService.get_origin_countries()
    return JsonResponse(data, safe=False)

def get_airports_by_country(request):
    country = request.GET.get("country")
    data = FlightService.get_airports_by_country(country)
    return JsonResponse(data, safe=False)

def get_destination_countries(request):
    origin_country = request.GET.get("origin_country")
    origin_city = request.GET.get("origin_city")
    data = FlightService.get_destination_countries(origin_country, origin_city)
    return JsonResponse(data, safe=False)

def get_destination_airports(request):
    origin_country = request.GET.get("origin_country")
    origin_city = request.GET.get("origin_city")
    dest_country = request.GET.get("dest_country")
    
    data = FlightService.get_destination_airports(origin_country, origin_city, dest_country)
    return JsonResponse(data, safe=False)

def get_available_dates(request):
    dep = request.GET.get("departure_city")
    arr = request.GET.get("arrival_city")
    route_type = request.GET.get("type", "departure")
    
    data = FlightService.get_available_dates_for_route(dep, arr, route_type)
    return JsonResponse(data, safe=False)