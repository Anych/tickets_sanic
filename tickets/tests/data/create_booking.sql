CREATE SCHEMA test AUTHORIZATION postgres;

CREATE TABLE test.booking
(
    id bigserial NOT NULL UNIQUE,
    booking_id uuid NOT NULL UNIQUE,
    pnr character varying(6) NOT NULL,
    expires_at character varying(32) NOT NULL,
    phone character varying(12) NOT NULL,
    email character varying(255) NOT NULL,
    offer json NOT NULL,
    passengers json NOT NULL,
    PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
);

ALTER TABLE test.booking OWNER to postgres;
