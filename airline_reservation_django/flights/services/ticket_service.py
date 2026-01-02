from dataclasses import dataclass
from typing import Optional
from django.utils import timezone
from django.db import transaction

from ..models import Ticket
from ..utils.pdf_generator import generate_ticket_pdf


@dataclass(frozen=True)
class TicketCheckinResult:
    ok: bool
    error: Optional[str] = None


def can_cancel(ticket: Ticket) -> bool:
    return ticket.seat_class == "PLUS"


@transaction.atomic
def cancel_ticket(ticket: Ticket) -> None:
    if not can_cancel(ticket):
        raise ValueError("You can only cancel PLUS class tickets.")

    flight = ticket.flight
    ticket.status = "canceled"
    ticket.payment_status = "refunded"

    if ticket.seat_number:
        flight.available_seats += 1
        flight.save()

    ticket.seat_number = None
    ticket.save()


def can_download_pdf(ticket: Ticket) -> bool:
    return bool(ticket.checked_in) and ticket.status != "canceled"


def ticket_pdf_buffer(ticket: Ticket):
    return generate_ticket_pdf(ticket)


def verify_checkin_data(ticket: Ticket, first_name: str, last_name: str, id_number: str) -> TicketCheckinResult:
    if ticket.status == "canceled":
        return TicketCheckinResult(ok=False, error="Canceled tickets cannot be checked in.")

    if not first_name or not last_name or not id_number:
        return TicketCheckinResult(ok=False, error="Missing data.")

    if (
        first_name.strip().lower() == ticket.passenger_name.lower()
        and last_name.strip().lower() == ticket.passenger_surname.lower()
        and id_number.strip() == ticket.id_number
    ):
        return TicketCheckinResult(ok=True)

    return TicketCheckinResult(ok=False, error="❌ Entered data does not match our records!")


@transaction.atomic
def mark_checked_in(ticket: Ticket) -> None:
    ticket.checked_in = True
    ticket.checked_in_at = timezone.now()
    ticket.save()
