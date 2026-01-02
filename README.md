# ✈️ Airline Reservation System (Django)

The **Airline Reservation System** is a full-stack web application built with the Django framework and PostgreSQL(via Docker and Flyway migrations).It allows users to search, book, and cancel flight tickets, while administrators can manage flights and monitor all reservations through the Django Admin Panel.

---

## 🚀 Main Features

### 👤 Users
- User registration, login and password reset via email
- Search for available flights by origin, destination, and date  
- Multi-step booking process:
  1. Enter personal information  
  2. Choose seat class (**Basic**, **Regular**, **Plus**)  
  3. Select a seat on the airplane map (supports multiple passengers)
  4. (Optional) Add extras: Extra Luggage (10/20/23 kg) & Equipment (Sports/Music/Baby)
  5. Payment & ticket issuing
- race conditioning for users if 2 people buys same seat slower user will get error and masage to change seat
- View all purchased tickets (**Check Booked Flights**) — shows tickets bought by the logged-in user (even for other passengers)
- View ticket details (**About Ticket**) — includes extras and PDF ticket with a QR code  
- Cancel a ticket (**Cancel Ticket**) – available only for **PLUS** class  
- When a ticket is canceled, the seat automatically becomes available again
- Real time zones flight times   

### 🧑‍💼 Administrator
- Add, edit, and delete flights through the **Django Admin Panel**  
- View all booked tickets and their payment status
- Automatically sync database schema via Flyway migrations 

---

## 🗄️ Models

### ✈️ Flight
Contains flight details:
- Flight number  
- Departure and arrival country & city
- Departure and arrival timezone
- Date and time of departure  
- Flight price 
- Seat availability
- Price
- Flight type (Domestic / International) 

### 🎫 Ticket
Contains ticket and passenger details:
- Passenger info (name, surname, ID number, email, phone, country)  
- Linked flight (**ForeignKey → Flight**)  
- Seat class and seat number  
- extra_luggage or equipment
- Payment method  
- **Payment Status:** Paid / Refunded  
- **Ticket Status:** Booked / Canceled
- **Purchased By:** `auth.user` (who paid for the booking) 
- **Checked in:** 

---

## ⚙️ How to Run with Docker + PostgreSQL + Flyway
The project includes a fully containerized environment with:
- 🐍 Django (Python 3.11)
- 🐘 PostgreSQL (database)
- 🚀 Flyway (for database schema migrations)

## 🔧 Steps to Start

1️⃣ **Clone the repository**
```bash
git clone https://github.com/leonserka/airline-reservation-system-final-.git
cd airline_reservation_django
```
2️⃣ **Create .env file**
```bash

SECRET_KEY=your_django_secret_key
DEBUG=True
POSTGRES_USER=airline_user
POSTGRES_PASSWORD=airline_pass
POSTGRES_DB=airline_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
NGROK_AUTHTOKEN=your_ngok_key
NGROK_REGION=eu
PAYPAL_CLIENT_ID=your_pp_id
PAYPAL_SECRET=your_pp_secret
```

3️⃣ **Build and start all containers**
```bash
docker-compose up --build
```
This will:
- Start the PostgreSQL database on port 5432
- Automatically apply all Flyway migrations (`/flyway/sql/V1__initial_schema.sql`)
- Launch the Django app on port 8000

4️⃣ **Open in browser**
```bash
http://127.0.0.1:8000/
```
or using Ngrok (external access):
```bash
https://unfelicitated-pneumatological-wally.ngrok-free.dev/
```

5️⃣ **Access the Django Admin Panel**
Access the Django Admin interface:
```bash
http://127.0.0.1:8000/admin/
```
or with ngrok:
```bash
https://unfelicitated-pneumatological-wally.ngrok-free.dev/admin/
```

Create a superuser (inside the container):
```bash
docker exec -it airline_django python manage.py createsuperuser

```
6️⃣ **Database access**
```bash
http://localhost:5052/login?next=/browser/
```

7️⃣ **Stop containers**
```bash
docker-compose down

```
To remove all data and rebuild from scratch:
```bash
docker-compose down -v --rmi all

```

---

## ⚙️ Default Environment Variables
Defined in docker-compose.yml:
```bash
POSTGRES_USER: airline_user
POSTGRES_PASSWORD: airline_pass
POSTGRES_DB: airline_db

```

---

## 🗄️ Database Migrations
Database structure is version-controlled with Flyway.
All schema definitions are located in:
```bash
flyway/sql/V1__initial_schema.sql

```

---
## 🗂️ Project Structure (after migrating to Docker, PostgreSQL, and Flyway.)

```bash
airline_reservation_django\
├── requirements.txt                
├── README.md                       
├── Dockerfile                      
├── docker-compose.yml              
├── .gitignore                      
├── .env                            
├── .venv\
├── flyway\                         
│   └── sql\                        
│       ├── V1__initial_schema.sql  
│       ├── V2__add_schema.sql  
│       ├── V3__add_timestamp.sql 
│       ├── V4__add_checkin_fields.sql
│       └── V5__add_timezones.sql 
│
└── airline_reservation_django\
    ├── manage.py                   
    │
    ├── airline_project\            
    │   ├── __init__.py
    │   ├── settings.py            
    │   ├── urls.py                
    │   ├── wsgi.py                
    │   └── asgi.py                 
    │
    ├── flights\                   
    │   ├── __init__.py
    │   ├── admin.py               
    │   ├── apps.py                 
    │   ├── country_codes.py        
    │   ├── choices.py   
    │   ├── constants.py            
    │   ├── forms.py                
    │   ├── models.py               
    │   ├── urls.py                
    │   │
    │   ├── services\   
    │   │   ├── __init__.py
    │   │   ├── booking_service.py
    │   │   ├── booking_session.py
    │   │   ├── flight_service.py
    │   │   ├── email_service.py
    │   │   ├── pdf_service.py
    │   │   ├── seatmap_service.py
    │   │   └── ticket_service.py
    │   │
    │   ├── static\                     
    │   │   └── flights\
    │   │      └── css\
    │   │       ├── base.css     
    │   │       ├── book_step5.css     
    │   │       ├── flight_step3.css   
    │   │       ├── home_carousel.css    
    │   │       ├── home_search.css    
    │   │       ├── login_dropdown.css   
    │   │       ├── passenger_step1.css 
    │   │       ├── receipt_pdf.css 
    │   │       ├── search.css      
    │   │       ├── ticket_pdf.css  
    │   │       └── step2.css             
    │   │      └── img\
    │   │       ├── avion.png  
    │   │       ├── promo1.jpg   
    │   │       ├── promo5.jpg 
    │   │       ├── promo3.jpg 
    │   │       ├── promo4.jpg         
    │   │       └── promo5.jpg    
    │   │      └── js\   
    │   │       ├── book_step5.js    
    │   │       ├── book_step3.js    
    │   │       ├── home_carousel.js
    │   │       ├── home_search.js
    │   │       ├── search.js        
    │   │       └── login_dropdown.js      
    │   │
    │   ├── templates\                  
    │   │   └── flights\
    │   │       ├── base.html           
    │   │       ├── home.html           
    │   │       ├── flight_list.html    
    │   │       ├── create_flight.html  
    │   │       ├── check_in.html
    │   │       ├── book_step1.html     
    │   │       ├── book_step2.html     
    │   │       ├── book_step3.html     
    │   │       ├── book_step4.html     
    │   │       ├── book_step5.html     
    │   │       ├── book_success.html   
    │   │       ├── check_booked_flights.html   
    │   │       ├── about_ticket.html   
    │   │       ├── cancel_success.html 
    │   │       ├── empty_login.html         
    │   │       ├── password_reset.html        
    │   │       ├── password_reset_complete.html  
    │   │       ├── password_reset_confirm.html   
    │   │       ├── password_reset_done.html      
    │   │       ├──receipt_pdf_template.html
    │   │       ├──ticket_pdf_template.html
    │   │       └── register.html       
    │   │
    │   │   
    │   ├── views\                     
    │   │   ├── booking.py        
    │   │   ├── ajax.py           
    │   │   ├── auth.py    
    │   │   ├── flights.py   
    │   │   ├── tickets.py        
    │   │   └── __init__.py
    │   │   
    ├── staticfiles\            
        ├── admin\              
        └── flights\

```

---

## 📦 Technologies Used
- 🐍 Python (Django Framework)
- 🐘 PostgreSQL — primary database
- 🚀 Flyway — version-controlled database migrations
- 🐳 Docker & Docker Compose — containerized environment
- 💻 HTML, CSS, JavaScript
- 🎨 Bootstrap — frontend styling
- 💳 PayPal API — payment integration
- 📧 Google API — email services

---

## 🗄️ Database Technology

This project uses **PostgreSQL** as the primary database engine, managed through Flyway migrations for schema version control.
All database tables and structures are defined in SQL migration files stored under:
```bash
flyway/sql/
```
When the containers start, Flyway automatically applies any new migrations to keep the database schema up to date.


**Default configuration (docker-compose.yml):**
- Database: airline_db
- User: airline_user
- Password: airline_pass
- Port: 5432

This setup ensures consistent database state across all environments — development, testing, and production.


---

## 📅 Recent Updates

| Date | Version | Highlights |
|------|----------|-------------|
| **2025-10-25** | v1.0 | Base booking flow, flight search, login/register, ticket issue & cancel (**PLUS only**), seat map, admin CRUD for flights. |
| **2025-10-31** | v1.1 | Multi-passenger booking & seat selection; hide past flights (`date >= today`); new Step 4 (**Extras: luggage/equipment**) and Step 5 (**Payment**); total price includes extras × passengers; `Ticket.purchased_by` for per-user bookings list; **About Ticket** shows extras & PDF with Code128 barcode; session scoping for seats per flight; bugfixes & cleanup. |
| **2025-11-02** | v1.2 | Migrated project to **PostgreSQL** with **Flyway** and **Docker Compose**; added persistent schema migrations; configured `docker-compose.yml` and `Dockerfile`; removed old `db.sqlite3`; created superuser inside container; updated `.gitignore` and `README.md` with full Docker setup documentation. |
| **2025-11-07** | v1.3 | Cleanup & UI refactor: moved inline CSS/JS into static files ( `search.css/js`, `step2.css`,  `flight_step3.css`, etc.); extracted `COUNTRY_CHOICES` into `choices.py`; improved login/register pages with Forgot Password + Register Now; configured full email password-reset flow (Gmail SMTP + Django password reset views); bugfixes in multi-flight seat selection | 
| **2025-11-08** | v1.4 | Added PayPal Sandbox integration for flight payments (Step 5); implemented live PayPal button + payment confirmation; automatic PDF invoice generation (ReportLab) and email sending via Gmail SMTP after successful booking; moved PayPal scripts and overlay styles into static files (`book_step5.css` / `book_step5.js`); improved session cleanup and confirmation UX. | 
| **2025-11-15** | v1.5 | Major ticket system overhaul: Added QR code generation (qrcode + base64), Replaced barcode system, Full redesign of the boarding pass PDF (HTML + WeasyPrint), Extracted ticket CSS to /static/flights/ticket_pdf.css, Fixed missing template loader path & adjusted HTML template path, Refactored generate_ticket_pdf (clean buffer handling + external CSS load), Refactored invoice PDF with cleaner typography, section titles, margins, total row redesign, Cleaned requirements (WeasyPrint 60.1, pydyf 0.9.0, qrcode[pil]), Cleaned Dockerfile & docker-compose (removed ngrok, extra deps), Updated .gitignore (Flyway, Docker, staticfiles, venvs) | 
| 2025-11-18 | v1.6 | Added full Croatia Airlines–style home page search UI (custom dropdowns, country → airport → destination logic), Implemented dynamic destination filtering based on origin (ajax/origin_countries, ajax/airports, ajax/dest_countries, ajax/dest_airports), Added Round Trip & One-Way toggle with auto-hiding return date, Integrated dynamic date availability loading via `/ajax/available_dates/` for both legs, Replaced old select boxes with interactive custom dropdown panels, Fixed missing destination airport issue (Zagreb not showing for Neum), Added login-required search validation (origin+destination blocking), Added swap button & UI refinements, Cleaned and reorganized `home_search.js` logic (origin flow, destination flow, date loading, tripType), Updated `home.html` with new search bar, added trip type selector, improved structure and clarity, Fixed dropdown panel layouts & style alignment |
| 2025-11-20 | v1.7 | Implemented Check-In functionality — users can check in 24h before flight, otherwise displays error: “Check-in available 24h before departure.”. Added real timezone handling for flights (example: Helsinki flight stored as `10:00–13:00` in database, displays `14:00` (+1h) timezone). Introduced `race condition` handling for seat purchase — if two users try to buy the same seat, the slower one receives an error. Added passenger verification for check-in — requires first name, last name, and OIB as confirmation. Updated backend and database to support timezone-aware flight times and check-in validation. Minor UI refinements for check-in form (name, surname, OIB fields, error display). |
| 2026-01-02 | v1.8 | **Major Refactoring & Service Layer Implementation**: Extracted business logic from views into dedicated services (`BookingService`, `SeatmapService`, `TicketService`, `PdfService`, `EmailService`) for cleaner architecture. **Frontend Overhaul**: Switched Booking Step 5 (Payment) to use **JSON/AJAX** communication instead of form submission to fix PayPal redirect issues.  **Security**: Implemented `.env` file support using `python-dotenv` to secure sensitive credentials (`SECRET_KEY`, Database, Email, PayPal). Added Flatpickr and Select2 via CDN to `base.html` for better UI/UX.|


## 🚧 Future Improvements
- Cancel flight (admin) — delete flight from database
- Check all bought tickets by route 
- Admin dashboard with earnings display and statistics (daily/weekly/monthly, top routes, occupancy)
- currency handling
- Check-in notifications on gmail
- Dynamic airplane seat map (improved seat layout)
- Edit / change seat after booking
- Admin dashboard with analytics and statistics
- Automatic email reminders (push mail notifications)
- Loyalty program (reward points system)
- Coupons / promo code discounts
- Refund API (automated payment refunds)
- Multilingual support (EN, HR, DE)
- User profile page with history & stats
- Responsive design
- Automatic check-in notifications (Scheduled email reminders 24h before flight)
- Currency handling

---

## 📄 License
This project is open-source and free to use, modify, and distribute — attribution is appreciated.

---

## ✍️ Author
**Leon Serka**  
[https://github.com/leonserka](https://github.com/leonserka)

---

