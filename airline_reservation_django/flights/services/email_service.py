from django.core.mail import EmailMessage
from django.conf import settings

class EmailService:
    @staticmethod
    def send_receipt_email(to_email: str, total_sum: float, pdf_buffer):
        try:
            email = EmailMessage(
                subject="Your Airline Receipt",
                body=f"Thank you! Total paid: €{total_sum:.2f}",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@airline.com'),
                to=[to_email],
            )
            email.attach("receipt.pdf", pdf_buffer.getvalue(), "application/pdf")
            email.send()
            return True
        except Exception as e:
            print(f"Failed to send receipt email: {e}")
            return False

    @staticmethod
    def send_checkin_email(to_email: str, flight_number: str):
        try:
            EmailMessage(
                subject="Check-in successful",
                body=f"You have successfully checked in for flight {flight_number}.",
                to=[to_email],
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@airline.com')
            ).send()
            return True
        except Exception as e:
            print(f"Failed to send checkin email: {e}")
            return False