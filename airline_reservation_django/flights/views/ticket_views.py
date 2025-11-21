from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ..models import Ticket
from ..utils.pdf_generator import generate_ticket_pdf
from django.utils import timezone
from django.core.mail import EmailMessage

@login_required
def check_booked_flights(request):
    tickets = Ticket.objects.filter(
        purchased_by=request.user
    ).select_related("flight")

    return render(request, "flights/check_booked_flights.html", {
        "tickets": tickets
    })

@login_required
def cancel_booked_flight(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, purchased_by=request.user)

    if ticket.seat_class != "PLUS":
        return render(request, "flights/error.html", {
            "message": "You can only cancel PLUS class tickets."
        })

    ticket.status = "canceled"
    ticket.payment_status = "refunded"
    ticket.seat_number = None
    ticket.save()

    return redirect("check_booked_flights")

@login_required
def about_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, purchased_by=request.user)
    can_cancel = ticket.seat_class == "PLUS"

    if request.GET.get("download") == "pdf":
        if not ticket.checked_in:
            return HttpResponse("❌ You must complete check-in before downloading your boarding pass.", status=403)
        pdf_buffer = generate_ticket_pdf(ticket)
        return HttpResponse(
            pdf_buffer.getvalue(),
            content_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="ticket_{ticket.id}.pdf"'
            }
        )

    return render(request, "flights/about_ticket.html", {
        "ticket": ticket,
        "can_cancel": can_cancel
    })


@login_required
def check_in(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, purchased_by=request.user)

    if ticket.status == "canceled":
        return render(request, "flights/error.html", {
            "message": "Canceled tickets cannot be checked in."
        })

    if ticket.checked_in:
        return redirect("about_ticket", ticket_id=ticket.id)

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        id_number = request.POST.get("id_number")

        if (
            first_name.strip().lower() == ticket.passenger_name.lower() and
            last_name.strip().lower() == ticket.passenger_surname.lower() and
            id_number.strip() == ticket.id_number
        ):
            ticket.checked_in = True
            ticket.checked_in_at = timezone.now()
            ticket.save()

            EmailMessage(
                subject="Check-in successful",
                body=f"You have successfully checked in for flight {ticket.flight.flight_number}.",
                to=[ticket.email],
                from_email="Airline <no-reply@airline.com>"
            ).send()

            return redirect("about_ticket", ticket_id=ticket.id)
        else:
            return render(request, "flights/check_in.html", {
                "ticket": ticket,
                "error": "❌ Entered data does not match our records!"
            })

    return render(request, "flights/check_in.html", {
        "ticket": ticket
    })
