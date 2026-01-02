from django.core.mail import EmailMessage

def send_receipt_email(to_email: str, total_sum: float, pdf_buffer):
    email = EmailMessage(
        subject="Your Airline Receipt",
        body=f"Thank you! Total paid: €{total_sum:.2f}",
        from_email="Airline <no-reply@airline.com>",
        to=[to_email],
    )
    email.attach("receipt.pdf", pdf_buffer.getvalue(), "application/pdf")
    email.send()

def send_checkin_email(to_email: str, flight_number: str):
    EmailMessage(
        subject="Check-in successful",
        body=f"You have successfully checked in for flight {flight_number}.",
        to=[to_email],
        from_email="Airline <no-reply@airline.com>"
    ).send()
