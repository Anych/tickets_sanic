-- migrate:up
CREATE TYPE gender AS ENUM ('M', 'F');
CREATE TYPE cabin AS ENUM ('Economy', 'Business');
CREATE TYPE offer_type AS ENUM ('OW', 'RT');
CREATE TYPE passenger_type AS ENUM ('ADT', 'CHD', 'INF');
CREATE TYPE provider AS ENUM ('Amadeus', 'Sabre');

CREATE TABLE public.booking
(
    id serial NOT NULL,
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


CREATE TABLE currency_exchange
(
    id serial,
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



-- migrate:down

CREATE TABLE public.offer
(
    id serial NOT NULL,
    booking_id integer NOT NULL,
    offer_id uuid NOT NULL,
    refundable boolean DEFAULT FALSE,
    baggage character varying(5),
    cabin cabin,
    airline integer NOT NULL,
    passengers integer NOT NULL,
    type offer_type NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT booking_fkey FOREIGN KEY (booking_id)
        REFERENCES public.booking (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
        NOT VALID,
    CONSTRAINT airline_fkey FOREIGN KEY (airline)
        REFERENCES public.airline (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL
        NOT VALID,
    CONSTRAINT passengers_fkey FOREIGN KEY (passengers)
        REFERENCES public.passengers (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL
        NOT VALID
)
WITH (
    OIDS = FALSE
);

ALTER TABLE public.offer
    OWNER to postgres;
