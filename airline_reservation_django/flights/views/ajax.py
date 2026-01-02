# flights/views/ajax.py
from django.http import JsonResponse
from ..models import Flight
from datetime import date

def distinct_list(field, **filters):
    return list(
        Flight.objects.filter(**filters)
        .values_list(field, flat=True)
        .distinct()
    )

def get_origin_countries(request):
    return JsonResponse(distinct_list("departure_country"), safe=False)

def get_airports_by_country(request):
    return JsonResponse(
        distinct_list("departure_city", departure_country=request.GET.get("country")),
        safe=False,
    )

def get_destination_countries(request):
    return JsonResponse(
        distinct_list("arrival_country",
                      departure_country=request.GET.get("origin_country"),
                      departure_city=request.GET.get("origin_city")),
        safe=False
    )

def get_destination_airports(request):
    return JsonResponse(
        distinct_list("arrival_city",
                      departure_country=request.GET.get("origin_country"),
                      departure_city=request.GET.get("origin_city"),
                      arrival_country=request.GET.get("dest_country")),
        safe=False
    )

def get_available_dates(request):
    dep = request.GET.get("departure_city")
    arr = request.GET.get("arrival_city")
    route_type = request.GET.get("type", "departure")
    today = date.today()

    if not dep or not arr:
        return JsonResponse([], safe=False)

    if route_type == "departure":
        qs = Flight.objects.filter(departure_city=dep, arrival_city=arr, date__gte=today)
    else:
        qs = Flight.objects.filter(departure_city=arr, arrival_city=dep, date__gte=today)

    return JsonResponse(
        [f.date.strftime("%Y-%m-%d") for f in qs.distinct()],
        safe=False
    )
