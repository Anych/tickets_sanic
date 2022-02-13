-- migrate:up
CREATE TABLE public.booking
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

ALTER TABLE public.booking
    OWNER to postgres;

-- migrate:down

