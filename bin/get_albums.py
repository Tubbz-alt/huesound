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
        return (-1, -1)

    count = 0
    for al in data['artist']['albums']:
        count += 1
        try:
            artist_uri = al['album']['artist-id']
        except KeyError:
            artist_uri = album.VARIOUS_ARTISTS_URI
            al["album"]["artist-id"] = artist_uri
        if not album.album_exists(conn, al['album']['href']):
            album.insert_album(conn, al)
            added += 1
        else:
            exist += 1

    return (added, exist)

try:
    conn = psycopg2.connect(config.PG_CONNECT)
    ins = psycopg2.connect(config.PG_CONNECT)
except psycopg2.OperationalError as err:
    print "Cannot connect to database: %s" % err
    sys.exit(-1)

added = 0
exist = 0

cur = conn.cursor()
cur.execute("""SELECT artist_uri  
                 FROM artist 
             ORDER BY last_updated""")
for row in cur.fetchall():
    artist_uri = row[0]
    print "%s: " % artist_uri,
    try:
        added_tmp, exist_tmp = get_albums(ins, artist_uri)
        if added_tmp < 0: continue
        cur_ins = ins.cursor()
        cur_ins.execute("""UPDATE artist
                              SET last_updated = now()
                            WHERE artist_uri = %s""", (artist_uri,))
        ins.commit()
    except psycopg2.IntegrityError, e:
        ins.rollback()
        print "Commit failed: %s" % e
        sys.exit(-1)
    print "%d added, %d already exist" % (added_tmp, exist_tmp)
    added = added + added_tmp
    exits = exist + exist_tmp

print "Done. %d added, %d albums exist" % (added, exist)
