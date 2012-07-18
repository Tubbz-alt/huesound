import sys
import json;
import psycopg2;
from time import sleep
from huesound import artist, config, countries, api_call

def fetch_album_json(album_uri):
    return api_call.api_call("http://ws.spotify.com/lookup/1/?uri=%s" % album_uri)

def insert_album(conn, album_uri, data):
    """ Caller must have transaction open and catch errors! """

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