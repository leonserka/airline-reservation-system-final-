from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
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
    available_dates = []

    dep = request.GET.get('departure_city')
    arr = request.GET.get('arrival_city')

    today = date.today()

    if dep and arr:
        flights_for_dates = Flight.objects.filter(
            departure_city=dep,
            arrival_city=arr,
            date__gte=today
        )
    else:
        flights_for_dates = Flight.objects.filter(date__gte=today)

    available_dates = [f.date.strftime("%Y-%m-%d") for f in flights_for_dates]

    if dep and arr:
        flights = flights_for_dates
        selected_date = request.GET.get('date')
        if selected_date:
            try:
                selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
                flights = flights.filter(date=selected_date_obj)
            except ValueError:
                pass
    else:
        flights = Flight.objects.none()

    routes_dict = {}
    for flight in Flight.objects.filter(date__gte=today):
        routes_dict.setdefault(flight.departure_city, [])
        if flight.arrival_city not in routes_dict[flight.departure_city]:
            routes_dict[flight.departure_city].append(flight.arrival_city)

    return render(request, 'flights/flight_list.html', {
        'form': form,
        'flights': flights,
        'available_dates': available_dates,
        'routes': routes_dict
    })
