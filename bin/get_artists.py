#!/usr/bin/env python
#!/usr/local/virtualenv/huesound/bin/python

# This script is intended to move from Spotify schema 1 to schema 2
# (album top level -> artist top level)

import sys
sys.path.append("../huesound")

import urllib2
import urllib
import json;
from time import sleep
import psycopg2
from huesound import config, artist

def fetch_album_json(album_uri):
    url = "http://ws.spotify.com/lookup/1/?uri=%s" % urllib.quote_plus(album_uri)
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('Accept', 'application/json'), 
                             ('User-agent', '%s' % config.USER_AGENT)]
        f = opener.open(url)
    except urllib2.URLError, e:
        print "error!", e
        return (None, e)

    data = json.loads(f.read())
    f.close();
    return (data, "")

try:
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()
except psycopg2.OperationalError as err:
    print "Cannot connect to database: %s" % err
    exit()

while True:
    line = sys.stdin.readline()
    if not line: break
    uri = line.strip()
    data, err = fetch_album_json(uri)
    if err: 
        print "fetch album %s failed: %s" % (uri, err)
    else:
        try:
            artist_uri = data['album']['artist-id']
        except KeyError:
            if data['album']['artist'] != "Various Artists":
                print "Cannot find artist-id in returned data."
                print json.dumps(data, sort_keys=True, indent = 4);
            continue

        id = artist.get_or_insert_artist(conn, artist_uri)
        print "%s -> %d" % (artist_uri, id)
            
    sleep(.1)
