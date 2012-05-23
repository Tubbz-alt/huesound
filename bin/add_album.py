#!/usr/bin/env python
#!/usr/local/virtualenv/huesound/bin/python

import sys
sys.path.append("../huesound")

import urllib2
import json;
import psycopg2;
from time import sleep
from huesound import config, countries

def fetch_album_json(album_uri):
    url = "http://ws.spotify.com/lookup/1/?uri=%s" % album_uri
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('Accept', 'application/json'), 
                             ('User-agent', '%s' % config.USER_AGENT)]
        f = opener.open(url)
    except urllib2.URLError, e:
        if e.code == 403:
            print "Requesting data too fast! Sleeping!"
            sleep(5)
        return (None, e)

    data = json.loads(f.read())
    f.close();
    return (data, "")

def insert_album(conn, album_uri, data):
    cur = conn.cursor()
    cs = countries.get_or_insert_country_string(cur, data['album']['availability']['territories'])

    sql = '''INSERT INTO color_cube (album_uri, red, green, blue, color, countries) 
                  VALUES (%s, -1, -1, -1, '(1000,1000,1000)', %s)''';
    data = (album_uri, cs)

    try:
        cur.execute(sql, data)
    except psycopg2.IntegrityError, e:
        conn.rollback()
        return e

def album_exists(conn, album_uri):
    cur = conn.cursor()
    cur.execute('''SELECT id FROM color_cube WHERE album_uri = %s''', (album_uri,))
    row = cur.fetchone()
    if not row: return None
    return row[0] 

def add_album(album_uri):
    try:
        conn = psycopg2.connect(config.PG_CONNECT)
    except psycopg2.OperationalError as err:
        return "Cannot connect to database: %s" % err

    if album_exists(conn, album_uri):
        return "This album already exists"

    data, err = fetch_album_json(album_uri)
    if not data: return err

    insert_album(conn, album_uri, data)
    try:
        conn.commit()
    except psycopg2.IntegrityError, e:
        conn.rollback()
        return "Commit failed: %s" % e

    return ""

if len(sys.argv) == 1:
    while True:
        line = sys.stdin.readline()
        if not line: break
        album_uri = line[:-1]
        e = add_album(album_uri)
        if e: 
            print e
        else:
            print "added: %s" % album_uri
        sleep(.12)
else:
    album_uri = sys.argv[1] 
    e = add_album(album_uri)
    if e: 
        print e
    else:
        print "album added: %s" % album_uri
