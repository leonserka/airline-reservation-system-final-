import base64
import os
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS

class PdfService:
    @staticmethod
    def generate_ticket_pdf(ticket):
        departure_local = ticket.flight.departure_datetime.strftime("%Y-%m-%d %H:%M")
        arrival_local = ticket.flight.arrival_datetime.strftime("%Y-%m-%d %H:%M")
        qr_data = f"TICKET-{ticket.id}-{ticket.flight.flight_number}"
        qr_img = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        gate_closes = (
            ticket.flight.departure_datetime - timedelta(minutes=30)
        ).strftime("%H:%M")

        context = {
            "ticket": ticket,
            "departure_local": departure_local,
            "arrival_local": arrival_local,
            "qr_base64": qr_base64,
            "gate_closes": gate_closes,
        }

        html = render_to_string("flights/ticket_pdf_template.html", context)
        css_path = os.path.join(
            settings.BASE_DIR, "flights", "static", "flights", "css", "ticket_pdf.css"
        )

        pdf_bytes = HTML(string=html).write_pdf(stylesheets=[CSS(css_path)])
        out = BytesIO()
        out.write(pdf_bytes)
        out.seek(0)
        return out

    @staticmethod
    def generate_receipt_pdf(flight, passengers, seat_class, user):
        rows = []
        total_sum = 0.0

        for p in passengers:
            price = float(flight.price)
            rows.append({
                "name": f"{p['passenger_name']} {p['passenger_surname']}",
                "seat": p.get("seat_number", "N/A"),
                "class": seat_class,
                "price": f"{price:.2f}",
            })
            total_sum += price

        context = {
            "flight": flight,
            "passengers": rows,
            "user": user,
            "total_sum": f"{total_sum:.2f}",
            "date_today": datetime.now().strftime("%d/%m/%Y"),
            "order_number": datetime.now().strftime("%Y%m%d-%H%M%S"),
        }

        html = render_to_string("flights/receipt_pdf_template.html", context)
        css_path = os.path.join(
            settings.BASE_DIR, "flights", "static", "flights", "css", "receipt_pdf.css"
        )
        
        stylesheets = [CSS(css_path)] if os.path.exists(css_path) else []
        pdf_bytes = HTML(string=html).write_pdf(stylesheets=stylesheets)
        out = BytesIO()
        out.write(pdf_bytes)
        out.seek(0)
        return out, total_sum