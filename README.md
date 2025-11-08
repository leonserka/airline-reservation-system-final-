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
- View all purchased tickets (**Check Booked Flights**) — shows tickets bought by the logged-in user (even for other passengers)
- View ticket details (**About Ticket**) — includes extras and PDF ticket with Code128 barcode  
- Cancel a ticket (**Cancel Ticket**) – available only for **PLUS** class  
- When a ticket is canceled, the seat automatically becomes available again  

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
- Date and time of departure  
- Flight price 
- Seat availability
- Flight type (Domestic / International) 

### 🎫 Ticket
Contains ticket and passenger details:
- Passenger info (name, surname, ID number, email, phone, country)  
- Linked flight (**ForeignKey → Flight**)  
- Seat class and seat number  
- Payment method  
- **Payment Status:** Paid / Refunded  
- **Ticket Status:** Booked / Canceled
- **Purchased By:** `auth.user` (who paid for the booking) 

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

2️⃣ **Build and start all containers**
```bash
docker-compose up --build
```
This will:
- Start the PostgreSQL database on port 5432
- Automatically apply all Flyway migrations (`/flyway/sql/V1__initial_schema.sql`)
- Launch the Django app on port 8000

3️⃣ **Open in browser**
```bash
http://127.0.0.1:8000/
```

4️⃣ **Access the Django Admin Panel**
Access the Django Admin interface:
```bash
http://127.0.0.1:8000/admin/
```

Create a superuser (inside the container):
```bash
docker exec -it airline_django python manage.py createsuperuser

```


5️⃣ **Stop containers**
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
├── requirements.txt                # Project dependencies
├── README.md                       # Project documentation
├── Dockerfile                      # Defines how the Django application is built inside a container
├── docker-compose.yml              # Orchestrates all services (Django, PostgreSQL, and Flyway) and runs them together.
├── .gitignore                      # Git ignore rules
├── venv\
├── flyway\                         # Contains database migration scripts
│   └── sql\                        
│       └── V1__initial_schema.sql  # Initial PostgreSQL schema
│
└── airline_reservation_django\
    ├── manage.py                   # Django management script (runserver, migrate, etc.)
    │
    ├── airline_project\            # Main Django project configuration
    │   ├── __init__.py
    │   ├── settings.py             # Project settings (database, apps, middleware)
    │   ├── urls.py                 # Root URL configuration
    │   ├── wsgi.py                 # Root URL configuration
    │   └── asgi.py                 # ASGI entry point (for async servers)
    │
    ├── flights\                    # Core application module
    │   ├── __init__.py
    │   ├── admin.py                # Django admin configuration for models
    │   ├── apps.py                 # App registration
    │   ├── country_codes.py        # Country code list for form dropdowns
    │   ├── choices.py              # Centralized reusable choice lists
    │   ├── forms.py                # Django forms (booking, registration, etc.)
    │   ├── models.py               # Database models (Flight, Ticket)
    │   ├── tests.py                # Automated tests
    │   ├── urls.py                 # App-specific routes
    │   │
    │   │
    │   ├── static\                     # Static files (CSS, JS, images)
    │   │   └── flights\
    │   │       ├── avion.png           # Airplane image used in templates
    │   │       ├── base.css            # Global CSS styles
    │   │       ├── flight_list.js      # Script for filtering/searching flights
    │   │       ├── flight_step1.js     # Handles Step 1 interactions
    │   │       ├── flight_step3.css    # Seat map styling
    │   │       ├── flight_step3.js     # Seat selection logic
    │   │       ├── login.css           # Styling for login page
    │   │       ├── passenger_step1.css # Styling for passenger details (Step 1)
    │   │       ├── search.css          # Styling for flight search UI
    │   │       ├── search.js           # JS logic for dynamic flight search
    │   │       └── step2.css           # Styling for seat class selection (Step 2)
    │   │
    │   ├── templates\                  # HTML templates for the application
    │   │   └── flights\
    │   │       ├── base.html           # Main layout template (navbar, footer)
    │   │       ├── home.html           # Home page with flight search form
    │   │       ├── flight_list.html    # Search results with available flights
    │   │       ├── create_flight.html  # Admin page to add new flights
    │   │       ├── book_flight.html    # Booking overview page
    │   │       ├── book_step1.html     # Step 1: Personal information
    │   │       ├── book_step2.html     # Step 2: Seat class selection
    │   │       ├── book_step3.html     # Step 3: Seat map selection
    │   │       ├── book_step4.html     # Step 4: Adding extras
    │   │       ├── book_step5.html     # Step 5: Confirmation and payment
    │   │       ├── book_success.html   # Success message after booking
    │   │       ├── check_booked_flights.html   # User’s booked tickets list
    │   │       ├── about_ticket.html   # Detailed ticket information
    │   │       ├── cancel_success.html # Ticket cancellation confirmation
    │   │       ├── login.html          # User login page
    │   │       ├── password_reset.html # Form where user enters email to reset password        
    │   │       ├── password_reset_complete.html  # Final success page after password is changed
    │   │       ├── password_reset_confirm.html   # Page where user sets a new password (token link)
    │   │       ├── password_reset_done.html      # Confirmation that reset email was sent
    │   │       └── register.html       # User registration page
    │   │
    │   ├── utils\                       # Helper utilities used across the app
    │   │   ├── pdf_generator.py         # Generates PDF tickets with passenger and flight details (includes barcode)
    │   │   └── __init__.py
    │   │   
    │   ├── views\                      # Split views for better code organization
    │   │   ├── booking_views.py        # Handles flight search, multi-step booking, seat selection, and payments
    │   │   ├── misc_views.py           # Contains home, login/logout, registration, and general-purpose views
    │   │   ├── ticket_views.py         # Manages booked tickets, cancellations, and PDF ticket generation
    │   │   └── __init__.py
    │   │   
    ├── staticfiles\            # Collected static files for deployment
    │   ├── admin\              # Django admin assets (css, js, img, fonts)
    │   └── flights\
    │
    └── venv\

```

---

## 📦 Technologies Used
- 🐍 Python (Django Framework)
- 🐘 PostgreSQL — primary database
- 🚀 Flyway — version-controlled database migrations
- 🐳 Docker & Docker Compose — containerized environment
- 💻 HTML, CSS, JavaScript
- 🎨 Bootstrap — frontend styling

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



## 🚧 Future Improvements
- Admin section: List all flights with filter by route (departure Split, arrival Madrid)
- Cancel flight (admin) — delete flight from database
- Check all bought tickets by route 
- Admin dashboard with earnings display and statistics (daily/weekly/monthly, top routes, occupancy)


---

## 📄 License
This project is open-source and free to use, modify, and distribute — attribution is appreciated.

---

## ✍️ Author
**Leon Serka**  
[https://github.com/leonserka](https://github.com/leonserka)

---

