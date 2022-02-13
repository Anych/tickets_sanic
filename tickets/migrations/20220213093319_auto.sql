-- migrate:up
CREATE TYPE gender AS ENUM ('M', 'F')
CREATE TYPE cabin AS ENUM ('Economy', 'Business')
CREATE TYPE offer_type AS ENUM ('OW', 'RT')
CREATE TYPE passenger_type AS ENUM ('ADT', 'CHD', 'INF')
CREATE TYPE passenger_type AS ENUM ('Amadeus', 'Sabre')

CREATE TABLE booking
(
    id serial NOT NULL,
    offer_id uuid NOT NULL,
    phone character varying(12) NOT NULL,
    email character varying(255) NOT NULL,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE booking OWNER to postgres;

-- migrate:down

