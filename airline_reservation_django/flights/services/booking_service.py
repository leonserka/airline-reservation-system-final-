from django.db import transaction, IntegrityError
from ..models import Ticket
from ..services.pdf_service import PdfService
from ..services.email_service import EmailService

class BookingService:
    @staticmethod
    def process_booking(user, flight, return_flight, passengers, seat_class, all_selected_seats, total_price):
        try:
            with transaction.atomic():
                for fl in filter(None, [flight, return_flight]):
                    selected = all_selected_seats.get(str(fl.id), [])
                    
                    taken = set(
                        Ticket.objects.select_for_update()
                        .filter(flight=fl)
                        .values_list("seat_number", flat=True)
                    )
                    
                    for seat in selected:
                        if seat in taken:
                            return {"status": "seat_taken", "seat": seat}

                created_tickets = []
                for i, pax in enumerate(passengers):
                    for fl in filter(None, [flight, return_flight]):
                        seats = all_selected_seats.get(str(fl.id), [])
                        
                        ticket = Ticket.objects.create(
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
                            purchased_by=user,
                        )
                        created_tickets.append(ticket)
                        
                        fl.available_seats -= 1
                        fl.save()

        except IntegrityError:
            return {"status": "seat_taken", "seat": "unknown"}
        except Exception as e:
            return {"status": "error", "msg": str(e)}

        try:
            pdf_buffer, total_sum = PdfService.generate_receipt_pdf(flight, passengers, seat_class, user)
            EmailService.send_receipt_email(user.email, total_sum, pdf_buffer)
        except Exception as e:
            print(f"Error sending email: {e}")

        return {"status": "ok"}