#!/usr/bin/env python
#!/usr/local/virtualenv/huesound/bin/python

import sys
sys.path.append("../huesound")

import urllib
import psycopg2
import json;
from time import sleep
from huesound import album, config, api_call

def get_albums(conn, artist_uri):
    added = 0;
    exist = 0;

    data, e = api_call.api_call("http://ws.spotify.com/lookup/1/?uri=%s&extras=albumdetail" % artist_uri)
    if e:
        print e
        return

    for al in data['artist']['albums']:
        print json.dumps(al, sort_keys=True, indent = 4);
        if not album.album_exists(conn, al['album']['href']):
            album.insert_album(conn, al['album']['href'], album)
            added += 1
        else:
            exists += 1

    return (added, exists)

artist_uri = "spotify:artist:6pmxr66tMAePxzOLfjGNcX"

try:
    conn = psycopg2.connect(config.PG_CONNECT)
except psycopg2.OperationalError as err:
    print "Cannot connect to database: %s" % err
    sys.exit(-1)

try:
    added, exists = get_albums(conn, artist_uri)
    conn.commit()
except psycopg2.IntegrityError, e:
    conn.rollback()
    print "Commit failed: %s" % e
    sys.exit(-1)

print "%s: %d albums exist, %d added" % (artist_uri, added, exists)
