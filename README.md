# ✈️ Airline Reservation System (Django)

The **Airline Reservation System** is a web application built with the Django framework that enables users to search, book, and cancel flight tickets.  
Administrators can manage flights and view all reservations through the Django Admin Panel.

---

## 🚀 Main Features

### 👤 Users
- User registration and login  
- Search for available flights by origin, destination, and date  
- Multi-step booking process:
  1. Enter personal information  
  2. Choose seat class (**Basic**, **Plus**, **Premium**)  
  3. Select a seat on the airplane map  
  4. Review and confirm the booking  
- View all purchased tickets (**Check Booked Flights**)  
- View details of each ticket (**About Ticket**)  
- Cancel a ticket (**Cancel Ticket**) – available only for **PLUS** class  
- When a ticket is canceled, the seat automatically becomes available again  

### 🧑‍💼 Administrator
- Add, edit, and delete flights through the **Django Admin Panel**  
- View all booked tickets and their payment status  

---

## 🗄️ Models

### ✈️ Flight
Contains flight details:
- Flight number  
- Departure and destination cities  
- Date and time of departure  
- Flight price  

### 🎫 Ticket
Contains ticket and passenger details:
- Passenger info (name, surname, OIB, email, phone, country)  
- Linked flight (**ForeignKey → Flight**)  
- Seat class and seat number  
- Payment method  
- **Payment Status:** Paid / Refunded  
- **Ticket Status:** Booked / Canceled  

---

## ⚙️ How to Run Locally

1️⃣ **Clone the repository**
```bash
git clone https://github.com/leonserka/airline-reservation-system-final-.git
cd airline_reservation_django
```

2️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

3️⃣ **Apply database migrations**
```bash
python manage.py migrate
```

4️⃣ **Start the development server**
```bash
python manage.py runserver
```

5️⃣ **Open in browser**
```
http://127.0.0.1:8000/
```

---

## 👩‍💻 Admin Panel

Access the Django Admin interface:
```
http://127.0.0.1:8000/admin/
```

Create a superuser:
```bash
python manage.py createsuperuser
```

---

## 🗂️ Project Structure
```
airline_reservation_django/
├── airline_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── flights/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── static/
│   └── templates/
└── manage.py
```

---

## 📦 Technologies Used
- Python (Django Framework)  
- SQLite / PostgreSQL database  
- HTML, CSS, JavaScript  
- Bootstrap (for frontend styling)

---

## 🚧 Future Improvements
More information coming soon — still deciding what to add next.

---

## 📄 License
This project is open-source and free to use, modify, and distribute — attribution is appreciated.

---

## ✍️ Author
**Leon Serka**  
[https://github.com/leonserka](https://github.com/leonserka)
