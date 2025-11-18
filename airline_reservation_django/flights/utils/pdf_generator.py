from io import BytesIO
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
import qrcode
import base64
import os

def generate_ticket_pdf(ticket):
    qr_data = f"TICKET-{ticket.id}-{ticket.passenger_name}-{ticket.flight.id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer_qr = BytesIO()
    img.save(buffer_qr, format="PNG")
    qr_base64 = base64.b64encode(buffer_qr.getvalue()).decode("utf-8")
    html_string = render_to_string(
        "flights/ticket_pdf_template.html",
        {"ticket": ticket, "qr_base64": qr_base64}
    )

    pdf_file = BytesIO()
    css_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "static", "flights", "css", "ticket_pdf.css")
    )

    html = HTML(string=html_string)
    pdf_bytes = html.write_pdf(stylesheets=[CSS(css_path)])
    pdf_file.write(pdf_bytes)
    pdf_file.seek(0)
    return pdf_file

def generate_receipt_pdf(flight, passengers, seat_class, user):
    """Generate receipt PDF using WeasyPrint for consistency"""
    order_number = datetime.now().strftime("%Y%m%d-%H%M%S")
    full_name = user.get_full_name() or user.username
    
    # Calculate totals
    passenger_data = []
    total_sum = 0.0
    
    for pax in passengers:
        base = float(flight.price)
        tax = 9.00
        total = base + tax
        total_sum += total
        
        pax_name = f"{pax.get('passenger_name')} {pax.get('passenger_surname')}"
        passenger_data.append({
            'name': pax_name,
            'price': f"{base:.2f}",
            'tax': f"{tax:.2f}",
            'total': f"{total:.2f}"
        })
    
    # Render HTML template
    html_string = render_to_string(
        "flights/receipt_pdf_template.html",
        {
            "order_number": order_number,
            "date": datetime.now().strftime('%d/%m/%Y'),
            "customer_name": full_name,
            "customer_email": user.email,
            "route": f"{flight.departure_city} → {flight.arrival_city}",
            "flight_date": flight.date.strftime('%d/%m/%Y'),
            "seat_class": seat_class,
            "passengers": passenger_data,
            "total_sum": f"{total_sum:.2f}"
        }
    )
    
    # Generate PDF
    pdf_file = BytesIO()
    css_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "static", "flights", "css", "receipt_pdf.css")
    )
    
    html = HTML(string=html_string)
    pdf_bytes = html.write_pdf(stylesheets=[CSS(css_path)])
    pdf_file.write(pdf_bytes)
    pdf_file.seek(0)
    
    return pdf_file, total_sum