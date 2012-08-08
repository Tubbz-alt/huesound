import sys
import urllib2
import json;
import psycopg2
import socket
from time import sleep
from huesound import artist, config, countries

TIMEOUT = 30

def api_call(url):

    while True:
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('Accept', 'application/json'), 
                                 ('User-agent', '%s' % config.USER_AGENT)]
            f = opener.open(url, timeout=TIMEOUT)
        except urllib2.HTTPError, e:
            if e.code == 403:
                sys.stdout.write("Requesting data too fast! Sleeping!\n")
                sleep(5)
                continue
            if e.code == 504:
                sys.stdout.write("Gateway timeout. Sleeping 1 second!\n")
                sleep(1)
                continue
            return (None, e)
        except urllib2.URLError, e:
            if isinstance(e.reason, socket.timeout):
                continue
            print "URLError: ", e.reason
            return (None, e)
        
        try:
            data = json.loads(f.read())
        except urllib2.URLError, e:
            if isinstance(e.reason, socket.timeout):
                continue
            print "URLError: ", e.reason
            return (None, e)

        f.close();
        return (data, "")
