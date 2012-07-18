#!/usr/bin/env python

import sys
import urllib
import json;
import psycopg2;
from huesound import config

def fetch_artist_json(artist_uri):
    return api_call.api_call("http://ws.spotify.com/lookup/1/?uri=%s&extras=albumdetail" % urllib.quote_plus(artist_uri))

def get_or_insert_artist(conn, artist_uri):
    try:
        cur = conn.cursor()
        cur.execute('''INSERT INTO artist (id, artist_uri) 
                            VALUES (DEFAULT, %s) 
                         RETURNING id''', (artist_uri,))
        row = cur.fetchone()
        conn.commit()
        return row[0]
    except psycopg2.IntegrityError:
        conn.rollback()
        cur = conn.cursor()
        cur.execute('''SELECT id FROM artist WHERE artist_uri = %s''', (artist_uri,))
        row = cur.fetchone()
        return row[0]