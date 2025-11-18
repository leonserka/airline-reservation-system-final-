from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Flight, Ticket
from .country_codes import COUNTRY_CODES
from .choices import COUNTRY_CHOICES


class FlightForm(forms.ModelForm):
    departure_country = forms.ChoiceField(
        choices=COUNTRY_CHOICES, label="Departure Country"
    )
    arrival_country = forms.ChoiceField(
        choices=COUNTRY_CHOICES, label="Arrival Country"
    )

    class Meta:
        model = Flight
        fields = [
            "flight_number",
            "departure_country", "departure_city",
            "arrival_country", "arrival_city",
            "date", "departure_time", "arrival_time",
            "price", "total_seats", "available_seats",
            "flight_type",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "departure_time": forms.TimeInput(attrs={"type": "time"}),
            "arrival_time": forms.TimeInput(attrs={"type": "time"}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class FlightSearchForm(forms.Form):
    departure_city = forms.ChoiceField(choices=[], label="Departure")
    arrival_city = forms.ChoiceField(choices=[], label="Arrival")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        departures = (
            Flight.objects.order_by()
            .values_list("departure_city", flat=True)
            .distinct()
        )

        arrivals = (
            Flight.objects.order_by()
            .values_list("arrival_city", flat=True)
            .distinct()
        )

        self.fields["departure_city"].choices = [(c, c) for c in departures]
        self.fields["arrival_city"].choices = [(c, c) for c in arrivals]

        self.routes = {
            dep: list(
                Flight.objects.filter(departure_city=dep)
                .values_list("arrival_city", flat=True)
                .distinct()
            )
            for dep in departures
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            "passenger_name",
            "passenger_surname",
            "id_number",
            "country_code",
            "phone_number",
            "seat_class",
            "seat_number",
            "payment_method",
        ]


class PassengerForm(forms.ModelForm):
    country_code = forms.ChoiceField(choices=COUNTRY_CODES)

    class Meta:
        model = Ticket
        fields = [
            "passenger_name",
            "passenger_surname",
            "id_number",
            "country_code",
            "phone_number",
            "email",
        ]
        widgets = {
            "id_number": forms.TextInput(attrs={"maxlength": 11}),
            "email": forms.EmailInput(),
        }


class SeatSelectionForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["seat_class", "seat_number"]

    def __init__(self, *args, flight=None, **kwargs):
        self.flight = flight
        super().__init__(*args, **kwargs)

        if flight:
            taken = self.flight.ticket_set.values_list("seat_number", flat=True)
            all_seats = [str(i) for i in range(1, self.flight.total_seats + 1)]
            available = [s for s in all_seats if s not in taken]

            self.fields["seat_number"].widget = forms.Select(
                choices=[(s, s) for s in available]
            )
