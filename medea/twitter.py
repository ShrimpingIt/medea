import gc

from medea.auth import twitterBearerId

twitterBaseUrl = "https://api.twitter.com/1.1/"

twitterHeaders = (
    b'Authorization: Bearer ',
    twitterBearerId,
    b'\r\n'
)
"""Headers authenticating request to the Twitter API"""


def createTwitterUrl(apiPath, getParams):
    url = twitterBaseUrl + apiPath + "?"
    url += "&".join(["{}={}".format(key, value) for key,value in getParams.items()])
    gc.collect()
    return url


def createTwitterTimelineUrl(screen_name, count=1, **k):
    params = dict(
        screen_name=screen_name,
        count=count,
        include_rts = "false",
    )
    params.update(k)
    return createTwitterUrl("statuses/user_timeline.json", params)


def createTwitterSearchUrl(text, count=1, **k):
    params = dict(
        q=text,
        count=count,
        include_entities = "false",
    )
    params.update(k)
    return createTwitterUrl("search/tweets.json", params)