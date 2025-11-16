from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models import Flight, Ticket
from ..forms import PassengerForm
import json
from django.conf import settings
from django.core.mail import EmailMessage

def load_booking_context(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id) 
    
    return_id = request.session.get("return_id") 
    return_flight = Flight.objects.filter(id=return_id).first() if return_id else None 
    total_price = float(request.session.get("total_price", flight.price)) 
    num_passengers = int(request.session.get("num_passengers", 1)) 
    
    return flight, return_flight, total_price, num_passengers
@login_required
def book_step1(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    return_id = request.GET.get("return_id")
    if return_id:
        request.session["return_id"] = return_id  
    else:
        return_id = request.session.get("return_id")

    return_flight = None
    if return_id:
        try:
            return_flight = Flight.objects.get(id=return_id)
        except Flight.DoesNotExist:
            request.session.pop("return_id", None)
    num_passengers = int(request.GET.get("pax", request.session.get("num_passengers", 1)))

    if request.method == 'POST':
        passenger_forms = [PassengerForm(request.POST, prefix=str(i)) for i in range(num_passengers)]
        if all(form.is_valid() for form in passenger_forms):
            passengers = [form.cleaned_data for form in passenger_forms]
            request.session['passengers'] = passengers
            request.session['num_passengers'] = num_passengers
            request.session['departure_id'] = flight.id
            return redirect('book_step2', flight_id=flight.id)
    else:
        passenger_forms = [PassengerForm(prefix=str(i)) for i in range(num_passengers)]

    return render(request, 'flights/book_step1.html', {
        'flight': flight,
        'return_flight': return_flight,  
        'passenger_forms': passenger_forms,
        'num_passengers': num_passengers
    })

@login_required
def book_step2(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return_id = request.session.get('return_id')
    return_flight = Flight.objects.filter(id=return_id).first() if return_id else None

    if request.method == 'POST':
        selected_class = request.POST.get('seat_class')
        request.session['seat_class'] = selected_class
        dep_price = flight.price + {'BASIC': 0, 'REGULAR': 30, 'PLUS': 45}.get(selected_class, 0)
        ret_price = (return_flight.price + {'BASIC': 0, 'REGULAR': 30, 'PLUS': 45}.get(selected_class, 0)) if return_flight else 0
        total_price = dep_price + ret_price
        request.session['total_price'] = float(total_price)

        return redirect('book_step3', flight_id=flight.id)

    seat_options = [
        {'name': 'BASIC', 'price': 0},
        {'name': 'REGULAR', 'price': 30},
        {'name': 'PLUS', 'price': 45}
    ]

    return render(request, 'flights/book_step2.html', {
        'flight': flight,
        'return_flight': return_flight,
        'seat_options': seat_options,
        'total_price': flight.price
    })

@login_required
def book_step3(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return_id = request.session.get('return_id')
    return_flight = Flight.objects.filter(id=return_id).first() if return_id else None
    departure_id = request.session.get("departure_id", flight_id)
    num_passengers = request.session.get('num_passengers', 1)
    all_selected = request.session.get('selected_seats', {})
    taken_seats = list(flight.ticket_set.values_list('seat_number', flat=True))
    selected_seats = all_selected.get(str(flight_id), [])

    seat_positions = []
    for row in range(1, 18):
        row_seats = {'left': [], 'right': []}
        for seat in range(1, 5):
            seat_id = (row - 1) * 4 + seat
            top = 105 + (row - 1) * 25.1
            if seat <= 2:
                left = 150 + (seat - 1) * 23
                row_seats['left'].append({
                    'seat_id': seat_id,
                    'top': top,
                    'left': left,
                    'occupied': str(seat_id) in taken_seats or str(seat_id) in selected_seats
                })
            else:
                right = 150 + (seat - 3) * 23
                row_seats['right'].append({
                    'seat_id': seat_id,
                    'top': top,
                    'left': right,
                    'occupied': str(seat_id) in taken_seats or str(seat_id) in selected_seats
                })
        seat_positions.append(row_seats)

    if request.method == 'POST':
        selected_seat = request.POST.get('selected_seat')

        if selected_seat and selected_seat not in selected_seats:
            selected_seats.append(selected_seat)
            all_selected[str(flight_id)] = selected_seats
            request.session['selected_seats'] = all_selected
        if len(selected_seats) >= num_passengers:
            if return_flight and str(return_flight.id) not in all_selected:
                return redirect('book_step3', flight_id=return_flight.id)
            
            return redirect('book_step4', flight_id=departure_id)

    total_price = request.session.get('total_price', float(flight.price))

    return render(request, 'flights/book_step3.html', {
        'flight': flight,
        'return_flight': return_flight,        
        'seat_positions': seat_positions,
        'selected_seats': selected_seats,
        'num_passengers': num_passengers,
        'remaining': num_passengers - len(selected_seats),
        'total_price': total_price
    })

@login_required
def book_step4(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    total_price = request.session.get('total_price', float(flight.price))

    if request.method == 'POST':
        selected_luggage = request.POST.get('luggage_option')
        selected_equipment = request.POST.get('equipment_option')

        extra_cost = ({'10kg': 20, '20kg': 30, '23kg': 40}.get(selected_luggage, 0) + 
                      {'sports': 40, 'music': 50, 'baby': 10}.get(selected_equipment, 0))
        request.session['selected_luggage'] = selected_luggage
        request.session['selected_equipment'] = selected_equipment
        request.session['extra_cost'] = extra_cost
        request.session['total_price'] = total_price + extra_cost

        return redirect('book_step5', flight_id=flight_id)

    return render(request, 'flights/book_step4.html', {'flight': flight, 'total_price': total_price})


@login_required
def book_step5(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    return_id = request.session.get('return_id')
    return_flight = Flight.objects.filter(id=return_id).first() if return_id else None

    passengers = request.session.get('passengers', [])
    num_passengers = request.session.get('num_passengers', 1)
    seat_class = request.session.get('seat_class')
    all_selected = request.session.get('selected_seats', {})
    extra_luggage = request.session.get('selected_luggage')
    extra_equipment = request.session.get('selected_equipment')
    total_price = float(request.session.get('total_price', flight.price)) * num_passengers

    if request.method == 'GET':
        return render(request, 'flights/book_step5.html', {
            'flight': flight,
            'return_flight': return_flight,
            'total_price': total_price,
            'num_passengers': num_passengers,
            'extra_luggage': extra_luggage,
            'extra_equipment': extra_equipment,
            'PAYPAL_CLIENT_ID': getattr(settings, 'PAYPAL_CLIENT_ID', ''),
        })

    try:
        json.loads(request.body)
    except Exception:
        return JsonResponse({'status': 'error', 'msg': 'Invalid JSON'})

    for i, pax in enumerate(passengers):
        for fl in filter(None, [flight, return_flight]):
            seat_list = all_selected.get(str(fl.id), [])
            seat_number = seat_list[i] if i < len(seat_list) else None
            Ticket.objects.create(
                flight=fl,
                passenger_name=pax.get('passenger_name'),
                passenger_surname=pax.get('passenger_surname'),
                id_number=pax.get('id_number'),
                email=pax.get('email'),
                phone_number=pax.get('phone_number'),
                seat_class=seat_class,
                seat_number=seat_number,
                country_code=pax.get('country_code'),
                price_paid=fl.price,
                payment_method='PayPal',
                extra_luggage=extra_luggage,
                extra_equipment=extra_equipment,
                purchased_by=request.user,
            )
            fl.available_seats = max(0, fl.available_seats - 1)
            fl.save()

    from ..utils.pdf_generator import generate_receipt_pdf
    pdf_buffer, total_sum = generate_receipt_pdf(flight, passengers, seat_class, request.user)

    email = EmailMessage(
        subject="✅ Airline Ticket Confirmation & Receipt",
        body=(
            f"Dear {request.user.first_name or 'Customer'},\n\n"
            f"Thank you for your purchase!\n\n"
            f"Flight: {flight.departure_city} → {flight.arrival_city}\n"
            f"Date: {flight.date}\n"
            f"Passengers: {num_passengers}\n"
            f"Total Paid: €{total_sum:.2f}\n\n"
            f"Your receipt is attached.\n\n"
            f"Have a safe flight! ✈️\n"
            f"— Airline Reservation Team"
        ),
        from_email="Airline Reservation <no-reply@airline.com>",
        to=[request.user.email],
    )
    email.attach("receipt.pdf", pdf_buffer.getvalue(), "application/pdf")
    email.send(fail_silently=False)

    for key in ['ticket_ids', 'passengers', 'num_passengers', 'selected_seats', 'seat_class', 'total_price', 'return_id']:
        request.session.pop(key, None)

    return JsonResponse({'status': 'ok'})

@login_required
def book_success(request):
    tickets = Ticket.objects.filter(purchased_by=request.user).order_by('-id')[:10]
    for key in ['ticket_ids', 'passengers', 'num_passengers', 'selected_seats', 'seat_class', 'total_price', 'return_id']:
        request.session.pop(key, None)
    return render(request, 'flights/book_success.html', {'tickets': tickets})
