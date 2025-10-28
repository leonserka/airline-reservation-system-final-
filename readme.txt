✈️ Airline Reservation System (Django)

Airline Reservation System is a web application built with the Django framework that allows users to search, book, and cancel flight tickets.
Administrators can manage flights through the Django admin panel, while users can view and manage their personal bookings.

🚀 Features
👤 Users

User registration and login

Search for available flights by origin, destination, and date

Multi-step booking process:

Enter personal information

Choose seat class (Basic, Plus, Premium)

Select a seat on the airplane map

Review and confirm the booking

View all purchased tickets (Check Booked Flights)

View ticket details (About Ticket)

Cancel a ticket (Cancel Ticket) – available only for PLUS class

When a ticket is canceled, the seat automatically becomes available again

🧑‍💼 Administrator

Add, edit, and delete flights via Django Admin Panel

View all booked tickets and payment statuses

🗄️ Models
Flight

Contains flight details:

Flight number

Departure city & destination city

Date, time, and price

Ticket

Contains booking details:

Passenger info (name, surname, OIB, email, phone, country)

Related flight (ForeignKey → Flight)

Seat class and seat number

Payment method

Payment Status: Paid / Refunded

Status: Booked / Canceled
