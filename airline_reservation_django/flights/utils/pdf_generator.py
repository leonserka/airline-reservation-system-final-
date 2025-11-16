from io import BytesIO
from reportlab.lib.pagesizes import A4
from datetime import datetime
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
        os.path.join(os.path.dirname(__file__), "..", "static", "flights", "ticket_pdf.css")
    )

    html = HTML(string=html_string)
    pdf_bytes = html.write_pdf(stylesheets=[CSS(css_path)])
    pdf_file.write(pdf_bytes)
    pdf_file.seek(0)
    return pdf_file

def generate_receipt_pdf(flight, passengers, seat_class, user):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=25,
        rightMargin=25,
        topMargin=25,
        bottomMargin=25,
        title="Flight Receipt",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReceiptTitle",
        parent=styles["Heading1"],
        alignment=1,
        fontSize=20,
        spaceAfter=10,
    )

    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading3"],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6,
    )

    elems = []

    order_number = datetime.now().strftime("%Y%m%d-%H%M%S")
    elems.append(Paragraph("FLIGHT RECEIPT", title_style))
    elems.append(Paragraph(f"<b>Order number:</b> {order_number}", styles["Normal"]))
    elems.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]))
    elems.append(Spacer(1, 12))

    full_name = user.get_full_name() or user.username

    elems.append(Paragraph("CUSTOMER", section_title))
    elems.append(Paragraph(f"<b>Name:</b> {full_name}", styles["Normal"]))
    elems.append(Paragraph(f"<b>Email:</b> {user.email}", styles["Normal"]))
    elems.append(Spacer(1, 8))
    elems.append(Paragraph("FLIGHT DETAILS", section_title))
    elems.append(Paragraph(f"<b>Route:</b> {flight.departure_city} → {flight.arrival_city}", styles["Normal"]))
    elems.append(Paragraph(f"<b>Date:</b> {flight.date.strftime('%d/%m/%Y')}", styles["Normal"]))
    elems.append(Paragraph(f"<b>Class:</b> {seat_class}", styles["Normal"]))
    elems.append(Spacer(1, 10))
    elems.append(Paragraph("PAYMENT OVERVIEW", section_title))

    data = [["Passenger", "Price", "Tax", "Total"]]
    total_sum = 0.0

    for pax in passengers:
        base = float(flight.price)
        tax = 9.00
        total = base + tax
        total_sum += total

        pax_name = f"{pax.get('passenger_name')} {pax.get('passenger_surname')}"

        data.append([
            pax_name,
            f"{base:.2f} €",
            f"{tax:.2f} €",
            f"{total:.2f} €"
        ])

    data.append([
        "",
        "",
        "",
        Paragraph(f"<b>Total: {total_sum:.2f} €</b>", styles["Normal"])
    ])

    table = Table(data, colWidths=[200, 80, 80, 80])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -2), 0.3, colors.lightgrey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8e8e8")),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
    ]))

    elems.append(table)
    elems.append(Spacer(1, 20))
    elems.append(
        Paragraph("<i>Thank you for choosing our airline.</i>",
            ParagraphStyle("thanks", fontSize=10, alignment=1),
        )
    )
    doc.build(elems)
    buffer.seek(0)
    return buffer, total_sum