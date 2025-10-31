from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.graphics.barcode import code128

def generate_ticket_pdf(ticket):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    p.setFont("Helvetica-Bold", 18)
    p.drawString(2 * cm, h - 2.5 * cm, "AIRLINE TICKET")
    p.setFont("Helvetica", 11)
    y = h - 4 * cm
    gap = 0.7 * cm
    def row(label, value):
        nonlocal y
        p.setFont("Helvetica-Bold", 10); p.drawString(2 * cm, y, label)
        p.setFont("Helvetica", 10); p.drawString(6 * cm, y, str(value)); y -= gap
    row("Passenger:", f"{ticket.passenger_name} {ticket.passenger_surname}")
    row("Flight:", f"{ticket.flight.departure_city} → {ticket.flight.arrival_city}")
    row("Date:", ticket.flight.date.strftime("%Y-%m-%d"))
    row("Seat:", ticket.seat_number or "N/A")
    row("Class:", ticket.seat_class)
    row("Price Paid:", f"€{ticket.price_paid}")
    row("Extra Luggage:", ticket.extra_luggage or "None")
    row("Equipment:", ticket.extra_equipment or "None")
    row("Payment Status:", ticket.payment_status.capitalize())
    row("Booking Status:", ticket.status.capitalize())
    code = f"TCK-{ticket.id:06d}"
    barcode = code128.Code128(code, barHeight=25, barWidth=0.6)
    barcode.drawOn(p, 2 * cm, 4 * cm)
    p.setFont("Helvetica-Bold", 12); p.drawString(2 * cm, 3.2 * cm, code)
    p.setFont("Helvetica-Oblique", 8); p.drawString(2 * cm, 2 * cm, "Please present this ticket at the check-in desk.")
    p.showPage(); p.save(); buffer.seek(0)
    return buffer
