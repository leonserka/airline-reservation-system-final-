import os
import base64
from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML, CSS
import qrcode


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
    dep_tz = ZoneInfo(ticket.flight.departure_timezone or "UTC")
    arr_tz = ZoneInfo(ticket.flight.arrival_timezone or "UTC")
    dep_dt = ticket.flight.departure_datetime
    arr_dt = ticket.flight.arrival_datetime

    if getattr(dep_dt, "tzinfo", None) is None:
        dep_dt = dep_dt.replace(tzinfo=dep_tz)
    else:
        dep_dt = dep_dt.astimezone(dep_tz)

    if getattr(arr_dt, "tzinfo", None) is None:
        try:
            arr_dt = arr_dt.replace(tzinfo=dep_tz).astimezone(arr_tz)
        except Exception:
            arr_dt = arr_dt.replace(tzinfo=arr_tz)
    else:
        arr_dt = arr_dt.astimezone(arr_tz)

    departure_local_str = f"{dep_dt.strftime('%Y-%m-%d %H:%M')} ({ticket.flight.departure_timezone or dep_tz.key})"
    arrival_local_str = f"{arr_dt.strftime('%Y-%m-%d %H:%M')} ({ticket.flight.arrival_timezone or arr_tz.key})"
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
        "qr_base64": qr_base64,
        "departure_local": departure_local_str,
        "arrival_local": arrival_local_str,
    }

    return render_pdf(
        "flights/ticket_pdf_template.html",
        context,
        "ticket_pdf.css"
    )

def generate_receipt_pdf(flight, passengers, seat_class, user):
    rows = []
    total_sum = 0.0

    for pax in passengers:
        price = float(getattr(pax, "price_paid", 0) or 0)
        rows.append({
            "name": f"{getattr(pax, 'passenger_name', '')} {getattr(pax, 'passenger_surname', '')}",
            "seat": getattr(pax, "seat_number", "N/A"),
            "class": getattr(pax, "seat_class", seat_class),
            "price": f"{price:.2f}",
        })
        total_sum += price

    context = {
        "flight": flight,
        "seat_class": seat_class,
        "passengers": rows,
        "order_number": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "user": user,
        "total_sum": f"{total_sum:.2f}",
        "date_today": datetime.now().strftime("%d/%m/%Y"),
    }

    return render_pdf(
        "flights/receipt_pdf_template.html",
        context,
        "receipt_pdf.css"
    )