ALTER TABLE flights_ticket
ADD COLUMN checked_in BOOLEAN DEFAULT FALSE;

ALTER TABLE flights_ticket
ADD COLUMN checked_in_at TIMESTAMP NULL;
