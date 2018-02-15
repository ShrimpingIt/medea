from medea.https import createByteGeneratorFactory
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
import sys

twitterUrl = createTwitterTimelineUrl('realDonaldTrump', tweet_mode="extended")
byteGeneratorFactory = createByteGeneratorFactory(twitterUrl, twitterHeaders)
byteGenerator = byteGeneratorFactory()

try:
    while True:
        sys.stdout.write(chr(next(byteGenerator)))
except StopIteration:
    pass