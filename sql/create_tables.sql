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
    color      CUBE
);

CREATE TABLE color_cube_country (
    color      INTEGER NOT NULL, -- references color_cube.id
    country    INTEGER NOT NULL  -- references country.id
);

CREATE TABLE country (
    id         SERIAL,
    code       VARCHAR(16)
);

CREATE UNIQUE INDEX color_cube_album_key_index ON color_cube (album_uri);
CREATE UNIQUE INDEX color_cube_id_index ON color_cube (id);
CREATE UNIQUE INDEX country_code_id_index ON country (id);
CREATE UNIQUE INDEX country_code_index ON country (code);
CREATE UNIQUE INDEX color_cube_country_color_index ON color_cube_country(color);
CREATE UNIQUE INDEX color_cube_country_country_index ON color_cube_country(country);

ALTER TABLE color_cube_country
    ADD CONSTRAINT color_cube_fk_color
    FOREIGN KEY (color)
    REFERENCES color_cube(id);

ALTER TABLE color_cube_country
    ADD CONSTRAINT color_cube_fk_country
    FOREIGN KEY (country)
    REFERENCES country(id);

COMMIT;
