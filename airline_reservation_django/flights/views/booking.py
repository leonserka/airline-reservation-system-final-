from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction, IntegrityError
import json
from ..services.seatmap_service import build_seat_positions
from ..models import Flight, Ticket
from ..forms import PassengerForm
from ..utils.pdf_generator import generate_receipt_pdf
from ..constants import (
    SEAT_PRICES, LUGGAGE, EQUIPMENT,
    SKEY_RETURN_ID, SKEY_PASSENGERS, SKEY_NUM_PAX, SKEY_DEP_ID,
    SKEY_SEAT_CLASS, SKEY_SELECTED_SEATS, SKEY_TOTAL_PRICE,
    SKEY_LUGGAGE, SKEY_EQUIPMENT,
)
from ..services.email_service import send_receipt_email


def get_return_flight(request):
    rid = request.session.get(SKEY_RETURN_ID)
    return Flight.objects.filter(id=rid).first() if rid else None


@login_required
def book_step1(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(request)

    if request.GET.get("return_id"):
        request.session[SKEY_RETURN_ID] = request.GET.get("return_id")

    num_passengers = int(request.GET.get("pax", request.session.get(SKEY_NUM_PAX, 1)))

    if request.method == "POST":
        forms = [PassengerForm(request.POST, prefix=str(i)) for i in range(num_passengers)]
        if all(f.is_valid() for f in forms):
            request.session[SKEY_PASSENGERS] = [f.cleaned_data for f in forms]
            request.session[SKEY_NUM_PAX] = num_passengers
            request.session[SKEY_DEP_ID] = flight.id
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
        request.session[SKEY_SEAT_CLASS] = seat_class

        dep_price = flight.price + SEAT_PRICES.get(seat_class, 0)
        ret_price = return_flight.price + SEAT_PRICES.get(seat_class, 0) if return_flight else 0
        request.session[SKEY_TOTAL_PRICE] = float(dep_price + ret_price)

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
    num_passengers = request.session.get(SKEY_NUM_PAX, 1)

    all_selected = request.session.get(SKEY_SELECTED_SEATS, {})
    selected = all_selected.get(str(flight_id), [])

    taken = set(
        Ticket.objects.filter(flight=flight)
        .values_list("seat_number", flat=True)
    )

    seat_positions = build_seat_positions(
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
            request.session[SKEY_SELECTED_SEATS] = all_selected

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
        "total_price": request.session.get(SKEY_TOTAL_PRICE, float(flight.price)),
    })



@login_required
def book_step4(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    total = request.session.get(SKEY_TOTAL_PRICE, float(flight.price))

    if request.method == "POST":
        lug = request.POST.get("luggage_option")
        eq = request.POST.get("equipment_option")
        extra = LUGGAGE.get(lug, 0) + EQUIPMENT.get(eq, 0)

        request.session[SKEY_LUGGAGE] = lug
        request.session[SKEY_EQUIPMENT] = eq
        request.session[SKEY_TOTAL_PRICE] = total + extra

        return redirect("book_step5", flight_id=flight.id)

    return render(request, "flights/book_step4.html", {
        "flight": flight,
        "total_price": total,
    })


@login_required
def book_step5(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return_flight = get_return_flight(request)

    passengers = request.session.get(SKEY_PASSENGERS, [])
    seat_class = request.session.get(SKEY_SEAT_CLASS)
    all_selected = request.session.get(SKEY_SELECTED_SEATS, {})
    total_price = float(request.session.get(SKEY_TOTAL_PRICE, flight.price))

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
    send_receipt_email(request.user.email, total_sum, pdf_buffer)

    for key in [
        SKEY_PASSENGERS, SKEY_NUM_PAX, SKEY_SELECTED_SEATS,
        SKEY_SEAT_CLASS, SKEY_TOTAL_PRICE, SKEY_RETURN_ID,
        SKEY_LUGGAGE, SKEY_EQUIPMENT,
    ]:
        request.session.pop(key, None)

    return JsonResponse({"status": "ok"})

@login_required
def book_success(request):
    tickets = Ticket.objects.filter(purchased_by=request.user).order_by("-id")[:10]
    return render(request, "flights/book_success.html", {"tickets": tickets})
