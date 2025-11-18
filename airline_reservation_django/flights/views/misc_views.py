from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse
from ..forms import FlightForm, RegisterForm, FlightSearchForm
from ..models import Flight
from datetime import date, datetime

def distinct_list(field, **filters):
    return list(
        Flight.objects.filter(**filters)
        .values_list(field, flat=True)
        .distinct()
    )

def valid_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except:
        return None

def home(request):
    return render(request, "flights/home.html")

def create_flight(request):
    form = FlightForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("flight_list")
    return render(request, "flights/create_flight.html", {"form": form})

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_staff = False
        user.save()
        login(request, user)
        return redirect("home")
    return render(request, "flights/register.html", {"form": form})

def custom_logout(request):
    logout(request)
    return redirect("home")

def flight_list(request):
    today = date.today()
    dep = request.GET.get("departure_city")
    arr = request.GET.get("arrival_city")
    dep_date = valid_date(request.GET.get("departure_date"))
    ret_date = valid_date(request.GET.get("return_date"))
    flights = Flight.objects.none()
    returns = Flight.objects.none()
    show = False

    if dep and arr:
        show = True
        base = Flight.objects.filter(
            departure_city=dep,
            arrival_city=arr,
            date__gte=today
        )

        flights = base.filter(date=dep_date) if dep_date else base

        if ret_date:
            returns = Flight.objects.filter(
                departure_city=arr,
                arrival_city=dep,
                date=ret_date,
                date__gte=today
            )

    routes = {}
    for f in Flight.objects.filter(date__gte=today):
        routes.setdefault(f.departure_city, set()).add(f.arrival_city)
    routes = {k: list(v) for k, v in routes.items()}

    return render(request, "flights/flight_list.html", {
        "form": FlightSearchForm(request.GET or None),
        "flights": flights,
        "return_flights": returns,
        "available_dates": [f.date.strftime("%Y-%m-%d") for f in flights],
        "routes": routes,
        "show_results": show,
    })

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
