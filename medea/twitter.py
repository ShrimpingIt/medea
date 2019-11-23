import gc

from medea.auth import twitterBearerId
from medea import Tokenizer,STR,NUM
from medea.https import generateContentBytes

twitterBaseUrl = "https://api.twitter.com/1.1/"

twitterHeaders = (
    b'Authorization: Bearer ',
    twitterBearerId,
    b'\r\n'
)
"""Headers authenticating request to the Twitter API"""


def createTwitterUrl(apiPath, getParams):
    """Constructs twitter URLs for an API endpoint and a map of named GET URL parameters"""
    url = twitterBaseUrl + apiPath + "?"
    url += "&".join(["{}={}".format(key, value) for key,value in getParams.items()])
    gc.collect()
    return url


def createTwitterTimelineUrl(screen_name, count=1, **k):
    """Constructs a twitter timeline URL returning 'count' tweets from the given Twitter account"""
    params = dict(
        screen_name=screen_name,
        count=count,
        include_rts = "false",
        tweet_mode="compat",
    )
    params.update(k)
    return createTwitterUrl("statuses/user_timeline.json", params)


def createTwitterSearchUrl(text, count=1, **k):
    """Constructs a twitter timeline URL returning 'count' tweets matching the search text"""
    params = dict(
        q=text,
        count=count,
        include_entities = "false",
    )
    params.update(k)
    return createTwitterUrl("search/tweets.json", params)

def generateTimelineBytes(account, count=1, buf=None):
    """Get bytes from the Twitter Timeline API"""
    twitterUrl = createTwitterTimelineUrl(account, count, tweet_mode="extended")
    return generateContentBytes(twitterUrl, twitterHeaders, buf=buf)

def generateSearchBytes(text, count=1, buf=None):
    """Create a JSON tokenizer from the Twitter Search API"""
    twitterUrl = createTwitterSearchUrl(text, count, tweet_mode="extended")
    return generateContentBytes(twitterUrl, twitterHeaders, buf=buf)

def generateTweets(tokenizer, gen):
    # initialise byteGenerator
    """Yields (id, full_text) pairs for tweets extracted from a Twitter API tokenizer"""

    reportNames = ["id", "full_text"] # process child values having these names
    suppressNames = ["user", "media", "quoted_status"] # throw away all descendants of these names (suppresses "id" descendants of these keys)
    
    def fieldGeneratorFactory(fieldName, gen):
        """If key matches intended fields, extracts string value from gen, otherwise throws away value"""
        valueTokens = tokenizer.tokenizeValue(gen, True)
        if fieldName in suppressNames:
            for tok, val in valueTokens: # consume tokens from stream
                pass
            return
        elif fieldName in reportNames:
            fieldVal = None
            for tok, val in valueTokens:
                if (tok is STR or tok is NUM) and fieldVal is None: 
                    fieldVal = val
                else:
                    raise ValueError # expect exactly one string or number
            else:
                return (yield fieldName, fieldVal)
        else:
            raise ValueError # specific named values expected by this callback 

    fieldGenerator = tokenizer.tokenizeValuesNamed(reportNames + suppressNames, fieldGeneratorFactory, gen)
    
    while True:
        try:
            _, tweetId = next(fieldGenerator)
            _, tweetText = next(fieldGenerator)
        except StopIteration: # raised by next() when generator stops 
            return
        else:
            yield tweetId, tweetText
