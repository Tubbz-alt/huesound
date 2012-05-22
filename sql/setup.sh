#!/bin/sh

# Create the database
psql -U postgres < create_db.sql

# install 
psql -U postgres huesound < `pg_config --sharedir`/contrib/cube.sql

# Create the tables
psql -U huesound huesound < create_tables.sql

# Insert the list of countries
psql -U huesound huesound < countries.sql
