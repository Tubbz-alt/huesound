#!/usr/bin/env python
#!/usr/local/virtualenv/huesound/bin/python

import sys
sys.path.append("../huesound")

import urllib2
import psycopg2
import subprocess
import re
import socket
import json
from time import sleep
from psycopg2.extensions import register_adapter
from huesound import cube, config, api_call, artist

register_adapter(cube.Cube, cube.adapt_cube)

COUNT = 100 

try:
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()
    conn2 = psycopg2.connect(config.PG_CONNECT)
    out_cur = conn2.cursor()
except psycopg2.OperationalError as err:
    print "Cannot connect to database: %s" % err
    exit()

while True:    
    cur.execute("""SELECT count(*)
                     FROM album 
                    WHERE artist 
                       IS null""")
    remaining = cur.fetchone()[0]
    cur.execute("""SELECT count(*) FROM album """)
    total = cur.fetchone()[0]
    print
    print "%d of %d complete (%d%%)" % (total - remaining, total, int(((total - remaining) * 100 / total)))
    print

    cur.execute("""SELECT id, album_uri 
                     FROM album 
                    WHERE artist 
                       IS null 
                      AND red != -2
                 ORDER BY id
                    LIMIT %s""", (COUNT,))
    if cur.rowcount == 0: break
    for row in cur:
        data, err = artist.fetch_artist_json(row[1])
        if not data: 
            print err
            break

        try:
            artist_uri = data['album']['artist-id']
        except KeyError:
            if data['album']['artist'] == "Various Artists":
                artist_uri = artist.VARIOUS_ARTISTS_URI
            else:
                print "Weird artist!"
                print json.dumps(data, indent=4, sort_keys=True)
                continue

        artist_id = artist.get_or_insert_artist(conn2, artist_uri)
        if artist_id >= 0:
            print "%s -> %d" % (artist_uri, artist_id)

            sql = '''UPDATE album SET artist = %s WHERE id = %s''';
            cur2 = conn2.cursor()
            try:
                cur2.execute(sql, (artist_id, row[0]))
                conn2.commit()
            except psycopg2.IntegrityError:
                print "rollback!"
                conn2.rollback()

        sleep(.25)

print "Processed all albums."
