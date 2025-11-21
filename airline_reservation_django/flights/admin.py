from django.contrib import admin
from .models import Flight, Ticket

class FlightAdmin(admin.ModelAdmin):
    list_display = (
        'flight_number',
        'departure_city',
        'arrival_city',
        'date',
        'departure_time',
        'available_seats',
        'flight_type'
    )
    list_filter = ('departure_city', 'arrival_city', 'date', 'flight_type')
    search_fields = ('flight_number', 'departure_city', 'arrival_city')

    fields = (
        'flight_number',
        'departure_country',
        'departure_city',
        'departure_timezone',
        'arrival_country',
        'arrival_city',
        'arrival_timezone',
        'date',
        'departure_time',
        'arrival_time',
        'price',
        'total_seats',
        'available_seats',
        'flight_type'
    )


class TicketAdmin(admin.ModelAdmin):
    list_display = ('passenger_name', 'passenger_surname', 'flight', 'seat_class', 'seat_number', 'price_paid')
    list_filter = ('seat_class',)
    search_fields = ('passenger_name', 'passenger_surname', 'id_number', 'email')
    readonly_fields = ('created_at',)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Ticket, TicketAdmin)
