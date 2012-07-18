#!/usr/bin/env python

import sys
import urllib2
import urllib
import json;
import psycopg2;
from huesound import config

def fetch_artist_json(artist_uri):
    url = "http://ws.spotify.com/lookup/1/?uri=%s&extras=albumdetail" % urllib.quote_plus(artist_uri)
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('Accept', 'application/json'), 
                             ('User-agent', '%s' % config.USER_AGENT)]
        f = opener.open(url)
    except urllib2.URLError, e:
        return (None, e)

    data = json.loads(f.read())
    f.close();
    return (data, "")

def insert_artist(conn, artist_uri):
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
