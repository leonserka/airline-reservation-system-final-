from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction, IntegrityError
import json
from ..models import Flight, Ticket
from ..forms import PassengerForm
from ..utils.pdf_generator import generate_receipt_pdf


SEAT_PRICES = {'BASIC': 0, 'REGULAR': 30, 'PLUS': 45}
LUGGAGE = {'10kg': 20, '20kg': 30, '23kg': 40}
EQUIPMENT = {'sports': 40, 'music': 50, 'baby': 10}

def get_return_flight(request):
    rid = request.session.get("return_id")
    return Flight.objects.filter(id=rid).first() if rid else None

@login_required
def book_step1(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(request)

    if request.GET.get("return_id"):
        request.session["return_id"] = request.GET.get("return_id")

    num_passengers = int(request.GET.get("pax", request.session.get("num_passengers", 1)))

    if request.method == "POST":
        forms = [PassengerForm(request.POST, prefix=str(i)) for i in range(num_passengers)]
        if all(f.is_valid() for f in forms):
            request.session["passengers"] = [f.cleaned_data for f in forms]
            request.session["num_passengers"] = num_passengers
            request.session["departure_id"] = flight.id
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
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(request)

    if request.method == "POST":
        seat_class = request.POST.get("seat_class")
        request.session["seat_class"] = seat_class
        dep_price = flight.price + SEAT_PRICES.get(seat_class, 0)
        ret_price = return_flight.price + SEAT_PRICES.get(seat_class, 0) if return_flight else 0
        request.session["total_price"] = float(dep_price + ret_price)

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
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(request)
    num_passengers = request.session.get("num_passengers", 1)
    all_selected = request.session.get("selected_seats", {})
    selected = all_selected.get(str(flight_id), [])
    taken = list(
        Ticket.objects.filter(flight=flight)
        .values_list("seat_number", flat=True)
    )
    seat_positions = []
    seats_per_row = 4
    total_rows = flight.total_seats // seats_per_row

    for r in range(1, total_rows + 1):
        row = {"left": [], "right": []}
        for s in range(1, seats_per_row + 1):
            seat_id = (r - 1) * seats_per_row + s
            pos = {
                "seat_id": seat_id,
                "top": 105 + (r - 1) * 25.10,
                "left": (
                    409 if s in [1, 2] else 380
                ) + (0 if s % 2 == 1 else 24),
                "occupied": str(seat_id) in taken or str(seat_id) in selected,
        }
            (row["left"] if s <= 2 else row["right"]).append(pos)
        seat_positions.append(row)

    if request.method == "POST":
        pick = request.POST.get("selected_seat")
        if pick and pick not in selected:
            selected.append(pick)
            all_selected[str(flight_id)] = selected
            request.session["selected_seats"] = all_selected

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
        "total_price": request.session.get("total_price", float(flight.price)),
    })

@login_required
def book_step4(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    total = request.session.get("total_price", float(flight.price))

    if request.method == "POST":
        lug = request.POST.get("luggage_option")
        eq = request.POST.get("equipment_option")
        extra = LUGGAGE.get(lug, 0) + EQUIPMENT.get(eq, 0)
        request.session["selected_luggage"] = lug
        request.session["selected_equipment"] = eq
        request.session["total_price"] = total + extra

        return redirect("book_step5", flight_id=flight.id)

    return render(request, "flights/book_step4.html", {
        "flight": flight,
        "total_price": total,
    })

@login_required
def book_step5(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(request)

    passengers = request.session.get("passengers", [])
    seat_class = request.session.get("seat_class")
    all_selected = request.session.get("selected_seats", {})
    total_price = float(request.session.get("total_price", flight.price))

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

    try:
        with transaction.atomic():
            for fl in filter(None, [flight, return_flight]):
                selected = all_selected.get(str(fl.id), [])
                taken = set(
                    Ticket.objects.select_for_update()
                    .filter(flight=fl)
                    .values_list("seat_number", flat=True)
                )
                for seat in selected:
                    if seat in taken:
                        return JsonResponse({"status": "seat_taken", "seat": seat})

            for i, pax in enumerate(passengers):
                for fl in filter(None, [flight, return_flight]):
                    seats = all_selected.get(str(fl.id), [])
                    Ticket.objects.create(
                        flight=fl,
                        passenger_name=pax["passenger_name"],
                        passenger_surname=pax["passenger_surname"],
                        id_number=pax["id_number"],
                        email=pax["email"],
                        phone_number=pax["phone_number"],
                        country_code=pax["country_code"],
                        seat_class=seat_class,
                        seat_number=seats[i] if i < len(seats) else None,
                        price_paid=fl.price,
                        payment_method="PayPal",
                        purchased_by=request.user,
                    )
                    fl.available_seats -= 1
                    fl.save()

    except IntegrityError:
        return JsonResponse({"status": "seat_taken", "seat": "unknown"})

    pdf_buffer, total_sum = generate_receipt_pdf(flight, passengers, seat_class, request.user)

    email = EmailMessage(
        subject="Your Airline Receipt",
        body=f"Thank you! Total paid: €{total_sum:.2f}",
        from_email="Airline <no-reply@airline.com>",
        to=[request.user.email],
    )
    email.attach("receipt.pdf", pdf_buffer.getvalue(), "application/pdf")
    email.send()

    for key in [
        "passengers", "num_passengers", "selected_seats",
        "seat_class", "total_price", "return_id"
    ]:
        request.session.pop(key, None)

    return JsonResponse({"status": "ok"})

@login_required
def book_success(request):
    tickets = Ticket.objects.filter(purchased_by=request.user).order_by("-id")[:10]
    return render(request, "flights/book_success.html", {"tickets": tickets})