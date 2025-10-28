# ✈️ Airline Reservation System (Django)

**Airline Reservation System** is a web application built with the **Django framework** that allows users to search, book, and cancel flight tickets.  
Administrators can manage flights through the Django admin panel, while users can view and manage their own bookings.  

---

## 🚀 Features

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
- Date, time, and price  

### 🎫 Ticket
Contains booking details:  
- Passenger information (name, surname, OIB, email, phone, country)  
- Linked flight (**ForeignKey → Flight**)  
- Seat class and seat number  
- Payment method  
- **Payment Status:** Paid / Refunded  
- **Status:** Booked / Canceled  

---

## ⚙️ Run the Project Locally

**1️⃣ Clone the Repository**
```bash
git clone https://github.com/<your_username>/airline_reservation_django.git
cd airline_reservation_django
