from datetime import date, datetime
from django.shortcuts import render, redirect
from ..forms import FlightForm, FlightSearchForm
from ..models import Flight

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
