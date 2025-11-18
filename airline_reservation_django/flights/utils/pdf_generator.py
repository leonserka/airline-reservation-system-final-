from io import BytesIO
from datetime import datetime
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
import qrcode
import base64
import os

def render_pdf(template, context, css_name):
    html = render_to_string(template, context)

    css_path = os.path.join(
        settings.BASE_DIR,
        "flights", "static", "flights", "css", css_name
    )

    pdf_bytes = HTML(string=html).write_pdf(stylesheets=[CSS(css_path)])
    out = BytesIO()
    out.write(pdf_bytes)
    out.seek(0)
    return out

def generate_ticket_pdf(ticket):
    qr_data = f"TICKET-{ticket.id}-{ticket.passenger_name}-{ticket.flight.id}"
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img_buffer = BytesIO()
    qr_img = qr.make_image()
    qr_img.save(img_buffer, format="PNG")
    qr_base64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

    context = {
        "ticket": ticket,
        "qr_base64": qr_base64
    }

    return render_pdf(
        "flights/ticket_pdf_template.html",
        context,
        "ticket_pdf.css"
    )

def generate_receipt_pdf(flight, passengers, seat_class, user):
    rows = []
    total_sum = 0

    for pax in passengers:
        base = float(flight.price)
        tax = 9
        total = base + tax
        total_sum += total

        rows.append({
            "name": f"{pax['passenger_name']} {pax['passenger_surname']}",
            "base": f"{base:.2f}",
            "tax": f"{tax:.2f}",
            "total": f"{total:.2f}",
        })

    context = {
        "flight": flight,
        "seat_class": seat_class,
        "passengers": rows,
        "order_number": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "user": user,
        "total_sum": f"{total_sum:.2f}",
        "date_today": datetime.now().strftime("%d/%m/%Y"),
    }

    return (
        render_pdf("flights/receipt_pdf_template.html", context, "receipt_pdf.css"),
        total_sum,
    )