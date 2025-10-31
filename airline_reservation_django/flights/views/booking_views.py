from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models import Flight, Ticket
from ..forms import PassengerForm, PaymentForm, TicketForm
import json

@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.flight = flight
            ticket.price_paid = flight.price
            ticket.save()
            return redirect('flight_list')
    else:
        form = TicketForm()
    return render(request, 'flights/book_flight.html', {'form': form, 'flight': flight})

@login_required
def book_step1(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        num_passengers = int(request.POST.get('num_passengers', 1))
        passenger_forms = [PassengerForm(request.POST, prefix=str(i)) for i in range(num_passengers)]
        if all(form.is_valid() for form in passenger_forms):
            passengers = [form.cleaned_data for form in passenger_forms]
            request.session['passengers'] = passengers
            request.session['num_passengers'] = num_passengers
            return redirect('book_step2', flight_id=flight.id)
    else:
        num_passengers = int(request.GET.get('num_passengers', 1))
        passenger_forms = [PassengerForm(prefix=str(i)) for i in range(num_passengers)]

    return render(request, 'flights/book_step1.html', {
        'flight': flight,
        'passenger_forms': passenger_forms,
        'num_passengers': num_passengers
    })


@login_required
def book_step2(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    base_price = flight.price
    if request.method == 'POST':
        selected_class = request.POST.get('seat_class')
        request.session['seat_class'] = selected_class
        class_prices = {'BASIC': 0, 'REGULAR': 30, 'PLUS': 45}
        total_price = base_price + class_prices.get(selected_class, 0)
        request.session['total_price'] = float(total_price)
        return redirect('book_step3', flight_id=flight.id)

    seat_options = [{'name': 'BASIC', 'price': 0}, {'name': 'REGULAR', 'price': 30}, {'name': 'PLUS', 'price': 45}]
    return render(request, 'flights/book_step2.html', {'flight': flight, 'seat_options': seat_options, 'total_price': base_price})


@login_required
def book_step3(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    num_passengers = request.session.get('num_passengers', 1)
    all_selected = request.session.get('selected_seats', {})
    selected_seats = all_selected.get(str(flight_id), [])
    taken_seats = list(flight.ticket_set.values_list('seat_number', flat=True))
    all_seats = [str(i) for i in range(1, flight.total_seats + 1)]
    available_seats = [s for s in all_seats if s not in taken_seats]
    seat_positions = []
    for row in range(1, 18):
        row_seats = {'left': [], 'right': []}
        for seat in range(1, 5):
            seat_id = (row - 1) * 4 + seat
            top = 105 + (row - 1) * 25.1
            if seat <= 2:
                left = 150 + (seat - 1) * 23
                row_seats['left'].append({
                    'seat_id': seat_id, 'top': top, 'left': left,
                    'occupied': str(seat_id) in taken_seats or str(seat_id) in selected_seats
                })
            else:
                right = 150 + (seat - 3) * 23
                row_seats['right'].append({
                    'seat_id': seat_id, 'top': top, 'left': right,
                    'occupied': str(seat_id) in taken_seats or str(seat_id) in selected_seats
                })
        seat_positions.append(row_seats)

    if request.method == 'POST':
        selected_seat = request.POST.get('selected_seat')
        if selected_seat and selected_seat not in taken_seats and selected_seat not in selected_seats:
            selected_seats.append(selected_seat)
            all_selected[str(flight_id)] = selected_seats
            request.session['selected_seats'] = all_selected
        if len(selected_seats) >= num_passengers:
            return redirect('book_step4', flight_id=flight.id)

    total_price = request.session.get('total_price', float(flight.price))
    return render(request, 'flights/book_step3.html', {'flight': flight, 'total_price': total_price, 'seat_positions': seat_positions,
                                                       'selected_seats': selected_seats, 'num_passengers': num_passengers,
                                                       'remaining': num_passengers - len(selected_seats)})


@login_required
def book_step4(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    total_price = request.session.get('total_price', float(flight.price))
    extra_cost = 0
    if request.method == 'POST':
        luggage_prices = {'10kg': 20, '20kg': 30, '23kg': 40}
        equipment_prices = {'sports': 40, 'music': 50, 'baby': 10}
        selected_luggage = request.POST.get('luggage_option')
        selected_equipment = request.POST.get('equipment_option')
        if selected_luggage in luggage_prices:
            extra_cost += luggage_prices[selected_luggage]
        if selected_equipment in equipment_prices:
            extra_cost += equipment_prices[selected_equipment]
        request.session['selected_luggage'] = selected_luggage
        request.session['selected_equipment'] = selected_equipment
        request.session['extra_cost'] = extra_cost
        request.session['total_price'] = total_price + extra_cost
        return redirect('book_step5', flight_id=flight_id)
    return render(request, 'flights/book_step4.html', {'flight': flight, 'total_price': total_price})


@login_required
def book_step5(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    passengers = request.session.get('passengers', [])
    num_passengers = request.session.get('num_passengers', 1)
    all_selected = request.session.get('selected_seats', {})
    selected_seats = all_selected.get(str(flight_id), [])
    seat_class = request.session.get('seat_class')
    extra_cost = float(request.session.get('extra_cost', 0))
    extra_luggage = request.session.get('selected_luggage')
    extra_equipment = request.session.get('selected_equipment')
    total_price = (float(flight.price) + extra_cost) * num_passengers

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            tickets = []
            for i, passenger_data in enumerate(passengers):
                seat_number = selected_seats[i] if i < len(selected_seats) else None
                ticket = Ticket.objects.create(
                    flight=flight,
                    passenger_name=passenger_data.get('passenger_name'),
                    passenger_surname=passenger_data.get('passenger_surname'),
                    id_number=passenger_data.get('id_number'),
                    email=passenger_data.get('email'),
                    phone_number=passenger_data.get('phone_number'),
                    seat_class=seat_class,
                    seat_number=seat_number,
                    country_code=passenger_data.get('country_code'),
                    price_paid=total_price / num_passengers,
                    payment_method='Card',
                    extra_luggage=extra_luggage,
                    extra_equipment=extra_equipment,
                    purchased_by=request.user
                )
                tickets.append(ticket)
            flight.available_seats -= num_passengers
            flight.save()
            request.session['ticket_ids'] = [t.id for t in tickets]
            return redirect('book_success')
    else:
        form = PaymentForm()
    return render(request, 'flights/book_step5.html', {
        'form': form,
        'flight': flight,
        'total_price': total_price,
        'num_passengers': num_passengers,
        'extra_luggage': extra_luggage,
        'extra_equipment': extra_equipment,
    })

@login_required
def book_success(request):
    ticket_ids = request.session.get('ticket_ids', [])
    if not ticket_ids:
        return redirect('home')
    tickets = Ticket.objects.filter(id__in=ticket_ids).select_related('flight')
    for key in ['ticket_ids', 'passengers', 'num_passengers', 'selected_seats', 'seat_class', 'total_price']:
        request.session.pop(key, None)
    return render(request, 'flights/book_success.html', {'tickets': tickets})

@csrf_exempt
def save_seat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_seat = data.get('selected_seat')
        request.session['selected_seat'] = selected_seat
        return JsonResponse({'status': 'success', 'selected_seat': selected_seat})
    return JsonResponse({'status': 'failed'})
