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
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('flight_list')
    else:
        form = FlightForm()
    return render(request, 'flights/create_flight.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'flights/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

def flight_list(request):
    today = date.today()
    dep = request.GET.get('departure_city')
    arr = request.GET.get('arrival_city')
    dep_date_str = request.GET.get('departure_date')
    ret_date_str = request.GET.get('return_date')
    dep_date = valid_date(dep_date_str)
    ret_date = valid_date(ret_date_str)
    flights = Flight.objects.none()
    return_flights = Flight.objects.none()
    show_results = False
    available_dates = []

    if dep and arr:
        show_results = True

        base_qs = Flight.objects.filter(
            departure_city=dep,
            arrival_city=arr,
            date__gte=today
        )

        available_dates = [f.date.strftime("%Y-%m-%d") for f in base_qs]

        if dep_date:
            flights = base_qs.filter(date=dep_date)
        else:
            flights = base_qs

    if dep and arr and ret_date:
        return_flights = Flight.objects.filter(
            departure_city=arr,
            arrival_city=dep,
            date__gte=today,
            date=ret_date
        )

    routes = {}
    for f in Flight.objects.filter(date__gte=today):
        routes.setdefault(f.departure_city, set()).add(f.arrival_city)

    routes = {k: list(v) for k, v in routes.items()}

    return render(request, 'flights/flight_list.html', {
        'form': FlightSearchForm(request.GET or None),
        'flights': flights,
        'return_flights': return_flights,
        'available_dates': available_dates,
        'routes': routes,
        'show_results': show_results,
    })

def get_airports_by_country(request):
    country = request.GET.get("country")
    return JsonResponse(
        distinct_list("departure_city", departure_country=country),
        safe=False
    )

def get_destination_countries(request):
    return JsonResponse(
        distinct_list("arrival_country",
            departure_country=request.GET.get("origin_country"),
            departure_city=request.GET.get("origin_city"),
        ),
        safe=False
    )

def get_destination_airports(request):
    return JsonResponse(
        distinct_list(
            "arrival_city",
            departure_country=request.GET.get("origin_country"),
            departure_city=request.GET.get("origin_city"),
            arrival_country=request.GET.get("dest_country"),
        ),
        safe=False
    )

def get_origin_countries(request):
    return JsonResponse(
        distinct_list("departure_country"),
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
        qs = Flight.objects.filter(
            departure_city=dep,
            arrival_city=arr,
            date__gte=today
        )
    else:
        qs = Flight.objects.filter(
            departure_city=arr,
            arrival_city=dep,
            date__gte=today
        )

    return JsonResponse(
        [f.date.strftime("%Y-%m-%d") for f in qs.distinct()],
        safe=False
    )
