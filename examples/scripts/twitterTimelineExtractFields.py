from medea import Tokenizer
from medea.https import createContentByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
from examples.scripts import timeit

defaultAccount = "realDonaldTrump"
reportNames = ["id", "full_text"] # process child values having these keys
suppressNames = ["user", "media"] # throw away all descendants of these keys (hence throwing their false-matching "id" or "full_text" entries)

def generateTweets(account=None):
    try:
        if account is None:
            account=defaultAccount
        
        twitterUrl = createTwitterTimelineUrl(account, count=1, tweet_mode="extended")
        byteGeneratorFactory = createContentByteGeneratorFactory(twitterUrl, twitterHeaders)
        tokenizer = Tokenizer(byteGeneratorFactory)

        def fieldGeneratorFactory(name):
            # generator for token pairs of the named JSON value
            valueTokenSequence = tokenizer.tokenizeValue()
            try:
                for tok, val in valueTokenSequence: # should be a single pair e.g. 'STR', '298743097324'
                    if name in reportNames: 
                        return (yield name, val)
            except StopIteration:
                return

        fieldGenerator = tokenizer.generateFromNamed(reportNames + suppressNames, fieldGeneratorFactory)
        
        while True:
            _, tweetId = next(fieldGenerator)
            _, tweetText = next(fieldGenerator)
            yield tweetId, tweetText
    except StopIteration:
        return

def run():
    for tweetId, tweetText in generateTweets():
        print("{} : '{}'".format(tweetId, tweetText))

if __name__ == "__main__":
    timeit(run)
