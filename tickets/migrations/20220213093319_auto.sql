-- migrate:up
CREATE TYPE gender AS ENUM ('M', 'F');
CREATE TYPE cabin AS ENUM ('Economy', 'Business');
CREATE TYPE offer_type AS ENUM ('OW', 'RT');
CREATE TYPE passenger_type AS ENUM ('ADT', 'CHD', 'INF');
CREATE TYPE provider AS ENUM ('Amadeus', 'Sabre');


-- airport
CREATE TABLE public.airport
(
    id serial NOT NULL,
    code character varying(3) NOT NULL,
    name character varying(30) NOT NULL,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.airport
    OWNER to postgres;


-- route_point
CREATE TABLE public.route_point
(
    id serial NOT NULL UNIQUE,
    time_at character varying(30) NOT NULL,
    airport_id integer NOT NULL,
    terminal character varying(10) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT airport_fkey FOREIGN KEY (airport_id)
        REFERENCES public.airport (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
        NOT VALID
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.route_point
    OWNER to postgres;


-- document
CREATE TABLE public.document
(
    id serial NOT NULL,
    number character varying(30) NOT NULL,
    expires_at character varying(10) NOT NULL,
    iin character varying(12) NOT NULL,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.document
    OWNER to postgres;


-- booking
CREATE TABLE public.booking
(
    id bigserial NOT NULL UNIQUE,
    booking_id uuid NOT NULL UNIQUE,
    pnr character varying(6) NOT NULL,
    expires_at character varying(32) NOT NULL,
    phone character varying(12) NOT NULL,
    email character varying(255) NOT NULL,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.booking OWNER to postgres;


-- passenger
CREATE TABLE public.passenger
(
    id bigserial NOT NULL,
    gender gender NOT NULL,
    type passenger_type NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    date_of_birth character varying(10) NOT NULL,
    citizenship character varying(2) NOT NULL,
    document_id integer NOT NULL,
    booking_id integer NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT document_fkey FOREIGN KEY (document_id)
        REFERENCES public.document (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT booking_fkey FOREIGN KEY (booking_id)
        REFERENCES public.booking (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
        NOT VALID
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.passenger
    OWNER to postgres;


-- currency_exchange
CREATE TABLE currency_exchange
(
    id serial NOT NULL UNIQUE,
    title character varying(3) NOT NULL,
    description numeric(6, 2) NOT NULL,
    quantity integer NOT NULL,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE currency_exchange
    OWNER to postgres;


-- logo
CREATE TABLE public.logo
(
    id serial NOT NULL UNIQUE,
    url character varying(512) NOT NULL,
    height integer,
    weight integer,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.logo
    OWNER to postgres;


-- airline
CREATE TABLE public.airline
(
    id bigserial NOT NULL UNIQUE,
    code character varying(3) NOT NULL,
    name character varying(50) NOT NULL,
    logo_id integer,
    PRIMARY KEY (id),
    CONSTRAINT logo_fkey FOREIGN KEY (logo_id)
        REFERENCES public.logo (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
        NOT VALID
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.airline
    OWNER to postgres;


-- passengers
CREATE TABLE public.passengers
(
    id bigserial NOT NULL UNIQUE,
    "ADT" smallint DEFAULT 1,
    "CHD" smallint DEFAULT 0,
    "INF" smallint DEFAULT 0,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.passengers
    OWNER to postgres;


-- offer
CREATE TABLE public.offer
(
    id bigserial NOT NULL UNIQUE,
    booking_id bigint NOT NULL UNIQUE,
    offer_id uuid NOT NULL,
    refundable boolean DEFAULT FALSE,
    baggage character varying(5),
    cabin cabin,
    airline integer NOT NULL,
    passengers int NOT NULL,
    type offer_type NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT booking_fkey FOREIGN KEY (booking_id)
        REFERENCES public.booking (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
        NOT VALID,
    CONSTRAINT airline_fkey FOREIGN KEY (airline)
        REFERENCES public.airline (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT passengers_fkey FOREIGN KEY (passengers)
        REFERENCES public.passengers (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
        NOT VALID
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.offer
    OWNER to postgres;


-- flight
CREATE TABLE public.flight
(
    id bigserial NOT NULL,
    offer_id bigint NOT NULL,
    duration integer NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT offer_fkey FOREIGN KEY (offer_id)
        REFERENCES public.offer (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.flight
    OWNER to postgres;


-- segment
CREATE TABLE public.segment
(
    id serial NOT NULL,
    flight_id bigint NOT NULL,
    operating_airline character varying(3) NOT NULL,
    flight_number character varying(30) NOT NULL,
    equipment character varying(30) NOT NULL,
    cabin cabin NOT NULL,
    departure_id bigint NOT NULL,
    arrive_id bigint NOT NULL,
    baggage character varying(5),
    PRIMARY KEY (id),
    CONSTRAINT flight_fkey FOREIGN KEY (flight_id)
        REFERENCES public.flight (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID,
    CONSTRAINT departure_fkey FOREIGN KEY (departure_id)
        REFERENCES public.route_point (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
        NOT VALID,
    CONSTRAINT arrive_fkey FOREIGN KEY (arrive_id)
        REFERENCES public.route_point (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE NO ACTION
        NOT VALID
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.segment
    OWNER to postgres;


-- price
CREATE TABLE public.price
(
    id bigserial NOT NULL UNIQUE,
    price numeric(8) NOT NULL,
    currency character varying(3) NOT NULL,
    offer_id bigint NOT NULL UNIQUE,
    PRIMARY KEY (id),
    CONSTRAINT offer_fkey FOREIGN KEY (offer_id)
        REFERENCES public.offer (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.price
    OWNER to postgres;

INSERT INTO airport
VALUES (1, 'ALA', 'Алматы');

INSERT INTO airport
VALUES (2, 'NQZ', 'Нур-Султан (Астана)');

INSERT INTO route_point
VALUES (1, '2022-02-20T03:25:00+06:00', 1, '1');

INSERT INTO route_point
VALUES (2, '2022-02-20T05:05:00+06:00', 2, '2');

INSERT INTO route_point
VALUES (3, '2022-02-21T03:10:00+06:00', 2, '2');

INSERT INTO route_point
VALUES (4, '2022-02-21T06:45:00+06:00', 1, '1');

INSERT INTO booking
VALUES (1, '8a5118b7-dd4d-4761-b09e-208b88edcfbe', 'HKBTXK', '2022-01-23T15:10:14.411858+06:00', '+77013748830', 'example@mail.com');

INSERT INTO document
VALUES (1, 'N09472779', '02.05.2022', '920502300060');

INSERT INTO passenger
VALUES (1, 'M', 'ADT', 'Umarov', 'Anuarbek', '02.05.1992', 'KZ', 1, 1);

INSERT INTO logo
VALUES (1, 'https://avia-api.k8s-test.aviata.team/img/5661-501f546c73c976a96cf0d18e600b4d7a.gif', 1416, 274);

INSERT INTO airline
VALUES (1, 'DV', 'SCAT', 1);

INSERT INTO passengers
VALUES (1, 1, 0, 0);

INSERT INTO offer
VALUES (1, 1, '3c0d66ca-47e2-4e4e-9c9f-21b774b64a7f', true, '1PC', 'Economy', 1, 1, 'OW');

INSERT INTO price
VALUES (1, 120000, 'KZT', 1);

INSERT INTO flight
VALUES (1, 1, 6000);

INSERT INTO flight
VALUES (2, 1, 30900);

INSERT INTO segment
VALUES (1, 1, 'IQ', '843', 'Airbus A300 Freighter', 'Economy', 1, 2, '1PC');

INSERT INTO segment
VALUES (2, 2, 'IQ', '652', 'Boeing 757', 'Economy', 2, 1, '1PC');

-- migrate:down
