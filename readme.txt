# ✈️ Airline Reservation System (Django)

Airline Reservation System je web aplikacija izrađena pomoću Django frameworka koja omogućuje korisnicima pretraživanje, rezervaciju i otkazivanje avionskih karata.  
Administrator putem Django Admin panela može upravljati letovima i pregledavati sve rezervacije.

------------------------------------------------------------
🚀 GLAVNE ZNAČAJKE
------------------------------------------------------------

👤 KORISNICI:
- Registracija i prijava korisnika
- Pretraživanje dostupnih letova prema polazištu, odredištu i datumu
- Višekorakni proces rezervacije:
  1. Unos osobnih podataka
  2. Odabir klase sjedala (BASIC, PLUS, PREMIUM)
  3. Odabir sjedala na karti zrakoplova
  4. Pregled i potvrda rezervacije
- Pregled svih kupljenih karata (Check Booked Flights)
- Detaljan prikaz svake karte (About Ticket)
- Otkazivanje karte (Cancel Ticket) – dostupno samo za PLUS klasu
- Nakon otkazivanja karte, sjedalo postaje ponovno dostupno

🧑‍💼 ADMINISTRATOR:
- Dodavanje, uređivanje i brisanje letova putem Django Admin panela
- Pregled svih rezervacija i statusa plaćanja

------------------------------------------------------------
🗄️ MODELI
------------------------------------------------------------

✈️ FLIGHT:
- Broj leta
- Grad polaska i odredišta
- Datum i vrijeme polaska
- Cijena leta

🎫 TICKET:
- Podaci o putniku (ime, prezime, OIB, email, telefon, država)
- Povezan let (ForeignKey → Flight)
- Klasa sjedala i broj sjedala
- Način plaćanja
- Status plaćanja: Paid / Refunded
- Status karte: Booked / Canceled

------------------------------------------------------------
⚙️ POKRETANJE PROJEKTA LOKALNO
------------------------------------------------------------

1️⃣ Kloniraj repozitorij:
    git clone https://github.com/<your_username>/airline_reservation_django.git
    cd airline_reservation_django

2️⃣ Instaliraj potrebne pakete:
    pip install -r requirements.txt

3️⃣ Pokreni migracije baze:
    python manage.py migrate

4️⃣ Pokreni razvojni server:
    python manage.py runserver

5️⃣ Otvori u pregledniku:
    http://127.0.0.1:8000/

------------------------------------------------------------
👩‍💻 ADMIN PANEL
------------------------------------------------------------

Pristup admin panelu:
    http://127.0.0.1:8000/admin/

Za kreiranje admin korisnika:
    python manage.py createsuperuser

------------------------------------------------------------
📦 TEHNOLOGIJE
------------------------------------------------------------
- Python (Django Framework)
- SQLite / PostgreSQL baza podataka
- HTML, CSS, JavaScript
- Bootstrap (za frontend stilizaciju)

------------------------------------------------------------
📄 LICENCA
------------------------------------------------------------

Ovaj projekt je otvorenog koda i može se slobodno koristiti, mijenjati i dijeliti uz navođenje autora.

------------------------------------------------------------
✍️ AUTOR
------------------------------------------------------------

Ime autora: <Tvoje ime>  
GitHub profil: https://github.com/<your_username>

------------------------------------------------------------
