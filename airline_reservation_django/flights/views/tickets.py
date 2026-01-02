from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ..models import Ticket
from ..services.email_service import send_checkin_email
from ..services import ticket_service


@login_required
def check_booked_flights(request):
    tickets = Ticket.objects.filter(purchased_by=request.user).select_related("flight")
    return render(request, "flights/check_booked_flights.html", {"tickets": tickets})


@login_required
def cancel_booked_flight(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, purchased_by=request.user)
    try:
        ticket_service.cancel_ticket(ticket)
    except ValueError as e:
        return render(request, "flights/error.html", {"message": str(e)})
    return redirect("check_booked_flights")


@login_required
def about_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, purchased_by=request.user)
    can_cancel = ticket_service.can_cancel(ticket)

    if request.GET.get("download") == "pdf":
        if not ticket_service.can_download_pdf(ticket):
            return HttpResponse("❌ You must complete check-in before downloading your boarding pass.", status=403)

        pdf_buffer = ticket_service.ticket_pdf_buffer(ticket)
        return HttpResponse(
            pdf_buffer.getvalue(),
            content_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="ticket_{ticket.id}.pdf"'},
        )

    return render(request, "flights/about_ticket.html", {"ticket": ticket, "can_cancel": can_cancel})


@login_required
def check_in(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, purchased_by=request.user)

    if ticket.status == "canceled":
        return render(request, "flights/error.html", {"message": "Canceled tickets cannot be checked in."})

    if ticket.checked_in:
        return redirect("about_ticket", ticket_id=ticket.id)

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        id_number = request.POST.get("id_number")

        res = ticket_service.verify_checkin_data(ticket, first_name, last_name, id_number)
        if res.ok:
            ticket_service.mark_checked_in(ticket)
            send_checkin_email(ticket.email, ticket.flight.flight_number)
            return redirect("about_ticket", ticket_id=ticket.id)

        return render(request, "flights/check_in.html", {"ticket": ticket, "error": res.error})

    return render(request, "flights/check_in.html", {"ticket": ticket})
