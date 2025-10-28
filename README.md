# ✈️ Airline Reservation System (Django)

The **Airline Reservation System** is a web application built with the Django framework that enables users to search, book, and cancel flight tickets.  
Administrators can manage flights and view all reservations through the Django Admin Panel.

------------------------------------------------------------
🚀 MAIN FEATURES
------------------------------------------------------------

👤 USERS:
1. **User Registration & Login**  
   - Secure authentication system for user accounts.
<hr>

2. **Flight Search**  
   - Search available flights by origin, destination, and date.
<hr>

3. **Multi-step Booking Process**  
   - Step 1: Enter personal information  
   - Step 2: Choose seat class (**Basic**, **Plus**, **Premium**)  
   - Step 3: Select a seat on the airplane map  
   - Step 4: Review and confirm the booking
<hr>

4. **View Purchased Tickets**  
   - Check all booked flights in one place.
<hr>

5. **Ticket Details (About Ticket)**  
   - View complete information for each ticket.
<hr>

6. **Cancel Ticket (Plus Class Only)**  
   - Available only for PLUS class passengers.  
   - When a ticket is canceled, the seat automatically becomes available again.
<hr>

🧑‍💼 ADMINISTRATOR:
7. **Admin Panel Management**  
   - Add, edit, or delete flights through the Django Admin Panel.
<hr>

8. **View Reservations and Payment Status**  
   - Track all booked tickets and their current payment states.
<hr>

------------------------------------------------------------
🗄️ MODELS
------------------------------------------------------------

✈️ **FLIGHT MODEL**
- Flight number  
- Departure and destination cities  
- Date and time of departure  
- Flight price
<hr>

🎫 **TICKET MODEL**
- Passenger information (first name, last name, OIB, email, phone, country)  
- Linked flight (**ForeignKey → Flight**)  
- Seat class and seat number  
- Payment method  
- **Payment status:** Paid / Refunded  
- **Ticket status:** Booked / Canceled
<hr>

------------------------------------------------------------
⚙️ HOW TO RUN LOCALLY
------------------------------------------------------------

1️⃣ Clone the repository:
git clone https://github.com/leonserka/airline-reservation-system-final-.git
cd airline_reservation_django

2️⃣ Install the dependencies:
pip install -r requirements.txt

3️⃣ Run database migrations:
python manage.py migrate

4️⃣ Start the development server:
python manage.py runserver

5️⃣ Open in your browser:
http://127.0.0.1:8000/
<hr>

------------------------------------------------------------
👩‍💻 ADMIN PANEL
------------------------------------------------------------

Access the admin panel:
http://127.0.0.1:8000/admin/

Create an admin user:
python manage.py createsuperuser
<hr>

------------------------------------------------------------
📦 TECHNOLOGIES USED
------------------------------------------------------------
- Python (Django Framework)  
- SQLite / PostgreSQL database  
- HTML, CSS, JavaScript  
- Bootstrap (for frontend styling)
<hr>

------------------------------------------------------------
📄 LICENSE
------------------------------------------------------------

This project is open-source and free to use, modify, and distribute — attribution is appreciated.
<hr>

------------------------------------------------------------
✍️ AUTHOR
------------------------------------------------------------

Author: **Leon Serka**  
GitHub: https://github.com/leonserka
<hr>
