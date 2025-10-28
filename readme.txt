<h1 align="center">✈️ Airline Reservation System (Django)</h1>

<p align="center">
  <b>Airline Reservation System</b> is a web application built with the <b>Django framework</b> that allows users to search, book, and cancel flight tickets.<br>
  Administrators can manage flights through the Django admin panel, while users can view and manage their own bookings.
</p>

<hr>

<h2>🚀 Features</h2>

<h3>👤 Users</h3>
<ul>
  <li>User registration and login</li>
  <li>Search for available flights by origin, destination, and date</li>
  <li>Multi-step booking process:</li>
  <ol>
    <li>Enter personal information</li>
    <li>Choose seat class (<b>Basic</b>, <b>Plus</b>, <b>Premium</b>)</li>
    <li>Select a seat on the airplane map</li>
    <li>Review and confirm the booking</li>
  </ol>
  <li>View all purchased tickets (<b>Check Booked Flights</b>)</li>
  <li>View details of each ticket (<b>About Ticket</b>)</li>
  <li>Cancel a ticket (<b>Cancel Ticket</b>) – available only for <b>PLUS</b> class</li>
  <li>When a ticket is canceled, the seat automatically becomes available again</li>
</ul>

<h3>🧑‍💼 Administrator</h3>
<ul>
  <li>Add, edit, and delete flights through the <b>Django Admin Panel</b></li>
  <li>View all booked tickets and their payment status</li>
</ul>

<hr>

<h2>🗄️ Models</h2>

<h3>✈️ Flight</h3>
Contains flight details:<br>
• Flight number<br>
• Departure and destination cities<br>
• Date, time, and price<br><br>

<h3>🎫 Ticket</h3>
Contains booking details:<br>
• Passenger information (name, surname, OIB, email, phone, country)<br>
• Linked flight (<b>ForeignKey → Flight</b>)<br>
• Seat class and seat number<br>
• Payment method<br>
• <b>Payment Status:</b> Paid / Refunded<br>
• <b>Status:</b> Booked / Canceled<br>

<hr>

<h2>⚙️ Run the Project Locally</h2>

<b>1️⃣ Clone the Repository</b><br>

```bash
git clone https://github.com/<your_username>/airline_reservation_django.git
cd airline_reservation_django
