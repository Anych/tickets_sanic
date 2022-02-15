-- migrate:up
CREATE TYPE gender AS ENUM ('M', 'F');
CREATE TYPE cabin AS ENUM ('Economy', 'Business');
CREATE TYPE offer_type AS ENUM ('OW', 'RT');
CREATE TYPE passenger_type AS ENUM ('ADT', 'CHD', 'INF');
CREATE TYPE provider AS ENUM ('Amadeus', 'Sabre');

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
    id bigserial NOT NULL UNIQUE,
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


-- migrate:down
