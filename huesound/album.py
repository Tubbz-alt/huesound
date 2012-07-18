import sys
import urllib2
import json;
import psycopg2;
from time import sleep
from huesound import artist, config, countries

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
    """ Caller must have transaction open and catch errors! """

    print data
    artist_id = artist.get_or_insert_artist(conn, data["album"]["artist-id"])

    cur = conn.cursor()
    sql = '''INSERT INTO album (album_uri, artist, red, green, blue, color) 
                  VALUES (%s, %s, -1, -1, -1, '(1000,1000,1000)') RETURNING id''';

    cur.execute(sql, (album_uri, artist_id))
    row = cur.fetchone()
    album_id = row[0]
    countries.insert_country_string(cur, album_id, data['album']['availability']['territories'])

def album_exists(conn, album_uri):
    cur = conn.cursor()
    cur.execute('''SELECT id FROM album WHERE album_uri = %s''', (album_uri,))
    row = cur.fetchone()
    if not row: return None
    return row[0] 
