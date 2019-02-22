from medea.https import generateResponseBytes
from medea.twitter import twitterHeaders, createTwitterTimelineUrl
import sys

twitterUrl = createTwitterTimelineUrl('realDonaldTrump', tweet_mode="extended")
byteGenerator = generateResponseBytes(twitterUrl, twitterHeaders)

try:
    while True:
        sys.stdout.write(chr(next(byteGenerator)))
except StopIteration:
    pass