#!/usr/bin/env python
#!/usr/local/virtualenv/huesound/bin/python

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
        id = artist.insert_artist(conn, data['album']['artist-id'])
    sleep(.1)
