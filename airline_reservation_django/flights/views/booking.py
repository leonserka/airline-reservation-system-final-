from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import json
from ..models import Flight, Ticket
from ..forms import PassengerForm
from ..constants import SEAT_PRICES, LUGGAGE, EQUIPMENT
from ..services.seatmap_service import SeatmapService
from ..services.booking_service import BookingService
from ..services.booking_session import BookingSession

def get_return_flight(bs):
    rid = bs.return_flight_id
    return Flight.objects.filter(id=rid).first() if rid else None

@login_required
def book_step1(request, flight_id):
    bs = BookingSession(request)
    flight = get_object_or_404(Flight, id=flight_id)
    if request.GET.get("return_id"):
        bs.return_flight_id = request.GET.get("return_id")
    return_flight = get_return_flight(bs) 
    num_passengers = int(request.GET.get("pax", bs.num_passengers))

    if request.method == "POST":
        forms = [PassengerForm(request.POST, prefix=str(i)) for i in range(num_passengers)]
        if all(f.is_valid() for f in forms):
            bs.passengers = [f.cleaned_data for f in forms]
            bs.num_passengers = num_passengers
            bs.departure_flight_id = flight.id
            return redirect("book_step2", flight_id=flight.id)
    else:
        forms = [PassengerForm(prefix=str(i)) for i in range(num_passengers)]

    return render(request, "flights/book_step1.html", {
        "flight": flight,
        "return_flight": return_flight,
        "passenger_forms": forms,
        "num_passengers": num_passengers,
    })

@login_required
def book_step2(request, flight_id):
    bs = BookingSession(request)
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(bs)

    if request.method == "POST":
        seat_class = request.POST.get("seat_class")
        bs.seat_class = seat_class
        dep_price = flight.price + SEAT_PRICES.get(seat_class, 0)
        ret_price = return_flight.price + SEAT_PRICES.get(seat_class, 0) if return_flight else 0
        bs.total_price = float(dep_price + ret_price)

        return redirect("book_step3", flight_id=flight.id)

    seat_options = [{"name": k, "price": v} for k, v in SEAT_PRICES.items()]

    return render(request, "flights/book_step2.html", {
        "flight": flight,
        "return_flight": return_flight,
        "seat_options": seat_options,
        "total_price": flight.price,
    })

@login_required
def book_step3(request, flight_id):
    bs = BookingSession(request)
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(bs)
    
    num_passengers = bs.num_passengers
    all_selected = bs.selected_seats
    selected = all_selected.get(str(flight_id), [])

    taken = set(
        Ticket.objects.filter(flight=flight)
        .values_list("seat_number", flat=True)
    )

    seat_positions = SeatmapService.build_seat_positions(
        total_seats=flight.total_seats,
        taken_seats=set(map(str, taken)),
        selected_seats=set(map(str, selected)),
        seats_per_row=4,
    )

    if request.method == "POST":
        pick = request.POST.get("selected_seat")
        if pick and pick not in selected:
            selected.append(pick)
            all_selected[str(flight_id)] = selected
            bs.selected_seats = all_selected

        if len(selected) >= num_passengers:
            if return_flight and str(return_flight.id) not in all_selected:
                return redirect("book_step3", flight_id=return_flight.id)
            return redirect("book_step4", flight_id=flight.id)

    return render(request, "flights/book_step3.html", {
        "flight": flight,
        "return_flight": return_flight,
        "seat_positions": seat_positions,
        "selected_seats": selected,
        "num_passengers": num_passengers,
        "remaining": num_passengers - len(selected),
        "total_price": bs.total_price or float(flight.price),
    })

@login_required
def book_step4(request, flight_id):
    bs = BookingSession(request)
    flight = get_object_or_404(Flight, id=flight_id)
    total = bs.init_price(float(flight.price))

    if request.method == "POST":
        lug = request.POST.get("luggage_option")
        eq = request.POST.get("equipment_option")
        extra = LUGGAGE.get(lug, 0) + EQUIPMENT.get(eq, 0)
        bs.set_extras(lug, eq)
        bs.total_price = total + extra

        return redirect("book_step5", flight_id=flight.id)

    return render(request, "flights/book_step4.html", {
        "flight": flight,
        "total_price": total,
    })

@login_required
def book_step5(request, flight_id):
    bs = BookingSession(request)
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(bs)
    passengers = bs.passengers
    seat_class = bs.seat_class
    all_selected = bs.selected_seats
    total_price = bs.init_price(float(flight.price))

    if request.method == "GET":
        return render(request, "flights/book_step5.html", {
            "flight": flight,
            "return_flight": return_flight,
            "total_price": total_price,
            "PAYPAL_CLIENT_ID": getattr(settings, "PAYPAL_CLIENT_ID", ""),
        })

    try:
        json.loads(request.body)
    except Exception:
        return JsonResponse({"status": "error", "msg": "Invalid JSON"})
    result = BookingService.process_booking(
        user=request.user,
        flight=flight,
        return_flight=return_flight,
        passengers=passengers,
        seat_class=seat_class,
        all_selected_seats=all_selected,
        total_price=total_price
    )

    if result["status"] == "ok":
        bs.clear() 
    return JsonResponse(result)

@login_required
def book_success(request):
    tickets = Ticket.objects.filter(purchased_by=request.user).order_by("-id")[:10]
    return render(request, "flights/book_success.html", {"tickets": tickets})