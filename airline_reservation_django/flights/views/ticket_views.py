from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ..models import Ticket
from ..utils.pdf_generator import generate_ticket_pdf

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