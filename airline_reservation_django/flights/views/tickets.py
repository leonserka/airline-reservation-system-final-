from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ..services.email_service import EmailService
from ..services.ticket_service import TicketService

@login_required
def check_booked_flights(request):
    tickets = TicketService.get_user_tickets(request.user)
    return render(request, "flights/check_booked_flights.html", {"tickets": tickets})

@login_required
def cancel_booked_flight(request, ticket_id):
    ticket = TicketService.get_ticket(ticket_id, request.user)
    try:
        TicketService.cancel_ticket(ticket)
    except ValueError as e:
        return render(request, "flights/error.html", {"message": str(e)})
    return redirect("check_booked_flights")

@login_required
def about_ticket(request, ticket_id):
    ticket = TicketService.get_ticket(ticket_id, request.user)
    can_cancel = TicketService.can_cancel(ticket)

    if request.GET.get("download") == "pdf":
        if not TicketService.can_download_pdf(ticket):
            return HttpResponse("❌ You must complete check-in before downloading your boarding pass.", status=403)

        pdf_buffer = TicketService.ticket_pdf_buffer(ticket)
        return HttpResponse(
            pdf_buffer.getvalue(),
            content_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="ticket_{ticket.id}.pdf"'},
        )

    return render(request, "flights/about_ticket.html", {"ticket": ticket, "can_cancel": can_cancel})

@login_required
def check_in(request, ticket_id):
    ticket = TicketService.get_ticket(ticket_id, request.user)

    if ticket.status == "canceled":
        return render(request, "flights/error.html", {"message": "Canceled tickets cannot be checked in."})

    if ticket.checked_in:
        return redirect("about_ticket", ticket_id=ticket.id)

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        id_number = request.POST.get("id_number")
        res = TicketService.verify_checkin_data(ticket, first_name, last_name, id_number)
        
        if res.ok:
            TicketService.mark_checked_in(ticket)
            EmailService.send_checkin_email(ticket.email, ticket.flight.flight_number)
            return redirect("about_ticket", ticket_id=ticket.id)

        return render(request, "flights/check_in.html", {"ticket": ticket, "error": res.error})

    return render(request, "flights/check_in.html", {"ticket": ticket})