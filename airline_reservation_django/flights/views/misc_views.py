from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse
from ..forms import FlightForm, RegisterForm, FlightSearchForm
from ..models import Flight
from datetime import date, datetime

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
    form = FlightSearchForm(request.GET or None)
    flights = Flight.objects.none()
    return_flights = Flight.objects.none()
    show_results = False  

    dep = request.GET.get('departure_city')
    arr = request.GET.get('arrival_city')
    departure_date = request.GET.get('departure_date')
    return_date = request.GET.get('return_date')

    today = date.today()

    if dep and arr:
        show_results = True 

        base_qs = Flight.objects.filter(
            departure_city=dep,
            arrival_city=arr,
            date__gte=today
        )

        available_dates = [f.date.strftime("%Y-%m-%d") for f in base_qs]

        if departure_date:
            try:
                dep_date_obj = datetime.strptime(departure_date, "%Y-%m-%d").date()
                flights = base_qs.filter(date=dep_date_obj)
            except ValueError:
                flights = base_qs
        else:
            flights = base_qs
    else:
        available_dates = []

    if dep and arr and return_date:
        try:
            ret_date_obj = datetime.strptime(return_date, "%Y-%m-%d").date()
            return_flights = Flight.objects.filter(
                departure_city=arr, 
                arrival_city=dep,
                date__gte=today,
                date=ret_date_obj
            )
        except ValueError:
            pass

    routes_dict = {}
    for flight in Flight.objects.filter(date__gte=today):
        routes_dict.setdefault(flight.departure_city, [])
        if flight.arrival_city not in routes_dict[flight.departure_city]:
            routes_dict[flight.departure_city].append(flight.arrival_city)

    return render(request, 'flights/flight_list.html', {
        'form': form,
        'flights': flights,
        'return_flights': return_flights,
        'available_dates': available_dates,
        'routes': routes_dict,
        'show_results': show_results, 
    })

def get_airports_by_country(request):
    country = request.GET.get("country")
    airports = (
        Flight.objects.filter(departure_country=country)
        .values_list("departure_city", flat=True)
        .distinct()
    )
    return JsonResponse(list(airports), safe=False)


def get_destination_countries(request):
    origin_country = request.GET.get("origin_country")
    origin_city = request.GET.get("origin_city")

    countries = (
        Flight.objects.filter(
            departure_country=origin_country,
            departure_city=origin_city,
        )
        .values_list("arrival_country", flat=True)
        .distinct()
    )
    return JsonResponse(list(countries), safe=False)

def get_destination_airports(request):
    origin_country = request.GET.get("origin_country")
    origin_city = request.GET.get("origin_city")
    dest_country = request.GET.get("dest_country")

    airports = (
        Flight.objects.filter(
            departure_country=origin_country,
            departure_city=origin_city,
            arrival_country=dest_country,
        )
        .values_list("arrival_city", flat=True)
        .distinct()
    )
    return JsonResponse(list(airports), safe=False)


def get_origin_countries(request):
    countries = (
        Flight.objects.exclude(departure_country__isnull=True)
        .exclude(departure_country__exact="")
        .values_list("departure_country", flat=True)
        .distinct()
    )
    return JsonResponse(list(countries), safe=False)

def get_available_dates(request):
    dep = request.GET.get("departure_city")
    arr = request.GET.get("arrival_city")
    route_type = request.GET.get("type", "departure") 
    today = date.today()

    if not dep or not arr:
        return JsonResponse([], safe=False)

    if route_type == "departure":
        flights = Flight.objects.filter(
            departure_city=dep,
            arrival_city=arr,
            date__gte=today,
        )
    else:  
        flights = Flight.objects.filter(
            departure_city=arr,
            arrival_city=dep,
            date__gte=today,
        )

    dates = [f.date.strftime("%Y-%m-%d") for f in flights.distinct()]
    return JsonResponse(dates, safe=False)
