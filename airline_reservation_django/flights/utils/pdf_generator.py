from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.graphics.barcode import code128
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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

def generate_receipt_pdf(flight, passengers, seat_class, user):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Flight Receipt")
    styles = getSampleStyleSheet()
    elems = []

    order_number = datetime.now().strftime("%Y%m%d-%H%M%S")
    elems.append(Paragraph("<b>Receipt</b>", styles['Heading1']))
    elems.append(Paragraph(f"Order number: <b>{order_number}</b>", styles['Normal']))
    elems.append(Paragraph(f"Order date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elems.append(Spacer(1, 12))

    full_name = user.get_full_name() or user.username
    elems.append(Paragraph("<b>CUSTOMER</b>", styles['Heading3']))
    elems.append(Paragraph(full_name, styles['Normal']))
    elems.append(Paragraph(user.email, styles['Normal']))
    elems.append(Spacer(1, 12))

    elems.append(Paragraph("<b>Payment Overview</b>", styles['Heading3']))
    elems.append(Paragraph(
        f"{flight.departure_city} - {flight.arrival_city}, {flight.date.strftime('%d/%m/%Y')}",
        styles['Normal']
    ))
    elems.append(Paragraph(f"Class: {seat_class}", styles['Normal']))
    elems.append(Spacer(1, 10))

    data = [["Description", "Price", "Taxes & charges", "Total"]]
    total_sum = 0.0
    for pax in passengers:
        base = float(flight.price)
        taxes = 9.00
        line_total = base + taxes
        total_sum += line_total
        pax_name = f"{pax.get('passenger_name')} {pax.get('passenger_surname')}"
        data.append([pax_name, f"{base:.2f} EUR", f"{taxes:.2f} EUR", f"{line_total:.2f} EUR"])

    data.append(["", "", "Sum", f"{total_sum:.2f} EUR"])

    table = Table(data, colWidths=[250, 80, 100, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 1), (-1, -2), 0.25, colors.lightgrey),
    ]))
    elems.extend([table, Spacer(1, 12), Paragraph(f"<b>Total:</b> {total_sum:.2f} EUR", styles['Heading3'])])
    doc.build(elems)
    buffer.seek(0)
    return buffer, total_sum
