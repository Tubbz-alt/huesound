#!/usr/bin/env python
#!/usr/local/virtualenv/huesound/bin/python

import sys
sys.path.append("../huesound")

import urllib2
import psycopg2
import subprocess
import re
import socket
from psycopg2.extensions import register_adapter
from huesound import cube, config

register_adapter(cube.Cube, cube.adapt_cube)

try:
    conn = psycopg2.connect(config.PG_CONNECT)
    cur = conn.cursor()
    conn2 = psycopg2.connect(config.PG_CONNECT)
    out_cur = conn2.cursor()
except psycopg2.OperationalError as err:
    print "Cannot connect to database: %s" % err
    exit()

completed = 0
total = 0
skipped = 0
while True:    
    cur.execute("""SELECT id, album_uri 
                     FROM album 
                    WHERE image_id 
                       IS null 
                      AND red != -2
                 ORDER BY id""")
    if cur.rowcount == 0: break
    total = cur.rowcount
    for row in cur:
        url = "http://open.spotify.com/album/%s" % row[1][14:]
        try:
            f = urllib2.urlopen(url)
        except urllib2.URLError, e:
            if isinstance(e.reason, socket.timeout):
                continue
            print "Cannot fetch open page: %s" % row[1]
            continue
        except urllib2.HTTPError, e:
            print "Cannot fetch open page %s: %s" % (row[1], e)
            continue

        page = f.read()
        f.close()

        m = re.search("[a-f0-9]{40}", page)
        if not m: 
            print "Could not find image id. Skipping %s" % row[1]
            skipped += 1
            sql = '''UPDATE album SET red = -2, green = -2, blue = -2 WHERE id = %s''';
            data = (row[0],)

        else:
            start, end = m.span()
            image_id = page[start:end]

            url = "http://o.scdn.co/300/%s" % image_id
            try:
                f = urllib2.urlopen(url)
            except urllib2.HTTPError, e:
                print "Cannot fetch image %s: %s" % (row[1], e)
                continue
            except urllib2.URLError, e:
                if isinstance(e.reason, socket.timeout):
                    continue
                print "Cannot fetch image: %s" % row[1]
                continue

            proc = subprocess.Popen(["jpegtopnm"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # catch socket.error: [Errno 104] Connection reset by peer
            tmp = proc.communicate(f.read())
            f.close();

            proc = subprocess.Popen(["pnmscale", "-xsize", "1", "-ysize", "1"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            out = proc.communicate(tmp[0])

            lines = out[0].split("\n", 3)
            if lines[0] == 'P6':
                red = ord(lines[3][0])
                green = ord(lines[3][1])
                blue = ord(lines[3][2])
            else:
                red = ord(lines[3])
                green = ord(lines[3])
                blue = ord(lines[3])

            sql = '''UPDATE album SET red = %s, green = %s, blue = %s, color = %s::cube, image_id = %s WHERE id = %s''';
            try:
                print "%s: %s, %s, %s -- %d of %d" % (row[0], red, green, blue, completed, total)
                data = ("%s" % red,
                        "%s" % green, 
                        "%s" % blue,
                        cube.Cube(red, green, blue),
                        image_id,
                        row[0])
            except IndexError:
                print "Internal error. Skipping %s" % row[1]
                skipped += 1
                continue
            completed += 1

        try:
            out_cur.execute(sql, data)
            conn2.commit()
        except psycopg2.IntegrityError:
            conn2.rollback()

print "%d processed, %d skipped." % (completed, skipped)
