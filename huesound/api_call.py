import sys
import urllib2
import json;
import psycopg2
import socket
from time import sleep
import artist, config, countries

TIMEOUT = 30

def api_call(url):

    while True:
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('Accept', 'application/json'), 
                                 ('User-agent', '%s' % config.USER_AGENT)]
            f = opener.open(url, timeout=TIMEOUT)
        except urllib2.HTTPError, e:
            if hasattr(e, 'reason') and isinstance(e.reason, socket.timeout):
                print "timeout!"
                continue
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
            if hasattr(e, 'reason') and isinstance(e.reason, socket.timeout):
                print "timeout!"
                continue
            print "Cannot make api call: %s" % e
            return (None, e)
        
        try:
            data = json.loads(f.read())
        except socket.timeout:
            continue
        except socket.error:
            continue
        except urllib2.HTTPError, e:
            print "HTTPError: ", e.code
            return (None, e)
        except urllib2.URLError, e:
            print "URLError: ", e.reason
            return (None, e)

        f.close();
        return (data, "")
