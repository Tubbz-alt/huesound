#!/usr/bin/env python

import sys
import urllib2
import json;
import psycopg2;
from huesound import config

def get_country_id(cur, country):
    cur.execute('''SELECT id
                     FROM country 
                    WHERE code = %s''', (country,))
    row = cur.fetchone()
    if row: return row[0]

    cur.execute('''INSERT INTO country (id, code) VALUES (DEFAULT, %s) RETURNING id''', (country,))
    row = cur.fetchone()
    return row[0]

def get_or_insert_country_string(cur, countries):

    cur.execute('''SELECT id
                     FROM country_string cs
                    WHERE cs.string = %s''', (countries,))
    row = cur.fetchone()
    if row: return row[0]

    cur.execute('''INSERT INTO country_string (id, string) values (DEFAULT, %s) RETURNING id''', (countries,))
    row = cur.fetchone()
    id = row[0]

    for country in countries.split(' '):
        country_id = get_country_id(cur, country)
        cur.execute('''INSERT INTO country_string_country VALUES (%s, %s)''', (id, country_id))

    return id
