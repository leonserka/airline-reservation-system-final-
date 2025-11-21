ALTER TABLE flights_flight
ADD COLUMN departure_timezone VARCHAR(50) DEFAULT 'Europe/Zagreb';

ALTER TABLE flights_flight
ADD COLUMN arrival_timezone VARCHAR(50) DEFAULT 'Europe/Zagreb';
