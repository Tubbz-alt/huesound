--
-- PostgreSQL database dump
--

BEGIN;

CREATE TABLE color_cube (
    id         SERIAL,
    album_uri  TEXT,
    red        INTEGER,
    green      INTEGER,
    blue       INTEGER,
    color      CUBE,
    countries  INTEGER NOT NULL -- references country_string,
    image_id   TEXT
);

CREATE TABLE country (
    id         SERIAL,
    code       VARCHAR(16)
);

CREATE TABLE country_string (
    id         SERIAL,
    string     TEXT
);

CREATE TABLE country_string_country (
    country_string INTEGER NOT NULL, -- references country_string
    country        INTEGER NOT NULL  -- references country
);

CREATE UNIQUE INDEX color_cube_ndx_album_key ON color_cube (album_uri);
CREATE UNIQUE INDEX color_cube_ndx_id ON color_cube (id);
CREATE UNIQUE INDEX country_ndx_id ON country (id);
CREATE UNIQUE INDEX country_ndx_code ON country (code);
CREATE UNIQUE INDEX country_string_ndx_id ON country_string (id);
CREATE UNIQUE INDEX country_string_ndx_string ON country_string (string);
CREATE INDEX country_string_country_ndx_country_string ON country_string_country (country_string);
CREATE INDEX country_string_country_ndx_country ON country_string_country (country);

ALTER TABLE color_cube
    ADD CONSTRAINT color_cube_fk_countries
    FOREIGN KEY (countries)
    REFERENCES country_string(id);

ALTER TABLE country_string_country
    ADD CONSTRAINT country_string_country_fk_country_string
    FOREIGN KEY (country_string)
    REFERENCES country_string(id);

ALTER TABLE country_string_country
    ADD CONSTRAINT country_string_country_fk_country
    FOREIGN KEY (country)
    REFERENCES country(id);

COMMIT;
