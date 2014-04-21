#!/bin/sh

# Create the database
psql -U postgres < create_db.sql

# install 
echo "CREATE EXTENSION cube;" | psql -U postgres huesound

# Create the tables
psql -U huesound huesound < create_tables.sql
