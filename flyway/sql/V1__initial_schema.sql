-- V1__initial_schema.sql
-- =====================================
--  Minimal Flyway Initial Schema for airline_reservation_django
--  Matches Django models from flights/models.py
-- =====================================


CREATE TABLE flights_flight (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(10) NOT NULL,
    departure_city VARCHAR(50) NOT NULL,
    arrival_city VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    price NUMERIC(8,2) NOT NULL,
    total_seats INTEGER NOT NULL,
    available_seats INTEGER NOT NULL,
    flight_type VARCHAR(3) NOT NULL
);

CREATE TABLE flights_ticket (
    id SERIAL PRIMARY KEY,
    flight_id INTEGER NOT NULL REFERENCES flights_flight(id) ON DELETE CASCADE,
    passenger_name VARCHAR(50) NOT NULL,
    passenger_surname VARCHAR(50) NOT NULL,
    id_number VARCHAR(11) NOT NULL,
    country_code VARCHAR(10) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    seat_class VARCHAR(10) NOT NULL,
    seat_number VARCHAR(5),
    price_paid NUMERIC(8,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    extra_luggage VARCHAR(30),
    extra_equipment VARCHAR(50),
    purchased_by_id INTEGER,
    payment_status VARCHAR(10) DEFAULT 'paid',
    status VARCHAR(10) DEFAULT 'booked'
);

CREATE INDEX idx_ticket_flight ON flights_ticket(flight_id);
CREATE INDEX idx_ticket_purchased_by ON flights_ticket(purchased_by_id);
