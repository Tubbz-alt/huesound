alter table album add column type text;
alter table album add column year integer;
CREATE INDEX album_ndx_popularity ON album (popularity);
CREATE INDEX album_ndx_type ON album (type);
CREATE INDEX album_ndx_year ON album (year);
