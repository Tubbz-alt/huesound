#!/usr/bin/env python

import sys
import urllib
import json;
import psycopg2;
import config, api_call

VARIOUS_ARTISTS_URI = "spotify:artist:deadbeef"

def fetch_artist_json(artist_uri):
    return api_call.api_call("http://ws.spotify.com/lookup/1/?uri=%s" % artist_uri)

def get_or_insert_artist(conn, artist_uri):
    cur = conn.cursor()
    cur.execute('''SELECT id FROM artist WHERE artist_uri = %s''', (artist_uri,))
    row = cur.fetchone()
    if not row:
        cur.execute('''INSERT INTO artist (id, artist_uri) 
                            VALUES (DEFAULT, %s) 
                         RETURNING id''', (artist_uri,))
        row = cur.fetchone()
        return row[0]
    else:
        return row[0]
