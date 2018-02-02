from utime import sleep_ms, ticks_ms, ticks_diff
import network
import sys

from medea.agnostic import gc
from medea.auth import *

twitterBaseUrl = "https://api.twitter.com/1.1/"

uplink = network.WLAN(network.STA_IF)
uplink.active(True)
uplink.connect("SkyHome", "c3fnh0ile")

connectTime = ticks_ms()
connectTimeout = 16000 
while not uplink.isconnected() and ticks_diff(ticks_ms(), connectTime) < connectTimeout:
    sleep_ms(100)

def https_generate(url, headers=None, buf=None, socketTimeout=1.0):
    _, _, host, path = url.split('/', 3)

    import usocket
    import ussl
    if buf is None:
        buf = bytearray(128)
    bufmv = memoryview(buf)
    addr = usocket.getaddrinfo(host, 443)[0][-1]
    s=usocket.socket()
    s.connect(addr)
    s.settimeout(socketTimeout)
    try:
        s=ussl.wrap_socket(s)
        s.write(b'GET /{} HTTP/1.1\r\nHost: {}\r\nUser-Agent: Cockle\r\n'.format(path, host))
        if headers is not None:
            s.write(headers)
        s.write(b'\r\n')
        while True:
            gc.collect()
            try:
                count = s.readinto(buf) # need to parse HTTP Response to get number of bytes then close 
                if count > 0:
                    if count < len(buf):
                        yield bufmv[:count]
                    else:
                        yield buf
                    continue
            except OSError as ose:
                print(ose)
            break # handles case where read count is 0 and triggers close
    finally:
        s.close()

def twitter_generate_timeline(screen_name, count=1, extraGetParams=None, *a, **k):
    getParams = dict(
        screen_name=screen_name,
        count=count,
        include_rts = "false",
    )
    if extraGetParams is not None:
        getParams.update(extraGetParams)

    url = twitterBaseUrl + "statuses/user_timeline.json?"
    url += "&".join(["{}={}".format(key, value) for key,value in getParams.items()])
    gc.collect()
    yield from https_generate(url, headers=bearerHeader, *a, **k)

def twitter_generate_search(text, count=1, extraGetParams=None, *a, **k):
    getParams = dict(
        q=text,
        count=count,
        include_entities = "false",
    )
    if extraGetParams is not None:
        getParams.update(extraGetParams)

    url = twitterBaseUrl + "search/tweets.json?"
    url += "&".join(["{}={}".format(key, value) for key,value in getParams.items()])
    gc.collect()
    yield from https_generate(url, headers=bearerHeader, *a, **k)

def dump(count=1):
    for block in twitter_generate_timeline('realDonaldTrump', count=count):
        sys.stdout.write(block)