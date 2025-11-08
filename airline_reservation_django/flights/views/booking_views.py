from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ..models import Flight, Ticket
from ..forms import PassengerForm, TicketForm
import json
from django.conf import settings
from django.core.mail import EmailMessage
from io import BytesIO
from reportlab.lib.pagesizes import A4
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
        class_prices = {'BASIC': 0, 'REGULAR': 30, 'PLUS': 45}
        dep_price = flight.price + class_prices.get(selected_class, 0)
        ret_price = (return_flight.price + class_prices.get(selected_class, 0)) if return_flight else 0
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
        luggage_prices = {'10kg': 20, '20kg': 30, '23kg': 40}
        equipment_prices = {'sports': 40, 'music': 50, 'baby': 10}
        selected_luggage = request.POST.get('luggage_option')
        selected_equipment = request.POST.get('equipment_option')

        extra_cost = 0
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
    return_id = request.session.get('return_id')
    return_flight = Flight.objects.filter(id=return_id).first() if return_id else None
    passengers = request.session.get('passengers', [])
    num_passengers = request.session.get('num_passengers', 1)
    all_selected = request.session.get('selected_seats', {})
    seat_class = request.session.get('seat_class')
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

    if request.method == 'POST':
        try:
            json.loads(request.body)
        except Exception:
            return JsonResponse({'status': 'error', 'msg': 'Invalid JSON'})

        for i, passenger_data in enumerate(passengers):
            for fl in [flight] + ([return_flight] if return_flight else []):
                seat_list = all_selected.get(str(fl.id), [])
                seat_number = seat_list[i] if i < len(seat_list) else None
                Ticket.objects.create(
                    flight=fl,
                    passenger_name=passenger_data.get('passenger_name'),
                    passenger_surname=passenger_data.get('passenger_surname'),
                    id_number=passenger_data.get('id_number'),
                    email=passenger_data.get('email'),
                    phone_number=passenger_data.get('phone_number'),
                    seat_class=seat_class,
                    seat_number=seat_number,
                    country_code=passenger_data.get('country_code'),
                    price_paid=fl.price,
                    payment_method='PayPal',
                    extra_luggage=extra_luggage,
                    extra_equipment=extra_equipment,
                    purchased_by=request.user
                )
                fl.available_seats = max(0, fl.available_seats - 1)
                fl.save()

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, title="Flight Receipt")
        styles = getSampleStyleSheet()
        elems = []

        order_number = datetime.now().strftime("%Y%m%d-%H%M%S")
        elems.append(Paragraph("<b>Receipt</b>", styles['Heading1']))
        elems.append(Paragraph(f"Order number: <b>{order_number}</b>", styles['Normal']))
        elems.append(Paragraph(f"Order date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        elems.append(Spacer(1, 12))
        elems.append(Paragraph("<b>CUSTOMER</b>", styles['Heading3']))
        full_name = request.user.get_full_name() or request.user.username
        elems.append(Paragraph(f"{full_name}", styles['Normal']))
        elems.append(Paragraph(f"{request.user.email}", styles['Normal']))
        elems.append(Spacer(1, 12))
        elems.append(Paragraph("<b>Payment Overview</b>", styles['Heading3']))
        elems.append(Paragraph(
            f"{flight.departure_city} - {flight.arrival_city}, {flight.date.strftime('%d/%m/%Y')}",
            styles['Normal']
        ))
        elems.append(Paragraph(f"Class: {seat_class}", styles['Normal']))
        elems.append(Spacer(1, 10))
        data = [["Description", "Price", "Taxes & charges", "Total"]]
        total_sum = 0.0

        for i, pax in enumerate(passengers):
            pax_name = f"{pax.get('passenger_name', '')} {pax.get('passenger_surname', '')}".strip() or f"Passenger {i+1}"
            base_price = float(flight.price)
            taxes = 9.00
            line_total = round(base_price + taxes, 2)
            total_sum += line_total

            data.append([
                Paragraph(f"<b>{pax_name}</b><br/><font size=9>Adult</font>", styles['Normal']),
                f"{base_price:.2f} EUR",
                f"{taxes:.2f} EUR",
                f"{line_total:.2f} EUR"
            ])

        data.append(["", "", Paragraph("<b>Sum</b>", styles['Normal']), f"{total_sum:.2f} EUR"])

        table = Table(data, colWidths=[250, 80, 100, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 1), (-1, -2), 0.25, colors.lightgrey),
            ('LINEBELOW', (0, 0), (-1, 0), 0.75, colors.grey),
            ('LINEABOVE', (-2, -2), (-1, -2), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
        ]))
        elems.append(table)
        elems.append(Spacer(1, 10))
        elems.append(Paragraph(f"<b>Total amount:</b> {total_sum:.2f} EUR", styles['Heading3']))
        elems.append(Paragraph("<font size=9>Paid with PayPal</font>", styles['Normal']))
        doc.build(elems)
        pdf_buffer.seek(0)

        email = EmailMessage(
            subject="✅ Airline Ticket Confirmation & Receipt",
            body=(
                f"Dear {request.user.first_name or 'Customer'},\n\n"
                f"Thank you for your purchase! Your booking was successful.\n\n"
                f"Flight: {flight.departure_city} → {flight.arrival_city}\n"
                f"Date: {flight.date}\n"
                f"Passengers: {num_passengers}\n"
                f"Total Paid: €{total_sum:.2f}\n\n"
                f"Your receipt is attached as a PDF.\n\n"
                f"Have a safe flight! ✈️\n"
                f"— Airline Reservation Team"
            ),
            from_email="Airline Reservation <no-reply@airline.com>",
            to=[request.user.email],
        )
        email.attach("receipt.pdf", pdf_buffer.getvalue(), "application/pdf")
        email.send(fail_silently=False)
        for key in ['ticket_ids', 'passengers', 'num_passengers', 'selected_seats',
                    'seat_class', 'total_price', 'return_id']:
            request.session.pop(key, None)

        return JsonResponse({'status': 'ok'})

@login_required
def book_success(request):
    tickets = Ticket.objects.filter(purchased_by=request.user).order_by('-id')[:10]
    for key in ['ticket_ids', 'passengers', 'num_passengers', 'selected_seats',
                'seat_class', 'total_price', 'return_id']:
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