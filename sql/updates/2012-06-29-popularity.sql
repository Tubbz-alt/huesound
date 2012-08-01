BEGIN;

alter table color_cube add column popularity real default -1.0;

COMMIT;
