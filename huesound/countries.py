#!/usr/bin/env python

import sys
import json;
import psycopg2;
import config

def get_country_id(cur, country):
    cur.execute('''SELECT id
                     FROM country 
                    WHERE code = %s''', (country,))
    row = cur.fetchone()
    if row: return row[0]

    cur.execute('''INSERT INTO country (id, code) VALUES (DEFAULT, %s) RETURNING id''', (country,))
    row = cur.fetchone()
    return row[0]

def insert_countries(cur, album, countries):
    countries = list(set(countries))
    for country in countries:
        country_id = get_country_id(cur, country)
        cur.execute('''INSERT INTO album_country VALUES (%s, %s)''', (album, country_id))
