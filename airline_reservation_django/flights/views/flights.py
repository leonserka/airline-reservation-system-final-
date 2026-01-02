from django.shortcuts import render, redirect
from ..forms import FlightForm, FlightSearchForm
from ..services.flight_service import FlightService

def home(request):
    return render(request, "flights/home.html")

def create_flight(request):
    form = FlightForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("flight_list")
    return render(request, "flights/create_flight.html", {"form": form})

def flight_list(request):
    dep = request.GET.get("departure_city")
    arr = request.GET.get("arrival_city")
    dep_date = request.GET.get("departure_date")
    ret_date = request.GET.get("return_date")
    search_data = FlightService.search(dep, arr, dep_date, ret_date) 
    routes = FlightService.get_routes()

    context = {
        "form": FlightSearchForm(request.GET or None),
        "routes": routes,
        **search_data 
    }
    return render(request, "flights/flight_list.html", context)