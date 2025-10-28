✈️ <b>Airline Reservation System (Django)</b><br><br>

<b>Airline Reservation System</b> is a web application built with the <b>Django framework</b> that allows users to search, book, and cancel flight tickets.<br>
Administrators can manage flights through the Django admin panel, while users can view and manage their own bookings.<br><br>

<hr>

🚀 <b>Features</b><br><br>

👤 <b>Users</b><br>
• User registration and login<br>
• Search for available flights by origin, destination, and date<br>
• Multi-step booking process:<br>
&nbsp;&nbsp;1️⃣ Enter personal information<br>
&nbsp;&nbsp;2️⃣ Choose seat class (<b>Basic</b>, <b>Plus</b>, <b>Premium</b>)<br>
&nbsp;&nbsp;3️⃣ Select a seat on the airplane map<br>
&nbsp;&nbsp;4️⃣ Review and confirm the booking<br>
• View all purchased tickets (<b>Check Booked Flights</b>)<br>
• View details of each ticket (<b>About Ticket</b>)<br>
• Cancel a ticket (<b>Cancel Ticket</b>) – available only for <b>PLUS</b> class<br>
• When a ticket is canceled, the seat automatically becomes available again<br><br>

🧑‍💼 <b>Administrator</b><br>
• Add, edit, and delete flights through the <b>Django Admin Panel</b><br>
• View all booked tickets and their payment status<br><br>

<hr>

🗄️ <b>Models</b><br><br>

✈️ <b>Flight</b><br>
Contains flight details:<br>
• Flight number<br>
• Departure and destination cities<br>
• Date, time, and price<br><br>

🎫 <b>Ticket</b><br>
Contains booking details:<br>
• Passenger information (name, surname, OIB, email, phone, country)<br>
• Linked flight (<b>ForeignKey → Flight</b>)<br>
• Seat class and seat number<br>
• Payment method<br>
• <b>Payment Status:</b> Paid / Refunded<br>
• <b>Status:</b> Booked / Canceled<br><br>

<hr>

⚙️ <b>Run the Project Locally</b><br><br>

<b>1️⃣ Clone the Repository</b><br>
<pre>
git clone https://github.com/&lt;your_username&gt;/airline_reservation_django.git
cd airline_reservation_django
</pre><br>

<b>2️⃣ Create a Virtual Environment</b><br>
<pre>
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
</pre><br>

<b>3️⃣ Install Dependencies</b><br>
<pre>
pip install -r requirements.txt
</pre><br>

<b>4️⃣ Apply Migrations</b><br>
<pre>
python manage.py makemigrations
python manage.py migrate
</pre><br>

<b>5️⃣ Create a Superuser</b><br>
<pre>
python manage.py createsuperuser
</pre><br>

<b>6️⃣ Run the Server</b><br>
<pre>
python manage.py runserver
</pre><br>

Then open 👉 <a href="http://localhost:8000" target="_blank">http://localhost:8000</a><br><br>

<hr>

🧩 <b>Technologies Used</b><br>
• Python (Django Framework)<br>
• HTML, CSS, JavaScript<br>
• SQLite / MySQL (configurable)<br><br>

<hr>

💡 <b>Future Improvements</b><br>
• Email notifications after booking or cancellation<br>
• Integration with real flight APIs<br>
• Enhanced seat selection interface<br>
• Online payment gateway integration<br><br>

<hr>

👨‍💻 <b>Author</b><br>
Developed by <b>Leon Serka</b><br>
🔗 <a href="https://github.com/leonserka" target="_blank">GitHub Profile</a><br><br>

<hr>

🖼️ <b>Preview (optional)</b><br>
Add screenshots here to show your project interface:<br><br>

<pre>
![Home Page](screenshots/homepage.png)
![Booking Page](screenshots/booking.png)
![Admin Panel](screenshots/admin.png)
</pre><br>
