#!/usr/bin/env python
#!/usr/local/virtualenv/huesound/bin/python

import sys
sys.path.append("../huesound")

import urllib2
import urllib
import json;
from time import sleep
from huesound import config

def fetch_artist_json(artist_name):
    url = "http://ws.spotify.com/search/1/album?q=artist:%s" % urllib.quote_plus(artist_name)
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

def parse_albums(data):
    for albums in data:
        try: 
            for album in albums['albums']:
                print album['href']
        except:
            pass

while True:
    line = sys.stdin.readline()
    if not line: break
    artist, crap = line.split('|')
    artist = artist.strip()
    data = fetch_artist_json(artist)
    parse_albums(data)
    sleep(.1)
